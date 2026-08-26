"""
Locust Load Testing for AIOPS Dashboard
Generates realistic traffic and captures metrics during testing
Run: locust -f locustfile.py --host=http://localhost:5000
"""

import time
import psutil
import json
from datetime import datetime
from locust import HttpUser, task, between, events
from typing import Dict, List


# ============================================================================
# METRICS CAPTURE
# ============================================================================

class LoadTestMetricsCollector:
    """Capture metrics during load testing"""

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.metrics_log: List[Dict] = []
        self.request_log: List[Dict] = []

    def record_system_metrics(self, label: str = ""):
        """Record system metrics at this moment"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'elapsed_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'label': label,
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_mb': psutil.virtual_memory().used / (1024*1024),
            'disk_percent': psutil.disk_usage('/').percent,
            'network_in_mb': psutil.net_io_counters().bytes_recv / (1024*1024),
            'network_out_mb': psutil.net_io_counters().bytes_sent / (1024*1024),
            'process_count': len(psutil.pids()),
            'open_connections': len(psutil.net_connections()),
        }
        self.metrics_log.append(metrics)
        return metrics

    def record_request(self, request_type: str, name: str, response_time: float,
                       status_code: int, error: bool = False):
        """Record a request event"""
        self.request_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': request_type,
            'name': name,
            'response_time_ms': response_time,
            'status_code': status_code,
            'error': error
        })

    def get_statistics(self) -> Dict:
        """Calculate statistics"""
        if not self.request_log:
            return {}

        response_times = [r['response_time_ms'] for r in self.request_log]
        errors = sum(1 for r in self.request_log if r['error'])

        return {
            'total_requests': len(self.request_log),
            'total_errors': errors,
            'error_rate': errors / len(self.request_log) * 100,
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'requests_per_second': len(self.request_log) / (
                (datetime.utcnow() - self.start_time).total_seconds() + 1
            )
        }

    def print_report(self):
        """Print test report"""
        print("\n" + "="*70)
        print("📊 LOAD TEST METRICS REPORT")
        print("="*70)

        # System metrics
        if self.metrics_log:
            latest = self.metrics_log[-1]
            print(f"\n📈 Final System Metrics:")
            print(f"   CPU:              {latest['cpu_percent']:.1f}%")
            print(f"   Memory:           {latest['memory_percent']:.1f}% "
                  f"({latest['memory_mb']:.0f} MB)")
            print(f"   Disk:             {latest['disk_percent']:.1f}%")
            print(f"   Network In:       {latest['network_in_mb']:.1f} MB")
            print(f"   Network Out:      {latest['network_out_mb']:.1f} MB")
            print(f"   Processes:        {latest['process_count']}")
            print(f"   Connections:      {latest['open_connections']}")

        # Request statistics
        stats = self.get_statistics()
        if stats:
            print(f"\n📋 Request Statistics:")
            print(f"   Total Requests:   {stats['total_requests']}")
            print(f"   Errors:           {stats['total_errors']}")
            print(f"   Error Rate:       {stats['error_rate']:.2f}%")
            print(f"   Avg Response:     {stats['avg_response_time']:.1f} ms")
            print(f"   Min Response:     {stats['min_response_time']:.1f} ms")
            print(f"   Max Response:     {stats['max_response_time']:.1f} ms")
            print(f"   Requests/sec:     {stats['requests_per_second']:.1f}")

        print("="*70 + "\n")

    def export_json(self, filename: str = "load_test_results.json"):
        """Export results to JSON"""
        results = {
            'test_started': self.start_time.isoformat(),
            'test_ended': datetime.utcnow().isoformat(),
            'duration_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'metrics': self.metrics_log,
            'requests': self.request_log,
            'statistics': self.get_statistics()
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"📁 Results exported to {filename}")


# ============================================================================
# GLOBAL METRICS COLLECTOR
# ============================================================================

metrics_collector = LoadTestMetricsCollector()


# ============================================================================
# LOAD TEST SCENARIOS
# ============================================================================

class DashboardUser(HttpUser):
    """Simulate dashboard users"""

    wait_time = between(2, 5)  # Wait 2-5 seconds between requests

    def on_start(self):
        """Called when user starts"""
        metrics_collector.record_system_metrics("user_started")

    @task(2)
    def view_overview_dashboard(self):
        """View the main overview dashboard"""
        with self.client.get(
            "/",
            catch_response=True,
            name="GET /"
        ) as response:
            start_time = time.time()
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")
            metrics_collector.record_request(
                "GET", "/", (time.time() - start_time) * 1000,
                response.status_code, response.status_code >= 400
            )

    @task(3)
    def get_all_metrics(self):
        """Fetch all metrics via API"""
        start_time = time.time()
        response = self.client.get("/api/metrics/all")
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "GET", "/api/metrics/all", elapsed,
            response.status_code, response.status_code >= 400
        )

    @task(2)
    def get_metrics_summary(self):
        """Fetch metrics summary"""
        start_time = time.time()
        response = self.client.get("/api/metrics/summary")
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "GET", "/api/metrics/summary", elapsed,
            response.status_code, response.status_code >= 400
        )

    @task(1)
    def get_anomalies(self):
        """Check current anomalies"""
        start_time = time.time()
        response = self.client.get("/api/metrics/anomalies")
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "GET", "/api/metrics/anomalies", elapsed,
            response.status_code, response.status_code >= 400
        )

    @task(1)
    def login(self):
        """Authenticate"""
        start_time = time.time()
        response = self.client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "POST", "/api/auth/login", elapsed,
            response.status_code, response.status_code >= 400
        )


class AnomalyTriggerUser(HttpUser):
    """Simulate anomaly injection during load test"""

    wait_time = between(30, 60)  # Trigger every 30-60 seconds
    token = None

    def on_start(self):
        """Get auth token"""
        response = self.client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            self.token = response.json().get('token')

    @task(1)
    def trigger_memory_leak(self):
        """Trigger memory leak anomaly"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()

        response = self.client.post(
            "/api/metrics/anomalies/trigger",
            json={"anomaly_type": "memory_leak", "duration": 30},
            headers=headers
        )
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "POST", "/api/metrics/anomalies/trigger:memory_leak", elapsed,
            response.status_code, response.status_code >= 400
        )

    @task(1)
    def trigger_cpu_spike(self):
        """Trigger CPU spike anomaly"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()

        response = self.client.post(
            "/api/metrics/anomalies/trigger",
            json={"anomaly_type": "cpu_spike", "duration": 20},
            headers=headers
        )
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "POST", "/api/metrics/anomalies/trigger:cpu_spike", elapsed,
            response.status_code, response.status_code >= 400
        )

    @task(1)
    def trigger_network_latency(self):
        """Trigger network latency anomaly"""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()

        response = self.client.post(
            "/api/metrics/anomalies/trigger",
            json={"anomaly_type": "network_latency", "duration": 25},
            headers=headers
        )
        elapsed = (time.time() - start_time) * 1000

        metrics_collector.record_request(
            "POST", "/api/metrics/anomalies/trigger:network_latency", elapsed,
            response.status_code, response.status_code >= 400
        )


# ============================================================================
# EVENT HOOKS
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "="*70)
    print("🚀 AIOPS DASHBOARD LOAD TEST STARTED")
    print("="*70)
    print(f"⏰ Start Time:     {metrics_collector.start_time}")
    print(f"🎯 Target:        {environment.host}")
    print("="*70 + "\n")

    metrics_collector.record_system_metrics("test_start")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("\n" + "="*70)
    print("⏹️  AIOPS DASHBOARD LOAD TEST STOPPED")
    print("="*70)

    metrics_collector.print_report()
    metrics_collector.export_json()

    print("✅ Test analysis complete!")


@events.quit.add_listener
def on_quit(environment, **kwargs):
    """Called when test quits"""
    metrics_collector.export_json()


# ============================================================================
# USAGE
# ============================================================================

"""
Installation:
    pip install locust

Running the test:
    # Basic test (10 users, ramp up at 2 per second)
    locust -f locustfile.py --host=http://localhost:5000 -u 10 -r 2

    # With headless mode (runs for 60 seconds)
    locust -f locustfile.py --host=http://localhost:5000 -u 20 -r 5 --headless -t 60

    # Web UI (default, runs on http://localhost:8089)
    locust -f locustfile.py --host=http://localhost:5000

Key Metrics Captured:
    - System CPU, Memory, Disk, Network usage
    - Request response times
    - Error rates
    - Throughput (requests/second)
    - Anomaly trigger success

Output:
    - Console report at test end
    - JSON file with detailed results
    - Real metrics feed to dashboard during test
"""
