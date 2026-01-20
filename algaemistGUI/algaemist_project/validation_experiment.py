####################################
# Example Experiment File
#
# This file contains a simple example experiment
# that can be performed using the Algaemist reactor 
# with this Python module.
#
# The settings are explained so that a new user
# can quickly set up their own experiments.
####################################

# Import the reactor commands
from reactor.reactor import Reactor

# Path where experiment data should be saved
savefile = './experiment/main_experiment.csv'

# Interval in seconds between automatic sensor readings
save_interval = 60*15     # 15 minutes

# Turbidity (culture density) settings
high_turb = 350     # Upper threshold: pump will add growth medium until this density
low_turb = 270      # Lower threshold: culture will grow until this density
end_turb = 90       # Emergency stop or final setpoint for experiment end

# Temperature settings
temp_range_start = 18      # Start temperature for experiment
temp_range_end = 38        # End temperature for experiment
exp_temp = [i for i in range(temp_range_start, temp_range_end+1)]  # Temperature sweep
end_temp = 20              # Final temperature at experiment end

# Number of repetitions for growth experiment ("sawtooth cycles")
reps = 3

# Flag to safely stop the experiment if an error occurs
stop_experiment = False

# Safe sensor reading function with retries
def safe_sensor_read(reactor, max_retries=20):
    """
    Attempt to read all sensors from the reactor.
    Retries up to max_retries times if the read fails.
    Returns sensor readings if successful, else None.
    """
    sensors = None
    counter = 0
    while sensors is None and counter < max_retries:
        counter += 1
        sensors = reactor.read_all_sensors()
        
    if sensors is not None:
        return sensors
    else:
        print("Could not read sensors after multiple attempts.")
        return None
                                

# Create a Reactor object and connect to the physical reactor
algaemist = Reactor(addr=21)  # Set reactor address to 21
algaemist.connect()            # Connect to the reactor

if algaemist.connected:
    print('Connection established...')
    
    # Configure the data logger
    algaemist.data_logger.set_path(savefile)        # Set file path for saving data
    algaemist.start_auto_logging(save_interval)     # Start automatic logging at defined interval
    algaemist.wait(.5)                              # Small delay to avoid serial connection overload
    
    # Main experiment loop
    print('Starting experiment...')
    while True:
        if algaemist.connected:
            # Set a base light level
            _ = algaemist.set_brightness(25)
            
            # Sweep through the temperature range
            for temp in exp_temp:
                algaemist.log_current_values(f'Temp set to {temp}')  # Log temperature change
                _ = algaemist.set_temp_day(temp)                     # Apply new temperature
                algaemist.wait(.5)
                print(f'Temp set to {temp}')
                
                # Repeat turbidity cycles ("sawtooth") as specified
                for i in range(reps):
                    # Start the dilution process
                    turb_set = algaemist.get_turb_setpoint()
                    if turb_set < high_turb:
                        algaemist.log_current_values(f'Turb set to {high_turb}')
                        _ = algaemist.set_turbidity(high_turb)  # Increase turbidity
                        print(f'Turbidity set to: {high_turb}')
                        algaemist.wait(.5)
                    
                    sensors = safe_sensor_read(algaemist)
                    if sensors is None:
                        stop_experiment = True
                        break
                    light_sec = sensors['light_sec']
            
                    # Wait until culture reaches high turbidity
                    while light_sec < high_turb:
                        sensors = safe_sensor_read(algaemist)
                        if sensors is None:
                            stop_experiment = True
                            break
                        light_sec = sensors['light_sec']
                        algaemist.wait(60*4)  # Wait 4 minutes between checks
                    if stop_experiment:
                        break 
                    
                    # Short waiting period before reducing turbidity
                    algaemist.wait(60*10)
                    algaemist.log_current_values(f'Turb set to {low_turb}')
                    _ = algaemist.set_turbidity(low_turb)  # Reduce turbidity
                    print(f'Values logged and turbidity set to: {low_turb}')
                    algaemist.wait(.5)
                    
                    # Wait until culture reaches low turbidity
                    while light_sec > low_turb:
                        sensors = safe_sensor_read(algaemist)
                        if sensors is None:
                            stop_experiment = True
                            break
                        light_sec = sensors['light_sec']
                        algaemist.wait(60*4)
                    if stop_experiment:
                        break   
                        
                    print('Turbidity reached, restarting cycle...')
                    algaemist.log_current_values('End of cycle')
                    algaemist.wait(60*5)  # Short delay between cycles
                
                if stop_experiment:
                    break    
                print(f'Finished {reps} repetitions, changing temperature...')
                algaemist.wait(60*5)  # Short delay before next temperature step
                
            # Stop automatic logging after experiment
            algaemist.stop_auto_logging()
            
            # Reset turbidity and temperature to safe end values
            _ = algaemist.set_turbidity(end_turb)
            print(f'Turbidity set to: {end_turb}')
            _ = algaemist.set_temp_day(end_temp)
            print(f'Temperature set to: {end_temp}')
            algaemist.wait(.5)
            
            print('Experiment finished successfully.')
            break
                
        else:
            print('Connection lost...')
            
    # Ensure reactor is in safe state at the end
    turb_set = algaemist.get_turb_setpoint()
    temp_set = algaemist.get_temp_setpoint()
    
    if turb_set != end_turb:
        _ = algaemist.set_turbidity(end_turb)
        print(f'Turbidity set to: {end_turb}')
    if temp_set != end_temp:
        _ = algaemist.set_temp_day(end_temp)
        print(f'Temperature set to: {end_temp}')
    algaemist.wait(.5)
    _ = algaemist.set_brightness(10)  # Reduce light for safety/storage
    print('Experiment finished and reactor set to safe conditions.')
    
else:
    print('Connection could not be established...')
