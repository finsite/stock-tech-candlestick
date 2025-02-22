import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure `src` is in Python's import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.main import main


class TestMain(unittest.TestCase):

    @patch("app.queue_handler.consume_messages")
    def test_main_starts_correctly(self, mock_consume_messages):
        """Test if the main function starts message consumption"""
        mock_consume_messages.return_value = None  # Simulate normal execution
        main()
        mock_consume_messages.assert_called_once()

    @patch("app.queue_handler.consume_messages")
    def test_rabbitmq_message_consumption(self, mock_consume_messages):
        """Test if RabbitMQ consumer runs without errors"""
        mock_consume_messages.return_value = (
            None  # Simulate successful message processing
        )
        result = main()
        self.assertIsNone(result)

    @patch("app.queue_handler.pika.BlockingConnection")
    def test_rabbitmq_connection_failure(self, mock_pika_connection):
        """Test handling of RabbitMQ connection failure"""
        mock_pika_connection.side_effect = Exception(
            "RabbitMQ error"
        )  # Simulate failure

        with self.assertRaises(Exception) as context:
            main()

        self.assertIn("RabbitMQ error", str(context.exception))

    @patch("app.queue_handler.consume_messages")
    @patch("app.processor.analyze")
    def test_message_processing_calls_analyze(
        self, mock_analyze, mock_consume_messages
    ):
        """Test if received messages are processed by analyze()"""
        mock_message = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 150.0,
            "source": "YFinance",
            "data": {
                "open": 150.0,
                "high": 151.0,
                "low": 149.0,
                "close": 150.0,
                "volume": 1000000,
            },
        }
        mock_consume_messages.return_value = mock_message
        mock_analyze.return_value = {"candlestick_pattern": "Doji"}

        main()
        mock_analyze.assert_called_once_with(mock_message)


if __name__ == "__main__":
    unittest.main()
