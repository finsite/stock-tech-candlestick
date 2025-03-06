# import logging

# # Setup logger
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


# def analyze(
#     data: dict[str, any],
#     prev_data: dict[str, any] | None = None,
#     prev_prev_data: dict[str, any] | None = None,
# ) -> dict[str, any]:
#     """
#     Detects candlestick patterns from stock price data and logs detected patterns.

#     Args:
#         data (dict[str, any]): The current stock data containing OHLC values.
#         prev_data (dict[str, any] | None, optional): Previous stock data. Defaults to None.
#         prev_prev_data (dict[str, any] | None, optional): Two-periods-ago stock data. Defaults to None.

#     Returns:
#         dict[str, any]: A dictionary containing the detected pattern, original data, and metadata.
#     """
#     try:
#         ohlc_data = data["data"]  # Extract OHLC values
#         open_price = ohlc_data["open"]
#         high_price = ohlc_data["high"]
#         low_price = ohlc_data["low"]
#         close_price = ohlc_data["close"]
#     except KeyError:
#         logger.error("Invalid data format: %s", data)
#         return {
#             "error": "Invalid data format. Expected 'data' with open, high, low, close."
#         }

#     prev_data = prev_data["data"] if prev_data and "data" in prev_data else None
#     prev_prev_data = (
#         prev_prev_data["data"] if prev_prev_data and "data" in prev_prev_data else None
#     )

#     pattern = detect_candlestick_pattern(
#         open_price, high_price, low_price, close_price, prev_data, prev_prev_data
#     )

#     logger.info(
#         "Detected pattern: %s | Symbol: %s | Time: %s",
#         pattern,
#         data["symbol"],
#         data["timestamp"],
#     )
#     return {
#         "symbol": data["symbol"],
#         "timestamp": data["timestamp"],
#         "candlestick_pattern": pattern,
#         "raw_data": data,
#     }


# def detect_candlestick_pattern(
#     open_price: float,
#     high_price: float,
#     low_price: float,
#     close_price: float,
#     prev_data: dict[str, float] | None = None,
#     prev_prev_data: dict[str, float] | None = None,
# ) -> str:
#     """
#     Determines the type of candlestick pattern based on price movements.

#     Args:
#         open_price (float): The opening price.
#         high_price (float): The highest price.
#         low_price (float): The lowest price.
#         close_price (float): The closing price.
#         prev_data (dict[str, float] | None, optional): Previous period data. Defaults to None.
#         prev_prev_data (dict[str, float] | None, optional): Two-periods-ago data. Defaults to None.

#     Returns:
#         str: The detected candlestick pattern name.
#     """
#     body_size = abs(close_price - open_price)
#     upper_shadow = high_price - max(open_price, close_price)
#     lower_shadow = min(open_price, close_price) - low_price
#     candle_range = high_price - low_price

#     logger.debug(
#         "Processing candle: Open=%.2f, High=%.2f, Low=%.2f, Close=%.2f",
#         open_price,
#         high_price,
#         low_price,
#         close_price,
#     )

#     small_body_threshold = 0.02 * candle_range
#     large_body_threshold = 0.6 * candle_range

#     patterns = {
#         "Tweezer Tops": prev_data and prev_data["high"] == high_price,
#         "Tweezer Bottoms": prev_data and prev_data["low"] == low_price,
#         "Piercing Pattern": prev_data
#             and prev_data["close"] < prev_data["open"]  # Previous is bearish
#             and close_price > (prev_data["open"] + prev_data["close"]) / 2  # Closes above midpoint
#             and close_price < prev_data["open"],  # Closes below previous open
#         "Dark Cloud Cover": prev_data
#             and prev_data["close"] > prev_data["open"]  # Previous is bullish
#             and close_price < (prev_data["open"] + prev_data["close"]) / 2  # Closes below midpoint
#             and close_price > prev_data["open"],  # Closes above previous open
#         "Doji": body_size <= small_body_threshold
#             and upper_shadow > body_size
#             and lower_shadow > body_size,
#         "Dragonfly Doji": body_size <= small_body_threshold
#             and lower_shadow > body_size * 2
#             and upper_shadow == 0,
#         "Gravestone Doji": body_size <= small_body_threshold
#             and upper_shadow > body_size * 2
#             and lower_shadow == 0,
#         "Spinning Top": body_size > small_body_threshold
#             and body_size < 0.4 * candle_range,
#         "Hammer": body_size > small_body_threshold
#             and close_price > open_price
#             and lower_shadow > body_size * 2,
#         "Inverted Hammer": body_size > small_body_threshold
#             and close_price > open_price
#             and upper_shadow > body_size * 2,
#         "Shooting Star": body_size > small_body_threshold
#             and close_price < open_price
#             and upper_shadow > body_size * 2,
#         "Marubozu": body_size > large_body_threshold
#             and upper_shadow == 0
#             and lower_shadow == 0,
#     }

