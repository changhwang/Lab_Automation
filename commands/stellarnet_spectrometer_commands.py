from typing import Tuple, Optional

from .command import Command, CommandResult
from devices.stellarnet_spectrometer import StellarNetSpectrometer

class SpectrometerParentCommand(Command):
    """Parent class for all StellarNet Spectrometer commands."""
    receiver_cls = StellarNetSpectrometer

    def __init__(self, receiver: StellarNetSpectrometer, **kwargs):
        super().__init__(receiver, **kwargs)

class SpectrometerInitialize(SpectrometerParentCommand):
    """Initialize spectrometer by verifying connection and getting each spectrometer object and wavelength array."""

    def __init__(self, receiver: StellarNetSpectrometer, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.initialize())

class SpectrometerDeinitialize(SpectrometerParentCommand):
    """Deinitialize the spectrometer, currently does nothing except optionally change init flag."""

    def __init__(self, receiver: StellarNetSpectrometer, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.deinitialize(self._params['reset_init_flag']))

class SpectrometerUpdateDark(SpectrometerParentCommand):
    """Update the stored dark spectra for all spectrometers."""

    def __init__(
            self, 
            receiver: StellarNetSpectrometer, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['integration_times'] = integration_times
        self._params['scans_to_avg'] = scans_to_avg
        self._params['smoothings'] = smoothings

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.update_all_dark_spectra(self._params['integration_times'], self._params['scans_to_avg'], self._params['smoothings']))

class SpectrometerUpdateBlank(SpectrometerParentCommand):
    """Update the stored blank spectra for all spectrometers."""

    def __init__(
            self, 
            receiver: StellarNetSpectrometer, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['integration_times'] = integration_times
        self._params['scans_to_avg'] = scans_to_avg
        self._params['smoothings'] = smoothings

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.update_all_blank_spectra(self._params['integration_times'], self._params['scans_to_avg'], self._params['smoothings']))

class SpectrometerGetAbsorbance(SpectrometerParentCommand):
    """Calculate and update the stored absorbance spectra, merge spectra, and optionally save to file. No filename = timestamped filename."""

    def __init__(
            self, 
            receiver: StellarNetSpectrometer,
            save_to_file: bool = True, 
            filename: Optional[str] = None,
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['save_to_file'] = save_to_file
        self._params['filename'] = filename
        self._params['integration_times'] = integration_times
        self._params['scans_to_avg'] = scans_to_avg
        self._params['smoothings'] = smoothings

    def execute(self) -> None:
        self._result = CommandResult(*self._receiver.get_all_absorbance(self._params['save_to_file'], self._params['filename'], self._params['integration_times'], self._params['scans_to_avg'], self._params['smoothings']))

class SpectrometerShutterIn(SpectrometerParentCommand):
    pass

class SpectrometerShutterOut(SpectrometerParentCommand):
    pass

class SpectrometerLampOn(SpectrometerParentCommand):
    pass

class SpectrometerLampOff(SpectrometerParentCommand):
    pass