"""
AIOps MVP - Main package.

Modules:
- ingest: Data ingestion from various sources
- preprocess: Data preprocessing and normalization
- detect: Anomaly detection algorithms
- classify: Issue classification
- correlate: Correlation analysis for root cause identification
- respond: Remediation and response actions
- pipeline: Main orchestration pipeline
- evaluate: Model evaluation and metrics
"""

from .ingest import DataIngester
from .preprocess import load_config, engineer_features, normalise_features, time_based_split
from .detect import train_isolation_forest, score_observations, calibrate_threshold
from .classify import IssueClassifier, CorrelationAnalyzer
from .respond import ResponseExecutor, RecoveryMonitor, AlertGenerator
from .evaluate import ModelEvaluator

__version__ = "0.1.0"
__all__ = [
    'DataIngester',
    'load_config',
    'engineer_features',
    'normalise_features',
    'time_based_split',
    'train_isolation_forest',
    'score_observations',
    'calibrate_threshold',
    'IssueClassifier',
    'CorrelationAnalyzer',
    'ResponseExecutor',
    'RecoveryMonitor',
    'AlertGenerator',
    'ModelEvaluator'
]
