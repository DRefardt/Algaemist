# reactor/reactor.py

import threading
import time
import logging
from datetime import datetime
from .connection import list_ports, open_connection
from .utils import DataLogger



class Reactor:
    def __init__(self, addr=1):
        self.addr = addr
        self.ser = None
        self._connected = False
        self.data_logger = DataLogger()
        self._serial_lock = threading.Lock()
        self.time = datetime.now()


    @property
    def connected(self):
        """Return True if serial is connected."""
        return self._connected
        
        
    def connect(self, port=None):
        """Auto-detect FTDI port if not specified."""
        if port is None:
            port = list_ports(manufacturer="FTDI")
            if not port:
                raise ConnectionError("No FTDI device found")
            port = port[0]

        self.ser = open_connection(port)
        self._connected = True
        logging.info(f"Connected to {port}")
        self.set_time(self.time.hour, self.time.minute)
        logging.info(f"Set reactor time to {self.time}")
        
    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self._connected = False
        logging.info("Disconnected")
        
    def wait(self, interval: float):
        time.sleep(interval)
    
    def send(self, cmd: str, read_response=True, timeout=1) -> str | None:
        """
        Thread-safe serial send. Locks serial access so only one thread
        communicates with the reactor at a time.
        """
        if not self._connected or not self.ser:
            logging.error("Send called while reactor not connected")
            return None

        with self._serial_lock:  # Only one thread can send info a time
            try:
                self.ser.write(cmd.encode())

                if read_response:
                    old_timeout = self.ser.timeout
                    self.ser.timeout = timeout
                    resp = self.ser.readline().decode(errors="ignore").strip()
                    self.ser.timeout = old_timeout
                    time.sleep(0.1)
                    return resp
                else:
                    time.sleep(0.1)
                    return None

            except Exception as e:
                logging.error(f"Serial error sending command '{cmd}': {e}")
                time.sleep(0.1)
                return None

    # -- Data Logging ---
        
    def log_current_values(self, comment: str | None = None):
        """Read current sensor & pump values and log them manually."""
        if self._connected:
            sensors = self.read_all_sensors() or {}
            pumps = self.read_all_pumps() or {}
            self.data_logger.log_values(sensors, pumps, comment)

    def emergency_log(self, sensors, pumps, path):
        """Read current sensor & pump values and log them in the emergency log."""
        if self._connected:
            self.data_logger.max_log_values(sensors, pumps, path=path)

    def start_auto_logging(self, interval=1800):
        """Start automatic logging in a background thread."""
        self.data_logger.interval = interval
        self.data_logger.start_auto(reactor_getter=lambda: self)

    def stop_auto_logging(self):
        self.data_logger.stop_auto()
    
    # --- pH Methods ---
    def get_ph_setpoint(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}p0000")
        if resp:
            try:
                return float(resp.split("p")[-1])
            except Exception as e:
                logging.error(f"Failed to parse pH setpoint: {resp} -> {e}")
        return None

    def get_ph_value(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}p0001")
        if resp:
            try:
                return float(resp.split("p")[-1])
            except Exception as e:
                logging.error(f"Failed to parse pH value: {resp} -> {e}")
        return None

    def get_ph_co2_power(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}p0002")
        if resp:
            try:
                return float(resp.split("p")[-1])
            except Exception as e:
                logging.error(f"Failed to parse pH CO2 power: {resp} -> {e}")
        return None

    def get_ph_control_on(self) -> bool | None:
        resp = self.send(f"/{self.addr:02d}p0003")
        if resp:
            try:
                return bool(int(resp.split("p")[-1]))
            except Exception as e:
                logging.error(f"Failed to parse pH control state: {resp} -> {e}")
        return None

    def get_ph_base_power(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}p0004")
        if resp:
            try:
                return float(resp.split("p")[-1])
            except Exception as e:
                logging.error(f"Failed to parse pH base power: {resp} -> {e}")
        return None

    def get_ph_correction(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}p0005")
        if resp:
            try:
                return float(resp.split("p")[-1])
            except Exception as e:
                logging.error(f"Failed to parse pH correction: {resp} -> {e}")
        return None
    
    
    # --- Temperature ---
    def get_temp_setpoint(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}r0000")
        if resp is None:
            logging.error("No response from reactor for temperature setpoint")
        try:
            return float(resp.split("r")[-1])
        except Exception as e:
            logging.error(f"Failed to parse temperature setpoint: {resp} -> {e}")
            return None

    def get_temp_value(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}r0001")
        if resp:
            try:
                return float(resp.split("r")[-1])
            except Exception as e:
                logging.error(f"Failed to parse temperature value: {resp} -> {e}")
        return None

    def get_heater_power(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}r0002")
        if resp:
            try:
                return float(resp.split("r")[-1])
            except Exception as e:
                logging.error(f"Failed to parse heater power: {resp} -> {e}")
        return None

    def is_temp_control_on(self) -> bool | None:
        resp = self.send(f"/{self.addr:02d}r0003")
        if resp:
            try:
                return bool(int(resp.split("r")[-1]))
            except Exception as e:
                logging.error(f"Failed to parse temperature control state: {resp} -> {e}")
        return None

    def get_cooler_power(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}r0004")
        if resp:
            try:
                return float(resp.split("r")[-1])
            except Exception as e:
                logging.error(f"Failed to parse cooler power: {resp} -> {e}")
        return None
    
