from command_sequence import CommandSequence
from command_invoker import CommandInvoker
from commands.command import Command
from commands.utility_commands import LoopStartCommand, LoopEndCommand
from devices.heating_stage import HeatingStage
from devices.multi_stepper import MultiStepper
from devices.newport_esp301 import NewportESP301
# from devices.stellarnet_spectrometer import StellarNetSpectrometer
# from devices.ximea_camera import XimeaCamera
from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor


named_devices = {
    "PrintingStage": HeatingStage,
    "AnnealingStage": HeatingStage,
    "MultiStepper1": MultiStepper,
    "PrinterMotorX": NewportESP301,
    # "Spectrometer": StellarNetSpectrometer,
    # "SampleCamera": XimeaCamera,
    "DummyHeater": DummyHeater,
    "DummyHeater1": DummyHeater,
    "DummyHeater2": DummyHeater,
    "DummyMotor1": DummyMotor,
    "DummyMotor2": DummyMotor,
    }
command_directory = "commands/"
approved_devices = list(named_devices.keys())