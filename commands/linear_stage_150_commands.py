from devices.device import Device
from .command import Command, CommandResult
from devices.linear_stage_150 import LinearStage150


class LinearStage150ParentCommand(Command):
    """Parent class for all LinearStage150 commands."""
    receiver_cls = LinearStage150

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)

class LinearStage150Connect(LinearStage150ParentCommand):
    """Open a serial port for the linear stage."""

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial()) #TODO: check this (autocomplete did not show start serial method)

class LinearStage150Initialize(LinearStage150ParentCommand):
    """Initialize the linear stage by homing it."""

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class LinearStage150Deinitialize(LinearStage150ParentCommand):
    """Deinitialize the linear stage."""
    
    #TODO: command to deinitialize lts150

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())

class LinearStage150EnableMotor(LinearStage150ParentCommand):
    """Enable the linear stage motor."""

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['state'] = True
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_enabled_state(self._params['state']))
    
class LinearStage150DisableMotor(LinearStage150ParentCommand):
    """Disable the linear stage motor."""

    def __init__(self, receiver: LinearStage150, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['state'] = False
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_enabled_state(self._params['state']))

class LinearStage150MoveAbsolute(LinearStage150ParentCommand):
    """Move the linear stage to an absolute position."""

    def __init__(self, receiver: LinearStage150, position: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['position'] = position
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_absolute(self._params['position']))