from typing import Optional, Tuple, Union
from datetime import datetime
import logging
import time
import os

try:
    import slack
    from slack.errors import SlackApiError
except ImportError:
    _has_slack = False
else:
    _has_slack = True

from commands.command import Command


format = '[%(asctime)s] [%(levelname)-5s]: %(message)s'
log_formatter = logging.Formatter(format)
logging.basicConfig(level=logging.INFO, format=format)


class CommandInvoker:
    log_directory = "logs/"

    def __init__(
            self, 
            command_list: Tuple[Command, ...], 
            is_logging_to_file: bool = True, 
            log_filename: Optional[str] = None,
            is_alerting_slack: bool = False) -> None:

        if not _has_slack and is_alerting_slack:
            raise ImportError("slackclient module is required to alert slack.")
            
        self._command_list = command_list
        self._is_logging_to_file = is_logging_to_file
        self._is_alerting_slack = is_alerting_slack
        self._log_filename = log_filename
        self.log = logging.getLogger(__name__)

        if self._is_logging_to_file:
            if self._log_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self._log_filename = timestamp

            if not self._log_filename[-4:] == '.log':
                self._log_filename += '.log'
            
            self._log_filename = self.log_directory + self._log_filename

            self._file_handler = logging.FileHandler(self._log_filename)
            self._file_handler.setFormatter(log_formatter)
            self.log.addHandler(self._file_handler)

        if self._is_alerting_slack:
            self._slack_token = os.environ.get('SLACK_BOT_TOKEN')
            self._slack_client = slack.WebClient(token=self._slack_token)

    def list_command_names(self):
        print('='*10 + "List of Command Names" + "="*10)
        for command in self._command_list:
            print(command.name)
        print('='*10 + "End of Command Names" + "="*10)
    
    def log_command_names(self):
        self.log.info('='*10 + "List of Command Names" + "="*10)
        for command in self._command_list:
            self.log.info(command.name)
        self.log.info('='*10 + "End of Command Names" + "="*10)

    def list_command_descriptions(self):
        print('='*10 + "List of Command Descriptions" + "="*10)
        for command in self._command_list:
            print(command.description)
        print('='*10 + "End of Command Descriptions" + "="*10)

    def log_command_descriptions(self):
        self.log.info('='*10 + "List of Command Descriptions" + "="*10)
        for command in self._command_list:
            self.log.info(command.description)
        self.log.info('='*10 + "End of Command Descriptions" + "="*10)

    def list_command_names_descriptions(self):
        print('='*10 + "List of Command Names/Descriptions" + "="*10)
        for command in self._command_list:
            print("Name: " + command.name)
            print("Description: " + command.description)
        print('='*10 + "End of Command Names/Descriptions" + "="*10)

    def log_command_names_descriptions(self):
        self.log.info('='*10 + "List of Command Names/Descriptions" + "="*10)
        for command in self._command_list:
            self.log.info("Name: " + command.name)
            self.log.info("Description: " + command.description)
        self.log.info('='*10 + "End of Command Names/Descriptions" + "="*10)

    def invoke_commands(self):
        self.log_command_names()
        self.log.info("="*10 + "BEGINNING OF COMMAND SEQUENCE EXECUTION" + "="*10)
        for ndx, command in enumerate(self._command_list):
            delay = command.delay
            if type(delay) is float or type(delay) is int:
                if delay > 0.0:
                    self.log.info("DELAY -> " + str(delay))
                    time.sleep(delay)
            elif delay == "PAUSE" or delay == "P":
                self.log.info("DELAY -> Waiting for user to press enter")
                print('')
                print("Press ENTER to continue, type 'quit' to terminate execution immediately:")
                userinput = input()
                if userinput == "quit":
                    self.log.info("User terminated execution early by entering 'quit' at pause step")
                    break
                else:
                    self.log.info("DELAY -> User continued command execution")

            self.log.info("COMMAND -> " + command.name)
            command.execute()
            if command.was_successful:
                self.log.info("RESULT  -> " + str(command.was_successful) + ", " + command.result_message)
            else:
                self.log.error("RESULT  -> " + str(command.was_successful) + ", " + command.result_message)
                self.log.error("Received False result. Terminating command execution early!")
                if self._is_alerting_slack:
                    self.log.info("Sending command details to slack.")
                    self.alert_slack(command)
                break
        self.log.info("="*10 + "END OF COMMAND SEQUENCE EXECUTION" + "="*16)
        self.log.info("")
        if self._is_logging_to_file:
            print("")
            print("Log messages saved to: " + str(self._log_filename))
            print("")
        else:
            print("")
            print("Log messages were not saved")
            print("")

    def alert_slack(self, command: Command):
        try:
            response = self._slack_client.chat_postMessage(
                channel="printer-bot-test",
                text=("Error in the following command execution:\n" 
                    "COMMAND -> " + command.name + "\n" 
                    "RESULT  -> " + str(command.was_successful) + ", " + command.result_message + "\n" 
                    "See log file \"" + str(self._log_filename) + "\" for more details.")
                    )  
        except SlackApiError as inst:
            # You will get a SlackApiError if "ok" is False
            self.log.error("Could not send message to slack: " + inst.response['error'])
            # assert inst.response["error"]  # str like 'invalid_auth', 'channel_not_found'


# experiment name, id
#is logging, log file, delay between commands, or delay list
# delay list can have a value like -1 or a str to indicate that 
# we wait for user input before proceeding or type quit to terminate early 
# this could also be implemented as a Command that waits for input and returns
#  consider also ctrl c exception termination, safely terminate and log
#invoker observer/inspecter for more complex bookkeeping?

# for params such as experiment name, id, logfile, should these be passed to the invoker constructor OR to the invoke_command method

# for parallel processes with threading consider branches and loop done with the follow command nodes: jump, conditional jump, label, end (ala assembly, exapunks)
# example of conditional jump, prompt user for y/n to jump to a previous label to loop, or jump to a future label to skip some commands
# on loops we can either do the same thing or change the arguments to command (e.g. to explore how printing speed changes each loop). 
# This can be done with a preset that is passed (e.g. a list of parameters corresponding to each loop)
# or this can be done live, e.g. based on equation/condition or based on user input or based on input from a machine learning optimizer
# how to check against infinite loop
# how to check that an execution in a branch doesnt interfere with another branch? the root cannot proceed until its next branch no longer uses receivers that the root will need, and so forth
#  and the root can go as far as it can as long as it uses receivers not used by the next branch?
# how to control threading?, an invoked can call a new thread when it hits a new branch node (or the node is a command itself to start a new thread)
# or an invoker manager or the client sees a new branch node and creates a new invoker and passes it the branch list
# but what if a branch within a branch? need some sort of composite/recursive approach

# how to deal with commands with arguments that change every loop? 
# Should we have command objects that persist throughout loops? if so, should they keep track of their own execution count? (this probably makes writing command classes more complicated)
# should we generate new commands instead, cloning the loop section on each iteration with new commands?
# whose job is it to change the command or generate new commands, the client or invoker
# and how do we deal with commands with arguments that come from user input on each loop?
# how can we make the user input argument and preset list argument methods as similar as possible?
# are commands changable after instantiation or should we just destroy and remake them? 
# if changable then we need update functions/getters to update name/description when arguments change which makes them more complicated
# if we should destroy and remake, we might as well make them when we are ready (after taking user input). 
# But this means the client doesnt have a singular invoker_command method call, and we should always push new commands to the stack/queue and have invoker invoke them
# this means the invoker needs to wait when reaching the end of its current command list, meaning the client needs a definite way to terminate invoking on the invoker
