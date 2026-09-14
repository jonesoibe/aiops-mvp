"""
SLO Compliance Calculator
Real-time calculation and tracking of SLO compliance metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and aggregates metrics for SLO calculation"""

    def __init__(self, window_size: int = 3600):
        """
        Args:
            window_size: Time window in seconds for aggregation
        """
        self.window_size = window_size
        self.metrics: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self.requests: Dict[str, Dict] = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'latencies': []
        })

    def record_metric(self, service_id: str, metric_name: str, value: float) -> None:
        """Record a metric value"""
        key = f"{service_id}_{metric_name}"
        self.metrics[key].append((datetime.utcnow(), value))

        # Clean old entries outside window
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_size)
        self.metrics[key] = [
            (ts, val) for ts, val in self.metrics[key]
            if ts >= cutoff
        ]

    def record_request(self, service_id: str, duration_ms: float,
                      success: bool) -> None:
        """Record a request (for availability/error rate calculation)"""
        req = self.requests[service_id]
        req['total'] += 1

        if success:
            req['successful'] += 1
        else:
            req['failed'] += 1

        req['latencies'].append(duration_ms)

        # Keep only recent latencies (last 1000)
        if len(req['latencies']) > 1000:
            req['latencies'] = req['latencies'][-1000:]

    def get_percentile(self, service_id: str, percentile: float) -> Optional[float]:
        """Calculate percentile latency (e.g., P95, P99)"""
        latencies = self.requests[service_id].get('latencies', [])

        if not latencies:
            return None

        sorted_latencies = sorted(latencies)
        index = int((percentile / 100) * len(sorted_latencies))
        index = min(index, len(sorted_latencies) - 1)

        return sorted_latencies[index]

    def get_availability(self, service_id: str) -> float:
        """Get availability percentage"""
        req = self.requests[service_id]

        if req['total'] == 0:
            return 100.0

        return (req['successful'] / req['total']) * 100

    def get_error_rate(self, service_id: str) -> float:
        """Get error rate percentage"""
        req = self.requests[service_id]

        if req['total'] == 0:
            return 0.0

        return (req['failed'] / req['total']) * 100

    def get_average_latency(self, service_id: str) -> Optional[float]:
        """Get average latency"""
        latencies = self.requests[service_id].get('latencies', [])

        if not latencies:
            return None

        return sum(latencies) / len(latencies)

    def get_service_metrics(self, service_id: str) -> Dict:
        """Get all calculated metrics for a service"""
        return {
            'availability': round(self.get_availability(service_id), 2),
            'error_rate': round(self.get_error_rate(service_id), 2),
            'p50_latency': self.get_percentile(service_id, 50),
            'p95_latency': self.get_percentile(service_id, 95),
            'p99_latency': self.get_percentile(service_id, 99),
            'avg_latency': self.get_average_latency(service_id),
            'total_requests': self.requests[service_id]['total'],
            'failed_requests': self.requests[service_id]['failed']
        }

    def reset_service(self, service_id: str) -> None:
        """Reset metrics for a service"""
        if service_id in self.requests:
            self.requests[service_id] = {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'latencies': []
            }


class ErrorBudgetTracker:
    """Tracks error budget consumption and burndown"""

    def __init__(self):
        self.budgets: Dict[str, Dict] = {}  # slo_id -> budget info

    def initialize_budget(self, slo_id: str, period_seconds: int,
                         target_percentage: float) -> None:
        """Initialize error budget for an SLO"""
        total_seconds = period_seconds
        target_seconds = total_seconds * (target_percentage / 100)
        error_budget = total_seconds - target_seconds

        self.budgets[slo_id] = {
            'total': error_budget,
            'remaining': error_budget,
            'consumed': 0,
            'burndown_rate': 0,  # errors per second
            'last_update': datetime.utcnow()
        }

    def consume_budget(self, slo_id: str, error_seconds: float) -> Dict:
        """Consume error budget"""
        if slo_id not in self.budgets:
            return {}

        budget = self.budgets[slo_id]
        budget['consumed'] += error_seconds
        budget['remaining'] = max(0, budget['total'] - budget['consumed'])
        budget['last_update'] = datetime.utcnow()

        # Calculate burndown rate
        time_elapsed = (datetime.utcnow() - budget['last_update']).total_seconds()
        if time_elapsed > 0:
            budget['burndown_rate'] = budget['consumed'] / time_elapsed

        return self.get_budget_status(slo_id)

    def get_budget_status(self, slo_id: str) -> Dict:
        """Get current budget status"""
        if slo_id not in self.budgets:
            return {}

        budget = self.budgets[slo_id]
        total = budget['total']
        remaining = budget['remaining']
        consumed_pct = (budget['consumed'] / total * 100) if total > 0 else 0

        return {
            'slo_id': slo_id,
            'total_budget': round(total, 2),
            'remaining_budget': round(remaining, 2),
            'consumed_budget': round(budget['consumed'], 2),
            'consumed_percentage': round(consumed_pct, 2),
            'burndown_rate': round(budget['burndown_rate'], 4),
            'last_update': budget['last_update'].isoformat()
        }

    def get_all_budgets(self) -> List[Dict]:
        """Get status of all error budgets"""
        return [self.get_budget_status(slo_id) for slo_id in self.budgets]


