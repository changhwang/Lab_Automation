from typing import Tuple, Optional
import serial

from .device import ArduinoSerialDevice, check_initialized, check_serial

class FestoSolenoidValve(ArduinoSerialDevice):

    def __init__(self, name: str, port: str, baudrate: int, timeout: float):
        super().__init__(name, port, baudrate, timeout)
    
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True
        #TODO solenoid valve initialize
        return (True, "Solenoid valve initialized")
    
    def deinitialize(self) -> Tuple[bool, str]:
        self._is_initialized = False
        #TODO solenoid valve deinitialize
        return (True, "Solenoid valve deinitialized")

    @check_serial
    @check_initialized
    def valve_open(self) -> Tuple[bool, str]:
        #TODO activate solenoid valve
        return (True, "Solenoid valve is open")