from .command import Command, CommandResult
from aamp_app.devices.psd6_syringe_pump import PSD6SyringePump
from typing import Optional


# Parent class, subclass from Command ABC
class PSD6SyringePumpParentCommand(Command):
    """Parent class for all PSD6SyringePump commands."""

    receiver_cls = PSD6SyringePump

    def __init__(self, receiver: PSD6SyringePump, **kwargs):
        super().__init__(receiver, **kwargs)


# Recommended command classes
class PSD6SyringePumpConnect(PSD6SyringePumpParentCommand):
    """Open the serial port to the PSD6 syringe pump."""

    def __init__(self, receiver: PSD6SyringePump, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.start_serial())


class PSD6SyringePumpInitialize(PSD6SyringePumpParentCommand):
    def __init__(self, receiver: PSD6SyringePump, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())


class PSD6SyringePumpMoveValve(PSD6SyringePumpParentCommand):
    def __init__(self, receiver: PSD6SyringePump, valve_num: int, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params["valve_num"] = valve_num

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.move_valve_position(self._params["valve_num"])
        )


class PSD6SyringePumpMoveAbsolute(PSD6SyringePumpParentCommand):
    def __init__(
        self,
        receiver: PSD6SyringePump,
        volume: float,
        valve_num: Optional[int] = None,
        flowrate: Optional[float] = None,
        **kwargs
    ):
        super().__init__(receiver, **kwargs)
        self._params["volume"] = volume
        self._params["valve_num"] = valve_num
        self._params["flowrate"] = flowrate

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.move_syringe_absolute_volume(
                self._params["volume"],
                self._params["valve_num"],
                self._params["flowrate"],
            )
        )


class PSD6SyringePumpInfuse(PSD6SyringePumpParentCommand):
    def __init__(
        self,
        receiver: PSD6SyringePump,
        volume: float,
        valve_num: Optional[int] = None,
        flowrate: Optional[float] = None,
        **kwargs
    ):
        super().__init__(receiver, **kwargs)
        self._params["volume"] = volume
        self._params["valve_num"] = valve_num
        self._params["flowrate"] = flowrate

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.infuse_syringe_volume(
                self._params["volume"],
                self._params["valve_num"],
                self._params["flowrate"],
            )
        )


class PSD6SyringePumpWithdraw(PSD6SyringePumpParentCommand):
    def __init__(
        self,
        receiver: PSD6SyringePump,
        volume: float,
        valve_num: Optional[int] = None,
        flowrate: Optional[float] = None,
        **kwargs
    ):
        super().__init__(receiver, **kwargs)
        self._params["volume"] = volume
        self._params["valve_num"] = valve_num
        self._params["flowrate"] = flowrate

    def execute(self) -> None:
        self._result = CommandResult(
            *self._receiver.withdraw_syringe_volume(
                self._params["volume"],
                self._params["valve_num"],
                self._params["flowrate"],
            )
        )
