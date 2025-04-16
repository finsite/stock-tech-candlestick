# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Final Runtime ----
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src /app/src

ENV PYTHONPATH="/app"

RUN useradd -m appuser && chown -R appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD pgrep -f "main.py" > /dev/null || exit 1

CMD ["python", "/app/src/app/main.py"]
