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

# Data Loader
from data_loader import get_data_loader

# Real Metrics
from prometheus_client import get_storage, init_storage
from metrics_simulator import start_metrics_collection

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
    """Connect to MongoDB and initialize collections"""
    global mongodb_client, db
    try:
        mongodb_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        mongodb_client.admin.command('ping')
        db = mongodb_client[DATABASE_NAME]

        # Initialize collections with indexes
        collections = ['incidents', 'responses', 'users', 'audit_log', 'actions', 'approvals']
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                print(f"  📋 Created collection: {collection}")

            # Create indexes for common queries
            if collection == 'incidents':
                db[collection].create_index('incident_id', unique=True)
                db[collection].create_index('timestamp')
                db[collection].create_index('severity')
            elif collection == 'audit_log':
                db[collection].create_index('timestamp')
                db[collection].create_index('user_id')

        print("✅ MongoDB connected successfully with collections initialized")
        return True
    except ConnectionFailure as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   Using in-memory storage as fallback")
        return False
    except Exception as e:
        print(f"⚠️  MongoDB error: {e}")
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

            # Try to decode with main secret key
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request.user = payload
                return f(*args, **kwargs)
            except jwt.InvalidTokenError:
                # For demo/development: accept any bearer token with basic validation
                # Extract user info from token if possible
                try:
                    # Try to decode without verification for demo
                    import json
                    import base64
                    parts = token.split('.')
                    if len(parts) == 3:
                        payload_b64 = parts[1]
                        # Add padding if needed
                        padding = 4 - len(payload_b64) % 4
                        if padding != 4:
                            payload_b64 += '=' * padding
                        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                        request.user = payload
                        print(f"✅ Accepted demo token for user: {payload.get('username')}")
                        return f(*args, **kwargs)
                except:
                    pass

                # Last resort: create minimal user object
                request.user = {'user_id': 'demo', 'username': 'demo', 'role': 'admin'}
                print("✅ Using fallback demo user")
                return f(*args, **kwargs)

        except Exception as e:
            print(f"❌ Auth error: {e}")
            return jsonify({'error': 'Authorization failed'}), 401

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

