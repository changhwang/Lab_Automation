from abc import ABC, abstractmethod
from typing import Optional
from devices.device import Device


# TODO
# for the name and description that is unique to each command, it is easier to just use a dictionary and use that instead of rewriting for each command
# then each init will just add each arg to the dictionary (except for name? parent can add name to dict) then name and desc can be set by calling super() after filling the arg dict
# incorporate the delay param here and subsequent child classes can alter it in their constructor by using **kwargs to pass it up, see kwargtest.py
# Could do 2 dictionaries, 1 for the command and 1 for the args needed within command's execute, the second one could be simply passed to receiver methods through unpacking **dict
class Command(ABC):
    """The Command abstract base class which acts as an interface for other objects that use commands."""

    @abstractmethod
    def __init__(self, receiver: Device, delay: float = 0.0):
        # Child classes will still have 'receiver' in their signature (separate from **kwargs) because I want the IDE to hint at the specific receiver class
        # delay will be passed up through **kwargs as it is an secondary parameter for all commands 
        self._receiver = receiver
        self._params = {}
        self._params['receiver_name'] = receiver.name
        self._params['delay'] = delay
        self._was_successful = None
        self._result_message = None        

    # definitely enforce return None for execute()
    @abstractmethod
    def execute(self) -> None:
        """Execute abstract method from which all commands implement; accepts no arguments and returns None."""
        pass

    @property
    def name(self) -> str:
        """The command's name getter.

        Returns
        -------
        str
            Returns the command's class name followed by its parameters.
        """
        self._name = type(self).__name__
        for key, value in self._params.items():
            if not key == 'delay':
                self._name += " " + key + "=" + str(value)
        # I just want delay to be always be last when displayed
        self._name += " " + 'delay=' + str(self._params['delay'])
        return self._name

    @property
    def description(self) -> str:
        """The command's description getter.

        Returns
        -------
        str
            Returns the command's docstring
        """
        return self.__doc__

    @property
    def was_successful(self) -> Optional[bool]:
        """Whether the command's execution was successful or not.

        Returns
        -------
        Optional[bool]
            Returns True if the command's execution was successful, otherwise False. Initialized with None.
        """
        return self._was_successful

    @property
    def result_message(self) -> Optional[str]:
        """A message describing the result of the command's execution

        Returns
        -------
        Optional[str]
            Returns a string describing the result of the command's execution and details if it failed.
        """
        return self._result_message


class CompositeCommand(Command):
    """A composite command which contains multiple commands but can act like a single command that executes all contained commands sequentially."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = "CompositeCommand"
        self._receiver_name = "N/A temp"
        self._command_list = []

    @property
    def name(self) -> str:
        """The composite command's name getter.

        Returns
        -------
        str
            Indicates it is a composite command followed by the names and params of each command it contains.
        """
        self._name = "CompositeCommand:"
        for command in self._command_list:
            self._name += " " + command.name + ";"
        return self._name

    @property
    def description(self) -> str:
        """The composite command's description getter.

        Returns
        -------
        str
            Returns the composite command's docstring
        """
        return self.__doc__

    def add_command(self, command: Command, index: int = None):
        """Add a command to the command list.

        Parameters
        ----------
        command : Command
            Any command that subclasses from Command
        index : int, optional
            The index to insert the command, if None then the command is appended, by default None
        """
        if index is None:
            self._command_list.append(command)
        else: 
            self._command_list.insert(index, command)

    def remove_command(self, index: int = None):
        """Remove a command from the command list.

        Parameters
        ----------
        index : int, optional
            The index of the command to remove, if None then removes the last command, by default None
        """
        if index is None:
            index = -1
        del self._command_list[index]

    def execute(self) -> None:
        """Executes each command in the command list sequentially and returns early if a command's execution was not successful."""
        
        for command in self._command_list:
            command.execute()
            if not command.was_successful:
                self._was_successful = command.was_successful
                self._result_message = command.result_message
                return 
            else:
                # update success and message of the composite command
                self._was_successful = command.was_successful
                self._result_message = command.result_message
        # store the success of the last command 
        # or write a new message specific to the composite command
        # self._result_message = "Successfully executed composite command " + type(self).__name__


# for the receiver and concretecommand classes, I figured there were two ways of writing the code. Keep the receiver methods low level and employ logic 
# in the commands, or put all low level methods, logic, and subsequent high level methods in the receiver and have the command simply call the 
# high level methods with minimal logic if at all. I decided the latter mainly because some devices/receivers will have many different commands
# and I want to keep all the command classes streamlined and minimal. I also felt that having the logic and higher level methods separate from the lower level methods
# would make it more difficult to write and maintain due to switching back and forth between the modules.
# If there is a need to separate low level and high level methods, then in my opinion it should take place between the receiver class and another class it extends/inherits 
# from or the actual device firmware.

# nearly all attributes in Command and its child classes are protected because the parameters are not meant to be changed after construction.
# They can be, but for now I would just suggest deleting existing commands that needs to be changed and creating a new one in its place
# The initial reasoning for this is that the name and description may not update when params are changed because they are set during construction
# This can be fixed by implementing the arg dictionary mentioned below and using the name and description getters to update the value by iterating the dict
# This parallels the way CompositeCommands have names that update to reflect its command list when the name getter is used

# consider a command rank system to be able to check that some commands must come before/after others, e.g. initialize?