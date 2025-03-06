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
#     Detects candlestick patterns from stock price data.
#     Logs detected patterns.

#     Expected input format:
#     {
#         "symbol": str,
#         "timestamp": str,
#         "price": float,
#         "source": str,
#         "data": {
#             "open": float,
#             "high": float,
#             "low": float,
#             "close": float,
#             "volume": int
#         }
#     }
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

#     # Ensure prev_data and prev_prev_data are valid
#     prev_data = prev_data.get("data") if prev_data and isinstance(prev_data, dict) and "data" in prev_data else None
#     prev_prev_data = prev_prev_data.get("data") if prev_prev_data and isinstance(prev_prev_data, dict) and "data" in prev_prev_data else None

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
#     Logs pattern detection steps.
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

#     small_body_threshold = 0.02 * candle_range  # Small body relative to range
#     large_body_threshold = 0.6 * candle_range  # Large body relative to range

#     # **Single-Candle Patterns**
#     if (
#         body_size <= small_body_threshold
#         and upper_shadow > body_size
#         and lower_shadow > body_size
#     ):
#         logger.info("Pattern Matched: Doji")
#         return "Doji"

#     if (
#         body_size > small_body_threshold
#         and close_price > open_price
#         and lower_shadow > body_size * 2
#     ):
#         logger.info("Pattern Matched: Hammer")
#         return "Hammer"

#     if (
#         body_size > small_body_threshold
#         and close_price > open_price
#         and upper_shadow > body_size * 2
#     ):
#         logger.info("Pattern Matched: Inverted Hammer")
#         return "Inverted Hammer"

#     if (
#         body_size > small_body_threshold
#         and close_price < open_price
#         and upper_shadow > body_size * 2
#     ):
#         logger.info("Pattern Matched: Shooting Star")
#         return "Shooting Star"

#     if body_size > large_body_threshold and upper_shadow == 0 and lower_shadow == 0:
#         logger.info("Pattern Matched: Marubozu")
#         return "Marubozu"

#     # **Two-Candle Patterns**
#     if prev_data:
#         prev_open = prev_data.get("open", 0)
#         prev_close = prev_data.get("close", 0)

#         if (
#             prev_close < prev_open
#             and close_price > open_price
#             and close_price > prev_open
#             and open_price < prev_close
#         ):
#             logger.info("Pattern Matched: Bullish Engulfing")
#             return "Bullish Engulfing"

#         if (
#             prev_close > prev_open
#             and close_price < open_price
#             and close_price < prev_open
#             and open_price > prev_close
#         ):
#             logger.info("Pattern Matched: Bearish Engulfing")
#             return "Bearish Engulfing"

#     # **Three-Candle Patterns**
#     if prev_data and prev_prev_data:
#         prev_prev_open = prev_prev_data.get("open", 0)
#         prev_prev_close = prev_prev_data.get("close", 0)
#         prev_open = prev_data.get("open", 0)
#         prev_close = prev_data.get("close", 0)

#         # 🔥 Three Black Crows Detection
#         if (
#             prev_prev_close > prev_prev_open  # First candle is bearish
#             and prev_close > prev_open  # Second candle is bearish
#             and close_price > open_price  # Third candle is bearish
#             and prev_prev_close > prev_close > close_price  # Three consecutive lower closes
#             and prev_prev_open > prev_open > open_price  # Three consecutive lower opens
#         ):
#             logger.info("Pattern Matched: Three Black Crows")
#             return "Three Black Crows"

#         # 🔥 Morning Star
#         if (
#             prev_prev_close < prev_prev_open
#             and prev_close < prev_prev_close
#             and close_price > prev_close
#             and close_price > (prev_prev_open + prev_prev_close) / 2
#         ):
#             logger.info("Pattern Matched: Morning Star")
#             return "Morning Star"

#         # 🔥 Evening Star
#         if (
#             prev_prev_close > prev_prev_open
#             and prev_close > prev_prev_close
#             and close_price < prev_close
#             and close_price < (prev_prev_open + prev_prev_close) / 2
#         ):
#             logger.info("Pattern Matched: Evening Star")
#             return "Evening Star"

#     return "No clear pattern"
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
        if detect_three_black_crows(
            prev_prev_data, prev_data, {"open": open_price, "close": close_price}
        ):
            logger.info("Pattern Matched: Three Black Crows")
            return "Three Black Crows"

        if (
            prev_prev_data["close"] < prev_prev_data["open"]
            and prev_data["close"] < prev_prev_data["close"]
            and close_price > prev_data["close"]
            and close_price > (prev_prev_data["open"] + prev_prev_data["close"]) / 2
        ):
            logger.info("Pattern Matched: Morning Star")
            return "Morning Star"

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

    Criteria:
    - Three consecutive bearish (red) candles.
    - Each candle closes lower than the previous one.
    - Each candle opens within the previous candle’s body.
    - Each candle has a long real body (small upper/lower shadows).
    """
    if not prev_prev_data or not prev_data or not current_data:
        return False

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

    # Ensure strong bearish trend (bodies are large compared to wicks)
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
