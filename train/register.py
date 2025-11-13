"""
Model registration and deployment marking module.
"""
import mlflow
from mlflow.entities.model_registry.model_version_status import ModelVersionStatus
import time


def register_model(model_uri: str, model_name: str = "iris-classifier"):
    """
    Register a model in MLflow Model Registry.
    
    Args:
        model_uri: URI of the model to register (e.g., "runs:/run_id/model")
        model_name: Name for the registered model
        
    Returns:
        ModelVersion object
    """
    try:
        # Register the model
        model_version = mlflow.register_model(model_uri, model_name)
        print(f"Model registered: {model_name} v{model_version.version}")
        return model_version
    except Exception as e:
        print(f"Error registering model: {e}")
        raise


def mark_for_deployment(model_name: str, version: int, stage: str = "Production"):
    """
    Mark a model version for deployment by transitioning to Production stage.
    
    Args:
        model_name: Name of the registered model
        version: Version number to promote
        stage: Target stage (Production, Staging, Archived)
    """
    client = mlflow.tracking.MlflowClient()
    
    try:
        # Transition model to Production
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=False
        )
        print(f"Model {model_name} v{version} transitioned to {stage}")
    except Exception as e:
        print(f"Error transitioning model: {e}")
        raise


def get_model_info(model_name: str, version: int = None):
    """
    Get information about a registered model.
    
    Args:
        model_name: Name of the registered model
        version: Specific version (None for latest)
        
    Returns:
        Model information
    """
    client = mlflow.tracking.MlflowClient()
    
    try:
        if version is None:
            # Get latest version
            model = client.get_latest_versions(model_name, stages=["Production"])
            if model:
                return model[0]
        else:
            # Get specific version
            return client.get_model_version(model_name, version)
    except Exception as e:
        print(f"Error getting model info: {e}")
        return None


def list_model_versions(model_name: str):
    """
    List all versions of a registered model.

    Args:
        model_name: Name of the registered model

    Returns:
        List of model versions
    """
    client = mlflow.tracking.MlflowClient()

    try:
        versions = client.search_model_versions(f"name='{model_name}'")
        return versions
    except Exception as e:
        print(f"Error listing model versions: {e}")
        return []


def list_all_registered_models():
    """
    List all registered models in MLflow Model Registry.

    Returns:
        List of all registered models
    """
    client = mlflow.tracking.MlflowClient()

    try:
        models = client.search_registered_models()
        return models
    except Exception as e:
        print(f"Error listing registered models: {e}")
        return []


def delete_model_version(model_name: str, version: int):
    """
    Delete a specific version of a registered model.

    Args:
        model_name: Name of the registered model
        version: Version number to delete

    Returns:
        True if successful, False otherwise
    """
    client = mlflow.tracking.MlflowClient()

    try:
        client.delete_model_version(model_name, version)
        print(f"✓ Deleted {model_name} v{version}")
        return True
    except Exception as e:
        print(f"✗ Error deleting {model_name} v{version}: {e}")
        return False


def delete_registered_model(model_name: str):
    """
    Delete an entire registered model (all versions).

    Args:
        model_name: Name of the registered model to delete

    Returns:
        True if successful, False otherwise
    """
    client = mlflow.tracking.MlflowClient()

    try:
        # First, delete all versions
        versions = list_model_versions(model_name)
        for version in versions:
            try:
                client.delete_model_version(model_name, version.version)
                print(f"  ✓ Deleted version {version.version}")
            except Exception as e:
                print(f"  ✗ Error deleting version {version.version}: {e}")

        # Then delete the model itself
        client.delete_registered_model(model_name)
        print(f"✓ Deleted registered model: {model_name}")
        return True
    except Exception as e:
        print(f"✗ Error deleting registered model {model_name}: {e}")
        return False


def delete_all_registered_models():
    """
    Delete ALL registered models from MLflow Model Registry.
    WARNING: This action cannot be undone!

    Returns:
        Dictionary with deletion results
    """
    print("\n" + "=" * 70)
    print("⚠️  WARNING: DELETING ALL REGISTERED MODELS")
    print("=" * 70)

    models = list_all_registered_models()

    if not models:
        print("No registered models found.")
        return {"total": 0, "deleted": 0, "failed": 0}

    print(f"\nFound {len(models)} registered model(s):")
    for model in models:
        print(f"  - {model.name}")

    # Ask for confirmation
    print("\n" + "-" * 70)
    confirmation = input("Are you sure you want to delete ALL models? (yes/no): ").strip().lower()

    if confirmation != "yes":
        print("✗ Deletion cancelled.")
        return {"total": len(models), "deleted": 0, "failed": 0}

    print("\n" + "=" * 70)
    print("DELETING ALL MODELS...")
    print("=" * 70)

    deleted = 0
    failed = 0

    for model in models:
        print(f"\nDeleting: {model.name}")
        if delete_registered_model(model.name):
            deleted += 1
        else:
            failed += 1

    print("\n" + "=" * 70)
    print("DELETION SUMMARY")
    print("=" * 70)
    print(f"Total models: {len(models)}")
    print(f"Successfully deleted: {deleted}")
    print(f"Failed: {failed}")
    print("=" * 70)

    return {"total": len(models), "deleted": deleted, "failed": failed}

