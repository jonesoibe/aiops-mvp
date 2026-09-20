#!/usr/bin/env python3
"""
Real-time Machine Analyzer with Anomaly Detection & Recommendations
Hybrid Flask + WebSocket approach for live analysis of SMD machine data
"""

import csv
import json
import time
import threading
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque
from typing import List, Dict, Tuple
import statistics

# Feature Configuration with Weights
FEATURE_CONFIG = {
    "cpu": {"indices": [0, 1, 2, 3], "weight": 1.0, "name": "CPU Utilization"},
    "memory": {"indices": [4, 5, 6, 7, 8], "weight": 0.95, "name": "Memory Management"},
    "disk": {"indices": [9, 10, 11, 12, 13, 14, 15, 16, 17], "weight": 0.85, "name": "Disk I/O"},
    "network": {"indices": [18, 19, 20, 21, 22, 23], "weight": 0.90, "name": "Network"},
    "processes": {"indices": [24, 25, 26, 27, 28, 29], "weight": 0.70, "name": "Process Management"},
    "services": {"indices": [30, 31, 32, 33, 34, 35, 36, 37], "weight": 0.80, "name": "Services"},
}

# Fault Categories and Detection Rules
FAULT_CATEGORIES = {
    "cpu_exhaustion": {
        "name": "CPU Exhaustion",
        "severity": "critical",
        "triggers": [
            {"feature": 0, "threshold": 0.85, "comparison": "gt"},  # CPU User
            {"feature": 29, "threshold": 0.80, "comparison": "gt"},  # Load Avg
        ],
        "recommendations": [
            {"action": "Scale horizontally (add more instances)", "priority": 1},
            {"action": "Check for runaway processes", "priority": 2},
            {"action": "Optimize application code", "priority": 3},
        ]
    },
    "memory_pressure": {
        "name": "Memory Pressure",
        "severity": "critical",
        "triggers": [
            {"feature": 5, "threshold": 0.90, "comparison": "gt"},  # Memory Util
            {"feature": 4, "threshold": 0.05, "comparison": "gt"},   # Swap In
        ],
        "recommendations": [
            {"action": "Increase available memory", "priority": 1},
            {"action": "Check for memory leaks", "priority": 2},
            {"action": "Restart memory-heavy service", "priority": 3},
            {"action": "Enable swap monitoring", "priority": 4},
        ]
    },
    "disk_bottleneck": {
        "name": "Disk I/O Bottleneck",
        "severity": "high",
        "triggers": [
            {"feature": 11, "threshold": 0.80, "comparison": "gt"},  # Disk Time
            {"feature": 12, "threshold": 0.50, "comparison": "gt"},  # Disk Queue
        ],
        "recommendations": [
            {"action": "Upgrade disk to SSD", "priority": 1},
            {"action": "Optimize I/O patterns", "priority": 2},
            {"action": "Distribute I/O across disks", "priority": 3},
            {"action": "Check for runaway I/O operations", "priority": 4},
        ]
    },
    "network_errors": {
        "name": "Network Interface Issues",
        "severity": "high",
        "triggers": [
            {"feature": 22, "threshold": 0.0, "comparison": "gt"},   # Net Errors In
            {"feature": 23, "threshold": 0.0, "comparison": "gt"},   # Net Errors Out
        ],
        "recommendations": [
            {"action": "Check network hardware", "priority": 1},
            {"action": "Inspect cable connections", "priority": 2},
            {"action": "Review network driver logs", "priority": 3},
            {"action": "Monitor packet loss rate", "priority": 4},
        ]
    },
    "error_rate_spike": {
        "name": "Application Error Rate Spike",
        "severity": "high",
        "triggers": [
            {"feature": 31, "threshold": 0.20, "comparison": "gt"},  # App Errors
            {"feature": 30, "threshold": 0.60, "comparison": "gt"},  # QPS or Load
        ],
        "recommendations": [
            {"action": "Review application logs", "priority": 1},
            {"action": "Check database connectivity", "priority": 2},
            {"action": "Restart application service", "priority": 3},
            {"action": "Rollback recent changes", "priority": 4},
        ]
    },
    "slow_queries": {
        "name": "Database Performance Degradation",
        "severity": "medium",
        "triggers": [
            {"feature": 33, "threshold": 0.20, "comparison": "gt"},  # Slow Queries
            {"feature": 32, "threshold": 0.80, "comparison": "gt"},  # QPS
        ],
        "recommendations": [
            {"action": "Analyze slow query log", "priority": 1},
            {"action": "Add database indexes", "priority": 2},
            {"action": "Optimize query patterns", "priority": 3},
            {"action": "Scale database resources", "priority": 4},
        ]
    },
    "connection_limit": {
        "name": "Connection Limit Approaching",
        "severity": "medium",
        "triggers": [
            {"feature": 34, "threshold": 0.90, "comparison": "gt"},  # Connections
            {"feature": 32, "threshold": 0.70, "comparison": "gt"},  # QPS
        ],
        "recommendations": [
            {"action": "Increase connection pool size", "priority": 1},
            {"action": "Implement connection pooling", "priority": 2},
            {"action": "Close idle connections", "priority": 3},
        ]
    },
    "unusual_activity": {
        "name": "Unusual System Activity",
        "severity": "low",
        "triggers": [
            {"feature": 26, "threshold": 0.40, "comparison": "gt"},  # Context Switches
            {"feature": 0, "threshold": 0.20, "comparison": "lt"},   # Low CPU but high switches
        ],
        "recommendations": [
            {"action": "Monitor for syscall spikes", "priority": 1},
            {"action": "Check for cron/scheduled jobs", "priority": 2},
            {"action": "Investigate background processes", "priority": 3},
        ]
    },
}