class SLOComplianceCalculator:
    """Calculate SLO compliance based on metrics"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.error_budget_tracker = ErrorBudgetTracker()

    def evaluate_slo(self, slo, metric_values: Dict[str, float]) -> Dict:
        """Evaluate if service meets SLO based on metrics"""
        results = {
            'slo_id': slo.id,
            'service_id': slo.service_id,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics_evaluated': [],
            'overall_compliance': True,
            'issues': []
        }

        # Evaluate each metric
        for metric in slo.metrics:
            if metric.name not in metric_values:
                results['issues'].append(f"Metric '{metric.name}' not found")
                continue

            value = metric_values[metric.name]
            meets_threshold = metric.check_condition(value)

            metric_result = {
                'name': metric.name,
                'value': value,
                'threshold': metric.threshold,
                'comparison': metric.comparison,
                'meets_threshold': meets_threshold
            }
            results['metrics_evaluated'].append(metric_result)

            if not meets_threshold:
                results['overall_compliance'] = False
                results['issues'].append(
                    f"Metric '{metric.name}': {value} {metric.comparison} {metric.threshold} failed"
                )

        return results

    def calculate_trend(self, compliance_history: List[Dict]) -> Dict:
        """Calculate compliance trend"""
        if len(compliance_history) < 2:
            return {'trend': 'insufficient_data'}

        recent = [r.compliance_percentage for r in compliance_history[-10:]]
        older = [r.compliance_percentage for r in compliance_history[-20:-10]]

        recent_avg = sum(recent) / len(recent) if recent else 0
        older_avg = sum(older) / len(older) if older else 0

        trend_value = recent_avg - older_avg

        if trend_value > 1:
            trend = 'improving'
        elif trend_value < -1:
            trend = 'degrading'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'trend_value': round(trend_value, 2),
            'recent_average': round(recent_avg, 2),
            'older_average': round(older_avg, 2)
        }

    def forecast_breach(self, slo, compliance_history: List[Dict],
                       hours_ahead: int = 24) -> Dict:
        """Forecast if SLO will be breached"""
        if len(compliance_history) < 5:
            return {'forecast': 'insufficient_data'}

        recent_values = [r.compliance_percentage for r in compliance_history[-10:]]

        # Simple linear regression forecast
        n = len(recent_values)
        x_sum = sum(range(n))
        y_sum = sum(recent_values)
        xy_sum = sum(i * recent_values[i] for i in range(n))
        x2_sum = sum(i**2 for i in range(n))

        # Slope calculation
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum**2) if (n * x2_sum - x_sum**2) != 0 else 0
        intercept = (y_sum - slope * x_sum) / n if n > 0 else 0

        # Forecast at hours_ahead
        forecast_value = intercept + slope * (n + hours_ahead)

        will_breach = forecast_value < slo.target_percentage

        return {
            'forecast': 'will_breach' if will_breach else 'will_meet',
            'forecasted_compliance': round(forecast_value, 2),
            'target': slo.target_percentage,
            'hours_ahead': hours_ahead,
            'confidence': 'low' if len(recent_values) < 10 else 'medium' if len(recent_values) < 50 else 'high'
        }
