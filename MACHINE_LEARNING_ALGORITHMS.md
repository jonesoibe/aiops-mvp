# AIOps Platform - Machine Learning Algorithms Guide

## 📚 Overview

The Nexus AIOps platform uses two core ML algorithms:
1. **Isolation Forest** - Unsupervised anomaly detection
2. **Random Forest** - Supervised incident classification

Both leverage scikit-learn's efficient implementations with production-ready hyperparameters.

---

## 🔍 PART 1: ANOMALY DETECTION - ISOLATION FOREST

### Algorithm Overview

**Isolation Forest** is an unsupervised ensemble method that detects anomalies by isolating outliers in feature space.

**Key Principle:** Anomalies are "few and different" - they require fewer splits to isolate in a decision tree.

### Mathematical Foundation

**Decision Function:**

```
anomaly_score = 2^(-E[h(x)]/c(n))
```

Where:
- `E[h(x)]` = Expected path length to isolate point x
- `c(n)` = Average path length of unsuccessful search
- `n` = Number of training samples

**Score Interpretation:**
```
score ≈ 1.0  → Highly anomalous (outlier)
score ≈ 0.5  → Normal (within cluster)
score ≈ 0.0  → Typical (central point)
```

### Implementation

**Configuration (config/settings.yaml):**

```yaml
anomaly_detection:
  n_estimators: 100      # Number of isolation trees
  contamination: 0.05    # Assumed contamination rate (5%)
  random_state: 42       # Reproducibility
```

**Training Code:**

```python
from sklearn.ensemble import IsolationForest
import joblib

def train_isolation_forest(X_train):
    """
    Train Isolation Forest model on preprocessed features.
    
    Args:
        X_train: Scaled training feature matrix (n_samples, n_features)
    
    Returns:
        Trained Isolation Forest model
    """
    model = IsolationForest(
        n_estimators=100,        # 100 trees in ensemble
        contamination=0.05,      # Expect ~5% anomalies in training
        random_state=42,         # Fixed seed for reproducibility
        n_jobs=-1                # Use all CPU cores for parallel fitting
    )
    
    model.fit(X_train)
    joblib.dump(model, 'models/isolation_forest.joblib')
    return model
```

**Prediction Code:**

```python
def score_observations(model, X, threshold=0.55):
    """
    Score observations and flag anomalies.
    
    Args:
        model: Trained Isolation Forest
        X: Feature matrix to score
        threshold: Anomaly flag threshold (0.0-1.0)
    
    Returns:
        Tuple of (anomaly_scores, binary_flags)
    """
    # Step 1: Get raw decision function scores
    raw_scores = model.decision_function(X)
    # Raw scores: negative (normal) to positive (anomalous)
    
    # Step 2: Normalize to [0, 1] range
    min_score = raw_scores.min()
    max_score = raw_scores.max()
    normalised = (raw_scores - min_score) / (max_score - min_score + 1e-9)
    
    # Step 3: Invert so high = anomalous
    anomaly_scores = 1 - normalised
    
    # Step 4: Binary flagging
    flags = (anomaly_scores >= threshold).astype(int)
    # 1 = anomaly, 0 = normal
    
    return anomaly_scores, flags
```

### Threshold Calibration

**Optimal Threshold Selection Using F1 Score:**

```python
from sklearn.metrics import precision_recall_curve

def calibrate_threshold(model, X_val, y_val_true):
    """
    Find optimal detection threshold on validation set.
    Maximizes F1 score = 2 * (precision * recall) / (precision + recall)
    
    Args:
        model: Trained Isolation Forest
        X_val: Validation feature matrix
        y_val_true: True binary labels (1=anomaly, 0=normal)
    
    Returns:
        Optimal threshold value
    """
    # Score validation set
    scores, _ = score_observations(model, X_val, threshold=0)
    
    # Generate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(
        y_val_true,  # True labels
        scores       # Anomaly scores
    )
    
    # Calculate F1 for each threshold
    f1_scores = 2 * precision * recall / (precision + recall + 1e-9)
    
    # Find threshold with maximum F1
    best_idx = f1_scores.argmax()
    best_threshold = thresholds[best_idx]
    best_f1 = f1_scores[best_idx]
    
    return float(best_threshold)
```

**F1 Score Formula:**

```
F1 = 2 * (Precision × Recall) / (Precision + Recall)

Where:
  Precision = TP / (TP + FP)    [Correct anomaly detections / All detections]
  Recall = TP / (TP + FN)       [Correct detections / All actual anomalies]
  
  TP (True Positive) = Correctly detected anomaly
  FP (False Positive) = Normal flagged as anomaly
  FN (False Negative) = Anomaly missed
```

