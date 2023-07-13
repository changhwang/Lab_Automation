from commands.command import Command
from commands.utility_commands import LoopStartCommand, LoopEndCommand
from devices.heating_stage import HeatingStage
from devices.multi_stepper import MultiStepper
from devices.newport_esp301 import NewportESP301

# from devices.stellarnet_spectrometer import StellarNetSpectrometer
from devices.ximea_camera import XimeaCamera
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
    "SampleCamera": XimeaCamera,
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


heating_stage_ref = {
    "obj": HeatingStage,
    "import_device": "from devices.heating_stage import HeatingStage",
    "import_commands": "from commands.heating_stage_commands import *",
    "init": "HeatingStage(name='PrintingStage', port='', baudrate=115200, timeout=0.1, heating_timeout=600.0)",
    "commands": {
        "HeatingStageConnect": "HeatingStageConnect(receiver= '')",
        "HeatingStageInitialize": "HeatingStageInitialize(receiver= '')",
        "HeatingStageDeinitialize": "HeatingStageDeinitialize(receiver= '')",
        "HeatingStageSetTemperature": "HeatingStageSetTemperature(receiver= '', temperature= 0.0)",
        "HeatingStageSetSetPoint": "HeatingStageSetSetPoint(receiver= '', temperature= 0.0)",
    },
}


