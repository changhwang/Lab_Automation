from commands.command import Command
from commands.utility_commands import LoopStartCommand, LoopEndCommand
from devices.heating_stage import HeatingStage
from devices.multi_stepper import MultiStepper
from devices.newport_esp301 import NewportESP301
# from devices.stellarnet_spectrometer import StellarNetSpectrometer
# from devices.ximea_camera import XimeaCamera
from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from devices.device import Device



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
    "DummyMotor": DummyMotor,
    "DummyMotor1": DummyMotor,
    "DummyMotor2": DummyMotor,
    }
command_directory = "commands/"
approved_devices = list(named_devices.keys())

device_init_args = {
    "DummyHeater": ["name", "heat_rate"],
    "DummyMotor": ["name", "speed"],
}

def dict_to_device(device: Device, type: str):
    device_cls = named_devices[type]
    arg_dict = device.get_args()
    
    # for attr in device_init_args[type]:
    #     arg_dict[attr] = dict["_"+attr]
    
    # print(arg_dict)
    return device_cls(**arg_dict)

def device_to_dict(device: Device):
    return device.get_args()