### Isolation Forest Hyperparameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **n_estimators** | 100 | Number of isolation trees (more = better but slower) |
| **contamination** | 0.05 | Assumed anomaly rate in training data |
| **random_state** | 42 | Seed for reproducibility |
| **n_jobs** | -1 | Use all CPU cores |

### Computational Complexity

```
Training Time: O(n_estimators * n * log(n))
Prediction Time: O(n_estimators * log(n))

Where:
  n = number of samples
  d = number of features
```

**Example:**
```
- 10,000 samples, 50 features
- Training: 100 trees * 10,000 * log(10,000) ≈ ~16 million operations
- Per-sample prediction: 100 * log(10,000) ≈ ~1,400 operations
```

### Advantages & Limitations

**Advantages:**
- ✅ Works well for high-dimensional data
- ✅ No need for labeled anomalies (unsupervised)
- ✅ Fast training and inference
- ✅ Robust to irrelevant features

**Limitations:**
- ❌ Struggles with dense regions
- ❌ Equal-sized clusters may not work well
- ❌ Cannot extrapolate beyond training range

---

## 🎯 PART 2: INCIDENT CLASSIFICATION - RANDOM FOREST

### Algorithm Overview

**Random Forest** is a supervised ensemble method that classifies incidents into 5 categories:
1. **Performance Degradation** (0) - High latency, slow response times
2. **Service Outage** (1) - Complete service unavailability
3. **Resource Exhaustion** (2) - CPU, memory, disk full
4. **Network Issue** (3) - Connectivity, packet loss problems
5. **Unknown** (4) - Cannot determine root cause

### Mathematical Foundation

**Random Forest Prediction:**

```
prediction = mode(decision_tree_1, decision_tree_2, ..., decision_tree_n)
probability = count(tree predictions for class i) / n_trees
```

**Decision Function at Each Node:**

```
information_gain(split) = entropy(parent) - Σ(weight * entropy(child))

entropy(node) = -Σ(p_i * log2(p_i))

Where:
  p_i = probability of class i at node
```

### Implementation

**Configuration (config/settings.yaml):**

```yaml
classification:
  n_estimators: 100      # Number of decision trees
  max_depth: 10          # Maximum tree depth
  random_state: 42       # Reproducibility
  automation_threshold: 0.7  # Confidence needed for auto-remediation
```

**Classifier Code:**

```python
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple
import numpy as np

class IssueClassifier:
    """Classifies anomalies into incident types."""
    
    ISSUE_TYPES = {
        0: 'performance_degradation',
        1: 'service_outage',
        2: 'resource_exhaustion',
        3: 'network_issue',
        4: 'unknown'
    }
    
    def __init__(self, config: dict):
        self.classifier = RandomForestClassifier(
            n_estimators=config['classification']['n_estimators'],      # 100 trees
            max_depth=config['classification']['max_depth'],            # Max depth 10
            random_state=config['classification']['random_state']       # Seed 42
        )
        self.automation_threshold = config['classification']['automation_threshold']
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'IssueClassifier':
        """
        Train classifier on labeled anomalies.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Class labels (0-4)
        
        Returns:
            Self (for method chaining)
        """
        self.classifier.fit(X, y)
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict issue classes and confidence scores.
        
        Args:
            X: Feature matrix
        
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        # Get class predictions
        predictions = self.classifier.predict(X)
        
        # Get probability for each class
        probabilities = self.classifier.predict_proba(X)
        # Shape: (n_samples, n_classes)
        # probabilities[i] = [p(class0), p(class1), p(class2), p(class3), p(class4)]
        
        # Confidence = maximum probability across all classes
        confidences = probabilities.max(axis=1)
        
        return predictions, confidences
    
    def predict_with_automation(
        self,
        X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict issues and determine if auto-remediable.
        
        Args:
            X: Feature matrix
        
        Returns:
            Tuple of (predictions, confidences, auto_remediable_flags)
        """
        predictions, confidences = self.predict(X)
        
        # Only these issue types are automatable:
        automatable_types = {
            0,  # performance_degradation
            2   # resource_exhaustion
        }
        
        # Flag as auto-remediable if:
        # 1. Confidence > threshold (default 0.7 = 70%)
        # 2. Issue type is automatable
        auto_remediable = np.array([
            (conf > self.automation_threshold) and (pred in automatable_types)
            for pred, conf in zip(predictions, confidences)
        ])
        
        return predictions, confidences, auto_remediable
```

