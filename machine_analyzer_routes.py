"""
Flask routes for Machine Analyzer
Integrates with Flask-SocketIO for real-time WebSocket updates
"""

from flask import Blueprint, jsonify, request, render_template
from flask_socketio import emit, disconnect
import threading
import time
from machine_analyzer import analyzer
from analysis_visualizations import AnalysisVisualizations, EvaluationReports, IncidentLog

bp = Blueprint('machine_analyzer', __name__, url_prefix='/api/machine-analyzer')

# Store active streaming threads
streaming_threads = {}

# ==================== REST ENDPOINTS ====================

@bp.route('/machines', methods=['GET'])
def get_machines():
    """Get list of all available machines grouped by server"""
    grouped = analyzer.loader.get_machines()
    return jsonify({
        'machines': grouped,
        'total_machines': len(analyzer.loader.available_machines)
    })

@bp.route('/status', methods=['GET'])
def get_status():
    """Get current analyzer status"""
    return jsonify({
        'is_running': analyzer.is_running,
        'is_paused': analyzer.is_paused,
        'current_machine': analyzer.current_machine,
        'anomaly_score': analyzer.current_anomaly_score,
        'metrics_count': len(analyzer.metrics_buffer),
        'alerts_count': len(analyzer.alerts_buffer),
        'update_frequency': analyzer.update_frequency
    })

@bp.route('/config', methods=['GET', 'POST'])
def config():
    """Get/set analyzer configuration"""
    if request.method == 'POST':
        data = request.get_json()

        if 'anomaly_threshold' in data:
            analyzer.anomaly_detector.anomaly_threshold = data['anomaly_threshold']

        if 'update_frequency' in data:
            analyzer.update_frequency = data['update_frequency']

        if 'baseline_window' in data:
            analyzer.baseline_calc.window_size = data['baseline_window']

        if 'feature_weights' in data:
            analyzer.anomaly_detector.weights = data['feature_weights']

        return jsonify({'success': True, 'message': 'Configuration updated'})

    else:  # GET
        return jsonify({
            'anomaly_threshold': analyzer.anomaly_detector.anomaly_threshold,
            'update_frequency': analyzer.update_frequency,
            'baseline_window': analyzer.baseline_calc.window_size,
            'feature_weights': analyzer.anomaly_detector.weights
        })

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get current metrics buffer (60-second window)"""
    return jsonify({
        'metrics': list(analyzer.metrics_buffer),
        'count': len(analyzer.metrics_buffer),
        'anomaly_score': analyzer.current_anomaly_score
    })

@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alert history"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'alerts': list(analyzer.alerts_buffer)[-limit:],
        'count': len(analyzer.alerts_buffer)
    })

@bp.route('/start', methods=['POST'])
def start_analysis():
    """Start analyzing a machine"""
    data = request.get_json()
    machine_name = data.get('machine')
    update_freq = data.get('update_frequency', 1.0)

    if not machine_name:
        return jsonify({'error': 'machine parameter required'}), 400

    analyzer.reset()

    if analyzer.start_simulation(machine_name, update_freq):
        # Start streaming in background thread
        thread = threading.Thread(target=_run_stream, daemon=True)
        thread.start()
        streaming_threads[machine_name] = thread

        return jsonify({
            'success': True,
            'message': f'Analysis started for {machine_name}',
            'machine': machine_name
        })
    else:
        return jsonify({'error': 'Failed to load machine'}), 400

@bp.route('/pause', methods=['POST'])
def pause_analysis():
    """Pause current analysis"""
    analyzer.pause()
    return jsonify({'success': True, 'message': 'Analysis paused'})

@bp.route('/resume', methods=['POST'])
def resume_analysis():
    """Resume paused analysis"""
    analyzer.resume()
    return jsonify({'success': True, 'message': 'Analysis resumed'})

@bp.route('/reset', methods=['POST'])
def reset_analysis():
    """Reset analysis"""
    analyzer.reset()
    return jsonify({'success': True, 'message': 'Analysis reset'})

# ==================== HELPER FUNCTIONS ====================

def _run_stream():
    """Run the analyzer stream"""
    analyzer.run_stream()

# ==================== PAGE ROUTE ====================

@bp.route('/page', methods=['GET'])
def machine_analyzer_page():
    """Render the machine analyzer page"""
    return render_template('nexus/machine_analyzer.html')

# ==================== ANALYSIS VISUALIZATIONS ====================

@bp.route('/analysis/visualizations', methods=['GET'])
def get_all_visualizations():
    """Get all analysis visualizations as base64-encoded images"""
    try:
        visualizations = AnalysisVisualizations.generate_all_visualizations()
        return jsonify({
            'success': True,
            'visualizations': visualizations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analysis/visualization/<viz_type>', methods=['GET'])
def get_visualization(viz_type):
    """Get a specific visualization"""
    try:
        method_name = viz_type.lower()
        if not hasattr(AnalysisVisualizations, method_name):
            return jsonify({'error': f'Unknown visualization: {viz_type}'}), 404

        method = getattr(AnalysisVisualizations, method_name)
        fig = method()
        image_base64 = AnalysisVisualizations.fig_to_base64(fig)

        return jsonify({
            'success': True,
            'type': viz_type,
            'image': image_base64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== EVALUATION REPORTS ====================

@bp.route('/analysis/reports', methods=['GET'])
def get_all_reports():
    """Get all evaluation reports"""
    try:
        reports = EvaluationReports.get_all_reports()
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analysis/report/<report_type>', methods=['GET'])
def get_report(report_type):
    """Get a specific evaluation report"""
    try:
        reports = EvaluationReports.get_all_reports()
        if report_type not in reports:
            return jsonify({'error': f'Unknown report: {report_type}'}), 404

        return jsonify({
            'success': True,
            'type': report_type,
            'report': reports[report_type]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== INCIDENT LOGS ====================

@bp.route('/analysis/incident-log', methods=['GET'])
def get_incident_log():
    """Get detailed incident log"""
    try:
        incidents = IncidentLog.get_incident_log()
        return jsonify({
            'success': True,
            'incidents': incidents,
            'total_count': len(incidents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
