"""
Chaos Simulation Export Module
Generates PNG visualizations and CSV data exports from simulation results
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
from sklearn.metrics import confusion_matrix, classification_report
from io import StringIO, BytesIO
import base64


class SimulationExporter:
    """Export simulation results to PNG and CSV formats"""

    def __init__(self, output_dir: str = 'simulation_exports'):
        """Initialize exporter

        Args:
            output_dir: Directory to save exports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_dir = os.path.join(output_dir, f'sim_{self.timestamp}')
        os.makedirs(self.session_dir, exist_ok=True)

    # ========== CSV EXPORTS ==========

    def export_chaos_simulation_csv(self, metrics_df: pd.DataFrame) -> str:
        """Export raw chaos simulation metrics to CSV"""
        filename = os.path.join(self.session_dir, 'chaos_simulation.csv')
        metrics_df.to_csv(filename, index=False)
        return filename

    def export_classification_results_csv(self, y_true: List, y_pred: List) -> str:
        """Export classification results"""
        filename = os.path.join(self.session_dir, 'classification_results.csv')

        df = pd.DataFrame({
            'actual': y_true,
            'predicted': y_pred,
            'correct': [1 if a == p else 0 for a, p in zip(y_true, y_pred)]
        })
        df.to_csv(filename, index=False)
        return filename

    def export_incident_log_csv(self, incidents: List[Dict]) -> str:
        """Export incident detection log"""
        filename = os.path.join(self.session_dir, 'incident_log.csv')

        df = pd.DataFrame(incidents)
        df.to_csv(filename, index=False)
        return filename

    def export_response_log_csv(self, responses: List[Dict]) -> str:
        """Export response/remediation log"""
        filename = os.path.join(self.session_dir, 'response_log.csv')

        df = pd.DataFrame(responses)
        df.to_csv(filename, index=False)
        return filename

    def export_remediation_results_csv(self, results: List[Dict]) -> str:
        """Export remediation results"""
        filename = os.path.join(self.session_dir, 'remediation_results.csv')

        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        return filename

    def export_threshold_calibration_csv(self, calibration_data: Dict) -> str:
        """Export threshold calibration data"""
        filename = os.path.join(self.session_dir, 'threshold_calibration.csv')

        data = {
            'metric': list(calibration_data.keys()),
            'threshold': [calibration_data[k].get('threshold', 0) for k in calibration_data.keys()],
            'precision': [calibration_data[k].get('precision', 0) for k in calibration_data.keys()],
            'recall': [calibration_data[k].get('recall', 0) for k in calibration_data.keys()],
            'f1_score': [calibration_data[k].get('f1_score', 0) for k in calibration_data.keys()]
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename

    def export_metrics_comparison_csv(self, metrics: List[Dict]) -> str:
        """Export metrics comparison"""
        filename = os.path.join(self.session_dir, 'metrics_comparison.csv')

        df = pd.DataFrame(metrics)
        df.to_csv(filename, index=False)
        return filename

    def export_dos_simulation_analysis_csv(self, dos_data: Dict) -> str:
        """Export DoS simulation analysis"""
        filename = os.path.join(self.session_dir, 'dos_simulation_analysis.csv')

        # Flatten DoS data structure
        rows = []
        for timestamp, metrics in dos_data.items():
            row = {'timestamp': timestamp}
            row.update(metrics)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        return filename

    # ========== PNG EXPORTS ==========

    def export_confusion_matrix_png(self, y_true: List, y_pred: List,
                                    title: str = "Confusion Matrix") -> str:
        """Generate confusion matrix PNG"""
        filename = os.path.join(self.session_dir, 'confusion_matrix_mvp.png')

        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.colorbar()

        # Add text annotations
        tick_marks = np.arange(len(np.unique(y_true)))
        plt.xticks(tick_marks, np.unique(y_true))
        plt.yticks(tick_marks, np.unique(y_true))

        # Add numbers to cells
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j] > cm.max() / 2 else 'black')

        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    def export_confusion_matrix_supervised_png(self, y_true: List, y_pred: List) -> str:
        """Generate supervised confusion matrix PNG"""
        return self.export_confusion_matrix_png(y_true, y_pred,
                                               "Supervised Learning Confusion Matrix")

    def export_feature_importance_png(self, features: Dict[str, float]) -> str:
        """Generate feature importance bar chart"""
        filename = os.path.join(self.session_dir, 'feature_importance.png')

        # Sort by importance
        sorted_features = dict(sorted(features.items(),
                                     key=lambda x: x[1],
                                     reverse=True))

        plt.figure(figsize=(12, 6))
        names = list(sorted_features.keys())[:15]  # Top 15
        values = list(sorted_features.values())[:15]

        bars = plt.barh(names, values, color='steelblue')

        # Color gradient
        for i, bar in enumerate(bars):
            bar.set_color(plt.cm.viridis(i / len(bars)))

        plt.xlabel('Importance Score', fontsize=12)
        plt.title('Feature Importance (Top 15)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    def export_feature_importance_mvp_png(self, features: Dict[str, float]) -> str:
        """Generate MVP feature importance PNG"""
        filename = os.path.join(self.session_dir, 'feature_importance_mvp.png')

        sorted_features = dict(sorted(features.items(), key=lambda x: x[1], reverse=True))

        plt.figure(figsize=(10, 6))
        names = list(sorted_features.keys())[:10]  # Top 10 for MVP
        values = list(sorted_features.values())[:10]

        plt.bar(range(len(names)), values, color='coral')
        plt.xticks(range(len(names)), names, rotation=45, ha='right')
        plt.ylabel('Importance', fontsize=12)
        plt.title('Top 10 Feature Importance (MVP)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    def export_dos_simulation_analysis_png(self, dos_data: Dict) -> str:
        """Generate DoS attack simulation visualization"""
        filename = os.path.join(self.session_dir, 'dos_simulation_analysis.png')

        # Extract time series data
        timestamps = []
        request_rates = []
        error_rates = []

        for ts, metrics in dos_data.items():
            timestamps.append(ts)
            request_rates.append(metrics.get('request_rate', 0))
            error_rates.append(metrics.get('error_rate', 0))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Request rate
        ax1.plot(range(len(timestamps)), request_rates, marker='o', color='blue', linewidth=2)
        ax1.set_ylabel('Request Rate (req/s)', fontsize=11)
        ax1.set_title('DoS Attack Simulation: Request Rate', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Error rate
        ax2.plot(range(len(timestamps)), error_rates, marker='s', color='red', linewidth=2)
        ax2.set_ylabel('Error Rate (%)', fontsize=11)
        ax2.set_xlabel('Time', fontsize=11)
        ax2.set_title('DoS Attack Simulation: Error Rate', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    def export_threshold_calibration_png(self, calibration_data: Dict) -> str:
        """Generate threshold calibration curve"""
        filename = os.path.join(self.session_dir, 'threshold_calibration.png')

        metrics = list(calibration_data.keys())
        precisions = [calibration_data[m].get('precision', 0) for m in metrics]
        recalls = [calibration_data[m].get('recall', 0) for m in metrics]
        f1_scores = [calibration_data[m].get('f1_score', 0) for m in metrics]

        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(len(metrics[:8]))  # Top 8
        width = 0.25

        ax.bar(x - width, precisions[:8], width, label='Precision', color='skyblue')
        ax.bar(x, recalls[:8], width, label='Recall', color='lightcoral')
        ax.bar(x + width, f1_scores[:8], width, label='F1 Score', color='lightgreen')

        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Threshold Calibration Results', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics[:8], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    def export_metrics_comparison_png(self, metrics_list: List[Dict]) -> str:
        """Generate metrics comparison chart"""
        filename = os.path.join(self.session_dir, 'metrics_comparison.png')

        df = pd.DataFrame(metrics_list)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Accuracy comparison
        if 'accuracy' in df.columns:
            axes[0, 0].bar(range(len(df)), df['accuracy'], color='steelblue')
            axes[0, 0].set_title('Accuracy Comparison', fontweight='bold')
            axes[0, 0].set_ylabel('Accuracy')

        # Precision comparison
        if 'precision' in df.columns:
            axes[0, 1].bar(range(len(df)), df['precision'], color='coral')
            axes[0, 1].set_title('Precision Comparison', fontweight='bold')
            axes[0, 1].set_ylabel('Precision')

        # Recall comparison
        if 'recall' in df.columns:
            axes[1, 0].bar(range(len(df)), df['recall'], color='lightgreen')
            axes[1, 0].set_title('Recall Comparison', fontweight='bold')
            axes[1, 0].set_ylabel('Recall')

        # F1 Score comparison
        if 'f1_score' in df.columns:
            axes[1, 1].bar(range(len(df)), df['f1_score'], color='gold')
            axes[1, 1].set_title('F1 Score Comparison', fontweight='bold')
            axes[1, 1].set_ylabel('F1 Score')

        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        return filename

    # ========== BATCH EXPORT ==========

    def export_all(self, simulation_data: Dict) -> Dict[str, str]:
        """Export all available formats

        Args:
            simulation_data: Dict containing all simulation results

        Returns:
            Dict mapping export type to file path
        """
        exports = {}

        # CSV Exports
        if 'metrics' in simulation_data:
            exports['chaos_simulation_csv'] = self.export_chaos_simulation_csv(
                simulation_data['metrics']
            )

        if 'classification' in simulation_data:
            y_true = simulation_data['classification'].get('y_true', [])
            y_pred = simulation_data['classification'].get('y_pred', [])
            exports['classification_results_csv'] = self.export_classification_results_csv(
                y_true, y_pred
            )

        if 'incidents' in simulation_data:
            exports['incident_log_csv'] = self.export_incident_log_csv(
                simulation_data['incidents']
            )

        if 'responses' in simulation_data:
            exports['response_log_csv'] = self.export_response_log_csv(
                simulation_data['responses']
            )

        if 'remediation' in simulation_data:
            exports['remediation_results_csv'] = self.export_remediation_results_csv(
                simulation_data['remediation']
            )

        if 'threshold_calibration' in simulation_data:
            exports['threshold_calibration_csv'] = self.export_threshold_calibration_csv(
                simulation_data['threshold_calibration']
            )

        if 'metrics_comparison' in simulation_data:
            exports['metrics_comparison_csv'] = self.export_metrics_comparison_csv(
                simulation_data['metrics_comparison']
            )

        if 'dos_analysis' in simulation_data:
            exports['dos_simulation_analysis_csv'] = self.export_dos_simulation_analysis_csv(
                simulation_data['dos_analysis']
            )

        # PNG Exports
        if 'classification' in simulation_data:
            y_true = simulation_data['classification'].get('y_true', [])
            y_pred = simulation_data['classification'].get('y_pred', [])

            exports['confusion_matrix_mvp_png'] = self.export_confusion_matrix_png(
                y_true, y_pred
            )
            exports['confusion_matrix_supervised_png'] = self.export_confusion_matrix_supervised_png(
                y_true, y_pred
            )

        if 'features' in simulation_data:
            exports['feature_importance_png'] = self.export_feature_importance_png(
                simulation_data['features']
            )
            exports['feature_importance_mvp_png'] = self.export_feature_importance_mvp_png(
                simulation_data['features']
            )

        if 'dos_analysis' in simulation_data:
            exports['dos_simulation_analysis_png'] = self.export_dos_simulation_analysis_png(
                simulation_data['dos_analysis']
            )

        if 'threshold_calibration' in simulation_data:
            exports['threshold_calibration_png'] = self.export_threshold_calibration_png(
                simulation_data['threshold_calibration']
            )

        if 'metrics_comparison' in simulation_data:
            exports['metrics_comparison_png'] = self.export_metrics_comparison_png(
                simulation_data['metrics_comparison']
            )

        return exports

    def create_export_manifest(self, exports: Dict[str, str]) -> str:
        """Create manifest file listing all exports"""
        manifest_file = os.path.join(self.session_dir, 'MANIFEST.json')

        manifest = {
            'timestamp': self.timestamp,
            'export_directory': self.session_dir,
            'exports': exports,
            'file_count': len(exports),
            'csv_exports': [k for k in exports.keys() if 'csv' in k],
            'png_exports': [k for k in exports.keys() if 'png' in k]
        }

        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest_file


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == '__main__':
    # Example usage
    exporter = SimulationExporter()

    # Prepare sample data
    sample_data = {
        'metrics': pd.DataFrame({
            'timestamp': pd.date_range('2026-08-26', periods=100, freq='1S'),
            'cpu': np.random.rand(100) * 100,
            'memory': np.random.rand(100) * 100
        }),
        'classification': {
            'y_true': [0, 1, 0, 1, 1] * 20,
            'y_pred': [0, 1, 0, 0, 1] * 20
        },
        'features': {
            'cpu_usage': 0.95,
            'memory_usage': 0.87,
            'network_io': 0.76,
            'disk_usage': 0.65,
            'process_count': 0.54
        }
    }

    # Export all
    exports = exporter.export_all(sample_data)
    print(f"Exports created: {len(exports)}")
    for export_type, filepath in exports.items():
        print(f"  ✓ {export_type}: {filepath}")
