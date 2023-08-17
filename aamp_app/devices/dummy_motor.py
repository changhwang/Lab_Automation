import time
from typing import Tuple

from .device import Device, check_initialized
from .dummy_motor_source import DummyMotorSource


class DummyMotor(Device):
    def __init__(self, name: str, speed: float = 20.0):
        super().__init__(name)
        # Want to inherit from Device to implement standard name and initialization attributes/methods
        # Using composition instead of multiple inheritance
        self.motor = DummyMotorSource(speed)

    def get_init_args(self) -> dict:
        args_dict = {
            "name": self._name,
            "speed": self.motor._speed,
        }
        return args_dict

    def update_init_args(self, args_dict: dict):
        self.motor._speed = args_dict["speed"]
        self._name = args_dict["name"]

    @property
    def position(self) -> float:
        return self.motor.position

    def get_position(self) -> float:
        return self.motor.position

    @property
    def speed(self) -> float:
        return self.motor.speed

    def get_speed(self) -> float:
        return self.motor.speed

    def initialize(self) -> Tuple[bool, str]:
        self.motor.home_motor()
        while self.motor._position != 0.0:
            print(
                "DummyMotor " + self.name + " position: " + str(self.motor._position),
                end="\r",
            )
            time.sleep(0.1)
        print(
            "DummyMotor " + self.name + " position: " + str(self.motor._position),
            end="\r",
        )
        self._is_initialized = True
        return (True, "Initialized DummyMotor by homing and setting position to zero")

    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        self.move_absolute(position=0.0)
        if reset_init_flag:
            self._is_initialized = False
        return (True, "Deinitialized DummyMotor by moving to position zero")

    def set_speed(self, speed: float):
        self.motor.speed = speed
        # if out of range, then the setter did nothing
        if self.motor.speed == speed:
            return (
                True,
                "DummyMotor speed was successfully set to " + str(self.motor.speed),
            )
        else:
            return (
                False,
                "DummyMotor speed was not set. Speed is currently "
                + str(self.motor.speed),
            )

    @check_initialized
    def move_absolute(self, position: float) -> Tuple[bool, str]:
        # if not self._is_initialized:
        #     return (False, "DummyMotor is not initialized")
        if not self.is_valid_position(position):
            return (False, "Position is not valid")

        self.motor.move_absolute(position)

        while self.motor.position != position:
            print(
                "DummyMotor " + self.name + " position: " + str(self.motor.position),
                end="\r",
            )
            time.sleep(0.1)
        print(
            "DummyMotor " + self.name + " position: " + str(self.motor.position),
            end="\r",
        )

        return (True, "DummyMotor has reached position " + str(position))

    @check_initialized
    def move_relative(self, distance: float) -> Tuple[bool, str]:
        # if not self._is_initialized:
        #     return (False, "DummyMotor is not initialized")

        position = self.motor.position + distance
        if not self.is_valid_position(position):
            return (False, "Position is not valid")

        self.motor.move_relative(distance)

        while self.motor.position != position:
            print(
                "DummyMotor " + self.name + " position: " + str(self.motor.position),
                end="\r",
            )
            time.sleep(0.1)
        print(
            "DummyMotor " + self.name + " position: " + str(self.motor.position),
            end="\r",
        )

        return (
            True,
            "DummyMotor has moved by "
            + str(distance)
            + " and reached position "
            + str(position),
        )

    def is_valid_position(self, position) -> bool:
        if position >= self.motor.min_position and position <= self.motor.max_position:
            return True
        else:
            return False
