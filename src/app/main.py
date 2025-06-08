"""Main entry point of the application.

Starts the Candlestick Analysis Service and begins consuming messages
from the configured queue.
"""

import os
import sys

# Add 'src/' to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import __version__
from app.utils.setup_logger import setup_logger
from app.queue_handler import consume_messages

logger = setup_logger(__name__)
logger.info("🏁 Starting Candlestick Analysis Service (v%s)", __version__)


def main() -> None:
    """Starts the Candlestick Analysis Service."""
    consume_messages()


if __name__ == "__main__":
    main()
