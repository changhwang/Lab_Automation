from .command import Command
from devices.heating_stage import HeatingStage

#parent class for all HeatingStage commands
class HeatingStageParentCommand(Command):
    receiver_cls = HeatingStage

    def __init__(self, receiver: HeatingStage, **kwargs):
        super().__init__(receiver, **kwargs)

class HeatingStageConnect(HeatingStageParentCommand):
    """Open serial port of heating stage's arduino controller."""
    
    def __init__(self, receiver: HeatingStage, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        # the serial port parameters should already be set in the HeatingStage instance
        self._was_successful, self._result_message = self._receiver.start_serial()

class HeatingStageInitialize(HeatingStageParentCommand):
    """Initialize heating stage by setting to room temperature and turning PID ON."""
    
    def __init__(self, receiver: HeatingStage, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class HeatingStageDeinitialize(HeatingStageParentCommand):
    """Deinitialize heating stage by setting to room temperature and turning PID OFF."""
    
    def __init__(self, receiver: HeatingStage, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._params['reset_init_flag'])


class HeatingStageSetTemp(HeatingStageParentCommand):
    """Set heating stage temperature. Execution completes when stabilized."""
    
    def __init__(self, receiver: HeatingStage, temperature: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['temperature'] = temperature

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.set_temp(self._params['temperature'])

class HeatingStageSetSetPoint(HeatingStageParentCommand):
    """Set heating stage setpoint temperature. Execution completes immediately after setting setpoint, even if temperature is not stabilized."""
    
    def __init__(self, receiver: HeatingStage, temperature: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['temperature'] = temperature

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.set_settemp(self._params['temperature'])
