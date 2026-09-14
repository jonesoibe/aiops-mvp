"""
SLO (Service Level Objective) Tracking Engine
Monitors and tracks compliance against defined SLOs
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class SLOMetricType(Enum):
    """Types of metrics tracked for SLOs"""
    AVAILABILITY = "availability"  # Uptime percentage
    LATENCY = "latency"  # Response time (P95, P99)
    ERROR_RATE = "error_rate"  # % of failed requests
    THROUGHPUT = "throughput"  # Requests per second
    CUSTOM = "custom"  # Custom metric


class SLOStatus(Enum):
    """SLO compliance status"""
    HEALTHY = "healthy"  # Meeting SLO
    WARNING = "warning"  # Approaching SLO threshold
    VIOLATED = "violated"  # SLO breached
    NO_DATA = "no_data"  # Insufficient data


class TimePeriod(Enum):
    """SLO tracking periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class SLOMetric:
    """Individual metric within an SLO"""
    name: str
    metric_type: SLOMetricType
    threshold: float
    comparison: str  # "<", "<=", ">", ">=", "=="
    window: int  # Time window in seconds (e.g., 300 for P95)
    weight: float = 1.0  # Importance weight (0-1)

    def check_condition(self, value: float) -> bool:
        """Check if metric value meets the threshold"""
        if self.comparison == "<":
            return value < self.threshold
        elif self.comparison == "<=":
            return value <= self.threshold
        elif self.comparison == ">":
            return value > self.threshold
        elif self.comparison == ">=":
            return value >= self.threshold
        elif self.comparison == "==":
            return value == self.threshold
        return False


@dataclass
class ServiceLevelObjective:
    """Defines an SLO for a service"""
    id: str
    service_id: str
    service_name: str
    description: str
    metrics: List[SLOMetric]  # Target metrics
    target_percentage: float  # e.g., 99.9 (%)
    tracking_period: TimePeriod
    period_start: datetime
    period_end: datetime
    enabled: bool = True
    error_budget_threshold: float = 0.3  # Alert when 30% of error budget used
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        """Check if SLO is currently active"""
        now = datetime.utcnow()
        return self.enabled and self.period_start <= now <= self.period_end

    def days_remaining(self) -> int:
        """Days left in tracking period"""
        remaining = self.period_end - datetime.utcnow()
        return max(0, remaining.days)

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'service_name': self.service_name,
            'description': self.description,
            'metrics': [
                {
                    'name': m.name,
                    'metric_type': m.metric_type.value,
                    'threshold': m.threshold,
                    'comparison': m.comparison,
                    'window': m.window,
                    'weight': m.weight
                }
                for m in self.metrics
            ],
            'target_percentage': self.target_percentage,
            'tracking_period': self.tracking_period.value,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'enabled': self.enabled,
            'error_budget_threshold': self.error_budget_threshold,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class SLOComplianceRecord:
    """Record of SLO compliance at a point in time"""
    slo_id: str
    service_id: str
    timestamp: datetime
    compliance_percentage: float  # 0-100
    status: SLOStatus
    error_budget_remaining: float  # % of error budget left
    errors_count: int
    total_requests: int
    details: Dict = field(default_factory=dict)

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            'slo_id': self.slo_id,
            'service_id': self.service_id,
            'timestamp': self.timestamp.isoformat(),
            'compliance_percentage': round(self.compliance_percentage, 2),
            'status': self.status.value,
            'error_budget_remaining': round(self.error_budget_remaining, 2),
            'errors_count': self.errors_count,
            'total_requests': self.total_requests,
            'details': self.details
        }


