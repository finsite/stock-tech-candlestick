# Stock Tech Candlestick

## Overview

`stock-tech-candlestick` is a technical analysis microservice that detects
candlestick patterns from incoming stock OHLC (open, high, low, close) data. It
is part of a modular system for stock market analysis built around asynchronous
message queues.

The service supports both RabbitMQ and AWS SQS as queue backends and integrates
with Vault for secure configuration management.

---

## Features

- Detects common candlestick patterns (e.g., Doji, Hammer, Marubozu, Three Black
  Crows)
- Supports both single-candle and multi-candle analysis
- Input via RabbitMQ or AWS SQS
- Outputs results to queue or log
- Configurable using Vault and environment variables
- Fully containerizable with minimal external dependencies

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-org/stock-tech-candlestick.git
   cd stock-tech-candlestick
   ```

2. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Configuration is handled via a combination of Vault secrets and environment
variables. See `config.py` for the full list of supported keys.

Minimum required configuration:

```env
QUEUE_TYPE=rabbitmq
RABBITMQ_HOST=localhost
RABBITMQ_VHOST=/
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_EXCHANGE=stock_analysis
RABBITMQ_ROUTING_KEY=candlestick
RABBITMQ_QUEUE=analysis_queue
```

---

## Running the Service

```bash
python -m app.main
```

---

## Example Input

```json
{
  "symbol": "AAPL",
  "timestamp": "2025-04-16T10:00:00",
  "data": {
    "open": 160.0,
    "high": 162.0,
    "low": 159.5,
    "close": 161.0,
    "volume": 100000
  }
}
```

---

## License

Apache 2.0 License
