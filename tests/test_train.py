"""Unit tests for training module."""
import pytest
from train.data_fetch import fetch_data
from train.multi_model_train import (
    train_logistic_regression,
    train_random_forest,
    train_svm,
    evaluate_model
)


class TestDataFetch:
    """Test data fetching functionality."""
    
    def test_fetch_data_returns_correct_shapes(self):
        """Test that fetch_data returns correct shapes."""
        X_train, X_test, y_train, y_test = fetch_data()
        
        assert X_train.shape[0] == 120, "Train set should have 120 samples"
        assert X_test.shape[0] == 30, "Test set should have 30 samples"
        assert X_train.shape[1] == 4, "Features should have 4 dimensions"
        assert X_test.shape[1] == 4, "Features should have 4 dimensions"
    
    def test_fetch_data_returns_correct_labels(self):
        """Test that labels are in correct range."""
        X_train, X_test, y_train, y_test = fetch_data()
        
        assert set(y_train).issubset({0, 1, 2}), "Labels should be 0, 1, or 2"
        assert set(y_test).issubset({0, 1, 2}), "Labels should be 0, 1, or 2"


class TestLogisticRegression:
    """Test Logistic Regression model."""
    
    def test_logistic_regression_trains(self):
        """Test that Logistic Regression model trains successfully."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }
        
        model = train_logistic_regression(X_train, y_train, params)
        assert model is not None, "Model should be trained"
        assert hasattr(model, 'predict'), "Model should have predict method"
    
    def test_logistic_regression_predicts(self):
        """Test that Logistic Regression model can make predictions."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }
        
        model = train_logistic_regression(X_train, y_train, params)
        predictions = model.predict(X_test)
        
        assert len(predictions) == len(y_test), "Should have predictions for all test samples"
        assert all(p in {0, 1, 2} for p in predictions), "Predictions should be valid classes"


class TestRandomForest:
    """Test Random Forest model."""
    
    def test_random_forest_trains(self):
        """Test that Random Forest model trains successfully."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }
        
        model = train_random_forest(X_train, y_train, params)
        assert model is not None, "Model should be trained"
        assert hasattr(model, 'predict'), "Model should have predict method"
    
    def test_random_forest_predicts(self):
        """Test that Random Forest model can make predictions."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }
        
        model = train_random_forest(X_train, y_train, params)
        predictions = model.predict(X_test)
        
        assert len(predictions) == len(y_test), "Should have predictions for all test samples"
        assert all(p in {0, 1, 2} for p in predictions), "Predictions should be valid classes"


class TestSVM:
    """Test Support Vector Machine model."""
    
    def test_svm_trains(self):
        """Test that SVM model trains successfully."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": "scale",
            "random_state": 42
        }
        
        model = train_svm(X_train, y_train, params)
        assert model is not None, "Model should be trained"
        assert hasattr(model, 'predict'), "Model should have predict method"
    
    def test_svm_predicts(self):
        """Test that SVM model can make predictions."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": "scale",
            "random_state": 42
        }
        
        model = train_svm(X_train, y_train, params)
        predictions = model.predict(X_test)
        
        assert len(predictions) == len(y_test), "Should have predictions for all test samples"
        assert all(p in {0, 1, 2} for p in predictions), "Predictions should be valid classes"


class TestEvaluation:
    """Test model evaluation."""
    
    def test_evaluate_model_returns_metrics(self):
        """Test that evaluate_model returns all required metrics."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }

        model = train_logistic_regression(X_train, y_train, params)
        metrics = evaluate_model(model, X_test, y_test, "test")

        assert "accuracy" in metrics, "Metrics should include accuracy"
        assert "precision" in metrics, "Metrics should include precision"
        assert "recall" in metrics, "Metrics should include recall"
        assert "f1" in metrics, "Metrics should include f1"
    
    def test_evaluate_model_metrics_in_range(self):
        """Test that metrics are in valid range."""
        X_train, X_test, y_train, y_test = fetch_data()
        params = {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }

        model = train_logistic_regression(X_train, y_train, params)
        metrics = evaluate_model(model, X_test, y_test, "test")

        assert 0 <= metrics["accuracy"] <= 1, "Accuracy should be between 0 and 1"
        assert 0 <= metrics["precision"] <= 1, "Precision should be between 0 and 1"
        assert 0 <= metrics["recall"] <= 1, "Recall should be between 0 and 1"
        assert 0 <= metrics["f1"] <= 1, "F1-score should be between 0 and 1"

