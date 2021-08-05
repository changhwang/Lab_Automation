from .command import Command
from devices.multi_stepper import MultiStepper


#parent class for all MultiStepper commands
class MultiStepperParentCommand(Command):
    receiver_cls = MultiStepper

    def __init__(self, receiver: MultiStepper):
        super().__init__()
        self._receiver = receiver
        self._receiver_name = receiver.name


class MultiStepperConnect(MultiStepperParentCommand):
    # cls_name = "multi_stepper_connect"
    cls_description = "Open the one serial port for all stepper's controlled by a single arduino."
    
    def __init__(self, receiver: MultiStepper):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        # the serial port parameters should already be set in the StepperLinear instance
        self._was_successful, self._result_message = self._receiver.start_serial()
        
class MultiStepperInitialize(MultiStepperParentCommand):
    # cls_name = "multi_stepper_initialize"
    cls_description = "Initialize all passed steppers by homing them."
    
    def __init__(self, receiver: MultiStepper):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class MultiStepperDeinitialize(MultiStepperParentCommand):
    # cls_name = "multi_stepper_deinitialize"
    cls_description = "Deinitialize all passed steppers by homing them."

    def __init__(self, receiver: MultiStepper, reset_init_flag: bool = True):
        super().__init__(receiver)
        self._reset_init_flag = reset_init_flag
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._reset_init_flag)

class MultiStepperMoveAbsolute(MultiStepperParentCommand):
    # cls_name = "multi_stepper_move_absolute"
    cls_description = "Move stepper to absolute position."

    def __init__(self, receiver: MultiStepper, stepper_number: int, position: float):
        super().__init__(receiver)
        self._stepper_number = stepper_number
        self._position = position
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._stepper_number) + " " + str(self._position)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " StepperNum: " + str(self._stepper_number) + " Pos: " + str(self._position)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_absolute(self._stepper_number, self._position)

class MultiStepperMoveRelative(MultiStepperParentCommand):
    # cls_name = "multi_stepper_move_relative"
    cls_description = "Move stepper by relative distance."

    def __init__(self, receiver: MultiStepper, stepper_number: int, distance: float):
        super().__init__(receiver)
        self._stepper_number = stepper_number
        self._distance = distance
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._stepper_number) + " " + str(self._distance)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " StepperNum: " + str(self._stepper_number) + " Dist: " + str(self._distance)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_relative(self._stepper_number, self._distance)