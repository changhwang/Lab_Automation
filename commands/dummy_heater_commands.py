from .command import Command, CompositeCommand
from devices.dummy_heater import DummyHeater

class DummyHeaterParentCommand(Command):
    """Parent class for all DummyHeater commands."""
    receiver_cls = DummyHeater

    def __init__(self, receiver: DummyHeater, **kwargs):
        super().__init__(receiver, **kwargs)

class DummyHeaterInitialize(DummyHeaterParentCommand):
    """Initialize the heater by setting to room temp (25 C)."""
    
    def __init__(self, receiver: DummyHeater, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class DummyHeaterDeinitialize(DummyHeaterParentCommand):
    """Deinitialize the heater by setting to room temp (25 C)."""
    
    def __init__(self, receiver: DummyHeater, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._params['reset_init_flag'])

class DummyHeaterSetHeatRate(DummyHeaterParentCommand):
    """Set the heating rate of the heater."""

    def __init__(self, receiver: DummyHeater, heat_rate: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['heat_rate'] = heat_rate

    def execute(self) -> None:
        self._receiver.heat_rate = self._params['heat_rate']

        # logic implemented here because heat_rate setter does not return Tuple[bool, str]
        if self._receiver.heat_rate == self._params['heat_rate']:
            self._was_successful, self._result_message = (True, "Successfully set DummyHeater heat rate to " + str(self._receiver.heat_rate))
        else:
            self._was_successful, self._result_message = (False, "Failed to set DummyHeater heat rate. Heat rate is currently " + str(self._receiver.heat_rate))

class DummyHeaterSetTemp(DummyHeaterParentCommand):
    """Set the temperature of the heater and wait for it to stabilize."""

    def __init__(self, receiver: DummyHeater, temperature: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['temperature'] = temperature

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.set_temp(self._params['temperature'])

# Composite command example
class DummyHeaterRampHoldRamp(CompositeCommand):
    """Ramps up to temperature1 @ rate1, holds for specified time, then ramps to temperature2 @ rate2"""

    def __init__(
            self, 
            receiver: 
            DummyHeater, 
            temp1: float, 
            rate1: float, 
            hold_time: float, 
            temp2: float, 
            rate2: float,
            **kwargs):
        super().__init__(**kwargs)
        self.add_command(DummyHeaterSetHeatRate(receiver, rate1))
        self.add_command(DummyHeaterSetTemp(receiver, temp1))
        self.add_command(DummyHeaterSetHeatRate(receiver, rate2, delay=hold_time))
        self.add_command(DummyHeaterSetTemp(receiver, temp2))
