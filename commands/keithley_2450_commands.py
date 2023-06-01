import pyvisa
from typing import List

from devices.device import Device
from .command import Command, CommandResult, CompositeCommand
from devices.keithley_2450 import Keithley2450

class KeithleyParentCommand(Command):
    """Parent class for all Keithley2450 commands."""
    receiver_cls = Keithley2450

    def __init__(self, receiver: Keithley2450, **kwargs):
        super().__init__(receiver, **kwargs)

class Keithley2450Initialize(KeithleyParentCommand):
    """Initialize the SMU by resetting it"""
    
    def __init__(self, receiver: Keithley2450, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class Keithley2450Deinitialize(KeithleyParentCommand):
    """Deinitialize the SMU"""

    #TODO: create command to deinitialize keithley2450 if necessary

    def __init__(self, reciever: Keithley2450, reset_init_flag: bool = True, **kwargs):
        super().__init__(reciever, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize())


class KeithleyWait(KeithleyParentCommand):
    """Wait for all pending operations to finish"""

    def __init__(self, receiver: Keithley2450, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.wait())

class KeithleyWriteCommand(KeithleyParentCommand):
    """Write arbitrary SCPI ASCII command"""

    def __init__(self, receiver: Keithley2450, command: str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['command'] = command

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.write_command(self._params['command']))

class KeithleySetTerminal(KeithleyParentCommand):
    """Set the terminal position of the SMU"""

    def __init__(self, receiver: Keithley2450, position: str, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['position'] = position

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.terminal_pos(self._params['position']))

class KeithleyErrorCheck(KeithleyParentCommand):
    """Check for errors that occur during measurement"""

    def __init__(self, receiver: Keithley2450, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.error_check())

class KeithleyIVCharacteristic(KeithleyParentCommand):
    """I-V linear sweep sourcing voltage and measuring current"""

    def __init__(self, receiver: Keithley2450, ilimit: float, vmin: float, vmax: float, steps: int, delay: float, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['ilimit'] = ilimit
        self._params['vmin'] = vmin
        self._params['vmax'] = vmax
        self._params['steps'] = steps
        self._params['delay'] = delay

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.IV_characteristic(self._params['ilimit'], self._params['vmin'], 
            self._params['vmax'], self._params['steps'], self._params['delay']))
        
class KeithleyGetData(KeithleyParentCommand):
    """Retrieve data"""

    def __init__(self, receiver: Keithley2450, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_data())
