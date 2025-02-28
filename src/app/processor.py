import logging
from typing import Optional, Dict

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def analyze(data: Dict[str, any], prev_data: Optional[Dict[str, any]] = None, prev_prev_data: Optional[Dict[str, any]] = None) -> Dict[str, any]:
    """
    Detects candlestick patterns from stock price data.
    Logs detected patterns.

    Expected input format:
    {
        "symbol": str,
        "timestamp": str,
        "price": float,
        "source": str,
        "data": {
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": int
        }
    }
    """
    try:
        ohlc_data = data["data"]  # Extract OHLC values
        open_price = ohlc_data["open"]
        high_price = ohlc_data["high"]
        low_price = ohlc_data["low"]
        close_price = ohlc_data["close"]
    except KeyError:
        logger.error("Invalid data format: %s", data)
        return {
            "error": "Invalid data format. Expected 'data' with open, high, low, close."
        }

    # Ensure prev_data and prev_prev_data are valid
    prev_data = prev_data["data"] if prev_data else None
    prev_prev_data = prev_prev_data["data"] if prev_prev_data else None

    pattern = detect_candlestick_pattern(
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
    open_price: float, high_price: float, low_price: float, close_price: float,
    prev_data: Optional[Dict[str, float]] = None,
    prev_prev_data: Optional[Dict[str, float]] = None
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
    if (
        body_size <= small_body_threshold
        and upper_shadow > body_size
        and lower_shadow > body_size
    ):
        logger.info("Pattern Matched: Doji")
        return "Doji"

    if (
        body_size > small_body_threshold
        and close_price > open_price
        and lower_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Hammer")
        return "Hammer"

    if (
        body_size > small_body_threshold
        and close_price > open_price
        and upper_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Inverted Hammer")
        return "Inverted Hammer"

    if (
        body_size > small_body_threshold
        and close_price < open_price
        and upper_shadow > body_size * 2
    ):
        logger.info("Pattern Matched: Shooting Star")
        return "Shooting Star"

    if body_size > large_body_threshold and upper_shadow == 0 and lower_shadow == 0:
        logger.info("Pattern Matched: Marubozu")
        return "Marubozu"

    # **Two-Candle Patterns**
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

        if (
            prev_close > prev_open
            and close_price < open_price
            and close_price < prev_open
            and open_price > prev_close
        ):
            logger.info("Pattern Matched: Bearish Engulfing")
            return "Bearish Engulfing"

    # **Three-Candle Patterns**
    if prev_data and prev_prev_data:
        prev_prev_open = prev_prev_data.get("open", 0)
        prev_prev_close = prev_prev_data.get("close", 0)
        prev_open = prev_data.get("open", 0)
        prev_close = prev_data.get("close", 0)

        if (
            prev_prev_close < prev_prev_open
            and prev_close < prev_prev_close
            and close_price > prev_close
            and close_price > (prev_prev_open + prev_prev_close) / 2
        ):
            logger.info("Pattern Matched: Morning Star")
            return "Morning Star"

        if (
            prev_prev_close > prev_prev_open
            and prev_close > prev_prev_close
            and close_price < prev_close
            and close_price < (prev_prev_open + prev_prev_close) / 2
        ):
            logger.info("Pattern Matched: Evening Star")
            return "Evening Star"

    return "No clear pattern"
