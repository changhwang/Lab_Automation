from .device import ArduinoSerialDevice, check_initialized, check_serial
from typing import Optional, Tuple, Union

class HumiditySensor(ArduinoSerialDevice):

    def __init__(self, name: str, port: str, baudrate: int, timeout: Optional[float] = 1.0):
        super().__init__(name, port, baudrate, timeout)
    
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True
        #TODO Humidity sensor initialize
        return (True, "Humidity sensor initialized.")
    
    def deinitialize(self) -> Tuple[bool, str]:
        self._is_initialized = False
        #TODO Humidity sensor deinitialize
        return (True, "Humidity sensor deinitialized.")

    @check_serial
    @check_initialized
    def get_humidity(self) -> Tuple[bool, Union[float, str]]:
        #TODO Humidity sensor get humidity
        return (True, 0.0)
    
