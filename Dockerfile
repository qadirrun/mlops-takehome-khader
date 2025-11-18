FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn gunicorn

# Copy application code
COPY app/ ./app/
COPY train/ ./train/

# Copy Alembic configuration
COPY alembic.ini .
COPY alembic/ /app/alembic/

# Create directories with full permissions for training
RUN mkdir -p /app/mlruns /app/artifacts && \
    chmod 777 /app/mlruns /app/artifacts

# Copy and prepare entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create non-root user and set ownership
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/healthz')" || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

