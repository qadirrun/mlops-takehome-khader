"""
Loop-based MLflow pipeline for training multiple models separately.
Trains 3 different models in a loop: Logistic Regression, Random Forest, SVM
Each model runs in its own MLflow experiment for easy comparison.
Automatically finds and registers the best model.
"""
import mlflow
import mlflow.sklearn
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from train.data_fetch import fetch_data, save_data
from train.multi_model_train import (
    train_logistic_regression,
    train_random_forest,
    train_svm,
    evaluate_model
)
from train.register import register_model, mark_for_deployment



# Define models to train
MODELS = [
    {
        "name": "logistic_regression",
        "display_name": "Logistic Regression",
        "run_name": "logistic-regression-run",
        "train_func": train_logistic_regression,
        "registry_name": "demo-iris-LR",
        "params": {
            "max_iter": 200,
            "random_state": 42,
            "solver": "lbfgs",
            "multi_class": "multinomial"
        }
    },
    {
        "name": "random_forest",
        "display_name": "Random Forest",
        "run_name": "random-forest-run",
        "train_func": train_random_forest,
        "registry_name": "demo-iris-RF",
        "params": {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }
    },
    {
        "name": "svm",
        "display_name": "Support Vector Machine",
        "run_name": "svm-run",
        "train_func": train_svm,
        "registry_name": "demo-iris-SVM",
        "params": {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": "scale",
            "random_state": 42
        }
    }
]


def train_model_pipeline(model_config, X_train, X_test, y_train, y_test):
    """
    Train a single model (registration happens after best model is selected).

    Args:
        model_config: Dictionary with model configuration
        X_train, X_test: Training and test features
        y_train, y_test: Training and test labels

    Returns:
        Dictionary with results
    """
    model_name = model_config["name"]
    display_name = model_config["display_name"]
    run_name = model_config["run_name"]
    train_func = model_config["train_func"]
    registry_name = model_config["registry_name"]
    params = model_config["params"]

    print("\n" + "=" * 70)
    print(f"Training: {display_name}")
    print("=" * 70)

    with mlflow.start_run(run_name=run_name):
        try:
            # Log data info
            print(f"\n[1/4] Logging data info...")
            mlflow.log_param("train_samples", len(X_train))
            mlflow.log_param("test_samples", len(X_test))
            mlflow.log_param("n_features", X_train.shape[1])
            mlflow.log_param("n_classes", len(set(y_train)))
            mlflow.log_param("model_type", model_name)
            print(f"✓ Data info logged")

            # Train model
            print(f"\n[2/4] Training {display_name}...")
            model = train_func(X_train, y_train, params)
            print(f"✓ Model trained successfully")

            # Evaluate model
            print(f"\n[3/4] Evaluating model...")
            metrics = evaluate_model(model, X_test, y_test, model_name)
            print(f"✓ Model evaluated")
            print(f"  - Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  - Precision: {metrics['precision']:.4f}")
            print(f"  - Recall:    {metrics['recall']:.4f}")
            print(f"  - F1-Score:  {metrics['f1']:.4f}")

            # Save and log model
            print(f"\n[4/4] Saving model...")
            mlflow.sklearn.log_model(model, "model")
            run_id = mlflow.active_run().info.run_id
            model_uri = f"runs:/{run_id}/model"
            print(f"✓ Model saved")
            print(f"  - Model URI: {model_uri}")

            print("\n" + "=" * 70)
            print(f"{display_name} Pipeline completed successfully!")
            print("=" * 70)
            print(f"Run Name: {run_name}")
            print(f"Run ID: {run_id}")

            return {
                "model": model_name,
                "display_name": display_name,
                "run_id": run_id,
                "registry_name": registry_name,
                "model_uri": model_uri,
                "metrics": metrics
            }

        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            mlflow.end_run(status="FAILED")
            raise


def run_all_models_loop(X_train, X_test, y_train, y_test):
    """
    Run all models in a loop.

    Args:
        X_train, X_test: Training and test features
        y_train, y_test: Training and test labels

    Returns:
        List of results for each model
    """
    all_results = []

    print("\n" + "#" * 70)
    print("# STARTING MULTI-MODEL TRAINING LOOP")
    print("#" * 70)

    for i, model_config in enumerate(MODELS, 1):
        print(f"\n\n>>> Model {i}/{len(MODELS)}: {model_config['display_name']}")

        result = train_model_pipeline(model_config, X_train, X_test, y_train, y_test)
        all_results.append(result)

    return all_results


