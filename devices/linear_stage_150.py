from typing import Optional, Tuple
from struct import pack, unpack
import time
from .device import SerialDevice, check_serial, check_initialized


class LinearStage150(SerialDevice):
    def __init__(
        self,
        name: str,
        port: str = "'COM6'",
        baudrate: int = 115200,
        timeout: float | None = 0.1,
        destination: int = 0x50,
        source: int = 0x01,
        channel: int = 1,
    ):
        super().__init__(name, port, baudrate, timeout)
        self._destination = destination
        self._source = source
        self._channel = channel
        # print("dest: "+str(self._destination))

    def get_init_args(self) -> dict:
        args_dict = {
            "name": self._name,
            "port": self._port,
            "baudrate": self._baudrate,
            "timeout": self._timeout,
            "destination": self._destination,
            "source": self._source,
            "channel": self._channel,
        }
        return args_dict

    def update_init_args(self, args_dict: dict):
        self._name = args_dict["name"]
        self._port = args_dict["port"]
        self._baudrate = args_dict["baudrate"]
        self._timeout = args_dict["timeout"]
        self._destination = args_dict["destination"]
        self._source = args_dict["source"]
        self._channel = args_dict["channel"]

    @check_serial
    def initialize(self) -> Tuple[bool, str]:
        self._is_initialized = False

        # lts150: initialize, home it (if needed)

        # Home Stage; MGMSG_MOT_MOVE_HOME
        self.ser.write(pack("<HBBBB", 0x0443, self._channel, 0x00, self._destination, self._source))
        print("Homing stage...")

        # Confirm stage homed before advancing; MGMSG_MOT_MOVE_HOMED
        Rx = ""
        Homed = pack("<H", 0x0444)
        while Rx != Homed:
            Rx = self.ser.read(2)
        print("Stage Homed")
        self.ser.flushInput()
        self.ser.flushOutput()

        self._is_initialized = True
        return (True, "Successfully initialized LTS150 by homing it.")
        # return super().initialize()

    def deinitialize(self) -> Tuple[bool, str]:
        # i dont think this is needed: lts150: deinitialize
        # if reset_init_flag: //used in other devices
        self._is_initialized = False
        return (True, "Successfully deinitialized LTS150.")
        # return super().deinitialize()

    @check_serial
    # @check_initialized
    def get_enabled_state(self) -> bool:
        self._is_enabled = False

        # TODO: lts150 get enabled state, MGMSG_MOD_GET_CHANENABLESTATE
        # self.ser.write(pack('<HBBBB',0x0212,self._channel,0x00,self._destination,self._source))

        return self._is_enabled

    def set_enabled_state(self, state: bool) -> Tuple[bool, str]:
        if state:
            self.ser.write(pack("<HBBBB", 0x0210, 1, 0x01, self._destination, self._source))
        else:
            self.ser.write(pack("<HBBBB", 0x0210, 1, 0x02, 0x50, 0x01))
        time.sleep(0.1)

        self.ser.flushInput()
        self.ser.flushOutput()
        return (True, "Successfully set enable state to " + str(state) + ".")

    @check_serial
    def get_position(self) -> float:
        self._position = 0.0
        Device_Unit_SF = 409600
        # MGMSG_MOT_GET_POSCOUNTER
        self.ser.write(pack("<HBBBB", 0x0411, self._channel, 0x00, self._destination, self._source))

        # Read back position returns by the cube; Rx message MGMSG_MOT_GET_POSCOUNTER
        header, chan_dent, position_dUnits = unpack("<6sHI", self.ser.read(12))
        self._position = position_dUnits / float(Device_Unit_SF)

        return self._position

    @check_serial
    # @check_initialized
    def move_absolute(self, position: float) -> Tuple[bool, str]:
        if position > 150:
            return (False, "Position " + str(position) + " is out of range.")

        Device_Unit_SF = 409600
        dUnitpos = int(Device_Unit_SF * position)
        self.ser.write(
            pack(
                "<HBBBBHI",
                0x0453,
                0x06,
                0x00,
                self._destination | 0x80,
                self._source,
                self._channel,
                dUnitpos,
            )
        )

        # Confirm stage completed move before advancing; MGMSG_MOT_MOVE_COMPLETED
        Rx = ""
        Moved = pack("<H", 0x0464)
        while Rx != Moved:
            Rx = self.ser.read(2)

        print("Move Complete")

        self.ser.flushInput()
        self.ser.flushOutput()

        return (
            True,
            "Successfully moved stage to position " + str(position) + "[units].",
        )

    @check_serial
    # @check_initialized
    def move_relative(self, distance: float) -> Tuple[bool, str]:
        if distance + self.get_position() > 150:
            return (
                False,
                "Position " + str(distance + self.get_position()) + " is out of range.",
            )

        Device_Unit_SF = 409600
        dUnitpos = int(Device_Unit_SF * distance)
        self.ser.write(
            pack(
                "<HBBBBHI",
                0x0448,
                0x06,
                0x00,
                self._destination | 0x80,
                self._source,
                self._channel,
                dUnitpos,
            )
        )

        # Confirm stage completed move before advancing; MGMSG_MOT_MOVE_COMPLETED
        Rx = ""
        Moved = pack("<H", 0x0464)
        while Rx != Moved:
            Rx = self.ser.read(2)

        print("Move Complete")

        self.ser.flushInput()
        self.ser.flushOutput()

        return (
            True,
            "Successfully moved stage by distance " + str(distance) + "[units].",
        )