devices_ref = {
    "PrintingStage": heating_stage_ref,
    "AnnealingStage": heating_stage_ref,
    "MultiStepper": {
        "obj": MultiStepper,
        "import_device": "from devices.multi_stepper import MultiStepper",
        "import_commands": "from commands.multi_stepper_commands import *",
        "init": "MultiStepper(name='MultiStepper', port='', baudrate=115200, timeout=0.1, destination=0x50, source=0x01, channel=1)",
        "commands": {
            "MultiStepperConnect": "MultiStepperConnect(receiver= '')",
            "MultiStepperInitialize": "MultiStepperInitialize(receiver= '')",
            "MultiStepperDeinitialize": "MultiStepperDeinitialize(receiver= '')",
            "MultiStepperMoveAbsolute": "MultiStepperMoveAbsolute(receiver= '', stepper_number= 0, position= 0)",
            "MultiStepperMoveRelative": "MultiStepperMoveRelative(receiver= '', stepper_number= 0, distance= 0)",
        },
    },
    "PrinterMotorX": {"obj": NewportESP301},
    # "Spectrometer": {"obj": StellarNetSpectrometer},
    "XimeaCamera": {"obj": XimeaCamera},
    "DummyHeater": {"obj": DummyHeater},
    "DummyMotor": {"obj": DummyMotor},
    "LinearStage150": {
        "obj": LinearStage150,
        "import_device": "from devices.linear_stage_150 import LinearStage150",
        "import_commands": "from commands.linear_stage_150_commands import *",
        "init": "LinearStage150(name='LinearStage150', port='', baudrate=115200, timeout=0.1, destination=0x50, source=0x01, channel=1)",
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


devices_ref_redundancy = {
    "PrintingStage": heating_stage_ref,
    "AnnealingStage": heating_stage_ref,
    "MultiStepper": {
        "obj": MultiStepper,
        "import_device": "from devices.multi_stepper import MultiStepper",
        "import_commands": "from commands.multi_stepper_commands import *",
        "init": "MultiStepper(name='MultiStepper', port='', baudrate=115200, timeout=0.1, destination=0x50, source=0x01, channel=1)",
        "commands": {
            "MultiStepperConnect": "MultiStepperConnect(receiver= '')",
            "MultiStepperInitialize": "MultiStepperInitialize(receiver= '')",
            "MultiStepperDeinitialize": "MultiStepperDeinitialize(receiver= '')",
            "MultiStepperMoveAbsolute": "MultiStepperMoveAbsolute(receiver= '', stepper_number= 0, position= 0)",
            "MultiStepperMoveRelative": "MultiStepperMoveRelative(receiver= '', stepper_number= 0, distance= 0)",
        },
    },
    "PrinterMotorX": {"obj": NewportESP301},
    # "Spectrometer": {"obj": StellarNetSpectrometer},
    "XimeaCamera": {"obj": XimeaCamera},
    "DummyHeater": {"obj": DummyHeater},
    "DummyMotor": {
        "obj": DummyMotor,
        "serial": True,
        "serial_sequence":["DummyMotorInitialize"],
        "import_device": "from devices.dummy_motor import DummyMotor",
        "import_commands": "from commands.dummy_motor_commands import *",
        "init": {
            "default_code": "DummyMotor(name='DummyMotor', speed=20.0)",
            "obj_name": "DummyMotor",
            "args": {
                "name": {
                    "default": "DummyMotor",
                    "type": str,
                    "notes": "Name of the device.",
                },
                "speed": {
                    "default": 20.0,
                    "type": float,
                    "notes": "Speed of the motor.",
                },
            },
        },
        "commands": {
            "DummyMotorInitialize": {
                "default_code": "DummyMotorInitialize(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    }
                },
            },
            "DummyMotorDeinitialize": {
                "default_code": "DummyMotorDeinitialize(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    }
                },
            },
            "DummyMotorSetSpeed": {
                "default_code": "DummyMotorSetSpeed(receiver= '', speed= 0.0)",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    },
                    "speed": {
                        "default": 0.0,
                        "type": float,
                        "notes": "Speed of the motor.",
                    },
                },
            },
            "DummyMotorMoveAbsolute": {
                "default_code": "DummyMotorMoveAbsolute(receiver= '', position= 0)",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    },
                    "position": {
                        "default": 0,
                        "type": float,
                        "notes": "Position to move to.",
                    },
                },
            },
            "DummyMotorMoveRelative": {
                "default_code": "DummyMotorMoveRelative(receiver= '', distance= 0)",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    },
                    "distance": {
                        "default": 0,
                        "type": float,
                        "notes": "Distance to move.",
                    },
                },
            },
            "DummyMotorMoveSpeedAbsolute": {
                "default_code": "DummyMotorMoveSpeedAbsolute(receiver= '', position= 0.0, speed= 0.0)",
                "args": {
                    "receiver": {
                        "default": "DummyMotor",
                        "type": str,
                        "notes": "Name of the device.",
                    },
                    "position": {
                        "default": 0.0,
                        "type": float,
                        "notes": "Position to move to.",
                    },
                    "speed": {
                        "default": 0.0,
                        "type": float,
                        "notes": "Speed of the motor.",
                    },
                },
            }
        },
    },
    "LinearStage150": {
        "obj": LinearStage150,
        "serial": True,
        "serial_sequence": ["LinearStage150Connect"],
        "import_device": "from devices.linear_stage_150 import LinearStage150",
        "import_commands": "from commands.linear_stage_150_commands import *",
        "init": {
            "default_code": "LinearStage150(name='LinearStage150', port='', baudrate=115200, timeout=0.1, destination=0x50, source=0x01, channel=1)",
            "obj_name": "LinearStage150",
            "args": {
                "name": {
                    "default": "LinearStage150",
                    "type": str,
                    "notes": "Name of the device.",
                },
                "port": {"default": "COM", "type": str, "notes": "Port"},
                "baudrate": {
                    "default": 115200,
                    "type": int,
                    "notes": "Baudrate",
                },
                "timeout": {
                    "default": 0.1,
                    "type": float,
                    "notes": "Timeout",
                },
                "destination": {
                    "default": 0x50,
                    "type": int,
                    "notes": "",
                },
                "source": {
                    "default": 0x01,
                    "type": int,
                    "notes": "",
                },
                "channel": {
                    "default": 1,
                    "type": int,
                    "notes": "",
                },
            },
        },
        "commands": {
            "LinearStage150Connect": {
                "default_code": "LinearStage150Connect(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    }
                },
            },
            "LinearStage150Initialize": {
                "default_code": "LinearStage150Initialize(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    }
                },
            },
            "LinearStage150Deinitialize": {
                "default_code": "LinearStage150Deinitialize(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    }
                },
            },
            "LinearStage150EnableMotor": {
                "default_code": "LinearStage150EnableMotor(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    }
                },
            },
            "LinearStage150DisableMotor": {
                "default_code": "LinearStage150DisableMotor(receiver= '')",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    }
                },
            },
            "LinearStage150MoveAbsolute": {
                "default_code": "LinearStage150MoveAbsolute(receiver= '', position= 0)",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    },
                    "position": {
                        "default": 0,
                        "type": int,
                        "notes": "",
                    },
                },
            },
            "LinearStage150MoveRelative": {
                "default_code": "LinearStage150MoveRelative(receiver= '', distance= 0)",
                "args": {
                    "receiver": {
                        "default": "LinearStage150",
                        "type": str,
                        "notes": "",
                    },
                    "distance": {
                        "default": 0,
                        "type": int,
                        "notes": "",
                    },
                },
            },
        },
    },
}
