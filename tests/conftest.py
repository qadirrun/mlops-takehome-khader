"""Pytest configuration and fixtures."""
import pytest
import mlflow
from pathlib import Path


def pytest_configure(config):
    """Initialize MLflow before running tests."""
    # Create mlruns directory if it doesn't exist
    mlruns_dir = Path("mlruns")
    mlruns_dir.mkdir(exist_ok=True)
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("sqlite:///mlruns/mlflow.db")
    
    # Create a test experiment
    try:
        mlflow.create_experiment("test-experiment")
    except mlflow.exceptions.MlflowException:
        # Experiment already exists
        pass
    
    # Set the experiment
    mlflow.set_experiment("test-experiment")

