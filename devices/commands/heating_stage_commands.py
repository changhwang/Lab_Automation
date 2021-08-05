from .command import Command
from ..heating_stage import HeatingStage

#parent class for all HeatingStage commands
class HeatingStageParentCommand(Command):
    receiver_cls = HeatingStage

    def __init__(self, receiver: HeatingStage):
        super().__init__()
        self._receiver = receiver
        self._receiver_name = receiver.name


class HeatingStageConnect(HeatingStageParentCommand):
    # cls_name = "heating_stage_connect"
    cls_description = "Open serial port of heating stage's arduino controller."
    
    def __init__(self, receiver: HeatingStage):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        # the serial port parameters should already be set in the HeatingStage instance
        self._was_successful, self._result_message = self._receiver.start_serial()

class HeatingStageInitialize(HeatingStageParentCommand):
    # cls_name = "heating_stage_initialize"
    cls_description = "Initialize heating stage by setting to room temperature and turning PID ON."
    
    def __init__(self, receiver: HeatingStage):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class HeatingStageDeinitialize(HeatingStageParentCommand):
    # cls_name = "heating_stage_deinitialize"
    cls_description = "Deinitialize heating stage by setting to room temperature and turning PID OFF."
    
    def __init__(self, receiver: HeatingStage, reset_init_flag: bool = True):
        super().__init__(receiver)
        self._reset_init_flag = reset_init_flag
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._reset_init_flag)


class HeatingStageSetTemp(HeatingStageParentCommand):
    # cls_name = "heating_stage_set_temp"
    cls_description = "Set heating stage temperature, returns when stabilized."
    
    def __init__(self, receiver: HeatingStage, temperature: float):
        super().__init__(receiver)
        self._temperature = temperature
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._temperature)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Temp: " + str(self._temperature)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.set_temp(self._temperature)

