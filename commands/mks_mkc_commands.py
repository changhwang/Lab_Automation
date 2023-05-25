from devices.device import Device
from .command import Command, CommandResult
from devices.mks_mfc import MFC

class MFCParentCommand(Command):
    """Parent class for all MKS MFC commands."""
    receiver_cls = MFC

    def __init__(self, receiver: Device, **kwargs):
        super().__init__(receiver, **kwargs)

class MFCInitializeCommand(MFCParentCommand):
    """Initialize the mass flow controller."""

    def __init__(self, receiver: Device, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class MFCSetGasCommand(MFCParentCommand):
    """Set gas flow rate for the mass flow controller."""

    def __init__(self, receiver: Device, gas: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['gas'] = gas

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.set_gas(self._params['gas']))