#     for pattern, condition in patterns.items():
#         if condition:
#             logger.info("Pattern Matched: %s", pattern)
#             return pattern

#     if prev_data and prev_prev_data:
#         if detect_three_black_crows(
#             prev_prev_data, prev_data, {"open": open_price, "close": close_price}
#         ):
#             logger.info("Pattern Matched: Three Black Crows")
#             return "Three Black Crows"

#     return "No clear pattern"


# def detect_three_black_crows(
#     prev_prev_data: dict[str, float],
#     prev_data: dict[str, float],
#     current_data: dict[str, float],
# ) -> bool:
#     """
#     Detects the Three Black Crows candlestick pattern.

#     Args:
#         prev_prev_data (dict[str, float]): Data from two periods ago.
#         prev_data (dict[str, float]): Data from one period ago.
#         current_data (dict[str, float]): Data from the current period.

#     Returns:
#         bool: True if the pattern is detected, otherwise False.
#     """
#     p1_open, p1_close = prev_prev_data["open"], prev_prev_data["close"]
#     p2_open, p2_close = prev_data["open"], prev_data["close"]
#     p3_open, p3_close = current_data["open"], current_data["close"]

#     return (
#         p1_close < p1_open
#         and p2_close < p2_open
#         and p3_close < p3_open
#         and p1_close > p2_close > p3_close
#         and p2_open <= p1_close
#         and p3_open <= p2_close
#     )
import logging

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def analyze(
    data: dict[str, any],  # The current stock data containing OHLC values.
    prev_data: dict[str, any] | None = None,  # Previous stock data. Defaults to None.
    prev_prev_data: (
        dict[str, any] | None
    ) = None,  # Two-periods-ago stock data. Defaults to None.
) -> dict[
    str, any
]:  # Returns a dictionary containing the detected pattern, original data, and metadata.
    """
    Detects candlestick patterns from stock price data and logs detected patterns.

    Args:
        data (dict[str, any]): The current stock data containing OHLC values.
        prev_data (dict[str, any] | None, optional): Previous stock data. Defaults to None.
        prev_prev_data (dict[str, any] | None, optional): Two-periods-ago stock data. Defaults to None.

    Returns:
        dict[str, any]: A dictionary containing the detected pattern, original data, and metadata.
    """
    try:
        ohlc_data = data["data"]  # Extract OHLC values
        open_price: float = ohlc_data["open"]
        high_price: float = ohlc_data["high"]
        low_price: float = ohlc_data["low"]
        close_price: float = ohlc_data["close"]
    except KeyError:
        logger.error("Invalid data format: %s", data)
        return {
            "error": "Invalid data format. Expected 'data' with open, high, low, close."
        }

    prev_data = prev_data["data"] if prev_data and "data" in prev_data else None
    prev_prev_data = (
        prev_prev_data["data"] if prev_prev_data and "data" in prev_prev_data else None
    )

    pattern: str = detect_candlestick_pattern(
        open_price, high_price, low_price, close_price, prev_data, prev_prev_data
    )

    logger.info(
        "Detected pattern: %s | Symbol: %s | Time: %s",
        pattern,
        data["symbol"],
        data["timestamp"],
    )
    return {
        "symbol": data["symbol"],
        "timestamp": data["timestamp"],
        "candlestick_pattern": pattern,
        "raw_data": data,
    }


