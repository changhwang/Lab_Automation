from typing import Tuple, List
from aamp_app.devices.sht85_sensor import SHT85HumidityTempSensor
from .command import Command, CommandResult


class SHT85ParentCommand(Command):
    """Parent class for SHT85 humidity and temperature sensor"""

    receiver_cls = SHT85HumidityTempSensor

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)


class SHT85Connect(Command):
    """Open the serial port to the SHT85 sensor."""

    receiver_cls = SHT85HumidityTempSensor

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())


class SHT85Initialize(SHT85ParentCommand):
    """Initialize the humidity and temperature sensor"""

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())


class SHT85Deinitialize(SHT85ParentCommand):
    """Deinitialize the humidity and temperature sensor"""

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())


class SHT85GetHumidity(SHT85ParentCommand):
    """Read humidity data"""

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_humidity())


class SHT85GetTemp(SHT85ParentCommand):
    """Read temperature data"""

    def __init__(self, receiver: SHT85HumidityTempSensor, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_temp())
