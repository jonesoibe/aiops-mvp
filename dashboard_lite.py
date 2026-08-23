#!/usr/bin/env python3
"""
Lightweight AIOps Dashboard - No heavy ML dependencies
Just Flask + Chaos Simulator + Authentication
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Minimal imports
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from functools import wraps
import bcrypt
import jwt

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only what we need
from src.chaos_simulator import ChaosSimulator

# ==================== APP SETUP ====================

app = Flask(__name__, template_folder='templates')
CORS(app)

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

# ==================== STATE ====================

simulation_state = {
    'incidents': [],
    'anomalies': [],
    'faults': [],
    'last_run': None,
    'is_running': False
}

incident_status_map = {}

# ==================== SECURITY ====================

def hash_password(password):
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    """Verify password."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id, username, role):
    """Generate JWT token."""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def require_auth(f):
    """Decorator for API authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization header'}), 401

        try:
            token = auth_header[7:]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated

# ==================== ROUTES ====================

@app.route('/login', methods=['GET'])
def login_page():
    """Render login page."""
    return render_template('login.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    # Demo accounts
    demo_users = {
        'admin': {'password': 'admin123', 'role': 'admin', 'email': 'admin@aiops.local'},
        'operator': {'password': 'operator123', 'role': 'operator', 'email': 'operator@aiops.local'},
        'viewer': {'password': 'viewer123', 'role': 'viewer', 'email': 'viewer@aiops.local'}
    }

    if username in demo_users and demo_users[username]['password'] == password:
        user_data = demo_users[username]
        token = generate_token(username, username, user_data['role'])

        return jsonify({
            'token': token,
            'user': {
                'id': username,
                'username': username,
                'email': user_data['email'],
                'role': user_data['role']
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/')
def home():
    """Render home page."""
    return render_template('home_page.html')

@app.route('/problems')
def problems():
    """Render problems page."""
    return render_template('problems_page.html')

@app.route('/infrastructure')
def infrastructure():
    """Render infrastructure page."""
    return render_template('infrastructure_page.html')

@app.route('/demo')
def demo():
    """Render demo page."""
    return render_template('demo_dashboard.html')

@app.route('/settings')
def settings():
    """Render system settings page."""
    return render_template('settings.html')

@app.route('/audit-trail')
def audit_trail():
    """Render audit trail page."""
    return render_template('audit_trail.html')

@app.route('/api-docs')
def api_docs():
    """Render API documentation page."""
    return render_template('api_docs.html')

@app.route('/outputs')
def outputs():
    """Render outputs and results page."""
    return render_template('outputs.html')

@app.route('/users')
def users():
    """Render user management page."""
    return render_template('users_page.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/chaos-simulation/run', methods=['POST'])
@require_auth
def run_chaos():
    """Run chaos simulation."""
    global simulation_state

    if simulation_state['is_running']:
        return jsonify({'error': 'Simulation already running'}), 400

    try:
        simulation_state['is_running'] = True

        print("\n" + "="*70)
        print("🔥 Running Chaos Simulation...")
        print("="*70)

        # Run the chaos simulation
        simulator = ChaosSimulator(base_metrics=60, noise_level=0.15)
        metrics_data, df_faults = simulator.simulate()
        df_anomalies = simulator.detect_anomalies(df_faults)
        df_incidents = simulator.classify_incidents(df_anomalies)
        correlations = simulator.detect_correlations(df_faults)

        # Store results
        simulation_state['faults'] = df_faults.to_dict('records') if not df_faults.empty else []
        simulation_state['anomalies'] = df_anomalies.to_dict('records') if not df_anomalies.empty else []
        simulation_state['last_run'] = datetime.utcnow().isoformat()

        # Create incidents with IDs and status
        incidents_data = []
        for idx, row in df_incidents.iterrows():
            incident_id = f"INC-{int(row['time']):04d}-{row['service'][:4].upper()}"

            if incident_id not in incident_status_map:
                incident_status_map[incident_id] = 'new'

            incidents_data.append({
                'id': incident_id,
                'time': int(row['time']),
                'service': row['service'],
                'incident_type': row['incident_type'],
                'confidence': float(row['confidence']),
                'metric_value': float(row['metric_value']),
                'deviation_pct': float(row['deviation_pct']),
                'status': incident_status_map[incident_id],
                'severity': 'critical' if row['confidence'] > 0.8 else ('high' if row['confidence'] > 0.6 else 'medium')
            })

        simulation_state['incidents'] = incidents_data
        incidents_by_type = df_incidents.groupby('incident_type').size().to_dict() if not df_incidents.empty else {}

        simulation_state['is_running'] = False

        print(f"\n✅ Simulation complete!")
        print(f"   Incidents: {len(incidents_data)}")
        print(f"   Anomalies: {len(df_anomalies)}")

        return jsonify({
            'status': 'success',
            'summary': {
                'faults_injected': len(df_faults),
                'anomalies_detected': len(df_anomalies),
                'incidents_classified': len(df_incidents),
                'detection_rate': f"{len(df_anomalies) / max(len(df_faults), 1) * 100:.1f}%"
            },
            'by_type': incidents_by_type,
            'incidents': incidents_data
        }), 200
    except Exception as e:
        simulation_state['is_running'] = False
        print(f"❌ Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Get all incidents."""
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')

    incidents = simulation_state['incidents']

    if status_filter:
        incidents = [i for i in incidents if i['status'] == status_filter]
    if severity_filter:
        incidents = [i for i in incidents if i['severity'] == severity_filter]

    incidents = sorted(incidents, key=lambda x: x['time'], reverse=True)

    return jsonify({
        'incidents': incidents,
        'total': len(incidents),
        'last_run': simulation_state['last_run']
    }), 200

@app.route('/api/incidents/<incident_id>/status', methods=['PUT'])
@require_auth
def update_incident_status(incident_id):
    """Update incident status."""
    global incident_status_map
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['new', 'acknowledged', 'resolved', 'failed']:
        return jsonify({'error': 'Invalid status'}), 400

    incident_status_map[incident_id] = new_status

    for incident in simulation_state['incidents']:
        if incident['id'] == incident_id:
            incident['status'] = new_status
            break

    return jsonify({'success': True, 'status': new_status}), 200

@app.route('/api/simulation/status', methods=['GET'])
@require_auth
def get_simulation_status():
    """Get simulation status."""
    return jsonify({
        'is_running': simulation_state['is_running'],
        'last_run': simulation_state['last_run'],
        'incidents_count': len(simulation_state['incidents']),
        'anomalies_count': len(simulation_state['anomalies']),
        'faults_count': len(simulation_state['faults'])
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ==================== RUN ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 AIOps Dashboard Lite")
    print("  Starting on http://localhost:5000")
    print("="*70)
    print("\n📍 Login at: http://localhost:5000/login")
    print("   Demo: admin / admin123\n")

    app.run(debug=True, port=5000, use_reloader=False)
