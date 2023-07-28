from typing import List

from devices.festo_solenoid_valve import FestoSolenoidValve
from .command import Command, CommandResult

class FestoParentCommand(Command):
    """Parent class for all Festo Solenoid Valve commands."""
    receiver_cls = FestoSolenoidValve

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

class FestoInitialize(FestoParentCommand):
    """Initialize the solenoid valve"""

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class FestoDeinitialize(FestoParentCommand):
    """Deinitialize the solenoid valve"""

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())

class FestoValveOpen(FestoParentCommand):
    """Open the solenoid valve and keep open"""

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.valve_open())

class FestoValveClosed(FestoParentCommand):
    """Close the solenoid valve and keep closed"""

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.valve_closed())

class FestoOpenTimed(FestoParentCommand):
    """Open the valve for a set time then close"""

    def __init__(self, receiver: FestoSolenoidValve, time: int, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['time'] = time
    
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.open_timed(self._params['time']))

