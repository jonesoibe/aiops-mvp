"""
Real-time Metrics Simulator - Generates Prometheus-compatible metrics
Simulates realistic system behavior with anomalies, trends, and seasonality
"""

import time
import random
import math
from datetime import datetime, timedelta
from threading import Thread
from typing import Dict, List, Tuple

class MetricsSimulator:
    """Generate realistic system metrics with anomalies and trends."""

    def __init__(self):
        self.metrics = {}
        self.anomalies = {}
        self.initialize_metrics()
        self.running = False
        self.update_interval = 5  # Update every 5 seconds

    def initialize_metrics(self):
        """Initialize metric data structures."""
        self.metrics = {
            # CPU metrics
            'cpu_usage': {'value': 25, 'min': 5, 'max': 90, 'trend': 0.5},
            'cpu_cores': {'value': 4, 'min': 4, 'max': 4},

            # Memory metrics
            'memory_usage': {'value': 45, 'min': 20, 'max': 90, 'trend': 0.3},
            'memory_total_gb': {'value': 16, 'min': 16, 'max': 16},

            # Disk metrics
            'disk_usage': {'value': 55, 'min': 30, 'max': 95, 'trend': 0.1},
            'disk_read_rate': {'value': 50, 'min': 10, 'max': 500, 'trend': 0},
            'disk_write_rate': {'value': 30, 'min': 5, 'max': 300, 'trend': 0},

            # Network metrics
            'network_in': {'value': 120, 'min': 50, 'max': 1000, 'trend': 0},
            'network_out': {'value': 80, 'min': 30, 'max': 800, 'trend': 0},
            'network_errors': {'value': 0, 'min': 0, 'max': 100, 'trend': 0},

            # Process metrics
            'process_count': {'value': 142, 'min': 100, 'max': 300, 'trend': 0},
            'open_connections': {'value': 45, 'min': 10, 'max': 500, 'trend': 0.2},

            # Application metrics
            'request_rate': {'value': 500, 'min': 100, 'max': 5000, 'trend': 0.5},
            'response_time_ms': {'value': 150, 'min': 50, 'max': 5000, 'trend': 0},
            'error_rate': {'value': 0.1, 'min': 0, 'max': 10, 'trend': 0},

            # Database metrics
            'db_connections': {'value': 20, 'min': 5, 'max': 100, 'trend': 0.1},
            'db_queries_per_sec': {'value': 250, 'min': 50, 'max': 2000, 'trend': 0},
            'db_query_time_ms': {'value': 45, 'min': 10, 'max': 1000, 'trend': 0},
        }

        self.anomalies = {
            'memory_leak': False,
            'cpu_spike': False,
            'network_latency': False,
            'high_error_rate': False,
        }

    def simulate_anomaly(self, anomaly_type: str, duration: int = 60):
        """Trigger an anomaly for specified duration (seconds)."""
        self.anomalies[anomaly_type] = True
        Thread(
            target=self._reset_anomaly_after,
            args=(anomaly_type, duration)
        ).start()

    def _reset_anomaly_after(self, anomaly_type: str, duration: int):
        """Reset anomaly after duration."""
        time.sleep(duration)
        self.anomalies[anomaly_type] = False

    def update_metrics(self) -> Dict:
        """Update all metrics with realistic changes."""
        timestamp = datetime.utcnow()
        updated_metrics = {}

        # Get hour for seasonality (higher traffic during business hours)
        hour = timestamp.hour
        business_hour_factor = 1 + (0.5 if 9 <= hour <= 17 else 0)

        for metric_name, metric_data in self.metrics.items():
            current = metric_data['value']
            trend = metric_data.get('trend', 0)
            min_val = metric_data['min']
            max_val = metric_data['max']

            # Add trend (gradual change over time)
            change = random.gauss(trend, 1)

            # Add seasonality for request-based metrics
            if 'request' in metric_name or 'query' in metric_name:
                change *= business_hour_factor

            # Apply anomalies
            if self.anomalies['memory_leak'] and 'memory' in metric_name:
                change += 5  # Memory increases faster

            if self.anomalies['cpu_spike'] and 'cpu' in metric_name:
                change += random.uniform(10, 20)  # CPU spikes

            if self.anomalies['network_latency'] and 'response_time' in metric_name:
                change += random.uniform(50, 200)  # Response time increases

            if self.anomalies['high_error_rate'] and 'error' in metric_name:
                change += random.uniform(2, 5)  # Error rate increases

            # Add random noise
            noise = random.gauss(0, metric_data.get('noise', 2))
            new_value = current + change + noise

            # Clamp to min/max
            new_value = max(min_val, min(max_val, new_value))

            # Update metric
            self.metrics[metric_name]['value'] = new_value

            # Store for return
            updated_metrics[metric_name] = {
                'value': round(new_value, 2),
                'unit': self._get_unit(metric_name),
                'timestamp': timestamp.isoformat(),
                'status': self._get_status(metric_name, new_value, max_val)
            }

        return updated_metrics

    def _get_unit(self, metric_name: str) -> str:
        """Get unit for metric."""
        if 'percent' in metric_name or 'usage' in metric_name or 'rate' in metric_name:
            if 'error_rate' in metric_name:
                return '%'
            return '%'
        elif 'ms' in metric_name:
            return 'ms'
        elif 'gb' in metric_name:
            return 'GB'
        elif 'rate' in metric_name:
            return 'ops/sec'
        return ''

    def _get_status(self, metric_name: str, value: float, max_val: float) -> str:
        """Determine metric status."""
        threshold_critical = max_val * 0.9
        threshold_warning = max_val * 0.7

        if value >= threshold_critical:
            return 'critical'
        elif value >= threshold_warning:
            return 'warning'
        else:
            return 'healthy'

    def get_metrics_snapshot(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            name: {
                'value': data['value'],
                'unit': self._get_unit(name),
                'status': self._get_status(name, data['value'], data['max'])
            }
            for name, data in self.metrics.items()
        }

    def get_prometheus_format(self) -> str:
        """Get metrics in Prometheus text format."""
        lines = []
        timestamp_ms = int(datetime.utcnow().timestamp() * 1000)

        for metric_name, metric_data in self.metrics.items():
            value = metric_data['value']
            lines.append(f"nexus_{metric_name} {value} {timestamp_ms}")

        return '\n'.join(lines) + '\n'

    def get_recent_history(self, metric_name: str, minutes: int = 60) -> List[Tuple]:
        """Get historical data for a metric."""
        # This would normally pull from database
        # For now, generate synthetic history
        history = []
        now = datetime.utcnow()

        current_value = self.metrics[metric_name]['value']

        for i in range(minutes):
            timestamp = now - timedelta(minutes=minutes-i)
            # Add variance to simulate history
            variance = random.gauss(0, 5)
            value = current_value + variance
            history.append({
                'timestamp': timestamp.isoformat(),
                'value': max(self.metrics[metric_name]['min'],
                           min(self.metrics[metric_name]['max'], value))
            })

        return history