### Feature Importance

**How Random Forest Determines Feature Importance:**

```
importance(feature) = Σ(information_gain from splits using feature) / total_splits

Features with highest importance = most useful for classification
```

**Example Output:**

```python
feature_importance = classifier.feature_importances_
# Output shape: (n_features,)

# Sorted importance
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

#         feature  importance
# 0   cpu_p95         0.241
# 1   mem_max         0.187
# 2   error_rate      0.156
# 3   latency_mean    0.142
# 4   disk_io         0.089
# ...
```

### Random Forest Hyperparameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **n_estimators** | 100 | Number of trees in forest |
| **max_depth** | 10 | Maximum tree depth (prevents overfitting) |
| **random_state** | 42 | Seed for reproducibility |
| **min_samples_split** | 2 | Min samples to split a node |
| **min_samples_leaf** | 1 | Min samples in leaf node |

### Computational Complexity

```
Training Time: O(n_estimators * n * log(n) * d)
Prediction Time: O(n_estimators * log(n))

Where:
  n = number of samples
  d = number of features
```

---

## 🛠️ PART 3: FEATURE ENGINEERING

### Raw Metrics → Features

**Input:** Time series of metrics
```
timestamp    cpu    memory    latency   error_rate
2026-09-07   45.2   72.1      125.4     0.05
2026-09-07   46.1   73.2      128.1     0.06
2026-09-07   47.3   74.5      130.2     0.07
...
```

**Feature Engineering Code:**

```python
def engineer_features(df, window_size=60):
    """
    Aggregate raw metrics into feature vectors using sliding windows.
    
    For each window, compute:
    - Mean (average value)
    - Max (peak value)
    - 95th percentile (extreme outliers)
    - Rate of change (trend)
    
    Args:
        df: DataFrame with raw metrics (timestamps × metrics)
        window_size: Number of samples per window (default 60 = 1 minute @ 1Hz)
    
    Returns:
        DataFrame of aggregated features
    """
    features = []
    
    for start in range(0, len(df) - window_size, window_size):
        window = df.iloc[start:start + window_size]
        stats = {}
        
        for metric_col in df.columns:
            values = window[metric_col]
            
            # Mean: Average value in window
            stats[f'{metric_col}_mean'] = values.mean()
            
            # Max: Peak value in window
            stats[f'{metric_col}_max'] = values.max()
            
            # P95: 95th percentile (captures extreme outliers)
            stats[f'{metric_col}_p95'] = values.quantile(0.95)
            
            # Rate of change: (last - first) / window_size
            stats[f'{metric_col}_roc'] = (
                (values.iloc[-1] - values.iloc[0]) / window_size
            )
        
        features.append(stats)
    
    return pd.DataFrame(features)
```

**Example Output:**

```
From 60 raw metric points:
- cpu_mean: 45.8
- cpu_max: 52.3
- cpu_p95: 50.1
- cpu_roc: 0.12
- memory_mean: 73.4
- memory_max: 76.2
... (4 statistics × N metrics)
```

**Why These Features?**

| Feature | Detects |
|---------|---------|
| **mean** | Sustained high values (overload) |
| **max** | Peak spikes (sudden events) |
| **p95** | Outlier presence |
| **roc** (rate of change) | Degradation trends, memory leaks |

### Feature Scaling - StandardScaler

**Problem:** Different metrics have different ranges
```
CPU: 0-100%
Memory: 0-64GB
Latency: 10-500ms
```

**Solution: Standardization**

```
x_scaled = (x - mean) / std_dev

So each feature has:
- Mean = 0
- Std Dev = 1
```

**Implementation:**

```python
from sklearn.preprocessing import StandardScaler

def normalise_features(X_train, X_val, X_test):
    """
    Normalize features to zero mean and unit variance.
    
    CRITICAL: Fit scaler on TRAINING data only!
    Apply same scaler to validation/test to avoid data leakage.
    
    Args:
        X_train: Training feature matrix
        X_val: Validation feature matrix
        X_test: Test feature matrix
    
    Returns:
        Tuple of scaled matrices
    """
    # Step 1: Fit scaler on training data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    # Scaler learns: mean and std of training data
    
    # Step 2: Apply same scaler to validation and test
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    # Uses training mean and std!
    
    # Step 3: Save scaler for production
    joblib.dump(scaler, 'models/scaler.joblib')
    
    return X_train_scaled, X_val_scaled, X_test_scaled
```

---

## 📊 PART 4: DATA SPLITTING - TIME-BASED

**Problem:** Time series data is sequential - random shuffling breaks temporal patterns!

