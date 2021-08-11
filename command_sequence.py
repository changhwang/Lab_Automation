from typing import Type, Optional, List, Union
import yaml
from yaml.representer import Representer
from abc import ABCMeta

from commands.command import Command
from devices.device import Device
from commands.utility_commands import LoopStartCommand, LoopEndCommand

# Representer.add_representer(ABCMeta, Representer.represent_name)

# Should move loop interpretation to invoker?
# Make functional with yaml safe_load

class CommandSequence:

    recipe_directory = 'recipes/'

    def __init__(self):
        self.device_list = []
        self.command_list = []
        self.num_iterations = 1
        # self.processed_devices = []
        # self.processed_commands = []
        # self.processed_delays = []
        self.device_by_name = {}

    def add_device(self, receiver: Device):
        self.device_list.append(receiver)
        self.update_device_by_name()

    def remove_device(self, receiver_name: str):
        if receiver_name in self.device_by_name:
            for ndx, device in enumerate(self.device_list):
                if device.name == receiver_name:
                    del self.device_list[ndx]
                    self.update_device_by_name()
                    break # Each device should have a unique name, always

    
    def remove_device_by_index(self, index: Optional[int] = None):
        if index is None:
            index = -1
        del self.device_list[index]
        self.update_device_by_name()

    def add_command(self, command: Union[Command, List[Command]], index: Optional[int] = None):
        if not isinstance(command, list):
            command = [command]
        if index is None:
            self.command_list.append(command)
        else:
            self.command_list.insert(index, command)
    
    def remove_command(self, index: Optional[int] = None):
        if index is None:
            index = -1
        del self.command_list[index]

    def move_command_by_index(self, old_index: int, new_index: int):
        if old_index >= 0 and old_index <= len(self.command_list) - 1 and new_index >= 0 and new_index <= len(self.command_list) - 1:
            if old_index != new_index:
                self.command_list.insert(new_index, self.command_list.pop(old_index))
        else:
            print("Invalid indices")

    def add_loop_start(self, index: Optional[int] = None):
        if index is None:
            self.command_list.append("LOOP START")
        else:
            self.command_list.insert(index, "LOOP START")

    def add_loop_end(self, index: Optional[int] = None):
        if index is None:
            self.command_list.append("LOOP END")
        else:
            self.command_list.insert(index, "LOOP END")

    def add_command_iteration(self, command: Union[Command, List[Command]], index: Optional[int] = None, iteration: Optional[int] = None):
        if not isinstance(command, list):
            command = [command]
        if index is None:
            index = -1
        if iteration is None:
            # add to end of iteration list
            self.command_list[index].extend(command)
        else:
            # insert at specific iteration index
            for ndx in range(len(command)):
                self.command_list[index].insert(iteration, command.pop(-1))

    def remove_command_iteration(self, index: Optional[int] = None, iteration: Optional[int] = None):
        if index is None:
            index = -1
        if iteration is None:
            iteration = -1
        del self.command_list[index][iteration]

    def move_command_iteration_by_index(self, index: int, old_iter: int, new_iter: int):
        if old_iter >= 0 and old_iter <= len(self.command_list[index]) - 1 and new_iter >= 0 and new_iter <= len(self.command_list[index]) - 1:
            if old_iter != new_iter:
                self.command_list[index].insert(new_iter, self.command_list[index].pop(old_iter))
        else:
            print("Invalid indices")

    def verify_device_list(self):
        # each device must be unique (by name attribute)
        pass

    def verify_command_list(self):
        # loop end must be after loop start
        # either they are both included or both not included
        # iteration list has commands of same class
        pass
    
    def update_device_by_name(self):
        self.device_by_name = {}
        for device in self.device_list:
            self.device_by_name[device.name] = device

    def get_unlooped_command_list(self) -> List[Command]:
        unlooped_list = []
        index = 0
        iteration = 0
        loop_start_index = None

        while index < len(self.command_list):
            # Get the command at the current index and iteration
            # if current iteration is larger than the number of the current command's iterations then use the last one
            if iteration > len(self.command_list[index]) - 1:
                command = self.command_list[index][-1]
            else:
                command = self.command_list[index][iteration]
            
            if isinstance(command, LoopStartCommand):
                loop_start_index = index
                index += 1
                continue

            if isinstance(command, LoopEndCommand):
                iteration += 1
                if iteration < self.num_iterations:
                    index = loop_start_index + 1
                    continue
                else:
                    iteration = 0
                    index += 1
                    continue

            unlooped_list.append([command])
            index += 1
        return unlooped_list

    def save_to_yaml(self, filename: str):
        filename = self.recipe_directory + filename
        data_list = [self.device_list, self.command_list, self.num_iterations]
        with open(filename, 'w') as file:
            yaml.dump(data_list, file, default_flow_style=False, sort_keys=False)

    def load_from_yaml(self, filename: str):
        filename = self.recipe_directory + filename
        with open(filename) as file:
            # not safe loader
            imported_list = yaml.load(file, Loader=yaml.Loader)
            self.device_list = imported_list[0]
            self.command_list = imported_list[1]
            self.num_iterations = imported_list[2]