# Global simulator instance
_simulator = None

def get_simulator() -> MetricsSimulator:
    """Get or create global simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = MetricsSimulator()
    return _simulator

def start_metrics_collection():
    """Start background metrics collection."""
    simulator = get_simulator()

    def collect():
        while True:
            try:
                simulator.update_metrics()
                time.sleep(simulator.update_interval)
            except Exception as e:
                print(f"Error updating metrics: {e}")
                time.sleep(1)

    thread = Thread(target=collect, daemon=True)
    thread.start()
    print("✅ Metrics collection started")


if __name__ == '__main__':
    # Test the simulator
    simulator = MetricsSimulator()
    start_metrics_collection()

    print("Starting metrics simulator test...")
    print(f"Initial metrics: {simulator.get_metrics_snapshot()}")

    time.sleep(2)
    print("\nTriggering memory leak anomaly for 10 seconds...")
    simulator.simulate_anomaly('memory_leak', duration=10)

    for i in range(15):
        metrics = simulator.update_metrics()
        print(f"\n[{i+1}] Memory: {metrics['memory_usage']['value']:.1f}%, "
              f"CPU: {metrics['cpu_usage']['value']:.1f}%, "
              f"Anomaly active: {simulator.anomalies['memory_leak']}")
        time.sleep(1)
