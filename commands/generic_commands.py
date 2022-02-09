from .command import Command, CommandResult

class GenericInitialize(Command):
    """desc"""

    def __init__(self, receiver, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        try:
            self._result = CommandResult(*self._receiver.initialize())
        except AttributeError as err:
            self._result = CommandResult(False, str(err))

class GenericDeinitialize(Command):
    """desc"""

    def __init__(self, receiver, reset_init_flag: bool = True, **kwargs):
        super().__init__(receiver, **kwargs)
        self._params['reset_init_flag'] = reset_init_flag

    def execute(self) -> None:
        try:
            self._result = CommandResult(*self._receiver.deinitialize(self._params['reset_init_flag']))
        except AttributeError as err:
            self._result = CommandResult(False, str(err))

class GenericSerialConnect(Command):
    """desc"""

    def __init__(self, receiver, **kwargs):
        super().__init__(receiver, **kwargs)

    def execute(self) -> None:
        try:
            self._result = CommandResult(*self._receiver.start_serial())
        except AttributeError as err:
            self._result = CommandResult(False, str(err))

    