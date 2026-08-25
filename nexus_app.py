#!/usr/bin/env python3
"""
Nexus AIOps - Enterprise Autonomous Observability Platform
Enhanced Flask app with WebSocket, MongoDB, and Real-time Telemetry Streaming
"""

import os
import sys
import json
from datetime import datetime, timedelta
import threading
import time
import random

# Flask & WebSocket
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from functools import wraps

# Authentication & Security
import bcrypt
import jwt

# Database
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ==================== APP SETUP ====================

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = 'nexus_aiops'

app.config['SECRET_KEY'] = SECRET_KEY

# ==================== DATABASE CONNECTION ====================

mongodb_client = None
db = None

def connect_mongodb():
    """Connect to MongoDB"""
    global mongodb_client, db
    try:
        mongodb_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        mongodb_client.admin.command('ping')
        db = mongodb_client[DATABASE_NAME]
        print("✅ MongoDB connected successfully")
        return True
    except ConnectionFailure:
        print("⚠️  MongoDB connection failed - using in-memory storage")
        return False

# ==================== IN-MEMORY STATE (Fallback) ====================

in_memory_store = {
    'users': {},
    'incidents': [],
    'telemetry': [],
    'audit_log': [],
    'remediation_queue': [],
    'approvals': []
}

# ==================== AUTHENTICATION ====================

def hash_password(password):
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    """Verify password."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id, username, role, expires_in_days=7):
    """Generate JWT token."""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=expires_in_days)
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

# ==================== INITIALIZATION ====================

def initialize_users():
    """Initialize demo users in MongoDB or in-memory storage."""
    demo_users = {
        'admin': {
            'username': 'admin',
            'email': 'admin@nexus.local',
            'role': 'admin',
            'password_hash': hash_password('admin123'),
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        },
        'operator': {
            'username': 'operator',
            'email': 'operator@nexus.local',
            'role': 'operator',
            'password_hash': hash_password('operator123'),
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        },
        'viewer': {
            'username': 'viewer',
            'email': 'viewer@nexus.local',
            'role': 'viewer',
            'password_hash': hash_password('viewer123'),
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        }
    }

    if db:
        # Store in MongoDB
        users_collection = db['users']
        for username, user_data in demo_users.items():
            users_collection.update_one(
                {'username': username},
                {'$set': user_data},
                upsert=True
            )
    else:
        # Store in memory
        in_memory_store['users'] = demo_users

# ==================== ROUTES ====================

@app.route('/login')
def login_page():
    """Login Page"""
    return render_template('nexus/login.html')

@app.route('/')
def index():
    """Executive Overview - Landing Page"""
    return render_template('nexus/overview.html')

@app.route('/live-operations')
def live_operations():
    """Live Operations Center"""
    return render_template('nexus/live-operations.html')

@app.route('/ai-operations')
def ai_operations():
    """AI Operations Center - Davis AI Style"""
    return render_template('nexus/ai-operations.html')

@app.route('/topology')
def topology():
    """Smart Service Topology - Smartscape Inspired"""
    return render_template('nexus/topology.html')

@app.route('/problems')
def problems():
    """Problems & Incidents"""
    return render_template('nexus/problems.html')

@app.route('/infrastructure')
def infrastructure():
    """Windows Infrastructure Monitoring"""
    return render_template('nexus/infrastructure.html')

@app.route('/logs')
def logs():
    """Logs Explorer"""
    return render_template('nexus/logs.html')

@app.route('/traces')
def traces():
    """Distributed Trace Explorer"""
    return render_template('nexus/traces.html')

@app.route('/remediation')
def remediation():
    """Autonomous Remediation Center"""
    return render_template('nexus/remediation.html')

@app.route('/approvals')
def approvals():
    """Approval Queue"""
    return render_template('nexus/approvals.html')

@app.route('/audit')
def audit():
    """Audit Timeline"""
    return render_template('nexus/audit.html')

@app.route('/settings')
def settings():
    """Platform Settings & Policies"""
    return render_template('nexus/settings.html')

# ==================== AUTH API ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    # Try MongoDB first
    user_data = None
    if db:
        user_data = db['users'].find_one({'username': username})
    else:
        user_data = in_memory_store['users'].get(username)

    if user_data and check_password(password, user_data.get('password_hash', '')):
        token = generate_token(username, username, user_data['role'])

        # Log login event
        audit_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'user': username,
            'action': 'login_success',
            'ip': request.remote_addr,
            'status': 'success'
        }
        if db:
            db['audit_log'].insert_one(audit_event)
        else:
            in_memory_store['audit_log'].append(audit_event)

        return jsonify({
            'token': token,
            'user': {
                'username': username,
                'email': user_data.get('email'),
                'role': user_data.get('role')
            }
        }), 200

    # Log failed login
    audit_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'user': username,
        'action': 'login_failed',
        'ip': request.remote_addr,
        'status': 'failed'
    }
    if db:
        db['audit_log'].insert_one(audit_event)
    else:
        in_memory_store['audit_log'].append(audit_event)

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh JWT token."""
    user = request.user
    new_token = generate_token(user['user_id'], user['username'], user['role'])
    return jsonify({'token': new_token}), 200