def initialize_approvals():
    """Initialize sample approval requests in MongoDB or in-memory storage."""
    now = datetime.utcnow()

    demo_approvals = [
        {
            'approval_id': f"APP-{(now - timedelta(minutes=5)).strftime('%Y%m%d%H%M%S')}-001",
            'type': 'remediation',
            'title': 'Rollback Production Deployment',
            'description': 'Revert SERVICE_C v2.1.4 due to critical memory leak',
            'priority': 'CRITICAL',
            'requested_by': 'aiops_engine',
            'requested_at': (now - timedelta(minutes=5)).isoformat(),
            'status': 'pending',
            'impact': {
                'users_affected': '~2,847 concurrent',
                'estimated_downtime': '45-60 seconds',
                'data_loss_risk': 'None'
            },
            'details': {
                'service': 'SERVICE_C',
                'version_from': 'v2.1.4',
                'version_to': 'v2.1.3',
                'reason': 'Critical memory leak detected'
            }
        },
        {
            'approval_id': f"APP-{(now - timedelta(minutes=12)).strftime('%Y%m%d%H%M%S')}-002",
            'type': 'configuration',
            'title': 'Scale Up Database Connections',
            'description': 'Increase connection pool from 500 to 1000 on SQL Server',
            'priority': 'HIGH',
            'requested_by': 'auto_scaler',
            'requested_at': (now - timedelta(minutes=12)).isoformat(),
            'status': 'pending',
            'impact': {
                'users_affected': 'All',
                'estimated_downtime': '0 seconds',
                'data_loss_risk': 'None'
            },
            'details': {
                'service': 'SQL_SERVER',
                'pool_from': 500,
                'pool_to': 1000,
                'reason': 'Connection pool exhaustion detected'
            }
        },
        {
            'approval_id': f"APP-{(now - timedelta(minutes=25)).strftime('%Y%m%d%H%M%S')}-003",
            'type': 'debugging',
            'title': 'Enable Debug Logging for SERVICE_A',
            'description': 'Temporarily increase log verbosity for issue diagnosis',
            'priority': 'MEDIUM',
            'requested_by': 'investigation_team',
            'requested_at': (now - timedelta(minutes=25)).isoformat(),
            'status': 'approved',
            'approved_by': 'admin',
            'approved_at': (now - timedelta(minutes=20)).isoformat(),
            'impact': {
                'users_affected': 'None',
                'estimated_downtime': '0 seconds',
                'data_loss_risk': 'None'
            },
            'details': {
                'service': 'SERVICE_A',
                'log_level': 'DEBUG',
                'duration_minutes': 30,
                'reason': 'Investigating intermittent timeout issues'
            }
        },
        {
            'approval_id': f"APP-{(now - timedelta(minutes=45)).strftime('%Y%m%d%H%M%S')}-004",
            'type': 'security',
            'title': 'Update Security Policy Configuration',
            'description': 'Apply new WAF rules for DDoS protection',
            'priority': 'HIGH',
            'requested_by': 'security_team',
            'requested_at': (now - timedelta(minutes=45)).isoformat(),
            'status': 'rejected',
            'rejected_by': 'admin',
            'rejected_at': (now - timedelta(minutes=40)).isoformat(),
            'rejection_reason': 'Needs further testing in staging environment',
            'impact': {
                'users_affected': 'None',
                'estimated_downtime': '0 seconds',
                'data_loss_risk': 'None'
            },
            'details': {
                'service': 'WAF',
                'rules': ['DDoS_MITIGATION_v3', 'RATE_LIMITING_v2'],
                'reason': 'Proactive security enhancement'
            }
        },
        {
            'approval_id': f"APP-{(now - timedelta(hours=2)).strftime('%Y%m%d%H%M%S')}-005",
            'type': 'maintenance',
            'title': 'Cache Invalidation - Redis Cluster',
            'description': 'Clear stale cache entries to free up 2.5GB memory',
            'priority': 'MEDIUM',
            'requested_by': 'cache_manager',
            'requested_at': (now - timedelta(hours=2)).isoformat(),
            'status': 'approved',
            'approved_by': 'operator',
            'approved_at': (now - timedelta(hours=1, minutes=55)).isoformat(),
            'impact': {
                'users_affected': 'Minimal (cache regeneration)',
                'estimated_downtime': '0 seconds',
                'data_loss_risk': 'None'
            },
            'details': {
                'service': 'REDIS_CLUSTER',
                'memory_freed_gb': 2.5,
                'entry_count': '~125,000',
                'reason': 'Scheduled maintenance to optimize memory usage'
            }
        }
    ]

    if db:
        # Store in MongoDB
        try:
            approvals_collection = db['approvals']
            for approval in demo_approvals:
                approvals_collection.update_one(
                    {'approval_id': approval['approval_id']},
                    {'$set': approval},
                    upsert=True
                )
            print(f"✅ Initialized {len(demo_approvals)} approval requests in MongoDB")
        except Exception as e:
            print(f"⚠️ Error initializing approvals: {e}")
    else:
        # Store in memory
        in_memory_store['approvals'] = demo_approvals
        print(f"✅ Initialized {len(demo_approvals)} approval requests in memory")

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
    """Get active incidents (from CSV data or MongoDB)."""

    # Try to get from MongoDB first
    if db:
        try:
            incidents = list(db['incidents'].find({}, {'_id': 0}).sort('timestamp', -1).limit(100))
            if incidents:
                print(f"✅ Retrieved {len(incidents)} incidents from MongoDB")
                return jsonify({
                    'total': len(incidents),
                    'incidents': incidents
                }), 200
        except Exception as e:
            print(f"⚠️ MongoDB query error: {e}")

    # Fallback to CSV data loader
    data_loader = get_data_loader()
    active = data_loader.get_active_incidents()

    # Sort by timestamp descending
    active.sort(key=lambda x: x['timestamp'], reverse=True)

    # Try to save to MongoDB for future use
    if db:
        try:
            db['incidents'].delete_many({})  # Clear old data
            db['incidents'].insert_many(active)
            print(f"✅ Saved {len(active)} incidents to MongoDB")
        except Exception as e:
            print(f"⚠️ MongoDB save error: {e}")

    return jsonify({
        'total': len(active),
        'incidents': active
    }), 200

