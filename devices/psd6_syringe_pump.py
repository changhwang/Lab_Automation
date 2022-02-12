import time
from typing import Optional, Tuple, List

from testing.syringe_test import is_ready

from .device import SerialDevice, check_initialized, check_serial


# terminology, valve_num or position; steps_per_sec or step_rate, valve or port
# dead volume flags
# double check flowrates are accurate

class PSD6SyringePump(SerialDevice):
    status_dict = {
        '@': "Pump busy - no error",
        '`': "Pump ready - no error",
        'a': "Initialization error - pump failed to initialize",
        'b': "Invalid command - unrecognized command is used.",
        'c': "Invalid operand - invalid parameter is given with a command.",
        'd': "Invalid command sequence - command communication protocol is incorrect",
        'f': "EEPROM failure - EEPROM is faulty",
        'g': "Syringe not initialized - syringe failed to initialize",
        'i': "Syringe overload - syringe encounters excessive back pressure",
        'j': "Valve overload - valve drive encounters excessive back pressure",
        'k': "Syringe move not allowed - valve is in the bypass or throughput position, syringe move commands are not allowed",
        'o': "Pump busy - command buffer is full"
    }
    
    # volume_factor = {'ul': 1.0, 'ml': 1000.0}
    # time_factor = {'s': 1.0, 'min': 1.0/60.0}
    
    def __init__(
            self,
            name: str,
            port: str,
            baudrate: int = 9600,
            timeout: Optional[float] = 10.0,
            stroke_volume: float = 5000.0, 
            stroke_steps: int = 6000,
            default_flowrate: float = 1000.0,
            # volume_unit: str = 'ul',
            # time_unit: str = 's',
            port_dead_volumes: List[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            poll_interval: float = 0.1):

        super().__init__(name, port, baudrate, timeout)
        self._stroke_volume = stroke_volume
        self._stroke_steps = stroke_steps
        self._default_flowrate = default_flowrate
        # self._volume_unit = volume_unit
        # self._time_unit = time_unit
        self._port_dead_volumes = port_dead_volumes
        self._poll_interval = poll_interval
        
        # technically if I send a command that is out of range of these values
        # the pump should be able to give me an error message anyways
        # but if I store a default flowrate in this object I'd rather
        # have it be correct, than let the pump handle it because
        # setting a wrong default flowrate here does not yield an error until
        # later when some other command is sent that uses it
        self._max_steps_per_sec = 10000
        self._min_steps_per_sec = 2
        
        # # this is ok to leave out since anything using a position immediately issues a command
        # self._min_position = 0
        # self._max_position = 6000

    @property
    def default_flowrate(self) -> float:
        return self._default_flowrate
    
    @default_flowrate.setter
    def default_flowrate(self, flowrate: float):
        # careful units!
        # steps_per_sec = flowrate / self._stroke_volume * self._stroke_steps
        # steps_per_sec = int(round(steps_per_sec))
        steps_per_sec = self.volume_to_step(flowrate)
        if steps_per_sec >= self._min_steps_per_sec and steps_per_sec <= self._max_steps_per_sec:
            self._default_flowrate = flowrate
            
    @property
    def default_step_rate(self) -> int:
        return self.volume_to_step(self._default_flowrate)
            
    
    # for init and deinit, it needs to set the waste valve!, not just left most or right most!!
    # we need to check, does it move valve first? or syringe first? IT MOVES VALVE FIRST
    # either way, enable hfactor, initialize valve, move to waste, then either run Y/Z or init syringe only
    @check_serial
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = False
        
        # sets syringe to 0 (max dispense)
        # sets valve to position 1 (Use command Z to set valve to 6 instead)
        command = '/1ZR\r' # sets output to right side
        self.ser.write(command.encode('ascii'))
        is_ready, message = self.check_error_ready()
        if not is_ready:
            return (False, message)
        self._is_initialized = True
        return (True, "Successfully initialized PSD6 syringe pump.")
    
    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        #move to waste first
        if reset_init_flag:
            self._is_initialized = False
        return (True, "Successfully deinitialized PSD6 syringe pump.")
        
        
    
    def volume_to_step(self, volume: float):
        return int(round(volume / self._stroke_volume * self._stroke_steps))
    
    def step_to_volume(self, step: int):
        return float(step / self._stroke_steps * self._stroke_volume)
    
    # change order, valve num before flowrate
    def move_syringe_absolute_volume(self, volume: float, valve_num: Optional[int] = None, flowrate: Optional[float] = None):
        step = self.volume_to_step(volume)
        if flowrate is None:
            step_rate = None
        else:
            step_rate = self.volume_to_step(flowrate)
        return self.move_syringe_absolute_step(step, valve_num, step_rate)

    # dead volume compensation flag
    def infuse_syringe_volume(self, volume: float, valve_num: Optional[int] = None, flowrate: Optional[float] = None):
        step = self.volume_to_step(volume)
        if flowrate is None:
            step_rate = None
        else:
            step_rate = self.volume_to_step(flowrate)
        return self.infuse_syringe_steps(step, valve_num, step_rate)
    
    def withdraw_syringe_volume(self, volume: float, valve_num: Optional[int] = None, flowrate: Optional[float] = None):
        step = self.volume_to_step(volume)
        if flowrate is None:
            step_rate = None
        else:
            step_rate = self.volume_to_step(flowrate)
        return self.withdraw_syringe_steps(step, valve_num, step_rate)
    
    
    # switch order of step and volume display in message, volume first steps in ()
    @check_serial
    @check_initialized
    def move_syringe_absolute_step(self, step: int, valve_num: Optional[int] = None, step_rate: Optional[int] = None):
        if valve_num is not None:
            self.move_valve_position(valve_num)
        if step_rate is None:
            step_rate = self.default_step_rate
        # this is here in case a user manually passes a step_rate
        if isinstance(step_rate, float):
            step_rate = int(round(step_rate))
        
        command = '/1V' + str(step_rate) + 'A' + str(step) + 'R\r'
        self.ser.write(command.encode('ascii'))
        is_ready, message = self.check_error_ready()
        if not is_ready:
            return (False, message)

        volume = self.step_to_volume(step)
        return (True, "Successfully moved syringe to step " + str(step) + ", volume " + str(volume) + " uL.")
       
    @check_serial
    @check_initialized
    def infuse_syringe_steps(self, steps: int, valve_num: Optional[int] = None, step_rate: Optional[int] = None):
        if valve_num is not None:
            self.move_valve_position(valve_num)
        if step_rate is None:
            step_rate = self.default_step_rate
        if isinstance(step_rate, float):
            step_rate = int(round(step_rate))
        
        command = '/1V' + str(step_rate) + 'D' + str(steps) + 'R\r'
        self.ser.write(command.encode('ascii'))
        is_ready, message = self.check_error_ready()
        if not is_ready:
            return (False, message)

        volume = self.step_to_volume(steps)
        return (True, "Successfully infused syringe by steps " + str(steps) + ", volume " + str(volume) + " uL.")
    
    @check_serial
    @check_initialized
    def withdraw_syringe_steps(self, steps: int, valve_num: Optional[int] = None, step_rate: Optional[int] = None):
        if valve_num is not None:
            self.move_valve_position(valve_num)
        if step_rate is None:
            step_rate = self.default_step_rate
        if isinstance(step_rate, float):
            step_rate = int(round(step_rate))
        
        command = '/1V' + str(step_rate) + 'P' + str(steps) + 'R\r'
        self.ser.write(command.encode('ascii'))
        is_ready, message = self.check_error_ready()
        if not is_ready:
            return (False, message)

        volume = self.step_to_volume(steps)
        return (True, "Successfully withdrew syringe by steps " + str(steps) + ", volume " + str(volume) + " uL.")
    
    @check_serial
    @check_initialized
    def move_valve_position(self, valve_num: int):
        command = '/1I' + str(valve_num) + "R\r"
        self.ser.write(command.encode('ascii'))
        is_ready, message = self.check_error_ready()
        if not is_ready:
            return (False, message)
        
        return (True, "Successfully moved valve to position " + str(valve_num))
    
    
    # we need to think how numerical information is returned
    # either return value, or return tuple of (bool, message=value)
    # or consider adding a new attribute to the CommandResult class
    def syringe_position(self):
        pass
    
    def valve_position(self):
        command = '/1?24000R\r'
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        position = response.decode('ascii')[3]
        return position

    def port_dead_volume(self, port_num: int):
        # no real need to check port, any command sent regarding a wrong port will be caught by the pump
        # if port_num < 1 or port_num > 6:
        #     pass 
        return self._port_dead_volumes[port_num-1]
    
    def check_error_ready(self, read_first: bool = True) -> Tuple[bool, str]:
        # Read first if checking right after sending a command
        # there should be a response in the input buffer
        if read_first:
            response = self.ser.readline()
            status_byte = response.decode('ascii')[2]
            if status_byte not in '@`':
                # there was a problem with the initial response
                return (False, self.status_dict[status_byte])
        
        # keep querying status until ready or error
        status_byte = '@'    
        while status_byte == '@':
            time.sleep(self._poll_interval)
            status_byte = self.query_status_byte()
            
        message = self.status_dict[status_byte]
        
        if status_byte == '`':
            return (True, message)
        else:
            return (False, message)

    def query_status_byte(self):
        command = "/1QR\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        status_byte = response.decode('ascii')[2]
        return status_byte