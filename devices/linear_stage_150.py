from typing import Optional, Tuple
from .device import SerialDevice, check_serial, check_initialized

class LinearStage150(SerialDevice):
    def __init__(self, name: str, port: str, baudrate: int, timeout: float | None = 1):
        super().__init__(name, port, baudrate, timeout)
    
    @check_serial
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = False

        #TODO: initialize lts150, home it (if needed)

        self._is_initialized = True
        return (True, "Successfully initialized LTS150.")
        # return super().initialize()

    def deinitialize(self) -> Tuple[bool, str]:
        
        #TODO: deinitialize lts 150
        # if reset_init_flag: //used in other devices
        self._is_initialized = False
        return (True, "Successfully deinitialized LTS150.")
        # return super().deinitialize()
    
    @check_serial
    @check_initialized
    def get_enabled_state(self) -> bool:

        #TODO: lts150 get enabled state

        return False