import threading
import sys
import os
from datetime import datetime
import subprocess

# add algaemist_project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import customtkinter as ctk
import algaemistGUI.interface_subclasses as guiElements
from algaemistGUI.config_manager import ConfigManager
from reactor.reactor import Reactor


class AlgaemistGUI:
    def __init__(self): # The reactor has the adress 21
        
        # --- Initialize Configurations ---
        self.config_manger = ConfigManager()
        reactor_addr = self.config_manger.get("reactor_addr")
        
        # --- Reactor setup ---
        self.reactor = Reactor(addr=reactor_addr)
        self.reactor.connect()  # auto-detect FTDI port
        
        now = datetime.now()  # current local date and time
        hh = now.hour   # current hour (0-23)
        mm = now.minute # current minute (0-59)
        self.reactor.set_time(hh,mm)

        # --- GUI root ---
        self.root = ctk.CTk()
        self.root.title("Algaemist Reactor GUI")
        self.root.geometry("1200x800")
        
        # --- handle threading ---
        self.sensor_lock = threading.Lock()
        
        # Track last logged time for hidden log
        self._last_log_time = None
        self.log_interval = 600  # 10 minutes in seconds
        self.emergency_log_path = os.path.join(os.getcwd(), ".data", "emergency_log.csv")

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.emergency_log_path), exist_ok=True)
        

        # --- Layout configuration ---
        self.root.grid_columnconfigure((0,1,2), weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        
        # --- Camera integration ---
        self.camera_button = ctk.CTkButton(
            self.root,
            text="Open Camera",
            command=self.open_camera
        )
        self.camera_button.grid(row=1, column=2, padx=10, pady=5, sticky="e")

        # --- Frames ---
        self.header = ctk.CTkLabel(self.root, text='Live System Overview', fg_color="gray30",
                                    anchor="w", font=("Arial", 20, "bold"), corner_radius=6)
        self.header.grid(row=0, column=0, pady=(10,0), padx=10, sticky='ew', columnspan=3)

        self.connection_frame = guiElements.ConnectionFrame(self.root, reactor=self.reactor)
        self.connection_frame.grid(row=1, column=0, padx=10, pady=(10,5), sticky='ew', columnspan=2)

        self.temperature_frame = guiElements.TemperatureFrame(self.root, reactor=self.reactor, config_manger=self.config_manger, sensor_lock=self.sensor_lock)
        self.temperature_frame.grid(row=2, column=0, padx=10, pady=(10,5), sticky='nsew')

        self.pH_frame = guiElements.PHFrame(self.root, reactor=self.reactor, sensor_lock=self.sensor_lock)
        self.pH_frame.grid(row=3, column=0, padx=10, pady=(5,10), sticky='nsew')

        self.light_frame = guiElements.LightFrame(self.root, reactor=self.reactor, sensor_lock=self.sensor_lock)
        self.light_frame.grid(row=2, column=1, padx=10, pady=(10,10), sticky='nsew', rowspan=2)

        self.gas_frame = guiElements.GasFrame(self.root, reactor=self.reactor)
        self.gas_frame.grid(row=3, column=2, padx=10, pady=(5,5), sticky='nsew')

        self.reactor_frame = guiElements.ReactorFrame(self.root, reactor=self.reactor, config_manger=self.config_manger, sensor_lock=self.sensor_lock)
        self.reactor_frame.grid(row=2, column=2, padx=10, pady=(5,10), sticky='nsew')
        
        self.poll_reactor_sensors()

    def _read_and_update_sensors(self):
        with self.sensor_lock:
            if self.reactor.connected:
                sensors = self.reactor.read_all_sensors()
                pumps = self.reactor.read_all_pumps()
                temp_setpoint1 = self.reactor.get_temp_setpoint()
                temp_ctrl_on = self.reactor.is_temp_control_on()
                temp_setpoint2 = self.config_manger.get("night_temp_sp2")
                ph_setpoint = self.reactor.get_ph_setpoint()
                ph_ctrl_on = self.reactor.get_ph_control_on()
                ph_corr_fact = self.reactor.get_ph_correction()
                light_brightness = self.reactor.get_brightness()
                light_mode = self.reactor.get_light_mode()
                light_on = self.reactor.get_light_on_time()
                light_off = self.reactor.get_light_off_time()
                sec_sens = self.reactor.get_sec_light_sensitivity()
                turb_setpt = self.reactor.get_turb_setpoint()
                reactor_mode = self.reactor.get_reactor_mode()
                chemostat_per = self.config_manger.get("chemostat_setpoint")
                
                        
        # Update GUI safely from the main thread
        self.root.after(0, lambda: self._update_frames(
        sensors, pumps, temp_setpoint1, temp_ctrl_on, temp_setpoint2,
        ph_setpoint, ph_ctrl_on, ph_corr_fact,
        light_brightness, light_mode, light_on, light_off, sec_sens, turb_setpt , reactor_mode, chemostat_per))
        
        # Auto-log every 10 minutes using DataLogger
        now = datetime.now()
        if self._last_log_time is None or (now - self._last_log_time).total_seconds() >= self.log_interval:
            self.reactor.emergency_log(sensors, pumps, path=self.emergency_log_path)
            self._last_log_time = now
        
    def _update_frames(self, sensors, pumps, t_sp1, t_ctrl, t_sp2,
                ph_sp, ph_ctrl, ph_corr,
                light_brightness, light_mode, light_on, light_off,
                sec_sens, turb_setpt, reactor_mode, chemostat_per):
        
        self.temperature_frame.temperature_frame_display_update(
            sensors["temp"], pumps["heater_pump"], pumps["cooler_pump"], t_sp1, t_ctrl, t_sp2
        )
        self.pH_frame.ph_frame_display_update(
            sensors["pH"], ph_sp, ph_ctrl, pumps["co2_pump"], ph_corr
        )
        self.light_frame.light_frame_display_update(
            light_brightness, sensors["light_prim"], light_mode, light_on, light_off, sec_sens, sensors["light_sec"]
        )
        self.gas_frame.update_gas_values(sensors['air'], sensors['co2'])
        
        self.reactor_frame.update_reactor_status(pumps['turb_pump'], turb_setpt, reactor_mode, chemostat_per)
        

    def poll_reactor_sensors(self):
        if self.reactor.connected and not self.sensor_lock.locked():
            threading.Thread(target=self._read_and_update_sensors, daemon=True).start()
            
        self.root.after(4000, self.poll_reactor_sensors)
            
            
        
    def run(self):
        self.root.mainloop()

    def open_camera(self):
        if hasattr(self, "camera_process") and self.camera_process.poll() is None:
            # camera already running → stop it
            self.camera_process.terminate()
            self.camera_process = None
            self.camera_button.configure(text="Open Camera")
        else:
            # start camera preview
            self.camera_process = subprocess.Popen(
                ["rpicam-hello", "-t", "0"],  # -t 0 = infinite
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.camera_button.configure(text="Close Camera")