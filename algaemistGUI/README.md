# AlgaemistGUI

A modular, user-friendly control and data-logging system for the  **Algaemist photobioreactor** .

This software provides both a Python API and an interactive graphical interface, enabling reliable operation for users with or without programming experience.

---

## ✨ Features

* **Modular architecture** separating hardware communication, experiment logic, and GUI components
* **Interactive GUI** built with *CustomTkinter* for intuitive, non-programmatic use
* **Full Python API** for advanced automation and scripting
* **Continuous data logging** (manual and automatic) with automatic file management
* **Thread-safe operation** to prevent UI blocking and ensure smooth experiment control
* **Extensive error handling** and event logging for traceability and safety

---

## 🧩 Project Structure

```
algaemist_project/
│
├── reactor/
│   ├── reactor.py
│   ├── connection.py
│   ├── logger.py
│   └── utils.py
│   
└── algaemistGUI/
    ├── gui.py
    ├── interface_subclasses.py
    └── config_manager.py
```

---

## ⚙️ Reactor Module

The core logic of the software resides in the  **Reactor module** , which encapsulates communication, experiment routines, and data logging.

### **Subsystems**

#### 1. Hardware Communication & Logging

* Manages serial communication with the Algaemist reactor
* Logs events, errors, and sensor data
* Stores values in CSV files
* Maintains the most recent 72 hours of data to limit file size

#### 2. Experiment Planning

* Enables definition, execution, and storage of experiment configurations
* Designed for modular extension and automated workflows

---

### `reactor.py` — Reactor Class

This script defines the central control class. Typical responsibilities include:

* Sending commands to the reactor hardware
* Parsing and validating responses
* Handling sensor queries (e.g., pH, temperature, light intensity)
* Logging errors and unexpected return values
* Returning processed Python data types or `None` on invalid responses
* Ensuring actuator commands return `True` on success or log an error otherwise

---

### `connection.py` — Serial Communication

Handles discovery and communication with supported devices:

* `list_ports()` identifies FTDI-manufactured hardware
* `open_connection()` creates a serial link at  **9600 baud** , with a **1 s timeout**
* Prevents blocking during hardware inactivity
* Manages reconnection and communication stability

---

### `logger.py` — Centralized Logging

* Implements centralized logging using Python’s `logging` module.
* Logs are written to **reactor_app.log** with timestamps and severity levels.
* A `RotatingFileHandler` keeps files under **5 MB** and retains up to three backups.
* Captures essential info, warnings, and errors while avoiding verbose debug output.

---

### `utils.py` — Continuous Data Logging

Implements the `DataLogger` class:

* Creates timestamped CSV files with headers for all measured variables
* Auto-creates directory structures
* Supports manual logging or automatic background logging
* Background logging runs in a dedicated thread and does not interrupt reactor communication
* Maintains rolling data of the last **72 hours**
* Allows dynamic reconfiguration of logging paths

---

## 🖥️ Algaemist GUI

The `algaemistGUI` module provides a clean, structured visual interface for reactor control.

### Overview

The GUI consists of:

* `gui.py` — Application controller
* `interface_subclasses.py` — Reusable UI frame templates
* `config_manager.py` — Persisted configuration parameters

The interface displays real-time sensor values and provides intuitive controls for interacting with the reactor.

### `gui.py` — Main Application

* Loads configuration parameters
* Connects to the reactor and synchronizes its internal clock
* Divides the interface into functional frames (temperature, pH, lighting, gas flow, reactor control)
* Updates sensor values continuously in a dedicated thread
* Maintains an emergency log of critical values every 10 minutes

---

### `interface_subclasses.py` — UI Components

Each frame follows a consistent design pattern:

* Graphical elements created via Tkinter’s grid system
* `update()` methods refresh sensor readings dynamically
* Input fields include validation, security prompts, and automatic retry on failure
* Uniform error handling and logging across all interface elements

#### Frame Types

* **ConnectionFrame** — Displays connection status; updates every 10 seconds
* **TemperatureFrame** — Shows temperature and heating/cooling power; allows day/night setpoints
* **PHFrame** — Displays current pH and control activity; handles pump mode switching
* **LightFrame** — Controls lighting modes (continuous, timed, sinusoidal) with validated inputs
* **GasFrame** — Shows air and CO₂ flow (read-only)
* **ReactorFrame** — Configures operational modes (turbidostat, chemostat, timed variants) and pump setpoints

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/algaemist_project.git
cd algaemist_project
pip install -r requirements.txt
```

Python **3.10.7** is recommended (the version used for development).

---

## ▶️ Running the GUI

```bash
python3 main.py
```

---

## ⚡ Using the Python API

Example:

```python
from reactor.reactor import Reactor

r = Reactor()
temperature = r.get_temperature()
r.set_temperature(25)
```

Add automation, custom experiments, or batch processing using standard Python scripts.
