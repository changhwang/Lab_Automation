from .command import Command, CommandResult
from devices.kinova_arm import KinovaArm

# Parent class, subclass from Command ABC
class KinovaArmParentCommand(Command):
    """Parent class for all KinovaArm commands."""
    receiver_cls = KinovaArm

    def __init__(self, receiver: KinovaArm, **kwargs):
        super().__init__(receiver, **kwargs)

# Recommended command classes
class KinovaArmConnect(KinovaArmParentCommand):
    """Connect to the Kinova arm (TCP)."""

    def __init__(self, receiver: KinovaArm, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.connect())
        
class KinovaArmInitialize(KinovaArmParentCommand):
    def __init__(self, receiver: KinovaArm, **kwargs):
        super().__init__(receiver, **kwargs)
        
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class KinovaArmMoveArmAngular(KinovaArmParentCommand):
    def __init__(self, receiver: KinovaArm, pose_name: str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['pose_name'] = pose_name

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.move_arm_angular(self._params['pose_name']))

class KinovaArmExecuteAction(KinovaArmParentCommand):
    def __init__(self, receiver: KinovaArm, action_name: str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['action_name'] = action_name

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.execute_action(self._params['action_name']))

class KinovaArmOpenGripper(KinovaArmParentCommand):
    def __init__(self, receiver: KinovaArm, grip_speed: float = 0.2, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['grip_speed'] = grip_speed

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.open_gripper(self._params['grip_speed']))

class KinovaArmCloseGripper(KinovaArmParentCommand):
    def __init__(self, receiver: KinovaArm, grip_speed: float = -0.2, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['grip_speed'] = grip_speed
        
    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.close_gripper(self._params['grip_speed']))