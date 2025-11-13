# Model Card: Iris Classifier

## Overview
This model card documents the Iris Classifier, a machine learning model trained to classify iris flowers into three species based on their physical measurements.

## Model Details

### Model Type
- **Algorithm**: Random Forest Classifier
- **Framework**: scikit-learn
- **Version**: 1.0
- **Training Date**: 2025-11-11

### Model Architecture
- **Number of Trees**: 100
- **Max Depth**: 10
- **Min Samples Split**: 2
- **Min Samples Leaf**: 1
- **Random State**: 42

## Dataset

### Dataset Description
The model is trained on the Iris dataset, a classic dataset in machine learning containing measurements of iris flowers.

### Dataset Characteristics
- **Total Samples**: 150 (120 training, 30 test)
- **Features**: 4 numerical features
  - Sepal Length (cm)
  - Sepal Width (cm)
  - Petal Length (cm)
  - Petal Width (cm)
- **Target Classes**: 3 (Setosa, Versicolor, Virginica)
- **Feature Range**: 0.1 - 7.9 cm
- **Class Distribution**: Balanced (50 samples per class)

### Data Splits
- **Training Set**: 80% (120 samples)
- **Test Set**: 20% (30 samples)
- **Random State**: 42 (for reproducibility)

## Performance Metrics

### Training Metrics
- **Training Accuracy**: ~0.98
- **Training Precision**: ~0.98
- **Training Recall**: ~0.98

### Test Metrics
- **Test Accuracy**: ~0.97
- **Test Precision**: ~0.97 (weighted)
- **Test Recall**: ~0.97 (weighted)
- **Test F1-Score**: ~0.97 (weighted)

### Per-Class Performance
The model performs well across all three iris species with balanced precision and recall.

## Feature Importance
The model's feature importance ranking (from most to least important):
1. **Petal Length**: ~0.45
2. **Petal Width**: ~0.42
3. **Sepal Length**: ~0.08
4. **Sepal Width**: ~0.05

Petal measurements are the most discriminative features for iris classification.

## Limitations

### Known Limitations
1. **Limited Dataset**: The Iris dataset is small (150 samples) and may not generalize to real-world iris classification tasks
2. **Balanced Classes Only**: The model is trained on perfectly balanced classes; performance may degrade with imbalanced data
3. **Feature Scope**: Only 4 features are used; additional features (color, texture, etc.) could improve performance
4. **Controlled Environment**: The dataset was collected in controlled conditions; real-world variations may affect performance
5. **No Temporal Data**: The model doesn't account for seasonal or temporal variations

### Generalization Concerns
- The model may not perform well on iris species not in the training set
- Measurement variations due to different collection methods could impact predictions
- The model assumes similar feature distributions to the training data

## Risks and Mitigations

### Potential Risks
1. **Overfitting**: With only 120 training samples, there's a risk of overfitting
   - **Mitigation**: Cross-validation and regularization through tree depth limits

2. **Class Imbalance**: If deployed on imbalanced data, performance may degrade
   - **Mitigation**: Monitor class distribution in production; retrain if needed

3. **Out-of-Distribution Data**: Predictions on data outside the training distribution may be unreliable
   - **Mitigation**: Implement input validation and anomaly detection

4. **Model Drift**: Performance may degrade over time as data distributions change
   - **Mitigation**: Regular monitoring and periodic retraining

### Fairness Considerations
- The model treats all iris species equally; no fairness issues identified
- No protected attributes are used in the model

## Usage

### Input Format
The model expects 4 numerical features in the following order:
1. Sepal Length (cm)
2. Sepal Width (cm)
3. Petal Length (cm)
4. Petal Width (cm)

### Output Format
The model outputs a class prediction (0, 1, or 2):
- 0: Setosa
- 1: Versicolor
- 2: Virginica

### Example Usage
```python
import mlflow.pyfunc

model = mlflow.pyfunc.load_model("models:/iris-classifier/Production")
predictions = model.predict([[5.1, 3.5, 1.4, 0.2]])
# Output: [0] (Setosa)
```

## Deployment

### Deployment Status
- **Current Stage**: Production
- **Deployment Method**: MLflow Model Registry
- **Serving Framework**: MLflow pyfunc

### Deployment Requirements
- Python 3.8+
- scikit-learn 1.3.2+
- MLflow 2.10.2+
- pandas 2.1.3+
- numpy 1.24.3+

### Monitoring Recommendations
1. Track prediction latency
2. Monitor input feature distributions
3. Log prediction confidence/probabilities
4. Track model performance metrics over time
5. Set up alerts for performance degradation

## Maintenance

### Retraining Schedule
- **Recommended Frequency**: Quarterly or when performance drops below 95% accuracy
- **Trigger Conditions**:
  - Accuracy drops below 95%
  - Significant data distribution shift detected
  - New iris species data becomes available

### Version Control
- Model versions are tracked in MLflow Model Registry
- Each version includes training parameters, metrics, and artifacts
- Production stage indicates the currently deployed version

## Contact and Support
For questions or issues with this model, please contact the ML team.

---
**Last Updated**: 2025-11-11
**Model Version**: 1.0
**Status**: Production Ready

