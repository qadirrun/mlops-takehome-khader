"""FastAPI application for Iris classifier."""
import os
import time
import uuid
import joblib
from datetime import datetime
from typing import List
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import numpy as np
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.metrics import (
    track_request, track_prediction, record_prediction,
    record_batch_prediction, set_model_loaded, registry
)
from app.database import log_prediction

app = FastAPI(
    title="Iris Classifier API",
    description="ML model serving API for Iris classification using MLflow and scikit-learn",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
MODEL_NAME = os.getenv("MODEL_NAME", "iris-logistic-regression")
CANARY_PERCENTAGE = int(os.getenv("CANARY_PERCENTAGE", "100"))

# Global model variable
model = None
MODEL_VERSION = "0.0.0"

@app.on_event("startup")
async def startup_event():
    """Initialize DB and load model from .pkl file on startup."""
    global model, MODEL_VERSION

    # Database is now initialized by Alembic in the entrypoint.sh script

    # Load Model from .pkl file
    try:
        model_path = Path(__file__).parent.parent / "artifacts" / "model.pkl"
        print(f"Loading model from: {model_path}")
        model = joblib.load(model_path)
        MODEL_VERSION = "1.0.0"  # Static version, since we're not using registry
        set_model_loaded(MODEL_NAME, True)
        print(f"✓ Model loaded successfully from .pkl file")
    except Exception as e:
        print(f"❌ CRITICAL: Could not load model from .pkl file: {e}")
        model = None
        MODEL_VERSION = "0.0.0"
        set_model_loaded(MODEL_NAME, False)


class PredictRequest(BaseModel):
    """Prediction request model.

    Features should be in the order:
    1. Sepal length (cm)
    2. Sepal width (cm)
    3. Petal length (cm)
    4. Petal width (cm)
    """
    features: List[float] = Field(
        ...,
        min_items=4,
        max_items=4,
        example=[5.1, 3.5, 1.4, 0.2],
        description="List of 4 iris features (sepal length, sepal width, petal length, petal width)"
    )

    class Config:
        schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }


class PredictBatchRequest(BaseModel):
    """Batch prediction request model."""
    features: List[List[float]] = Field(
        ...,
        example=[[5.1, 3.5, 1.4, 0.2], [7.0, 3.2, 4.7, 1.4]],
        description="List of iris feature vectors (each with 4 features)"
    )

    class Config:
        schema_extra = {
            "example": {
                "features": [
                    [5.1, 3.5, 1.4, 0.2],
                    [7.0, 3.2, 4.7, 1.4]
                ]
            }
        }


class PredictResponse(BaseModel):
    """Prediction response model."""
    prediction: int = Field(
        ...,
        description="Predicted iris class (0=setosa, 1=versicolor, 2=virginica)"
    )
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence probability of the prediction"
    )
    latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Inference latency in milliseconds"
    )
    model: str = Field(
        ...,
        description="Name of the model used for prediction"
    )
    version: str = Field(
        ...,
        description="Version of the model"
    )

    class Config:
        schema_extra = {
            "example": {
                "prediction": 0,
                "probability": 0.99,
                "latency_ms": 12.5,
                "model": "iris-logistic-regression",
                "version": "1.0.0"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(
        ...,
        description="Health status (ok or error)"
    )
    environment: str = Field(
        ...,
        description="Deployment environment (dev, staging, prod)"
    )
    model: str = Field(
        ...,
        description="Name of the loaded model"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "environment": "prod",
                "model": "iris-logistic-regression"
            }
        }


class InfoResponse(BaseModel):
    """Info response model."""
    model_name: str = Field(
        ...,
        description="Name of the model"
    )
    version: str = Field(
        ...,
        description="Version of the model"
    )
    environment: str = Field(
        ...,
        description="Deployment environment"
    )
    canary_percentage: int = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of traffic for canary deployment"
    )

    class Config:
        schema_extra = {
            "example": {
                "model_name": "iris-logistic-regression",
                "version": "1.0.0",
                "environment": "prod",
                "canary_percentage": 100
            }
        }


