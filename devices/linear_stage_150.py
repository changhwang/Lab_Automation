from typing import Optional, Tuple
from struct import pack,unpack
import time
from .device import SerialDevice, check_serial, check_initialized

class LinearStage150(SerialDevice):
    def __init__(self, name: str, port: str = '\'/dev/cu.URT0\'', baudrate: int = 115200, timeout: float | None = 0.1, destination: int = 0x50, source: int = 0x01, channel: int = 1):
        super().__init__(name, port, baudrate, timeout)
        self._destination = destination
        self._source = source
        self._channel = channel
        print("dest: "+str(self._destination))
    
    @check_serial
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = False

        #TODO: lts150: initialize, home it (if needed)

        self._is_initialized = True
        return (True, "Successfully initialized LTS150.")
        # return super().initialize()

    def deinitialize(self) -> Tuple[bool, str]:
        
        #TODO: lts150: deinitialize
        # if reset_init_flag: //used in other devices
        self._is_initialized = False
        return (True, "Successfully deinitialized LTS150.")
        # return super().deinitialize()
    
    @check_serial
    @check_initialized
    def get_enabled_state(self) -> bool:
        self._is_enabled = False

        #TODO: lts150 get enabled state, MGMSG_MOD_GET_CHANENABLESTATE

        return self._is_enabled
    
    def set_enabled_state(self,  state: bool) -> Tuple[bool, str]:
        if state:
            self.ser.write(pack('<HBBBB',0x0210,1,0x01,self._destination,self._source))
        else:
            self.ser.write(pack('<HBBBB',0x0210,1,0x02,0x50,0x01))
        time.sleep(0.1)
        #TODO-VERIFY: (verify) lts150 set enable state, MGMSG_MOD_SET_CHANENABLESTATE
        #TODO: check if flushing is needed
        return (True, "Successfully set enable state to " + str(state) + ".")

    @check_serial
    @check_initialized #TODO: lts150: check if initialized required for absolute movement
    def move_absolute(self, position: float) -> Tuple[bool, str]:
        Device_Unit_SF = 409600
        dUnitpos = int(Device_Unit_SF*position)
        self.ser.write(pack('<HBBBBHI',0x0453,0x06,0x00,self._destination|0x80,self._source,self._channel,dUnitpos))

        #Confirm stage completed move before advancing; MGMSG_MOT_MOVE_COMPLETED 
        Rx = ''
        Moved = pack('<H',0x0464)
        while Rx != Moved:
            Rx = self.ser.read(2)

        print('Move Complete')

        self.ser.flushInput()
        self.ser.flushOutput()

        #TODO-VERIFY: (verify) lts150 move absolute, MGMSG_MOT_MOVE_ABSOLUTE

        return (True, "Successfully moved stage to position " + str(position) + "[units].")

    @check_serial
    @check_initialized #TODO: lts150: check is initialized required for relative movement
    def move_relative(self, distance: float) -> Tuple[bool, str]:
        
        #TODO: lts150 move relative, MGMSG_MOT_MOVE_RELATIVE

        return (True, "Successfully moved stage by distance " + str(distance) + "[units].")