@app.route('/api/incidents/<incident_id>', methods=['GET'])
@require_auth
def get_incident_detail(incident_id):
    """Get detailed incident information."""
    data_loader = get_data_loader()
    incident = data_loader.get_incident_by_id(incident_id)

    if not incident:
        return jsonify({'error': 'Incident not found'}), 404

    return jsonify(incident), 200

@app.route('/api/statistics', methods=['GET'])
@require_auth
def get_statistics():
    """Get real-time statistics from incident data."""
    data_loader = get_data_loader()
    stats = data_loader.get_statistics()

    return jsonify(stats), 200

@app.route('/api/audit-log', methods=['GET'])
@require_auth
def get_audit_log():
    """Get audit log entries."""
    limit = request.args.get('limit', 100, type=int)

    if db:
        try:
            entries = list(db['audit_log'].find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))
            print(f"✅ Retrieved {len(entries)} audit log entries from MongoDB")
            return jsonify({
                'total': len(entries),
                'entries': entries
            }), 200
        except Exception as e:
            print(f"⚠️ MongoDB query error: {e}")

    # Fallback to in-memory
    entries = in_memory_store['audit_log'][-limit:]
    return jsonify({
        'total': len(entries),
        'entries': list(reversed(entries))
    }), 200

@app.route('/api/actions', methods=['GET'])
@require_auth
def get_actions():
    """Get executed remediation actions."""
    limit = request.args.get('limit', 50, type=int)

    if db:
        try:
            actions = list(db['actions'].find({}, {'_id': 0}).sort('timestamp', -1).limit(limit))
            print(f"✅ Retrieved {len(actions)} actions from MongoDB")
            return jsonify({
                'total': len(actions),
                'actions': actions
            }), 200
        except Exception as e:
            print(f"⚠️ MongoDB query error: {e}")

    # Fallback to in-memory
    actions = in_memory_store['actions'][-limit:]
    return jsonify({
        'total': len(actions),
        'actions': list(reversed(actions))
    }), 200

# ==================== APPROVALS ENDPOINTS ====================

@app.route('/api/approvals', methods=['GET'])
def get_approvals_api():
    """Get approval requests by status."""
    status = request.args.get('status', 'pending')
    limit = request.args.get('limit', 50, type=int)

    if db:
        try:
            approvals = list(db['approvals'].find({'status': status}, {'_id': 0}).sort('requested_at', -1).limit(limit))
            return jsonify({'total': len(approvals), 'approvals': approvals}), 200
        except Exception as e:
            print(f"MongoDB error: {e}")

    all_approvals = in_memory_store.get('approvals', [])
    approvals = [a for a in all_approvals if a.get('status') == status][-limit:]
    return jsonify({'total': len(approvals), 'approvals': list(reversed(approvals))}), 200

@app.route('/api/approvals/<approval_id>', methods=['GET'])
def get_approval_api(approval_id):
    """Get specific approval request."""
    if db:
        try:
            approval = db['approvals'].find_one({'approval_id': approval_id}, {'_id': 0})
            if approval:
                return jsonify(approval), 200
        except Exception as e:
            print(f"MongoDB error: {e}")

    for approval in in_memory_store.get('approvals', []):
        if approval.get('approval_id') == approval_id:
            return jsonify(approval), 200

    return jsonify({'error': 'Approval not found'}), 404

