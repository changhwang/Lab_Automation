from commands.command import Command
from commands.utility_commands import LoopStartCommand, LoopEndCommand
from devices.heating_stage import HeatingStage
from devices.multi_stepper import MultiStepper
from devices.newport_esp301 import NewportESP301

# from devices.stellarnet_spectrometer import StellarNetSpectrometer
# from devices.ximea_camera import XimeaCamera
from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from devices.linear_stage_150 import LinearStage150
from devices.device import Device, MiscDeviceClass
import json
import numpy as np


named_devices = {
    "PrintingStage": HeatingStage,
    "AnnealingStage": HeatingStage,
    "MultiStepper1": MultiStepper,
    "PrinterMotorX": NewportESP301,
    # "Spectrometer": StellarNetSpectrometer,
    # "SampleCamera": XimeaCamera,
    "DummyHeater1": DummyHeater,
    "DummyHeater2": DummyHeater,
    "DummyMotor": DummyMotor,
    "DummyMotor1": DummyMotor,
    "DummyMotor2": DummyMotor,
}
command_directory = "commands/"
approved_devices = list(named_devices.keys())

# device_init_args = {
#     "DummyHeater": ["name", "heat_rate"],
#     "DummyMotor": ["name", "speed"],
# }


def dict_to_device(device: Device, type: str):
    device_cls = named_devices[type]
    arg_dict = device.get_init_args()

    # for attr in device_init_args[type]:
    #     arg_dict[attr] = dict["_"+attr]

    # print(arg_dict)
    return device_cls(**arg_dict)


def str_to_device(device_str: str):
    print(device_str)
    return eval(device_str)


def device_to_dict(device: Device):
    return device.get_init_args()


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if (
            isinstance(obj, Device)
            or isinstance(obj, Command)
            or isinstance(obj, MiscDeviceClass)
        ):
            return obj.__dict__
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


devices_ref = {
    "PrintingStage": {"obj": HeatingStage},
    "AnnealingStage": {"obj": HeatingStage},
    "MultiStepper": {"obj": MultiStepper},
    "PrinterMotorX": {"obj": NewportESP301},
    # "Spectrometer": {"obj": StellarNetSpectrometer},
    # "SampleCamera": {"obj": XimeaCamera},
    "DummyHeater": {"obj": DummyHeater},
    "DummyMotor": {"obj": DummyMotor},
    "LinearStage150": {
        "obj": LinearStage150,
        "import_device": "from devices.linear_stage_150 import LinearStage150",
        "import_commands": "from commands.linear_stage_150_commands import *",
        "init": "LinearStage150(name='LinearStage150', port='/dev/cu.URT0', baudrate=115200, timeout=0.1, destination=0x50, source=0x01, channel=1)",
        "commands": {
            "LinearStage150Connect": "LinearStage150Connect(receiver= '')",
            "LinearStage150Initialize": "LinearStage150Initialize(receiver= '')",
            "LinearStage150Deinitialize": "LinearStage150Deinitialize(receiver= '')",
            "LinearStage150EnableMotor": "LinearStage150EnableMotor(receiver= '')",
            "LinearStage150DisableMotor": "LinearStage150DisableMotor(receiver= '')",
            "LinearStage150MoveAbsolute": "LinearStage150MoveAbsolute(receiver= '', position= 0)",
            "LinearStage150MoveRelative": "LinearStage150MoveRelative(receiver= '', distance= 0)",
        },
    },
}
