"""Requires download of NI-VISA with equivalent bitness"""
import pyvisa
from time import sleep
from datetime import datetime
import pandas as pd
from typing import Optional, Tuple
from .device import Device, check_initialized



class Keithley2450(Device):
    save_directory = 'data/keithley_2450/'

    def __init__(self, name: str, ID: str, query_delay: int):
        super().__init__(name)
        self.ID = ID
        self.query_delay = query_delay
        self.keithley = pyvisa.ResourceManager().open_resource(self.ID)
        print(self.keithley.query('*IDN?'))
        sleep(self.query_delay)

    def get_init_args(self) -> dict:
        args_dict = {
            "name": self.name,
            "ID": self.ID,
            "query_delay": self.query_delay,
        }
        return args_dict
    
    def update_init_args(self, args_dict: dict):
        self.name = args_dict["name"]
        self.ID = args_dict["ID"]
        self.query_delay = args_dict["query_delay"]

    @property   #TODO: Check if necessary
    def terminal_pos(self) -> str:
        return self.position
    
    def initialize(self) -> Tuple[bool, str]:
        self.keithley.write('*RST')
        self._is_initialized = True
        return (True, "Initialized Keithley2450 by performing device reset")

    def deinitialize(self) -> Tuple[bool, str]:
        #TODO: Keithley deinitialization steps
        self.keithley.close()
        self._is_initialized = False
        return(True, "Deinitialized Keithley2450")
    
    @check_initialized
    def wait(self):
        self.keithley.query('*OPC?')
        if self.keithley.query('*ESR?') != 1: 
            self.keithley.write('*CLS')
            print("Wait Completed, Standard Event Status Register cleared")

    #TODO: Test wait function below
    """
    def wait(self):
        self.keithley.write('*OPC?')
        while True:
            try: 
                self.keithley.read()
                break
            except pyvisa.errors.VisaIOError:
                continue
            """

    @check_initialized
    def write_command(self, command: str):
        self.keithley.write(command)
        
    @check_initialized
    def terminal_pos(self, position: str = 'front'):
        """Set terminal positions to front or rear"""
        if position == "rear":
            self.keithley.write('ROUT:TERM REAR')
            self.wait()
        elif position == "front":
            self.keithley.write('ROUT:TERM FRONT')
            self.wait()
        else:
            raise Exception(f"Expected 'rear' or 'front', found {position}")
    @check_initialized
    def error_check(self):
        """Check for errors raised by Keithley2450"""
        self.keithley.write('SYSTem:ERRor:COUNt?')
        num_errors = int(self.keithley.read())
        if num_errors != 0:
            errors = []
            for i in range(num_errors):
                self.keithley.write('SYSTem:ERRor:NEXT?')
                errors.append(self.device.read())
            errors = ''.join(errors)
            raise Warning(f"An error has occurred:\n {errors}")
    
    @check_initialized
    def clear_buffer(self, buffer: str = 'defbuffer1') -> Tuple[bool, str]:
        """Clear the data storage buffer within the Keithley2450"""
        self.keithley.write(f':TRACe:CLEar "{buffer}"')
        return (True, f'Cleared buffer {buffer}')

        
    @check_initialized
    def IV_characteristic(self, ilimit: float, vmin: float, vmax: float, delay: float, steps: int = 60):
        """Sourcing voltage and measuring current with linear sweep"""
        if ilimit <= 1e-9 and ilimit >= 1.05:
            raise Exception(f"Expected source current limit between 1nA and 1.05A")

        if vmin < -210 or vmin > 210:
            raise Exception(f"Voltage minimum out of range -210V to 210V")
        
        if vmax < -210 or vmin > 210:
            raise Exception(f"Voltage maximum out of range -210V to 210V")
        if vmax < vmin:
            raise Exception(f"Voltage minimum is greater than voltage maximum")

        if delay < 50e-6:
            raise Exception(f"Delay value too small, must be greater than 50 µs")
        
        self.keithley.write('*RST')
        self.keithley.write('SENS:CURR:RANG:AUTO ON')
        self.keithley.write('SYST:RSEN ON')
        self.keithley.write(f"SOURce:VOLT:ILIMit {ilimit}")
        self.keithley.write(f"SOURce:SWE:VOLT:LIN {vmin}, {vmax}, {steps}, {delay}")
        self.keithley.write('INIT')
        self.keithley.write('*WAI')

    @check_initialized
    def four_point(self, test_curr: float, vlimit: float, curr_reversal: bool = False) -> float:
        """Measure resistance through four-point collinear probe method"""

        self.keithley.write('*RST')
        self.keithley.write('SENS:VOLT:RANG:AUTO ON')
        self.keithley.write('SYST:RSEN ON')
        self.keithley.write(f"SOURce:CURR:VLIMit {vlimit}")
        self.keithley.write(f"SOURce:CURR {test_curr}")
        self.keithley.write(':OUTP ON')
        self.keithley.write('*WAI')
        sleep(2)
        res1 = self.keithley.query(':READ?')
        self.keithley.write(':OUTP OFF')
        four_point_data = res1
        if curr_reversal:
            self.keithley.write(f"SOURce:CURR:VLIMit {vlimit}")
            self.keithley.write(f"SOURce:CURR {-1*test_curr}")
            self.keithley.write(':OUTP ON')
            self.keithley.write('*WAI')
            sleep(2)
            res2 = self.keithley.query('READ?')
            self.keithley.write(':OUTP OFF')
            four_point_data = (res1 + res2) / 2
        return four_point_data
    
        
    @check_initialized
    def get_data(self, filename: str = None, four_point: bool = False):
        """Retrieve data from buffer and save locally"""

        if not four_point:
            self.keithley.write(':TRACe:ACTual:END?')
            end_index = int(self.keithley.read())
            self.keithley.write(f':TRACe:DATA? 1, {end_index}, "defbuffer1", RELative, SOURce, READing')
            results = self.keithley.read()
            results = results.split(',')
            results = list(map(float, results))
            data = {
                'time' : results[::3],
                'source' : results[1::3],
                'reading' : results[2::3]
            }
        else:
            self.keithley.write(':TRACe:ACTual:END?')
            end_index = int(self.keithley.read())
            self.keithley.write(f':TRACe:DATA? 1, {end_index}, "defbuffer1"')
            data = self.keithley.read()

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = timestamp

        dataframe = pd.DataFrame(data)

        fullfilename = self.save_directory + filename + '.csv'
        dataframe.to_csv(fullfilename, mode = 'w', index = False)

        return (True, "Saved data to at " + fullfilename)
    

