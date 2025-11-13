"""
Model deployment and serving module.
"""
import mlflow.pyfunc
import json
from pathlib import Path


class ModelServer:
    """Simple model server for inference."""
    
    def __init__(self, model_uri: str):
        """
        Initialize model server.
        
        Args:
            model_uri: URI to the model (e.g., "models:/iris-classifier/Production")
        """
        self.model = mlflow.pyfunc.load_model(model_uri)
        self.model_uri = model_uri
        print(f"Model loaded from: {model_uri}")
    
    def predict(self, features):
        """
        Make predictions on input features.
        
        Args:
            features: Input features (list or array-like)
            
        Returns:
            Predictions
        """
        try:
            predictions = self.model.predict(features)
            return predictions
        except Exception as e:
            print(f"Error making prediction: {e}")
            raise
    
    def predict_batch(self, features_list):
        """
        Make batch predictions.
        
        Args:
            features_list: List of feature arrays
            
        Returns:
            List of predictions
        """
        predictions = []
        for features in features_list:
            pred = self.predict(features)
            predictions.append(pred)
        return predictions


def deploy_model(model_name: str, stage: str = "Production", output_dir: str = "deploy"):
    """
    Deploy a model from the registry.
    
    Args:
        model_name: Name of the registered model
        stage: Stage to deploy from (Production, Staging, etc.)
        output_dir: Directory to save deployment info
        
    Returns:
        ModelServer instance
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # Model URI for loading from registry
    model_uri = f"models:/{model_name}/{stage}"
    
    # Initialize server
    server = ModelServer(model_uri)
    
    # Save deployment info
    deployment_info = {
        "model_name": model_name,
        "stage": stage,
        "model_uri": model_uri,
        "status": "deployed"
    }
    
    info_path = f"{output_dir}/deployment_info.json"
    with open(info_path, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"Model deployed successfully. Info saved to {info_path}")
    
    return server


def save_deployment_config(model_name: str, output_dir: str = "deploy"):
    """
    Save deployment configuration for Kubernetes/Docker.
    
    Args:
        model_name: Name of the registered model
        output_dir: Directory to save config
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # Example Docker deployment config
    docker_config = {
        "image": "mlflow-model-server:latest",
        "model_name": model_name,
        "port": 5000,
        "environment": {
            "MLFLOW_TRACKING_URI": "http://localhost:5000",
            "MODEL_NAME": model_name,
            "MODEL_STAGE": "Production"
        }
    }
    
    config_path = f"{output_dir}/docker_config.json"
    with open(config_path, 'w') as f:
        json.dump(docker_config, f, indent=2)
    
    print(f"Deployment config saved to {config_path}")

