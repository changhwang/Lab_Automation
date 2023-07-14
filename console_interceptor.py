import sys
import logging

class ConsoleInterceptor:
    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.intercepted_messages = []

    def start_interception(self):
        sys.stdout = self.InterceptedStream(self.stdout, self._handle_message)
        sys.stderr = self.InterceptedStream(self.stderr, self._handle_message)
        self._configure_logger()

    def stop_interception(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def get_intercepted_messages(self):
        return self.intercepted_messages

    def _handle_message(self, message):
        # Store the intercepted message for later use
        self.intercepted_messages.append(message)

    def _configure_logger(self):
        logger = logging.getLogger()
        logger.addHandler(self._get_logging_handler())
        logger.addFilter(self._get_logging_filter())

    def _get_logging_handler(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        return handler

    def _get_logging_filter(self):
        return self.InterceptedMessageFilter(self.intercepted_messages)

    class InterceptedStream:
        def __init__(self, stream, handler):
            self.stream = stream
            self.handler = handler

        def write(self, message):
            self.handler(message)
            self.stream.write(message)

        def flush(self):
            self.stream.flush()

    class InterceptedMessageFilter(logging.Filter):
        def __init__(self, intercepted_messages):
            super().__init__()
            self.intercepted_messages = intercepted_messages

        def filter(self, record):
            message = record.getMessage()
            return message not in self.intercepted_messages

