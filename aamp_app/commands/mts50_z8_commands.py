from aamp_app.devices.device import Device
from .command import Command, CommandResult
from aamp_app.devices.mts50_z8 import MTS50_Z8


class MTS50_Z8ParentCommand(Command):
    """Parent class for all MTS50_Z8 commands."""

    receiver_cls = MTS50_Z8

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)


class MTS50_Z8Connect(MTS50_Z8ParentCommand):
    """Open a serial port for the stage."""

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())


class MTS50_Z8Initialize(MTS50_Z8ParentCommand):
    """Initialize the stage by homing it."""

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())


class MTS50_Z8Deinitialize(MTS50_Z8ParentCommand):
    """Deinitialize the stage."""

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())


class MTS50_Z8EnableMotor(MTS50_Z8ParentCommand):
    """Enable the stage motor."""

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params["state"] = True

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.set_enabled_state(self._params["state"])
        )


class MTS50_Z8DisableMotor(MTS50_Z8ParentCommand):
    """Disable the stage motor."""

    def __init__(self, receiver: MTS50_Z8, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params["state"] = False

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.set_enabled_state(self._params["state"])
        )


class MTS50_Z8MoveAbsolute(MTS50_Z8ParentCommand):
    """Move the stage to an absolute position."""

    def __init__(self, receiver: MTS50_Z8, position: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params["position"] = position

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.move_absolute(self._params["position"])
        )


class MTS50_Z8MoveRelative(MTS50_Z8ParentCommand):
    """Move the stage by a relative distance."""

    def __init__(self, receiver: MTS50_Z8, distance: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params["distance"] = distance

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.move_relative(self._params["distance"])
        )