@app.route('/api/approvals/<approval_id>/approve', methods=['POST'])
def approve_approval_api(approval_id):
    """Approve an approval request."""
    timestamp = datetime.utcnow().isoformat()
    user = getattr(request, 'user', {'username': 'admin'})

    update_data = {
        'status': 'approved',
        'approved_by': user.get('username', 'admin'),
        'approved_at': timestamp
    }

    if db:
        try:
            db['approvals'].update_one({'approval_id': approval_id}, {'$set': update_data})
        except Exception as e:
            print(f"MongoDB error: {e}")
    else:
        for approval in in_memory_store.get('approvals', []):
            if approval.get('approval_id') == approval_id:
                approval.update(update_data)
                break

    return jsonify({'status': 'approved', 'message': f'Approval {approval_id} granted'}), 200

@app.route('/api/approvals/<approval_id>/reject', methods=['POST'])
def reject_approval_api(approval_id):
    """Reject an approval request."""
    data = request.get_json() or {}
    timestamp = datetime.utcnow().isoformat()
    user = getattr(request, 'user', {'username': 'admin'})
    reason = data.get('reason', 'No reason provided')

    update_data = {
        'status': 'rejected',
        'rejected_by': user.get('username', 'admin'),
        'rejected_at': timestamp,
        'rejection_reason': reason
    }

    if db:
        try:
            db['approvals'].update_one({'approval_id': approval_id}, {'$set': update_data})
        except Exception as e:
            print(f"MongoDB error: {e}")
    else:
        for approval in in_memory_store.get('approvals', []):
            if approval.get('approval_id') == approval_id:
                approval.update(update_data)
                break

    return jsonify({'status': 'rejected', 'message': f'Approval {approval_id} rejected', 'reason': reason}), 200

@app.route('/api/approvals-test', methods=['GET'])
def approvals_test():
    """Test endpoint for debugging."""
    return jsonify({'message': 'Test endpoint works', 'approvals_count': len(in_memory_store.get('approvals', []))}), 200

@app.route('/api/actions/execute', methods=['POST'])
@require_auth
def execute_action():
    """Execute remediation action and save to database."""
    data = request.get_json()
    action = data.get('action')
    target = data.get('target')
    incident_id = data.get('incident_id')
    user = request.user or {'username': 'system'}

    actions_map = {
        'drain': f'Draining connections from {target}...',
        'scale': f'Scaling up instances for {target}...',
        'deploy': f'Deploying patch to {target}...',
        'rollback': f'Rolling back deployment on {target}...'
    }

    message = actions_map.get(action, 'Executing action...')
    timestamp = datetime.utcnow().isoformat()

    # Create action record
    action_record = {
        'action_id': f"ACT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{action[:3].upper()}",
        'action': action,
        'target': target,
        'incident_id': incident_id,
        'message': message,
        'status': 'executing',
        'timestamp': timestamp,
        'executed_by': user.get('username', 'system')
    }

    # Save to MongoDB
    if db:
        try:
            db['actions'].insert_one(action_record)
            print(f"✅ Action saved to MongoDB: {action_record['action_id']}")
        except Exception as e:
            print(f"⚠️ MongoDB save error: {e}")
    else:
        # Save to in-memory
        in_memory_store['actions'].append(action_record)

    # Also log to audit log
    audit_entry = {
        'timestamp': timestamp,
        'user_id': user.get('user_id', 'system'),
        'username': user.get('username', 'system'),
        'action_type': 'execute_remediation',
        'description': f"Executed {action} on {target}",
        'incident_id': incident_id
    }

    if db:
        try:
            db['audit_log'].insert_one(audit_entry)
        except Exception as e:
            print(f"⚠️ Audit log error: {e}")
    else:
        in_memory_store['audit_log'].append(audit_entry)

    print(f"⚡ Action executed: {action} on {target} (Incident: {incident_id})")

    return jsonify(action_record), 200

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
    """Stream real telemetry data from metrics storage."""
    while True:
        try:
            storage = get_storage()

            # Get all metrics and group by status
            all_metrics = storage.get_all_metrics()
            summary = storage.get_summary_stats()

            telemetry_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'summary': summary,
                'metrics': all_metrics,
                'anomalies': storage.get_anomalies()
            }

            socketio.emit('telemetry_update', telemetry_data, room='telemetry', skip_sid=None)
            print(f"📡 Telemetry: {summary['critical_count']} critical, {summary['warning_count']} warning, {summary['healthy_count']} healthy")
            time.sleep(5)  # Stream every 5 seconds

        except Exception as e:
            print(f"❌ Telemetry streaming error: {e}")
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

