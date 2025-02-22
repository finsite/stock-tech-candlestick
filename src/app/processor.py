import logging

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def analyze(data, prev_data=None, prev_prev_data=None):
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
        return {"error": "Invalid data format. Expected 'data' with open, high, low, close."}

    pattern = detect_candlestick_pattern(
        open_price, high_price, low_price, close_price, prev_data, prev_prev_data
    )

    logger.info("Detected pattern: %s | Symbol: %s | Time: %s", pattern, data["symbol"], data["timestamp"])
    return {
        "symbol": data["symbol"],
        "timestamp": data["timestamp"],
        "candlestick_pattern": pattern,
        "raw_data": data
    }


def detect_candlestick_pattern(open_price, high_price, low_price, close_price, prev_data=None, prev_prev_data=None):
    """
    Determines the type of candlestick pattern based on price movements.
    Logs pattern detection steps.
    """
    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    candle_range = high_price - low_price

    logger.debug("Processing candle: Open=%.2f, High=%.2f, Low=%.2f, Close=%.2f", open_price, high_price, low_price, close_price)

    small_body_threshold = 0.02 * candle_range  # Small body relative to range
    large_body_threshold = 0.6 * candle_range  # Large body relative to range

    # **Single-Candle Patterns**
    if body_size <= small_body_threshold and upper_shadow > body_size and lower_shadow > body_size:
        return "Doji"

    if body_size > small_body_threshold and close_price > open_price and lower_shadow > body_size * 2:
        return "Hammer"

    if body_size > small_body_threshold and close_price > open_price and upper_shadow > body_size * 2:
        return "Inverted Hammer"

    if body_size > small_body_threshold and close_price < open_price and upper_shadow > body_size * 2:
        return "Shooting Star"

    if body_size > large_body_threshold and upper_shadow == 0 and lower_shadow == 0:
        return "Marubozu"

    # **Two-Candle Patterns**
    if prev_data:
        prev_open = prev_data["open"]
        prev_close = prev_data["close"]

        if prev_close < prev_open and close_price > open_price and close_price > prev_open and open_price < prev_close:
            return "Bullish Engulfing"

        if prev_close > prev_open and close_price < open_price and close_price < prev_open and open_price > prev_close:
            return "Bearish Engulfing"

        if prev_close < prev_open and close_price > open_price and open_price < prev_close and close_price > (prev_open + prev_close) / 2:
            return "Piercing Line"

        if prev_close > prev_open and close_price < open_price and open_price > prev_close and close_price < (prev_open + prev_close) / 2:
            return "Dark Cloud Cover"

        if prev_close < prev_open and close_price > open_price and open_price > prev_close and close_price < prev_open:
            return "Bullish Harami"

        if prev_close > prev_open and close_price < open_price and open_price < prev_close and close_price > prev_open:
            return "Bearish Harami"

    # **Three-Candle Patterns**
    if prev_data and prev_prev_data:
        prev_prev_close = prev_prev_data["close"]
        prev_prev_open = prev_prev_data["open"]
        prev_open = prev_data["open"]
        prev_close = prev_data["close"]

        if prev_prev_close < prev_prev_open and prev_close < prev_prev_close and close_price > prev_close and close_price > (prev_prev_open + prev_prev_close) / 2:
            return "Morning Star"

        if prev_prev_close > prev_prev_open and prev_close > prev_prev_close and close_price < prev_close and close_price < (prev_prev_open + prev_prev_close) / 2:
            return "Evening Star"

        if prev_prev_close < prev_prev_open and prev_close > prev_open and close_price > open_price and close_price > prev_close:
            return "Three White Soldiers"

        if prev_prev_close > prev_prev_open and prev_close < prev_open and close_price < open_price and close_price < prev_close:
            return "Three Black Crows"

    return "No clear pattern"
