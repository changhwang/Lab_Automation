from typing import Union
import time

try:
    import slack
    from slack.errors import SlackApiError
    import os
except ImportError:
    _has_slack = False
else:
    _has_slack = True

    
from .command import Command, CommandResult

class UtilityParentCommand(Command):
    """Parent class for utility commands that performs some function for its execute method but does not actually have a receiver."""

    # receiver_cls = None

    def __init__(self, delay: float = 0.0):
        # self._receiver = None
        self._params = {}
        # self._params['receiver_name'] = 'None'
        self._params['delay'] = delay
        # self._was_successful = None
        # self._result_message = None  
        self._result = CommandResult()

class LoopStartCommand(UtilityParentCommand):
    """Marks the start of a loop."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self) -> None:
        self._result = CommandResult(True, "Currently at loop start.")

class LoopEndCommand(UtilityParentCommand):
    """Marks the end of a loop."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self) -> None:
        self._result = CommandResult(True, "Currently at loop end.")

class DelayPauseCommand(UtilityParentCommand):
    """Has a delay or pause but does nothing."""

    def __init__(self, delay: Union[str, float]):
        arg_dict={}
        arg_dict['delay'] = delay
        super().__init__(**arg_dict)

    def execute(self) -> None:
        self._result = CommandResult(True, "Does nothing.")

class NotifySlackCommand(UtilityParentCommand):
    """Send a message to a designated slack channel"""

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self._params['message'] = message.replace(" ", "_") # just for parsing name with spaces
        self._slack_message = message
        self._slack_token = os.environ.get('SLACK_BOT_TOKEN')
        self._slack_client = slack.WebClient(token=self._slack_token)

    def execute(self) -> None:
        try:
            response = self._slack_client.chat_postMessage(
                channel="printer-bot-test",
                text=("from NotifySlackCommand: " + self._slack_message)
                )
            self._result = CommandResult(True, "Successfully sent message.")  
        except SlackApiError as inst:
            self._result = CommandResult(False, "Could not send message: " + inst.response['error'])  

class LogUserMessageCommand(UtilityParentCommand):
    """Store a message in the command's result.message so it can be logged during invocation."""

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self._params['message'] = message.replace(" ", "_") # just for parsing name with spaces
        # self._result_message = message
    
    def execute(self):
        self._result = CommandResult(True, self._params['message'])


