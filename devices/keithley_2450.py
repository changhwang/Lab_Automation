"""Requires download of NI-VISA with equivalent bitness"""
import pyvisa
import time
from typing import Optional, Tuple
from device import Device, check_initialized


def sleep(t):
    time.sleep(t)


class Keithley2450(Device):
    #save_directory = 'data/source_measuring/'

    def __init__(self, name: str, ID: str, query_delay: int, position: str):
        super().__init__(name)
        self.ID = ID
        self.query_delay = query_delay
        self.position = position
        self.keithley = pyvisa.ResourceManager().open_resource(self.ID)
        print(self.keithley.query('*IDN?'))
        sleep(self.query_delay)
        self.keithley.write('ROUT:TERM ' + self.position)

    @property   #TODO: Check if necessary
    def terminal_pos(self) -> str:
        return self.position
    
    def initialize(self) -> Tuple[bool, str]:
        self.keithley.write('*RST')
        self._is_initialized = True
        return (True, "Initialized Keithley2450 by performing device reset")

    def deinitialize(self) -> Tuple[bool, str]:

        #TODO: Keithley deinitialization steps
        self._is_initialized = False
        return(True, "Deinitialized Keithley2450")
    
    @check_initialized
    def wait(self):
        self.keithley.query('*OPC?')
        if self.keithley.query('*ESR?') != 1: 
            self.keithley.write('*CLS')
            print("Wait Completed, Standard Event Status Register cleared")

    @check_initialized
    def write_command(self, command: str):
        self.keithley.write(command)
        
    @check_initialized
    def terminal_pos(self, position: str):              # set terminal position rear or front
        if position == "rear":
            self.keithley.write('ROUT:TERM REAR')
            self.wait()
        elif position == "front":
            self.keithley.write('ROUT:TERM FRONT')
            self.wait()
        else:
            raise Exception(f"Expected 'rear' or 'front', found {position}")
    
    def error_check(self):
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
    def IV_characteristic(self, ilimit: float, vmin: float, vmax: float, steps: int, delay: float):
        """Sourcing voltage and measuring current with linear sweep"""
        if ilimit >= 1e-9 and ilimit <= 1.05:
            self.keithley.write('SOURce:VOLT:ILIMit ' + str(ilimit))
        else:
            raise Exception(f"Expected source current limit between 1nA and 1.05A")

        if vmin < -210 or vmin > 210:
            raise Exception(f"Voltage minimum out of range -210V to 210V")
        
        if vmax < -210 or vmin > 210:
            raise Exception(f"Voltage maximum out of range -210V to 210V")
        if vmax < vmin:
            raise Exception(f"Voltage minimum is greater than voltage maximum")

        if delay < 50e-6:
            raise Exception(f"Delay value too small, must be greater than 50 µs")
        
        #TODO: Buffer/defbuffer IF statements, if necessary

        self.keithley.write('*RST')
        self.keithley.write('SENS:CURR:RANG:AUTO ON')
        self.keithley.write('SYS:RSEN ON')
        self.wait()
        self.keithley.write(f"SOURce:VOLT:ILIMit {ilimit}")
        self.keithley.write(f"SOURce:SWE:VOLT:LIN {vmin}, {vmax}, {steps}, {delay}")
        self.keithley.write('INIT')
        self.keithley.write('*WAI')
        
    @check_initialized
    def get_data(self):
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
        return data
