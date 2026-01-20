# reactor/config_manager.py
import json
import os
import logging

class ConfigManager:
    def __init__(self, filename="config.json"):
        self.filename = os.path.join(os.path.dirname(__file__), filename)
        self.config = {
            "reactor_addr": 21,
            "night_temp_sp2": 10.0,
            "chemostat_setpoint": 50,
            "external_ph_pump": 0
        }
        self.load()

    def load(self):
        """Load config from JSON file, fallback to defaults if missing."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.config.update(json.load(f))
                logging.info(f"Config loaded from {self.filename}")
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
        else:
            logging.info(f"No config file found, using defaults.")

    def save(self):
        """Save current config to JSON file."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.config, f, indent=4)
            #logging.info(f"Config saved to {self.filename}")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        """Return a config value, fallback to default."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Update a config value and save immediately."""
        self.config[key] = value
        self.save()