def register_best_model(best_result):
    """
    Register the best model in MLflow Model Registry and mark for Production.

    Args:
        best_result: Dictionary with best model information

    Returns:
        ModelVersion object or None if registration fails
    """
    print("\n" + "=" * 70)
    print("REGISTERING BEST MODEL")
    print("=" * 70)

    model_uri = best_result["model_uri"]
    registry_name = best_result["registry_name"]
    display_name = best_result["display_name"]
    accuracy = best_result["metrics"]["accuracy"]

    print(f"\nBest Model: {display_name}")
    print(f"  - Accuracy: {accuracy:.4f}")
    print(f"  - Model URI: {model_uri}")
    print(f"  - Registry Name: {registry_name}")

    try:
        # Register the best model
        print(f"\n[1/2] Registering model in MLflow Model Registry...")
        model_version = register_model(model_uri, registry_name)
        print(f"✓ Model registered: {registry_name} v{model_version.version}")

        # Mark for Production deployment
        print(f"\n[2/2] Marking model for Production deployment...")
        mark_for_deployment(registry_name, model_version.version, stage="Production")
        print(f"✓ Model marked for Production")

        print("\n" + "=" * 70)
        print(f"✓ BEST MODEL SUCCESSFULLY REGISTERED AND DEPLOYED")
        print("=" * 70)

        return model_version

    except Exception as e:
        print(f"\n✗ Error registering best model: {e}")
        return None


def main():
    """Main entry point."""
    print("\n" + "#" * 70)
    print("# MULTI-MODEL TRAINING PIPELINE (LOOP-BASED)")
    print("#" * 70)

    # Set MLflow tracking URI to a temporary directory for CI/container runs
    import tempfile
    tracking_uri = f"sqlite:///{tempfile.mkdtemp()}/mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)
    print(f"\nMLflow Tracking URI: {mlflow.get_tracking_uri()}")

    # Set experiment once for all models
    experiment_name = "iris-demos"
    try:
        mlflow.set_experiment(experiment_name)
    except Exception as e:
        print(f"Note: {e}")
        print(f"Creating new experiment...")
        experiment_name = "iris-demos-v2"
        mlflow.set_experiment(experiment_name)

    print(f"\nExperiment: {experiment_name}")

    # Fetch data once
    print("\nFetching data...")
    X_train, X_test, y_train, y_test = fetch_data()
    save_data(X_train, X_test, y_train, y_test)
    print(f"✓ Data fetched: {len(X_train)} train, {len(X_test)} test samples")

    # Run all models in loop
    all_results = run_all_models_loop(X_train, X_test, y_train, y_test)

    # Print summary
    print("\n\n" + "#" * 70)
    print("# TRAINING SUMMARY")
    print("#" * 70)

    print("\nModel Comparison:")
    print("-" * 70)
    print(f"{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 70)

    for result in all_results:
        metrics = result["metrics"]
        print(f"{result['display_name']:<25} {metrics['accuracy']:<12.4f} {metrics['precision']:<12.4f} {metrics['recall']:<12.4f} {metrics['f1']:<12.4f}")

    print("-" * 70)

    # Find best model
    best_result = max(all_results, key=lambda x: x["metrics"]["accuracy"])
    print(f"\n✓ Best Model Found: {best_result['display_name']}")
    print(f"  - Accuracy: {best_result['metrics']['accuracy']:.4f}")
    print(f"  - Run ID: {best_result['run_id']}")

    # Register the best model
    model_version = register_best_model(best_result)

    if model_version:
        print(f"\n✓ Best model registered as: {best_result['registry_name']} v{model_version.version}")
        best_result['model_version'] = model_version.version
    else:
        print(f"\n✗ Failed to register best model")

    print("\n" + "#" * 70)
    print("# ALL MODELS TRAINED SUCCESSFULLY!")
    print("# Best model has been registered and marked for Production")
    print("# Check MLflow UI at http://localhost:5000 to compare")
    print("#" * 70)

    return all_results


if __name__ == "__main__":
    results = main()
    print(f"\n\nFinal Results: {len(results)} models trained")

