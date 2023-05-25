from typing import Tuple
from .device import Device, check_initialized

class MFC(Device):

    def __init__(self, name: str):
        super().__init__(name)
    
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = False

        #TODO MFC initialize

        self._is_initialized = True
        return (True, "MFC Initialized.")

    @check_initialized
    def get_gas(self) -> float:
        self._gas = 0

        #TODO MFC get gas

        return self._gas

    @check_initialized
    def set_gas(self, gas: float) -> Tuple[bool, str]:

        #TODO MFC set gas

        return(True, "MFC Gas set to " + str(gas) + ".")
    