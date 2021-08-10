from .command import Command
from devices.multi_stepper import MultiStepper


#parent class for all MultiStepper commands
class MultiStepperParentCommand(Command):
    receiver_cls = MultiStepper

    def __init__(self, receiver: MultiStepper, **kwargs):
        super().__init__(receiver, **kwargs)

class MultiStepperConnect(MultiStepperParentCommand):
    """Open the one serial port for all stepper's controlled by a single arduino."""
    
    def __init__(self, receiver: MultiStepper, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        # the serial port parameters should already be set in the StepperLinear instance
        self._was_successful, self._result_message = self._receiver.start_serial()
        
class MultiStepperInitialize(MultiStepperParentCommand):
    """Initialize all passed steppers by homing them."""
    
    def __init__(self, receiver: MultiStepper, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class MultiStepperDeinitialize(MultiStepperParentCommand):
    """Deinitialize all passed steppers by zeroing them."""

    def __init__(self, receiver: MultiStepper, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._params['reset_init_flag'])

class MultiStepperMoveAbsolute(MultiStepperParentCommand):
    """Move stepper to absolute position."""

    def __init__(self, receiver: MultiStepper, stepper_number: int, position: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['stepper_number'] = stepper_number
        self._params['position'] = position

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_absolute(self._params['stepper_number'], self._params['position'])

class MultiStepperMoveRelative(MultiStepperParentCommand):
    """Move stepper by relative distance."""

    def __init__(self, receiver: MultiStepper, stepper_number: int, distance: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['stepper_number'] = stepper_number
        self._params['distance'] = distance

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_relative(self._params['stepper_number'], self._params['distance'])