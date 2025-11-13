"""Prometheus metrics for API monitoring."""
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from functools import wraps

# Create registry
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'iris_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_LATENCY = Histogram(
    'iris_api_request_duration_seconds',
    'API request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
    registry=registry
)

# Prediction metrics
PREDICTIONS_TOTAL = Counter(
    'iris_predictions_total',
    'Total number of predictions made',
    ['model', 'prediction_class'],
    registry=registry
)

PREDICTION_LATENCY = Histogram(
    'iris_prediction_duration_seconds',
    'Prediction latency in seconds',
    ['model'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
    registry=registry
)

# Error metrics
ERRORS_TOTAL = Counter(
    'iris_api_errors_total',
    'Total number of API errors',
    ['error_type', 'endpoint'],
    registry=registry
)

# System metrics
CPU_USAGE = Gauge(
    'iris_cpu_usage_percent',
    'CPU usage percentage',
    registry=registry
)

MEMORY_USAGE = Gauge(
    'iris_memory_usage_bytes',
    'Memory usage in bytes',
    registry=registry
)

MEMORY_PERCENT = Gauge(
    'iris_memory_usage_percent',
    'Memory usage percentage',
    registry=registry
)

# Model metrics
MODEL_LOADED = Gauge(
    'iris_model_loaded',
    'Whether the model is loaded (1=yes, 0=no)',
    ['model_name'],
    registry=registry
)

# Batch prediction metrics
BATCH_SIZE = Histogram(
    'iris_batch_size',
    'Batch prediction size',
    buckets=(1, 5, 10, 25, 50, 100, 250, 500),
    registry=registry
)


def update_system_metrics():
    """Update system resource metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        CPU_USAGE.set(cpu_percent)
        MEMORY_USAGE.set(memory.used)
        MEMORY_PERCENT.set(memory.percent)
    except Exception as e:
        print(f"Error updating system metrics: {e}")


def track_request(method: str, endpoint: str):
    """Decorator to track API request metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = getattr(e, 'status_code', 500)
                ERRORS_TOTAL.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                update_system_metrics()
        
        return wrapper
    return decorator


def track_prediction(model_name: str):
    """Decorator to track prediction metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                PREDICTION_LATENCY.labels(model=model_name).observe(duration)
        
        return wrapper
    return decorator


def record_prediction(model_name: str, prediction_class: int):
    """Record a prediction."""
    PREDICTIONS_TOTAL.labels(
        model=model_name,
        prediction_class=str(prediction_class)
    ).inc()


def record_batch_prediction(model_name: str, batch_size: int):
    """Record batch prediction size."""
    BATCH_SIZE.observe(batch_size)


def set_model_loaded(model_name: str, loaded: bool):
    """Set model loaded status."""
    MODEL_LOADED.labels(model_name=model_name).set(1 if loaded else 0)

