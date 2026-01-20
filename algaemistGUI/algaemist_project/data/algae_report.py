# Generate a report on the algaemist system

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file = r'.\turb_test.csv'
columns = ['temp', 'pH',   'air', 'co2', 'turb_pump', 'light_prim', 'light_sec',]

y_axis_ranges = {
    "temp": (0, 45),
    "pH": (2, 12),
    "light_prim": (0, 850),
    "light_sec": (0, 850),
    "air": (0, 1000),
    "co2": (0, 200),
    "turb_pump": (-5, 100)
}

y_axis_units = {
    "temp": "Temperatur in [°C]",
    "pH": "pH",
    "light_prim": "Light Sensor Value",
    "light_sec": "",
    "air": "Airflow [ml/min]",
    "co2": "Co2 [ml/min]",
    "turb_pump": "Power in [%]"
}

data = pd.read_csv(file)

data['timestamp'] = pd.to_datetime(data['timestamp'])

# Get first and last timestamps
first_ts = data['timestamp'].min().strftime("%Y-%m-%d %H:%M")
last_ts = data['timestamp'].max().strftime("%Y-%m-%d %H:%M")

fig, axes = plt.subplots(3,2, figsize=(12,15), sharex=True)

# Rename the window
fig.canvas.manager.set_window_title("System Report Algaemist")

ax = axes.flatten()

for i in range(6):
    ax[i].plot(data['timestamp'], data[columns[i]], '.', label=columns[i])
    ax[i].set_ylim(y_axis_ranges[columns[i]])
    ax[i].set_ylabel(y_axis_units[columns[i]])
    ax[i].grid()
    if i == 5:
        ax[i].plot(data['timestamp'], data[columns[i+1]], '.', label=columns[i+1])
        ax[i].legend()
        ax[i].set_xlabel('timestamp')
    if i == 4:
        ax[i].set_xlabel('timestamp')
        
    # Format X-axis: major ticks every 12 hours
    ax[i].xaxis.set_major_locator(mdates.HourLocator(interval=12))
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%Y-%m-%d'))
    
# Set overall title with first and last timestamp
plt.suptitle(f"System report from {first_ts} to {last_ts}", size=18, weight='bold')

# plt.tight_layout()
plt.show()