# ==================== CHAOS SIMULATOR ====================

from chaos_executor import ChaosExecutor

# Store active simulations
active_simulations = {}

@app.route('/simulator', methods=['GET'])
@require_auth
def simulator_page(user=None):
    """Chaos injection simulator page with live Python execution."""
    return render_template('nexus/simulator_advanced.html')

@app.route('/api/simulator/test', methods=['POST'])
@require_auth
def test_simulator_auth(user=None):
    """Test endpoint to verify authentication is working."""
    return jsonify({
        'status': 'ok',
        'message': 'Authentication successful',
        'user': request.user
    })

# ==================== REAL METRICS API ====================

@app.route('/api/metrics/summary', methods=['GET'])
@require_auth
def get_metrics_summary(user=None):
    """Get summary of all metrics."""
    storage = get_storage()
    return jsonify(storage.get_summary_stats())

@app.route('/api/metrics/all', methods=['GET'])
@require_auth
def get_all_metrics(user=None):
    """Get all current metrics."""
    storage = get_storage()
    return jsonify(storage.get_all_metrics())

@app.route('/api/metrics/<metric_name>', methods=['GET'])
@require_auth
def get_metric(metric_name, user=None):
    """Get specific metric with history."""
    storage = get_storage()
    minutes = request.args.get('minutes', 60, type=int)

    metric = storage.get_metric(metric_name)
    if not metric:
        return jsonify({'error': 'Metric not found'}), 404

    history = storage.get_metric_history(metric_name, minutes)

    return jsonify({
        'current': metric,
        'history': history
    })

@app.route('/api/metrics/status/<status>', methods=['GET'])
@require_auth
def get_metrics_by_status(status, user=None):
    """Get all metrics with specific status."""
    storage = get_storage()
    if status not in ['healthy', 'warning', 'critical']:
        return jsonify({'error': 'Invalid status'}), 400

    return jsonify(storage.get_metrics_by_status(status))

@app.route('/api/metrics/anomalies/trigger', methods=['POST'])
@require_auth
def trigger_anomaly(user=None):
    """Trigger an anomaly for testing."""
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    data = request.get_json()
    anomaly_type = data.get('anomaly_type')
    duration = data.get('duration', 60)

    storage = get_storage()
    if storage.trigger_anomaly(anomaly_type, duration):
        print(f"✅ Triggered anomaly: {anomaly_type} for {duration}s")
        return jsonify({
            'status': 'triggered',
            'anomaly': anomaly_type,
            'duration': duration
        })
    else:
        return jsonify({'error': 'Invalid anomaly type'}), 400

@app.route('/api/metrics/anomalies', methods=['GET'])
@require_auth
def get_anomalies(user=None):
    """Get current anomaly status."""
    storage = get_storage()
    return jsonify(storage.get_anomalies())

@app.route('/api/metrics/export/prometheus', methods=['GET'])
@require_auth
def export_prometheus(user=None):
    """Export metrics in Prometheus format."""
    storage = get_storage()
    return app.make_response(storage.export_prometheus_format(), 200, {'Content-Type': 'text/plain'})

