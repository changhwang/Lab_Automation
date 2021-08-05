from typing import Tuple, Optional

from .command import Command
from ..stellarnet_spectrometer import StellarNetSpectrometer

class SpectrometerParentCommand(Command):
    receiver_cls = StellarNetSpectrometer

    def __init__(self, receiver: StellarNetSpectrometer):
        self._receiver = receiver
        self._receiver_name = receiver.name

class SpectrometerInitialize(SpectrometerParentCommand):
    cls_description = "Initialize spectrometer by verifying connection and getting each spectrometer object and wavelength array. "

    def __init__(self, receiver: StellarNetSpectrometer):
        super().__init__(receiver)
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.initialize()

class SpectrometerDeinitialize(SpectrometerParentCommand):
    cls_description = "Deinitialize the spectrometer, currently does nothing. "

    def __init__(self, receiver: StellarNetSpectrometer, reset_init_flag: bool = True):
        super().__init__(receiver)
        self._reset_init_flag = reset_init_flag
        self._name = type(self).__name__ + " " + self._receiver_name
        self._description = type(self).cls_description + " Name: " + self._receiver_name

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.deinitialize(self._reset_init_flag)

class SpectrometerUpdateDark(SpectrometerParentCommand):
    cls_description = "Update the stored dark spectra for all spectrometers"

    def __init__(
            self, 
            receiver: StellarNetSpectrometer, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0)):
        super().__init__(receiver)
        self._integration_times = integration_times
        self._scans_to_avg = scans_to_avg
        self._smoothings = smoothings
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._integration_times) + " " + str(self._scans_to_avg) + " " + str(self._smoothings)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " IntTime: " + str(self._integration_times) + " ScanAvg: " + str(self._scans_to_avg) + " Smooth: " + str(self._smoothings)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.update_all_dark_spectra(self._integration_times, self._scans_to_avg, self._smoothings)

class SpectrometerUpdateBlank(SpectrometerParentCommand):
    cls_description = "Update the stored blank spectra for all spectrometers"

    def __init__(
            self, 
            receiver: StellarNetSpectrometer, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0)):
        super().__init__(receiver)
        self._integration_times = integration_times
        self._scans_to_avg = scans_to_avg
        self._smoothings = smoothings
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._integration_times) + " " + str(self._scans_to_avg) + " " + str(self._smoothings)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " IntTime: " + str(self._integration_times) + " ScanAvg: " + str(self._scans_to_avg) + " Smooth: " + str(self._smoothings)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.update_all_blank_spectra(self._integration_times, self._scans_to_avg, self._smoothings)

class SpectrometerGetAbsorbance(SpectrometerParentCommand):
    cls_description = "Calculate and update the stored absorbance spectra, merge spectra, and optionally save to file. No filename = timestamped filename."

    def __init__(
            self, 
            receiver: StellarNetSpectrometer,
            save_to_file: bool = True, 
            filename: Optional[str] = None,
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0)):
        super().__init__(receiver)
        self._save_to_file = save_to_file
        self._filename = filename
        self._integration_times = integration_times
        self._scans_to_avg = scans_to_avg
        self._smoothings = smoothings
        self._name = type(self).__name__ + " " + self._receiver_name + " " + str(self._save_to_file) + " " + str(self._filename) + " " + str(self._integration_times) + " " + str(self._scans_to_avg) + " " + str(self._smoothings)
        self._description = type(self).cls_description + " Name: " + self._receiver_name + " Save?: " + str(self._save_to_file) + " Filename: " + str(self._filename)+ " IntTime: " + str(self._integration_times) + " ScanAvg: " + str(self._scans_to_avg) + " Smooth: " + str(self._smoothings)

    def execute(self) -> None:
        self._was_successful, self._result_message = self._receiver.get_all_absorbance(self._save_to_file, self._filename, self._integration_times, self._scans_to_avg, self._smoothings)

class SpectrometerShutterIn(SpectrometerParentCommand):
    pass

class SpectrometerShutterOut(SpectrometerParentCommand):
    pass

class SpectrometerLampOn(SpectrometerParentCommand):
    pass

class SpectrometerLampOff(SpectrometerParentCommand):
    pass