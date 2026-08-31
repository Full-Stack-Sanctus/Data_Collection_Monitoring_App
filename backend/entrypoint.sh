#!/bin/sh

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Running data pipeline..."
python run_pipeline.py

echo "Verifying monitoring aggregates..."
python check_monitoring.py

echo "Starting FastAPI..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}"