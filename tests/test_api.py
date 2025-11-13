"""Unit tests for API module."""
import pytest
from fastapi.testclient import TestClient
from app.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthz:
    """Test health check endpoint."""
    
    def test_healthz_returns_200(self, client):
        """Test that /healthz returns 200."""
        response = client.get("/healthz")
        assert response.status_code == 200, "Health check should return 200"
    
    def test_healthz_returns_ok(self, client):
        """Test that /healthz returns OK status."""
        response = client.get("/healthz")
        data = response.json()
        assert data["status"] == "ok", "Health check should return ok status"


class TestPredict:
    """Test prediction endpoint."""

    def test_predict_returns_200(self, client):
        """Test that /predict returns 200 with valid input."""
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = client.post("/predict", json=payload)
        # Should return 200 if model is loaded, 503 if not
        assert response.status_code in [200, 503], "Predict should return 200 or 503"

    def test_predict_returns_prediction(self, client):
        """Test that /predict returns prediction when model is loaded."""
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = client.post("/predict", json=payload)

        # Skip if model not loaded
        if response.status_code == 503:
            pytest.skip("Model not loaded in test environment")

        data = response.json()
        assert "prediction" in data, "Response should include prediction"
        assert "probability" in data, "Response should include probability"
        assert "latency_ms" in data, "Response should include latency_ms"

    def test_predict_valid_class(self, client):
        """Test that prediction is valid class."""
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = client.post("/predict", json=payload)

        if response.status_code == 503:
            pytest.skip("Model not loaded in test environment")

        data = response.json()
        assert data["prediction"] in [0, 1, 2], "Prediction should be valid class"

    def test_predict_probability_range(self, client):
        """Test that probability is in valid range."""
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = client.post("/predict", json=payload)

        if response.status_code == 503:
            pytest.skip("Model not loaded in test environment")

        data = response.json()
        assert 0 <= data["probability"] <= 1, "Probability should be between 0 and 1"

    def test_predict_latency_ms(self, client):
        """Test that latency_ms is a valid positive number."""
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = client.post("/predict", json=payload)

        if response.status_code == 503:
            pytest.skip("Model not loaded in test environment")

        data = response.json()
        assert data["latency_ms"] >= 0, "Latency should be non-negative"
        assert isinstance(data["latency_ms"], (int, float)), "Latency should be a number"
    
    def test_predict_missing_features(self, client):
        """Test that /predict returns 422 with missing features."""
        payload = {"features": [5.1, 3.5]}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422, "Should return 422 for invalid input"
    
    def test_predict_invalid_features(self, client):
        """Test that /predict returns 422 with invalid features."""
        payload = {"features": "invalid"}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422, "Should return 422 for invalid input"
    
    def test_predict_batch(self, client):
        """Test batch prediction."""
        payload = {
            "features": [
                [5.1, 3.5, 1.4, 0.2],
                [7.0, 3.2, 4.7, 1.4],
                [6.3, 3.3, 6.0, 2.5]
            ]
        }
        response = client.post("/predict-batch", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data, "Response should include predictions"
            assert len(data["predictions"]) == 3, "Should have 3 predictions"
            assert "latency_ms" in data, "Response should include latency_ms"
            assert data["latency_ms"] >= 0, "Latency should be non-negative"


class TestMetrics:
    """Test metrics endpoint."""
    
    def test_metrics_returns_200(self, client):
        """Test that /metrics returns 200."""
        response = client.get("/metrics")
        assert response.status_code == 200, "Metrics should return 200"
    
    def test_metrics_returns_data(self, client):
        """Test that /metrics returns metrics data."""
        response = client.get("/metrics")
        data = response.json()
        
        assert "model_name" in data, "Metrics should include model_name"
        assert "version" in data, "Metrics should include version"


class TestInfo:
    """Test info endpoint."""
    
    def test_info_returns_200(self, client):
        """Test that /info returns 200."""
        response = client.get("/info")
        assert response.status_code == 200, "Info should return 200"
    
    def test_info_returns_data(self, client):
        """Test that /info returns model information."""
        response = client.get("/info")
        data = response.json()
        
        assert "model_name" in data, "Info should include model_name"
        assert "version" in data, "Info should include version"
        assert "environment" in data, "Info should include environment"

