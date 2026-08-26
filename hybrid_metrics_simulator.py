"""
Hybrid Metrics Simulator
Blends real system metrics with simulated anomalies
Maintains dashboard anomaly injection capability while using real data
"""

import time
import random
from datetime import datetime
from typing import Dict
from threading import Thread

from metrics_simulator import MetricsSimulator
from real_metrics_collector import RealMetricsCollector


class HybridMetricsSimulator(MetricsSimulator):
    """Combines real system metrics with simulated anomalies"""

    def __init__(self, use_real_metrics=True, use_perfmon=True):
        """Initialize hybrid simulator

        Args:
            use_real_metrics: Use real system metrics (vs pure simulation)
            use_perfmon: Enable Windows Performance Monitor
        """
        super().__init__()
        self.use_real = use_real_metrics
        self.real_collector = RealMetricsCollector(use_perfmon=use_perfmon) if use_real_metrics else None
        self.last_real_metrics = {}

    def update_metrics(self) -> Dict:
        """Update metrics using real data + simulated anomalies

        Process:
        1. Get real metrics from system
        2. Apply anomalies on top of real values
        3. Maintain trend/seasonality for simulated metrics
        """

        if self.use_real and self.real_collector:
            return self._update_with_real_data()
        else:
            return super().update_metrics()

    def _update_with_real_data(self) -> Dict:
        """Update using real system metrics with anomaly overlay"""
        timestamp = datetime.utcnow()
        real_metrics = self.real_collector.get_metrics_snapshot()
        updated_metrics = {}

        # ---- CPU Metrics ----
        if 'cpu_usage' in real_metrics:
            cpu_value = real_metrics['cpu_usage']

            # Apply CPU spike anomaly
            if self.anomalies['cpu_spike']:
                cpu_value += random.uniform(15, 40)  # Spike
                cpu_value = min(cpu_value, 99)  # Cap at 99%

            self.metrics['cpu_usage']['value'] = cpu_value
            updated_metrics['cpu_usage'] = {
                'value': round(cpu_value, 2),
                'unit': '%',
                'timestamp': timestamp.isoformat(),
                'status': self._get_status('cpu_usage', cpu_value, 90)
            }

        # ---- Memory Metrics ----
        if 'memory_usage' in real_metrics:
            mem_value = real_metrics['memory_usage']

            # Apply memory leak anomaly
            if self.anomalies['memory_leak']:
                # Memory leak: gradual increase
                mem_value += random.uniform(0.5, 2.0)
                mem_value = min(mem_value, 99)  # Cap at 99%

            self.metrics['memory_usage']['value'] = mem_value
            updated_metrics['memory_usage'] = {
                'value': round(mem_value, 2),
                'unit': '%',
                'timestamp': timestamp.isoformat(),
                'status': self._get_status('memory_usage', mem_value, 90)
            }

        # ---- Disk Metrics ----
        if 'disk_usage' in real_metrics:
            disk_value = real_metrics['disk_usage']
            self.metrics['disk_usage']['value'] = disk_value
            updated_metrics['disk_usage'] = {
                'value': round(disk_value, 2),
                'unit': '%',
                'timestamp': timestamp.isoformat(),
                'status': self._get_status('disk_usage', disk_value, 95)
            }

        if 'disk_read_rate' in real_metrics:
            read_rate = real_metrics['disk_read_rate']
            self.metrics['disk_read_rate']['value'] = read_rate
            updated_metrics['disk_read_rate'] = {
                'value': round(read_rate, 2),
                'unit': 'MB/s',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        if 'disk_write_rate' in real_metrics:
            write_rate = real_metrics['disk_write_rate']
            self.metrics['disk_write_rate']['value'] = write_rate
            updated_metrics['disk_write_rate'] = {
                'value': round(write_rate, 2),
                'unit': 'MB/s',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        # ---- Network Metrics ----
        if 'network_in' in real_metrics:
            net_in = real_metrics['network_in']
            self.metrics['network_in']['value'] = net_in
            updated_metrics['network_in'] = {
                'value': round(net_in, 2),
                'unit': 'MB/s',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        if 'network_out' in real_metrics:
            net_out = real_metrics['network_out']
            self.metrics['network_out']['value'] = net_out
            updated_metrics['network_out'] = {
                'value': round(net_out, 2),
                'unit': 'MB/s',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        if 'network_errors' in real_metrics:
            net_errors = real_metrics['network_errors']
            self.metrics['network_errors']['value'] = net_errors
            updated_metrics['network_errors'] = {
                'value': round(net_errors, 2),
                'unit': 'count',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy' if net_errors < 5 else 'warning'
            }

        # ---- Process Metrics ----
        if 'process_count' in real_metrics:
            proc_count = real_metrics['process_count']
            self.metrics['process_count']['value'] = proc_count
            updated_metrics['process_count'] = {
                'value': round(proc_count, 0),
                'unit': 'count',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        if 'open_connections' in real_metrics:
            open_conn = real_metrics['open_connections']
            self.metrics['open_connections']['value'] = open_conn
            updated_metrics['open_connections'] = {
                'value': round(open_conn, 0),
                'unit': 'count',
                'timestamp': timestamp.isoformat(),
                'status': 'healthy'
            }

        # ---- Application Metrics (Simulated) ----
        # Request rate
        request_rate = self.metrics['request_rate']['value']
        if random.random() > 0.7:  # Occasional changes
            request_rate += random.gauss(0, 20)
            request_rate = max(100, min(5000, request_rate))
        self.metrics['request_rate']['value'] = request_rate
        updated_metrics['request_rate'] = {
            'value': round(request_rate, 0),
            'unit': 'req/sec',
            'timestamp': timestamp.isoformat(),
            'status': self._get_status('request_rate', request_rate, 5000)
        }

        # Response time
        response_time = self.metrics['response_time_ms']['value']
        if self.anomalies['network_latency']:
            response_time += random.uniform(100, 500)  # Network latency
            response_time = min(5000, response_time)
        else:
            response_time += random.gauss(0, 5)
            response_time = max(50, min(1000, response_time))

        self.metrics['response_time_ms']['value'] = response_time
        updated_metrics['response_time_ms'] = {
            'value': round(response_time, 2),
            'unit': 'ms',
            'timestamp': timestamp.isoformat(),
            'status': self._get_status('response_time_ms', response_time, 5000)
        }

        # Error rate
        error_rate = self.metrics['error_rate']['value']
        if self.anomalies['high_error_rate']:
            error_rate += random.uniform(2, 5)  # High error rate
            error_rate = min(10, error_rate)
        else:
            error_rate += random.gauss(0, 0.1)
            error_rate = max(0, min(1, error_rate))

        self.metrics['error_rate']['value'] = error_rate
        updated_metrics['error_rate'] = {
            'value': round(error_rate, 2),
            'unit': '%',
            'timestamp': timestamp.isoformat(),
            'status': self._get_status('error_rate', error_rate, 10)
        }

        # ---- Database Metrics (Simulated) ----
        db_conn = self.metrics['db_connections']['value']
        db_conn += random.gauss(0, 0.5)
        db_conn = max(5, min(100, db_conn))
        self.metrics['db_connections']['value'] = db_conn
        updated_metrics['db_connections'] = {
            'value': round(db_conn, 0),
            'unit': 'connections',
            'timestamp': timestamp.isoformat(),
            'status': 'healthy'
        }

        db_qps = self.metrics['db_queries_per_sec']['value']
        db_qps += random.gauss(0, 10)
        db_qps = max(50, min(2000, db_qps))
        self.metrics['db_queries_per_sec']['value'] = db_qps
        updated_metrics['db_queries_per_sec'] = {
            'value': round(db_qps, 0),
            'unit': 'queries/sec',
            'timestamp': timestamp.isoformat(),
            'status': 'healthy'
        }

        db_time = self.metrics['db_query_time_ms']['value']
        db_time += random.gauss(0, 2)
        db_time = max(10, min(1000, db_time))
        self.metrics['db_query_time_ms']['value'] = db_time
        updated_metrics['db_query_time_ms'] = {
            'value': round(db_time, 2),
            'unit': 'ms',
            'timestamp': timestamp.isoformat(),
            'status': 'healthy'
        }

        # Store for later reference
        self.last_real_metrics = real_metrics

        return updated_metrics

    def get_metrics_snapshot(self) -> Dict:
        """Get current metrics snapshot"""
        if self.use_real and self.real_collector:
            real = self.real_collector.get_metrics_snapshot()
            return {
                name: {
                    'value': real.get(name, data['value']),
                    'unit': self._get_unit(name),
                    'status': self._get_status(name, real.get(name, data['value']), data['max'])
                }
                for name, data in self.metrics.items()
            }
        else:
            return super().get_metrics_snapshot()

    def print_status(self):
        """Print current status"""
        print("\n" + "="*70)
        print("📊 HYBRID METRICS SIMULATOR STATUS")
        print("="*70)

        if self.use_real:
            print(f"✅ Real Metrics:      ENABLED")
            if self.real_collector:
                collector_info = self.real_collector.get_metrics_snapshot()
                print(f"   Source:           {collector_info.get('source', 'unknown')}")
        else:
            print(f"❌ Real Metrics:      DISABLED (using simulation)")

        print(f"\n📍 Anomalies:")
        anomaly_count = sum(1 for v in self.anomalies.values() if v)
        if anomaly_count == 0:
            print(f"   Status:           ✅ NONE ACTIVE")
        else:
            print(f"   Active:           🔴 {anomaly_count}")
            for name, active in self.anomalies.items():
                if active:
                    print(f"     - {name.upper()}")

        # Sample metrics
        print(f"\n📈 Current Metrics:")
        metrics = self.get_metrics_snapshot()
        if 'cpu_usage' in metrics:
            print(f"   CPU:              {metrics['cpu_usage']['value']:.1f}%")
        if 'memory_usage' in metrics:
            print(f"   Memory:           {metrics['memory_usage']['value']:.1f}%")
        if 'error_rate' in metrics:
            print(f"   Error Rate:       {metrics['error_rate']['value']:.2f}%")

        print("="*70 + "\n")


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_hybrid_simulator = None


def get_hybrid_simulator() -> HybridMetricsSimulator:
    """Get or create global hybrid simulator instance"""
    global _hybrid_simulator
    if _hybrid_simulator is None:
        _hybrid_simulator = HybridMetricsSimulator(use_real_metrics=True, use_perfmon=True)
    return _hybrid_simulator


def start_hybrid_collection():
    """Start background metrics collection using real data"""
    simulator = get_hybrid_simulator()

    def collect():
        while True:
            try:
                simulator.update_metrics()
                time.sleep(simulator.update_interval)
            except Exception as e:
                print(f"❌ Error updating hybrid metrics: {e}")
                time.sleep(1)

    thread = Thread(target=collect, daemon=True)
    thread.start()
    print("✅ Hybrid metrics collection started (real data + anomaly injection)")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🚀 Hybrid Metrics Simulator Test\n")

    simulator = HybridMetricsSimulator(use_real_metrics=True, use_perfmon=True)

    print("Starting collection...")
    start_hybrid_collection()

    # Run for 20 seconds
    for i in range(4):
        time.sleep(5)
        simulator.print_status()

    print("\n🔴 Triggering Memory Leak anomaly for 10 seconds...")
    simulator.simulate_anomaly('memory_leak', duration=10)

    for i in range(3):
        time.sleep(5)
        simulator.print_status()

    print("✅ Test complete!")
