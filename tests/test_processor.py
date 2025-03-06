# import os
# import sys
# import unittest

# # Ensure `src` is in Python's import path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# from app.processor import analyze  # Ensure this matches your actual module


# class TestCandlestickPatterns(unittest.TestCase):

#     def test_valid_doji(self):
#         """Test Doji candlestick pattern detection"""
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 150.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 150.0,
#                 "high": 151.0,
#                 "low": 149.0,
#                 "close": 150.0,
#                 "volume": 1000000,
#             },
#         }
#         result = analyze(data)
#         self.assertEqual(result["candlestick_pattern"], "Doji")

#     def test_valid_hammer(self):
#         """Test Hammer candlestick pattern detection"""
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 148.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 148.0,
#                 "high": 149.0,
#                 "low": 145.0,
#                 "close": 149.0,
#                 "volume": 1000000,
#             },
#         }
#         result = analyze(data)
#         self.assertEqual(result["candlestick_pattern"], "Hammer")

#     def test_valid_shooting_star(self):
#         """Test Shooting Star candlestick pattern detection"""
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 152.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 152.0,
#                 "high": 155.0,
#                 "low": 151.0,
#                 "close": 151.5,
#                 "volume": 1000000,
#             },
#         }
#         result = analyze(data)
#         self.assertEqual(result["candlestick_pattern"], "Shooting Star")

#     def test_valid_bullish_engulfing(self):
#         """Test Bullish Engulfing pattern detection"""
#         prev_data = {
#             "data": {  # ✅ Ensure "data" is present
#                 "open": 151.0,
#                 "high": 152.0,
#                 "low": 150.0,
#                 "close": 150.5,
#             }
#         }
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 153.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 150.0,
#                 "high": 153.0,
#                 "low": 149.5,
#                 "close": 152.5,
#                 "volume": 1000000,
#             },
#         }
#         result = analyze(data, prev_data)
#         self.assertEqual(result["candlestick_pattern"], "Bullish Engulfing")

#     def test_invalid_payload_missing_data(self):
#         """Test handling of missing 'data' field"""
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 150.0,
#             "source": "YFinance",
#         }
#         result = analyze(data)
#         self.assertIn("error", result)

#     def test_invalid_payload_missing_keys(self):
#         """Test handling of missing open/close fields"""
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 150.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 150.0,
#                 "high": 151.0,
#                 # Missing "low" and "close"
#             },
#         }
#         result = analyze(data)
#         self.assertIn("error", result)

#     def test_evening_star(self):
#         """Test Evening Star pattern detection"""
#         prev_prev_data = {
#             "data": {  # ✅ Ensuring "data" key exists
#                 "open": 145,
#                 "high": 148,
#                 "low": 144,
#                 "close": 147,
#             }
#         }
#         prev_data = {
#             "data": {  # ✅ Ensuring "data" key exists
#                 "open": 148,
#                 "high": 150,
#                 "low": 146,
#                 "close": 149,
#             }
#         }
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 140.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 149.0,
#                 "high": 149.5,
#                 "low": 139.0,
#                 "close": 140.0,
#                 "volume": 1200000,
#             },
#         }
#         result = analyze(data, prev_data, prev_prev_data)
#         self.assertEqual(result["candlestick_pattern"], "Evening Star")

#     def test_three_black_crows(self):
#         """Test Three Black Crows pattern detection"""
#         prev_prev_data = {
#             "data": {
#                 "open": 155,
#                 "high": 157,
#                 "low": 152,
#                 "close": 153,  # ✅ Downtrend starts here
#             }
#         }
#         prev_data = {
#             "data": {
#                 "open": 153,
#                 "high": 154,
#                 "low": 149,
#                 "close": 150,  # ✅ Lower close than previous
#             }
#         }
#         data = {
#             "symbol": "AAPL",
#             "timestamp": "2025-02-22T14:30:00Z",
#             "price": 147.0,
#             "source": "YFinance",
#             "data": {
#                 "open": 150.0,  # ✅ Opens within the previous body
#                 "high": 151.0,
#                 "low": 145.0,
#                 "close": 147.0,  # ✅ Closes near the low
#                 "volume": 1200000,
#             },
#         }
#         result = analyze(data, prev_data, prev_prev_data)
#         self.assertEqual(result["candlestick_pattern"], "Three Black Crows")


# if __name__ == "__main__":
#     unittest.main()
import os
import sys
import unittest

