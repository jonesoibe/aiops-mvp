from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_curve
import pandas as pd, numpy as np
import joblib, yaml
import matplotlib.pyplot as plt

def load_config():
    with open('config/settings.yaml') as f:
        return yaml.safe_load(f)

def train_isolation_forest(X_train):
    cfg = load_config()
    params = cfg['anomaly_detection']

    # MLflow tracking disabled for Render deployment
    # mlflow.end_run()
    # mlflow.set_experiment(cfg['mlflow']['experiment_name'])
    # with mlflow.start_run(run_name='IsolationForest_training'):
    #     mlflow.log_params(params)

    model = IsolationForest(
        n_estimators   = params['n_estimators'],
        contamination  = params['contamination'],
        random_state   = 42,
        n_jobs         = -1   # Use all CPU cores
    )
    model.fit(X_train)
    joblib.dump(model, 'models/isolation_forest.joblib')
    # mlflow.sklearn.log_model(model, 'isolation_forest')
    print('Isolation Forest trained and saved.')
    return model

def score_observations(model, X, threshold=0.55):
    """
    Returns anomaly scores and binary flags for each observation.
    Scores close to 1 = highly anomalous.
    Scores close to 0 = normal.
    threshold: flag as anomaly if score >= threshold.
    """
    # decision_function returns negative values for outliers in sklearn
    # We negate and normalise to [0,1] range
    raw_scores = model.decision_function(X)
    normalised = (raw_scores - raw_scores.min()) / \
                 (raw_scores.max() - raw_scores.min() + 1e-9)
    anomaly_scores = 1 - normalised  # Invert so high = anomalous
    flags = (anomaly_scores >= threshold).astype(int)
    return anomaly_scores, flags

def calibrate_threshold(model, X_val, y_val_true):
    """
    Find optimal detection threshold using precision-recall curve.

    Uses validation set to find the threshold that maximizes F1 score.
    This prevents overfitting to the training set.

    Args:
        model: Trained Isolation Forest model
        X_val: Validation feature matrix
        y_val_true: True labels on validation set (1=anomaly, 0=normal)

    Returns:
        Optimal threshold value (float)
    """
    scores, _ = score_observations(model, X_val, threshold=0)
    precision, recall, thresholds = precision_recall_curve(
        y_val_true, scores)

    # F1 for each threshold
    f1_scores = 2 * precision * recall / (precision + recall + 1e-9)
    best_idx  = f1_scores.argmax()
    best_thresh = thresholds[best_idx]

    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, f1_scores[:-1], label='F1', linewidth=2)
    plt.axvline(best_thresh, color='red',
                linestyle='--', label=f'Best threshold: {best_thresh:.3f}')
    plt.xlabel('Detection threshold')
    plt.ylabel('F1 Score')
    plt.title('Threshold Calibration — Isolation Forest')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('data/processed/threshold_calibration.png', dpi=150, bbox_inches='tight')
    plt.show()

    print(f'Best threshold on validation set: {best_thresh:.4f}')
    print(f'Best F1 on validation set: {f1_scores[best_idx]:.4f}')

    # Log to MLflow (disabled for Render deployment)
    # mlflow.log_metric('best_threshold', best_thresh)
    # mlflow.log_metric('best_f1', f1_scores[best_idx])

    return float(best_thresh)