@app.get(
    "/metrics-prometheus",
    tags=["Monitoring"],
    summary="Prometheus Metrics",
    description="Get Prometheus metrics for monitoring and alerting"
)
async def metrics_prometheus():
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    return Response(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get(
    "/healthz",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check if the API and model are healthy"
)
@track_request("GET", "/healthz")
async def healthz():
    """Health check endpoint.

    Returns the health status of the API and model.
    Used by Kubernetes liveness and readiness probes.
    Will return a 503 error if the model is not loaded yet.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    return {
        "status": "ok",
        "environment": ENVIRONMENT,
        "model": MODEL_NAME
    }


@app.post(
    "/predict",
    response_model=PredictResponse,
    tags=["Predictions"],
    summary="Single Prediction",
    description="Make a single prediction for iris classification",
    responses={
        200: {"description": "Successful prediction"},
        422: {"description": "Invalid features (must have 4 dimensions)"},
        503: {"description": "Model not loaded"}
    }
)
@track_request("POST", "/predict")
async def predict(request: PredictRequest):
    """Make a single prediction.

    Takes iris features and returns the predicted class and confidence.

    Args:
        request: PredictRequest with 4 iris features

    Returns:
        PredictResponse with prediction, probability, latency_ms, model name and version
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(request.features) != 4:
        raise HTTPException(status_code=422, detail="Features must have 4 dimensions")

    try:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Measure inference latency
        start_time = time.time()

        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        probability = float(np.max(probabilities))

        # Calculate latency in milliseconds
        latency_ms = (time.time() - start_time) * 1000

        # Record metrics
        record_prediction(MODEL_NAME, int(prediction))

        # Log to database
        log_prediction(
            request_id=request_id,
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
            features=request.features,
            prediction=int(prediction),
            probability=probability,
            latency_ms=latency_ms,
            timestamp=datetime.now()
        )

        return {
            "prediction": int(prediction),
            "probability": probability,
            "latency_ms": latency_ms,
            "model": MODEL_NAME,
            "version": MODEL_VERSION,
            "request_id": request_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/predict-batch",
    tags=["Predictions"],
    summary="Batch Predictions",
    description="Make multiple predictions for iris classification",
    responses={
        200: {"description": "Successful batch predictions"},
        422: {"description": "Invalid features (each must have 4 dimensions)"},
        503: {"description": "Model not loaded"}
    }
)
@track_request("POST", "/predict-batch")
async def predict_batch(request: PredictBatchRequest):
    """Make batch predictions.

    Takes multiple iris feature vectors and returns predictions for all.

    Args:
        request: PredictBatchRequest with list of feature vectors

    Returns:
        Dictionary with predictions, probabilities, latency_ms, model name and version
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Measure inference latency
        start_time = time.time()

        features = np.array(request.features)
        if features.shape[1] != 4:
            raise HTTPException(status_code=422, detail="Features must have 4 dimensions")

        predictions = model.predict(features)
        probabilities = model.predict_proba(features)
        max_probs = np.max(probabilities, axis=1)

        # Calculate latency in milliseconds
        latency_ms = (time.time() - start_time) * 1000

        # Record metrics
        record_batch_prediction(MODEL_NAME, len(predictions))
        for pred in predictions:
            record_prediction(MODEL_NAME, int(pred))

        return {
            "predictions": [int(p) for p in predictions],
            "probabilities": [float(p) for p in max_probs],
            "latency_ms": latency_ms,
            "model": MODEL_NAME,
            "version": MODEL_VERSION
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Model Metrics",
    description="Get model metrics and configuration"
)
@track_request("GET", "/metrics")
async def metrics():
    """Get model metrics.

    Returns information about the loaded model and current configuration.
    """
    return {
        "model_name": MODEL_NAME,
        "version": MODEL_VERSION,
        "environment": ENVIRONMENT,
        "canary_percentage": CANARY_PERCENTAGE
    }


@app.get(
    "/logs",
    tags=["Monitoring"],
    summary="Prediction Logs",
    description="Get recent prediction logs from database"
)
@track_request("GET", "/logs")
async def get_logs(limit: int = 100):
    """Get recent prediction logs.

    Returns recent predictions logged to the database with request_id,
    model_version, latency_ms, and timestamp.
    """
    from app.database import get_predictions
    logs = get_predictions(limit=limit)
    return {
        "count": len(logs),
        "logs": logs
    }


@app.get(
    "/info",
    response_model=InfoResponse,
    tags=["Information"],
    summary="API Information",
    description="Get API and model information"
)
@track_request("GET", "/info")
async def info():
    """Get API information.

    Returns information about the API, model, and deployment configuration.
    """
    return {
        "model_name": MODEL_NAME,
        "version": MODEL_VERSION,
        "environment": ENVIRONMENT,
        "canary_percentage": CANARY_PERCENTAGE
    }


@app.get(
    "/",
    tags=["Information"],
    summary="Root Endpoint",
    description="Get API information and documentation links"
)
@track_request("GET", "/")
async def root():
    """Root endpoint.

    Returns links to API documentation and health check.
    """
    return {
        "message": "Iris Classifier API",
        "docs": "/docs",
        "health": "/healthz"
    }

