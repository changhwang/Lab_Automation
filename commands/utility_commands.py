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

    
from .command import Command

class UtilityCommand(Command):
    """Parent class for utility commands that performs some function for its execute method but does not actually have a receiver."""

    receiver_cls = None

    def __init__(self, delay: float = 0.0):
        # self._receiver = None
        self._params = {}
        # self._params['receiver_name'] = 'None'
        self._params['delay'] = delay
        self._was_successful = None
        self._result_message = None  

class LoopStartCommand(UtilityCommand):
    """Marks the start of a loop."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = (True, "Currently at loop start.")

class LoopEndCommand(UtilityCommand):
    """Marks the end of a loop."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self) -> None:
        self._was_successful, self._result_message = (True, "Currently at loop end.")

class DelayPauseCommand(UtilityCommand):
    """Has a delay or pause but does nothing."""

    def __init__(self, delay: Union[str, float]):
        super().__init__(delay)

    def execute(self) -> None:
        self._was_successful, self._result_message = (True, "Does nothing.")

class NotifySlackCommand(UtilityCommand):
    """Send a message to a designated slack channel"""

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self._params['message'] = message
        self._slack_token = os.environ.get('SLACK_BOT_TOKEN')
        self._slack_client = slack.WebClient(token=self._slack_token)

    def execute(self) -> None:
        try:
            response = self._slack_client.chat_postMessage(
                channel="printer-bot-test",
                text=("from NotifySlackCommand: " + self._params['message'])
                )
            self._was_successful, self._result_message = (True, "Successfully sent message.")  
        except SlackApiError as inst:
            self._was_successful, self._result_message = (False, "Could not send message: " + inst.response['error'])  


