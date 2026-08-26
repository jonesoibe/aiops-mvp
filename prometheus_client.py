"""
Prometheus-compatible metrics client and storage
Integrates with the metrics simulator and provides API endpoints
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from metrics_simulator import get_simulator


class PrometheusStorage:
    """Store and query metrics in Prometheus-like format."""

    def __init__(self, max_history_points: int = 1000):
        self.max_history = max_history_points
        self.metrics_history = {}  # {metric_name: [{'timestamp': ..., 'value': ...}]}
        self.simulator = get_simulator()

    def record_snapshot(self):
        """Record current metrics to history."""
        simulator = self.simulator
        simulator.update_metrics()

        for metric_name, metric_data in simulator.metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []

            record = {
                'timestamp': datetime.utcnow().isoformat(),
                'value': round(metric_data['value'], 2),
                'status': self._get_status(metric_name, metric_data['value'])
            }

            self.metrics_history[metric_name].append(record)

            # Keep only recent history
            if len(self.metrics_history[metric_name]) > self.max_history:
                self.metrics_history[metric_name].pop(0)

    def get_metric(self, metric_name: str) -> Optional[Dict]:
        """Get current value of a metric."""
        if metric_name not in self.simulator.metrics:
            return None

        metric_data = self.simulator.metrics[metric_name]
        return {
            'name': metric_name,
            'value': round(metric_data['value'], 2),
            'unit': self._get_unit(metric_name),
            'status': self._get_status(metric_name, metric_data['value']),
            'min': metric_data['min'],
            'max': metric_data['max'],
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_all_metrics(self) -> Dict:
        """Get all current metrics."""
        result = {}
        for metric_name in self.simulator.metrics:
            result[metric_name] = self.get_metric(metric_name)
        return result

    def get_metric_history(self, metric_name: str, minutes: int = 60) -> List[Dict]:
        """Get historical data for a metric."""
        if metric_name not in self.metrics_history:
            return []

        history = self.metrics_history[metric_name]

        # Filter to requested time range
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        filtered = [
            h for h in history
            if datetime.fromisoformat(h['timestamp']) >= cutoff_time
        ]

        return filtered

    def get_metrics_by_status(self, status: str) -> Dict:
        """Get all metrics with specific status (healthy/warning/critical)."""
        result = {}
        for metric_name, metric_data in self.simulator.metrics.items():
            metric_status = self._get_status(metric_name, metric_data['value'])
            if metric_status == status:
                result[metric_name] = self.get_metric(metric_name)
        return result

    def _get_unit(self, metric_name: str) -> str:
        """Get unit for metric."""
        if 'usage' in metric_name or 'percent' in metric_name:
            return '%'
        elif 'ms' in metric_name:
            return 'ms'
        elif 'gb' in metric_name:
            return 'GB'
        elif 'rate' in metric_name or 'sec' in metric_name:
            return 'ops/sec'
        elif 'errors' in metric_name:
            return 'count'
        return ''

    def _get_status(self, metric_name: str, value: float) -> str:
        """Determine metric status."""
        if metric_name not in self.simulator.metrics:
            return 'unknown'

        metric_data = self.simulator.metrics[metric_name]
        max_val = metric_data['max']

        # Different thresholds for different metrics
        if 'error' in metric_name:
            if value >= 5:
                return 'critical'
            elif value >= 1:
                return 'warning'
        else:
            threshold_critical = max_val * 0.85
            threshold_warning = max_val * 0.65

            if value >= threshold_critical:
                return 'critical'
            elif value >= threshold_warning:
                return 'warning'

        return 'healthy'

    def get_summary_stats(self) -> Dict:
        """Get summary statistics for dashboard."""
        all_metrics = self.simulator.metrics
        statuses = {'healthy': 0, 'warning': 0, 'critical': 0}

        for metric_name, metric_data in all_metrics.items():
            status = self._get_status(metric_name, metric_data['value'])
            statuses[status] += 1

        return {
            'total_metrics': len(all_metrics),
            'healthy_count': statuses['healthy'],
            'warning_count': statuses['warning'],
            'critical_count': statuses['critical'],
            'healthy_percentage': round(
                (statuses['healthy'] / len(all_metrics) * 100), 1
            ) if all_metrics else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

    def trigger_anomaly(self, anomaly_type: str, duration: int = 60):
        """Trigger an anomaly for testing."""
        if anomaly_type in self.simulator.anomalies:
            self.simulator.simulate_anomaly(anomaly_type, duration)
            return True
        return False

    def get_anomalies(self) -> Dict:
        """Get current anomaly status."""
        return {
            name: active
            for name, active in self.simulator.anomalies.items()
        }

    def export_prometheus_format(self) -> str:
        """Export all metrics in Prometheus text format."""
        lines = []
        timestamp_ms = int(datetime.utcnow().timestamp() * 1000)

        for metric_name, metric_data in self.simulator.metrics.items():
            value = metric_data['value']
            status = self._get_status(metric_name, value)

            # Main metric
            lines.append(f'nexus_{metric_name}{{status="{status}"}} {value} {timestamp_ms}')

        return '\n'.join(lines) + '\n'


# Global storage instance
_storage = None

def get_storage() -> PrometheusStorage:
    """Get or create global storage instance."""
    global _storage
    if _storage is None:
        _storage = PrometheusStorage()
    return _storage

def init_storage():
    """Initialize and start storage."""
    storage = get_storage()

    # Start background recording
    from threading import Thread
    import time

    def record_loop():
        while True:
            try:
                storage.record_snapshot()
                time.sleep(5)  # Record every 5 seconds
            except Exception as e:
                print(f"Error recording metrics: {e}")
                time.sleep(1)

    thread = Thread(target=record_loop, daemon=True)
    thread.start()
    print("✅ Prometheus storage initialized")


if __name__ == '__main__':
    # Test the storage
    init_storage()
    storage = get_storage()

    print("Available metrics:")
    for name, data in storage.get_all_metrics().items():
        print(f"  {name}: {data['value']}{data['unit']} ({data['status']})")

    print("\nSummary stats:")
    print(json.dumps(storage.get_summary_stats(), indent=2))

    print("\nTriggering CPU spike...")
    storage.trigger_anomaly('cpu_spike', duration=30)
