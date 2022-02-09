from typing import List

from .device import Device, check_initialized

# Importing Dummy devices only for emulation purposes
import numpy as np
import pandas as pd
from datetime import datetime
from .dummy_heater import DummyHeater
from .dummy_motor import DummyMotor


# Given a parameter space of x1 and x2, bounded by x1_range and x2_range
# emulate a noisy potential energy surface as an objective function by 
# multiplying two fourier series from coefficients a1, b1 and a2, b2
# Then perform a "measurement" by sampling a point of the objective surface

# The two parameters x1, x2 in this case are a DummyHeater's temperature and a DummyMotor's speed
# This can be thought of as emulating a printing system where a material is processed at a certain temperature and speed
# Then the DummyMeter takes a "measurement" of the material and stores the data
class DummyMeter(Device):
    save_directory = 'data/dummy_meter/'

    def __init__(
            self, 
            name: str, 
            heater: DummyHeater,
            motor: DummyMotor,
            a1: List[float], 
            b1: List[float], 
            a2: List[float], 
            b2: List[float], 
            noise_width: float = 0.0
            ):
        super().__init__(name)
        # All arguments except 'name' are only for emulation purposes
        self.heater = heater
        self.motor = motor
        self.x1_range = (heater.min_temperature, heater.max_temperature)
        self.x2_range = (motor.motor.min_speed, motor.motor.max_speed)
        self.a1 = a1
        self.b1 = b1
        self.a2 = a2
        self.b2 = b2
        self.noise_width = noise_width

    def initialize(self):
        self._is_initialized = True
        return (True, "Initialized DummyMeter")

    def deinitialize(self, reset_init_flag: bool = True):
        if reset_init_flag:
            self._is_initialized = False
        return (True, "Deinitialized DummyMeter")

    @check_initialized
    def measure(self, filename: str = None):
        # if not self._is_initialized:
        #     return (False, "DummyMeter is not initialized")

        # Emulating dependency on temperature and speed
        x1 = self.heater.temperature
        x2 = self.motor.speed

        # Take a "measurement"
        data = self.fourier2d(
            [x1, x2],
            self.x1_range,
            self.x2_range,
            self.a1,
            self.b1,
            self.a2,
            self.b2,
            self.noise_width
            )
        
        # Store the measured data to a csv file
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = timestamp

        dataframe = pd.DataFrame()
        dataframe['Temperature'] = [x1]
        dataframe['Speed'] = [x2]
        dataframe['Data'] = [data]
        
        fullfilename = self.save_directory + filename + '.csv'
        dataframe.to_csv(fullfilename, mode='w', index=False)

        return (True, "Measured data and saved to file at " + fullfilename)
    
    @staticmethod
    def fourier2d(x, x1_range, x2_range, a1, b1, a2, b2, noise_width) -> float:
        x1 = x[0]
        x2 = x[1]
        x1_min = x1_range[0]
        x1_max = x1_range[1]
        x2_min = x2_range[0]
        x2_max = x2_range[1]
        w1 = 2 * np.pi / (x1_max - x1_min)
        w2 = 2 * np.pi / (x2_max - x2_min)

        f1 = 0
        f2 = 0

        for i in range(a1.shape[0]):
            f1 += a1[i]*np.cos(i*x1*w1) + b1[i]*np.sin(i*x1*w1)
            f2 += a2[i]*np.cos(i*x2*w1) + b2[i]*np.sin(i*x2*w1)

        f = f1 * f2
        if noise_width:
            f += np.random.normal(0, noise_width)
        return f[0]

