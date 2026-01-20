# reactor/utils.py

import csv
import os
import logging
from datetime import datetime, timedelta
import threading
import time


class DataLogger:
    def __init__(self, path: str | None = None, auto: bool = False, interval: float = 1800):
        """
        CSV data logger.

        Args:
            path: Path to CSV file. Defaults to ./data/data_log_<timestamp>.csv
            auto: If True, will start auto logging (requires reactor to call `log_manual` or `log_from_reactor` in _auto_loop).
            interval: Seconds between auto logging iterations.
        """
        self.interval = interval

        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.getcwd(), f"data/data_log_{timestamp}.csv")
        self.path = path

        # Create CSV with headers if it doesn't exist
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "temp", "pH", "light_prim", "light_sec",
                    "air", "co2", "heater_pump", "cooler_pump",
                    "co2_pump", "turb_pump", "comments"
                ])

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._reactor_getter: callable | None = None  # Function returning (sensors, pumps)

        if auto:
            self.start_auto()

    def log_values(self, sensors: dict, pumps: dict, comment: str | None = None, path: str | None = None):
        """Log sensor and pump values to CSV. Can override the path for this log."""
        file_path = path or self.path
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                timestamp,
                sensors.get("temp"),
                sensors.get("pH"),
                sensors.get("light_prim"),
                sensors.get("light_sec"),
                sensors.get("air"),
                sensors.get("co2"),
                pumps.get("heater_pump"),
                pumps.get("cooler_pump"),
                pumps.get("co2_pump"),
                pumps.get("turb_pump"),
                comment
            ]
            with open(file_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            logging.error(f"Failed to log data: {e}")
            
            
            
    def max_log_values(self, sensors: dict, pumps: dict, path: str | None = None, delta=72):
        """Log sensor & pump data, keep only last 72 hours."""
        file_path = path
        print('max_log called')
        try:
            timestamp = datetime.now()
            row = [
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                sensors.get("temp"),
                sensors.get("pH"),
                sensors.get("light_prim"),
                sensors.get("light_sec"),
                sensors.get("air"),
                sensors.get("co2"),
                pumps.get("heater_pump"),
                pumps.get("cooler_pump"),
                pumps.get("co2_pump"),
                pumps.get("turb_pump")
            ]

            # Read existing rows
            existing_rows = []
            if os.path.exists(file_path):
                with open(file_path, "r", newline="") as f:
                    reader = csv.reader(f)
                    # headers = next(reader)
                    for r in reader:
                        try:
                            ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")
                            existing_rows.append((ts, r))
                        except Exception as e:
                            logging.warning(f"Skipping invalid row in CSV: {r} -> {e}")
            
            # Append new row
            existing_rows.append((timestamp, row))

            # Keep only rows from last x hours
            cutoff = timestamp - timedelta(hours=delta)
            filtered_rows = [r for ts, r in existing_rows if ts >= cutoff]

            # Write back
            with open(file_path, "w", newline="") as f:
                print('file opend and writing..',file_path)
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "temp", "pH", "light_prim", "light_sec",
                    "air", "co2", "heater_pump", "cooler_pump",
                    "co2_pump", "turb_pump"
                ])
                writer.writerows(filtered_rows)

        except Exception as e:
            logging.error(f"Failed to log sensor data: {e}")
            

    def log_from_reactor(self, reactor, comment: str | None = None, path: str | None = None):
        """Read values from reactor and log them, optional path override."""
        if reactor._connected:
            sensors = reactor.read_all_sensors() or {}
            pumps = reactor.read_all_pumps() or {}
            self.log_values(sensors, pumps, comment=comment, path=path)

    def _auto_loop(self):
        """Background thread loop for auto logging."""
        while not self._stop_event.is_set():
            if self._reactor_getter:
                reactor = self._reactor_getter()
                if reactor:
                    self.log_from_reactor(reactor)
            time.sleep(self.interval)

    def start_auto(self, reactor_getter: callable):
        """
        Start automatic logging.

        reactor_getter: callable returning the reactor instance (e.g., `lambda: reactor`)
        """
        if self._thread and self._thread.is_alive():
            return  # Already running

        self._reactor_getter = reactor_getter
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._auto_loop, daemon=True)
        self._thread.start()
        logging.info("Auto data logging started.")

    def stop_auto(self):
        """Stop automatic logging."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        logging.info("Auto data logging stopped.")
        
    def set_path(self, path: str):
        """Set the CSV path for the DataLogger and create file if missing."""
        self.path = path

        # Ensure directory exists if specified
        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Create file with header if it doesn't exist
        if not os.path.exists(self.path):
            try:
                with open(self.path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp", "temp", "pH", "light_prim", "light_sec",
                        "air", "co2", "heater_pump", "cooler_pump",
                        "co2_pump", "turb_pump", "comments"
                    ])
            except Exception as e:
                logging.error(f"Failed to create DataLogger CSV file at {self.path}: {e}")
                raise

        logging.info(f"DataLogger path set to: {self.path}")