#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the Uvicorn server
echo "Starting Uvicorn server..."
exec uvicorn app.api:app --host 0.0.0.0 --port 8000