**Solution: Time-Based Train/Val/Test Split**

```python
def time_based_split(df, val_split=0.15, test_split=0.15):
    """
    Split time series data temporally (no shuffling).
    
    Timeline:
    |------- TRAIN (70%) ------|--- VAL (15%) ---|-- TEST (15%) --|
    
    Args:
        df: Time-ordered DataFrame
        val_split: Fraction for validation (0.15 = 15%)
        test_split: Fraction for test (0.15 = 15%)
    
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    n = len(df)
    
    # Calculate split points
    train_end = int(n * (1 - val_split - test_split))  # 70% of data
    val_end = int(n * (1 - test_split))                 # 85% of data
    
    # Split by position (not random)
    train_df = df.iloc[:train_end]           # First 70%
    val_df = df.iloc[train_end:val_end]      # Middle 15%
    test_df = df.iloc[val_end:]              # Last 15%
    
    return train_df, val_df, test_df
```

**Why Time-Based Split?**

```
❌ WRONG (Random Split):
├── Train: Mixed samples from entire time period
├── Val: Can see future patterns during training!
└── Test: Leakage - model trains on future data

✅ CORRECT (Time-Based Split):
├── Train: Early samples (model learns patterns)
├── Val: Middle samples (optimization happens)
└── Test: Latest samples (true production-like evaluation)
```

---

## 🎓 PART 5: MODEL EVALUATION

### Evaluation Metrics

**For Anomaly Detection (Binary Classification):**

```python
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)

def evaluate_detection(y_true, y_pred, y_scores=None):
    """
    Evaluate anomaly detection model.
    
    Args:
        y_true: True labels (1=anomaly, 0=normal)
        y_pred: Predicted labels
        y_scores: Anomaly scores (0-1)
    
    Returns:
        Dictionary of metrics
    """
    metrics = {
        # Precision: Of detected anomalies, how many are correct?
        'precision': precision_score(y_true, y_pred),
        
        # Recall: Of all actual anomalies, how many did we catch?
        'recall': recall_score(y_true, y_pred),
        
        # F1: Harmonic mean of precision and recall
        'f1': f1_score(y_true, y_pred),
        
        # Confusion matrix
        'confusion_matrix': confusion_matrix(y_true, y_pred)
    }
    
    # ROC-AUC: Area under receiver operating characteristic curve
    if y_scores is not None:
        metrics['roc_auc'] = roc_auc_score(y_true, y_scores)
    
    return metrics
```

**Confusion Matrix:**

```
                 Predicted
                 Normal  Anomaly
Actual Normal      TN      FP
       Anomaly     FN      TP

Where:
  TP (True Positive) = Correctly detected anomaly
  TN (True Negative) = Correctly identified normal
  FP (False Positive) = Normal flagged as anomaly (Type I error)
  FN (False Negative) = Anomaly missed (Type II error)
```

**For Classification (Multi-Class):**

```python
from sklearn.metrics import classification_report

def evaluate_classification(y_true, y_pred):
    """Classification accuracy by class."""
    return classification_report(y_true, y_pred, output_dict=True)
```

---

## 🔄 PART 6: COMPLETE ML PIPELINE

### End-to-End Training Flow

```
┌─────────────────────────────────────────────┐
│ 1. DATA LOADING & PREPROCESSING             │
│    - Load raw metrics from SMD dataset      │
│    - Clean, handle missing values           │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 2. FEATURE ENGINEERING (engineer_features) │
│    - Window aggregation (60-sample windows) │
│    - Calculate: mean, max, p95, roc        │
│    - Output: ~200 derived features         │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 3. TIME-BASED SPLIT                        │
│    - Train: First 70% (temporal)           │
│    - Val: Middle 15% (temporal)            │
│    - Test: Last 15% (temporal)             │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 4. FEATURE SCALING (StandardScaler)        │
│    - Fit on training data only             │
│    - Apply to val and test                 │
│    - Prevent data leakage                  │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 5. MODEL TRAINING                          │
│    A. Anomaly Detection                    │
│       - Train Isolation Forest (100 trees) │
│       - Fit on X_train_scaled              │
│                                             │
│    B. Threshold Calibration                │
│       - Score validation set               │
│       - Find threshold maximizing F1       │
│                                             │
│    C. Classification                       │
│       - Label anomalies by root cause      │
│       - Train Random Forest (100 trees)    │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 6. MODEL EVALUATION (Test Set)              │
│    - Precision, Recall, F1                 │
│    - ROC-AUC                               │
│    - Confusion Matrix                      │
│    - Feature Importance                    │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ 7. MODEL PERSISTENCE                       │
│    - Save Isolation Forest → joblib        │
│    - Save Random Forest → joblib           │
│    - Save Scaler → joblib                  │
└─────────────────────────────────────────────┘
```

