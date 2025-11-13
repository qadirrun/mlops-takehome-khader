"""
Model evaluation module.
"""
import mlflow
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import pandas as pd
from pathlib import Path
import json


def evaluate_and_log(model, X_test, y_test, output_dir: str = "artifacts"):
    """
    Comprehensive model evaluation with MLflow logging.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        output_dir: Directory to save evaluation artifacts

    Returns:
        Dictionary of evaluation metrics
    """
    Path(output_dir).mkdir(exist_ok=True)

    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0),
    }
    
    # Log metrics
    for metric_name, metric_value in metrics.items():
        mlflow.log_metric(f"eval_{metric_name}", metric_value)
    
    # Generate classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    report_path = f"{output_dir}/classification_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    mlflow.log_artifact(report_path)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_path = f"{output_dir}/confusion_matrix.csv"
    pd.DataFrame(cm).to_csv(cm_path, index=False)
    mlflow.log_artifact(cm_path)
    
    return metrics

