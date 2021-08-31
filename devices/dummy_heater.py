import threading
import time
from typing import Tuple
import random

from .device import Device

class DummyHeater(Device):

    def __init__(self, name: str, heat_rate: float = 20.0):
        super().__init__(name)
        self._heat_rate = heat_rate
        self.min_heat_rate = 1.0
        self.max_heat_rate = 50.0
        self.min_temperature = 25.0
        self.max_temperature = 100.0
        self._temperature = random.uniform(self.min_temperature, self.max_temperature)
        self._hardware_interval = 0.05

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def heat_rate(self) -> float:
        return self._heat_rate

    @heat_rate.setter
    def heat_rate(self, heat_rate: float):
        if heat_rate >= self.min_heat_rate and heat_rate <= self.max_heat_rate:
            self._heat_rate = heat_rate
        # The logic for success bool and result message is implemented in the SetHeatRate command
    
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True # this would normally go at the end of this method, but it needs to be true to set temp
        self.set_temp(25.0)
        return (True, "Initialized DummyHeater by setting to room temperature (25 C)")

    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        self.set_temp(25.0)
        if reset_init_flag:
            self._is_initialized = False
        return (True, "Deinitialized DummyHeater by setting to room temperature (25 C)")

    # set_temp waits for "hardware" to reach temperature set point before returning
    def set_temp(self, temperature: float) -> Tuple[bool, str]:
        if not self._is_initialized:
            return (False, "DummyHeater is not initialized")
        if not self.is_valid_temp(temperature):
            return (False, "Temperature setpoint is invalid")

        temp_diff = temperature - self._temperature
        if temp_diff > 0.0:
            self._hardware_heat(temperature, 1)
        elif temp_diff < 0.0:
            self._hardware_heat(temperature, -1)

        while self._temperature != temperature:
            print("DummyHeater " + self.name + " temperature: " + str(self._temperature), end='\r')
            time.sleep(.1)
            

        return (True, "DummyHeater temperature has stabilized at " + str(temperature))

    def is_valid_temp(self, temperature: float) -> bool:
        if temperature >= self.min_temperature and temperature <= self.max_temperature:
            return True
        else:
            return False

    # Emulates constant temperature change
    def _hardware_heat(self, target: float, direction: int):
        # direction is 1 or -1
        timer = threading.Timer(self._hardware_interval, self._hardware_heat, [target, direction])
        timer.start()
        temperature_change = self._heat_rate * self._hardware_interval * direction

        if abs(target - self._temperature) <= abs(temperature_change):
            self._temperature = target
            timer.cancel()
        else:
            self._temperature += temperature_change