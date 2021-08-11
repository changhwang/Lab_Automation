from .command import Command

class UtilityCommand(Command):
    """A command that performs some utility function for its execute method but does not actually have a receiver."""

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

class DelayCommand(UtilityCommand):
    pass

class PauseCommand(UtilityCommand):
    pass

class NotifySlackCommand(UtilityCommand):
    pass