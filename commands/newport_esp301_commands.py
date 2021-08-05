from .command import Command, CompositeCommand
from devices.newport_esp301 import NewportESP301
from typing import Optional

# Parent class, subclass from Command ABC
class NewportESP301ParentCommand(Command):
    receiver_cls = NewportESP301

    def __init__(self, receiver: NewportESP301):
        super().__init__()
        self._receiver = receiver
        self._receiver_name = receiver.name

# Recommended command classes
class NewportESP301Connect(NewportESP301ParentCommand):
    cls_description = "Open the serial port to the ESP301 controller."

    def __init__(self, receiver: NewportESP301):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.start_serial()

class NewportESP301Initialize(NewportESP301ParentCommand):
    cls_description = "Initialize the axes by homing them."
    
    def __init__(self, receiver: NewportESP301):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class NewportESP301Deinitialize(NewportESP301ParentCommand):
    cls_description = "Deinitialize the axes by moving them to position zero."
    
    def __init__(self, receiver: NewportESP301, reset_init_flag: bool = True):
        super().__init__(receiver)
        self._reset_init_flag = reset_init_flag
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._reset_init_flag)

# Device-related commands classes
class NewportESP301MoveSpeedAbsolute(NewportESP301ParentCommand):
    cls_description = "Move axis to absolute position at specific speed (No speed uses default speed)."
    
    def __init__(self, receiver: NewportESP301, position: float, speed: Optional[float] = None, axis_number: int = 1):
        super().__init__(receiver)
        self._position = position
        self._speed = speed
        self._axis_number = axis_number
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._position) + " " + str(self._speed) + " " + str(self._axis_number)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Pos: " + str(self._position) + " Speed: " + str(self._speed) + " AxisNum: " + str(self._axis_number)
    
    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_speed_absolute(self._position, self._speed, self._axis_number)

class NewportESP301MoveSpeedRelative(NewportESP301ParentCommand):
    cls_description = "Move axis by relative distance at specific speed (No speed uses default speed)."
    
    def __init__(self, receiver: NewportESP301, distance: float, speed: Optional[float] = None, axis_number: int = 1):
        super().__init__(receiver)
        self._distance = distance
        self._speed = speed
        self._axis_number = axis_number
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._distance) + " " + str(self._speed) + " " + str(self._axis_number)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Dist: " + str(self._distance) + " Speed: " + str(self._speed) + " AxisNum: " + str(self._axis_number)
    
    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.move_speed_relative(self._distance, self._speed, self._axis_number)

# Example of command with additional logic to determine the returned tuple of (success/fail: bool, success/fail message: str)
class NewportESP301SetDefaultSpeed(NewportESP301ParentCommand):
    cls_description = "Set the default speed of the axes."
    
    def __init__(self, receiver: NewportESP301, speed: float):
        super().__init__(receiver)
        self._speed = speed
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._speed)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Speed: " + str(self._speed)

    def execute(self) -> None:
        self._receiver.default_speed = self._speed
        # receiver's default_speed has a setter than checks the value is > 0 and < max_speed before setting
        # therefore, we can check if we actually changed the receiver's default speed, if not, it means the speed was out of range
        if self._receiver.default_speed == self._speed:
            return (True, "Default speed successfully set to " + str(self._speed))
        else:
            return (False, "Failed to set the default speed to " + str(self._speed) + ". The default speed must be > 0 and < " + str(self._receiver._max_speed))

# Just for testing composite commands
class NewportESP301Dance(CompositeCommand):
    def __init__(self, receiver, speed, distance):
        super().__init__()
        self.add_command(NewportESP301MoveSpeedRelative(receiver, -distance, speed))
        self.add_command(NewportESP301MoveSpeedRelative(receiver, distance, speed))