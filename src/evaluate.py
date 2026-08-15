"""
Model evaluation module for AIOps MVP.

Computes evaluation metrics:
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion Matrix
- Performance over time
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    auc,
    classification_report
)
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluates anomaly detection and classification models."""

    def __init__(self, config: dict):
        """Initialize evaluator."""
        self.config = config

    def evaluate_detection(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_scores: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Evaluate anomaly detection performance.

        Args:
            y_true: True binary labels (1=anomaly, 0=normal)
            y_pred: Predicted binary labels
            y_scores: Prediction scores/probabilities (optional)

        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating detection performance")

        metrics = {
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }

        # ROC-AUC if scores available
        if y_scores is not None:
            try:
                metrics['roc_auc'] = roc_auc_score(y_true, y_scores)
            except ValueError:
                metrics['roc_auc'] = None

        logger.info(f"Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, F1: {metrics['f1']:.3f}")
        return metrics

    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_scores: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Evaluate issue classification performance.

        Args:
            y_true: True issue type labels
            y_pred: Predicted issue types
            y_scores: Prediction probabilities (optional)

        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating classification performance")

        metrics = {
            'precision_macro': precision_score(y_true, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(y_true, y_pred, average='macro', zero_division=0),
            'f1_macro': f1_score(y_true, y_pred, average='macro', zero_division=0),
            'precision_weighted': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall_weighted': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_weighted': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'classification_report': classification_report(y_true, y_pred, output_dict=True)
        }

        logger.info(f"Macro F1: {metrics['f1_macro']:.3f}, Weighted F1: {metrics['f1_weighted']:.3f}")
        return metrics

    def compute_roc_curve(
        self,
        y_true: np.ndarray,
        y_scores: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Compute ROC curve.

        Args:
            y_true: True binary labels
            y_scores: Prediction scores

        Returns:
            Tuple of (fpr, tpr, auc_score)
        """
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        auc_score = auc(fpr, tpr)
        logger.info(f"ROC-AUC: {auc_score:.3f}")
        return fpr, tpr, auc_score

    def evaluate_temporal(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        timestamps: np.ndarray,
        window_size: int = 1440  # 24 hours for minute-level data
    ) -> pd.DataFrame:
        """
        Evaluate model performance over time windows.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            timestamps: Timestamps
            window_size: Size of evaluation window

        Returns:
            DataFrame with temporal evaluation metrics
        """
        logger.info(f"Evaluating performance in {window_size}-sample windows")

        results = []

        for i in range(0, len(y_true) - window_size, window_size):
            window_true = y_true[i:i + window_size]
            window_pred = y_pred[i:i + window_size]

            result = {
                'window_start': timestamps[i] if isinstance(timestamps, np.ndarray) else i,
                'precision': precision_score(window_true, window_pred, zero_division=0),
                'recall': recall_score(window_true, window_pred, zero_division=0),
                'f1': f1_score(window_true, window_pred, zero_division=0),
                'n_anomalies': (window_true == 1).sum()
            }
            results.append(result)

        df_results = pd.DataFrame(results)
        logger.info(f"Computed metrics for {len(df_results)} time windows")
        return df_results

    def compute_latency_metrics(self, detection_times: np.ndarray) -> Dict:
        """
        Compute detection latency metrics.

        Args:
            detection_times: Array of detection execution times (in seconds)

        Returns:
            Dictionary of latency metrics
        """
        metrics = {
            'min_latency_ms': detection_times.min() * 1000,
            'max_latency_ms': detection_times.max() * 1000,
            'mean_latency_ms': detection_times.mean() * 1000,
            'p95_latency_ms': np.percentile(detection_times, 95) * 1000,
            'p99_latency_ms': np.percentile(detection_times, 99) * 1000
        }

        logger.info(f"Mean latency: {metrics['mean_latency_ms']:.2f}ms, P99: {metrics['p99_latency_ms']:.2f}ms")
        return metrics

    def compute_resource_metrics(self, memory_usage: np.ndarray, cpu_usage: np.ndarray) -> Dict:
        """
        Compute resource utilization metrics.

        Args:
            memory_usage: Memory usage in MB
            cpu_usage: CPU usage in percentage

        Returns:
            Dictionary of resource metrics
        """
        metrics = {
            'mean_memory_mb': memory_usage.mean(),
            'max_memory_mb': memory_usage.max(),
            'mean_cpu_percent': cpu_usage.mean(),
            'max_cpu_percent': cpu_usage.max()
        }

        logger.info(f"Resource usage - Memory: {metrics['mean_memory_mb']:.1f}MB, CPU: {metrics['mean_cpu_percent']:.1f}%")
        return metrics

    def generate_evaluation_report(
        self,
        detection_metrics: Dict,
        classification_metrics: Dict,
        latency_metrics: Dict,
        resource_metrics: Dict,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive evaluation report.

        Args:
            detection_metrics: Anomaly detection metrics
            classification_metrics: Issue classification metrics
            latency_metrics: Detection latency metrics
            resource_metrics: Resource utilization metrics
            output_file: Optional file to save report

        Returns:
            Complete evaluation report
        """
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'detection_metrics': detection_metrics,
            'classification_metrics': classification_metrics,
            'latency_metrics': latency_metrics,
            'resource_metrics': resource_metrics
        }

        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Evaluation report saved to {output_file}")

        return report

    def compare_models(
        self,
        models_results: Dict[str, Dict],
        metric_name: str = 'f1'
    ) -> pd.DataFrame:
        """
        Compare performance of different models.

        Args:
            models_results: Dictionary mapping model names to their metrics
            metric_name: Metric to use for comparison

        Returns:
            DataFrame comparing models
        """
        comparison = []

        for model_name, metrics in models_results.items():
            comparison.append({
                'model': model_name,
                metric_name: metrics.get(metric_name, np.nan)
            })

        df_comparison = pd.DataFrame(comparison).sort_values(metric_name, ascending=False)
        logger.info(f"Model comparison by {metric_name}:\n{df_comparison}")

        return df_comparison
