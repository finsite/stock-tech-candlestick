# TODO: stock-tech-candlestick

## 🧩 Core Functionality

- [x] Add processor for candlestick pattern detection
- [x] Implement single- and multi-candle pattern logic
- [x] Log detected patterns with context
- [x] Return model metadata in output payload

## 🪝 Queue Integration

- [x] Support RabbitMQ and SQS via config.py
- [x] Use Vault + env fallback for queue configuration
- [x] Add retry/backoff logic for RabbitMQ connections
- [x] Add batch size and polling interval config for SQS

## 🧪 Testing

- [ ] Add unit tests for all candlestick pattern functions
- [ ] Add integration test with synthetic queue input
- [ ] Add test case runner for patterns

## 🪛 Config Enhancements

- [x] Use `get_config_value()` wrapper for all config
- [x] Add get_polling_interval() and get_batch_size()
- [x] Add get_output_mode(), get_dlq_name() (if needed)

## 🔊 Logging

- [x] Add environment-driven LOG_LEVEL support
- [x] Support plain and JSON log formatting via LOG_FORMAT
- [x] Use structured service start logging with **version**

## 🛠 Dev Experience

- [x] Add version to `__init__.py`
- [x] Log version in main.py at startup
- [x] Use .pre-commit-config.yaml and shared hooks
- [ ] Review requirements.in for unneeded deps
- [ ] Enforce deptry or pip-check-reqs validation

## 📄 Documentation

- [x] Write README.md with overview, config, and example
- [ ] Add inline docstrings to all major modules
- [ ] Add usage examples and developer guide

## 🔐 Vault Integration

- [x] Use app.utils.vault_client for dynamic secret loading
- [ ] Add support for fallback to default dev secrets

## 📦 Packaging

- [x] Add pyproject.toml with metadata and version
- [ ] Use Commitizen or bump-my-version for releases
