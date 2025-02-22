import json

from app.logger import logger


def send_to_output(data):
    """
    Outputs processed candlestick analysis.
    """
    try:
        formatted_output = json.dumps(data, indent=4)
        logger.info("Sending data to output: %s", formatted_output)
        print(formatted_output)  # Placeholder: Replace with queue/db write
    except Exception as e:
        logger.error("Failed to send output: %s", e)
