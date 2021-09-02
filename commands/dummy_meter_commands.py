from .command import Command
from devices.dummy_meter import DummyMeter

class DummyMeterParentCommand(Command):
    """Parent class for all DummyMeter commands."""
    receiver_cls = DummyMeter

    def __init__(self, receiver: DummyMeter, **kwargs):
        super().__init__(receiver, **kwargs)

class DummyMeterInitialize(DummyMeterParentCommand):
    """Initialize the meter."""
    
    def __init__(self, receiver: DummyMeter, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class DummyMeterDeinitialize(DummyMeterParentCommand):
    """Deinitialize the meter."""
    
    def __init__(self, receiver: DummyMeter, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._params['reset_init_flag'])

class DummyMeterMeasure(DummyMeterParentCommand):
    """Measure data and save to file."""

    def __init__(self, receiver: DummyMeter, filename: str = None, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['filename'] = filename

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.measure(self._params['filename'])