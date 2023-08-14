from .command import Command, CompositeCommand
from aamp_app.devices.dummy_heater import DummyHeater
from aamp_app.devices.dummy_motor import DummyMotor
from .dummy_heater_commands import *
from .dummy_motor_commands import *


# Example of a composite command that interacts with multiple devices (receivers)
class DummyPrinterHeatMove(CompositeCommand):
    """Sets DummyHeater to temperature, moves DummyMotor a relative distance and back, and sets DummyHeater to 25, reverts heat_rate and speed to original values"""

    def __init__(
        self,
        heater: DummyHeater,
        motor: DummyMotor,
        temp: float,
        heat_rate: float,
        distance: float,
        speed: float,
        **kwargs
    ):
        super().__init__(**kwargs)
        initial_heat_rate = heater.heat_rate
        initial_speed = motor.speed
        self.add_command(DummyHeaterSetHeatRate(heater, heat_rate))
        self.add_command(DummyHeaterSetTemp(heater, temp))
        self.add_command(DummyMotorSetSpeed(motor, speed))
        self.add_command(DummyMotorMoveRelative(motor, distance))
        self.add_command(DummyMotorMoveRelative(motor, -distance))
        self.add_command(DummyHeaterSetTemp(heater, 25))
        self.add_command(DummyHeaterSetHeatRate(heater, initial_heat_rate))
        self.add_command(DummyMotorSetSpeed(motor, initial_speed))