# Considered making loop start/end as "special" Command objects that can be added to the command list. Then the invoker will jump, etc. if it encounters one of these special commands
# At the moment, I decided against this as it requires coding in specific dependencies for these special commands in the invoker
# Instead the way it works right now is that the CommandSequence can have string marker elements for loop start/end in its command list and when the actual command object list is generated
# from the information in the command sequence the CommandSequence will "unwrap" the looping by interpreting the markers. The full "unwrapped" command list is then sent to the invoker
#
# The data that a CommandSequence maintains and can save/load to/from a yaml file is as follows:
# There are two lists, the device_list and command_list.
# When saving and loading from a yaml file these two are combined as elements of an overall list, e.g. [device_list, command_list].
# Each list has the information to dynamically instantiate device (receiver) objects and command objects.
#
# The device list:
# Each element of the device list corresponds to a device. 
# Each element is a dict with 2 entries:
# - the first, 'class', being the class of the device, 'class': ReceiverClass.
# - the second, 'args', being an arg dict containing the arguments to be unpacked when instantiating with the contructor, e.g. ReceiverClass(**arg_dict).
# When it is time to actually create the device and command objects the device_list is used to create the device objects 
# and add them to a device_dict with the key being the device's name attribute and the value being the device object.
# The purpose of the device dict is to provide a way for the commands to find the exact device (receiver) object that it needs during construction
#
# The command list:
# Each element of the command list corresponds to a command or a loop marker
# In the case of the loop marker, the element is just a single string, either "LOOP START" or "LOOP END"
# In the case of a command, the element is a dict with several entries:
# - the first, 'class', being the class of the command, 'class': CommandClass.
# - the second, 'receiver_name', being the name attribute of the device (receiver) that the command needs during construction (the device name is used to get the actual device object needed)
# - the third, 'args', corresponds to a list of dicts. Each dict in the list corresponds to the args to be unpacked during construction for a particular iteration
#       e.g. ...['args'][0] is the first arg_dict to unpack on the first iteration, ...['args'][1] is the second arg_dict to unpack on the second iteration.
#       This allows the parameters of the command to change on each iteration. If there will be more iterations than arg_dicts then the last one is used once the current iteration exceeds amount of arg_dicts
#       Therefore if you don't want a command to change within a loop, the list will contain only 1 arg_dict
# - the fourth, 'delay', is a float for the time in seconds to wait BEFORE the command starts. 
#       The value can also be the string "PAUSE" which indicates the program will pause and wait for the user to press Enter to continue. Or type quit to exit early
#       In the future the delay parameter will be incorporated as a command arg instead of a separate list
# When it is time to actually create the command object list to send to the invoker, the command_list is used to create the command objects using the current iteration's arg_dict.
# During this step, an entry is added to the dict for the 'receiver': receiver_object by looking up the device (receiver) object in the aforemention device_dict using its name
# The command is then appended to the processed_commands list. Likewise, the delays are appended to a list but this will be changed in the future to be part of the command's args
#
# It can be seen that the device name attribute needs to be standardized and a standard string should be used to correspond to the physical device in the lab
# In the future it might be worth looking into dumping the actual objects to the yaml file as opposed to the class and its constructor args. Although command objects needs receiver objects first.