def detect_candlestick_pattern(
    open_price: float,  # Opening price of the current period
    high_price: float,  # Highest price of the current period
    low_price: float,  # Lowest price of the current period
    close_price: float,  # Closing price of the current period
    prev_data: dict[str, float] | None = None,  # Previous period data
    prev_prev_data: dict[str, float] | None = None,  # Two-periods-ago data
) -> str:  # Returns the name of the detected candlestick pattern
    """
    Determines the type of candlestick pattern based on price movements.

    Args:
        open_price (float): The opening price of the current period.
        high_price (float): The highest price of the current period.
        low_price (float): The lowest price of the current period.
        close_price (float): The closing price of the current period.
        prev_data (dict[str, float] | None, optional): Previous period data. Defaults to None.
        prev_prev_data (dict[str, float] | None, optional): Two-periods-ago data. Defaults to None.

    Returns:
        str: The name of the detected candlestick pattern.
    """
    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    candle_range = high_price - low_price

    logger.debug(
        "Processing candle: Open=%.2f, High=%.2f, Low=%.2f, Close=%.2f",
        open_price,
        high_price,
        low_price,
        close_price,
    )

    small_body_threshold = 0.02 * candle_range
    large_body_threshold = 0.6 * candle_range

    # **Two-Candle Patterns**
    if prev_data:
        prev_open = prev_data["open"]
        prev_close = prev_data["close"]

        if (
            prev_close < prev_open  # Previous candle is bearish
            and close_price > prev_open  # Current candle opens below previous close
            and close_price > (prev_open + prev_close) / 2  # Closes above midpoint
            and close_price < prev_open  # Closes below previous open
        ):
            logger.info("Pattern Matched: Piercing Pattern")
            return "Piercing Pattern"

        if (
            prev_close > prev_open  # Previous candle is bullish
            and close_price < prev_open  # Current candle opens above previous close
            and close_price < (prev_open + prev_close) / 2  # Closes below midpoint
            and close_price > prev_open  # Closes above previous open
        ):
            logger.info("Pattern Matched: Dark Cloud Cover")
            return "Dark Cloud Cover"

        if prev_data["high"] == high_price and prev_close > open_price:
            logger.info("Pattern Matched: Tweezer Tops")
            return "Tweezer Tops"

        if prev_data["low"] == low_price and prev_close < open_price:
            logger.info("Pattern Matched: Tweezer Bottoms")
            return "Tweezer Bottoms"

    # **Single-Candle Patterns**
    patterns = {
        "Doji": body_size <= small_body_threshold
        and upper_shadow > body_size
        and lower_shadow > body_size,
        "Dragonfly Doji": body_size <= small_body_threshold
        and lower_shadow > body_size * 2
        and upper_shadow == 0,
        "Gravestone Doji": body_size <= small_body_threshold
        and upper_shadow > body_size * 2
        and lower_shadow == 0,
        "Spinning Top": body_size > small_body_threshold
        and body_size < 0.4 * candle_range,
        "Hammer": body_size > small_body_threshold
        and close_price > open_price
        and lower_shadow > body_size * 2,
        "Inverted Hammer": body_size > small_body_threshold
        and close_price > open_price
        and upper_shadow > body_size * 2,
        "Shooting Star": body_size > small_body_threshold
        and close_price < open_price
        and upper_shadow > body_size * 2,
        "Marubozu": body_size > large_body_threshold
        and upper_shadow == 0
        and lower_shadow == 0,
    }

    for pattern, condition in patterns.items():
        if condition:
            logger.info("Pattern Matched: %s", pattern)
            return pattern

    if prev_data and prev_prev_data:
        if detect_three_black_crows(
            prev_prev_data, prev_data, {"open": open_price, "close": close_price}
        ):
            logger.info("Pattern Matched: Three Black Crows")
            return "Three Black Crows"

    return "No clear pattern"


def detect_three_black_crows(
    prev_prev_data: dict[
        str, float
    ],  # Data from two periods ago, with keys "open" and "close"
    prev_data: dict[
        str, float
    ],  # Data from one period ago, with keys "open" and "close"
    current_data: dict[
        str, float
    ],  # Data from the current period, with keys "open" and "close"
) -> bool:  # True if the Three Black Crows pattern is detected, otherwise False
    """
    Detects the Three Black Crows candlestick pattern.

    Args:
        prev_prev_data (dict[str, float]): Data from two periods ago, with keys "open" and "close"
        prev_data (dict[str, float]): Data from one period ago, with keys "open" and "close"
        current_data (dict[str, float]): Data from the current period, with keys "open" and "close"

    Returns:
        bool: True if the Three Black Crows pattern is detected, otherwise False
    """
    p1_open, p1_close = prev_prev_data["open"], prev_prev_data["close"]
    p2_open, p2_close = prev_data["open"], prev_data["close"]
    p3_open, p3_close = current_data["open"], current_data["close"]

    return (
        p1_close < p1_open
        and p2_close < p2_open
        and p3_close < p3_open
        and p1_close > p2_close > p3_close
        and p2_open <= p1_close
        and p3_open <= p2_close
    )
