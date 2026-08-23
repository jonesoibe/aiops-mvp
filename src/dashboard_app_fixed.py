"""
Flask dashboard for AIOps MVP - enhanced real-time visualization with security & API docs
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from functools import wraps
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from src.pipeline import AIOpsPipeline
from src.chaos_simulator import run_chaos_simulation

# Get the correct template folder path (one level up from src/)
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'"
    return response

# Global state
pipeline_state = {
    'last_run': None,
    'results': None,
    'metrics': None,
    'chaos_results': None
}

# Simple token-based auth
VALID_TOKENS = {
    os.getenv('AIOPS_API_KEY', 'demo_key_12345'): 'demo_user'
}

def require_auth(f):
    """Decorator for API authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header[7:]
        if token not in VALID_TOKENS:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Render main dashboard."""
    return render_template('dashboard.html')

@app.route('/api/chaos-simulation', methods=['POST'])
@require_auth
def run_chaos():
    """Run chaos simulation."""
    try:
        df_faults, df_anomalies, df_incidents = run_chaos_simulation()

        pipeline_state['chaos_results'] = {
            'faults': df_faults.to_dict('records'),
            'anomalies': df_anomalies.to_dict('records'),
            'incidents': df_incidents.to_dict('records')
        }

        incidents_by_service = df_incidents.groupby('service').agg({
            'incident_type': 'count',
            'confidence': 'mean'
        }).to_dict()

        incidents_by_type = df_incidents.groupby('incident_type').size().to_dict()

        return jsonify({
            'status': 'success',
            'summary': {
                'faults_injected': len(df_faults),
                'anomalies_detected': len(df_anomalies),
                'incidents_classified': len(df_incidents),
                'detection_rate': f"{len(df_anomalies) / max(len(df_faults), 1) * 100:.1f}%"
            },
            'by_service': incidents_by_service,
            'by_type': incidents_by_type,
            'timeline': df_incidents[['time', 'service', 'incident_type', 'confidence']].to_dict('records'),
            'faults': df_faults[['time', 'service', 'fault_type']].to_dict('records')
        }), 200
    except Exception as e:
        app.logger.error(f"Chaos simulation error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get latest metrics."""
    if pipeline_state['results'] is None:
        return jsonify({'status': 'error', 'message': 'No analysis run yet'}), 400

    results = pipeline_state['results']
    return jsonify({
        'anomalies_detected': int(results.get('anomalies_detected', 0)),
        'precision': float(results.get('precision', 0)),
        'recall': float(results.get('recall', 0)),
        'f1_score': float(results.get('f1_score', 0))
    }), 200

@app.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Get incident log."""
    if pipeline_state['results'] is None:
        return jsonify({'status': 'error', 'message': 'No analysis run yet'}), 400

    incidents = pipeline_state['results'].get('incident_log', [])
    return jsonify({'incidents': incidents[:50], 'total': len(incidents)}), 200

@app.route('/api/statistics', methods=['GET'])
@require_auth
def get_statistics():
    """Get statistics."""
    if pipeline_state['results'] is None:
        return jsonify({'status': 'error', 'message': 'No analysis run yet'}), 400

    results = pipeline_state['results']
    return jsonify({
        'model_performance': {
            'precision': float(results.get('precision', 0)),
            'recall': float(results.get('recall', 0)),
            'f1_score': float(results.get('f1_score', 0)),
            'roc_auc': float(results.get('roc_auc', 0))
        }
    }), 200

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Swagger/OpenAPI documentation."""
    return jsonify(get_openapi_schema()), 200

def get_openapi_schema():
    """Generate OpenAPI 3.0 schema."""
    return {
        'openapi': '3.0.0',
        'info': {
            'title': 'AIOps MVP API',
            'version': '1.0.0',
            'description': 'Automated Incident Detection & Response System'
        },
        'paths': {
            '/api/chaos-simulation': {
                'post': {
                    'summary': 'Run chaos simulation',
                    'tags': ['Simulation'],
                    'responses': {'200': {'description': 'Simulation completed'}}
                }
            }
        }
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
