"""
Multi-model training module with MLflow integration.
Trains 3 different models: Logistic Regression, Random Forest, SVM
"""
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
from pathlib import Path
import json


def train_logistic_regression(X_train, y_train, params: dict = None):
    """
    Train Logistic Regression model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters
        
    Returns:
        Trained model
    """
    if params is None:
        params = {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }
    
    mlflow.log_params({f"lr_{k}": v for k, v in params.items()})
    model = LogisticRegression(**params)
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train, y_train, params: dict = None):
    """
    Train Random Forest model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters
        
    Returns:
        Trained model
    """
    if params is None:
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }
    
    mlflow.log_params({f"rf_{k}": v for k, v in params.items()})
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    return model


def train_svm(X_train, y_train, params: dict = None):
    """
    Train Support Vector Machine model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters
        
    Returns:
        Trained model
    """
    if params is None:
        params = {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": "scale",
            "random_state": 42
        }
    
    mlflow.log_params({f"svm_{k}": v for k, v in params.items()})
    model = SVC(**params)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test, model_name: str):
    """
    Evaluate model and return metrics.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        model_name: Name of the model for logging
        
    Returns:
        Dictionary of metrics
    """
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0),
    }
    
    # Log metrics with model prefix
    for metric_name, metric_value in metrics.items():
        mlflow.log_metric(f"{model_name}_{metric_name}", metric_value)
    
    return metrics


def save_model_comparison(results: dict, output_dir: str = "artifacts"):
    """
    Save model comparison results to JSON.
    
    Args:
        results: Dictionary with model results
        output_dir: Directory to save results
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    comparison_path = f"{output_dir}/model_comparison.json"
    with open(comparison_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    mlflow.log_artifact(comparison_path)
    return comparison_path


def train_all_models(X_train, X_test, y_train, y_test):
    """
    Train all 3 models and compare performance.
    
    Args:
        X_train, X_test: Training and test features
        y_train, y_test: Training and test labels
        
    Returns:
        Dictionary with all model results
    """
    results = {}
    models = {}
    
    # Train Logistic Regression
    print("\n  Training Logistic Regression...")
    lr_model = train_logistic_regression(X_train, y_train)
    lr_metrics = evaluate_model(lr_model, X_test, y_test, "lr")
    results["logistic_regression"] = lr_metrics
    models["logistic_regression"] = lr_model
    print(f"    ✓ Accuracy: {lr_metrics['accuracy']:.4f}")
    
    # Train Random Forest
    print("\n  Training Random Forest...")
    rf_model = train_random_forest(X_train, y_train)
    rf_metrics = evaluate_model(rf_model, X_test, y_test, "rf")
    results["random_forest"] = rf_metrics
    models["random_forest"] = rf_model
    print(f"    ✓ Accuracy: {rf_metrics['accuracy']:.4f}")
    
    # Train SVM
    print("\n  Training Support Vector Machine...")
    svm_model = train_svm(X_train, y_train)
    svm_metrics = evaluate_model(svm_model, X_test, y_test, "svm")
    results["svm"] = svm_metrics
    models["svm"] = svm_model
    print(f"    ✓ Accuracy: {svm_metrics['accuracy']:.4f}")
    
    # Save comparison
    print("\n  Saving model comparison...")
    save_model_comparison(results)
    
    return results, models

