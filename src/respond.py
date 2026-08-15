"""
Response/Remediation module for AIOps MVP.

Handles automated and manual responses to detected issues:
- Remediation action execution
- Alert generation
- Recovery monitoring
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RemediationAction(Enum):
    """Possible remediation actions."""
    RESTART_SERVICE = "restart_service"
    SCALE_UP_REPLICAS = "scale_up_replicas"
    CLEAR_CACHE = "clear_cache"
    INCREASE_CONNECTION_POOL = "increase_connection_pool"
    FAILOVER = "failover"
    MANUAL_INVESTIGATION = "manual_investigation"


class ResponseExecutor:
    """Executes remediation actions in response to detected issues."""

    def __init__(self, config: dict):
        """Initialize response executor."""
        self.config = config
        self.simulate_only = config['response']['simulate_only']
        self.recovery_window = config['response']['recovery_window_seconds']
        self.executed_actions = []
        logger.info(f"Initialized ResponseExecutor (simulate_only={self.simulate_only})")

    def map_issue_to_actions(self, issue_type: str, confidence: float) -> List[RemediationAction]:
        """
        Map issue type to recommended remediation actions.

        Args:
            issue_type: Type of issue detected
            confidence: Confidence score (0-1)

        Returns:
            List of recommended actions
        """
        action_map = {
            'performance_degradation': [
                RemediationAction.CLEAR_CACHE,
                RemediationAction.INCREASE_CONNECTION_POOL,
                RemediationAction.RESTART_SERVICE
            ],
            'service_outage': [
                RemediationAction.RESTART_SERVICE,
                RemediationAction.FAILOVER,
                RemediationAction.MANUAL_INVESTIGATION
            ],
            'resource_exhaustion': [
                RemediationAction.SCALE_UP_REPLICAS,
                RemediationAction.INCREASE_CONNECTION_POOL
            ],
            'network_issue': [
                RemediationAction.FAILOVER,
                RemediationAction.MANUAL_INVESTIGATION
            ]
        }

        actions = action_map.get(issue_type, [RemediationAction.MANUAL_INVESTIGATION])

        # Prioritize actions based on confidence
        if confidence < 0.6:
            actions = [RemediationAction.MANUAL_INVESTIGATION]

        logger.info(f"Mapped '{issue_type}' to actions: {[a.value for a in actions]}")
        return actions

    def execute_action(
        self,
        action: RemediationAction,
        target: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Execute a remediation action.

        Args:
            action: The action to execute
            target: Target system/service
            parameters: Additional parameters for the action

        Returns:
            Execution result dictionary
        """
        timestamp = datetime.now()
        result = {
            'action': action.value,
            'target': target,
            'timestamp': timestamp,
            'simulated': self.simulate_only,
            'success': None,
            'message': ''
        }

        if self.simulate_only:
            logger.info(f"[SIMULATION] Would execute {action.value} on {target}")
            result['success'] = True
            result['message'] = f"Simulated execution of {action.value}"
        else:
            try:
                # Actual execution would happen here
                logger.warning(f"[PRODUCTION] Executing {action.value} on {target}")
                result['success'] = True
                result['message'] = f"Successfully executed {action.value}"
            except Exception as e:
                logger.error(f"Failed to execute {action.value}: {str(e)}")
                result['success'] = False
                result['message'] = str(e)

        self.executed_actions.append(result)
        return result

    def execute_remediation(
        self,
        issue_type: str,
        target: str,
        confidence: float
    ) -> List[Dict]:
        """
        Execute full remediation workflow.

        Args:
            issue_type: Type of issue
            target: Target system
            confidence: Confidence score

        Returns:
            List of executed actions
        """
        logger.info(f"Executing remediation for {issue_type} on {target} (conf={confidence:.2f})")

        actions = self.map_issue_to_actions(issue_type, confidence)
        results = []

        for action in actions:
            result = self.execute_action(action, target)
            results.append(result)

        return results

    def get_execution_history(self) -> pd.DataFrame:
        """Get DataFrame of all executed actions."""
        return pd.DataFrame(self.executed_actions)


class RecoveryMonitor:
    """Monitors recovery after remediation actions."""

    def __init__(self, config: dict):
        """Initialize recovery monitor."""
        self.config = config
        self.recovery_window = config['response']['recovery_window_seconds']

    def check_recovery(
        self,
        df: pd.DataFrame,
        anomaly_idx: int,
        remediation_time: datetime,
        anomaly_scores: np.ndarray
    ) -> Dict:
        """
        Check if system recovered after remediation.

        Args:
            df: Metric data
            anomaly_idx: Index of original anomaly
            remediation_time: Time when remediation was executed
            anomaly_scores: Anomaly scores over time

        Returns:
            Recovery status dictionary
        """
        # Calculate recovery window in samples
        recovery_samples = self.recovery_window // 60  # Assuming minute-level data

        # Check metrics after remediation
        recovery_start = anomaly_idx
        recovery_end = min(len(anomaly_scores), anomaly_idx + recovery_samples)

        post_remediation_scores = anomaly_scores[recovery_start:recovery_end]

        # Calculate recovery metrics
        initial_score = anomaly_scores[anomaly_idx]
        avg_score_after = post_remediation_scores.mean()
        max_score_after = post_remediation_scores.max()

        recovered = avg_score_after < initial_score * 0.5

        result = {
            'recovered': recovered,
            'initial_anomaly_score': initial_score,
            'avg_post_remediation_score': avg_score_after,
            'max_post_remediation_score': max_score_after,
            'recovery_time_minutes': (recovery_end - recovery_start),
            'recovery_percentage': ((initial_score - avg_score_after) / initial_score * 100) if initial_score > 0 else 0
        }

        logger.info(f"Recovery check: {result['recovery_percentage']:.1f}% improvement")
        return result


class AlertGenerator:
    """Generates alerts for detected issues."""

    SEVERITY_LEVELS = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }

    def __init__(self, config: dict):
        """Initialize alert generator."""
        self.config = config

    def generate_alert(
        self,
        issue_type: str,
        confidence: float,
        target: str,
        correlated_metrics: List[str],
        auto_remediated: bool = False
    ) -> Dict:
        """
        Generate alert for an issue.

        Args:
            issue_type: Type of issue
            confidence: Confidence score
            target: Affected target
            correlated_metrics: List of correlated metrics
            auto_remediated: Whether auto-remediation was attempted

        Returns:
            Alert dictionary
        """
        # Determine severity based on confidence
        if confidence > 0.9:
            severity = 'critical'
        elif confidence > 0.7:
            severity = 'high'
        elif confidence > 0.5:
            severity = 'medium'
        else:
            severity = 'low'

        alert = {
            'timestamp': datetime.now(),
            'issue_type': issue_type,
            'confidence': confidence,
            'severity': severity,
            'target': target,
            'correlated_metrics': correlated_metrics,
            'auto_remediated': auto_remediated,
            'message': self._generate_message(issue_type, confidence, target)
        }

        logger.warning(f"[{severity.upper()}] {alert['message']}")
        return alert

    def _generate_message(self, issue_type: str, confidence: float, target: str) -> str:
        """Generate human-readable alert message."""
        conf_text = f"{confidence*100:.1f}%"
        return f"{issue_type} detected on {target} (confidence: {conf_text})"
