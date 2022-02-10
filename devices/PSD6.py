from serial_device import SerialDevice
import time
from typing import Optional, Tuple, Union

### ERASE EVERY .self.start_serial() WHEN APPLYING EXECUTION COMMAND!!!

class PSD6pump(SerialDevice):
    def __init__(
            self,
            name: str,
            port: str,
            baudrate: int,
            timeout: Optional[float] = 10.0,
            default_speed: int = 10,
            poll_interval: float = 0.1):

        super().__init__(name, port, baudrate, timeout)
        self._default_speed = default_speed
        self._poll_interval = poll_interval
        self._max_speed = 40

    @property
    def default_speed(self) -> int:
        return self._default_speed

    @default_speed.setter
    def default_speed(self, speed: int):
        if speed > 0 and speed < self._max_speed:
            self._default_speed = speed

    def initialize(self) -> Tuple[bool, str]:
        self.start_serial()
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        self.check_error()
        self.ser.reset_input_buffer()

        was_turned_on, message = self.pump_on()
        if not was_turned_on:
            self._is_initialized = False
            return (was_turned_on, message)

        # set speed to default(10), move syringe to home, move valve to #1
        print("Initialization setting : moving syringe to home, valve to #1")
        command = "/1h24001R\r\n"
        self.ser.write(command.encode('ascii'))

        max_time_end = time.time() + 120

        # check valve type is 6
        if type(self.valvetype()) != int:
            return (False, str(self.valvetype()))
        else:
            while self.valvetype() != 6:
                time.sleep(self._poll_interval)
                if time.time() > max_time_end:
                    return (False, "Valve type error. Re-initialize! ")

        command = "/1S10A0R\r\n"
        self.ser.write(command.encode('ascii'))

        # check valve is on #1
        if type(self.valveposition()) != int:
            return (False, str(self.valveposition()))
        else:
            while self.valveposition() != 1:
                time.sleep(self._poll_interval)
                if time.time() > max_time_end:
                    return (False, "Valve position error. Re-initialize! ")


        # check syringe position is home(0)
        time.sleep(1)
        if type(self.syringeposition()) != int :
            return (False, str(self.syringeposition()))
        else :
            while self.syringeposition() > 1.1 :
                time.sleep(self._poll_interval)
                if time.time() > max_time_end:
                    return(False, "Syringe moving timeout. Re-initialize! ")


        self._is_initialized = True
        return (True, "Successfully initialized pump at 0 and valve at 1")

    def deinitialize(self) -> Tuple[bool, str]:
        self.start_serial()
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")

        was_syringe_zeroed, message_syringe = self.move_syringe_absolute(0)
        if not was_syringe_zeroed:
            return (was_syringe_zeroed, message_syringe)

        was_valve_at_1, message_valve = self.move_valve_position(1)
        if not was_valve_at_1:
            return (was_valve_at_1, message_valve)

        return (True, "Successfully deinitialized axes ")


    def syringe_home(self) -> Tuple[bool,str]:
        self.start_serial()
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")

        was_successful, message = self.move_syringe_absolute(0)
        if not was_successful :
            return (was_successful, message)

        return (True, "Successfully homed syringe")

    def move_syringe_absolute(self, position: int, speed: Optional[int] = None) -> Tuple[bool, str]:
        self.start_serial()
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        if not self._is_initialized:
            return (False, "Pump is not not initialized. ")

        command = "/1"

        if speed is None:
            speed = self._default_speed
        elif 1<= speed <= 40 :
            speed = int(round(speed))
        else :
            return (False, "Invalid speed input! ")

        command += "S" + str(speed)

        if 0<= position <=6000 :
            position = int(round(position))
        else :
            return (False, "Invalid position input! ")

        command += "A" + str(position) + "R\r\n"
        self.ser.write(command.encode('ascii'))

        max_time_end = time.time() + 1300
        if type(self.syringeposition()) != int :
            return (False, str(self.syringeposition()))
        else :
            while abs(self.syringeposition() - position) > 1.1 :
                time.sleep(self._poll_interval)
                if time.time()>max_time_end :
                    return (False, "Syringe movement timeout! ")

        was_successful, message = self.check_error()
        if not was_successful :
            return (was_successful, message)
        else:
            return (True, "Successfully completed absolute syringe move at "+ str(position))


    def move_valve_position(self, position: int) -> Tuple[bool, str]:
        self.start_serial()
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")
        if not self._is_initialized:
            return (False, "Pump is not not initialized. ")

        if type(self.valvetype()) != int:
            return (False, str(self.valvetype()))
        elif self.valvetype() != 6 :
            return (False, "Wrong valve type! ")

        command = "/1"

        if 0<= position <= 6 :
            command += "h2400" + str(position)
        else :
            return (False, "Invalid valve number! ")

        command += "R\r\n"
        self.ser.write(command.encode('ascii'))

        max_time_end = time.time() + 100
        if type(self.valveposition()) != int:
            return (False, str(self.valveposition()))
        else:
            while self.valveposition() != position:
                time.sleep(self._poll_interval)
                if time.time() > max_time_end :
                    return(False, "Valve movement timeout! ")


        was_successful, message = self.check_error()
        if not was_successful :
            return (was_successful, message)
        else:
            return (True, "Successfully moved valve position at " + str(position))


    def pump_on(self) -> Tuple[bool, str]:
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")

        # enable h factor command
        print("Enabling h command... ")
        command1 = "/1h30001R\r\n"
        self.ser.write(command1.encode('ascii'))
        self.waitpumpready()

        # initialize valve
        print("Initializing valve... ")
        command2 = "/1h20000R\r\n"
        self.ser.write(command2.encode('ascii'))
        self.waitpumpready()

        # initialize pump
        command3 = "/1h10000R\r\n"
        self.ser.write(command3.encode('ascii'))
        self.waitpumpready()

        was_successful, message = self.check_error()
        if was_successful is True:
            return(was_successful, "Pump initialized - ready to go! ")
        else :
            return(False, "Pump initialization failure. ")


    def check_error(self) -> Tuple[bool, str]:
        self.start_serial()
        print("checking error... ")

        if not self.ser.is_open:
            return (False, "Serial port " + self._port + "is not open. ")

        command = '/1Q\r\n'
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response == b'':
            return (False, "Response timed out. ")

        statusbyte = response.strip()[2:-1].decode('ascii')

        if statusbyte[0] == '`':
            return (True, "Pump ready - no error. ")
        else:
            # flush error buffer
            for n in range(10):
                self.ser.write(command.encode('ascii'))
                self.ser.readline()
            # flush serial input buffer
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return (False, self.statusinfo[statusbyte[0]])

    def waitpumpready(self):
        self.start_serial()
        max_time_end = time.time() + 1300
        print("Waiting for pump... ")
        time.sleep(10)

        while True:
            time.sleep(0.2)
            command = '/1Q\r\n'
            self.ser.write(command.encode('ascii'))
            response = self.ser.readline()
            statusbyte = response.strip()[2:-1].decode('ascii')
            print("pump status : " + statusbyte[0] + '-' + self.statusinfo[statusbyte[0]])
            if statusbyte[0] == '`':
                break
            elif time.time() > max_time_end:
                print("Pump Timeout! ")
                break

    def syringeposition(self) -> Union[str, int]:
        self.start_serial()
        if not self.ser.is_open:
            return "Serial port " + self._port + "is not open. "

        command = '/1?4\r\n'
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        if response == b'':
            return "Syringe position response timed out. "
        else:
            return int(response.strip()[3:-1].decode('ascii'))

    def valveposition(self)-> Union[str, int]:
        self.start_serial()
        command = '/1?24000\r\n'
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        if response == b'':
            return "Valve position response timed out. "
        else:
            return int(response.strip()[3:-1].decode('ascii'))

    def valvetype(self)-> Union[str, int]:
        self.start_serial()
        command = '/1?21000\r\n'
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        if response == b'':
            return "Valve type Response timed out. "
        else:
            return int(response.strip()[3:-1].decode('ascii'))

    statusinfo = {
        '@': "Pump busy - no error",
        '`': "Pump ready - no error",
        'a': "Initialization error – pump failed to initialize",
        'b': "Invalid command – unrecognized command is used.",
        'c': "Invalid operand – invalid parameter is given with a command.",
        'd': "Invalid command sequence – command communication protocol is incorrect",
        'f': "EEPROM failure – EEPROM is faulty",
        'g': "Syringe not initialized – syringe failed to initialize",
        'i': "Syringe overload – syringe encounters excessive back pressure",
        'j': "Valve overload – valve drive encounters excessive back pressure",
        'k': "Syringe move not allowed – valve is in the bypass or throughput position, syringe move commands are not allowed",
        'o': "Pump busy - command buffer is full"
    }
