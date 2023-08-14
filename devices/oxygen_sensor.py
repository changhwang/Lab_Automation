from device import ArduinoSerialDevice, check_initialized, check_serial
import serial
from time import sleep
from typing import Optional, Tuple


class OxygenSensor(ArduinoSerialDevice):
    def __init__(
        self, name: str, port: str, baudrate: int = 9600, timeout: Optional[float] = 1.0
    ):
        super().__init__(name, port, baudrate, timeout)
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE

    def initialize(self) -> Tuple[bool, str]:
        self.ser.setDTR(False)
        self.ser.flushInput()
        self.ser.setDTR(True)
        self._is_initialized = True
        return (True, "Initialized oxygen sensor")

    def deinitialize(self) -> Tuple[bool, str]:
        self.ser.close()
        self._is_initialized = False
        return (True, "Deinitialized oxygen sensor")

    @check_serial
    @check_initialized
    def get_oxygen(self) -> Tuple[bool, float, str]:
        self.ser.write(b"O")
        sleep(0.75)
        oxygen = float(self.ser.readline().strip().decode())
        return (True, f"Oxygen concentration is {oxygen} %vol")
