"""
Real-Time Alerting Engine for AIOps MVP
Evaluates metrics against rules and triggers notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class AlertStatus(Enum):
    """Alert lifecycle states"""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class AlertRule:
    """Defines when to trigger an alert"""
    id: str
    name: str
    description: str
    metric_name: str  # e.g., "cpu_usage", "error_rate", "response_time"
    condition: str  # e.g., ">", "<", "==", "range"
    threshold: float  # e.g., 90 (for CPU > 90%)
    threshold_high: Optional[float] = None  # For range conditions
    duration: int = 300  # Seconds the condition must be true
    severity: AlertSeverity = AlertSeverity.MAJOR
    enabled: bool = True
    notification_channels: List[str] = None  # ['slack', 'email', 'pagerduty']

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ['slack', 'email']


@dataclass
class Alert:
    """An active or resolved alert"""
    id: str
    rule_id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    status: AlertStatus
    service_id: str
    fired_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolution_reason: Optional[str] = None
    notifications_sent: List[str] = None  # ['slack', 'email', ...]

    def __post_init__(self):
        if self.notifications_sent is None:
            self.notifications_sent = []

    @property
    def duration(self) -> timedelta:
        """How long has this alert been firing?"""
        end = self.resolved_at or self.acknowledged_at or datetime.utcnow()
        return end - self.fired_at

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'metric_name': self.metric_name,
            'current_value': round(self.current_value, 2),
            'threshold': self.threshold,
            'severity': self.severity.value,
            'status': self.status.value,
            'service_id': self.service_id,
            'fired_at': self.fired_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_by': self.acknowledged_by,
            'duration_seconds': int(self.duration.total_seconds()),
            'notifications_sent': self.notifications_sent
        }


class AlertingEngine:
    """Evaluates metrics against alert rules and manages alerts"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}  # Active/resolved alerts
        self.alert_history: List[Alert] = []
        self.metric_history: Dict[str, List[Tuple[datetime, float]]] = {}  # Track metric trends
        self.notifier = None  # Will be injected

    # ==================== RULE MANAGEMENT ====================

    def add_rule(self, rule: AlertRule) -> None:
        """Register a new alert rule"""
        self.rules[rule.id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def update_rule(self, rule_id: str, **kwargs) -> None:
        """Update an existing rule"""
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")

        rule = self.rules[rule_id]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        logger.info(f"Updated alert rule: {rule.name}")

    def delete_rule(self, rule_id: str) -> None:
        """Remove a rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Deleted alert rule: {rule_id}")

    def get_rules(self, enabled_only: bool = False) -> List[AlertRule]:
        """Get all rules"""
        rules = list(self.rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    # ==================== METRIC EVALUATION ====================

    def evaluate_metrics(self, service_id: str, metrics: Dict[str, float]) -> List[Alert]:
        """
        Check metrics against all rules, fire/resolve alerts as needed.

        Args:
            service_id: Service being monitored
            metrics: Dict of metric_name -> value pairs

        Returns:
            List of newly fired/resolved alerts
        """
        changed_alerts = []

        for rule in self.get_rules(enabled_only=True):
            metric_key = f"{service_id}_{rule.metric_name}"

            # Track metric history for duration checks
            self._record_metric(metric_key, metrics.get(rule.metric_name, 0))

            # Check if condition is met
            is_breached = self._check_condition(
                metrics.get(rule.metric_name, 0),
                rule.condition,
                rule.threshold,
                rule.threshold_high
            )

            # Check if breach has lasted long enough
            if is_breached:
                recent_breach = self._check_sustained_breach(metric_key, rule.duration)
            else:
                recent_breach = False

            # Find or create alert for this rule/service combo
            alert_key = f"{service_id}_{rule.id}"
            existing_alert = self.alerts.get(alert_key)

            # FIRE: Condition met and sustained
            if recent_breach and not existing_alert:
                alert = Alert(
                    id=alert_key,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    metric_name=rule.metric_name,
                    current_value=metrics.get(rule.metric_name, 0),
                    threshold=rule.threshold,
                    severity=rule.severity,
                    status=AlertStatus.FIRING,
                    service_id=service_id,
                    fired_at=datetime.utcnow()
                )
                self.alerts[alert_key] = alert
                changed_alerts.append(alert)
                logger.warning(f"Alert fired: {rule.name} on {service_id}")

                # Send notifications
                self._send_notifications(alert, rule)

            # RESOLVE: Condition no longer met
            elif not recent_breach and existing_alert and existing_alert.status == AlertStatus.FIRING:
                existing_alert.status = AlertStatus.RESOLVED
                existing_alert.resolved_at = datetime.utcnow()
                self.alert_history.append(existing_alert)
                del self.alerts[alert_key]
                changed_alerts.append(existing_alert)
                logger.info(f"Alert resolved: {rule.name} on {service_id}")

                # Send resolution notification
                self._send_notifications(existing_alert, rule, resolved=True)

        return changed_alerts

    # ==================== CONDITION CHECKING ====================

    def _check_condition(
        self,
        value: float,
        condition: str,
        threshold: float,
        threshold_high: Optional[float] = None
    ) -> bool:
        """
        Check if metric value meets condition.

        Args:
            value: Current metric value
            condition: '>', '<', '>=', '<=', '==', '!=', 'range'
            threshold: Low threshold (or exact value for ==)
            threshold_high: High threshold for range condition

        Returns:
            True if condition is met
        """
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        elif condition == '==':
            return value == threshold
        elif condition == '!=':
            return value != threshold
        elif condition == 'range':
            return threshold <= value <= threshold_high
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False

    def _record_metric(self, metric_key: str, value: float) -> None:
        """Track metric values for trend analysis"""
        if metric_key not in self.metric_history:
            self.metric_history[metric_key] = []

        self.metric_history[metric_key].append((datetime.utcnow(), value))

        # Keep only last hour of data
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.metric_history[metric_key] = [
            (ts, v) for ts, v in self.metric_history[metric_key]
            if ts > cutoff
        ]

    def _check_sustained_breach(self, metric_key: str, duration_seconds: int) -> bool:
        """
        Check if metric has been breached for the required duration.

        Args:
            metric_key: Unique metric identifier
            duration_seconds: Required breach duration

        Returns:
            True if breached for long enough
        """
        if metric_key not in self.metric_history:
            return False

        history = self.metric_history[metric_key]
        if not history:
            return False

        # Check if last N seconds all show breach
        cutoff = datetime.utcnow() - timedelta(seconds=duration_seconds)
        recent = [v for ts, v in history if ts >= cutoff]

        # Need at least a few data points in the window
        return len(recent) >= 3

    # ==================== ALERT MANAGEMENT ====================

    def get_active_alerts(self) -> List[Alert]:
        """Get all currently firing/acknowledged alerts"""
        return [a for a in self.alerts.values() if a.status != AlertStatus.RESOLVED]

    def get_all_alerts(self, limit: int = 100) -> List[Alert]:
        """Get alerts (active + historical)"""
        active = list(self.alerts.values())
        historical = self.alert_history[-limit:]
        return active + historical

    def get_alerts_by_service(self, service_id: str) -> List[Alert]:
        """Get alerts for a specific service"""
        return [a for a in self.get_all_alerts() if a.service_id == service_id]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level"""
        return [a for a in self.get_active_alerts() if a.severity == severity]

    # ==================== ALERT ACTIONS ====================

    def acknowledge_alert(self, alert_id: str, user_id: str) -> Optional[Alert]:
        """
        Mark an alert as acknowledged by a user.

        Args:
            alert_id: Alert to acknowledge
            user_id: User acknowledging the alert

        Returns:
            Updated alert or None if not found
        """
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return alert
        return None

    def silence_alert(self, alert_id: str, duration_minutes: int) -> Optional[Alert]:
        """Temporarily silence an alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.SILENCED
            logger.info(f"Alert {alert_id} silenced for {duration_minutes} minutes")
            return alert
        return None

    def resolve_alert(self, alert_id: str, reason: str) -> Optional[Alert]:
        """Manually resolve an alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolution_reason = reason
            self.alert_history.append(alert)
            del self.alerts[alert_id]
            logger.info(f"Alert {alert_id} resolved: {reason}")
            return alert
        return None

    # ==================== NOTIFICATIONS ====================

    def _send_notifications(self, alert: Alert, rule: AlertRule, resolved: bool = False) -> None:
        """
        Send alert notifications through configured channels.

        Args:
            alert: Alert to notify about
            rule: Rule that triggered the alert
            resolved: Whether this is a resolution notification
        """
        if not self.notifier:
            logger.warning("Notifier not configured, skipping notifications")
            return

        for channel in rule.notification_channels:
            try:
                if resolved:
                    self.notifier.send_resolution(alert, channel)
                else:
                    self.notifier.send_alert(alert, channel)
                alert.notifications_sent.append(channel)
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")

    # ==================== STATISTICS ====================

    def get_statistics(self) -> Dict:
        """Get alerting statistics"""
        active = self.get_active_alerts()
        critical = self.get_alerts_by_severity(AlertSeverity.CRITICAL)
        major = self.get_alerts_by_severity(AlertSeverity.MAJOR)

        return {
            'active_alerts': len(active),
            'critical': len(critical),
            'major': len(major),
            'total_rules': len(self.rules),
            'enabled_rules': len(self.get_rules(enabled_only=True)),
            'total_alerts_fired': len(self.alert_history),
            'avg_resolution_time': self._calculate_avg_resolution_time()
        }

    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average time from firing to resolution"""
        if not self.alert_history:
            return 0

        durations = [a.duration.total_seconds() for a in self.alert_history if a.resolved_at]
        return sum(durations) / len(durations) if durations else 0


# ==================== SINGLETON INSTANCE ====================

alerting_engine = AlertingEngine()


def get_alerting_engine() -> AlertingEngine:
    """Get the global alerting engine instance"""
    return alerting_engine