# Ensure `src` is in Python's import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.processor import analyze


class TestCandlestickPatterns(unittest.TestCase):

    def test_valid_doji(self):
        """Test Doji candlestick pattern detection"""
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 150.0,
            "source": "YFinance",
            "data": {
                "open": 150.0,
                "high": 151.0,
                "low": 149.0,
                "close": 150.0,
                "volume": 1000000,
            },
        }
        result = analyze(data)
        self.assertEqual(result.get("candlestick_pattern"), "Doji")

    def test_dragonfly_doji(self):
        """Test Dragonfly Doji detection"""
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 150.0,
            "source": "YFinance",
            "data": {
                "open": 150.0,
                "high": 150.0,
                "low": 145.0,
                "close": 150.0,
                "volume": 1000000,
            },
        }
        result = analyze(data)
        self.assertEqual(result.get("candlestick_pattern"), "Dragonfly Doji")

    def test_gravestone_doji(self):
        """Test Gravestone Doji detection"""
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 152.0,
            "source": "YFinance",
            "data": {
                "open": 152.0,
                "high": 155.0,
                "low": 152.0,
                "close": 152.0,
                "volume": 1000000,
            },
        }
        result = analyze(data)
        self.assertEqual(result.get("candlestick_pattern"), "Gravestone Doji")

    def test_spinning_top(self):
        """Test Spinning Top detection"""
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 150.0,
            "source": "YFinance",
            "data": {
                "open": 148.0,
                "high": 152.0,
                "low": 147.0,
                "close": 149.5,
                "volume": 1000000,
            },
        }
        result = analyze(data)
        self.assertEqual(result.get("candlestick_pattern"), "Spinning Top")

    def test_marubozu(self):
        """Test Marubozu detection"""
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 150.0,
            "source": "YFinance",
            "data": {
                "open": 145.0,
                "high": 150.0,
                "low": 145.0,
                "close": 150.0,
                "volume": 1000000,
            },
        }
        result = analyze(data)
        self.assertEqual(result.get("candlestick_pattern"), "Marubozu")

    def test_piercing_pattern(self):
        """Test Piercing Pattern detection"""
        prev_data = {
            "data": {
                "open": 155.0,
                "high": 157.0,
                "low": 152.0,
                "close": 153.0,
            }
        }
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 157.0,
            "source": "YFinance",
            "data": {
                "open": 153.0,
                "high": 157.0,
                "low": 152.5,
                "close": 156.5,
                "volume": 1000000,
            },
        }
        result = analyze(data, prev_data)
        self.assertEqual(result.get("candlestick_pattern"), "Piercing Pattern")

    def test_dark_cloud_cover(self):
        """Test Dark Cloud Cover detection"""
        prev_data = {
            "data": {
                "open": 148.0,
                "high": 150.0,
                "low": 146.0,
                "close": 149.5,
            }
        }
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 145.0,
            "source": "YFinance",
            "data": {
                "open": 150.0,
                "high": 151.0,
                "low": 144.5,
                "close": 146.0,
                "volume": 1000000,
            },
        }
        result = analyze(data, prev_data)
        self.assertEqual(result.get("candlestick_pattern"), "Dark Cloud Cover")

    def test_tweezer_tops(self):
        """Test Tweezer Tops detection"""
        prev_data = {
            "data": {
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 154.0,
            }
        }
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 152.0,
            "source": "YFinance",
            "data": {
                "open": 153.0,
                "high": 155.0,
                "low": 151.0,
                "close": 152.5,
                "volume": 1000000,
            },
        }
        result = analyze(data, prev_data)
        self.assertEqual(result.get("candlestick_pattern"), "Tweezer Tops")

    def test_tweezer_bottoms(self):
        """Test Tweezer Bottoms detection"""
        prev_data = {
            "data": {
                "open": 148.0,
                "high": 149.5,
                "low": 144.0,
                "close": 146.5,
            }
        }
        data = {
            "symbol": "AAPL",
            "timestamp": "2025-02-22T14:30:00Z",
            "price": 147.0,
            "source": "YFinance",
            "data": {
                "open": 147.5,
                "high": 149.5,
                "low": 144.0,
                "close": 146.0,
                "volume": 1000000,
            },
        }
        result = analyze(data, prev_data)
        self.assertEqual(result.get("candlestick_pattern"), "Tweezer Bottoms")


if __name__ == "__main__":
    unittest.main()
