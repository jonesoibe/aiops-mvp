"""
Main AIOps pipeline orchestration module.

Coordinates all components:
- Data ingestion
- Preprocessing
- Anomaly detection
- Issue classification
- Remediation and response
"""

import os
import yaml
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, List, Optional
import logging

# Import all modules
from .ingest import DataIngester
from .preprocess import (
    load_config,
    engineer_features,
    normalise_features,
    time_based_split
)
from .detect import (
    train_isolation_forest,
    score_observations,
    calibrate_threshold
)
from .classify import IssueClassifier, CorrelationAnalyzer
from .respond import ResponseExecutor, RecoveryMonitor, AlertGenerator
from .evaluate import ModelEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIOpsPipeline:
    """Main orchestration pipeline for AIOps MVP."""

    def __init__(self, config_path: str = 'config/settings.yaml'):
        """
        Initialize the AIOps pipeline.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._initialize_components()

        # Store model artifacts
        self.model = None
        self.scaler = None
        self.optimal_threshold = None

        logger.info("AIOps Pipeline initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"Configuration loaded from {config_path}")
        return config

    def _initialize_components(self):
        """Initialize all pipeline components."""
        self.ingester = DataIngester(self.config)
        self.classifier = IssueClassifier(self.config)
        self.correlator = CorrelationAnalyzer(self.config)
        self.responder = ResponseExecutor(self.config)
        self.recovery_monitor = RecoveryMonitor(self.config)
        self.alert_generator = AlertGenerator(self.config)
        self.evaluator = ModelEvaluator(self.config)
        logger.info("All components initialized")

    def prepare_data(self, data_source: str = 'smd', machine_id: str = 'machine-1-1') -> Tuple:
        """
        Load and prepare data for training.

        Args:
            data_source: 'smd' or 'aiops'
            machine_id: Machine to load

        Returns:
            Tuple of (X_train_scaled, X_val_scaled, X_test_scaled, test_df)
        """
        logger.info(f"Preparing data from {data_source}/{machine_id}")

        # Load raw data
        if data_source == 'smd':
            df = self.ingester.read_smd_data(machine_id)
        else:
            raise NotImplementedError("AIOps data loading not yet implemented")

        # Extract numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_numeric = df[numeric_cols]

        # Time-based split
        train_df, val_df, test_df = time_based_split(
            df_numeric,
            val_split=self.config['data']['val_split'],
            test_split=self.config['data']['test_split']
        )

        # Feature engineering
        X_train = engineer_features(train_df, window_size=60)
        X_val = engineer_features(val_df, window_size=60)
        X_test = engineer_features(test_df, window_size=60)

        # Normalization
        X_train_scaled, X_val_scaled, X_test_scaled = normalise_features(
            X_train.values,
            X_val.values,
            X_test.values
        )

        logger.info(f"Data preparation complete: train={X_train_scaled.shape}, val={X_val_scaled.shape}, test={X_test_scaled.shape}")
        return X_train_scaled, X_val_scaled, X_test_scaled, test_df

    def train(self, X_train_scaled: np.ndarray, X_val_scaled: np.ndarray, y_val_true: np.ndarray = None) -> float:
        """
        Train anomaly detection model and classifier, then calibrate threshold.

        Args:
            X_train_scaled: Training features
            X_val_scaled: Validation features
            y_val_true: True validation labels (optional)

        Returns:
            Optimal threshold
        """
        logger.info("Training anomaly detection model and classifier")

        # Train Isolation Forest
        self.model = train_isolation_forest(X_train_scaled)

        # Train classifier on synthetic labels (in production, use real labels)
        y_train_classifier = np.random.randint(0, 4, X_train_scaled.shape[0])
        self.classifier.fit(X_train_scaled, y_train_classifier)
        logger.info("Classifier trained on training data")

        # Calibrate threshold
        if y_val_true is None:
            y_val_true = np.random.randint(0, 2, X_val_scaled.shape[0])

        self.optimal_threshold = calibrate_threshold(self.model, X_val_scaled, y_val_true)
        logger.info(f"Model trained with optimal threshold: {self.optimal_threshold:.4f}")

        return self.optimal_threshold

    def detect(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Detect anomalies in data.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (scores, flags, indices)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        scores, flags = score_observations(self.model, X, threshold=self.optimal_threshold)
        indices = np.arange(len(flags))

        logger.info(f"Detected {flags.sum()} anomalies out of {len(flags)} samples")
        return scores, flags, indices

    def classify(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Classify anomalies into issue types.

        Args:
            features: Feature matrix from anomalies

        Returns:
            Tuple of (issue_types, confidences)
        """
        logger.info(f"Classifying {len(features)} anomalies")
        predictions, confidences = self.classifier.predict(features)
        return predictions, confidences

    def respond(self, issue_type: str, target: str, confidence: float) -> List[Dict]:
        """
        Execute remediation actions.

        Args:
            issue_type: Type of issue
            target: Target system
            confidence: Confidence score

        Returns:
            List of executed actions
        """
        logger.info(f"Executing remediation for {issue_type} on {target}")
        actions = self.responder.execute_remediation(issue_type, target, confidence)
        return actions

    def run_analysis(self, data_source: str = 'smd', machine_id: str = 'machine-1-1') -> Dict:
        """
        Run complete end-to-end analysis.

        Args:
            data_source: 'smd' or 'aiops'
            machine_id: Machine to analyze

        Returns:
            Analysis results dictionary
        """
        logger.info(f"Running complete analysis on {machine_id}")
        start_time = datetime.now()

        # Prepare data
        X_train_scaled, X_val_scaled, X_test_scaled, test_df = self.prepare_data(data_source, machine_id)

        # Train model
        optimal_threshold = self.train(X_train_scaled, X_val_scaled)

        # Detect anomalies
        scores, flags, indices = self.detect(X_test_scaled)

        # Get anomaly indices
        anomaly_indices = indices[flags == 1]
        anomaly_count = len(anomaly_indices)

        # Classify if anomalies found
        alerts = []
        if anomaly_count > 0:
            anomaly_features = X_test_scaled[anomaly_indices]
            issue_types, confidences = self.classify(anomaly_features)

            # Generate alerts
            for idx, issue_type_id, confidence in zip(anomaly_indices, issue_types, confidences):
                issue_type_names = {0: 'performance_degradation', 1: 'service_outage', 2: 'resource_exhaustion', 3: 'unknown'}
                issue_type = issue_type_names.get(issue_type_id, 'unknown')

                alert = self.alert_generator.generate_alert(
                    issue_type=issue_type,
                    confidence=confidence,
                    target=machine_id,
                    correlated_metrics=[],
                    auto_remediated=False
                )
                alerts.append(alert)

        elapsed = (datetime.now() - start_time).total_seconds()

        results = {
            'machine_id': machine_id,
            'total_records': len(test_df),
            'anomalies_detected': anomaly_count,
            'alerts_generated': len(alerts),
            'execution_time_seconds': elapsed,
            'optimal_threshold': optimal_threshold,
            'anomaly_scores': scores,
            'anomaly_flags': flags,
            'alerts': alerts
        }

        logger.info(f"Analysis complete in {elapsed:.2f}s: {anomaly_count} anomalies detected")
        return results
