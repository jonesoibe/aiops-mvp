"""
Issue classification module for AIOps MVP.

Classifies detected anomalies into actionable issue types:
- Performance degradation
- Service outage
- Resource exhaustion
- Network issues
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class IssueClassifier:
    """Classifies anomalies into issue types."""

    # Issue categories
    ISSUE_TYPES = {
        0: 'performance_degradation',
        1: 'service_outage',
        2: 'resource_exhaustion',
        3: 'network_issue',
        4: 'unknown'
    }

    def __init__(self, config: dict):
        """Initialize issue classifier."""
        self.config = config
        self.classifier = RandomForestClassifier(
            n_estimators=config['classification']['n_estimators'],
            max_depth=config['classification']['max_depth'],
            random_state=config['classification']['random_state']
        )
        self.label_encoders = {}
        self.feature_names = None
        self.automation_threshold = config['classification']['automation_threshold']
        logger.info("Initialized Issue Classifier")

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'IssueClassifier':
        """
        Fit classifier on labeled anomalies.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (issue type indices)

        Returns:
            Self
        """
        logger.info(f"Fitting classifier on {X.shape[0]} samples with {X.shape[1]} features")
        self.classifier.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict issue types.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, confidence scores)
        """
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)
        confidences = probabilities.max(axis=1)

        logger.debug(f"Predicted {len(predictions)} issue types")
        return predictions, confidences

    def predict_with_automation(
        self,
        X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict issues and determine if they can be auto-remediated.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, confidences, auto_remediable)
        """
        predictions, confidences = self.predict(X)

        # Issues are considered automatable if:
        # 1. Confidence is high (above threshold)
        # 2. Issue type is in automatable list
        automatable_types = {0, 2}  # performance_degradation, resource_exhaustion
        auto_remediable = np.array([
            (conf > self.automation_threshold) and (pred in automatable_types)
            for pred, conf in zip(predictions, confidences)
        ])

        logger.debug(f"Marked {auto_remediable.sum()} issues as auto-remediable")
        return predictions, confidences, auto_remediable

    def get_issue_name(self, issue_idx: int) -> str:
        """Get human-readable issue name."""
        return self.ISSUE_TYPES.get(issue_idx, 'unknown')

    def extract_anomaly_features(
        self,
        df: pd.DataFrame,
        window_indices: np.ndarray
    ) -> np.ndarray:
        """
        Extract features from anomalous windows.

        Args:
            df: DataFrame with metric data
            window_indices: Indices of anomalous windows

        Returns:
            Feature matrix (n_anomalies, n_features)
        """
        features = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'machine_id' in numeric_cols:
            numeric_cols.remove('machine_id')

        for idx in window_indices:
            # Extract a window around the anomaly
            window_start = max(0, idx - 5)
            window_end = min(len(df), idx + 5)
            window_data = df[numeric_cols].iloc[window_start:window_end].values

            # Compute statistical features
            feature_vec = np.concatenate([
                window_data.mean(axis=0),  # Mean
                window_data.std(axis=0),   # Std dev
                np.abs(np.diff(window_data.mean(axis=1))).sum(axis=0) if window_data.shape[0] > 1 else np.zeros(len(numeric_cols)),  # Rate of change
            ])
            features.append(feature_vec)

        self.feature_names = numeric_cols
        logger.info(f"Extracted features from {len(features)} anomalies")
        return np.array(features)


class CorrelationAnalyzer:
    """Analyzes metric correlations to pinpoint root causes."""

    def __init__(self, config: dict):
        """Initialize correlation analyzer."""
        self.config = config
        self.window_seconds = config['correlation']['window_seconds']

    def find_correlated_metrics(
        self,
        df: pd.DataFrame,
        anomaly_idx: int,
        threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Find metrics most correlated with anomaly.

        Args:
            df: DataFrame with metric data
            anomaly_idx: Index of anomalous point
            threshold: Correlation threshold

        Returns:
            List of (metric_name, correlation) tuples
        """
        # Get window around anomaly
        window_size = self.window_seconds // 60  # Assuming minute-level data
        window_start = max(0, anomaly_idx - window_size)
        window_end = min(len(df), anomaly_idx + window_size)

        window_data = df.iloc[window_start:window_end]
        numeric_cols = window_data.select_dtypes(include=[np.number]).columns

        # Compute correlations
        corr_matrix = window_data[numeric_cols].corr()

        # Get correlations with first metric (as reference)
        correlations = corr_matrix.iloc[0].abs().sort_values(ascending=False)
        high_corr = [(metric, corr) for metric, corr in correlations.items() if corr > threshold and corr < 1.0]

        logger.debug(f"Found {len(high_corr)} highly correlated metrics")
        return high_corr
