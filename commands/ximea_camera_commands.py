from typing import Optional

from .command import Command
from devices.ximea_camera import XimeaCamera


class XimeaCameraParentCommand(Command):
    receiver_cls = XimeaCamera

    def __init__(self, receiver: XimeaCamera):
        super().__init__()
        self._receiver = receiver
        self._receiver_name = receiver.name

class XimeaCameraInitialize(XimeaCameraParentCommand):
    cls_description = "Initialize camera by opening communication with camera and optionally set defaults"

    def __init__(self, receiver: XimeaCamera):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class XimeaCameraDeinitialize(XimeaCameraParentCommand):
    cls_description = "Deinitialize camera by stopping any acquisition and closing communication with camera."

    def __init__(self, receiver: XimeaCamera, reset_init_flag: bool = True):
        super().__init__(receiver)
        self._reset_init_flag = reset_init_flag
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._reset_init_flag)

class XimeaCameraGetImage(XimeaCameraParentCommand):
    cls_description = "Get image and save to file, display image, or both. No filename = timestamped filename. No exposure or gain = use defaults."
    
    def __init__(
            self, 
            receiver: XimeaCamera, 
            save_to_file: bool = True, 
            filename: str = None, 
            exposure_time: Optional[int] = None, 
            gain: Optional[float] = None, 
            show_pop_up: bool = False):
        super().__init__(receiver)
        self._save_to_file = save_to_file
        self._filename = filename
        self._exposure_time = exposure_time
        self._gain = gain
        self._show_pop_up = show_pop_up
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._save_to_file) + " " + str(self._filename) + " " + str(self._exposure_time) + " " + str(self._gain) + " " + str(self._show_pop_up)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Save?: " + str(self._save_to_file) + " Filename: " + str(self._filename) + " Exposure: " + str(self._exposure_time) + " Gain: " + str(self._gain) + " Show?: " + str(self._show_pop_up)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.get_image(self._save_to_file, self._filename, self._exposure_time, self._gain, self._show_pop_up)

class XimeaCameraSetDefaultExposure(XimeaCameraParentCommand):
    cls_description = "Set the default exposure time to use if no exposure time is passed when getting image."

    def __init__(self, receiver: XimeaCamera, exposure_time: int):
        super().__init__(receiver)
        self._exposure_time = exposure_time
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._exposure_time)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Exposure: " + str(self._exposure_time)

    def execute(self) -> None:
        self._receiver.default_exposure_time = self._exposure_time
        if self._receiver.default_exposure_time == self._exposure_time:
            self._was_successful, self._result_message = (True, "Default exposure time successfully set to " + str(self._exposure_time))
        else:
            self._was_successful, self._result_message = (False, "Failed to set the default exposure time to " + str(self._exposure_time) + ". The default exposure time must be > 0.")

class XimeaCameraSetDefaultGain(XimeaCameraParentCommand):
    cls_description = "Set the default gain to use if no gain is passed when getting image."

    def __init__(self, receiver: XimeaCamera, gain: float):
        super().__init__(receiver)
        self._gain = gain
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._gain)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Gain: " + str(self._gain)

    def execute(self) -> None:
        self._receiver.default_gain = self._gain
        if self._receiver.default_gain == self._gain:
            self._was_successful, self._result_message = (True, "Default gain successfully set to " + str(self._gain))
        else:
            # unsure what the upper limit is at the moment
            self._was_successful, self._result_message = (False, "Failed to set the default gain to " + str(self._gain) + ". The default gain must be >= 0 and has an upper limit.")

class XimeaCameraUpdateWhiteBal(XimeaCameraParentCommand):
    cls_description = "Update the white balance coefficients using the current camera feed."

    def __init__(self, receiver: XimeaCamera, exposure_time: int = None, gain: Optional[float] = None):
        super().__init__(receiver)
        self._exposure_time = exposure_time
        self._gain = gain
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._exposure_time) + " " + str(self._gain)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Exposure: " + str(self._exposure_time) + " Gain: " + str(self._gain)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.update_white_balance(self._exposure_time, self._gain)

class XimeaCameraSetManualWhiteBal(XimeaCameraParentCommand):
    cls_description = "Set any of the red, green, and blue white balance coefficients manually."

    def __init__(self, receiver: XimeaCamera, wb_kr: Optional[float] = None, wb_kg: Optional[float] = None, wb_kb: Optional[float] = None):
        super().__init__(receiver)
        self._wb_kr = wb_kr
        self._wb_kg = wb_kg
        self._wb_kb = wb_kb
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._wb_kr) + " " + str(self._wb_kg) + " " + str(self._wb_kb)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " wb_kr: " + str(self._wb_kr) + " wb_kg: " + str(self._wb_kg) + " wb_kb: " + str(self._wb_kb)
    
    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.set_white_balance_manually(self._wb_kr, self._wb_kg, self._wb_kb)

class XimeaCameraResetWhiteBal(XimeaCameraParentCommand):
    cls_description = "Reset the red, green, and blue white balance coefficients to defaults."

    def __init__(self, receiver: XimeaCamera):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name
    
    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.reset_white_balance_rgb_coeffs()

