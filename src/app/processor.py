from typing import Any

from app.logger import setup_logger

logger = setup_logger(__name__)

__all__ = ["analyze"]


def analyze(
    data: dict[str, Any],
    prev_data: dict[str, Any] | None = None,
    prev_prev_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Detects candlestick patterns from stock price data and logs detected patterns.
    
    Args:
    ----
        data (dict[str, Any]): The current stock data containing OHLC values.
        prev_data (Optional[dict[str, Any]]): Previous stock data.
        prev_prev_data (Optional[dict[str, Any]]): Two-periods-ago stock data.
    
    Returns:
    -------
        dict[str, Any]: A dictionary containing the detected pattern, metadata, and raw input.

    :param data: dict[str:
    :param Any: param prev_data: dict[str:
    :param Any: None:  (Default value = None)
    :param prev_prev_data: dict[str:
    :param data: dict[str:
    :param Any: param prev_data: dict[str:
    :param Any: None:  (Default value = None)
    :param prev_prev_data: dict[str:
    :param data: dict[str: 
    :param Any]: 
    :param prev_data: dict[str: 
    :param Any] | None:  (Default value = None)
    :param prev_prev_data: dict[str: 

    """
    try:
        ohlc_data = data["data"]
        open_price = float(ohlc_data["open"])
        high_price = float(ohlc_data["high"])
        low_price = float(ohlc_data["low"])
        close_price = float(ohlc_data["close"])
    except (KeyError, TypeError, ValueError):
        logger.error("Invalid data format: %s", data)
        return {"error": "Invalid data format. Expected 'data' with open, high, low, close."}

    prev_data = prev_data.get("data") if prev_data and "data" in prev_data else None
    prev_prev_data = (
        prev_prev_data.get("data") if prev_prev_data and "data" in prev_prev_data else None
    )

    pattern = detect_candlestick_pattern(
        open_price, high_price, low_price, close_price, prev_data, prev_prev_data
    )

    logger.info(
        "Detected pattern: %s | Symbol: %s | Time: %s",
        pattern,
        data.get("symbol", "unknown"),
        data.get("timestamp", "unknown"),
    )

    return {
        "symbol": data.get("symbol"),
        "timestamp": data.get("timestamp"),
        "pattern": pattern,
        "model": "candlestick",
        "model_version": "v1.0",
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
    """Determines the type of candlestick pattern based on price movements.

    :param open_price: float:
    :param high_price: float:
    :param low_price: float:
    :param close_price: float:
    :param prev_data: dict[str:
    :param float: None:  (Default value = None)
    :param prev_prev_data: dict[str:
    :param open_price: float:
    :param high_price: float:
    :param low_price: float:
    :param close_price: float:
    :param prev_data: dict[str:
    :param float: None:  (Default value = None)
    :param prev_prev_data: dict[str:
    :param open_price: float: 
    :param high_price: float: 
    :param low_price: float: 
    :param close_price: float: 
    :param prev_data: dict[str: 
    :param float] | None:  (Default value = None)
    :param prev_prev_data: dict[str: 

    """
    EPSILON = 1e-5
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

    if prev_data:
        try:
            prev_open = float(prev_data["open"])
            prev_close = float(prev_data["close"])
            prev_high = float(prev_data["high"])
            prev_low = float(prev_data["low"])
        except (KeyError, TypeError, ValueError):
            prev_open = prev_close = prev_high = prev_low = None

        if prev_open and prev_close:
            if prev_close < prev_open and close_price > prev_close and open_price < prev_close:
                logger.info("Pattern Matched: Piercing Pattern")
                return "Piercing Pattern"

            if prev_close > prev_open and close_price < prev_close and open_price > prev_close:
                logger.info("Pattern Matched: Dark Cloud Cover")
                return "Dark Cloud Cover"

            if prev_high == high_price and prev_close > open_price:
                logger.info("Pattern Matched: Tweezer Tops")
                return "Tweezer Tops"

            if prev_low == low_price and prev_close < open_price:
                logger.info("Pattern Matched: Tweezer Bottoms")
                return "Tweezer Bottoms"

    patterns = {
        "Doji": body_size <= small_body_threshold
        and upper_shadow > body_size
        and lower_shadow > body_size,
        "Dragonfly Doji": body_size <= small_body_threshold
        and lower_shadow > body_size * 2
        and abs(upper_shadow) < EPSILON,
        "Gravestone Doji": body_size <= small_body_threshold
        and upper_shadow > body_size * 2
        and abs(lower_shadow) < EPSILON,
        "Spinning Top": small_body_threshold < body_size < 0.4 * candle_range,
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
        and abs(upper_shadow) < EPSILON
        and abs(lower_shadow) < EPSILON,
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
    prev_prev_data: dict[str, float],
    prev_data: dict[str, float],
    current_data: dict[str, float],
) -> bool:
    """Detects the Three Black Crows candlestick pattern.

    :param prev_prev_data: dict[str:
    :param float: param prev_data: dict[str:
    :param current_data: dict[str:
    :param prev_prev_data: dict[str:
    :param float: param prev_data: dict[str:
    :param current_data: dict[str:
    :param prev_prev_data: dict[str: 
    :param float]: 
    :param prev_data: dict[str: 
    :param current_data: dict[str: 

    """
    try:
        p1_open, p1_close = prev_prev_data["open"], prev_prev_data["close"]
        p2_open, p2_close = prev_data["open"], prev_data["close"]
        p3_open, p3_close = current_data["open"], current_data["close"]
    except (KeyError, TypeError, ValueError):
        return False

    return (
        p1_close < p1_open
        and p2_close < p2_open
        and p3_close < p3_open
        and p1_close > p2_close > p3_close
        and p2_open <= p1_close
        and p3_open <= p2_close
    )


if __name__ == "__main__":
    sample = {
        "symbol": "AAPL",
        "timestamp": "2025-04-16T10:00:00",
        "data": {
            "open": 160.0,
            "high": 162.0,
            "low": 159.5,
            "close": 161.0,
            "volume": 100000,
        },
    }
    print(analyze(sample))