# --- Turbidity / Light sensors --- 
    def get_sec_light_sensitivity(self) -> int | None:
        resp = self.send(f"/{self.addr:02d}s0000")
        if resp:
            try:
                return int(resp.split("s")[-1])
            except Exception as e:
                logging.error(f"Failed to parse secondary light sensitivity: {resp} -> {e}")
        return None

    def get_turb_setpoint(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}u0000")
        if resp:
            try:
                return float(resp.split("u")[-1])
            except Exception as e:
                logging.error(f"Failed to parse turbidity setpoint: {resp} -> {e}")
        return None

    def get_sec_light_value(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}u0001")
        if resp:
            try:
                return float(resp.split("u")[-1])
            except Exception as e:
                logging.error(f"Failed to parse secondary light value: {resp} -> {e}")
        return None

    def get_turb_pump_power(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}u0002")
        if resp:
            try:
                return float(resp.split("u")[-1])
            except Exception as e:
                logging.error(f"Failed to parse turbidity pump power: {resp} -> {e}")
        return None

    def is_turb_control_on(self) -> bool | None:
        resp = self.send(f"/{self.addr:02d}u0003")
        if resp:
            try:
                return bool(int(resp.split("u")[-1]))
            except Exception as e:
                logging.error(f"Failed to parse turbidity control state: {resp} -> {e}")
        return None
    
    def get_error(self) -> int | None:
        resp = self.send(f"/{self.addr:02d}e0000")
        if resp:
            try:
                return int(resp.split("e")[-1])
            except Exception as e:
                logging.error(f"Failed to parse error code: {resp} -> {e}")
        return None

    def get_system_info(self) -> str | None:
        resp = self.send(f"/{self.addr:02d}i0000")
        if resp:
            try:
                # Combine all semicolon-separated values
                return ";".join(resp.split("i")[-1].split(";"))
            except Exception as e:
                logging.error(f"Failed to parse system info: {resp} -> {e}")
        return None

    def get_board_version(self) -> str | None:
        resp = self.send(f"/{self.addr:02d}i0001")
        if resp:
            try:
                return resp.split("i")[-1]
            except Exception as e:
                logging.error(f"Failed to parse board version: {resp} -> {e}")
        return None

    def get_airflow(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}f0001")
        if resp:
            try:
                return float(resp.split("f")[-1])
            except Exception as e:
                logging.error(f"Failed to parse airflow: {resp} -> {e}")
        return None

    def get_co2_flow(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}f0002")
        if resp:
            try:
                return float(resp.split("f")[-1])
            except Exception as e:
                logging.error(f"Failed to parse CO2 flow: {resp} -> {e}")
        return None

        # --- Light control ---
    def get_brightness(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}b0000")
        if resp:
            try:
                return float(resp.split("b")[-1])
            except Exception as e:
                logging.error(f"Failed to parse brightness: {resp} -> {e}")
        return None

    def get_primary_light(self) -> float | None:
        resp = self.send(f"/{self.addr:02d}l0000")
        if resp:
            try:
                return float(resp.split("l")[-1])
            except Exception as e:
                logging.error(f"Failed to parse primary light: {resp} -> {e}")
        return None

    def get_light_mode(self) -> int | None:
        resp = self.send(f"/{self.addr:02d}o0000")
        if resp:
            try:
                return int(resp.split("o")[-1])
            except Exception as e:
                logging.error(f"Failed to parse light mode: {resp} -> {e}")
        return None

    def get_light_on_time(self) -> str | None:
        resp = self.send(f"/{self.addr:02d}n0000")
        if resp:
            try:
                return str(resp.split("n")[-1].zfill(4))
            except Exception as e:
                logging.error(f"Failed to parse light on time: {resp} -> {e}")
        return None

    def get_light_off_time(self) -> str | None:
        resp = self.send(f"/{self.addr:02d}k0000")
        if resp:
            try:
                return str(resp.split("k")[-1].zfill(4))
            except Exception as e:
                logging.error(f"Failed to parse light off time: {resp} -> {e}")
        return None

    # --- Misc ---
    def get_comm_version(self) -> str | None:
        resp = self.send(f"/{self.addr:02d}v0000")
        if resp:
            try:
                return resp.split("v")[-1]
            except Exception as e:
                logging.error(f"Failed to parse communication version: {resp} -> {e}")
        return None

    def get_reactor_mode(self) -> int | None:
        resp = self.send(f"/{self.addr:02d}m0000")
        if resp:
            try:
                return int(resp.split("^")[-1]) #the reactor answers with a "^" as seperator for the value
            except Exception as e:
                logging.error(f"Failed to parse reactor mode: {resp} -> {e}")
        return None

    # --- Aggregated sensor / pump readings ---
    def read_all_sensors(self) -> dict | None:
        resp = self.send(f"/{self.addr:02d}x0000")
        if resp:
            try:
                parts = resp.split("x")[-1].split(";")
                return {
                    "temp": float(parts[0]),
                    "pH": float(parts[1]),
                    "light_prim": float(parts[2]),
                    "light_sec": float(parts[3]),
                    "air": float(parts[4]),
                    "co2": float(parts[5]),
                }
            except Exception as e:
                logging.error(f"Failed to parse aggregated sensor data: {resp} -> {e}")
        return None

    def read_all_pumps(self) -> dict | None:
        resp = self.send(f"/{self.addr:02d}q0000")
        if resp:
            try:
                parts = resp.split("q")[-1].split(";")
                return {
                    "co2_pump": float(parts[0]),
                    "heater_pump": float(parts[1]),
                    "cooler_pump": float(parts[2]),
                    "turb_pump": float(parts[3]),
                }
            except Exception as e:
                logging.error(f"Failed to parse aggregated pump data: {resp} -> {e}")
        return None
    
    # --- Device / Time ---
    def change_address(self, new_addr: int) -> bool:
        """Change the reactor device address."""
        cmd = f"/{self.addr:02d}A{new_addr:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            self.addr = new_addr  # update internal address if successful
            return True
        logging.warning(f"Failed to change address: {resp}")
        return False

    def set_time(self, hh: int, mm: int) -> bool:
        """Set reactor device time (hours and minutes)."""
        cmd = f"/{self.addr:02d}T{hh:02d}{mm:02d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set time: {resp}")
        return False
    
    
    # --- Light ---
    def set_brightness(self, value: int) -> bool:
        """
        Set light brightness (0-100%).
        Accepts int from 0-100 and converts to
        command for reactor.
        E.g. 50 -> B0050 for 50% brightness
        """
        cmd_value = max(0, min(100, value))
        cmd = f"/{self.addr:02d}B{cmd_value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set brightness: {resp}")
        return False

    def set_light_on_time(self, hh: int, mm: int) -> bool:
        """Set light ON time (HHMM)."""
        cmd = f"/{self.addr:02d}N{hh:02d}{mm:02d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set light ON time: {resp}")
        return False

    def set_light_off_time(self, hh: int, mm: int) -> bool:
        """Set light OFF time (HHMM)."""
        cmd = f"/{self.addr:02d}K{hh:02d}{mm:02d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set light OFF time: {resp}")
        return False

    def set_light_mode(self, mode: int) -> bool:
        """Set light control mode: 1=Continuous, 2=Timed, 3=Sinus."""
        cmd = f"/{self.addr:02d}O{mode:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set light mode: {resp}")
        return False

    def set_light_range(self, mode: int) -> bool:
        """Set light range mode: 0=High, 1=Low."""
        cmd = f"/{self.addr:02d}L{mode:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set light range: {resp}")
        return False

    def set_secondary_light_sensitivity(self, mode: int) -> bool:
        """Set secondary light sensor sensitivity: 0=Low, 1=High."""
        cmd = f"/{self.addr:02d}S{mode:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set secondary light sensitivity: {resp}")
        return False

    # --- Temperature / pH ---
    def set_ph(self, value: int) -> bool:
        """
        Set pH setpoint. Values from 2-12. 
        The Value is automatically converted to
        the command format for the reactor. 
        E.g. pH 7.5 -> P0075
        """
        pH_val = max(2.0, min(12.0, value))         # Clamp the value to 2.0 - 12.0
        pH_val = round(pH_val, 1)                   # Round to 1 decimal place
        cmd_value = int(pH_val * 10)                # Convert to command format (pHSP = value * 10)
        cmd = f"/{self.addr:02d}P{cmd_value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set pH: {resp}")
        return False

    def set_temp_day(self, value: float) -> bool:
        """
        Set day temp setpoint. Values from 0 - 45. 
        The Value is automatically converted to
        the command format for the reactor. 
        E.g. 10.5°C -> R0105
        """
        temp_val = max(0.0, min(45.0, value))       # Clamp the value to 0.0 - 45.0
        temp_val = round(temp_val, 1)               # Round to 1 decimal place
        cmd_val = int(temp_val * 10)                # Convert to command format (SP1 = value * 10)
        cmd = f"/{self.addr:02d}R{cmd_val:04d}"     # Create the command
        resp = self.send(cmd)
        if resp and resp[-2:] == "??":              # Reactor answers with ?? here, idk why...
            return True
        logging.warning(f"Failed to set day temperature: {resp}")
        return False

    def set_temp_night(self, value: int) -> bool:
        """
        Set night temp setpoint. Values from 0 - 45. 
        The Value is automatically converted to
        the command format for the reactor. 
        E.g. 10.5°C -> R1105 (R1 is for night temp)
        """
        temp_val = max(0.0, min(45.0, value))       # Clamp the value to 0.0 - 45.0
        temp_val = round(temp_val, 1)               # Round to 1 decimal place
        cmd_val = int(temp_val * 10)                # Convert to command format (SP2 = value * 10)
        cmd = f"/{self.addr:02d}R1{cmd_val:03d}"    # Create the command
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set night temperature: {resp}")
        return False

    # --- Turbidity / Chemostat ---
    def set_turbidity(self, value: int) -> bool:
        """
        Set turbidity control level (0-850).
        Accepts int values form 0 to 850 and
        converts them to a reactor command.
        E.g. 150 -> U0150 to set 150 as turbidity setpoint
        """
        cmd_value = max(0, min(850, value)) # Clamp the value to 0 - 850
        cmd = f"/{self.addr:02d}U{cmd_value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set turbidity: {resp}")
        return False

    def set_chemostat(self, value: int) -> bool:
        """Set chemostat setpoint (0-100%)."""
        # Clamp the value to 0 - 100%
        cmd_value = max(0, min(100, value))
        cmd = f"/{self.addr:02d}C{cmd_value:04d}"
        resp = self.send(cmd)
        print(resp) #for debugging)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set chemostat: {resp}")
        return False

    # --- External / Misc ---
    def set_external_ph_pump(self, value: int) -> bool:
        """Set external pH pump control: 0=Base,1=Acid."""
        cmd = f"/{self.addr:02d}E{value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set external pH pump: {resp}")
        return False

    def set_anti_foam_timer(self, interval: int, runtime: int) -> bool:
        """Set anti-foam timer: interval & runtime."""
        cmd = f"/{self.addr:02d}F{interval:02d}{runtime:02d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set anti-foam timer: {resp}")
        return False

    def switch_off_master_modes(self) -> bool:
        """Switch off all master modes."""
        cmd = "/00^0000"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to switch off master modes: {resp}")
        return False

    def set_filter_cycles(self, value: int) -> bool:
        """Set measuring filter cycles (1-16)."""
        cmd = f"/{self.addr:02d}Q{value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set filter cycles: {resp}")
        return False

    def reset_communication(self) -> bool:
        """Reset communication controller."""
        cmd = f"/{self.addr:02d}!0000"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to reset communication: {resp}")
        return False

    def set_audible_alarm(self, value: int) -> bool:
        """Set audible alarm: 0=Off,1=On."""
        cmd = f"/{self.addr:02d}@{value:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set audible alarm: {resp}")
        return False

    def set_reactor_mode(self, mode: int) -> bool:
        """Set reactor mode: 0=Turbidostat, 2=Timed Turbidostat, 2=Chemostat, 3=Timed Chemostat."""
        cmd = f"/{self.addr:02d}M{mode:04d}"
        resp = self.send(cmd)
        if resp and resp[-2:] == "OK":
            return True
        logging.warning(f"Failed to set reactor mode: {resp}")
        return False
