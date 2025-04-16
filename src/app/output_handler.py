import json

from app.logger import logger


def send_to_output(data: dict[str, any]) -> None:
    """Outputs processed candlestick analysis to a chosen output target.

    Args:
    ----
        data (dict[str, any]): The processed candlestick analysis data as a dictionary.

    Returns:
    -------
        None

    """
    try:
        # Convert to JSON for output
        formatted_output: str = json.dumps(data, indent=4)

        # Log the output
        logger.info("Sending data to output: \n%s", formatted_output)

        # Placeholder: Replace with actual write to output target
        print(formatted_output)

    except Exception as e:
        # Log any errors
        logger.error("Failed to send output: %s", e)
