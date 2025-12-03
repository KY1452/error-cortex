import logging
import sys
from .client import LogAnalysisClient

class RabbitMQLogHandler(logging.Handler):
    def __init__(self, client: LogAnalysisClient):
        super().__init__()
        self.client = client

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            try:
                msg = self.format(record)
                exc_info = record.exc_info
                self.client.send_error(msg, exc_info)
            except Exception:
                self.handleError(record)

def install_excepthook(client: LogAnalysisClient):
    original_excepthook = sys.excepthook

    def uncaught_exception_handler(exc_type, exc_value, exc_traceback):
        # Send to RabbitMQ
        client.send_error(str(exc_value), exc_info=(exc_type, exc_value, exc_traceback))
        
        # Call the original handler (usually prints to stderr)
        original_excepthook(exc_type, exc_value, exc_traceback)

    sys.excepthook = uncaught_exception_handler