### Training Code Example

```python
import pandas as pd
from src.preprocess import engineer_features, normalise_features, time_based_split
from src.detect import train_isolation_forest, score_observations, calibrate_threshold
from src.classify import IssueClassifier

# Load raw metrics
df_raw = pd.read_csv('data/raw/metrics.csv')

# 1. Feature engineering
df_features = engineer_features(df_raw, window_size=60)

# 2. Time-based split (CRITICAL: NO SHUFFLING)
train, val, test = time_based_split(df_features, val_split=0.15, test_split=0.15)

# 3. Feature scaling
X_train_scaled, X_val_scaled, X_test_scaled = normalise_features(
    train, val, test
)

# 4. Train anomaly detection
model_if = train_isolation_forest(X_train_scaled)

# 5. Calibrate threshold on validation set
# (Assume we have labels for val set - labeled after incidents)
threshold = calibrate_threshold(model_if, X_val_scaled, y_val_labeled)

# 6. Score test set
anomaly_scores, flags = score_observations(model_if, X_test_scaled, threshold)

# 7. Train classification model
# (Assume incidents in test set labeled by root cause)
classifier = IssueClassifier(config)
classifier.fit(X_test_scaled[flags == 1], y_test_root_causes[flags == 1])

# 8. Evaluate
from src.evaluate import ModelEvaluator
evaluator = ModelEvaluator(config)
metrics = evaluator.evaluate_detection(y_test_labeled, flags, anomaly_scores)
print(f"Test Set Performance:")
print(f"  Precision: {metrics['precision']:.3f}")
print(f"  Recall: {metrics['recall']:.3f}")
print(f"  F1: {metrics['f1']:.3f}")
print(f"  ROC-AUC: {metrics.get('roc_auc', 'N/A')}")
```

---

## 📈 PART 7: PRODUCTION INFERENCE

### Real-Time Detection & Classification

```python
# In production (nexus_app.py)

# 1. Receive new metrics
new_metrics = get_latest_metrics()

# 2. Engineer features (same window size)
new_features = engineer_features(new_metrics, window_size=60)

# 3. Scale features (using saved scaler!)
scaler = joblib.load('models/scaler.joblib')
new_features_scaled = scaler.transform(new_features)

# 4. Detect anomalies
model_if = joblib.load('models/isolation_forest.joblib')
anomaly_scores, flags = score_observations(
    model_if,
    new_features_scaled,
    threshold=0.55  # Pre-calibrated threshold
)

# 5. Classify detected anomalies
if flags[0] == 1:  # Anomaly detected
    classifier = joblib.load('models/random_forest_classifier.joblib')
    issue_type, confidence = classifier.predict(new_features_scaled[0:1])
    
    print(f"Anomaly Detected!")
    print(f"  Type: {IssueClassifier.ISSUE_TYPES[issue_type[0]]}")
    print(f"  Confidence: {confidence[0]:.1%}")
    
    # If high-confidence and automatable, trigger remediation
    if confidence[0] > 0.7 and issue_type[0] in {0, 2}:
        trigger_auto_remediation(issue_type[0])
```

---

## 🎯 Summary: Algorithm Comparison

| Aspect | Isolation Forest | Random Forest |
|--------|------------------|---------------|
| **Type** | Unsupervised | Supervised |
| **Purpose** | Anomaly Detection | Classification |
| **Trees** | 100 isolation trees | 100 decision trees |
| **Training Data** | Unlabeled metrics | Labeled incidents |
| **Output** | Anomaly score (0-1) | Class + confidence |
| **Threshold** | Calibrated via F1 | Built-in probabilities |
| **Complexity** | O(n log n) | O(n log n) |
| **Parallelization** | n_jobs=-1 | n_jobs=-1 |

---

## 📚 References

**Isolation Forest Paper:**
- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008)
- "Isolation Forest"
- IEEE Transactions on Knowledge and Data Engineering

**Random Forest:**
- Breiman, L. (2001)
- "Random Forests"
- Machine Learning Journal

**scikit-learn Documentation:**
- https://scikit-learn.org/stable/modules/ensemble.html
- Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- Random Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-12  
**Models Used**: Isolation Forest (v1), Random Forest (v1)  
**Framework**: scikit-learn 1.3.0+  
**Training Data**: SMD dataset (28 machines, 640K samples)
