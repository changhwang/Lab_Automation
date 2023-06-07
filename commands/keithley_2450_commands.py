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

    def __init__(self, receiver: Keithley2450, position: str = 'front', **kwargs):
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

class KeithleyClearBuffer(KeithleyParentCommand):
    """Clear the data storage buffer within the Keithley2450"""
    def __init__(self, receiver: Keithley2450, buffer: str = "defbuffer1", **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['buffer'] = buffer

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.clear_buffer(self._params['buffer']))

class KeithleyIVCharacteristic(KeithleyParentCommand):
    """I-V linear sweep sourcing voltage and measuring current"""

    def __init__(self, receiver: Keithley2450, ilimit: float, vmin: float, vmax: float, delay: float, steps: int = 60, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['ilimit'] = ilimit
        self._params['vmin'] = vmin
        self._params['vmax'] = vmax
        self._params['delay'] = delay
        self._params['steps'] = steps


    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.IV_characteristic(self._params['ilimit'], self._params['vmin'], 
            self._params['vmax'], self._params['steps'], self._params['delay']))


class KeithleyFourPoint(KeithleyParentCommand):
    """Four collinear point sheet resistance measurement"""
    
    def __init__(self, receiver: Keithley2450, test_curr: float, vlimit: float, curr_reversal: bool = False, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['test_curr'] = test_curr
        self._params['vlimit'] = vlimit
        self._params['curr_reversal'] = curr_reversal

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.four_point(self._params['test_curr'], self._params['vlimit'], self._params['curr_reversal']))

class KeithleyGetData(KeithleyParentCommand):
    """Retrieve data"""

    def __init__(self, receiver: Keithley2450, filename: str = None, four_point: bool = False, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['filename'] = filename
        self._params['four_point'] = four_point

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_data(self._params['filename'], self._params['four_point']))


