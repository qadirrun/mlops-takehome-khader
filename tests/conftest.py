"""Pytest configuration and fixtures."""
import pytest
import mlflow
import joblib
from pathlib import Path
import tempfile


def pytest_configure(config):
    """Initialize MLflow and load model before running tests."""
    # Set MLflow tracking URI to a temporary directory
    tracking_dir = tempfile.mkdtemp()
    mlflow.set_tracking_uri(f"sqlite:///{tracking_dir}/mlflow.db")

    # Create a test experiment
    try:
        mlflow.create_experiment("test-experiment")
    except mlflow.exceptions.MlflowException:
        # Experiment already exists
        pass

    # Set the experiment
    mlflow.set_experiment("test-experiment")

    # Load the model for tests
    try:
        from app import api
        model_path = Path(__file__).parent.parent / "artifacts" / "model.pkl"
        if model_path.exists():
            api.model = joblib.load(model_path)
            api.MODEL_VERSION = "1.0.0"
            print(f"✓ Test model loaded from {model_path}")
        else:
            print(f"⚠ Model file not found at {model_path}, some tests may be skipped")
    except Exception as e:
        print(f"⚠ Could not load model for tests: {e}")

