"""Requires 'StandardFirmata' basic example uploaded on Arduino Uno"""
from typing import Tuple, Optional
import time
import pyfirmata

from device import ArduinoSerialDevice, check_initialized, check_serial

class FestoSolenoidValve(ArduinoSerialDevice):

    def __init__(self, name: str, numchannel: int, port: str = "COM5", baudrate: int = 9600, timeout: float = 0.1):
        super().__init__(name, port, baudrate, timeout)
        self.board = pyfirmata.Arduino(self.port)
        self.pin = self.board.get_pin(f"d:{numchannel}:o")
    
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True
        #TODO: solenoid valve initialize
        return (True, "Solenoid valve initialized")
    
    def deinitialize(self) -> Tuple[bool, str]:
        self._is_initialized = False
        self.board.exit()
        return (True, "Solenoid valve deinitialized")

    @check_serial
    @check_initialized
    def valve_open(self) -> Tuple[bool, str]:
        self.pin.write(1)
        return (True, "Solenoid valve is open")
    
    def valve_closed(self) -> Tuple[bool, str]:
        self.pin.write(0)
        return (True, "Solenoid valve is closed")
    
    def open_timed(self, time: int) -> Tuple[bool, str]:
        self.pin.write(1)
        self.board.pass_time(time)
        self.pin.write(0)
        return (True, f"Solenoid valve was opened for {time} seconds")



    