#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations (only for production with PostgreSQL)
ENVIRONMENT=${ENVIRONMENT:-dev}
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "Applying database migrations (PostgreSQL)..."
    alembic upgrade head
else
    echo "Skipping Alembic migrations (using SQLite for $ENVIRONMENT)"
fi

# Check if model exists, if not train it
if [ ! -f "/app/artifacts/model.pkl" ]; then
    echo "⚠️  Model not found at /app/artifacts/model.pkl"
    echo "🔧 Training model on startup..."
    python /app/train/main_loop_models.py
    echo "✅ Model training completed"
else
    echo "✅ Model found at /app/artifacts/model.pkl"
fi

# Start the Uvicorn server
echo "Starting Uvicorn server..."
exec uvicorn app.api:app --host 0.0.0.0 --port 8000

