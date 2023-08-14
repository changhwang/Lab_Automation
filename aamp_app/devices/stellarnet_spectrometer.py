from typing import Union, Tuple, Dict, List, Optional
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import minimize
import stellarnet_driver3 as sn

from .device import Device, check_initialized

# TODO
# convert to serial device parent when arduino added
# add shutter and lamp control
# check slicing as second index is not included in slice
# type hinting of ndarrays?
# type hint the static methods?

class StellarNetSpectrometer(Device):
    save_directory = 'data/spectroscopy/'

    def __init__(self, name: str, spec_keys: List[str] = ['UV-Vis', 'NIR']):
        super().__init__(name)
        self.spectrometer_dict = {}
        self.wavelength_dict = {}
        self.dark_spectra_dict = {}
        self.blank_spectra_dict = {}
        self.absorbance_dict = {}
        self.merged_absorbance = None
        self.num_spectrometers = 0
        self.spec_keys = spec_keys

    @staticmethod
    def num_specs_connected() -> int:
        num_connected = 0
        start_wav = [-1.]
        while True:
            try:
                spec, wav = sn.array_get_spec(num_connected)
                start_wav.append(wav[0].item())
                if start_wav[num_connected+1] == start_wav[num_connected]:
                    break
                else:
                    num_connected += 1
            except:
                break
        return num_connected

    def initialize(self) -> Tuple[bool, str]:
        #lamp on
        #shutter in/out
        #any other Arduino initialization

        self.num_spectrometers = self.num_specs_connected()
        if self.num_spectrometers == 0:
            self._is_initialized = False
            return (False, "There are no spectrometers connected")

        for ndx in range(self.num_spectrometers):
            spectrometer, wavelengths = sn.array_get_spec(ndx)
            if wavelengths[0] < 200.0:
                # UV-VIS
                self.spectrometer_dict['UV-Vis'] = spectrometer
                self.wavelength_dict['UV-Vis'] = wavelengths
            else:
                # NIR
                self.spectrometer_dict['NIR'] = spectrometer
                self.wavelength_dict['NIR'] = wavelengths
            # For additional spectrometers add to the if else ladder

        # Check that we were able to initialize all spectrometers that were declared during construction
        if set(self.spec_keys) == set(self.spectrometer_dict.keys()):        
            self._is_initialized = True
            return (True, "Successfully initialized " + str(self.num_spectrometers) + " spectrometers: " + str(list(self.spectrometer_dict.keys())))
        else:
            self._is_initialized = False
            return (False, "Not all declared spectrometers were initialized. Only initialized: " + str(list(self.spectrometer_dict.keys())))

    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        # turn off lamp?
        # move shutter the position  so that initialize can  be ready to move the shutter  correct position when starting the instrument
        if reset_init_flag:
            self._is_initialized = False

        return (True, "Pass, nothing to deinitialize for now.")

    @check_initialized
    def get_spectrum_counts(
            self, 
            spec_key: str, 
            integration_time: int = 100, 
            scans_to_avg: int = 3,  
            smoothing: int = 0, 
            xtiming: int = 1) -> Tuple[bool, str]:

        # if not self._is_initialized:
        #     return (False, "Spectrometer system not initialized")

        if spec_key in self.spectrometer_dict.keys():
            self.spectrometer_dict[spec_key]['device'].set_config(
                int_time=integration_time, 
                scans_to_avg=scans_to_avg, 
                x_smooth=smoothing, 
                x_timing=xtiming)

            spectrum_array = sn.array_spectrum(self.spectrometer_dict[spec_key], self.wavelength_dict[spec_key])

            max_count = np.amax(spectrum_array[:,1], axis=0)
            print("Max count: " + str(max_count))
            if max_count > 65500:
                return (False, spec_key + " detector is saturated, lower integration time")
            return (True, spectrum_array)
        else:
            return (False, spec_key + " spectrometer is not found" )

    def get_all_spectra_counts(
            self, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            xtimings: Tuple[int, ...] = (1, 1)) -> Tuple[bool, str]:

        # Modify the variable 'spec_keys' if you don't intend to use all spectrometers
        if self.num_spectrometers != len(self.spec_keys):
            return (False, "Spectrometers are not all connected")

        spectrum_array_dict = {}
        # print(spec_keys)
        # using self.spec_keys to ensure that the order within the parameter tuple matches the order of the declared spec_keys
        for ndx, spec_key in enumerate(self.spec_keys):
            # this function should already check if the spec_key is valid
            result, spectrum_array = self.get_spectrum_counts(
                                        spec_key,
                                        integration_time=integration_times[ndx], 
                                        scans_to_avg=scans_to_avg[ndx], 
                                        smoothing=smoothings[ndx], 
                                        xtiming=xtimings[ndx])
            if not result:
                return result, spectrum_array

            spectrum_array_dict[spec_key] = spectrum_array

        return (True, spectrum_array_dict)


    def update_all_dark_spectra(
            self, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            xtimings: Tuple[int, ...] = (1, 1)) -> Tuple[bool, str]:

        result, spectrum_array_dict = self.get_all_spectra_counts(
                                        integration_times, 
                                        scans_to_avg, 
                                        smoothings, 
                                        xtimings)

        if not result:
            return result, spectrum_array_dict

        for key, value in spectrum_array_dict.items():
            self.dark_spectra_dict[key] = value

        return (True, "All dark spectra stored")

    def update_all_blank_spectra(
            self, 
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            xtimings: Tuple[int, ...] = (1, 1)) -> Tuple[bool, str]:

        result, spectrum_array_dict = self.get_all_spectra_counts(
                                        integration_times, 
                                        scans_to_avg, 
                                        smoothings, 
                                        xtimings)

        if not result:
            return result, spectrum_array_dict

        for key, value in spectrum_array_dict.items():
            self.blank_spectra_dict[key] = value

        return (True, "All blank spectra stored")

    def get_all_absorbance(
            self,
            save_to_file: bool = False, 
            filename: Optional[str] = None,
            integration_times: Tuple[int, ...] = (100, 100), 
            scans_to_avg: Tuple[int, ...] = (3, 3), 
            smoothings: Tuple[int, ...] = (0, 0), 
            xtimings: Tuple[int, ...] = (1, 1)) -> Tuple[bool, str]:

        # get the sample spectra
        result, spectrum_array_dict = self.get_all_spectra_counts(
                                        integration_times, 
                                        scans_to_avg, 
                                        smoothings, 
                                        xtimings)
        if save_to_file and filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = timestamp


        # check if failed
        if not result:
            return result, spectrum_array_dict

        # check that dark/blank spectra exists for each initialized spectrometer
        for key in self.spectrometer_dict.keys():
            if not key in self.blank_spectra_dict:
                return (False, "Blank spectra for " + key + " is missing")
            if not key in self.dark_spectra_dict:
                return (False, "Dark spectra for " + key + " is missing")

        # Calculate absorbance for each spectra, save to self
        # Absorbance is -log10((Isample - Idark)/(Iblank - Idark))
        for ndx, spec_key in enumerate(self.spec_keys):
            wavelength = self.wavelength_dict[spec_key].copy()
            dark_spec = self.dark_spectra_dict[spec_key][:,1].copy()
            blank_spec = self.blank_spectra_dict[spec_key][:,1].copy()
            sam_spec = spectrum_array_dict[spec_key][:,1].copy()

            absorbance = np.expand_dims(-np.log10((sam_spec - dark_spec) / (blank_spec - dark_spec)), axis=1)
            absorbance_array = np.hstack((wavelength, absorbance))

            self.absorbance_dict[spec_key] = absorbance_array
            
            # save all data related to absorbance calculation to a file per spectrometer
            if save_to_file:
                data = pd.DataFrame()
                data[spec_key + ' Wavelength'] = np.squeeze(wavelength)
                data[spec_key + ' Dark Counts'] = np.squeeze(dark_spec)
                data[spec_key + ' Blank Counts'] = np.squeeze(blank_spec)
                data[spec_key + ' Sample Counts'] = np.squeeze(sam_spec)
                data[spec_key + ' Absorbance'] = np.squeeze(absorbance)
                
                comment = ["# spec_key = " + spec_key + "\n",
                            "# integration_time = " + str(integration_times[ndx]) + "\n",
                            "# scans_to_avg = " + str(scans_to_avg[ndx]) + "\n",
                            "# smoothing = " + str(smoothings[ndx]) + "\n",
                            "# xtiming = " + str(xtimings[ndx]) + "\n"]
                
                fullfilename = self.save_directory + filename + '_' + spec_key + '.csv'
                with open(fullfilename, 'w') as file:
                    file.writelines(comment)
                data.to_csv(fullfilename, mode='a', index_label='Index')

        if save_to_file:
            all_comments = ["# spec_keys = " + str(self.spec_keys) + "\n"
                            "# integration_times = " + str(integration_times) + "\n",
                            "# scans_to_avg = " + str(scans_to_avg) + "\n",
                            "# smoothings = " + str(smoothings) + "\n",
                            "# xtimings = " + str(xtimings) + "\n"]
        else:
            all_comments = ['#\n',]
        # Merge the absorbance spectra and optionally save to file
        # What happens if only 1 spectrometer is connected/being used?
        if len(self.spec_keys) > 1:
            result, message = self.merge_absorbance(save_to_file, filename, all_comments)

            if not result:
                return result, message

        if save_to_file:
            return (True, "All absorbance spectra stored to instance and saved to file: " + self.save_directory + filename)
        else:
            return (True, "All absorbance spectra stored to instance but not saved to file")

    # hard coded for UV-Vis and NIR
    # what happens if only 1 spectrometer is connected/being used?
    def merge_absorbance(self, save_to_file: bool, filename: str, comment_list: List[str]) -> Tuple[bool, str]:
        uv_wavelength = np.squeeze(self.wavelength_dict['UV-Vis'].copy())
        nir_wavelength = np.squeeze(self.wavelength_dict['NIR'].copy())
        uv_absorbance = np.squeeze(self.absorbance_dict['UV-Vis'][:,1].copy())
        nir_absorbance = np.squeeze(self.absorbance_dict['NIR'][:,1].copy())

        # start and end of overlapping regions
        WAVE_START = 900.0
        WAVE_END = 1030.0

        merge_result = minimize(self.merge_error, [1, 0], args=(uv_wavelength, uv_absorbance, nir_wavelength, nir_absorbance, WAVE_START, WAVE_END), method='BFGS')

        if not merge_result:
            return (False, "Failed to merge UV-Vis and NIR absorbance spectra: " + merge_result.message)
        else:
            scale = merge_result.x[0]
            shift = merge_result.x[1]

            # uv is not modified, nir is adjusted to match uv
            uv_array = self.absorbance_dict['UV-Vis'].copy()
            nir_wavelength = self.wavelength_dict['NIR'].copy()

            nir_absorbance = np.expand_dims(self.scale_shift_data([scale, shift], self.absorbance_dict['NIR'][:,1].copy()), axis=1)
            nir_array = np.hstack((nir_wavelength, nir_absorbance))

            UV_START = 210.0
            UV_END = 1030.0
            NIR_START = 900.0
            NIR_END = 1700.0

            uv_array = self.truncate_ends_by_wavelength(uv_array, UV_START, UV_END)
            nir_array = self.truncate_ends_by_wavelength(nir_array, NIR_START, NIR_END)

            merged_array = np.vstack((uv_array, nir_array))
            merged_array = merged_array[merged_array[:,0].argsort()]
            self.merged_absorbance = merged_array
            
            if save_to_file:
                data = pd.DataFrame()
                data['Wavelength'] = np.squeeze(self.merged_absorbance[:,0].copy())
                data['Absorbance'] = np.squeeze(self.merged_absorbance[:,1].copy())

                fullfilename = self.save_directory + filename + '_merged.csv'
                comment_list.append("# To merge, NIR data is scaled first then shifted\n")
                comment_list.append("# scale = " + str(scale) + "\n")
                comment_list.append("# shift = " + str(shift) + "\n")
                with open(fullfilename, 'w') as file:
                    file.writelines(comment_list)
                data.to_csv(fullfilename, mode='a', index_label='Index')

            return (True, "Successfully merged UV-Vis and NIR absorbance spectra: " + merge_result.message)

    # y and return are ndarrays
    @staticmethod
    def scale_shift_data(params: List[float], y):
        scale = params[0]
        shift = params[1]
        return y * scale + shift
        # return (y + shift) * scale

    @staticmethod
    def truncate_ends_by_wavelength(array, start: float, end: float):
        # expects array to be two columns with first being wavelength and second being the data of interest (counts, absorbance, etc.)
        return array[np.logical_and(array[:,0]>start, array[:,0]<end)]

    @staticmethod
    def find_nearest(x, x0):
        ndx = np.abs(x - x0).argmin()
        return ndx, x[ndx]

    @staticmethod
    def merge_error(params, x1, y1, x2, y2, x_start, x_end):
        # y1 (UV-Vis) has higher resolution (2048) than y2 (NIR, 512)
        # so although we will adjust y2 to match y1, y1 will be interpolated onto x2
        # get the overlapped slice of the data that is not being interpolated (x2)
        x2_start_ndx = StellarNetSpectrometer.find_nearest(x2, x_start)[0]
        x2_end_ndx = StellarNetSpectrometer.find_nearest(x2, x_end)[0]
        x2_slice = x2[x2_start_ndx : x2_end_ndx].copy()
        # adjust y2
        new_y2 = StellarNetSpectrometer.scale_shift_data(params, y2)
        y2_slice = new_y2[x2_start_ndx : x2_end_ndx].copy()
        # get interpolated function of y1(x1)
        y1_interp = interp1d(x1, y1)
        # get y1 interpolated onto x2
        y1_slice = y1_interp(x2_slice)
        # calc error
        sum_squares = ((y1_slice - y2_slice) ** 2).sum()
        return sum_squares

    def servo_shutter_in(self):
        pass

    def servo_shutter_out(self):
        pass

    def lamp_relay_on(self):
        pass

    def lamp_relay_off(self):
        pass


