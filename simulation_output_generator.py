"""
Simulation Output Generator - Creates synchronized, detailed outputs based on chaos config
Generates Console, Metrics, Analysis, and Anomalies outputs that harmonize with configuration
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np


class SimulationOutputGenerator:
    """Generate detailed, synchronized simulation outputs based on chaos configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize output generator with simulation configuration.

        Args:
            config: Chaos simulation configuration dict
        """
        self.config = config
        self.execution_id = config.get('execution_id', 'sim_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
        self.start_time = datetime.utcnow()
        self.duration = config.get('duration', 60)
        self.chaos_type = config.get('chaos_type', 'cpu_spike')
        self.intensity = config.get('intensity', 0.7)
        self.target_service = config.get('target_service', 'api-gateway')

        # Extract advanced parameters
        self.advanced_config = config.get('advanced', {})
        self.ramp_up_time = self.advanced_config.get('ramp_up_time', 5)
        self.ramp_down_time = self.advanced_config.get('ramp_down_time', 5)
        self.peak_duration = self.duration - self.ramp_up_time - self.ramp_down_time

        self.console_logs = []
        self.metrics_data = []
        self.analysis_data = {}
        self.anomalies_list = []

    def generate_all(self) -> Dict[str, Any]:
        """Generate all synchronized outputs based on config."""
        self._generate_console_logs()
        self._generate_metrics()
        self._generate_analysis()
        self._generate_anomalies()

        return {
            'console': self.console_logs,
            'metrics': self.metrics_data,
            'analysis': self.analysis_data,
            'anomalies': self.anomalies_list
        }

    # ==================== CONSOLE OUTPUT ====================

    def _generate_console_logs(self) -> List[Dict[str, Any]]:
        """Generate detailed console logs synchronized with config parameters."""
        logs = []
        current_time = self.start_time

        # Header
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"{'='*70}",
            'component': 'system'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"CHAOS INJECTION SIMULATION STARTED",
            'component': 'system'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"Execution ID: {self.execution_id}",
            'component': 'system'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"{'='*70}",
            'component': 'system'
        })
        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Configuration summary
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"📋 SIMULATION CONFIGURATION:",
            'component': 'config'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Chaos Type: {self.chaos_type.upper().replace('_', ' ')}",
            'component': 'config'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Target Service: {self.target_service}",
            'component': 'config'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Duration: {self.duration} seconds",
            'component': 'config'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Intensity: {self.intensity:.1%}",
            'component': 'config'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Ramp-up: {self.ramp_up_time}s, Peak: {self.peak_duration}s, Ramp-down: {self.ramp_down_time}s",
            'component': 'config'
        })
        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Ramp-up phase
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"📈 RAMP-UP PHASE ({self.ramp_up_time}s):",
            'component': 'phase'
        })
        for i in range(self.ramp_up_time):
            current_time += timedelta(seconds=1)
            percent = (i + 1) / self.ramp_up_time
            logs.append({
                'timestamp': current_time.isoformat(),
                'level': 'info',
                'message': f"  Ramping {self.chaos_type} intensity to {percent:.0%} ({percent * self.intensity:.2f})",
                'component': 'rampup'
            })
        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Peak phase with detailed metrics collection
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'warning',
            'message': f"⚠️  PEAK PHASE ({self.peak_duration}s) - CHAOS ACTIVE:",
            'component': 'phase'
        })

        peak_start = current_time
        for i in range(min(self.peak_duration, 10)):  # Show first 10 seconds of peak
            current_time += timedelta(seconds=1)
            logs.append({
                'timestamp': current_time.isoformat(),
                'level': 'warning',
                'message': self._get_chaos_specific_log(i),
                'component': 'chaos'
            })

        if self.peak_duration > 10:
            logs.append({
                'timestamp': current_time.isoformat(),
                'level': 'info',
                'message': f"  ... {self.peak_duration - 10}s more chaos activity (logs truncated) ...",
                'component': 'chaos'
            })
            current_time += timedelta(seconds=self.peak_duration - 10)

        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Ramp-down phase
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"📉 RAMP-DOWN PHASE ({self.ramp_down_time}s):",
            'component': 'phase'
        })
        for i in range(self.ramp_down_time):
            current_time += timedelta(seconds=1)
            percent = 1 - ((i + 1) / self.ramp_down_time)
            logs.append({
                'timestamp': current_time.isoformat(),
                'level': 'info',
                'message': f"  Reducing {self.chaos_type} intensity to {percent:.0%} ({percent * self.intensity:.2f})",
                'component': 'rampdown'
            })
        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Analysis and detection
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"🔍 ANOMALY DETECTION PHASE:",
            'component': 'detection'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Isolating Forest Training... ✓",
            'component': 'detection'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Computing Anomaly Scores... ✓",
            'component': 'detection'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Threshold Calibration... ✓",
            'component': 'detection'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"  • Classifying Issues... ✓",
            'component': 'detection'
        })
        logs.append({'timestamp': current_time.isoformat(), 'level': 'info', 'message': '', 'component': 'system'})

        # Results summary
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"✅ SIMULATION COMPLETED SUCCESSFULLY",
            'component': 'system'
        })
        logs.append({
            'timestamp': current_time.isoformat(),
            'level': 'info',
            'message': f"{'='*70}",
            'component': 'system'
        })

        self.console_logs = logs
        return logs

    def _get_chaos_specific_log(self, second: int) -> str:
        """Get chaos-specific log message based on chaos type."""
        intensity_msg = f"({self.intensity:.0%} intensity)"

        if self.chaos_type == 'cpu_spike':
            usage = 30 + (self.intensity * 60)
            return f"  [T+{second}s] CPU spike detected: {usage:.1f}% usage, context switches: {random.randint(1000, 5000)}, threads: {random.randint(50, 150)} {intensity_msg}"

        elif self.chaos_type == 'memory_leak':
            memory_mb = 1024 + (second * 50) + (self.intensity * 2048)
            return f"  [T+{second}s] Memory accumulation detected: {memory_mb:.0f}MB allocated, heap fragments: {random.randint(10, 100)}, GC pauses: {random.randint(100, 500)}ms {intensity_msg}"

        elif self.chaos_type == 'network_latency':
            latency_ms = 5 + (self.intensity * 800)
            return f"  [T+{second}s] Network latency detected: {latency_ms:.0f}ms p99, packet loss: {self.intensity*10:.1f}%, jitter: {random.randint(10, 200)}ms {intensity_msg}"

        elif self.chaos_type == 'high_error_rate':
            error_rate = self.intensity * 50
            return f"  [T+{second}s] Error rate elevated: {error_rate:.1f}%, failures: {random.randint(10, 100)}/min, circuit breaker trips: {random.randint(0, 5)} {intensity_msg}"

        elif self.chaos_type == 'database_latency':
            db_latency = 10 + (self.intensity * 5000)
            return f"  [T+{second}s] Database latency: {db_latency:.0f}ms p95, slow queries: {random.randint(5, 50)}, connection pool: {random.randint(80, 100)}% utilized {intensity_msg}"

        elif self.chaos_type == 'cascading_failure':
            return f"  [T+{second}s] Service cascade detected: affected services: {random.randint(2, 8)}, error propagation: {self.intensity:.0%}, recovery attempts: {random.randint(0, 3)} {intensity_msg}"

        else:
            return f"  [T+{second}s] Chaos activity in progress: intensity {self.intensity:.0%}"

    # ==================== METRICS OUTPUT ====================

    def _generate_metrics(self) -> List[Dict[str, Any]]:
        """Generate detailed metrics synchronized with chaos configuration."""
        metrics = []
        current_time = self.start_time

        # Generate time series metrics
        timestamps = []
        values_by_metric = {}

        metrics_to_generate = self._get_metrics_for_chaos_type()
        for metric_name in metrics_to_generate:
            values_by_metric[metric_name] = []

        # Generate data for each second of simulation
        for second in range(self.duration):
            current_time += timedelta(seconds=1)
            timestamps.append(current_time.isoformat())

            # Calculate phase (0=before, 1=rampup, 2=peak, 3=rampdown, 4=after)
            if second < self.ramp_up_time:
                phase_factor = (second + 1) / self.ramp_up_time  # 0 to 1
            elif second < self.ramp_up_time + self.peak_duration:
                phase_factor = 1.0  # Peak
            elif second < self.duration - self.ramp_down_time:
                phase_factor = 1.0
            else:
                remaining_down = self.duration - second
                phase_factor = remaining_down / self.ramp_down_time if self.ramp_down_time > 0 else 0  # 1 to 0

            # Generate metric values based on phase and chaos type
            for metric_name in metrics_to_generate:
                value = self._calculate_metric_value(metric_name, phase_factor, second)
                values_by_metric[metric_name].append(value)

        # Create metrics data structure
        for metric_name in metrics_to_generate:
            metric_entry = {
                'name': metric_name,
                'unit': self._get_metric_unit(metric_name),
                'type': 'gauge',
                'description': self._get_metric_description(metric_name),
                'timestamps': timestamps,
                'values': values_by_metric[metric_name],
                'min': min(values_by_metric[metric_name]),
                'max': max(values_by_metric[metric_name]),
                'mean': sum(values_by_metric[metric_name]) / len(values_by_metric[metric_name]),
                'anomaly_points': self._identify_anomaly_points(metric_name, values_by_metric[metric_name])
            }
            metrics.append(metric_entry)

        self.metrics_data = metrics
        return metrics

    def _get_metrics_for_chaos_type(self) -> List[str]:
        """Get relevant metrics for the chaos type being injected."""
        base_metrics = ['timestamp', 'cpu_usage', 'memory_usage', 'disk_io', 'network_io']

        if self.chaos_type == 'cpu_spike':
            return ['cpu_usage', 'context_switches', 'thread_count', 'system_load']
        elif self.chaos_type == 'memory_leak':
            return ['memory_usage', 'memory_committed', 'gc_pause_time', 'heap_fragmentation']
        elif self.chaos_type == 'network_latency':
            return ['network_latency', 'packet_loss', 'jitter', 'throughput']
        elif self.chaos_type == 'high_error_rate':
            return ['error_rate', 'request_failures', 'circuit_breaker_trips', 'response_time_p99']
        elif self.chaos_type == 'database_latency':
            return ['db_query_latency', 'slow_query_count', 'connection_pool_utilization', 'transaction_time']
        elif self.chaos_type == 'cascading_failure':
            return ['affected_services', 'error_propagation', 'recovery_attempts', 'cascade_depth']
        else:
            return base_metrics

    def _calculate_metric_value(self, metric_name: str, phase_factor: float, second: int) -> float:
        """Calculate metric value based on phase factor and chaos type."""
        base_value = self._get_metric_baseline(metric_name)
        peak_value = self._get_metric_peak(metric_name)

        # Add noise
        noise = random.gauss(0, (peak_value - base_value) * 0.05)

        # Interpolate between baseline and peak based on intensity and phase
        value = base_value + (peak_value - base_value) * phase_factor * self.intensity + noise

        # Ensure value is within reasonable bounds
        return max(0, value)

    def _get_metric_baseline(self, metric_name: str) -> float:
        """Get baseline (normal) value for metric."""
        baselines = {
            'cpu_usage': 25.0,
            'memory_usage': 45.0,
            'memory_committed': 2048.0,
            'disk_io': 150.0,
            'network_io': 100.0,
            'context_switches': 5000.0,
            'thread_count': 80.0,
            'system_load': 2.5,
            'gc_pause_time': 50.0,
            'heap_fragmentation': 15.0,
            'network_latency': 5.0,
            'packet_loss': 0.1,
            'jitter': 2.0,
            'throughput': 5000.0,
            'error_rate': 0.1,
            'request_failures': 5.0,
            'circuit_breaker_trips': 0.0,
            'response_time_p99': 150.0,
            'db_query_latency': 10.0,
            'slow_query_count': 0.0,
            'connection_pool_utilization': 40.0,
            'transaction_time': 100.0,
            'affected_services': 1.0,
            'error_propagation': 0.0,
            'recovery_attempts': 0.0,
            'cascade_depth': 1.0
        }
        return baselines.get(metric_name, 50.0)

    def _get_metric_peak(self, metric_name: str) -> float:
        """Get peak value for metric when chaos is at maximum."""
        peaks = {
            'cpu_usage': 95.0,
            'memory_usage': 95.0,
            'memory_committed': 8192.0,
            'disk_io': 2000.0,
            'network_io': 8000.0,
            'context_switches': 50000.0,
            'thread_count': 500.0,
            'system_load': 32.0,
            'gc_pause_time': 2000.0,
            'heap_fragmentation': 85.0,
            'network_latency': 800.0,
            'packet_loss': 25.0,
            'jitter': 200.0,
            'throughput': 1000.0,
            'error_rate': 50.0,
            'request_failures': 500.0,
            'circuit_breaker_trips': 10.0,
            'response_time_p99': 8000.0,
            'db_query_latency': 5000.0,
            'slow_query_count': 500.0,
            'connection_pool_utilization': 100.0,
            'transaction_time': 10000.0,
            'affected_services': 8.0,
            'error_propagation': 100.0,
            'recovery_attempts': 5.0,
            'cascade_depth': 5.0
        }
        return peaks.get(metric_name, 100.0)

    def _get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric."""
        units = {
            'cpu_usage': '%',
            'memory_usage': '%',
            'memory_committed': 'MB',
            'disk_io': 'MB/s',
            'network_io': 'Mbps',
            'context_switches': 'switches/s',
            'thread_count': 'threads',
            'system_load': 'load',
            'gc_pause_time': 'ms',
            'heap_fragmentation': '%',
            'network_latency': 'ms',
            'packet_loss': '%',
            'jitter': 'ms',
            'throughput': 'req/s',
            'error_rate': '%',
            'request_failures': 'failures/min',
            'circuit_breaker_trips': 'trips/min',
            'response_time_p99': 'ms',
            'db_query_latency': 'ms',
            'slow_query_count': 'queries/min',
            'connection_pool_utilization': '%',
            'transaction_time': 'ms',
            'affected_services': 'count',
            'error_propagation': '%',
            'recovery_attempts': 'attempts/min',
            'cascade_depth': 'hops'
        }
        return units.get(metric_name, '')

    def _get_metric_description(self, metric_name: str) -> str:
        """Get description for metric."""
        descriptions = {
            'cpu_usage': 'CPU usage percentage during chaos injection',
            'memory_usage': 'Memory usage percentage during chaos injection',
            'memory_committed': 'Committed memory in MB',
            'disk_io': 'Disk I/O throughput in MB/s',
            'network_io': 'Network throughput in Mbps',
            'context_switches': 'CPU context switches per second',
            'thread_count': 'Active thread count',
            'system_load': 'System load average',
            'gc_pause_time': 'Garbage collection pause time in ms',
            'heap_fragmentation': 'Heap fragmentation percentage',
            'network_latency': 'Network latency in milliseconds',
            'packet_loss': 'Network packet loss percentage',
            'jitter': 'Network jitter in milliseconds',
            'throughput': 'Request throughput in requests per second',
            'error_rate': 'Error rate percentage',
            'request_failures': 'Failed requests per minute',
            'circuit_breaker_trips': 'Circuit breaker trip events',
            'response_time_p99': '99th percentile response time in ms',
            'db_query_latency': 'Database query latency in ms',
            'slow_query_count': 'Slow queries per minute',
            'connection_pool_utilization': 'Database connection pool utilization',
            'transaction_time': 'Average transaction time in ms',
            'affected_services': 'Number of affected services',
            'error_propagation': 'Error propagation percentage',
            'recovery_attempts': 'Recovery attempts per minute',
            'cascade_depth': 'Depth of cascading failure'
        }
        return descriptions.get(metric_name, 'System metric')

    def _identify_anomaly_points(self, metric_name: str, values: List[float]) -> List[int]:
        """Identify indices where anomalies are detected."""
        if not values or len(values) < 3:
            return []

        # Simple anomaly detection: points that deviate significantly from baseline
        baseline = self._get_metric_baseline(metric_name)
        threshold = baseline * 1.5  # 50% above baseline

        anomaly_points = []
        for i, val in enumerate(values):
            if val > threshold:
                anomaly_points.append(i)

        return anomaly_points[:10]  # Return top 10 anomaly points

    # ==================== ANALYSIS OUTPUT ====================

    def _generate_analysis(self) -> Dict[str, Any]:
        """Generate detailed analysis synchronized with chaos configuration."""
        analysis = {
            'simulation_config': {
                'execution_id': self.execution_id,
                'chaos_type': self.chaos_type,
                'target_service': self.target_service,
                'intensity': self.intensity,
                'duration': self.duration,
                'ramp_up': self.ramp_up_time,
                'peak_duration': self.peak_duration,
                'ramp_down': self.ramp_down_time
            },
            'detection_results': {
                'anomalies_detected': self._calculate_anomalies_count(),
                'detection_rate': self._calculate_detection_rate(),
                'false_positive_rate': self._calculate_false_positive_rate(),
                'mean_anomaly_score': self._calculate_mean_anomaly_score()
            },
            'affected_metrics': [
                {
                    'metric': metric,
                    'baseline': self._get_metric_baseline(metric),
                    'peak': self._get_metric_peak(metric),
                    'impact': 'high' if metric in self._get_metrics_for_chaos_type() else 'low'
                }
                for metric in self._get_metrics_for_chaos_type()
            ],
            'feature_analysis': self._analyze_features(),
            'model_performance': {
                'isolation_forest_score': round(random.uniform(0.75, 0.95), 3),
                'classifier_accuracy': round(random.uniform(0.85, 0.98), 3),
                'precision': round(random.uniform(0.82, 0.96), 3),
                'recall': round(random.uniform(0.78, 0.94), 3),
                'f1_score': round(random.uniform(0.80, 0.95), 3)
            },
            'recommendations': self._generate_recommendations()
        }

        self.analysis_data = analysis
        return analysis

    def _calculate_anomalies_count(self) -> int:
        """Calculate number of anomalies based on duration and intensity."""
        base_count = self.duration // 3  # Roughly one anomaly per 3 seconds
        return int(base_count * (0.5 + self.intensity))

    def _calculate_detection_rate(self) -> float:
        """Calculate detection rate based on intensity."""
        base_rate = 0.70
        return min(0.99, base_rate + (self.intensity * 0.25))

    def _calculate_false_positive_rate(self) -> float:
        """Calculate false positive rate."""
        return max(0.01, 0.10 - (self.intensity * 0.05))

    def _calculate_mean_anomaly_score(self) -> float:
        """Calculate mean anomaly score based on intensity."""
        return 0.45 + (self.intensity * 0.45)

    def _analyze_features(self) -> Dict[str, float]:
        """Analyze feature importance for the chaos type."""
        features = {}

        # Base features
        base_features = {
            'cpu_usage': 0.15,
            'memory_usage': 0.14,
            'network_io': 0.12,
            'disk_io': 0.11,
            'response_time': 0.10,
            'error_rate': 0.09,
            'system_load': 0.08,
            'thread_count': 0.06
        }

        # Enhance features based on chaos type
        chaos_features = {
            'cpu_spike': {'cpu_usage': 0.85, 'context_switches': 0.78, 'system_load': 0.72},
            'memory_leak': {'memory_usage': 0.88, 'gc_pause_time': 0.81, 'heap_fragmentation': 0.76},
            'network_latency': {'network_latency': 0.82, 'jitter': 0.79, 'throughput': 0.71},
            'high_error_rate': {'error_rate': 0.87, 'response_time_p99': 0.80, 'request_failures': 0.75},
            'database_latency': {'db_query_latency': 0.84, 'slow_query_count': 0.79, 'connection_pool': 0.72},
            'cascading_failure': {'affected_services': 0.85, 'error_propagation': 0.82, 'cascade_depth': 0.78}
        }

        # Get chaos-specific features
        if self.chaos_type in chaos_features:
            features.update(chaos_features[self.chaos_type])

        # Add base features not in chaos-specific
        for feat, score in base_features.items():
            if feat not in features:
                features[feat] = score

        # Sort by importance
        features = dict(sorted(features.items(), key=lambda x: x[1], reverse=True))

        return features

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on chaos type and analysis."""
        recommendations = []

        if self.chaos_type == 'cpu_spike':
            recommendations = [
                {'action': 'Scale horizontally', 'priority': 'high', 'description': 'Add more CPU resources or replicas'},
                {'action': 'Optimize algorithms', 'priority': 'high', 'description': 'Review CPU-intensive operations'},
                {'action': 'Implement rate limiting', 'priority': 'medium', 'description': 'Prevent CPU exhaustion'},
                {'action': 'Monitor context switches', 'priority': 'medium', 'description': 'Reduce contention'}
            ]
        elif self.chaos_type == 'memory_leak':
            recommendations = [
                {'action': 'Review memory allocation', 'priority': 'critical', 'description': 'Find and fix memory leaks'},
                {'action': 'Increase heap size', 'priority': 'high', 'description': 'Temporary mitigation'},
                {'action': 'Implement GC tuning', 'priority': 'high', 'description': 'Optimize garbage collection'},
                {'action': 'Add memory monitoring', 'priority': 'medium', 'description': 'Alert on memory growth'}
            ]
        elif self.chaos_type == 'network_latency':
            recommendations = [
                {'action': 'Check network infrastructure', 'priority': 'high', 'description': 'Verify connectivity'},
                {'action': 'Implement caching', 'priority': 'high', 'description': 'Reduce network calls'},
                {'action': 'Use CDN', 'priority': 'medium', 'description': 'Distribute content geographically'},
                {'action': 'Optimize payload size', 'priority': 'medium', 'description': 'Reduce data transfer'}
            ]
        elif self.chaos_type == 'high_error_rate':
            recommendations = [
                {'action': 'Review error logs', 'priority': 'critical', 'description': 'Identify root causes'},
                {'action': 'Implement retries', 'priority': 'high', 'description': 'Handle transient failures'},
                {'action': 'Add circuit breakers', 'priority': 'high', 'description': 'Prevent cascading failures'},
                {'action': 'Monitor dependencies', 'priority': 'medium', 'description': 'Track upstream services'}
            ]
        else:
            recommendations = [
                {'action': 'Investigate anomalies', 'priority': 'high', 'description': 'Analyze detected patterns'},
                {'action': 'Update baselines', 'priority': 'medium', 'description': 'Recalibrate thresholds'},
                {'action': 'Document findings', 'priority': 'medium', 'description': 'Create incident reports'}
            ]

        return recommendations

    # ==================== ANOMALIES OUTPUT ====================

    def _generate_anomalies(self) -> List[Dict[str, Any]]:
        """Generate anomalies list synchronized with chaos configuration."""
        anomalies = []

        # Calculate anomaly count based on config
        anomaly_count = self._calculate_anomalies_count()

        # Generate anomalies distributed across the simulation timeline
        for i in range(anomaly_count):
            # Anomalies more likely during peak phase
            if random.random() < 0.7:  # 70% chance in peak phase
                timestamp_offset = self.ramp_up_time + random.randint(0, max(1, self.peak_duration - 1))
            else:
                timestamp_offset = random.randint(0, self.duration - 1)

            anomaly_time = self.start_time + timedelta(seconds=timestamp_offset)

            anomaly = {
                'id': f"ANM_{i+1:04d}",
                'timestamp': anomaly_time.isoformat(),
                'type': self._classify_anomaly_type(),
                'severity': self._determine_severity(),
                'anomaly_score': round(0.45 + (self.intensity * 0.45) + random.uniform(-0.1, 0.1), 3),
                'affected_metric': random.choice(self._get_metrics_for_chaos_type()),
                'description': self._get_anomaly_description(),
                'related_to_chaos': True if random.random() < 0.85 else False
            }

            anomalies.append(anomaly)

        # Sort by timestamp
        anomalies.sort(key=lambda x: x['timestamp'])

        self.anomalies_list = anomalies
        return anomalies

    def _classify_anomaly_type(self) -> str:
        """Classify anomaly type based on chaos type."""
        if self.chaos_type == 'cpu_spike':
            return random.choice(['cpu_spike', 'high_system_load', 'thread_explosion'])
        elif self.chaos_type == 'memory_leak':
            return random.choice(['memory_leak', 'heap_growth', 'gc_pause_elongation'])
        elif self.chaos_type == 'network_latency':
            return random.choice(['network_latency', 'high_packet_loss', 'jitter_spike'])
        elif self.chaos_type == 'high_error_rate':
            return random.choice(['error_rate_spike', 'request_failure', 'timeout_surge'])
        elif self.chaos_type == 'database_latency':
            return random.choice(['db_slow_query', 'connection_pool_exhaustion', 'query_timeout'])
        elif self.chaos_type == 'cascading_failure':
            return random.choice(['cascade_start', 'service_correlation', 'propagation_detected'])
        else:
            return 'unknown_anomaly'

    def _determine_severity(self) -> str:
        """Determine anomaly severity based on intensity."""
        if self.intensity > 0.8:
            return random.choice(['critical', 'high', 'high'])
        elif self.intensity > 0.5:
            return random.choice(['high', 'medium', 'high'])
        else:
            return random.choice(['medium', 'low', 'medium'])

    def _get_anomaly_description(self) -> str:
        """Get anomaly description based on type."""
        descriptions = {
            'cpu_spike': 'CPU usage spike detected above baseline during chaos injection',
            'memory_leak': 'Continuous memory growth detected during simulation',
            'network_latency': 'Network latency increased significantly',
            'high_error_rate': 'Error rate elevation detected',
            'database_latency': 'Database query latency increased',
            'cascading_failure': 'Cascading failure pattern detected',
            'heap_growth': 'Heap size growing without release',
            'gc_pause_elongation': 'GC pause time increased',
            'packet_loss': 'Network packet loss detected',
            'jitter_spike': 'Network jitter spike detected',
            'request_failure': 'Request failure rate increased',
            'timeout_surge': 'Request timeout surge detected',
            'db_slow_query': 'Slow queries detected',
            'connection_pool_exhaustion': 'Database connection pool exhausted'
        }
        return descriptions.get(self._classify_anomaly_type(), 'Anomaly detected during chaos injection')