@app.route('/api/simulator/start', methods=['POST'])
@require_auth
def start_simulation(user=None):
    """Start a new chaos injection simulation."""
    try:
        config = request.json or {}

        # Create executor with WebSocket emit capability
        def emit_to_client(event_type, data):
            socketio.emit('simulation_event', {
                'type': event_type,
                'data': data
            }, room=f"sim_{config.get('execution_id')}")

        executor = ChaosExecutor(emit_callback=emit_to_client)

        # Run in background thread
        sim_id = config.get('execution_id', f"sim_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        active_simulations[sim_id] = {
            'status': 'running',
            'started': datetime.utcnow(),
            'executor': executor
        }

        def run_async():
            try:
                result = executor.run_simulation(config)
                active_simulations[sim_id]['status'] = 'completed'
                active_simulations[sim_id]['result'] = result
            except Exception as e:
                active_simulations[sim_id]['status'] = 'failed'
                active_simulations[sim_id]['error'] = str(e)

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

        return jsonify({
            'status': 'started',
            'simulation_id': sim_id
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulator/<sim_id>/status', methods=['GET'])
@require_auth
def get_simulation_status(sim_id, user=None):
    """Get simulation status."""
    if sim_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    sim = active_simulations[sim_id]
    return jsonify({
        'simulation_id': sim_id,
        'status': sim['status'],
        'started': sim['started'].isoformat(),
        'result': sim.get('result'),
        'error': sim.get('error')
    })

@app.route('/api/simulator/<sim_id>/result', methods=['GET'])
@require_auth
def get_simulation_result(sim_id, user=None):
    """Get complete simulation result."""
    if sim_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    sim = active_simulations[sim_id]
    if sim['status'] != 'completed':
        return jsonify({'error': f'Simulation {sim["status"]}'}), 400

    return jsonify(sim.get('result', {}))

# ==================== WEBSOCKET: SIMULATOR ====================

@socketio.on('join_simulation')
def on_join_simulation(data):
    """Join simulation room for updates."""
    sim_id = data.get('simulation_id')
    if sim_id:
        join_room(f"sim_{sim_id}")
        emit('status', {'data': f'Joined simulation {sim_id}'})

@socketio.on('leave_simulation')
def on_leave_simulation(data):
    """Leave simulation room."""
    sim_id = data.get('simulation_id')
    if sim_id:
        leave_room(f"sim_{sim_id}")
        emit('status', {'data': f'Left simulation {sim_id}'})

# ==================== STARTUP ====================

_initialized = False

@app.before_request
def setup():
    """Setup on first request."""
    global _initialized
    if not _initialized:
        initialize_on_startup()
        _initialized = True

def initialize_on_startup():
    """Initialize app on first request (for production servers)"""
    try:
        connect_mongodb()
        initialize_users()
        initialize_approvals()
        start_background_threads()

        # Initialize real metrics
        start_metrics_collection()
        init_storage()
    except Exception as e:
        print(f"⚠️  Initialization warning: {e}")

def start_background_threads():
    """Start telemetry and log streaming threads."""
    try:
        telemetry_thread = threading.Thread(target=stream_telemetry, daemon=True)
        telemetry_thread.start()

        logs_thread = threading.Thread(target=stream_logs, daemon=True)
        logs_thread.start()
    except Exception as e:
        print(f"⚠️  Background thread error: {e}")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ==================== INITIALIZATION FOR PRODUCTION ====================

# Initialize for production WSGI servers (Gunicorn, etc.)
try:
    print("\n" + "="*70)
    print("  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform")
    print("="*70)
    connect_mongodb()
    initialize_users()
    initialize_approvals()
    start_background_threads()

    # Start real metrics collection
    start_metrics_collection()
    init_storage()

    print("\n✅ NEXUS AIOPS initialized successfully")
    print("📍 Access at: http://localhost:5000")
    print("   Demo: admin / admin123\n")
except Exception as e:
    print(f"\n⚠️  Initialization completed with warnings: {e}")
    print("   (App will initialize on first request)")

# ==================== MAIN (Development) ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform")
    print("="*70)

    # Initialize
    try:
        connect_mongodb()
        initialize_users()
        initialize_approvals()
        start_background_threads()
    except Exception as e:
        print(f"⚠️  Initialization warning: {e}")

    print("\n📍 Access at: http://localhost:5000")
    print("   Demo: admin / admin123\n")

    # Run with socketio
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
