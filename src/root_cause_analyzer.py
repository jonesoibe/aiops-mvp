"""
Root Cause Analysis Engine for AIOps
Analyzes alerts and incidents to identify likely root causes
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CauseConfidence(Enum):
    """Confidence level for identified root cause"""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"            # 70-90%
    MEDIUM = "medium"        # 50-70%
    LOW = "low"              # 30-50%


@dataclass
class RootCause:
    """Identified root cause for an incident"""
    cause: str
    description: str
    confidence: float  # 0-1
    evidence: List[str]  # Supporting evidence
    affected_components: List[str]
    remediation_suggestions: List[str]


class RootCauseAnalyzer:
    """Analyzes incidents and alerts to identify root causes"""

    def __init__(self):
        self.historical_incidents = []
        self.metric_baselines = {}
        self.dependency_graph = {}

    def analyze_incident(
        self,
        alert,
        metrics_history: Dict[str, List[Tuple[datetime, float]]],
        service_topology: Dict = None
    ) -> List[RootCause]:
        """
        Analyze an incident and identify likely root causes.

        Args:
            alert: The alert that triggered
            metrics_history: Historical metric data
            service_topology: Service dependency information

        Returns:
            List of identified root causes, ranked by confidence
        """
        causes = []

        # Analyze direct cause
        direct_cause = self._analyze_direct_cause(alert, metrics_history)
        if direct_cause:
            causes.append(direct_cause)

        # Analyze upstream dependencies
        if service_topology:
            upstream_causes = self._analyze_upstream_dependencies(
                alert.service_id,
                metrics_history,
                service_topology
            )
            causes.extend(upstream_causes)

        # Analyze temporal patterns
        temporal_causes = self._analyze_temporal_patterns(alert, metrics_history)
        causes.extend(temporal_causes)

        # Rank by confidence
        causes.sort(key=lambda c: c.confidence, reverse=True)

        return causes[:5]  # Return top 5 causes

    def _analyze_direct_cause(
        self,
        alert,
        metrics_history: Dict[str, List[Tuple[datetime, float]]]
    ) -> Optional[RootCause]:
        """Analyze the direct cause of the alert"""

        metric_key = f"{alert.service_id}_{alert.metric_name}"

        if metric_key not in metrics_history:
            return None

        history = metrics_history[metric_key]
        if len(history) < 2:
            return None

        # Extract timestamps and values
        times = [t for t, v in history]
        values = [v for t, v in history]

        # Calculate trend
        if len(values) >= 2:
            recent_value = values[-1]
            previous_value = values[-2]
            trend = "increasing" if recent_value > previous_value else "decreasing"
        else:
            trend = "stable"

        # Determine cause based on metric name and trend
        if alert.metric_name == "cpu_usage":
            if recent_value > 90:
                return RootCause(
                    cause="High CPU Utilization",
                    description="CPU usage exceeded safe thresholds",
                    confidence=0.85,
                    evidence=[
                        f"CPU at {recent_value:.1f}% (threshold: {alert.threshold}%)",
                        f"Trend: {trend}",
                        f"Sustained for {alert.duration_seconds}s"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Identify resource-intensive processes",
                        "Consider horizontal scaling",
                        "Optimize application code",
                        "Check for memory leaks causing GC spikes"
                    ]
                )

        elif alert.metric_name == "memory_usage":
            if recent_value > 85:
                return RootCause(
                    cause="Memory Pressure",
                    description="Memory usage exceeds safe levels",
                    confidence=0.80,
                    evidence=[
                        f"Memory at {recent_value:.1f}% (threshold: {alert.threshold}%)",
                        f"Trend: {trend}"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Restart service to free memory",
                        "Profile application for memory leaks",
                        "Increase allocated memory",
                        "Review caching strategies"
                    ]
                )

        elif alert.metric_name == "error_rate":
            if recent_value > 5:
                return RootCause(
                    cause="High Error Rate",
                    description="Service is experiencing elevated errors",
                    confidence=0.75,
                    evidence=[
                        f"Error rate at {recent_value:.2f}% (threshold: {alert.threshold}%)",
                        f"Trend: {trend}"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Check application logs for error patterns",
                        "Review recent code deployments",
                        "Verify external service dependencies",
                        "Check database connectivity"
                    ]
                )

        elif alert.metric_name == "response_time_p95":
            if recent_value > 500:
                return RootCause(
                    cause="Latency Degradation",
                    description="Response time has increased significantly",
                    confidence=0.70,
                    evidence=[
                        f"P95 latency at {recent_value:.0f}ms (threshold: {alert.threshold}ms)",
                        f"Trend: {trend}"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Check database query performance",
                        "Review cache hit rates",
                        "Identify slow endpoints via profiling",
                        "Check network conditions"
                    ]
                )

        return None

    def _analyze_upstream_dependencies(
        self,
        service_id: str,
        metrics_history: Dict[str, List[Tuple[datetime, float]]],
        service_topology: Dict
    ) -> List[RootCause]:
        """Analyze if upstream service failures caused this alert"""

        causes = []

        # Find upstream services
        if service_id not in service_topology.get('dependencies', {}):
            return causes

        upstream_services = service_topology['dependencies'][service_id]

        for upstream_service in upstream_services:
            # Check if upstream service had issues
            upstream_key = f"{upstream_service}_error_rate"
            if upstream_key in metrics_history:
                history = metrics_history[upstream_key]
                if history and history[-1][1] > 5:  # Error rate > 5%
                    causes.append(RootCause(
                        cause=f"Upstream Service Failure: {upstream_service}",
                        description=f"Upstream service {upstream_service} is failing",
                        confidence=0.60,
                        evidence=[
                            f"{upstream_service} error rate elevated",
                            f"Service {service_id} depends on {upstream_service}",
                            "Cascading failure pattern detected"
                        ],
                        affected_components=[upstream_service, service_id],
                        remediation_suggestions=[
                            f"Investigate {upstream_service} service",
                            "Check network connectivity between services",
                            "Review service dependency health"
                        ]
                    ))

        return causes

    def _analyze_temporal_patterns(
        self,
        alert,
        metrics_history: Dict[str, List[Tuple[datetime, float]]]
    ) -> List[RootCause]:
        """Analyze temporal patterns in metrics"""

        causes = []
        metric_key = f"{alert.service_id}_{alert.metric_name}"

        if metric_key not in metrics_history:
            return causes

        history = metrics_history[metric_key]

        # Check for sudden spikes
        if len(history) >= 3:
            values = [v for t, v in history]
            recent_change = values[-1] - values[-2]

            if abs(recent_change) > values[-2] * 0.5:  # >50% change
                causes.append(RootCause(
                    cause="Sudden Metric Spike",
                    description="Metric changed abruptly",
                    confidence=0.65,
                    evidence=[
                        f"Sudden {recent_change:.1f} point change",
                        f"From {values[-2]:.1f} to {values[-1]:.1f}",
                        "Likely triggered by event or deployment"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Check recent deployments",
                        "Review configuration changes",
                        "Check system logs for events"
                    ]
                ))

        # Check for gradual degradation
        if len(history) >= 10:
            values = [v for t, v in history]
            # Simple linear regression
            avg_value = sum(values) / len(values)
            increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))

            if increasing and values[-1] > avg_value * 1.5:
                causes.append(RootCause(
                    cause="Resource Leak or Gradual Degradation",
                    description="Metrics trending up over time",
                    confidence=0.55,
                    evidence=[
                        f"Metric consistently increasing",
                        f"Current value {values[-1]:.1f} vs average {avg_value:.1f}",
                        "Pattern suggests slow resource exhaustion"
                    ],
                    affected_components=[alert.service_id],
                    remediation_suggestions=[
                        "Profile for memory/connection leaks",
                        "Restart service for fresh state",
                        "Review application logs",
                        "Monitor for memory growth patterns"
                    ]
                ))

        return causes

    def suggest_remediation(self, root_cause: RootCause) -> Dict:
        """Suggest automated remediation actions"""

        recommendations = {
            "manual_steps": root_cause.remediation_suggestions,
            "automated_actions": []
        }

        # Suggest automated actions based on cause
        if "CPU" in root_cause.cause:
            recommendations["automated_actions"].extend([
                {
                    "action": "scale_horizontally",
                    "description": "Add more instances to distribute load",
                    "risk": "medium"
                },
                {
                    "action": "restart_service",
                    "description": "Restart service to clear state",
                    "risk": "low"
                }
            ])

        elif "Memory" in root_cause.cause:
            recommendations["automated_actions"].extend([
                {
                    "action": "restart_service",
                    "description": "Restart service to free memory",
                    "risk": "medium"
                }
            ])

        elif "Error Rate" in root_cause.cause:
            recommendations["automated_actions"].extend([
                {
                    "action": "circuit_breaker",
                    "description": "Enable circuit breaker for failing endpoint",
                    "risk": "medium"
                },
                {
                    "action": "rollback",
                    "description": "Rollback recent deployment",
                    "risk": "high"
                }
            ])

        return recommendations

    def correlate_with_events(
        self,
        alert,
        events: List[Dict]
    ) -> List[str]:
        """Correlate alert with system events"""

        correlated = []

        # Check for recent deployments
        deployments = [e for e in events if e.get('type') == 'deployment']
        if deployments:
            for deployment in deployments:
                if deployment['timestamp'] > (alert.fired_at - timedelta(minutes=30)):
                    correlated.append(f"Recent deployment: {deployment['service']}")

        # Check for configuration changes
        config_changes = [e for e in events if e.get('type') == 'config_change']
        if config_changes:
            for change in config_changes:
                if change['timestamp'] > (alert.fired_at - timedelta(minutes=30)):
                    correlated.append(f"Configuration change: {change['details']}")

        # Check for dependency changes
        dependency_changes = [e for e in events if e.get('type') == 'dependency_change']
        if dependency_changes:
            for change in dependency_changes:
                if change['timestamp'] > (alert.fired_at - timedelta(minutes=30)):
                    correlated.append(f"Dependency change: {change['service']}")

        return correlated
