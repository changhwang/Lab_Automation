from typing import Type, Optional
import yaml
from yaml.representer import Representer
from abc import ABCMeta

from commands.command import Command


Representer.add_representer(ABCMeta, Representer.represent_name)


class CommandSequence:
    def __init__(self):
        self.device_list = []
        self.command_list = []
        self.num_iterations = 1
        self.processed_devices = []
        self.processed_commands = []
        self.processed_delays = []
        self.device_dict = {}

    def add_command(
            self, 
            command_cls:  Type[Command],
            receiver_name: str,
            delay: float = 0.0, 
            index: Optional[int] = None,
            **kwargs):


        dict_to_add = {
            'class': command_cls,
            'receiver_name': receiver_name,
            'args': [{}],
            'delay': delay
        }
        for key, value in kwargs.items():
            dict_to_add['args'][0][key] = value

        if index is None:
            self.command_list.append(dict_to_add)
        else:
            self.command_list.insert(index, dict_to_add)
    
    def remove_command_by_index(self, index: int):
        del self.command_list[index]

    def move_command_by_index(self, old_index:int, new_index: int):
        if old_index >= 0 and old_index <= len(self.command_list) - 1 and new_index >= 0 and new_index <= len(self.command_list) - 1:
            if old_index != new_index:
                self.command_list.insert(new_index, self.command_list.pop(old_index))
        else:
            print("Invalid indices")

    def add_device(self, receiver_cls, index: Optional[int] = None, **kwargs):
        dict_to_add = {
            'class': receiver_cls,
            'args': {}
        }

        for key,value in kwargs.items():
            dict_to_add['args'][key] = value

        if index is None:
            self.device_list.append(dict_to_add)
        else:
            self.device_list.insert(index, dict_to_add)
    
    def remove_device_by_index(self, index: int):
        del self.device_list[index]

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

    def add_command_args(self, command_index: int, arg_index: Optional[int] = None, **kwargs):
        arg_dict = {}
        for key, value in kwargs.items():
            arg_dict[key] = value

        if arg_index is None:
            self.command_list[command_index]['args'].append(arg_dict)
        else:
            self.command_list[command_index]['args'].insert(arg_index, arg_dict)
              
    def remove_command_args_by_index(self, command_index: int, arg_index: int = None):
            del self.command_list[command_index]['args'][arg_index]

    def verify_device_list(self):
        # each device must be unique
        pass

    def verify_command_list(self):
        # loop end must be after loop start
        # either they are both included or both not included

        pass
    
    def process_devices(self):
        self.processed_devices = []
        self.device_dict = {}
        for device in self.device_list:
            device_cls = device['class']
            device_argdict = device['args']
            self.processed_devices.append(device_cls(**device_argdict))
            key = device_argdict['name']
            value = self.processed_devices[-1]
            self.device_dict[key] = value

    def process_commands(self):
        self.processed_commands = []
        self.processed_delays = []
        current_step_args = [dict() for x in range(len(self.command_list))]
        iteration = 0
        ndx = 0

        while ndx < len(self.command_list):
            element = self.command_list[ndx]
            if type(element) is str:
                # currently doesnt resolve recursively if loop start and loop end are next to each other
                if element == "LOOP START":
                    ndx += 1
                    element = self.command_list[ndx]
                if element == "LOOP END":
                    if iteration < self.num_iterations - 1:
                        # if still looping, then go to step after LOOP START marker
                        ndx = self.command_list.index("LOOP START")
                        ndx += 1
                        element = self.command_list[ndx]
                        iteration += 1
                    else:
                        # if reached max iterations, the skip and set iteration index to 0
                        ndx += 1
                        element = self.command_list[ndx]
                        iteration = 0 #exiting loop section

            # element should be a dictionary
            # get the command's class and receiver name
            command_cls = self.command_list[ndx]['class']
            receiver_name = self.command_list[ndx]['receiver_name']

            # get the arg dict for the current command (ndx) and current iteration
            if iteration > len(self.command_list[ndx]['args']) - 1:
                current_args = self.command_list[ndx]['args'][-1]
            else:
                current_args = self.command_list[ndx]['args'][iteration]

            # update the live arg dict with changes from the list
            for key, value in current_args.items():
                current_step_args[ndx][key] = value

            # get command's delay and add to list
            self.processed_delays.append(self.command_list[ndx]['delay'])

            # add the actual receiver object to the arg dict
            current_step_args[ndx]['receiver'] = self.device_dict[receiver_name]
            self.processed_commands.append(command_cls(**current_step_args[ndx]))
            ndx += 1

    def save_to_yaml(self, filename: str):
        data_list = [self.device_list, self.command_list]
        with open(filename, 'w') as file:
            yaml.dump(data_list, file, default_flow_style=False, sort_keys=False)

    def load_from_yaml(self, filename: str):
        with open(filename) as file:
            imported_list = yaml.load(file, Loader=yaml.FullLoader)
            self.device_list = imported_list[0]
            self.command_list = imported_list[1]


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