import time
from typing import Optional, Tuple, Union

from .device import SerialDevice


class NewportESP301(SerialDevice):
    def __init__(
            self, 
            name: str,
            port: str,
            baudrate: int,
            timeout: Optional[float] = 1.0,
            axis_list: Tuple[int, ...] = (1,),
            default_speed: float = 20.0,
            poll_interval: float = 0.1):

        super().__init__(name, port, baudrate, timeout)
        self._axis_list = axis_list
        self._default_speed = default_speed
        self._poll_interval = poll_interval
        self._max_speed = 200.0

    @property
    def default_speed(self) -> float:
        return self._default_speed

    @default_speed.setter
    def default_speed(self, speed: float):
        if speed > 0.0 and speed < self._max_speed:
            self._default_speed = speed

    def initialize(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        self.check_error() # just used to flush error and serial input buffer if there is an error
        self.ser.reset_input_buffer() # flush the serial input buffer even if there was no error

        for axis in self._axis_list:
            # Make sure axis motor is turned on
            was_turned_on, message = self.axis_on(axis)
            if not was_turned_on:
                self._is_initialized = False
                return (was_turned_on, message)
            # set units to mm, homing value to 0, set max speed, set current speed 
            command = str(axis) + "SN2;" + str(axis) + "SH0;" + str(axis) + "VU" + str(self._max_speed) + ";" + str(axis) + "VA" + str(self.default_speed) + "\r"
            self.ser.write(command.encode('ascii'))

        # Make sure initialization of settings was successful
        was_successful, message = self.check_error()
        if not was_successful:
            self._is_initialized = False
            return (was_successful, message)

        for axis in self._axis_list:
            was_homed, message = self.home(axis)
            if not was_homed:
                self._is_initialized = False
                return (was_homed, message)
    
        self._is_initialized = True
        return (True, "Successfully initialized axes by setting units to mm, settings max/current speeds, and homing. Current position set to zero.")

    def deinitialize(self, reset_init_flag: bool = True) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        for axis in self._axis_list:
            was_zeroed, message = self.move_speed_absolute(0.0, speed=None, axis_number=axis)
            if not was_zeroed:
                return (was_zeroed, message)

        if reset_init_flag:
            self._is_initialized = False

        return (True, "Successfully deinitialized axes by moving to position zero.")

    def home(self, axis_number: int) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        command = str(axis_number) + "OR4\r"
        self.ser.write(command.encode('ascii'))

        while self.is_any_moving():
            time.sleep(self._poll_interval)
        # pause one more time in case motor stopped moving but position has not been reset yet     
        time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully homed axes " + str(axis_number))

    # Consider a decorator for checks?
    def move_speed_absolute(self, position: float, speed: Optional[float] = None, axis_number: int = 1) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")
        if not self._is_initialized:
            return (False, "ESP301 axes are not initialized.")

        if speed is None:
            speed = self._default_speed

        command = str(axis_number) + "VA" + str(speed) +"\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        if position >= 0.0:
            sign = "+"
        else:
            sign = "-"

        # removed the WS command because it causes timeouts when checking if moving 
        # command = str(axis_number) + "PA" + sign + str(abs(position)) + ";" + str(axis_number) + "WS\r"
        command = str(axis_number) + "PA" + sign + str(abs(position)) + "\r"
        self.ser.write(command.encode('ascii'))

        while self.is_moving(axis_number):
            time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully completed absolute move at " + str(position))

    def move_speed_relative(self, distance: float, speed: Optional[float] = None, axis_number: int = 1) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")
        if not self._is_initialized:
            return (False, "ESP301 axes are not initialized.")

        if speed is None:
            speed = self._default_speed

        command = str(axis_number) + "VA" + str(speed) +"\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        if distance >= 0.0:
            sign = "+"
        else:
            sign = "-"

        # removed the WS command because it causes timeouts when checking if moving 
        # command = str(axis_number) + "PR" + sign + str(abs(distance)) + ";" + str(axis_number) + "WS\r"
        command = str(axis_number) + "PR" + sign + str(abs(distance)) + "\r"

        self.ser.write(command.encode('ascii'))

        while self.is_moving(axis_number):
            time.sleep(self._poll_interval)

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)
        else:
            return (True, "Successfully completed relative move by " + str(distance))
        

    def is_axis_num_valid(self, axis_number: int) -> bool:
        if axis_number in self._axis_list:
            return True
        else:
            return False
    
    def is_moving(self, axis_number: int = 1) -> bool:
        if not self.ser.is_open:
            return False
        else:
            command = str(axis_number) + "MD?\r"
            self.ser.write(command.encode('ascii'))
            response = self.ser.readline()

            if response.strip().decode('ascii') == '0':
                # motion is not done = is moving
                return True
            else:
                # includes timeout case
                return False

    def is_any_moving(self) -> bool:
        is_moving_list = []
        for ndx, axis_number in enumerate(self._axis_list):
            command = str(axis_number) + "MD?\r"
            self.ser.write(command.encode('ascii'))
            response = self.ser.readline()

            if response.strip().decode('ascii') == '0':
                is_moving_list.append(True)
            else:
                is_moving_list.append(False)

        if any(is_moving_list):
            return True
        else: 
            return False


    def check_error(self) -> Tuple[bool, str]:
        # not needed for queries, but use when instructing to do something
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        command = "TB?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response == b'':
            return (False, "Response timed out.")
        
        response = response.strip().decode('ascii')

        if response[0] == '0':
            return (True, "No errors.")
        else:
            # flush the error buffer
            for n in range(10):
                self.ser.write(command.encode('ascii'))
                self.ser.readline()
            # flush the serial input buffer
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return (False, response)
    
    def position(self, axis_number: int = 1) -> Tuple[bool, Union[str, float]]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "TP\r"
        self.ser.write(command.encode('ascii'))
        position_str = self.ser.readline()
        if position_str == b'':
            return (False, "Response timed out.")
        else:    
            return (True, float(position_str.strip().decode('ascii')))

    def axis_on(self, axis_number: int = 1) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "MO\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        command = str(axis_number) + "MO?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '1':
            return (True, "Axis " + str(axis_number) + " motor successfully turned ON.")
        else:
            # also means timeout
            return (False, "Axis " + str(axis_number) + " motor failed to turned ON.")

    def axis_off(self, axis_number: int = 1) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        if not self.is_axis_num_valid(axis_number):
            return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(axis_number) + "MF\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        command = str(axis_number) + "MF?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '0':
            return (True, "Axis " + str(axis_number) + " motor successfully turned OFF.")
        else:
            # also means timeout
            return (False, "Axis " + str(axis_number) + " motor failed to turned OFF.")
