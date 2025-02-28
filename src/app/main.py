import logging

from app.processor import process_data  # Adjust import based on actual usage

# Configure logging
logging.basicConfig(level=logging.INFO)


def main():
    """Main entry point of the application."""
    logging.info("Starting Candlestick Analysis Service...")

    # Call the processor (modify this based on how data should be handled)
    process_data()


if __name__ == "__main__":
    main()