class SLOEngine:
    """Core SLO tracking and compliance calculation engine"""

    def __init__(self):
        self.slos: Dict[str, ServiceLevelObjective] = {}
        self.compliance_history: List[SLOComplianceRecord] = []
        self.max_history = 10000  # Limit history size

    def add_slo(self, slo: ServiceLevelObjective) -> bool:
        """Add a new SLO"""
        if slo.id in self.slos:
            logger.warning(f"SLO {slo.id} already exists")
            return False

        self.slos[slo.id] = slo
        logger.info(f"✅ Added SLO: {slo.service_name} ({slo.id})")
        return True

    def update_slo(self, slo_id: str, **kwargs) -> Optional[ServiceLevelObjective]:
        """Update an SLO"""
        if slo_id not in self.slos:
            logger.warning(f"SLO {slo_id} not found")
            return None

        slo = self.slos[slo_id]
        for key, value in kwargs.items():
            if hasattr(slo, key):
                setattr(slo, key, value)

        logger.info(f"✅ Updated SLO: {slo_id}")
        return slo

    def delete_slo(self, slo_id: str) -> bool:
        """Delete an SLO"""
        if slo_id not in self.slos:
            return False

        del self.slos[slo_id]
        logger.info(f"✅ Deleted SLO: {slo_id}")
        return True

    def get_slo(self, slo_id: str) -> Optional[ServiceLevelObjective]:
        """Get a specific SLO"""
        return self.slos.get(slo_id)

    def get_slos(self, service_id: Optional[str] = None,
                 enabled_only: bool = False) -> List[ServiceLevelObjective]:
        """Get SLOs, optionally filtered by service"""
        slos = list(self.slos.values())

        if service_id:
            slos = [s for s in slos if s.service_id == service_id]

        if enabled_only:
            slos = [s for s in slos if s.enabled]

        return slos

    def record_compliance(self, record: SLOComplianceRecord) -> None:
        """Record a compliance measurement"""
        self.compliance_history.append(record)

        # Maintain history size limit
        if len(self.compliance_history) > self.max_history:
            self.compliance_history = self.compliance_history[-self.max_history:]

    def calculate_compliance(
        self,
        slo_id: str,
        errors_count: int,
        total_requests: int,
        metric_values: Dict[str, float]
    ) -> Optional[SLOComplianceRecord]:
        """Calculate current compliance for an SLO"""
        slo = self.get_slo(slo_id)
        if not slo or not slo.is_active():
            return None

        # Calculate availability (uptime)
        availability = 100.0
        if total_requests > 0:
            availability = ((total_requests - errors_count) / total_requests) * 100

        # Check if meeting SLO
        meets_slo = availability >= slo.target_percentage

        # Determine status
        if meets_slo:
            status = SLOStatus.HEALTHY
        elif availability >= (slo.target_percentage * 0.95):
            status = SLOStatus.WARNING
        else:
            status = SLOStatus.VIOLATED

        # Calculate error budget
        # Error budget = total time available - (target time * SLO target)
        period_seconds = (slo.period_end - slo.period_start).total_seconds()
        target_seconds = period_seconds * (slo.target_percentage / 100)
        error_budget_seconds = period_seconds - target_seconds

        # Actual errors (in seconds equivalent)
        actual_error_seconds = (errors_count / total_requests) * period_seconds if total_requests > 0 else 0
        error_budget_remaining = max(0, error_budget_seconds - actual_error_seconds)
        error_budget_remaining_pct = (error_budget_remaining / error_budget_seconds * 100) if error_budget_seconds > 0 else 100

        record = SLOComplianceRecord(
            slo_id=slo_id,
            service_id=slo.service_id,
            timestamp=datetime.utcnow(),
            compliance_percentage=availability,
            status=status,
            error_budget_remaining=error_budget_remaining_pct,
            errors_count=errors_count,
            total_requests=total_requests,
            details={
                'target_percentage': slo.target_percentage,
                'availability': round(availability, 2),
                'meets_slo': meets_slo,
                'days_remaining': slo.days_remaining()
            }
        )

        self.record_compliance(record)
        return record

    def get_compliance_history(
        self,
        slo_id: str,
        hours: int = 24
    ) -> List[SLOComplianceRecord]:
        """Get compliance history for an SLO"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            r for r in self.compliance_history
            if r.slo_id == slo_id and r.timestamp >= cutoff
        ]

    def get_compliance_summary(self, slo_id: str) -> Dict:
        """Get summary of SLO compliance"""
        slo = self.get_slo(slo_id)
        if not slo:
            return {}

        history = self.get_compliance_history(slo_id, hours=720)  # Last 30 days

        if not history:
            return {
                'slo_id': slo_id,
                'status': SLOStatus.NO_DATA.value,
                'message': 'No compliance data available'
            }

        # Calculate statistics
        compliances = [r.compliance_percentage for r in history]
        avg_compliance = sum(compliances) / len(compliances)
        min_compliance = min(compliances)
        max_compliance = max(compliances)

        # Count violations
        violations = sum(1 for r in history if r.status == SLOStatus.VIOLATED)

        # Latest record
        latest = history[-1]

        return {
            'slo_id': slo_id,
            'service_name': slo.service_name,
            'target_percentage': slo.target_percentage,
            'average_compliance': round(avg_compliance, 2),
            'min_compliance': round(min_compliance, 2),
            'max_compliance': round(max_compliance, 2),
            'violations': violations,
            'status': latest.status.value,
            'error_budget_remaining': round(latest.error_budget_remaining, 2),
            'days_remaining': slo.days_remaining(),
            'last_updated': latest.timestamp.isoformat()
        }

    def get_statistics(self) -> Dict:
        """Get overall SLO statistics"""
        slos = self.get_slos()
        active_slos = [s for s in slos if s.is_active()]

        # Calculate status counts
        status_counts = {
            'healthy': 0,
            'warning': 0,
            'violated': 0,
            'no_data': 0
        }

        for slo in active_slos:
            summary = self.get_compliance_summary(slo.id)
            status = summary.get('status', 'no_data')
            status_counts[status] += 1

        return {
            'total_slos': len(slos),
            'active_slos': len(active_slos),
            'status_counts': status_counts,
            'compliance_records': len(self.compliance_history),
            'largest_error_budget': self._find_largest_error_budget()
        }

    def _find_largest_error_budget(self) -> float:
        """Find service with largest remaining error budget"""
        max_budget = 0.0

        for slo in self.get_slos(enabled_only=True):
            summary = self.get_compliance_summary(slo.id)
            if 'error_budget_remaining' in summary:
                max_budget = max(max_budget, summary['error_budget_remaining'])

        return round(max_budget, 2)
