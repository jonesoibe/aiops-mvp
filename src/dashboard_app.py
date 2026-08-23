"""
AIOps MVP Dashboard - Enhanced with Authentication & RBAC
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from functools import wraps
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import bcrypt
import jwt
from pymongo import MongoClient
from src.pipeline import AIOpsPipeline
from src.chaos_simulator import run_chaos_simulation
import pandas as pd
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='../templates')
CORS(app)

# ==================== SIMULATION STATE ====================
# Store simulation results in memory
simulation_state = {
    'incidents': [],
    'anomalies': [],
    'faults': [],
    'metrics': {},
    'correlations': {},
    'last_run': None,
    'is_running': False
}

# Map incident status (persisted in memory for demo)
incident_status_map = {}

# ==================== CONFIGURATION ====================

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'aiops_mvp'

# MongoDB Connection
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[DB_NAME]
    users_collection = db['users']
    audit_collection = db['audit_trail']
    print("✅ MongoDB connected")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    mongo_client = None
    db = None

# ==================== SECURITY ====================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'"
    return response

# ==================== AUTHENTICATION ====================

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

def require_role(*roles):
    """Decorator for role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Not authenticated'}), 401

            if request.user['role'] not in roles:
                log_audit('access_denied', request.user['username'], f"Attempted access to {request.path}")
                return jsonify({'error': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)

        return decorated

    return decorator

# ==================== AUDIT LOGGING ====================

def log_audit(action, user, details=''):
    """Log audit trail to MongoDB."""
    if not audit_collection:
        return

    audit_entry = {
        'timestamp': datetime.utcnow(),
        'action': action,
        'user': user,
        'details': details,
        'ip': request.remote_addr,
        'endpoint': request.path,
        'method': request.method
    }
    audit_collection.insert_one(audit_entry)

# ==================== ROUTES - AUTHENTICATION ====================

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

    if not db:
        # Demo mode - accept demo accounts
        demo_users = {
            'admin': {'password': 'admin123', 'role': 'admin', 'email': 'admin@aiops.local'},
            'operator': {'password': 'operator123', 'role': 'operator', 'email': 'operator@aiops.local'},
            'viewer': {'password': 'viewer123', 'role': 'viewer', 'email': 'viewer@aiops.local'}
        }

        if username in demo_users and demo_users[username]['password'] == password:
            user_data = demo_users[username]
            token = generate_token(username, username, user_data['role'])
            log_audit('login_success', username)

            return jsonify({
                'token': token,
                'user': {
                    'id': username,
                    'username': username,
                    'email': user_data['email'],
                    'role': user_data['role']
                }
            }), 200

        log_audit('login_failed', username, 'Invalid credentials')
        return jsonify({'error': 'Invalid credentials'}), 401

    # Production mode - check MongoDB
    user = users_collection.find_one({'username': username})

    if not user or not check_password(password, user['password_hash']):
        log_audit('login_failed', username, 'Invalid credentials')
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(str(user['_id']), user['username'], user['role'])
    log_audit('login_success', username)

    return jsonify({
        'token': token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle user registration."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    if not db:
        return jsonify({'error': 'Registration disabled in demo mode'}), 400

    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400

    user_data = {
        'username': username,
        'email': email,
        'password_hash': hash_password(password),
        'role': 'viewer',  # Default role
        'active': True,
        'created_at': datetime.utcnow()
    }

    result = users_collection.insert_one(user_data)
    log_audit('user_created', 'system', f"New user: {username}")

    return jsonify({'success': True, 'message': 'Account created successfully'}), 201

# ==================== ROUTES - PAGES ====================

@app.route('/')
def index():
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
    """Render incident response simulator demo."""
    return render_template('demo_dashboard.html')

@app.route('/users')
def users():
    """Render user management page."""
    return render_template('users_page.html')

@app.route('/audit-trail')
@require_auth
@require_role('admin')
def audit_trail():
    """Render audit trail page."""
    # TODO: Create audit_trail.html
    return jsonify({'message': 'Audit trail page coming soon'}), 200

# ==================== ROUTES - API - USERS ====================

@app.route('/api/users', methods=['GET'])
@require_auth
@require_role('admin')
def get_users():
    """Get all users (admin only)."""
    if not db:
        # Demo mode
        demo_users = [
            {'_id': 'admin', 'username': 'admin', 'email': 'admin@aiops.local', 'role': 'admin', 'active': True, 'created_at': datetime.utcnow()},
            {'_id': 'operator', 'username': 'operator', 'email': 'operator@aiops.local', 'role': 'operator', 'active': True, 'created_at': datetime.utcnow()},
            {'_id': 'viewer', 'username': 'viewer', 'email': 'viewer@aiops.local', 'role': 'viewer', 'active': True, 'created_at': datetime.utcnow()}
        ]
        return jsonify({'users': demo_users}), 200

    users = list(users_collection.find({}, {'password_hash': 0}))
    for user in users:
        user['_id'] = str(user['_id'])

    return jsonify({'users': users}), 200

@app.route('/api/users', methods=['POST'])
@require_auth
@require_role('admin')
def create_user():
    """Create new user (admin only)."""
    data = request.get_json()

    if not all([data.get('username'), data.get('email'), data.get('password'), data.get('role')]):
        return jsonify({'error': 'Missing required fields'}), 400

    if not db:
        return jsonify({'error': 'User creation disabled in demo mode'}), 400

    if users_collection.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already exists'}), 400

    user_data = {
        'username': data['username'],
        'email': data['email'],
        'password_hash': hash_password(data['password']),
        'role': data['role'],
        'active': True,
        'created_at': datetime.utcnow()
    }

    result = users_collection.insert_one(user_data)
    log_audit('user_created', request.user['username'], f"Created user: {data['username']} as {data['role']}")

    return jsonify({'success': True, 'user_id': str(result.inserted_id)}), 201

@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    """Delete user (admin only)."""
    if not db:
        return jsonify({'error': 'User deletion disabled in demo mode'}), 400

    from bson.objectid import ObjectId
    result = users_collection.delete_one({'_id': ObjectId(user_id)})

    if result.deleted_count == 0:
        return jsonify({'error': 'User not found'}), 404

    log_audit('user_deleted', request.user['username'], f"Deleted user: {user_id}")

    return jsonify({'success': True}), 200

# ==================== ROUTES - API - AUDIT ====================

@app.route('/api/audit-trail', methods=['GET'])
@require_auth
@require_role('admin')
def get_audit_trail():
    """Get audit trail entries (admin only)."""
    if not audit_collection:
        return jsonify({'entries': []}), 200

    limit = request.args.get('limit', 100, type=int)
    entries = list(audit_collection.find().sort('timestamp', -1).limit(limit))

    for entry in entries:
        entry['_id'] = str(entry['_id'])
        entry['timestamp'] = entry['timestamp'].isoformat()

    return jsonify({'entries': entries}), 200

# ==================== ROUTES - API - ANALYSIS ====================

@app.route('/api/chaos-simulation/run', methods=['POST'])
@require_auth
def run_chaos():
    """Run chaos simulation and store results."""
    global simulation_state

    if simulation_state['is_running']:
        return jsonify({'error': 'Simulation already running'}), 400

    log_audit('chaos_simulation_started', request.user['username'])

    try:
        simulation_state['is_running'] = True

        print("\n" + "="*70)
        print("Running chaos simulation...")
        print("="*70)

        # Run the chaos simulation
        df_faults, df_anomalies, df_incidents = run_chaos_simulation()

        # Store results in global state
        simulation_state['faults'] = df_faults.to_dict('records') if not df_faults.empty else []
        simulation_state['anomalies'] = df_anomalies.to_dict('records') if not df_anomalies.empty else []
        simulation_state['last_run'] = datetime.utcnow().isoformat()

        # Create incidents with unique IDs and status
        incidents_data = []
        for idx, row in df_incidents.iterrows():
            incident_id = f"INC-{int(row['time']):04d}-{row['service'][:4].upper()}"

            # Check if this incident already has a status
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

        # Calculate metrics
        incidents_by_type = df_incidents.groupby('incident_type').size().to_dict() if not df_incidents.empty else {}

        simulation_state['is_running'] = False

        log_audit('chaos_simulation_completed', request.user['username'],
                 f"Incidents: {len(incidents_data)}, Anomalies: {len(df_anomalies)}")

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
        log_audit('chaos_simulation_error', request.user['username'], str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Get all incidents from last simulation."""
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')

    incidents = simulation_state['incidents']

    # Apply filters
    if status_filter:
        incidents = [i for i in incidents if i['status'] == status_filter]
    if severity_filter:
        incidents = [i for i in incidents if i['severity'] == severity_filter]

    # Sort by time descending
    incidents = sorted(incidents, key=lambda x: x['time'], reverse=True)

    return jsonify({
        'incidents': incidents,
        'total': len(incidents),
        'last_run': simulation_state['last_run']
    }), 200


@app.route('/api/incidents/<incident_id>', methods=['GET'])
@require_auth
def get_incident_detail(incident_id):
    """Get detailed information about an incident."""
    incidents = [i for i in simulation_state['incidents'] if i['id'] == incident_id]

    if not incidents:
        return jsonify({'error': 'Incident not found'}), 404

    incident = incidents[0]

    # Add additional details
    incident['root_cause'] = f"Fault in {incident['service']} causing {incident['incident_type']}"
    incident['affected_services'] = [incident['service']]
    incident['remediation_suggestions'] = [
        f"Scale resources on {incident['service']}",
        f"Review recent deployments to {incident['service']}",
        f"Check database connections for {incident['service']}"
    ]
    incident['manual_reviews'] = 2
    incident['automated_actions'] = 1

    return jsonify(incident), 200


@app.route('/api/incidents/<incident_id>/status', methods=['PUT'])
@require_auth
def update_incident_status(incident_id):
    """Update incident status."""
    global incident_status_map
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['new', 'acknowledged', 'resolved', 'failed']:
        return jsonify({'error': 'Invalid status'}), 400

    # Update status
    incident_status_map[incident_id] = new_status

    # Update in simulation state
    for incident in simulation_state['incidents']:
        if incident['id'] == incident_id:
            incident['status'] = new_status
            break

    log_audit('incident_updated', request.user['username'],
             f"Incident {incident_id} status changed to {new_status}")

    return jsonify({'success': True, 'status': new_status}), 200


@app.route('/api/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get simulated metrics."""
    service = request.args.get('service', '')

    if not simulation_state['faults']:
        return jsonify({'metrics': []}), 200

    faults = simulation_state['faults']

    # Filter by service if specified
    if service:
        faults = [f for f in faults if f['service'] == service]

    return jsonify({
        'metrics': faults,
        'services': list(set(f['service'] for f in simulation_state['faults']))
    }), 200


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

# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
