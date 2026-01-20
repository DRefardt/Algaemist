# reactor/connection.py
import serial
import serial.tools.list_ports

def list_ports(manufacturer=None):
    """Return list of matching ports."""
    ports = []
    for port in serial.tools.list_ports.comports():
        if manufacturer and manufacturer not in (port.manufacturer or ""):
            continue
        ports.append(port.device)
    return ports

def open_connection(port, baudrate=9600, timeout=1):
    """Open and return a serial connection."""
    return serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
    )