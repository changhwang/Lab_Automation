from typing import List

from devices.festo_solenoid_valve import FestoSolenoidValve
from .command import Command, CommandResult

class FestoParentCommand(Command):
    """Parent class for all Festo Solenoid Valve commands."""
    receiver_cls = FestoSolenoidValve

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)

class FestoInitialize(FestoParentCommand):
    """Initialize the solenoid valve"""

    def __init__(self, receiver: FestoSolenoidValve, **kwargs):
        super().__init__(receiver, **kwargs)