import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sdk.client import LogAnalysisClient
from sdk.handlers import RabbitMQLogHandler

class TestLogAnalysisSDK(unittest.TestCase):
    @patch("sdk.client.pika")
    def test_client_connection_and_send(self, mock_pika):
        # Setup mock
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        # Init client
        client = LogAnalysisClient("test-service")
        
        # Verify connection
        mock_pika.BlockingConnection.assert_called_once()
        mock_channel.queue_declare.assert_called_with(queue="log_errors", durable=False)
        
        # Send error
        client.send_error("Test error")
        
        # Verify publish
        mock_channel.basic_publish.assert_called_once()
        args, kwargs = mock_channel.basic_publish.call_args
        self.assertEqual(kwargs["routing_key"], "log_errors")
        self.assertIn("Test error", kwargs["body"])
        self.assertIn("test-service", kwargs["body"])

    @patch("sdk.client.pika")
    def test_handler_emit(self, mock_pika):
        # Setup mock
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        client = LogAnalysisClient("test-service")
        handler = RabbitMQLogHandler(client)
        
        # Create a log record
        import logging
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname=__file__, lineno=10,
            msg="Handler error", args=(), exc_info=None
        )
        
        handler.emit(record)
        
        # Verify publish
        mock_channel.basic_publish.assert_called_once()
        args, kwargs = mock_channel.basic_publish.call_args
        self.assertIn("Handler error", kwargs["body"])

if __name__ == "__main__":
    unittest.main()
