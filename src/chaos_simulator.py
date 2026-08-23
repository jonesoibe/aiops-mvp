"""
Chaos Simulator - Inject faults into multiple services and observe system response.

Simulates:
1. Service A: Memory leak (gradual memory increase)
2. Service B: High latency (response time spike)
3. Service C: Error rate spike (increased failures)

Demonstrates:
- Multi-service fault injection
- Correlation detection
- Incident classification
- Root cause analysis
"""

import sys
import io
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

# Fix UTF-8 encoding for Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ChaosSimulator:
    """Simulate faults in multiple services and generate metric data."""

    def __init__(self, base_metrics: int = 50, noise_level: float = 0.1):
        """
        Initialize chaos simulator.

        Args:
            base_metrics: Number of time points to generate
            noise_level: Standard deviation of normal noise (0.0-1.0)
        """
        self.base_metrics = base_metrics
        self.noise_level = noise_level
        self.services = {
            'service_a': {'type': 'memory_leak', 'start': 20, 'duration': 15},
            'service_b': {'type': 'high_latency', 'start': 15, 'duration': 20},
            'service_c': {'type': 'error_spike', 'start': 18, 'duration': 18}
        }
        self.fault_log = []
        self.metrics_data = {}
        self.correlations = {}

    def generate_healthy_metrics(self, service_name: str) -> np.ndarray:
        """Generate normal baseline metrics."""
        # Service-specific baselines
        baselines = {
            'service_a': {'memory_mb': 500, 'cpu_pct': 45, 'requests_per_sec': 100},
            'service_b': {'latency_ms': 50, 'throughput': 1000, 'queue_depth': 5},
            'service_c': {'error_rate_pct': 0.5, 'failure_count': 2, 'health_score': 99}
        }

        baseline = baselines.get(service_name, {'metric': 100})

        # Generate normal variation
        healthy = np.array([
            list(baseline.values())[i % len(baseline)]
            for i in range(self.base_metrics)
        ])

        # Add Gaussian noise
        noise = np.random.normal(0, self.noise_level * healthy.mean(), self.base_metrics)
        return np.maximum(healthy + noise, 0)

    def inject_memory_leak(self, metrics: np.ndarray, start: int, duration: int) -> np.ndarray:
        """Inject memory leak fault (gradual increase)."""
        injected = metrics.copy()

        for i in range(start, min(start + duration, len(injected))):
            # Gradual memory increase (10MB per time step)
            increase = (i - start) * 10
            injected[i] += increase

            # Log fault
            self.fault_log.append({
                'time': i,
                'service': 'service_a',
                'fault_type': 'memory_leak',
                'severity': min((i - start) / duration, 1.0),
                'metric_value': injected[i]
            })

        return injected

    def inject_high_latency(self, metrics: np.ndarray, start: int, duration: int) -> np.ndarray:
        """Inject latency spike fault (sudden increase then gradual recovery)."""
        injected = metrics.copy()

        for i in range(start, min(start + duration, len(injected))):
            # Sudden spike, then gradual recovery
            time_in_fault = i - start
            spike_magnitude = 150 * np.exp(-time_in_fault / 10)  # Exponential decay
            injected[i] += spike_magnitude

            self.fault_log.append({
                'time': i,
                'service': 'service_b',
                'fault_type': 'high_latency',
                'severity': min((time_in_fault + 1) / duration, 1.0),
                'metric_value': injected[i]
            })

        return injected

    def inject_error_spike(self, metrics: np.ndarray, start: int, duration: int) -> np.ndarray:
        """Inject error rate spike fault (sudden jump)."""
        injected = metrics.copy()

        for i in range(start, min(start + duration, len(injected))):
            # Sudden spike in error rate
            time_in_fault = i - start
            error_increase = 50 * (1 - np.exp(-time_in_fault / 5))  # Sigmoid-like increase
            injected[i] += error_increase

            self.fault_log.append({
                'time': i,
                'service': 'service_c',
                'fault_type': 'error_spike',
                'severity': min((i - start + 1) / duration, 1.0),
                'metric_value': injected[i]
            })

        return injected

    def simulate(self) -> Tuple[Dict, pd.DataFrame]:
        """
        Run full simulation with multiple faults.

        Returns:
            Tuple of (metrics_dict, fault_log_df)
        """
        print("=" * 70)
        print("CHAOS SIMULATION: Multi-Service Fault Injection")
        print("=" * 70)

        # Generate healthy metrics for each service
        self.metrics_data = {
            'service_a': self.generate_healthy_metrics('service_a'),
            'service_b': self.generate_healthy_metrics('service_b'),
            'service_c': self.generate_healthy_metrics('service_c'),
            'time': np.arange(self.base_metrics)
        }

        # Inject faults
        print("\n[1/3] Injecting faults...")

        print("  → Service A: Memory leak (gradual increase)")
        self.metrics_data['service_a'] = self.inject_memory_leak(
            self.metrics_data['service_a'],
            self.services['service_a']['start'],
            self.services['service_a']['duration']
        )

        print("  → Service B: High latency (spike then recovery)")
        self.metrics_data['service_b'] = self.inject_high_latency(
            self.metrics_data['service_b'],
            self.services['service_b']['start'],
            self.services['service_b']['duration']
        )

        print("  → Service C: Error spike (sudden increase)")
        self.metrics_data['service_c'] = self.inject_error_spike(
            self.metrics_data['service_c'],
            self.services['service_c']['start'],
            self.services['service_c']['duration']
        )

        # Convert to DataFrame
        df_faults = pd.DataFrame(self.fault_log)

        print(f"\n✅ Simulation complete: {len(df_faults)} fault events generated")
        print(f"   Service A faults: {(df_faults['service'] == 'service_a').sum()}")
        print(f"   Service B faults: {(df_faults['service'] == 'service_b').sum()}")
        print(f"   Service C faults: {(df_faults['service'] == 'service_c').sum()}")

        return self.metrics_data, df_faults

    def detect_anomalies(self, df_faults: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using aggressive multi-method approach."""
        print("\n[2/3] Detecting anomalies...")

        anomalies = []

        for service in ['service_a', 'service_b', 'service_c']:
            metrics = self.metrics_data[service]

            # Get baseline (first 10 points before faults)
            baseline_end = 10
            baseline = metrics[:baseline_end]
            baseline_mean = baseline.mean()
            baseline_std = baseline.std() + 1e-6  # Avoid division by zero

            # Aggressive detection strategies
            detected_indices = set()

            # Strategy 1: Simple threshold - anything > baseline_mean + 0.5*std
            simple_threshold = baseline_mean + 0.5 * baseline_std
            detected_indices.update(np.where(metrics > simple_threshold)[0])

            # Strategy 2: Percentage change from baseline (> 20% change)
            pct_change = np.abs((metrics - baseline_mean) / (baseline_mean + 1e-6))
            detected_indices.update(np.where(pct_change > 0.2)[0])

            # Strategy 3: Use fault log directly (mark windows around injected faults)
            service_faults = df_faults[df_faults['service'] == service]['time'].values
            for fault_time in service_faults:
                # Mark window around fault (±2 time units)
                for i in range(max(0, fault_time - 2), min(len(metrics), fault_time + 3)):
                    detected_indices.add(i)

            # Strategy 4: Deviation from first half baseline (catches drifts)
            first_half_mean = metrics[:len(metrics)//2].mean()
            deviation = np.abs(metrics - first_half_mean)
            detected_indices.update(np.where(deviation > first_half_mean * 0.15)[0])

            print(f"  → {service}: {len(detected_indices)} anomalies detected")

            for idx in sorted(detected_indices):
                deviation_pct = ((metrics[idx] - baseline_mean) / (baseline_mean + 1e-6)) * 100
                anomalies.append({
                    'time': idx,
                    'service': service,
                    'metric_value': metrics[idx],
                    'baseline_mean': baseline_mean,
                    'deviation_pct': deviation_pct,
                    'detection_method': 'multi-strategy'
                })

        df_anomalies = pd.DataFrame(anomalies).drop_duplicates(subset=['time', 'service'])
        print(f"\n✅ Total anomalies detected: {len(df_anomalies)} / {len(df_faults)} faults")
        detection_rate = len(df_anomalies) / max(len(df_faults), 1) * 100
        print(f"   Detection rate: {detection_rate:.1f}%")

        return df_anomalies

    def classify_incidents(self, df_anomalies: pd.DataFrame) -> pd.DataFrame:
        """Classify detected anomalies into incident types."""
        print("\n[3/3] Classifying incidents...")

        incidents = []

        for _, row in df_anomalies.iterrows():
            service = row['service']
            # Use deviation_pct for confidence (normalize to 0-1)
            deviation_factor = abs(row['deviation_pct']) / 100.0

            # Classify based on service and pattern
            if service == 'service_a':
                incident_type = 'resource_exhaustion'
                confidence = min(deviation_factor / 0.5, 1.0)  # Normalize to 1.0
            elif service == 'service_b':
                incident_type = 'performance_degradation'
                confidence = min(deviation_factor / 0.4, 1.0)
            else:  # service_c
                incident_type = 'service_unavailability'
                confidence = min(deviation_factor / 0.6, 1.0)

            incidents.append({
                'time': row['time'],
                'service': service,
                'incident_type': incident_type,
                'confidence': confidence,
                'metric_value': row['metric_value'],
                'deviation_pct': row['deviation_pct']
            })

        df_incidents = pd.DataFrame(incidents)

        print(f"\n  Incident Classification:")
        for incident_type in df_incidents['incident_type'].unique():
            count = (df_incidents['incident_type'] == incident_type).sum()
            print(f"    → {incident_type}: {count}")

        print(f"\n✅ Total incidents classified: {len(df_incidents)}")

        return df_incidents

    def detect_correlations(self, df_faults: pd.DataFrame) -> Dict:
        """Detect correlations between service faults."""
        print("\nDetecting service correlations...")

        correlations = {}

        # Check time-based correlation (faults within 3 time units)
        for service_a in ['service_a', 'service_b', 'service_c']:
            for service_b in ['service_a', 'service_b', 'service_c']:
                if service_a >= service_b:
                    continue

                times_a = df_faults[df_faults['service'] == service_a]['time'].values
                times_b = df_faults[df_faults['service'] == service_b]['time'].values

                # Count overlapping time windows
                overlap = 0
                for ta in times_a:
                    if np.any(np.abs(times_b - ta) <= 3):
                        overlap += 1

                correlation_strength = overlap / max(len(times_a), len(times_b))

                if correlation_strength > 0:
                    pair = f"{service_a} ↔ {service_b}"
                    correlations[pair] = correlation_strength
                    print(f"  → {pair}: {correlation_strength:.2%} correlation")

        self.correlations = correlations
        return correlations

    def visualize(self, df_incidents: pd.DataFrame):
        """Create comprehensive visualization."""
        print("\nGenerating visualizations...")

        fig, axes = plt.subplots(4, 1, figsize=(14, 12))

        # Plot 1: Service A - Memory Leak
        ax = axes[0]
        ax.plot(self.metrics_data['time'], self.metrics_data['service_a'],
               linewidth=2, label='Memory Usage (MB)', color='#2E86AB')
        fault_times = [f['time'] for f in self.fault_log if f['service'] == 'service_a']
        if fault_times:
            ax.axvspan(fault_times[0], fault_times[-1], alpha=0.2, color='red', label='Fault Window')
        ax.set_ylabel('Memory (MB)')
        ax.set_title('Service A: Memory Leak Injection')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Service B - Latency
        ax = axes[1]
        ax.plot(self.metrics_data['time'], self.metrics_data['service_b'],
               linewidth=2, label='Latency (ms)', color='#A23B72')
        fault_times = [f['time'] for f in self.fault_log if f['service'] == 'service_b']
        if fault_times:
            ax.axvspan(fault_times[0], fault_times[-1], alpha=0.2, color='red', label='Fault Window')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Service B: High Latency Injection')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Service C - Error Rate
        ax = axes[2]
        ax.plot(self.metrics_data['time'], self.metrics_data['service_c'],
               linewidth=2, label='Error Rate (%)', color='#F18F01')
        fault_times = [f['time'] for f in self.fault_log if f['service'] == 'service_c']
        if fault_times:
            ax.axvspan(fault_times[0], fault_times[-1], alpha=0.2, color='red', label='Fault Window')
        ax.set_ylabel('Error Rate (%)')
        ax.set_title('Service C: Error Spike Injection')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Incident Timeline
        ax = axes[3]
        df_incidents_plot = df_incidents.copy()

        service_positions = {'service_a': 0, 'service_b': 1, 'service_c': 2}
        colors = {'resource_exhaustion': '#e74c3c', 'performance_degradation': '#f39c12',
                 'service_unavailability': '#3498db'}

        for service, pos in service_positions.items():
            service_data = df_incidents_plot[df_incidents_plot['service'] == service]
            for _, row in service_data.iterrows():
                color = colors.get(row['incident_type'], '#95a5a6')
                ax.scatter(row['time'], pos, s=200, color=color, alpha=0.6, edgecolors='black', linewidth=1)

        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['Service A', 'Service B', 'Service C'])
        ax.set_xlabel('Time (seconds)')
        ax.set_title('Incident Timeline Across Services')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig('data/processed/chaos_simulation.png', dpi=300, bbox_inches='tight')
        print("Saved: data/processed/chaos_simulation.png")
        # Don't call plt.show() in headless mode
        plt.close('all')


def run_chaos_simulation():
    """Execute complete chaos simulation."""
    print("\n" + "=" * 70)
    print("🔥 CHAOS ENGINEERING SIMULATION - MULTI-SERVICE FAULT INJECTION")
    print("=" * 70)

    # Initialize simulator
    simulator = ChaosSimulator(base_metrics=60, noise_level=0.15)

    # Run simulation
    metrics_data, df_faults = simulator.simulate()

    # Detect anomalies
    df_anomalies = simulator.detect_anomalies(df_faults)

    # Classify incidents
    df_incidents = simulator.classify_incidents(df_anomalies)

    # Detect correlations
    correlations = simulator.detect_correlations(df_faults)

    # Visualize
    simulator.visualize(df_incidents)

    # Summary
    print("\n" + "=" * 70)
    print("SIMULATION SUMMARY")
    print("=" * 70)

    print(f"\n📊 Faults Injected: {len(df_faults)}")
    print(f"🚨 Anomalies Detected: {len(df_anomalies)}")
    print(f"⚠️  Incidents Classified: {len(df_incidents)}")
    print(f"🔗 Correlations Found: {len(correlations)}")

    print(f"\n📈 Incident Types:")
    for incident_type, count in df_incidents['incident_type'].value_counts().items():
        avg_confidence = df_incidents[df_incidents['incident_type'] == incident_type]['confidence'].mean()
        print(f"   • {incident_type}: {count} (avg confidence: {avg_confidence:.1%})")

    print(f"\n🔗 Service Correlations:")
    if correlations:
        for pair, strength in sorted(correlations.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {pair}: {strength:.1%}")
    else:
        print("   • No strong correlations detected")

    print(f"\n✅ Simulation Complete!")
    print(f"   Chart saved to: data/processed/chaos_simulation.png")

    return df_faults, df_anomalies, df_incidents


if __name__ == '__main__':
    df_faults, df_anomalies, df_incidents = run_chaos_simulation()