@dataclass
class Metric:
    timestamp: float
    feature_index: int
    feature_name: str
    value: float
    baseline: float
    deviation: float
    status: str  # green, yellow, red

@dataclass
class AnomalyAlert:
    timestamp: float
    anomaly_score: float
    severity: str
    affected_metrics: List[str]
    detected_faults: List[str]
    recommendations: List[Dict]

class BaselineCalculator:
    """Calculate baseline metrics from historical data"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.baselines = {}
        self.feature_history = {i: deque(maxlen=window_size) for i in range(38)}

    def add_value(self, feature_index: int, value: float):
        """Add a value to history"""
        self.feature_history[feature_index].append(value)

    def calculate_baseline(self) -> Dict[int, float]:
        """Calculate median baseline for each feature"""
        baselines = {}
        for feature_idx in range(38):
            history = list(self.feature_history[feature_idx])
            if history:
                baselines[feature_idx] = statistics.median(history)
            else:
                baselines[feature_idx] = 0.5  # Default baseline
        return baselines

    def get_baseline(self, feature_index: int, default: float = 0.5) -> float:
        """Get baseline for a specific feature"""
        if feature_index in self.baselines:
            return self.baselines[feature_index]
        return default

class AnomalyDetector:
    """Detect anomalies using weighted scoring"""

    def __init__(self, baseline_calculator: BaselineCalculator, weights: Dict = None):
        self.baseline_calc = baseline_calculator
        self.weights = weights or {cat: conf["weight"] for cat, conf in FEATURE_CONFIG.items()}
        self.anomaly_threshold = 0.52
        self.recent_scores = deque(maxlen=60)  # Last 60 readings

    def calculate_deviation(self, feature_index: int, value: float, baseline: float) -> float:
        """Calculate normalized deviation (0-1)"""
        if baseline == 0:
            return min(value, 1.0)
        deviation = abs(value - baseline) / baseline
        return min(deviation, 1.0)

    def calculate_anomaly_score(self, features: List[float]) -> Tuple[float, List[Metric]]:
        """
        Calculate composite anomaly score (0-1) with weighted features
        Returns: (anomaly_score, list_of_metrics)
        """
        metrics = []
        weighted_deviations = {}

        # Update baselines
        for i, value in enumerate(features):
            self.baseline_calc.add_value(i, value)

        baselines = self.baseline_calc.calculate_baseline()

        # Calculate weighted deviations by category
        for category, config in FEATURE_CONFIG.items():
            category_deviations = []
            for feature_idx in config["indices"]:
                if feature_idx < len(features):
                    value = features[feature_idx]
                    baseline = baselines.get(feature_idx, 0.5)
                    deviation = self.calculate_deviation(feature_idx, value, baseline)
                    category_deviations.append(deviation)

                    # Determine status color
                    if deviation < 0.3:
                        status = "green"
                    elif deviation < 0.6:
                        status = "yellow"
                    else:
                        status = "red"

                    metrics.append(Metric(
                        timestamp=time.time(),
                        feature_index=feature_idx,
                        feature_name=f"Feature #{feature_idx + 1}",
                        value=value,
                        baseline=baseline,
                        deviation=deviation * 100,
                        status=status
                    ))

            if category_deviations:
                avg_deviation = statistics.mean(category_deviations)
                weighted_deviations[category] = avg_deviation * self.weights[category]

        # Composite score
        total_weight = sum(self.weights.values())
        anomaly_score = sum(weighted_deviations.values()) / total_weight if total_weight > 0 else 0
        anomaly_score = min(anomaly_score, 1.0)

        self.recent_scores.append(anomaly_score)

        return anomaly_score, metrics

    def detect_faults(self, features: List[float], anomaly_score: float) -> List[Tuple[str, str, List]]:
        """
        Detect specific fault categories based on rules
        Returns: list of (fault_category, fault_name, recommendations)
        """
        detected_faults = []

        for fault_id, fault_config in FAULT_CATEGORIES.items():
            triggered = True
            affected_features = []

            # Check all triggers for this fault
            for trigger in fault_config["triggers"]:
                feature_idx = trigger["feature"]
                threshold = trigger["threshold"]
                comparison = trigger["comparison"]

                if feature_idx < len(features):
                    value = features[feature_idx]

                    if comparison == "gt" and value > threshold:
                        affected_features.append(f"Feature #{feature_idx + 1}")
                    elif comparison == "lt" and value < threshold:
                        affected_features.append(f"Feature #{feature_idx + 1}")
                    else:
                        triggered = False
                        break

            if triggered and affected_features:
                detected_faults.append((
                    fault_id,
                    fault_config["name"],
                    fault_config["severity"],
                    affected_features,
                    fault_config["recommendations"]
                ))

        return detected_faults

class MachineDataLoader:
    """Load and stream data from SMD CSV files"""

    def __init__(self, smd_dir: str = r"C:\Users\FAVOUR\aiops-mvp\data\raw\smd"):
        self.smd_dir = Path(smd_dir)
        self.available_machines = self._scan_machines()
        self.current_file = None
        self.current_reader = None

    def _scan_machines(self) -> List[Dict]:
        """Scan directory and return list of available machines"""
        machines = []
        if self.smd_dir.exists():
            for file in sorted(self.smd_dir.glob("machine-*.txt")):
                machines.append({
                    "name": file.name,
                    "path": str(file),
                    "server": file.name.split("-")[1],  # "1", "2", or "3"
                    "period": file.name.split("-")[2].replace(".txt", "")
                })
        return machines

    def get_machines(self) -> Dict[str, List[Dict]]:
        """Return machines grouped by server"""
        grouped = {"Machine 1": [], "Machine 2": [], "Machine 3": []}
        for machine in self.available_machines:
            server_key = f"Machine {machine['server']}"
            if server_key in grouped:
                grouped[server_key].append(machine)
        return grouped

    def load_machine(self, machine_name: str):
        """Load a specific machine file"""
        machine = next((m for m in self.available_machines if m["name"] == machine_name), None)
        if not machine:
            return False

        try:
            self.current_file = open(machine["path"], 'r')
            self.current_reader = csv.reader(self.current_file)
            return True
        except Exception as e:
            print(f"Error loading machine: {e}")
            return False

    def get_next_row(self) -> List[float]:
        """Get next row from current machine"""
        if not self.current_reader:
            return None

        try:
            row = next(self.current_reader)
            return [float(x) for x in row]
        except StopIteration:
            self.close()
            return None
        except Exception as e:
            print(f"Error reading row: {e}")
            return None

    def close(self):
        """Close current file"""
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.current_reader = None

class MachineAnalyzer:
    """Main analyzer coordinating all components"""

    def __init__(self):
        self.loader = MachineDataLoader()
        self.baseline_calc = BaselineCalculator(window_size=100)
        self.anomaly_detector = AnomalyDetector(self.baseline_calc)

        self.is_running = False
        self.is_paused = False
        self.current_machine = None
        self.update_frequency = 1  # seconds between updates
        self.metrics_buffer = deque(maxlen=60)  # 60-second window
        self.alerts_buffer = deque(maxlen=20)  # Last 20 alerts
        self.current_anomaly_score = 0.0

        self.callbacks = []  # For WebSocket notifications

    def register_callback(self, callback):
        """Register callback for real-time updates"""
        self.callbacks.append(callback)

    def notify_update(self, data):
        """Notify all callbacks of update"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")

    def start_simulation(self, machine_name: str, update_freq: float = 1.0):
        """Start analyzing a machine"""
        if self.loader.load_machine(machine_name):
            self.current_machine = machine_name
            self.is_running = True
            self.is_paused = False
            self.update_frequency = update_freq
            return True
        return False

    def pause(self):
        """Pause simulation"""
        self.is_paused = True

    def resume(self):
        """Resume simulation"""
        self.is_paused = False

    def reset(self):
        """Reset simulation"""
        self.is_running = False
        self.is_paused = False
        self.loader.close()
        self.baseline_calc = BaselineCalculator()
        self.anomaly_detector = AnomalyDetector(self.baseline_calc)
        self.metrics_buffer.clear()
        self.alerts_buffer.clear()
        self.current_anomaly_score = 0.0

    def process_next_row(self) -> Dict:
        """Process next row and return analysis"""
        if not self.is_running or self.is_paused:
            return None

        row = self.loader.get_next_row()
        if not row:
            self.is_running = False
            return None

        # Calculate anomaly and get metrics
        anomaly_score, metrics = self.anomaly_detector.calculate_anomaly_score(row)
        self.current_anomaly_score = anomaly_score

        # Add metrics to buffer
        for metric in metrics:
            self.metrics_buffer.append(asdict(metric))

        # Detect faults
        faults = self.anomaly_detector.detect_faults(row, anomaly_score)

        # Create alert if threshold exceeded
        if anomaly_score > self.anomaly_detector.anomaly_threshold:
            alert_severity = "CRITICAL" if anomaly_score > 0.75 else "HIGH" if anomaly_score > 0.60 else "MEDIUM"

            alert = AnomalyAlert(
                timestamp=time.time(),
                anomaly_score=anomaly_score,
                severity=alert_severity,
                affected_metrics=[m["feature_name"] for m in list(self.metrics_buffer)[-10:]],
                detected_faults=[f[1] for f in faults],
                recommendations=[]
            )

            # Add recommendations from detected faults
            for fault_id, fault_name, severity, affected, recs in faults:
                alert.recommendations.extend(recs)

            self.alerts_buffer.append(asdict(alert))

        return {
            "timestamp": time.time(),
            "machine": self.current_machine,
            "anomaly_score": round(anomaly_score, 4),
            "metrics": list(self.metrics_buffer)[-38:],  # Last 38 (one row)
            "alerts": list(self.alerts_buffer),
            "detected_faults": [
                {
                    "id": f[0],
                    "name": f[1],
                    "severity": f[2],
                    "affected_metrics": f[3],
                    "recommendations": f[4]
                }
                for f in faults
            ]
        }

    def run_stream(self):
        """Run the analysis stream (for threading)"""
        while self.is_running:
            if not self.is_paused:
                data = self.process_next_row()
                if data:
                    self.notify_update(data)

            time.sleep(self.update_frequency)

# Export for Flask integration
analyzer = MachineAnalyzer()
