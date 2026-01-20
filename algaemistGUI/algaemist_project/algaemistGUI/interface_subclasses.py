import customtkinter
from tkinter import messagebox
import logging


class ConnectionFrame(customtkinter.CTkFrame):
    def __init__(self, master, reactor):
        super().__init__(master, height=32)
        self.reactor = reactor
        self.grid_propagate(False)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Connection state
        self.con_state_label = customtkinter.CTkLabel(self, text="Connection state:")
        self.con_state_label.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=(2, 2))
        self.con_state_value_label = customtkinter.CTkLabel(self, text="disconnected", text_color="red")
        self.con_state_value_label.grid(row=1, column=1, sticky="w", padx=(5, 10), pady=(2, 2))

        # Port display
        self.port_label = customtkinter.CTkLabel(self, text="Port:")
        self.port_label.grid(row=1, column=2, sticky="e", padx=(10, 5), pady=(2, 2))
        self.port_value_label = customtkinter.CTkLabel(self, text="N/A")
        self.port_value_label.grid(row=1, column=3, sticky="w", padx=(5, 10), pady=(2, 2))

        # Start automatic refresh
        self.refresh_connection()

    def set_connection_state(self):
        """Update the connection label based on reactor.connected."""
        if self.reactor.connected:
            self.con_state_value_label.configure(text="connected", text_color="green")
            # Show actual port if available
            if self.reactor.ser:
                self.port_value_label.configure(text=self.reactor.ser.port)
        else:
            self.con_state_value_label.configure(text="disconnected", text_color="red")
            self.port_value_label.configure(text="N/A")

    def refresh_connection(self):
        """Refresh connection state periodically."""
        self.set_connection_state()
        self.after(10000, self.refresh_connection)  # refresh every 10 seconds


class TemperatureFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, reactor, config_manger, sensor_lock):
        super().__init__(master)
        
        self.reactor = reactor
        self.config_manger = config_manger
        self.sensor_lock = sensor_lock
        self.grid_columnconfigure((0,1), weight=1)
    
        self.title = customtkinter.CTkLabel(self, text='Temperature', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        # Temperature value label
        self.temp_label = customtkinter.CTkLabel(self, text="Current Temp: -- °C")
        self.temp_label.grid(row=1, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # horizontal line after live value
        separator1 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Temperature control label
        self.temp_ctrl_label_text = customtkinter.CTkLabel(self, text="Temperature control:")
        self.temp_ctrl_label_text.grid(row=3, column=0, pady=(10, 10), padx=(20,5), sticky='e')

        self.temp_ctrl_value_label = customtkinter.CTkLabel(self, text="OFF", text_color='red')
        self.temp_ctrl_value_label.grid(row=3, column=1, pady=(10, 10), padx=(5,20), sticky='w')

        # Temperature set point 2 value label
        self.set_pt_label = customtkinter.CTkLabel(self, text="Current temp set point SP1: -- °C")
        self.set_pt_label.grid(row=4, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.temp_set_pt = customtkinter.CTkEntry(self, placeholder_text='', width=100)
        self.temp_set_pt.grid(row=5, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply set point 1
        self.set_button = customtkinter.CTkButton(self, text="Set", command=self.apply_setpoint1)
        self.set_button.grid(row=5, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # horizontal line after live value
        separator2 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator2.grid(row=6, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Temperature set point 2 value label
        self.set_pt_label2 = customtkinter.CTkLabel(self, text="Current temp set point SP2: -- °C")
        self.set_pt_label2.grid(row=7, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.temp_set_pt2 = customtkinter.CTkEntry(self, placeholder_text='', width=100)
        self.temp_set_pt2.grid(row=8, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply set point 2
        self.set_button2 = customtkinter.CTkButton(self, text="Set", command=self.apply_setpoint2)
        self.set_button2.grid(row=8, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # horizontal line after live value
        separator3 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator3.grid(row=9, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Heater contorl power value label 
        self.heat_label = customtkinter.CTkLabel(self, text="Heater power: -- %")
        self.heat_label.grid(row=10, column=0, pady=(10, 0), padx=20, columnspan=2, sticky='w')
        
        # Cooler contorl power value label 
        self.cool_label = customtkinter.CTkLabel(self, text="Cooler power: -- %")
        self.cool_label.grid(row=11, column=0, pady=(0, 0), padx=20, columnspan=2, sticky='w')

    
    ### Methods for temperature frame ###
        
    def temperature_frame_display_update(self, temp_value: float, heater_power: float, cooler_power: float, temp_setpoint1: float,  control_on: bool, temp_setpoint2: float): 
        """Update all temperature frame display elements."""
        
        # Current temperature
        self.temp_label.configure(text=f"Current Temp: {temp_value:.2f} °C")
        
        # Heater / cooler powers
        self.heat_label.configure(text=f"Heater power: {heater_power} %")
        self.cool_label.configure(text=f"Cooler power: {cooler_power} %")
        
        # Temperature setpoint
        self.set_pt_label.configure(text=f"Current temp set point SP1: {temp_setpoint1:.2f} °C")
        self.set_pt_label2.configure(text=f"Current temp set point SP2: {temp_setpoint2:.2f} °C")
        
        # Control switch state
        if control_on:
            self.temp_ctrl_value_label.configure(text="ON", text_color="green")
        else:
            self.temp_ctrl_value_label.configure(text="OFF", text_color="red")
            
    def apply_setpoint1(self, retry=0):
        """Send the temperature day setpoint to the reactor."""
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_setpoint1(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return        
        
        temp_str = self.temp_set_pt.get()  # get value from entry
        if not temp_str:
            return  # nothing entered

        try:
            temp_val = float(temp_str)
            # Send command via Reactor method
            success = self.reactor.set_temp_day(temp_val)
            if success:
                logging.info(f"Day temperature setpoint sent: {temp_val} °C")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set day temperature: {temp_val} °C")

        except ValueError:
            # Show a pop-up error without halting the program
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")

    def apply_setpoint2(self, retry=0):
        """Send the temperature night setpoint to reactor and update config."""
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_setpoint2(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        temp_str = self.temp_set_pt2.get()
        if not temp_str:
            return

        try:
            temp_val = float(temp_str)
            # Send command via Reactor method
            success = self.reactor.set_temp_night(temp_val)
            if success:
                self.config_manger.set("night_temp_sp2", temp_val)
                self.config_manger.save()
                logging.info(f"Night temperature setpoint sent: {temp_val} °C (and saved to config)")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set night temperature: {temp_val} °C")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")    



class PHFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, reactor, sensor_lock):
        super().__init__(master)
        
        self.reactor = reactor
        self.sensor_lock = sensor_lock
        self.grid_columnconfigure((0,1), weight=1)
        # self.current_setpoint = '' # default set point 
        
        self.title = customtkinter.CTkLabel(self, text='pH', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        # pH value label 
        self.pH_label = customtkinter.CTkLabel(self, text="Current pH: --")
        self.pH_label.grid(row=1, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # horizontal line after live value
        separator1 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # pH control label
        self.pH_ctrl_label_text = customtkinter.CTkLabel(self, text="pH control:")
        self.pH_ctrl_label_text.grid(row=3, column=0, pady=(10, 10), padx=(20,5), sticky='e')

        self.pH_ctrl_value_label = customtkinter.CTkLabel(self, text="OFF", text_color='red')
        self.pH_ctrl_value_label.grid(row=3, column=1, pady=(10, 10), padx=(5,20), sticky='w')
        
        # Ph Set point value label 
        self.set_pt_label = customtkinter.CTkLabel(self, text="Current pH set point: --")
        self.set_pt_label.grid(row=4, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.pH_set_pt = customtkinter.CTkEntry(self, width=100)
        self.pH_set_pt.grid(row=5, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button = customtkinter.CTkButton(self, text="Set", command=self.apply_setpointpH)
        self.set_button.grid(row=5, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # horizontal line after live value
        separator2 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator2.grid(row=6, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # External pH pump mode
        self.ph_pump_label = customtkinter.CTkLabel(self, text="External pH Pump")
        self.ph_pump_label.grid(row=7, column=0, pady=(10, 10), padx=(20, 5), sticky="e")

        self.ph_pump_menu = customtkinter.CTkOptionMenu(self, values=["base", "acid"], command=self.on_ph_pump_selected) # 0=base, 1=acid
        self.ph_pump_menu.grid(row=7, column=1, pady=(10, 10), padx=(5, 20), sticky="w")
        
        # pH base pump power
        self.ph_base_label = customtkinter.CTkLabel(self, text="Base pump power: -- %")
        self.ph_base_label.grid(row=8, column=0, pady=(5, 5), padx=20, columnspan=2, sticky="w")

        # pH correction power
        self.ph_correction_label = customtkinter.CTkLabel(self, text="pH correction: -- ")
        self.ph_correction_label.grid(row=9, column=0, pady=(5, 10), padx=20, columnspan=2, sticky="w")

    ### Methods for pH frame ###    
        
    def ph_frame_display_update(self, ph_value: float, ph_setpoint: float, control_on: bool, ph_base_power: float, ph_correction : float):
        """Update all pH frame display elements."""
        
        # Current pH value
        self.pH_label.configure(text=f"Current pH: {ph_value:.2f}")
        
        # pH setpoint
        self.set_pt_label.configure(text=f"Current pH set point: {ph_setpoint:.2f}")
        
        # Pump powers
        self.ph_base_label.configure(text=f"Base pump power: {ph_base_power:.1f} %")
        self.ph_correction_label.configure(text=f"pH correction: {ph_correction:.1f}")

        
        # Control switch state (or ON/OFF indicator)
        if control_on:
            self.pH_ctrl_value_label.configure(text="ON", text_color="green")
        else:
            self.pH_ctrl_value_label.configure(text="OFF", text_color="red")
            
    def apply_setpointpH(self, retry=0):
        """Send the pH setpoint to the reactor."""
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_setpointpH(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        
        pH_str = self.pH_set_pt.get()  # get value from entry
        if not pH_str:
            return  # nothing entered

        try:
            pH_val = float(pH_str)
            # Send command via Reactor method
            success = self.reactor.set_ph(pH_val)
            if success:
                logging.info(f"pH setpoint sent: {pH_val}")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set pH setpoint: {pH_val}")

        except ValueError:
            # Show a pop-up error without halting the program
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")

    def on_ph_pump_selected(self, selected_mode, retry=0):
        """Confirm and send command to select acid/base pump."""
        result = messagebox.askyesno(
            "Confirm pH Pump Mode",
            f"Change external pH pump to '{selected_mode}'?"
        )
        if result:
            
            MAX_RETRIES = 10

            # If another thread is using the serial connection, retry shortly
            if self.sensor_lock.locked():
                if retry < MAX_RETRIES:
                    self.winfo_toplevel().after(1000, lambda: self.on_ph_pump_selected(retry + 1))
                else:
                    messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
                return
            
            
            mode_map = {"base": 0, "acid": 1}
            mode_value = mode_map.get(selected_mode)

            success = self.reactor.set_external_ph_pump(mode_value)
            if success:
                logging.info(f"External pH pump set to: {selected_mode.upper()}")
            else:
                messagebox.showwarning(
                    "Command Failed",
                    f"Failed to change external pH pump to '{selected_mode}'."
                )
                
                

class LightFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master,reactor, sensor_lock):
        super().__init__(master)
        
        self.reactor = reactor
        self.sensor_lock = sensor_lock
        self.grid_columnconfigure((0,1), weight=1)
        
        # Light frame title
        self.title = customtkinter.CTkLabel(self, text='Light', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        # Lightsensor 1 value label (initial placeholder)
        self.lisens1_label = customtkinter.CTkLabel(self, text="Sensor 1: --")
        self.lisens1_label.grid(row=1, column=0, pady=(10, 10), padx=(20,10), columnspan=1, sticky='w')
        
        # Lightsensor 2 value label (initial placeholder)
        self.lisens2_label = customtkinter.CTkLabel(self, text="Sensor 2: --")
        self.lisens2_label.grid(row=1, column=1, pady=(10, 10), padx=(10,20), columnspan=1, sticky='w')
        
        # horizontal line after live value
        separator1 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Secondary light sensor sensitivity dropdown
        self.sec_sens_label = customtkinter.CTkLabel(self, text="Secondary sensitivity")
        self.sec_sens_label.grid(row=3, column=0, padx=(20,5), pady=5, sticky='e')

        self.sec_sens_menu = customtkinter.CTkOptionMenu(self,values=["Low", "High"],command=self.on_sec_sens_selected)
        self.sec_sens_menu.grid(row=3, column=1, padx=(5,20), pady=5, sticky='w')
        
        # Light control mode
        self.light_ctrl_label = customtkinter.CTkLabel(self, text="Light control mode")
        self.light_ctrl_label.grid(row=4, column=0, pady=(10, 10), padx=(20,5), columnspan=1, sticky='e')
        self.light_ctrl_menu = customtkinter.CTkOptionMenu(self, values=['continuous', 'timed', 'sinus'], command=self.on_mode_selected)
        self.light_ctrl_menu.grid(row=4, column=1, pady=(10, 10), padx=(5,20), columnspan=1, sticky='w')
        
        
        # Brightness Set point value label (initial placeholder)
        self.set_pt_label = customtkinter.CTkLabel(self, text="Current brightness: -- %")
        self.set_pt_label.grid(row=5, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # Box to enter new setpoint
        self.bright_set_pt = customtkinter.CTkEntry(self, placeholder_text='', width=100)
        self.bright_set_pt.grid(row=6, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button1 = customtkinter.CTkButton(self, text="Set brightness", command=self.apply_brightness)
        self.set_button1.grid(row=6, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # horizontal line after live value
        separator2 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator2.grid(row=7, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # On time Set point value label (initial placeholder)
        self.on_set_pt_label = customtkinter.CTkLabel(self, text="ON time: --")
        self.on_set_pt_label.grid(row=8, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # Box to enter On time
        self.on_set_pt = customtkinter.CTkEntry(self,placeholder_text='',width=100)
        self.on_set_pt.grid(row=9, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button2 = customtkinter.CTkButton(self, text="Set ON time",command=self.apply_light_on_time)
        self.set_button2.grid(row=9, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # Off time Set point value label (initial placeholder)
        self.off_set_pt_label = customtkinter.CTkLabel(self, text="OFF time: --")
        self.off_set_pt_label.grid(row=10, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.off_set_pt = customtkinter.CTkEntry(self, placeholder_text='',width=100)
        self.off_set_pt.grid(row=11, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button3 = customtkinter.CTkButton(self, text="Set OFF time", command=self.apply_light_off_time)
        self.set_button3.grid(row=11, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
    
    def light_frame_display_update(self, brightness: float, prim_light: float, mode: int, on_time: str, off_time: str, sec_sensitivity: int, sec_value: float):
        """Update all display elements in the light frame."""
        
        # Brightness %
        self.set_pt_label.configure(text=f"Current brightness: {brightness:.1f} %")

        # Primary light sensor reading
        self.lisens1_label.configure(text=f"Sensor 1: {prim_light:.1f} ")

        # Mode (translate number to readable text)
        mode_text = {1: "continuous", 2: "timed", 3: "sinus"}.get(mode, f"unknown ({mode})")
        self.light_ctrl_menu.set(mode_text)

        # Timed On/Off
        self.on_set_pt_label.configure(text=f"ON time: {on_time[:2]}:{on_time[2:]}")
        self.off_set_pt_label.configure(text=f"OFF time: {off_time[:2]}:{off_time[2:]}")

        # Secondary light info
        self.lisens2_label.configure(text=f"Sensor 2: {sec_value:.1f}")
        
        # Set dropdown to current value
        if sec_sensitivity == 0:
            self.sec_sens_menu.set("Low")
        elif sec_sensitivity == 1:
            self.sec_sens_menu.set("High")
        else:
            self.sec_sens_menu.set("Unknown")

        
        
        
    def on_sec_sens_selected(self, selected_value: str, retry=0):
        """Send command to reactor when user selects sensitivity."""
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.on_sec_sens_selected(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        mode_map = {"Low": 0, "High": 1}
        mode_value = mode_map.get(selected_value)
        
        if mode_value is not None:
            success = self.reactor.set_secondary_light_sensitivity(mode_value)
            if success:
                logging.info(f"Secondary light sensitivity set to {selected_value}")
            else:
                messagebox.showwarning(
                    "Command Failed",
                    f"Failed to set secondary light sensitivity to {selected_value}"
                )
                
    def apply_brightness(self, retry=0):
        """Send the brightness setpoint to the reactor."""
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_brightness(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return   
        
        brigth_str = self.bright_set_pt.get()  # get value from entry
        if not brigth_str:
            return  # nothing entered

        try:
            bri_val = int(brigth_str)      
            # Send command via Reactor method
            success = self.reactor.set_brightness(bri_val)
            if success:
                logging.info(f"New brightness sent: {bri_val}")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set brightness: {bri_val}")

        except ValueError:
            # Show a pop-up error without halting the program
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")
    
    def apply_light_on_time(self, retry=0):
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_light_on_time(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        time_str = self.on_set_pt.get().strip()
        if not time_str:
            return  # nothing entered

        try:
            # Split input
            parts = time_str.split(":")
            if len(parts) != 2:
                raise ValueError("Time must be in HH:MM format")

            hh = int(parts[0])
            mm = int(parts[1])

            # Validate ranges
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError("Hours must be 0-23 and minutes 0-59")

            # Send command via Reactor method
            success = self.reactor.set_light_on_time(hh,mm)
            if success:
                logging.info(f"New ON time sent: {hh}:{mm}")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set ON time: {hh}:{mm}")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter a valid time in HH:MM format.\n{e}")
        
    
    
    def apply_light_off_time(self, retry=0):
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_light_off_time(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        time_str = self.off_set_pt.get().strip()
        if not time_str:
            return  # nothing entered

        try:
            # Split input
            parts = time_str.split(":")
            if len(parts) != 2:
                raise ValueError("Time must be in HH:MM format")

            hh = int(parts[0])
            mm = int(parts[1])

            # Validate ranges
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError("Hours must be 0-23 and minutes 0-59")

            # Send command via Reactor method
            success = self.reactor.set_light_off_time(hh,mm)
            if success:
                logging.info(f"New OFF time sent: {hh}:{mm}")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set OFF time: {hh}:{mm}")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter a valid time in HH:MM format.\n{e}")
        
    
    def on_mode_selected(self, selected_mode, retry=0):
        """Ask user if they want to change the mode and send command."""
        result = messagebox.askyesno(
            "Confirm Mode Change",
            f"Do you want to change the light mode to '{selected_mode}'?"
        )
        
        if result:
            
            MAX_RETRIES = 10

            # If another thread is using the serial connection, retry shortly
            if self.sensor_lock.locked():
                if retry < MAX_RETRIES:
                    self.winfo_toplevel().after(1000, lambda: self.on_mode_selected(retry + 1))
                else:
                    messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
                return
            
            # Map string to mode number
            mode_map = {"continuous": 1, "timed": 2, "sinus": 3}
            mode_value = mode_map.get(selected_mode)
            
            success = self.reactor.set_light_mode(mode_value)
            
            if success:
                logging.info(f"Light mode set to: {selected_mode.upper()}")
            else:
                messagebox.showwarning(
                    "Command Failed",
                    f"Failed to change light mode to '{selected_mode}'."
                )

class GasFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master,reactor):
        super().__init__(master, height=60)
        
        self.reactor = reactor
        self.grid_columnconfigure((0,1), weight=1)

        
        self.title = customtkinter.CTkLabel(self, text='Gas', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        # Airflow value label (initial placeholder)
        self.air_label = customtkinter.CTkLabel(self, text="Airflow: -- l/min")
        self.air_label.grid(row=1, column=0, pady=(10, 0), padx=20, columnspan=1, sticky='w')
        
        # Lightsensor 2 value label (initial placeholder)
        self.co2_label = customtkinter.CTkLabel(self, text="CO2: -- l/min")
        self.co2_label.grid(row=2, column=0, pady=(10, 10), padx=20, columnspan=1, sticky='w')
        
    def update_gas_values(self, value1, value2):
        """Update the displayed light sensor values."""
        self.air_label.configure(text=f"Airflow: {value1:.2f} l/min")
        self.co2_label.configure(text=f"CO2: {value2:.2f} l/min")
    
    

class ReactorFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, reactor, config_manger, sensor_lock):
        super().__init__(master)
        
        self.reactor = reactor
        self.config_manager = config_manger
        self.sensor_lock = sensor_lock
        self.grid_columnconfigure((0,1), weight=1)    
        
        self.title = customtkinter.CTkLabel(self, text='Reactor Control', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)
        
        
        # reactor control mode
        self.reactor_ctrl_label = customtkinter.CTkLabel(self, text="Reactor control mode")
        self.reactor_ctrl_label.grid(row=1, column=0, pady=(10, 10), padx=(20,5), columnspan=1, sticky='e')
        self.reactor_ctrl_menu = customtkinter.CTkOptionMenu(self, values=['Turbidity', 'Timed Turbitdity', 'Chemostat', 'Timed Chemostat'], command=self.on_reactor_mode_selected)
        self.reactor_ctrl_menu.grid(row=1, column=1, pady=(10, 10), padx=(5,20), columnspan=1, sticky='w')
    
    
        # horizontal line after live value
        separator1 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Turbidity Set point value label (initial placeholder)
        self.turb_set_pt_label = customtkinter.CTkLabel(self, text="Current Turb set point: -- ")
        self.turb_set_pt_label.grid(row=3, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.turb_set_pt = customtkinter.CTkEntry(self,placeholder_text='', width=100)
        self.turb_set_pt.grid(row=4, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button = customtkinter.CTkButton(self, text="Set", command=self.apply_turbidity)
        self.set_button.grid(row=4, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
        # horizontal line after live value
        separator2 = customtkinter.CTkFrame(self, height=2, fg_color="gray50")
        separator2.grid(row=5, column=0, columnspan=2, sticky="ew", padx=25, pady=(5,5))
        
        # Pump power value label (initial placeholder)
        self.turb_pump_label = customtkinter.CTkLabel(self, text="Pump power: -- %")
        self.turb_pump_label.grid(row=6, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # Current Chemostat (from config)
        self.chemo_label = customtkinter.CTkLabel(self, text="Chemostat: -- %")
        self.chemo_label.grid(row=7, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        # Chemostat Set point value label (initial placeholder)
        self.chemo_set_pt_label = customtkinter.CTkLabel(self, text="Chemostat set point (0-100%)")
        self.chemo_set_pt_label.grid(row=8, column=0, pady=(10, 10), padx=20, columnspan=2, sticky='w')
        
        self.chemo_set_pt = customtkinter.CTkEntry(self, placeholder_text="",width=100)
        self.chemo_set_pt.grid(row=9, column=0, padx=(20, 5), pady=(0, 10), sticky="e")
        
        # Button to apply setpoint
        self.set_button1 = customtkinter.CTkButton(self,text="Set",command=self.apply_chemostat)
        self.set_button1.grid(row=9, column=1, padx=(5, 20), pady=(0, 10), sticky="w")
        
    def update_reactor_status(self, pump_power: float, turb_setpoint: float,reactor_mode: int , chemostat_per : float):
        """ Update multiple reactor UI elements at once. """
        
        # Update pump power if provided
        if pump_power is not None:
            self.turb_pump_label.configure(text=f"Pump power: {pump_power:.2f} %")
        
        # Update turbidity setpoint if provided
        if turb_setpoint is not None:
            self.turb_set_pt_label.configure(text=f"Current Turb set point: {turb_setpoint:.2f}")
            
        if chemostat_per is not None:
            self.chemo_label.configure(text=f"Chemostat: {chemostat_per} %")

        # Update reactor mode if provided
        if reactor_mode is not None:
            mode_map = {
                0: "Turbidity",
                1: "Timed Turbidity",
                2: "Chemostat",
                3: "Timed Chemostat"
            }
            mode_str = mode_map.get(reactor_mode, "Chemostat")
            self.reactor_ctrl_menu.set(mode_str)

        
    
        
    def on_reactor_mode_selected(self, selected_mode, retry=0):
        """Ask user if they want to change the reactor mode and send command."""
        result = messagebox.askyesno(
            "Confirm Mode Change",
            f"Do you want to change the reactor mode to '{selected_mode}'?"
        )
        
        if not result:
            return  # user cancelled
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.on_reactor_mode_selected(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return

        # Map string mode names to numeric codes expected by reactor
        mode_mapping = {
            "Turbidity": 0,
            "Timed Turbidity": 1,
            "Chemostat": 2,
            "Timed Chemostat": 3
        }

        mode_value = mode_mapping.get(selected_mode)
        if mode_value is None:
            messagebox.showerror("Error", f"Unknown mode: {selected_mode}")
            return

        success = self.reactor.set_reactor_mode(mode_value)

        if success:
            logging.info(f"Reactor mode set to: {selected_mode}")
        else:
            messagebox.showwarning(
                "Command Failed",
                f"Failed to change reactor mode to '{selected_mode}'."
            )
                
                
    def apply_turbidity(self, retry=0):
        """Send the turbidostat setpoint to the reactor."""
        
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_turbidity(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        
        turb_str = self.turb_set_pt.get()  # get value from entry
        if not turb_str:
            return  # nothing entered

        try:
            turb_val = int(turb_str)
            
            # Send command via Reactor method
            success = self.reactor.set_turbidity(turb_val)
            if success:
                logging.info(f"New turbidity sent: {turb_val}")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set turbidity: {turb_val}")

        except ValueError:
            # Show a pop-up error without halting the program
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")
    
    
    def apply_chemostat(self, retry=0):
        """Send the chemostat setpoint to the reactor (auto retries if busy)."""
        MAX_RETRIES = 10

        # If another thread is using the serial connection, retry shortly
        if self.sensor_lock.locked():
            if retry < MAX_RETRIES:
                self.winfo_toplevel().after(1000, lambda: self.apply_chemostat(retry + 1))
            else:
                messagebox.showwarning("Please Try Again", "System is busy. Try again in a moment.")
            return
        chemo_str = self.chemo_set_pt.get()  # get value from entry
        if not chemo_str:
            return  # nothing entered

        try:
            chemo_val = int(chemo_str)

            
            # print(cmd_value)
            # Send command via Reactor method
            success = self.reactor.set_chemostat(chemo_val)                
            if success:
                self.config_manager.set("chemostat_setpoint", chemo_val)
                self.config_manager.save()
                logging.info(f"New chemostat setpoint sent: {chemo_val} (and saved to config)")
            else:
                messagebox.showwarning("Command Failed", f"Failed to set chemostat: {chemo_val}")

        except ValueError:
            # Show a pop-up error without halting the program
            messagebox.showerror("Invalid Input", "Please enter a valid number for the setpoint.")
    
    
