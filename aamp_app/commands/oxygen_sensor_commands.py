from typing import Tuple, List
from devices.oxygen_sensor import OxygenSensor
from .command import Command, CommandResult


class OxygenParentCommand(Command):
    """Parent class for DFRobot Oxygen Sensor Commands"""

    receiver_cls = OxygenSensor

    def __init__(self, receiver: OxygenSensor, **kwargs):
        super().__init__(receiver, **kwargs)


class OxygenConnect(Command):
    """Open the serial port to the oxygen sensor"""

    receiver_cls = OxygenSensor

    def __init__(self, receiver: OxygenSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())


class OxygenInitialize(OxygenParentCommand):
    """Initialize the oxygen sensor"""

    def __init__(self, receiver: OxygenSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())


class OxygenDeinitialize(OxygenParentCommand):
    """Deinitialize the oxygen sensor"""

    def __init__(self, receiver: OxygenSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())


class OxygenGetOxygen(OxygenParentCommand):
    """Read average oxygen data"""

    def __init__(self, receiver: OxygenSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_oxygen())