# Considered making get_spectrum_counts generalized to accept either a single spectrometer (spec_key + params) 
# or any sized list of spec_keys + list of params.
# I ended up not doing it this way and making get_spectrum_counts take only 1 spectrometer
# Then I made a second function get_all_spectra_counts that calls get_spectrum_counts multiple times.
# My subsequent functions to get dark spectra, blank spectra, absorbance spectra then work with get_all_spectra_counts
# At first this seems more complicated. However, I did it to avoid list/tuple type checking and len() checking for every single param
# and because I wanted to avoid the following situation:
# 1) User gets dark and blank spectra for all spectrometers and proceeds to use them to get absorption spectras
# 2) Later, user needs needs to retake the dark/blank spectra but makes an error and uses the generalized methods for NOT all spectrometers
# 3) User proceeds to calculate all absorption spectra for all spectrometers
# In this case, not all spectrometers had their dark/blank spectra correctly retaken.
# The data is then incorrect for those spectrometers since they use the old dark/blank but the user has no idea this just happened.
# Another option is to null all spectrometer dark/blanks when even only retaking for 1 spectrometer, but requires implementing checks and error messages
# It is easier at the moment to just enforce all spectrometers are used all the time by writing methods that always use all spectrometers
# However, The "get_all_..." methods can generalize to 1 spectrometer based on the spec_keys arg passed during construction