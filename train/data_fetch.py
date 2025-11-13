"""
Data fetching and preparation module for MLflow pipeline.
"""
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from pathlib import Path


def fetch_data(test_size: float = 0.2, random_state: int = 42):
    """
    Fetch and prepare the Iris dataset.
    
    Args:
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    # Load Iris dataset
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    return X_train, X_test, y_train, y_test


def save_data(X_train, X_test, y_train, y_test, output_dir: str = "data"):
    """
    Save train/test data to CSV files.
    
    Args:
        X_train, X_test, y_train, y_test: Data splits
        output_dir: Directory to save data
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create DataFrames with feature names
    feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    
    train_df = pd.DataFrame(X_train, columns=feature_names)
    train_df['target'] = y_train
    
    test_df = pd.DataFrame(X_test, columns=feature_names)
    test_df['target'] = y_test
    
    train_df.to_csv(f"{output_dir}/train.csv", index=False)
    test_df.to_csv(f"{output_dir}/test.csv", index=False)
    
    return f"{output_dir}/train.csv", f"{output_dir}/test.csv"

