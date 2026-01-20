import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_path = os.path.join(base_dir, "reactor_app.log")

    handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger