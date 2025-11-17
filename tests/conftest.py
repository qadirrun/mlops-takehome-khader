"""Pytest configuration and fixtures."""
import pytest
import mlflow
from pathlib import Path
import tempfile


def pytest_configure(config):
    """Initialize MLflow before running tests."""
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

