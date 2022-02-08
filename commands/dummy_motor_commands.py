from typing import List

from .command import Command, CommandResult, CompositeCommand
from devices.dummy_motor import DummyMotor

class DummyMotorParentCommand(Command):
    """Parent class for all DummyMotor commands."""
    receiver_cls = DummyMotor

    def __init__(self, receiver: DummyMotor, **kwargs):
        super().__init__(receiver, **kwargs)

class DummyMotorInitialize(DummyMotorParentCommand):
    """Initialize the motor by homing it."""
    
    def __init__(self, receiver: DummyMotor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        # original method, tuple unpack into pre-existing attributes
        # self._result._was_successful, self._result._message = self._receiver.initialize()

        # alternate method, tuple unpack positionally into constructor
        self._result = CommandResult(*self._receiver.initialize())

class DummyMotorDeinitialize(DummyMotorParentCommand):
    """Deinitialize the motor by moving to position zero."""
    
    def __init__(self, receiver: DummyMotor, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize(self._params['reset_init_flag']))

class DummyMotorSetSpeed(DummyMotorParentCommand):
    """Set the speed of the motor."""

    def __init__(self, receiver: DummyMotor, speed: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['speed'] = speed

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_speed(self._params['speed']))

class DummyMotorMoveAbsolute(DummyMotorParentCommand):
    """Move motor to absolute position."""

    def __init__(self, receiver: DummyMotor, position: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['position'] = position

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_absolute(self._params['position']))

class DummyMotorMoveRelative(DummyMotorParentCommand):
    """Move motor by relative distance."""

    def __init__(self, receiver: DummyMotor, distance: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['distance'] = distance

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_relative(self._params['distance']))


# Composite command that may have one receiver, more than one receiver of the same or different type, or no receiver at all
class DummyMotorMoveSpeedAbsolute(CompositeCommand):
    """Temporarily set the speed and move to position. Speed then reverts to its original value."""

    def __init__(self, receiver: DummyMotor, speed: float, position: float, **kwargs):
        super().__init__(**kwargs)
        original_speed = receiver.motor.speed
        self.add_command(DummyMotorSetSpeed(receiver, speed))
        self.add_command(DummyMotorMoveAbsolute(receiver, position))
        self.add_command(DummyMotorSetSpeed(receiver, original_speed))

class DummyMotorMultiMoveAbsolute(CompositeCommand):
    """Move a list of motors to a list of position at a particular speed"""

    def __init__(self, receiver_list: List[DummyMotor], position_list: List[float], speed: float, **kwargs):
        super().__init__(**kwargs)
        for ndx, receiver in enumerate(receiver_list):
            self.add_command(DummyMotorSetSpeed(receiver, speed))
            self.add_command(DummyMotorMoveAbsolute(receiver, position_list[ndx]))

class DummyMotorMultiInitialize(CompositeCommand):
    """Initialize a list of motors"""

    def __init__(self, receiver_list: List[DummyMotor], **kwargs):
        super().__init__(**kwargs)
        for receiver in receiver_list:
            self.add_command(DummyMotorInitialize(receiver))


