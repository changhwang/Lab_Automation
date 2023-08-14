import threading
import random
from .device import MiscDeviceClass


class DummyMotorSource(MiscDeviceClass):
    def __init__(self, speed: float = 20.0):
        self._speed = speed
        self.min_speed = 5.0
        self.max_speed = 50.0
        self.min_position = 0.0
        self.max_position = 100.0
        self._position = random.uniform(self.min_position, self.max_position)
        self._hardware_interval = 0.05

    @property
    def position(self) -> float:
        return self._position

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, speed: float):
        if speed >= self.min_speed and speed <= self.max_speed:
            self._speed = speed

    def home_motor(self):
        self.move_absolute(position=0.0)

    # Move functions do not wait to reach target, it simply initiates the move
    def move_absolute(self, position: float):
        distance = position - self._position
        if distance > 0.0:
            self._hardware_move(position, 1)
        elif distance < 0.0:
            self._hardware_move(position, -1)

    def move_relative(self, distance: float):
        position = self._position + distance
        if distance > 0.0:
            self._hardware_move(position, 1)
        elif distance < 0.0:
            self._hardware_move(position, -1)

    # Emulates change in motor position
    def _hardware_move(self, target: float, direction: int):
        # direction is 1 or -1
        timer = threading.Timer(
            self._hardware_interval, self._hardware_move, [target, direction]
        )
        timer.start()
        distance_moved = self._speed * self._hardware_interval * direction

        if abs(target - self._position) <= abs(distance_moved):
            self._position = target
            timer.cancel()
        else:
            self._position += distance_moved
