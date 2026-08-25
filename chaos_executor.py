"""
Chaos Injection Executor - Run chaos simulations with live output capture
Streams all outputs (console, metrics, graphs) to browser via WebSocket
"""

import io
import sys
import json
import base64
import threading
import traceback
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Callable, Optional

# Data science
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Custom modules
sys.path.insert(0, '.')
from src.chaos_simulator import ChaosSimulator
from src.preprocess import engineer_features, normalise_features
from src.detect import train_isolation_forest, score_observations, calibrate_threshold
from src.classify import IssueClassifier


class ChaosExecutor:
    """Execute chaos simulations with output capture and streaming."""

    def __init__(self, emit_callback: Optional[Callable] = None):
        """
        Initialize executor.

        Args:
            emit_callback: Function to emit WebSocket messages (for streaming output)
        """
        self.emit = emit_callback or self._default_emit
        self.execution_id = None
        self.outputs = []
        self.results = {}

    def _default_emit(self, event_type: str, data: Dict) -> None:
        """Default emit function (no-op)."""
        print(f"[{event_type}] {data.get('message', '')}")

    def _emit_output(self, message: str, level: str = "info") -> None:
        """Emit console output to browser."""
        self.emit('simulation_output', {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            'level': level,
            'execution_id': self.execution_id
        })
        self.outputs.append({'message': message, 'level': level})

    def _emit_step(self, step: str, status: str, details: Dict = None) -> None:
        """Emit execution step update."""
        self.emit('simulation_step', {
            'timestamp': datetime.utcnow().isoformat(),
            'step': step,
            'status': status,  # running, completed, failed
            'details': details or {},
            'execution_id': self.execution_id
        })

    def _emit_chart(self, chart_name: str, figure) -> None:
        """Emit matplotlib chart as base64 image."""
        try:
            # Convert to PNG in memory
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)

            # Encode to base64
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            self.emit('simulation_chart', {
                'timestamp': datetime.utcnow().isoformat(),
                'chart_name': chart_name,
                'image': f'data:image/png;base64,{image_base64}',
                'execution_id': self.execution_id
            })

            plt.close(figure)
        except Exception as e:
            self._emit_output(f"Error encoding chart {chart_name}: {e}", "error")

    def _emit_data(self, data_name: str, data: pd.DataFrame) -> None:
        """Emit data table."""
        try:
            # Convert to dict for JSON serialization
            data_dict = {
                'name': data_name,
                'shape': data.shape,
                'columns': list(data.columns),
                'head': data.head(10).to_dict('records'),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'stats': data.describe().to_dict()
            }

            self.emit('simulation_data', {
                'timestamp': datetime.utcnow().isoformat(),
                'data': data_dict,
                'execution_id': self.execution_id
            })
        except Exception as e:
            self._emit_output(f"Error serializing data {data_name}: {e}", "error")

    def run_simulation(self, config: Dict) -> Dict[str, Any]:
        """
        Run complete chaos injection simulation pipeline.

        Args:
            config: Configuration dict with parameters

        Returns:
            Dictionary with simulation results
        """
        self.execution_id = config.get('execution_id', 'sim_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
        self.outputs = []
        self.results = {}

        try:
            # STEP 1: Generate Chaos Data
            self._emit_step('chaos_generation', 'running')
            self._emit_output(f"🚀 Starting Chaos Injection Simulation (ID: {self.execution_id})", 'info')

            self._chaos_generation(config)
            self._emit_step('chaos_generation', 'completed', {
                'services_simulated': len(self.results.get('fault_log', []))
            })

            # STEP 2: Preprocess Data
            self._emit_step('preprocessing', 'running')
            self._preprocess_data()
            self._emit_step('preprocessing', 'completed')

            # STEP 3: Anomaly Detection
            self._emit_step('detection', 'running')
            self._anomaly_detection()
            self._emit_step('detection', 'completed', {
                'anomalies_found': len(self.results.get('anomalies', []))
            })

            # STEP 4: Classification
            self._emit_step('classification', 'running')
            self._issue_classification()
            self._emit_step('classification', 'completed', {
                'issues_classified': len(self.results.get('classified_issues', []))
            })

            # STEP 5: Generate Visualizations
            self._emit_step('visualization', 'running')
            self._generate_visualizations()
            self._emit_step('visualization', 'completed')

            self._emit_output("✅ Simulation completed successfully!", 'success')

            return {
                'status': 'success',
                'execution_id': self.execution_id,
                'results': self.results,
                'outputs': self.outputs
            }

        except Exception as e:
            error_msg = f"❌ Simulation failed: {str(e)}\n{traceback.format_exc()}"
            self._emit_output(error_msg, 'error')
            self._emit_step('error', 'failed', {'error': str(e)})

            return {
                'status': 'error',
                'execution_id': self.execution_id,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def _chaos_generation(self, config: Dict) -> None:
        """Generate chaos-injected metrics."""
        self._emit_output("📊 Generating chaos-injected metrics...", 'info')

        # Initialize simulator
        simulator = ChaosSimulator(
            base_metrics=config.get('num_metrics', 50),
            noise_level=config.get('noise_level', 0.1)
        )

        self._emit_output(f"   • Metrics: {simulator.base_metrics}", 'debug')
        self._emit_output(f"   • Noise level: {simulator.noise_level}", 'debug')
        self._emit_output(f"   • Services: {list(simulator.services.keys())}", 'debug')

        # Generate metrics for each service
        all_metrics = {}
        for service_name, fault_config in simulator.services.items():
            self._emit_output(f"   • Injecting {fault_config['type']} into {service_name}...", 'debug')

            # Generate healthy baseline
            healthy = simulator.generate_healthy_metrics(service_name)

            # Inject fault
            if fault_config['type'] == 'memory_leak':
                injected = simulator.inject_memory_leak(
                    healthy,
                    fault_config['start'],
                    fault_config['duration']
                )
            elif fault_config['type'] == 'high_latency':
                injected = simulator.inject_high_latency(
                    healthy,
                    fault_config['start'],
                    fault_config['duration']
                )
            else:  # error_spike
                injected = simulator.inject_error_spike(
                    healthy,
                    fault_config['start'],
                    fault_config['duration']
                )

            all_metrics[service_name] = injected

        # Create DataFrame
        df_metrics = pd.DataFrame(all_metrics)
        df_metrics['timestamp'] = pd.date_range(start='2024-01-01', periods=len(df_metrics), freq='1min')

        self._emit_output(f"✅ Generated {len(df_metrics)} metric samples from {len(all_metrics)} services", 'success')
        self._emit_data('Raw_Metrics', df_metrics)

        # Store results
        self.results['metrics'] = df_metrics
        self.results['fault_log'] = simulator.fault_log
        self.results['services'] = list(all_metrics.keys())

    def _preprocess_data(self) -> None:
        """Preprocess metrics data."""
        self._emit_output("🔧 Preprocessing metrics...", 'info')

        df = self.results['metrics'].copy()

        # Feature engineering
        self._emit_output("   • Engineering features...", 'debug')
        df_features = engineer_features(df)

        # Normalization
        self._emit_output("   • Normalizing features...", 'debug')
        df_normalized, scaler = normalise_features(df_features)

        self._emit_output(f"✅ Preprocessed {len(df_normalized)} samples with {len(df_normalized.columns)} features", 'success')
        self._emit_data('Preprocessed_Data', df_normalized)

        self.results['preprocessed'] = df_normalized
        self.results['scaler'] = scaler

    def _anomaly_detection(self) -> None:
        """Detect anomalies using Isolation Forest."""
        self._emit_output("🔍 Detecting anomalies...", 'info')

        df_preprocessed = self.results['preprocessed']

        # Train model
        self._emit_output("   • Training Isolation Forest...", 'debug')
        model, X_train = train_isolation_forest(df_preprocessed)

        # Score all observations
        self._emit_output("   • Scoring observations...", 'debug')
        scores = score_observations(model, df_preprocessed)

        # Calibrate threshold
        self._emit_output("   • Calibrating anomaly threshold...", 'debug')
        threshold = calibrate_threshold(scores, contamination=0.1)

        # Identify anomalies
        anomalies = scores > threshold
        num_anomalies = anomalies.sum()

        self._emit_output(f"✅ Detected {num_anomalies} anomalies (threshold: {threshold:.4f})", 'success')

        self.results['model'] = model
        self.results['scores'] = scores
        self.results['threshold'] = threshold
        self.results['anomalies'] = anomalies

    def _issue_classification(self) -> None:
        """Classify detected issues."""
        self._emit_output("🏷️ Classifying issues...", 'info')

        df_metrics = self.results['metrics']
        anomalies = self.results['anomalies']

        # Get anomaly timestamps
        anomaly_indices = np.where(anomalies)[0]

        # Simple classification based on anomaly patterns
        classified_issues = []

        for idx in anomaly_indices[:10]:  # Limit to first 10 for demo
            if idx < len(df_metrics):
                row = df_metrics.iloc[idx]

                # Classify based on metric patterns
                issue_type = "Unknown"
                confidence = 0.5

                if 'service_a' in df_metrics.columns and row['service_a'] > df_metrics['service_a'].mean() * 1.5:
                    issue_type = "Memory Leak"
                    confidence = 0.85
                elif 'service_b' in df_metrics.columns and row['service_b'] > df_metrics['service_b'].mean() * 2:
                    issue_type = "High Latency"
                    confidence = 0.90
                elif 'service_c' in df_metrics.columns and row['service_c'] > df_metrics['service_c'].mean() * 1.5:
                    issue_type = "Error Spike"
                    confidence = 0.75

                classified_issues.append({
                    'timestamp': str(row.get('timestamp', f'T_{idx}')),
                    'type': issue_type,
                    'confidence': confidence,
                    'metrics': {k: float(v) for k, v in row.items() if k != 'timestamp'}
                })

        self._emit_output(f"✅ Classified {len(classified_issues)} issues", 'success')
        self.results['classified_issues'] = classified_issues

    def _generate_visualizations(self) -> None:
        """Generate charts and visualizations."""
        self._emit_output("📈 Generating visualizations...", 'info')

        df_metrics = self.results['metrics']
        scores = self.results['scores']
        anomalies = self.results['anomalies']

        # 1. Time series with anomalies
        self._emit_output("   • Creating time series plot...", 'debug')
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot metrics
        for col in [c for c in df_metrics.columns if c != 'timestamp']:
            ax.plot(df_metrics[col], label=col, alpha=0.7)

        # Highlight anomalies
        if len(anomalies) > 0:
            ax.scatter(np.where(anomalies)[0], df_metrics.iloc[:, :-1].values[anomalies].mean(axis=1),
                      color='red', s=100, marker='X', label='Anomalies', zorder=5)

        ax.set_title('Chaos Injection: Metrics with Detected Anomalies', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time Index')
        ax.set_ylabel('Metric Value')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self._emit_chart('Time_Series_With_Anomalies', fig)

        # 2. Anomaly score distribution
        self._emit_output("   • Creating anomaly score distribution...", 'debug')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(scores, bins=30, alpha=0.7, label='Scores', color='blue')
        ax.axvline(self.results['threshold'], color='red', linestyle='--', linewidth=2, label=f'Threshold')
        ax.set_title('Anomaly Detection Score Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Anomaly Score')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self._emit_chart('Anomaly_Score_Distribution', fig)

        # 3. Service comparison heatmap
        self._emit_output("   • Creating service correlation heatmap...", 'debug')
        fig, ax = plt.subplots(figsize=(10, 8))

        # Calculate correlation
        service_cols = [c for c in df_metrics.columns if c != 'timestamp']
        if len(service_cols) > 1:
            corr_matrix = df_metrics[service_cols].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, ax=ax, cbar_kws={'label': 'Correlation'})
            ax.set_title('Service Metrics Correlation Matrix', fontsize=14, fontweight='bold')

        self._emit_chart('Correlation_Heatmap', fig)

        self._emit_output("✅ Visualizations generated", 'success')
