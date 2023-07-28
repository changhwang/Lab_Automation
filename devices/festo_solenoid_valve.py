# modules for device as of commit 4123ed0

"""Requires 'StandardFirmata' basic example uploaded on Arduino Uno"""
from typing import Tuple, Optional
import time
import pyfirmata

from .device import ArduinoSerialDevice, check_initialized, check_serial


class FestoSolenoidValve(ArduinoSerialDevice):
    def __init__(
        self,
        name: str,
        numchannel: int,
        port: str = "COM5",
        baudrate: int = 9600,
        timeout: float = 0.1,
    ):
        super().__init__(name, port, baudrate, timeout)
        self.board = pyfirmata.Arduino(self.port)
        self.numchannel = numchannel
        self.pin = self.board.get_pin(f"d:{numchannel}:o")

    def get_init_args(self) -> dict:
        args_dict = {
            "name": self.name,
            "numchannel": self.numchannel,
            "port": self.port,
            "baudrate": self.baudrate,
            "timeout": self.timeout,
        }
        return args_dict

    def update_init_args(self, args_dict: dict):
        self.name = args_dict["name"]
        self.numchannel = args_dict["numchannel"]
        self.port = args_dict["port"]
        self.pin = self.board.get_pin(f"d:{self.port}:o")  # TODO: Check if this is necessary
        self.baudrate = args_dict["baudrate"]
        self.timeout = args_dict["timeout"]

    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = True
        # TODO: solenoid valve initialize
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

    @check_serial
    def valve_closed(self) -> Tuple[bool, str]:
        self.pin.write(0)
        return (True, "Solenoid valve is closed")

    @check_serial
    def open_timed(self, time: int) -> Tuple[bool, str]:
        self.pin.write(1)
        self.board.pass_time(time)
        self.pin.write(0)
        return (True, f"Solenoid valve was opened for {time} seconds")