# ==================== TELEMETRY API ====================

@app.route('/api/telemetry/current', methods=['GET'])
@require_auth
def get_current_telemetry():
    """Get current system telemetry."""
    return jsonify({
        'healthy_entities': 1284,
        'healthy_trend': '+4.8%',
        'active_problems': 17,
        'critical_problems': 2,
        'ai_investigations': 11,
        'autonomous_resolutions': 7,
        'resolution_rate': '94%',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/incidents', methods=['GET'])
@require_auth
def get_incidents():
    """Get active incidents."""
    if db:
        incidents = list(db['incidents'].find().sort('timestamp', -1).limit(50))
        for i in incidents:
            i['_id'] = str(i['_id'])
    else:
        incidents = in_memory_store['incidents']

    return jsonify({'incidents': incidents}), 200

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Client connected."""
    print(f"🔌 Client connected: {request.sid}")
    emit('connection_response', {'data': 'Connected to Nexus AIOps'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected."""
    print(f"🔌 Client disconnected: {request.sid}")

@socketio.on('subscribe_telemetry')
def handle_subscribe_telemetry():
    """Subscribe to real-time telemetry stream."""
    join_room('telemetry')
    emit('telemetry_subscribed', {'status': 'subscribed'})
    print(f"📡 Client subscribed to telemetry: {request.sid}")

@socketio.on('subscribe_logs')
def handle_subscribe_logs():
    """Subscribe to real-time log stream."""
    join_room('logs')
    emit('logs_subscribed', {'status': 'subscribed'})
    print(f"📡 Client subscribed to logs: {request.sid}")

@socketio.on('subscribe_incidents')
def handle_subscribe_incidents():
    """Subscribe to incident stream."""
    join_room('incidents')
    emit('incidents_subscribed', {'status': 'subscribed'})
    print(f"📡 Client subscribed to incidents: {request.sid}")

# ==================== TELEMETRY STREAMING ====================

def stream_telemetry():
    """Background thread to stream mock telemetry data."""
    services = ['SERVICE_A', 'SERVICE_B', 'SERVICE_C', 'API_GATEWAY', 'SQL_SERVER']
    metrics = ['cpu_usage', 'memory_usage', 'latency', 'error_rate', 'throughput']

    while True:
        try:
            telemetry_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'services': {}
            }

            for service in services:
                telemetry_data['services'][service] = {}
                for metric in metrics:
                    if metric == 'cpu_usage':
                        value = random.uniform(20, 80)
                    elif metric == 'memory_usage':
                        value = random.uniform(30, 75)
                    elif metric == 'latency':
                        value = random.uniform(10, 200)
                    elif metric == 'error_rate':
                        value = random.uniform(0, 5)
                    else:  # throughput
                        value = random.uniform(100, 1000)

                    telemetry_data['services'][service][metric] = {
                        'value': value,
                        'unit': '%' if metric in ['cpu_usage', 'memory_usage', 'error_rate'] else 'ms' if metric == 'latency' else 'req/s'
                    }

            socketio.emit('telemetry_update', telemetry_data, room='telemetry')
            time.sleep(2)  # Stream every 2 seconds

        except Exception as e:
            print(f"Telemetry streaming error: {e}")
            time.sleep(5)

def stream_logs():
    """Background thread to stream mock log data."""
    log_messages = [
        "IIS Application Pool restarted successfully",
        "Memory allocation exceeded configured threshold",
        "Payment API returned HTTP 500",
        "Database connection pool exhausted",
        "Cache invalidation triggered",
        "Authentication service latency spike detected",
        "Disk I/O contention detected",
        "Network packet loss detected on interface eth0"
    ]

    while True:
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'severity': random.choice(['INFO', 'WARNING', 'ERROR']),
                'service': random.choice(['SERVICE_A', 'SERVICE_B', 'API_GATEWAY']),
                'message': random.choice(log_messages)
            }

            socketio.emit('log_update', log_entry, room='logs')
            time.sleep(3)

        except Exception as e:
            print(f"Log streaming error: {e}")
            time.sleep(5)

# ==================== STARTUP ====================

@app.before_request
def setup():
    """Setup on first request."""
    pass

def start_background_threads():
    """Start telemetry and log streaming threads."""
    telemetry_thread = threading.Thread(target=stream_telemetry, daemon=True)
    telemetry_thread.start()

    logs_thread = threading.Thread(target=stream_logs, daemon=True)
    logs_thread.start()

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform")
    print("="*70)

    # Initialize
    connect_mongodb()
    initialize_users()
    start_background_threads()

    print("\n📍 Access at: http://localhost:5000")
    print("   Demo: admin / admin123\n")

    # Run with socketio
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
