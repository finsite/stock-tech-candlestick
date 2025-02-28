import os
import sys

# Add 'src/' to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from app.queue_handler import consume_messages  # ✅ Correct Import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point of the application."""
    logger.info("Starting Candlestick Analysis Service...")
    consume_messages()  # ✅ Starts queue consumer

if __name__ == "__main__":
    main()
