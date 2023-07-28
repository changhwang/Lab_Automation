from typing import Tuple, List
import asyncio
from devices.mfc import MassFlowController
from .command import Command, CommandResult

class MFCParentCommand(Command):
    """Parent class for MKS instruments mass flow controller"""
    receiver_cls = MassFlowController

    def __init__(self, receiver: MassFlowController, **kwargs):
        super().__init__(receiver, **kwargs)

class MFCInitialize(MFCParentCommand):
    """Initialize the mass flow controller"""

    def __init__(self, receiver: MassFlowController, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class MFCDeinitialize(MFCParentCommand):
    """Deinitialize the mass flow controller"""

    def __init__(self, receiver: MassFlowController, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(asyncio.run(self._receiver.deinitialize()), "Deinitialized the mfc")
        #self._result = CommandResult(*self._receiver.deinitialize())

class MFCGetData(MFCParentCommand):
    """Return data on mfc operation"""
    
    def __init__(self, receiver: MassFlowController, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        #asyncio.run(self._receiver.get())
        self._result = CommandResult(asyncio.run(self._receiver.get()),"Received Data")
        #self._result = CommandResult(True, "got data")

class MFCSetGas(MFCParentCommand):
    """Set the type of gas for operation"""
    """Gas instance must first be created within web browser"""

    def __init__(self, receiver: MassFlowController, gas: str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['gas'] = gas
    
    def execute(self) -> None:
        self._result = CommandResult(asyncio.run(self._receiver.set_gas(self._params['gas'])), "Set the gas")
        #self._result = CommandResult(*self._receiver.set_gas(self._params['gas']))

class MFCSet(MFCParentCommand):
    """Set the desired flowrate in sccm"""
    
    def __init__(self, receiver: MassFlowController, setpoint: int, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['setpoint'] = setpoint
    
    def execute(self) -> None:
        self._result = CommandResult(asyncio.run(self._receiver.set(self._params['setpoint'])), "Set the flowrate")
        #self._result = CommandResult(*self._receiver.set(self._params['setpoint']))

class MFCOpen(MFCParentCommand):
    """Open the mfc, set the flowrate to the maximum for the set gas"""

    def __init__(self, receiver: MassFlowController, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(asyncio.run(self._receiver.open()), "Opened the mfc, maximum flowrate")
        #self._result = CommandResult(*self._receiver.open())

