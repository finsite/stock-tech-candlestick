import logging

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def analyze(
    data: dict[str, any],
    prev_data: dict[str, any] | None = None,
    prev_prev_data: dict[str, any] | None = None,
) -> dict[str, any]:
    """
    Detects candlestick patterns from stock price data and logs the detected patterns.

    Args:
        data (dict): Current period's stock data containing OHLC values and metadata.
        prev_data (dict | None): Previous period's stock data, if available.
        prev_prev_data (dict | None): Stock data from two periods ago, if available.

    Returns:
        dict: Analysis result including symbol, timestamp, detected pattern, and raw data.
    """
    try:
        # Extract Open, High, Low, Close (OHLC) values from the current data
        ohlc_data = data["data"]
        open_price = ohlc_data["open"]
        high_price = ohlc_data["high"]
        low_price = ohlc_data["low"]
        close_price = ohlc_data["close"]
    except KeyError:
        # Log an error and return an error message if data format is invalid
        logger.error("Invalid data format: %s", data)
        return {
            "error": "Invalid data format. Expected 'data' with open, high, low, close."
        }

    # Validate and extract data for previous periods if available
    prev_data = (
        prev_data.get("data")
        if prev_data and isinstance(prev_data, dict) and "data" in prev_data
        else None
    )
    prev_prev_data = (
        prev_prev_data.get("data")
        if prev_prev_data
        and isinstance(prev_prev_data, dict)
        and "data" in prev_prev_data
        else None
    )

    # Detect the candlestick pattern using current and past data
    pattern = detect_candlestick_pattern(
        open_price, high_price, low_price, close_price, prev_data, prev_prev_data
    )

    # Log the detected pattern
    logger.info(
        "Detected pattern: %s | Symbol: %s | Time: %s",
        pattern,
        data["symbol"],
        data["timestamp"],
    )

    # Return the analysis result with pattern and raw data
    return {
        "symbol": data["symbol"],
        "timestamp": data["timestamp"],
        "candlestick_pattern": pattern,
        "raw_data": data,
    }


def detect_candlestick_pattern(
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    prev_data: dict[str, float] | None = None,
    prev_prev_data: dict[str, float] | None = None,
) -> str:
    """
    Determines the type of candlestick pattern based on price movements.
    Logs pattern detection steps.
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

    small_body_threshold = 0.02 * candle_range  # Small body relative to range
    large_body_threshold = 0.6 * candle_range  # Large body relative to range

    # **Single-Candle Patterns**
    # Doji: A candle with a small body and long shadows
    if (
        body_size <= small_body_threshold
        and upper_shadow > body_size
        and lower_shadow > body_size
    ):
        logger.info("Pattern Matched: Doji")
        return "Doji"

    # Hammer: A bullish candle with a small body and long lower shadow
    if (
        body_size > small_body_threshold
        and close_price > open_price
        and lower_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Hammer")
        return "Hammer"

    # Inverted Hammer: A bullish candle with a small body and long upper shadow
    if (
        body_size > small_body_threshold
        and close_price > open_price
        and upper_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Inverted Hammer")
        return "Inverted Hammer"

    # Shooting Star: A bearish candle with a small body and long upper shadow
    if (
        body_size > small_body_threshold
        and close_price < open_price
        and upper_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Shooting Star")
        return "Shooting Star"

    # Marubozu: A candle with no shadows
    if body_size > large_body_threshold and upper_shadow == 0 and lower_shadow == 0:
        logger.info("Pattern Matched: Marubozu")
        return "Marubozu"

    # **Two-Candle Patterns**
    # Bullish Engulfing: A bullish candle that engulfs the previous bearish candle
    if prev_data:
        prev_open = prev_data.get("open", 0)
        prev_close = prev_data.get("close", 0)

        if (
            prev_close < prev_open
            and close_price > open_price
            and close_price > prev_open
            and open_price < prev_close
        ):
            logger.info("Pattern Matched: Bullish Engulfing")
            return "Bullish Engulfing"

        # Bearish Engulfing: A bearish candle that engulfs the previous bullish candle
        if (
            prev_close > prev_open
            and close_price < open_price
            and close_price < prev_open
            and open_price > prev_close
        ):
            logger.info("Pattern Matched: Bearish Engulfing")
            return "Bearish Engulfing"

    # **Three-Candle Patterns**
    # Three Black Crows: Three consecutive bearish candles
    if prev_data and prev_prev_data:
        if detect_three_black_crows(
            prev_prev_data, prev_data, {"open": open_price, "close": close_price}
        ):
            logger.info("Pattern Matched: Three Black Crows")
            return "Three Black Crows"

        # Morning Star: A bullish candle with a small body and long lower shadow
        if (
            prev_prev_data["close"] < prev_prev_data["open"]
            and prev_data["close"] < prev_prev_data["close"]
            and close_price > prev_data["close"]
            and close_price > (prev_prev_data["open"] + prev_prev_data["close"]) / 2
        ):
            logger.info("Pattern Matched: Morning Star")
            return "Morning Star"

        # Evening Star: A bearish candle with a small body and long upper shadow
        if (
            prev_prev_data["close"] > prev_prev_data["open"]
            and prev_data["close"] > prev_prev_data["close"]
            and close_price < prev_data["close"]
            and close_price < (prev_prev_data["open"] + prev_prev_data["close"]) / 2
        ):
            logger.info("Pattern Matched: Evening Star")
            return "Evening Star"

    return "No clear pattern"


def detect_three_black_crows(prev_prev_data, prev_data, current_data) -> bool:
    """
    Detects the Three Black Crows candlestick pattern.

    Pattern Criteria:
    - Three consecutive bearish (red) candles.
    - Each candle closes lower than the previous one.
    - Each candle opens within the previous candle’s body.
    - Each candle has a long real body (small upper/lower shadows).

    Args:
        prev_prev_data (dict): Data for the first candle (two periods ago).
        prev_data (dict): Data for the second candle (one period ago).
        current_data (dict): Data for the current candle.

    Returns:
        bool: True if the pattern is detected, False otherwise.
    """
    # Check if data for all three periods is present
    if not prev_prev_data or not prev_data or not current_data:
        return False

    # Extract open and close prices for each candle
    p1_open, p1_close = prev_prev_data["open"], prev_prev_data["close"]
    p2_open, p2_close = prev_data["open"], prev_data["close"]
    p3_open, p3_close = current_data["open"], current_data["close"]

    # Confirm all three candles are bearish
    if not (p1_close < p1_open and p2_close < p2_open and p3_close < p3_open):
        return False

    # Confirm each candle closes lower than the previous one
    if not (p1_close > p2_close > p3_close):
        return False

    # Confirm each candle opens within the previous body
    if not (p2_open <= p1_close and p3_open <= p2_close):
        return False

    # Calculate and confirm strong bearish trend with large bodies
    p1_body = abs(p1_open - p1_close)
    p2_body = abs(p2_open - p2_close)
    p3_body = abs(p3_open - p3_close)

    if not (
        p1_body > (p1_close - p1_open) * 0.5
        and p2_body > (p2_close - p2_open) * 0.5
        and p3_body > (p3_close - p3_open) * 0.5
    ):
        return False

    return True
