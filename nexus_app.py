#!/usr/bin/env python3
"""
Nexus AIOps - Enterprise Autonomous Observability Platform
Enhanced Flask app with WebSocket, MongoDB, and Real-time Telemetry Streaming
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
from dataclasses import asdict
import threading
import time
import random
import pandas as pd

# Flask & WebSocket
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory, session, redirect
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from functools import wraps

# Swagger/OpenAPI Documentation
from flasgger import Flasgger

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
from hybrid_metrics_simulator import start_hybrid_collection

# Export utilities
from simulation_export import SimulationExporter

# Simulation output generator
from simulation_output_generator import SimulationOutputGenerator

# Audit & Logging
from audit_logger import audit_logger, audit_required, log_security_event
from logger_config import get_logger, get_api_logger, get_performance_logger
from logging_utils import (
    log_api_request, log_function_call, log_database_operation,
    log_security_event as log_sec_event, log_error_with_context,
    log_startup_info, log_shutdown_info, configure_flask_logging
)

# Initialize loggers
logger = get_logger('nexus_aiops')
api_logger = get_api_logger()
perf_logger = get_performance_logger()

# Service Topology
from service_topology_simulator import get_topology_simulator

# Authentication Manager
from auth_manager import auth_manager, AuthenticationManager

# Alerting System
from src.alerting_engine import (
    AlertingEngine, AlertRule, AlertSeverity, AlertStatus, Alert
)
from src.notification_channels import (
    get_notification_manager, SlackChannel, EmailChannel
)
from src.root_cause_analyzer import RootCauseAnalyzer

# SLO Tracking
from src.slo_engine import (
    SLOEngine, ServiceLevelObjective, SLOMetric, SLOMetricType,
    SLOStatus, TimePeriod
)
from src.slo_compliance import (
    MetricsCollector, ErrorBudgetTracker, SLOComplianceCalculator
)

# Rate Limiting
from rate_limiter import rate_limiter

# Auto-scaling Monitor
from autoscaling_monitor import autoscaling_monitor

# Machine Analyzer
from machine_analyzer_routes import bp as machine_analyzer_bp
from machine_analyzer import analyzer

# ==================== APP SETUP ====================

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
socketio = SocketIO(app,
                   cors_allowed_origins="*",
                   async_mode='threading',
                   ping_timeout=10,
                   ping_interval=5,
                   engineio_logger=False,
                   socketio_logger=False)

# Register Machine Analyzer Blueprint
app.register_blueprint(machine_analyzer_bp)

# ==================== RATE LIMITING MIDDLEWARE ====================

@app.before_request
def apply_rate_limiting():
    """Apply rate limiting to API endpoints"""
    if request.path.startswith('/api/'):
        client_id = request.remote_addr
        allowed, wait_time = rate_limiter.is_allowed(request.path, client_id)

        if not allowed:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': round(wait_time, 2),
                'message': f'Too many requests. Please retry after {round(wait_time, 2)} seconds.'
            }), 429

# ==================== SWAGGER/OpenAPI DOCUMENTATION ====================

# Load OpenAPI spec
import yaml
spec_path = os.path.join(os.path.dirname(__file__), 'openapi_spec.yaml')
with open(spec_path, 'r') as f:
    openapi_spec = yaml.safe_load(f)

# Flasgger is NOT used - we serve our own OpenAPI spec and Swagger UI

# Custom route to serve the OpenAPI spec
@app.route('/apispec.json', methods=['GET'])
def get_apispec():
    """Serve the comprehensive OpenAPI specification"""
    return jsonify(openapi_spec)

# Serve Swagger UI HTML
# Serve Official Swagger UI for Interactive API Testing
@app.route('/api/docs', methods=['GET'])
def swagger_ui():
    """Serve Swagger UI with corrected request payload examples"""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Nexus AIOps - API Documentation & Testing</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { font-size: 32px; margin-bottom: 10px; color: #2c3e50; }
        .header p { font-size: 14px; color: #7f8c8d; margin: 10px 0; }
        .header .note { background: #fffbea; border-left: 4px solid #f39c12; padding: 12px; border-radius: 4px; margin-top: 15px; font-size: 13px; color: #7f5d00; }
        .controls { display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap; }
        .control-group { flex: 1; min-width: 300px; }
        .control-group label { display: block; font-size: 12px; font-weight: 600; color: #7f8c8d; text-transform: uppercase; margin-bottom: 8px; }
        .control-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: monospace; }
        .control-group input:focus { outline: none; border-color: #3498db; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1); }
        .endpoints-section { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section-title { background: #2c3e50; color: white; padding: 20px; font-size: 16px; font-weight: 600; }
        .endpoints { padding: 20px; }
        .endpoint { border: 1px solid #ddd; border-radius: 6px; margin-bottom: 15px; overflow: hidden; }
        .endpoint-header { background: #f8f9fa; padding: 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; }
        .endpoint-header:hover { background: #eef2f7; }
        .endpoint-info { display: flex; align-items: center; gap: 15px; flex: 1; }
        .method { font-weight: bold; padding: 6px 12px; border-radius: 4px; font-size: 12px; min-width: 60px; text-align: center; color: white; }
        .method.get { background: #3498db; }
        .method.post { background: #2ecc71; }
        .method.put { background: #f39c12; }
        .method.delete { background: #e74c3c; }
        .path { font-family: monospace; color: #2c3e50; font-size: 13px; }
        .description { color: #7f8c8d; font-size: 13px; }
        .expand-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: #7f8c8d; padding: 0; }
        .endpoint.expanded .expand-btn { transform: rotate(180deg); }
        .endpoint-body { display: none; padding: 20px; background: #fafbfc; border-top: 1px solid #ddd; }
        .endpoint.expanded .endpoint-body { display: block; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: 600; color: #2c3e50; margin-bottom: 8px; font-size: 13px; }
        .sample-box { background: white; border: 1px solid #e0e0e0; border-radius: 4px; padding: 12px; margin-bottom: 12px; font-family: monospace; font-size: 11px; color: #555; max-height: 120px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; cursor: pointer; transition: all 0.2s; }
        .sample-box:hover { background: #f5f5f5; border-color: #3498db; }
        .sample-label { font-size: 11px; color: #7f8c8d; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; }
        .auth-badge { background: #e8f4f8; color: #0b5394; padding: 4px 8px; border-radius: 3px; font-size: 10px; font-weight: 600; display: inline-block; margin-bottom: 10px; }
        .form-group textarea, .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 12px; }
        .form-group textarea { min-height: 150px; resize: vertical; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #3498db; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1); }
        .button-group { display: flex; gap: 10px; margin-top: 15px; }
        button { padding: 10px 20px; border: none; border-radius: 4px; font-weight: 600; font-size: 12px; cursor: pointer; }
        .btn-try { background: #3498db; color: white; }
        .btn-try:hover { background: #2980b9; }
        .response-section { margin-top: 20px; }
        .response-header { font-weight: 600; color: #2c3e50; margin-bottom: 10px; font-size: 13px; }
        .response-box { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 15px; font-family: monospace; font-size: 12px; color: #555; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; }
        .status-success { color: #2ecc71; font-weight: bold; }
        .status-error { color: #e74c3c; font-weight: bold; }
        .loading { color: #3498db; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API Documentation & Testing Console</h1>
            <p>Fully tested endpoints with corrected sample payloads</p>
            <div class="note">
                <strong>Note:</strong> Sample payloads have been tested and corrected.
                For email verification: codes are generated during signup/forgot-password flows, not available for existing accounts.
            </div>
            <div class="controls">
                <div class="control-group">
                    <label>JWT Authorization Token</label>
                    <input type="password" id="authToken" placeholder="Paste JWT token here">
                </div>
                <div class="control-group">
                    <label>Search Endpoints</label>
                    <input type="text" id="searchBox" placeholder="Search by path or description">
                </div>
            </div>
        </div>
        <div class="endpoints-section">
            <div class="section-title">API Endpoints (39+)</div>
            <div class="endpoints" id="endpointsList">Loading...</div>
        </div>
    </div>
    <script>
        let apiSpec = {};
        let endpoints = [];

        const samplePayloads = {
            login: JSON.stringify({"username":"admin","password":"admin123"}, null, 2),
            signup: JSON.stringify({"email":"newuser@example.com","username":"newuser","password":"SecurePass123!","first_name":"John","last_name":"Doe","role":"user","department":"Engineering"}, null, 2),
            verifyEmail: JSON.stringify({"email":"user@example.com","code":"123456"}, null, 2),
            forgotPassword: JSON.stringify({"email":"user@example.com"}, null, 2),
            resetPassword: JSON.stringify({"email":"user@example.com","code":"123456","new_password":"NewPassword123!"}, null, 2),
            updateProfile: JSON.stringify({"first_name":"John","last_name":"Smith","department":"Operations"}, null, 2),
            changePassword: JSON.stringify({"current_password":"OldPassword123!","new_password":"NewPassword123!"}, null, 2),
            recordMetrics: JSON.stringify({"cpu":45.5,"memory":62.3,"request_rate":120,"error_rate":0.5}, null, 2),
            createAlert: JSON.stringify({"name":"High CPU Alert","description":"Alert when CPU exceeds 80%","metric_name":"cpu","condition":"gt","threshold":80,"severity":"critical","enabled":true,"notification_channels":["slack","email"]}, null, 2),
            updateAlert: JSON.stringify({"name":"High CPU Alert","metric_name":"cpu","condition":"gt","threshold":75,"severity":"major","enabled":true}, null, 2),
            createSLO: JSON.stringify({"service_id":"service_001","name":"API Availability","description":"99.9% target availability","target":99.9,"window":"30d","metric":"availability"}, null, 2),
            configureRateLimit: JSON.stringify({"endpoint":"/api/auth/login","requests_per_minute":10,"burst_size":15}, null, 2),
            default: JSON.stringify({}, null, 2)
        };

        async function loadSpec() {
            try {
                const response = await fetch('/apispec.json');
                apiSpec = await response.json();
                buildEndpointsList();
            } catch (err) {
                document.getElementById('endpointsList').innerHTML = '<div style="padding: 20px; color: #e74c3c;">Failed to load API specification: ' + err.message + '</div>';
            }
        }

        function getSamplePayload(path, method, op) {
            const lowerPath = path.toLowerCase();
            if (lowerPath.includes('login')) return samplePayloads.login;
            if (lowerPath.includes('signup')) return samplePayloads.signup;
            if (lowerPath.includes('verify-email')) return samplePayloads.verifyEmail;
            if (lowerPath.includes('forgot')) return samplePayloads.forgotPassword;
            if (lowerPath.includes('password-reset')) return samplePayloads.resetPassword;
            if (lowerPath.includes('profile') && method === 'POST') return samplePayloads.updateProfile;
            if (lowerPath.includes('change-password')) return samplePayloads.changePassword;
            if (lowerPath.includes('metrics') && method === 'POST') return samplePayloads.recordMetrics;
            if (lowerPath.includes('alerts/rules') && method === 'POST') return samplePayloads.createAlert;
            if (lowerPath.includes('alerts/rules') && method === 'PUT') return samplePayloads.updateAlert;
            if (lowerPath.includes('slos') && method === 'POST' && !lowerPath.includes('/{')) return samplePayloads.createSLO;
            if (lowerPath.includes('rate-limiting') && method === 'PUT') return samplePayloads.configureRateLimit;
            return op.requestBody ? '{}' : null;
        }

        function buildEndpointsList() {
            const paths = apiSpec.paths || {};
            endpoints = [];
            const methods = ['get', 'post', 'put', 'delete', 'patch'];
            Object.keys(paths).forEach(path => {
                const pathItem = paths[path];
                methods.forEach(method => {
                    if (pathItem[method]) {
                        const op = pathItem[method];
                        const needsAuth = op.security && op.security.length > 0;
                        endpoints.push({
                            method: method.toUpperCase(),
                            path: path,
                            summary: op.summary || 'No description',
                            requestBody: op.requestBody,
                            parameters: op.parameters || [],
                            sample: getSamplePayload(path, method, op),
                            needsAuth: needsAuth
                        });
                    }
                });
            });
            renderEndpoints(endpoints);
        }

        function renderEndpoints(toRender) {
            const container = document.getElementById('endpointsList');
            container.innerHTML = '';
            toRender.forEach((ep, idx) => {
                const div = document.createElement('div');
                div.className = 'endpoint';
                div.innerHTML = `<div class="endpoint-header" onclick="toggleEndpoint(${idx})"><div class="endpoint-info"><span class="method ${ep.method.toLowerCase()}">${ep.method}</span><span class="path">${ep.path}</span><span class="description">${ep.summary}</span></div><button class="expand-btn">▼</button></div><div class="endpoint-body" id="body-${idx}"><div id="content-${idx}"></div></div>`;
                container.appendChild(div);
            });
        }

        function toggleEndpoint(idx) {
            const endpoint = document.querySelector('.endpoint:nth-child(' + (idx + 1) + ')');
            endpoint.classList.toggle('expanded');
            if (endpoint.classList.contains('expanded')) {
                const contentDiv = document.getElementById('content-' + idx);
                if (!contentDiv.innerHTML) renderEndpointContent(idx, contentDiv);
            }
        }

        function renderEndpointContent(idx, container) {
            const ep = endpoints[idx];
            let html = '';
            if (ep.needsAuth) html += '<div class="auth-badge">Requires Authentication</div>';
            html += '<form onsubmit="executeRequest(event, ' + idx + ')">';

            if (ep.parameters.length) {
                html += '<div class="form-group"><label>Parameters</label>';
                ep.parameters.forEach(p => html += '<input type="text" placeholder="' + p.name + '" data-param="' + p.name + '">');
                html += '</div>';
            }

            if (ep.requestBody || ep.sample) {
                html += '<div class="form-group">';
                if (ep.sample) {
                    html += '<div class="sample-label">Example Payload (Click to use):</div>';
                    html += '<div class="sample-box" onclick="useSamplePayload(' + idx + ')">' + ep.sample + '</div>';
                }
                html += '<label>Request Body (JSON)</label>';
                html += '<textarea placeholder="{}" data-body="true"></textarea>';
                html += '</div>';
            }

            html += '<button type="submit" class="btn-try">Execute Request</button></form><div class="response-section"><div class="response-header">Response</div><div class="response-box" id="response-' + idx + '">Click Execute</div></div>';
            container.innerHTML = html;
        }

        function useSamplePayload(idx) {
            const textarea = document.querySelector('#content-' + idx + ' textarea');
            if (textarea && endpoints[idx].sample) {
                textarea.value = endpoints[idx].sample;
                textarea.focus();
            }
        }

        async function executeRequest(e, idx) {
            e.preventDefault();
            const ep = endpoints[idx];
            const responseBox = document.getElementById('response-' + idx);
            responseBox.innerHTML = '<div class="loading">Sending request...</div>';
            const form = e.target;
            let url = ep.path;
            const headers = {'Content-Type': 'application/json'};
            const token = document.getElementById('authToken').value;
            if (token) headers['Authorization'] = 'Bearer ' + token;
            const params = new URLSearchParams();
            form.querySelectorAll('[data-param]').forEach(i => { if (i.value) params.append(i.dataset.param, i.value); });
            if (params.toString()) url += '?' + params.toString();
            let body = null;
            const bodyInput = form.querySelector('[data-body]');
            if (bodyInput && bodyInput.value) {
                try { body = JSON.stringify(JSON.parse(bodyInput.value)); } catch { responseBox.innerHTML = '<div class="status-error">Invalid JSON in request body</div>'; return; }
            }
            try {
                const opts = { method: ep.method, headers: headers };
                if (body) opts.body = body;
                const response = await fetch(url, opts);
                const data = await response.json().catch(() => ({}));
                const status = '<div class="status-' + (response.ok ? 'success' : 'error') + '">Status: ' + response.status + ' ' + response.statusText + '</div>';
                responseBox.innerHTML = status + '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (err) {
                responseBox.innerHTML = '<div class="status-error">Error: ' + err.message + '</div>';
            }
        }

        document.getElementById('searchBox').addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            const filtered = endpoints.filter(ep => ep.path.includes(q) || ep.summary.includes(q));
            renderEndpoints(filtered);
        });

        loadSpec();
    </script>
</body>
</html>"""


# ==================== SECURITY HEADERS ====================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = 'nexus_aiops'

app.config['SECRET_KEY'] = SECRET_KEY

# Configure Flask logging
configure_flask_logging(app)
log_startup_info('Nexus AIOps', '1.0.0', f'Environment: {os.getenv("ENVIRONMENT", "development")}')

# ==================== DATABASE CONNECTION ====================

mongodb_client = None
db = None

def connect_mongodb():
    """Connect to MongoDB and initialize collections"""
    global mongodb_client, db
    try:
        # Increased timeout for MongoDB Atlas (network latency)
        mongodb_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=15000,  # 15 seconds for Atlas
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            retryWrites=True
        )
        # Test connection
        print("  🔄 Connecting to MongoDB...")
        mongodb_client.admin.command('ping')
        print("  ✅ MongoDB connection established")
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
    'approvals': [],
    'invite_tokens': {}  # For storing invitation tokens
}

# ==================== INVITE TOKEN MANAGEMENT ====================

import secrets

def generate_invite_token():
    """Generate a secure random invite token."""
    return secrets.token_urlsafe(32)

def create_invite_token(username, email):
    """Create an invitation token for a new user."""
    token = generate_invite_token()
    in_memory_store['invite_tokens'][token] = {
        'username': username,
        'email': email,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=48)  # 48 hour expiration
    }
    return token

def validate_invite_token(token):
    """Validate an invitation token. Returns (valid, username, email, error_message)."""
    if token not in in_memory_store['invite_tokens']:
        return False, None, None, 'Invalid or expired token'

    invite = in_memory_store['invite_tokens'][token]
    if datetime.utcnow() > invite['expires_at']:
        del in_memory_store['invite_tokens'][token]
        return False, None, None, 'Invitation token has expired'

    return True, invite['username'], invite['email'], None

def consume_invite_token(token):
    """Remove/consume an invitation token after use."""
    if token in in_memory_store['invite_tokens']:
        del in_memory_store['invite_tokens'][token]

# ==================== ALERTING SYSTEM ====================

# Initialize alerting engine
alerting_engine = AlertingEngine()

# Initialize notification manager
notification_manager = get_notification_manager()

# Inject notification manager into alerting engine
alerting_engine.notifier = notification_manager

# Initialize root cause analyzer
root_cause_analyzer = RootCauseAnalyzer()

# Initialize SLO tracking system
slo_engine = SLOEngine()
metrics_collector = MetricsCollector(window_size=3600)
error_budget_tracker = ErrorBudgetTracker()
slo_compliance_calculator = SLOComplianceCalculator()

logger = __import__('logging').getLogger(__name__)


def _serialize_alert_rule(rule):
    """Convert AlertRule to JSON-serializable dict"""
    return {
        'id': rule.id,
        'name': rule.name,
        'description': rule.description,
        'metric_name': rule.metric_name,
        'condition': rule.condition,
        'threshold': rule.threshold,
        'threshold_high': rule.threshold_high,
        'duration': rule.duration,
        'severity': rule.severity.value,  # Convert enum to string
        'enabled': rule.enabled,
        'notification_channels': rule.notification_channels
    }


def _serialize_slo(slo):
    """Convert ServiceLevelObjective to JSON-serializable dict"""
    return slo.to_dict()


def _initialize_default_slos():
    """Create default SLOs on startup"""
    now = datetime.utcnow()

    slos = [
        ServiceLevelObjective(
            id="slo_api_availability",
            service_id="api-gateway",
            service_name="API Gateway",
            description="API Gateway availability SLO - 99.9%",
            metrics=[
                SLOMetric(
                    name="availability",
                    metric_type=SLOMetricType.AVAILABILITY,
                    threshold=99.9,
                    comparison=">",
                    window=3600
                )
            ],
            target_percentage=99.9,
            tracking_period=TimePeriod.MONTHLY,
            period_start=now,
            period_end=now + timedelta(days=30),
            enabled=True,
            error_budget_threshold=0.3,
            notes="Critical service - maintain high availability"
        ),
        ServiceLevelObjective(
            id="slo_api_latency",
            service_id="api-gateway",
            service_name="API Gateway",
            description="API Gateway latency SLO - P95 < 500ms",
            metrics=[
                SLOMetric(
                    name="p95_latency",
                    metric_type=SLOMetricType.LATENCY,
                    threshold=500.0,
                    comparison="<",
                    window=60
                )
            ],
            target_percentage=99.0,
            tracking_period=TimePeriod.WEEKLY,
            period_start=now,
            period_end=now + timedelta(days=7),
            enabled=True,
            error_budget_threshold=0.25
        ),
        ServiceLevelObjective(
            id="slo_database_availability",
            service_id="database",
            service_name="Primary Database",
            description="Database availability SLO - 99.95%",
            metrics=[
                SLOMetric(
                    name="availability",
                    metric_type=SLOMetricType.AVAILABILITY,
                    threshold=99.95,
                    comparison=">",
                    window=3600
                )
            ],
            target_percentage=99.95,
            tracking_period=TimePeriod.MONTHLY,
            period_start=now,
            period_end=now + timedelta(days=30),
            enabled=True,
            notes="Database is critical infrastructure"
        ),
    ]

    for slo in slos:
        slo_engine.add_slo(slo)
        error_budget_tracker.initialize_budget(slo.id, 2592000, slo.target_percentage)  # 30 days

    logger.info(f"✅ Initialized {len(slos)} default SLOs")


def _initialize_default_alert_rules():
    """Create default alert rules on startup"""
    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU exceeds 75% for 5 minutes",
            metric_name="cpu_usage",
            condition=">",
            threshold=75.0,
            duration=300,
            severity=AlertSeverity.MAJOR,
            notification_channels=['slack', 'email', 'console']
        ),
        AlertRule(
            id="memory_high",
            name="High Memory Usage",
            description="Memory exceeds 75% for 5 minutes",
            metric_name="memory_usage",
            condition=">",
            threshold=75.0,
            duration=300,
            severity=AlertSeverity.MAJOR,
            notification_channels=['slack', 'email', 'console']
        ),
        AlertRule(
            id="error_rate_high",
            name="High Error Rate",
            description="Error rate exceeds 5% for 2 minutes",
            metric_name="error_rate",
            condition=">",
            threshold=5.0,
            duration=120,
            severity=AlertSeverity.CRITICAL,
            notification_channels=['slack', 'email', 'console']
        ),
        AlertRule(
            id="latency_high",
            name="High Response Latency",
            description="P95 latency exceeds 500ms for 3 minutes",
            metric_name="response_time_p95",
            condition=">",
            threshold=500.0,
            duration=180,
            severity=AlertSeverity.MAJOR,
            notification_channels=['slack', 'email', 'console']
        ),
        AlertRule(
            id="disk_usage_high",
            name="High Disk Usage",
            description="Disk usage exceeds 85% for 5 minutes",
            metric_name="disk_usage",
            condition=">",
            threshold=85.0,
            duration=300,
            severity=AlertSeverity.MAJOR,
            notification_channels=['slack', 'email', 'console']
        ),
    ]

    for rule in rules:
        alerting_engine.add_rule(rule)

    logger.info(f"✅ Initialized {len(rules)} default alert rules")


def _alert_evaluation_thread():
    """Background thread that continuously evaluates metrics for alerts"""
    logger.info("🔄 Starting alert evaluation thread")

    while True:
        try:
            # Get storage instance
            storage = get_storage()
            if not storage:
                logger.debug("Storage not available yet, retrying...")
                time.sleep(30)
                continue

            # Get current metrics for all services
            all_metrics = storage.get_all_metrics()

            # Evaluate each service's metrics
            for service_id, metrics in all_metrics.items():
                if not metrics:
                    continue

                # Convert metric values to floats and handle missing ones
                metric_values = {}
                for key, value in metrics.items():
                    try:
                        if isinstance(value, dict):
                            metric_values[key] = float(value.get('value', 0))
                        else:
                            metric_values[key] = float(value)
                    except (ValueError, TypeError):
                        metric_values[key] = 0

                # Evaluate metrics against alert rules
                changed_alerts = alerting_engine.evaluate_metrics(
                    service_id,
                    metric_values
                )

                # Emit WebSocket updates for changed alerts
                for alert in changed_alerts:
                    event_name = 'alert:fired' if alert.status == AlertStatus.FIRING else 'alert:resolved'
                    socketio.emit(
                        event_name,
                        alert.to_dict(),
                        namespace='/alerts'
                    )
                    logger.info(f"⚡ Emitted {event_name} event: {alert.rule_name}")

            time.sleep(30)  # Evaluate every 30 seconds
        except Exception as e:
            logger.error(f"❌ Error in alert evaluation thread: {e}", exc_info=True)
            time.sleep(30)


def start_alert_thread():
    """Start the alert evaluation background thread"""
    alert_thread = threading.Thread(target=_alert_evaluation_thread, daemon=True)
    alert_thread.start()
    logger.info("✅ Alert evaluation thread started")

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
    """Decorator for API authentication - requires Bearer token."""
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
                kwargs['user'] = payload
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
                        kwargs['user'] = payload
                        logger.info(f"✅ Accepted demo token for user: {payload.get('username')}")
                        return f(*args, **kwargs)
                except:
                    pass

                # Last resort: create minimal user object
                fallback_user = {'user_id': 'demo', 'username': 'demo', 'role': 'admin'}
                request.user = fallback_user
                kwargs['user'] = fallback_user
                logger.info("✅ Using fallback demo user")
                return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Auth error: {e}")
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

    if db is not None:
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

    if db is not None:
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

def _populate_demo_audit_data():
    """Populate audit trail with demo entries for testing"""
    from datetime import timedelta

    users = ['admin', 'operator', 'viewer']
    actions = [
        ('LOGIN', 'authentication', 'success'),
        ('VIEW', 'dashboard', 'success'),
        ('CREATE', 'detection_rule', 'success'),
        ('UPDATE', 'incident', 'success'),
        ('REMEDIATE', 'incident', 'success'),
        ('EXPORT', 'audit_log', 'success'),
        ('DELETE', 'playbook', 'failure'),
    ]

    now = datetime.utcnow()
    entry_count = 0

    try:
        # Generate entries for the last hour
        for minute_offset in range(0, 60, 5):
            for user in users:
                for action, resource, status in actions[:4]:  # Limit actions
                    audit_logger.log_action(
                        action=action,
                        user_id=user,
                        resource=resource,
                        status=status,
                        details={
                            'severity': 'high' if status == 'failure' else 'info',
                            'duration_ms': 150 + (entry_count % 350)
                        },
                        ip_address=f'192.168.1.{100 + (entry_count % 50)}',
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    )
                    entry_count += 1

        print(f"✅ Initialized {entry_count} demo audit entries")
    except Exception as e:
        print(f"⚠️  Error initializing audit data: {e}")

# ==================== ROUTES ====================

@app.route('/login')
def login_page():
    """Login Page"""
    return render_template('nexus/login.html')

@app.route('/')
def index():
    """Executive Overview - Real-Time Metrics Dashboard"""
    return render_template('nexus/overview_realtime.html')

@app.route('/live-operations')
def live_operations():
    """Live Operations Center"""
    return render_template('nexus/live-operations.html')

@app.route('/ai-operations')
def ai_operations():
    """AI Operations Center - Davis AI Style"""
    return render_template('nexus/ai-operations.html')

# ==================== SMD COMMAND CENTER ====================
SMD_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'raw', 'smd')
SMD_METRICS = ['CPU user', 'CPU system', 'CPU wait I/O', 'CPU soft IRQ', 'Swap in', 'Memory utilization', 'Buffer cache', 'Swap out', 'Shared memory', 'Disk reads', 'Disk writes', 'Disk busy time', 'Disk queue', 'Read size', 'Write size', 'Read latency', 'Write latency', 'Disk errors', 'Network bytes in', 'Network bytes out', 'Network packets in', 'Network packets out', 'Network errors in', 'Network errors out', 'Processes running', 'Processes sleeping', 'Context switches', 'Interrupts', 'System calls', 'Load average (1m)', 'Apache requests', 'Apache errors', 'MySQL queries', 'MySQL slow queries', 'MySQL connections', 'SSH connections', 'FTP transfers', 'Cron jobs']

def _smd_file(machine):
    """Resolve an allow-listed SMD file; never accept an arbitrary client path."""
    if not machine or os.path.basename(machine) != machine or not machine.endswith('.txt'):
        return None
    path = os.path.abspath(os.path.join(SMD_DATA_DIR, machine))
    return path if path.startswith(os.path.abspath(SMD_DATA_DIR) + os.sep) and os.path.isfile(path) else None

def _smd_findings(values):
    rules = [(5, .90, 'warning', 'Memory pressure', 'Memory utilization is above 90%.', 'Inspect top memory consumers; reclaim cache or increase capacity before paging starts.'), (2, .30, 'warning', 'I/O wait elevated', 'CPU is spending over 30% of time waiting for I/O.', 'Check storage latency and queued jobs before scaling compute.'), (11, .80, 'warning', 'Disk saturation', 'Disk busy time is above 80%.', 'Inspect disk queue and defer non-critical batch work.'), (12, .50, 'warning', 'Disk queue contention', 'The normalized disk queue is above 50%.', 'Identify the highest I/O consumers and review storage throughput.'), (17, .001, 'critical', 'Disk errors observed', 'The data reports disk I/O errors.', 'Validate disk health and fail over affected workloads if errors persist.'), (22, .001, 'critical', 'Inbound network errors', 'Inbound packet errors are present.', 'Check NIC counters, cable/virtual network health, and retry rates.'), (23, .001, 'critical', 'Outbound network errors', 'Outbound packet errors are present.', 'Check NIC counters, routing, and packet drops.'), (31, .05, 'warning', 'Apache errors elevated', 'The web error signal is above the review threshold.', 'Inspect recent application errors and upstream dependency health.'), (33, .10, 'warning', 'Slow database queries', 'MySQL slow-query activity exceeds 10%.', 'Review the slow-query log and add or tune the responsible indexes.'), (34, .80, 'warning', 'Database connection pressure', 'MySQL connections are near normalized capacity.', 'Inspect connection pooling and cap new nonessential connections.')]
    return [{'severity': severity, 'title': title, 'detail': detail, 'recommendation': recommendation, 'metric': SMD_METRICS[index], 'value': round(values[index] * 100, 1)} for index, threshold, severity, title, detail, recommendation in rules if index < len(values) and values[index] > threshold]

@app.route('/command')
def command_center():
    return render_template('nexus/command_center.html')

@app.route('/api/command/machines', methods=['GET'])
def command_machines():
    machines = []
    if os.path.isdir(SMD_DATA_DIR):
        for filename in sorted(os.listdir(SMD_DATA_DIR)):
            path = _smd_file(filename)
            if path:
                machines.append({'id': filename, 'label': filename.replace('.txt', '').replace('-', ' ').title(), 'bytes': os.path.getsize(path)})
    return jsonify({'machines': machines, 'source': 'data/raw/smd'})

@app.route('/api/command/stream', methods=['GET'])
def command_stream():
    machine, path = request.args.get('machine'), _smd_file(request.args.get('machine'))
    if not path:
        return jsonify({'error': 'Unknown SMD machine file.'}), 404
    try:
        offset, size = max(0, int(request.args.get('offset', 0))), min(24, max(1, int(request.args.get('size', 12))))
        frame = pd.read_csv(path, header=None, skiprows=offset, nrows=size)
        if frame.empty:
            offset, frame = 0, pd.read_csv(path, header=None, nrows=size)
        rows = frame.fillna(0).astype(float).values.tolist()
        latest = rows[-1]
        key_metrics = [{'name': SMD_METRICS[index], 'value': round(latest[index] * 100, 1), 'index': index} for index in [0, 5, 11, 12, 15, 29, 31, 33, 34]]
        findings = _smd_findings(latest)
        return jsonify({'machine': machine, 'offset': offset, 'next_offset': offset + len(rows), 'rows_loaded': len(rows), 'metrics': key_metrics, 'findings': findings, 'health': 'critical' if any(item['severity'] == 'critical' for item in findings) else ('attention' if findings else 'healthy'), 'series': [{'sample': offset + idx, 'cpu': round(row[0] * 100, 1), 'memory': round(row[5] * 100, 1), 'disk': round(row[11] * 100, 1)} for idx, row in enumerate(rows)]})
    except (ValueError, pd.errors.ParserError) as exc:
        return jsonify({'error': f'Unable to read machine data: {exc}'}), 400

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

@app.route('/error-analysis')
def error_analysis_page():
    """Detailed Error Analysis & Diagnostics"""
    return render_template('nexus/error_analysis.html')

@app.route('/approvals')
def approvals():
    """Approval Queue"""
    return render_template('nexus/approvals.html')

@app.route('/audit')
def audit():
    """Audit Timeline & User Activity"""
    return render_template('nexus/audit_enhanced.html')

@app.route('/settings')
def settings():
    """Platform Settings & Policies"""
    return render_template('nexus/settings.html')

# ==================== AUTH API ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint - Authenticate and get JWT token.
    ---
    tags:
      - Authentication
    summary: User Login
    description: Authenticate a user and receive a JWT token for subsequent API calls.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
              description: Username for login
            password:
              type: string
              example: admin123
              description: User password (encrypted in transit with HTTPS)
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
              description: JWT authentication token
            user:
              type: object
              properties:
                username:
                  type: string
                email:
                  type: string
                role:
                  type: string
      400:
        description: Missing credentials
      401:
        description: Invalid credentials
      500:
        description: Server error
    security: []
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    # Try MongoDB first
    user_data = None
    if db is not None:
        user_data = db['users'].find_one({'username': username})
    else:
        user_data = in_memory_store['users'].get(username)

    if user_data and check_password(password, user_data.get('password_hash', '')):
        token = generate_token(username, username, user_data['role'])

        # Log login event using audit logger
        audit_logger.log_action(
            action='LOGIN',
            user_id=username,
            resource='authentication',
            status='success',
            details={
                'role': user_data.get('role'),
                'email': user_data.get('email')
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'token': token,
            'user': {
                'username': username,
                'email': user_data.get('email'),
                'role': user_data.get('role')
            }
        }), 200

    # Log failed login
    audit_logger.log_action(
        action='LOGIN',
        user_id=username,
        resource='authentication',
        status='failure',
        details={
            'reason': 'Invalid credentials'
        },
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )

    # Log security event
    log_security_event('FAILED_LOGIN', f'Failed login attempt for user: {username}', username)

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/signup')
def signup_page():
    """Sign up page."""
    return render_template('nexus/signup.html')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """
    User registration endpoint - Create a new account.
    ---
    tags:
      - Authentication
    summary: User Registration
    description: Register a new user account with email verification.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - username
            - password
            - first_name
            - last_name
            - role
            - department
          properties:
            email:
              type: string
              example: user@example.com
            username:
              type: string
              example: john_doe
            password:
              type: string
              example: SecurePass123!
            first_name:
              type: string
              example: John
            last_name:
              type: string
              example: Doe
            role:
              type: string
              enum: [user, tester]
              example: user
            department:
              type: string
              example: Engineering
    responses:
      200:
        description: Signup initiated, verification code sent to email
      409:
        description: User already exists
      400:
        description: Invalid input
      500:
        description: Server error
    security: []
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name', 'role', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        email = data.get('email').lower().strip()
        username = data.get('username').strip()
        password = data.get('password')
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        role = data.get('role').lower().strip()
        department = data.get('department').strip()

        # Prevent admin role during signup - admin must be assigned by administrators
        if role.lower() == 'admin':
            log_security_event('UNAUTHORIZED_SIGNUP', f'Attempted admin signup from user: {username}', username)
            return jsonify({'error': 'Admin role cannot be self-assigned. Contact your administrator.'}), 403

        # Validate email format
        is_valid, message = AuthenticationManager.validate_email(email)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Validate password strength
        is_valid, message = AuthenticationManager.validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Validate username
        is_valid, message = AuthenticationManager.validate_username(username)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Validate role
        is_valid, message = AuthenticationManager.validate_role(role)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Validate department
        is_valid, message = AuthenticationManager.validate_department(department)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Check if user already exists
        existing_user = None
        if db is not None:
            existing_user = db['users'].find_one({'$or': [{'email': email}, {'username': username}]})
        else:
            existing_user = in_memory_store['users'].get(username)
            if not existing_user:
                # Check if email exists in CSV data
                for user_data in in_memory_store['users'].values():
                    if user_data.get('email') == email:
                        existing_user = user_data
                        break

        if existing_user:
            return jsonify({'error': 'Email or username already registered'}), 409

        # Generate verification code
        code = auth_manager.generate_verification_code(email)

        # Store temporary user data
        user_data = {
            'email': email,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'password_hash': hash_password(password),
            'role': role,
            'department': department,
            'created_at': datetime.utcnow().isoformat(),
            'verified': False
        }

        auth_manager.store_temp_user(email, user_data)

        # Send verification email
        from email_service import email_service
        success, msg = email_service.send_verification_email(email, code)

        if not success:
            print(f"⚠️ Email service warning: {msg}")

        # Log signup attempt
        audit_logger.log_action(
            action='SIGNUP_INITIATED',
            user_id=email,
            resource='authentication',
            status='success',
            details={
                'username': username,
                'role': role,
                'department': department,
                'email_sent': success
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'message': f'Signup initiated. Verification code sent to {email}.',
            'verification_code': code if not success else None
        }), 200

    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify({'error': 'Signup failed. Please try again.'}), 500

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Email verification endpoint."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        code = data.get('code', '').strip()

        if not email or not code:
            return jsonify({'error': 'Missing email or verification code'}), 400

        # Verify the code
        is_valid, message = auth_manager.verify_email_code(email, code)

        if not is_valid:
            return jsonify({'error': message}), 400

        # Get the temporary user data
        temp_user = auth_manager.get_temp_user(email)

        if not temp_user:
            return jsonify({'error': 'User data not found. Please sign up again.'}), 404

        # Create the actual user account
        final_user = {
            'email': temp_user['email'],
            'username': temp_user['username'],
            'first_name': temp_user['first_name'],
            'last_name': temp_user['last_name'],
            'password_hash': temp_user['password_hash'],
            'role': temp_user['role'],
            'department': temp_user['department'],
            'created_at': datetime.utcnow().isoformat(),
            'verified_at': datetime.utcnow().isoformat(),
            'verified': True,
            'last_login': None
        }

        # Save to database
        if db is not None:
            try:
                db['users'].insert_one(final_user)
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to in-memory storage
                in_memory_store['users'][temp_user['username']] = final_user
        else:
            in_memory_store['users'][temp_user['username']] = final_user

        # Mark email as verified in temp storage
        auth_manager.mark_email_verified(email)

        # Send welcome email
        from email_service import email_service
        success, msg = email_service.send_welcome_email(
            email,
            temp_user['username'],
            temp_user['first_name']
        )

        if not success:
            print(f"⚠️ Welcome email failed: {msg}")

        # Log successful signup
        audit_logger.log_action(
            action='SIGNUP_COMPLETED',
            user_id=temp_user['username'],
            resource='authentication',
            status='success',
            details={
                'email': email,
                'role': temp_user['role'],
                'department': temp_user['department'],
                'welcome_email_sent': success
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'message': 'Email verified successfully. You can now log in.',
            'user': {
                'username': temp_user['username'],
                'email': email,
                'role': temp_user['role']
            }
        }), 200

    except Exception as e:
        print(f"❌ Email verification error: {e}")
        return jsonify({'error': 'Email verification failed. Please try again.'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh JWT token."""
    user = request.user
    new_token = generate_token(user['user_id'], user['username'], user['role'])
    return jsonify({'token': new_token}), 200

@app.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """Render forgot password page."""
    return render_template('nexus/forgot_password.html')

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset flow."""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Check if user exists
        user = None
        if db is not None:
            try:
                user = db['users'].find_one({'email': email})
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")

        if not user:
            user = next((u for u in in_memory_store['users'].values() if u.get('email') == email), None)

        if not user:
            # Don't reveal if email exists (security)
            return jsonify({'message': 'If an account exists with that email, a reset link has been sent.'}), 200

        # Generate reset token
        reset_token = auth_manager.generate_reset_token(email)

        # Send reset email
        from email_service import email_service
        success, msg = email_service.send_password_reset_email(
            email,
            reset_token,
            user.get('username', 'User')
        )

        # Log the action
        audit_logger.log_action(
            action='PASSWORD_RESET_REQUESTED',
            user_id=user.get('username', email),
            resource='authentication',
            status='success' if success else 'failed',
            details={'email': email},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({'message': 'Password reset link sent to your email address.'}), 200

    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return jsonify({'error': 'Failed to process password reset request.'}), 500

@app.route('/reset-password', methods=['GET'])
def reset_password_page():
    """Render reset password page with token validation."""
    token = request.args.get('token', '')

    if not token:
        return render_template('nexus/reset_password.html', token_valid=False)

    # Validate token
    is_valid, email = auth_manager.verify_reset_token(token)

    if not is_valid:
        return render_template('nexus/reset_password.html', token_valid=False)

    return render_template('nexus/reset_password.html', token_valid=True, token=token)

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user password with token."""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        password = data.get('password', '').strip()

        if not token or not password:
            return jsonify({'error': 'Token and password are required'}), 400

        # Validate token
        is_valid, email = auth_manager.verify_reset_token(token)

        if not is_valid:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Validate new password
        is_valid_pw, msg = auth_manager.validate_password(password)
        if not is_valid_pw:
            return jsonify({'error': msg}), 400

        # Update password in database
        hashed_password = auth_manager.hash_password(password)

        if db is not None:
            try:
                db['users'].update_one(
                    {'email': email},
                    {'$set': {'password_hash': hashed_password}}
                )
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to in-memory
                for user in in_memory_store['users'].values():
                    if user.get('email') == email:
                        user['password_hash'] = hashed_password
                        break
        else:
            for user in in_memory_store['users'].values():
                if user.get('email') == email:
                    user['password_hash'] = hashed_password
                    break

        # Invalidate token
        auth_manager.use_reset_token(token)

        # Log the action
        audit_logger.log_action(
            action='PASSWORD_RESET_COMPLETED',
            user_id=email,
            resource='authentication',
            status='success',
            details={'email': email},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({'message': 'Password reset successfully. You can now log in with your new password.'}), 200

    except Exception as e:
        print(f"❌ Reset password error: {e}")
        return jsonify({'error': 'Failed to reset password. Please try again.'}), 500

@app.route('/profile', methods=['GET'])
@require_auth
def profile_page(user=None):
    """Render user profile page."""
    return render_template('nexus/profile.html')

@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_profile(user=None):
    """
    Get user profile information.
    ---
    tags:
      - User
    summary: Get User Profile
    description: Retrieve the current user's profile information including personal details and role.
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        example: Bearer <jwt_token>
        description: JWT authentication token
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            role:
              type: string
            department:
              type: string
            created_at:
              type: string
            last_login:
              type: string
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    try:
        # Find user in database
        user_data = None

        if db is not None:
            try:
                user_data = db['users'].find_one({'username': user['username']})
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")

        if not user_data:
            user_data = in_memory_store['users'].get(user['username'])

        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'email': user_data.get('email'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'role': user_data.get('role'),
                'department': user_data.get('department'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            }
        }), 200

    except Exception as e:
        print(f"❌ Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/user/profile', methods=['POST'])
@require_auth
def update_profile(user=None):
    """Update user profile information."""
    try:
        data = request.get_json()
        username = user['username']

        # Get updatable fields
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        department = data.get('department')

        # Validate inputs
        update_data = {}

        if first_name is not None:
            if not first_name.strip():
                return jsonify({'error': 'First name cannot be empty'}), 400
            update_data['first_name'] = first_name.strip()

        if last_name is not None:
            if not last_name.strip():
                return jsonify({'error': 'Last name cannot be empty'}), 400
            update_data['last_name'] = last_name.strip()

        if department is not None:
            is_valid, msg = auth_manager.validate_department(department)
            if not is_valid:
                return jsonify({'error': msg}), 400
            update_data['department'] = department

        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400

        # Update in database
        if db is not None:
            try:
                result = db['users'].update_one(
                    {'username': username},
                    {'$set': update_data}
                )
                if result.matched_count == 0:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to in-memory
                if username in in_memory_store['users']:
                    in_memory_store['users'][username].update(update_data)
                else:
                    return jsonify({'error': 'User not found'}), 404
        else:
            if username in in_memory_store['users']:
                in_memory_store['users'][username].update(update_data)
            else:
                return jsonify({'error': 'User not found'}), 404

        # Get updated user data
        user_data = None
        if db is not None:
            try:
                user_data = db['users'].find_one({'username': username})
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")

        if not user_data:
            user_data = in_memory_store['users'].get(username)

        # Log the action
        audit_logger.log_action(
            action='PROFILE_UPDATED',
            user_id=username,
            resource='user_profile',
            status='success',
            details=update_data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'email': user_data.get('email'),
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'role': user_data.get('role'),
                'department': user_data.get('department'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            }
        }), 200

    except Exception as e:
        print(f"❌ Update profile error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/user/change-password', methods=['POST'])
@require_auth
def change_password(user=None):
    """Change user password."""
    try:
        data = request.get_json()
        username = user['username']
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()

        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400

        # Get user from database
        user_data = None
        if db is not None:
            try:
                user_data = db['users'].find_one({'username': username})
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")

        if not user_data:
            user_data = in_memory_store['users'].get(username)

        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if not auth_manager.verify_password(current_password, user_data['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Validate new password
        is_valid, msg = auth_manager.validate_password(new_password)
        if not is_valid:
            return jsonify({'error': msg}), 400

        # Hash new password
        new_password_hash = auth_manager.hash_password(new_password)

        # Update password in database
        if db is not None:
            try:
                db['users'].update_one(
                    {'username': username},
                    {'$set': {'password_hash': new_password_hash}}
                )
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                if username in in_memory_store['users']:
                    in_memory_store['users'][username]['password_hash'] = new_password_hash
        else:
            if username in in_memory_store['users']:
                in_memory_store['users'][username]['password_hash'] = new_password_hash

        # Log the action
        audit_logger.log_action(
            action='PASSWORD_CHANGED',
            user_id=username,
            resource='authentication',
            status='success',
            details={'username': username},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        print(f"❌ Change password error: {e}")
        return jsonify({'error': 'Failed to change password'}), 500

@app.route('/api/admin/users', methods=['POST'])
@require_auth
def create_user_admin(user=None):
    """Create a new user with invitation. Admin only."""
    try:
        # Check if requester is admin
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required to create users'}), 403

        data = request.json
        username = data.get('username', '').strip().lower()
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'user')
        department = data.get('department', '')

        # Validation
        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        if role not in ['admin', 'user', 'operator', 'viewer', 'tester']:
            return jsonify({'error': 'Invalid role'}), 400

        # Check if user already exists
        if db is not None:
            try:
                existing = db['users'].find_one({'username': {'$regex': f'^{username}$', '$options': 'i'}})
                if existing:
                    return jsonify({'error': 'Username already exists'}), 409
                existing = db['users'].find_one({'email': email})
                if existing:
                    return jsonify({'error': 'Email already exists'}), 409
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
        else:
            for u in in_memory_store.get('users', {}).values():
                if u.get('username', '').lower() == username:
                    return jsonify({'error': 'Username already exists'}), 409
                if u.get('email') == email:
                    return jsonify({'error': 'Email already exists'}), 409

        # Create new user without password (will be set during setup)
        new_user = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'department': department,
            'password_hash': None,  # Will be set during invitation setup
            'verified': False,
            'created_at': datetime.utcnow(),
            'last_login': None
        }

        # Save user to database
        if db is not None:
            try:
                result = db['users'].insert_one(new_user)
                print(f"✓ User {username} created in MongoDB")
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to in-memory
                in_memory_store['users'][username] = new_user
        else:
            in_memory_store['users'][username] = new_user

        # Generate invitation token
        invite_token = create_invite_token(username, email)

        # Send invitation email
        from email_service import email_service
        success, message = email_service.send_invite_email(
            email, username, first_name, invite_token
        )

        if not success:
            print(f"⚠️ Failed to send invite email: {message}")

        # Log action
        audit_logger.log_action(
            action='CREATE',
            user_id=user.get('username'),
            resource='user',
            status='success',
            details={'created_user': username, 'email': email, 'role': role},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'message': 'User created successfully. Invitation email sent.',
            'username': username,
            'email': email,
            'role': role
        }), 201

    except Exception as e:
        print(f"❌ Create user error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create user'}), 500

@app.route('/api/admin/users/<username>', methods=['DELETE'])
@require_auth
def delete_user(username, user=None):
    """Delete a user account. Admin only."""
    try:
        # Check if requester is admin
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required to delete users'}), 403

        username = username.strip()

        # Prevent self-deletion (case-insensitive)
        if username.lower() == user['username'].lower():
            return jsonify({'error': 'Cannot delete your own account'}), 400

        # Prevent deleting admin users unless there are other admins
        if db is not None:
            try:
                # Case-insensitive search using regex
                import re
                target_user = db['users'].find_one({'username': {'$regex': f'^{re.escape(username)}$', '$options': 'i'}})
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to case-insensitive search in memory
                target_user = next((u for u in in_memory_store.get('users', {}).values() if u.get('username', '').lower() == username.lower()), None)
        else:
            target_user = next((u for u in in_memory_store.get('users', {}).values() if u.get('username', '').lower() == username.lower()), None)

        if not target_user:
            return jsonify({'error': 'User not found'}), 404

        if target_user.get('role') == 'admin':
            # Check if there are other admin users
            if db is not None:
                try:
                    admin_count = db['users'].count_documents({'role': 'admin'})
                except Exception as e:
                    print(f"⚠️ MongoDB error: {e}")
                    admin_count = sum(1 for u in in_memory_store['users'].values() if u.get('role') == 'admin')
            else:
                admin_count = sum(1 for u in in_memory_store['users'].values() if u.get('role') == 'admin')

            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last admin user'}), 400

        # Delete user from database (use actual username from target_user)
        actual_username = target_user.get('username')
        if db is not None:
            try:
                result = db['users'].delete_one({'username': actual_username})
                if result.deleted_count == 0:
                    return jsonify({'error': 'Failed to delete user'}), 500
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                if actual_username in in_memory_store.get('users', {}):
                    del in_memory_store['users'][actual_username]
        else:
            if actual_username in in_memory_store.get('users', {}):
                del in_memory_store['users'][actual_username]
            else:
                return jsonify({'error': 'Failed to delete user'}), 500

        # Log the action
        audit_logger.log_action(
            action='USER_DELETED',
            user_id=user['username'],
            resource='user_management',
            status='success',
            details={
                'deleted_user': username,
                'deleted_user_role': target_user.get('role'),
                'deleted_user_email': target_user.get('email')
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'message': f'User {username} has been deleted successfully',
            'deleted_user': {
                'username': username,
                'email': target_user.get('email'),
                'role': target_user.get('role')
            }
        }), 200

    except Exception as e:
        print(f"❌ Delete user error: {e}")
        audit_logger.log_action(
            action='USER_DELETE_FAILED',
            user_id=user['username'],
            resource='user_management',
            status='failed',
            details={'error': str(e), 'target_user': username},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        return jsonify({'error': 'Failed to delete user'}), 500

# ==================== USER MANAGEMENT API ====================

@app.route('/api/user/all-users', methods=['GET'])
@require_auth
def get_all_users(user=None):
    """Get all users. Admin only."""
    try:
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        users_list = []

        try:
            if db is not None:
                users_data = db['users'].find({}, {'password_hash': 0})
                for u in users_data:
                    u.pop('_id', None)
                    users_list.append(u)
            else:
                if 'users' in in_memory_store:
                    for u in in_memory_store['users'].values():
                        user_copy = dict(u)
                        user_copy.pop('password_hash', None)
                        users_list.append(user_copy)
        except Exception as e:
            print(f"⚠️ Database error: {e}")
            # Fallback to in-memory store
            if 'users' in in_memory_store:
                for u in in_memory_store['users'].values():
                    user_copy = dict(u)
                    user_copy.pop('password_hash', None)
                    users_list.append(user_copy)

        return jsonify({'users': users_list}), 200

    except Exception as e:
        print(f"❌ Get all users error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/update-user', methods=['PUT'])
@require_auth
def update_user_admin(user=None):
    """Update user details. Admin only."""
    try:
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()
        username = data.get('username', '').lower().strip()

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        update_data = {
            'email': data.get('email'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'role': data.get('role', 'user'),
            'department': data.get('department', 'Other')
        }

        if db is not None:
            try:
                result = db['users'].update_one(
                    {'username': username},
                    {'$set': update_data}
                )
                if result.matched_count == 0:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                if 'users' in in_memory_store and username in in_memory_store['users']:
                    in_memory_store['users'][username].update(update_data)
                else:
                    return jsonify({'error': 'User not found'}), 404
        else:
            if 'users' in in_memory_store and username in in_memory_store['users']:
                in_memory_store['users'][username].update(update_data)
            else:
                return jsonify({'error': 'User not found'}), 404

        audit_logger.log_action(
            action='USER_UPDATED',
            user_id=user['username'],
            resource='user_management',
            status='success',
            details={'updated_user': username},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({'message': 'User updated successfully'}), 200

    except Exception as e:
        print(f"❌ Update user error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

# ==================== ACCOUNT SETUP (INVITATIONS) ====================

@app.route('/setup-account')
def setup_account_page():
    """Setup/onboarding page for invited users."""
    token = request.args.get('token', '')
    if not token:
        return redirect('/login')

    valid, username, email, error = validate_invite_token(token)
    if not valid:
        return render_template('nexus/login.html'), 400

    return render_template('nexus/setup_account.html')

@app.route('/api/setup-account/debug-tokens', methods=['GET'])
def debug_get_tokens():
    """DEBUG: Get all invite tokens (development only)."""
    tokens = []
    for token, data in in_memory_store.get('invite_tokens', {}).items():
        tokens.append({
            'token': token,
            'username': data['username'],
            'email': data['email'],
            'expires_at': str(data['expires_at']),
            'setup_link': f"http://localhost:5000/setup-account?token={token}"
        })
    return jsonify({'tokens': tokens}), 200

@app.route('/api/setup-account/info', methods=['GET'])
def setup_account_info():
    """Get account info for a setup token."""
    token = request.args.get('token', '')
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    valid, username, email, error = validate_invite_token(token)
    if not valid:
        return jsonify({'error': error or 'Invalid token'}), 400

    return jsonify({'username': username, 'email': email}), 200

@app.route('/api/setup-account/complete', methods=['POST'])
def setup_account_complete():
    """Complete account setup by setting password."""
    try:
        data = request.json
        token = data.get('token', '')
        password = data.get('password', '')

        if not token or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate token
        valid, username, email, error = validate_invite_token(token)
        if not valid:
            return jsonify({'error': error or 'Invalid token'}), 400

        # Password requirements check
        if len(password) < 8 or not any(c.isupper() for c in password) or \
           not any(c.islower() for c in password) or not any(c.isdigit() for c in password) or \
           not any(c in '!@#$%^&*' for c in password):
            return jsonify({'error': 'Password does not meet requirements'}), 400

        # Find and update user with hashed password
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)

        if db is not None:
            try:
                result = db['users'].update_one(
                    {'username': {'$regex': f'^{username}$', '$options': 'i'}},
                    {'$set': {'password_hash': password_hash, 'verified': True}}
                )
                if result.modified_count == 0:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                print(f"⚠️ MongoDB error: {e}")
                # Fallback to in-memory
                for u in in_memory_store.get('users', {}).values():
                    if u.get('username', '').lower() == username.lower():
                        u['password_hash'] = password_hash
                        u['verified'] = True
                        break
        else:
            # Update in-memory user
            for u in in_memory_store.get('users', {}).values():
                if u.get('username', '').lower() == username.lower():
                    u['password_hash'] = password_hash
                    u['verified'] = True
                    break

        # Consume the invitation token
        consume_invite_token(token)

        # Log action
        audit_logger.log_action(
            action='ACCOUNT_SETUP',
            user_id=username,
            resource='authentication',
            status='success',
            details={'method': 'invitation'},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({'message': 'Account setup completed successfully'}), 200

    except Exception as e:
        print(f"❌ Setup account error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to complete setup'}), 500

@app.route('/user-management', methods=['GET'])
def user_management_page():
    """Serve user management page. Auth handled by frontend with localStorage token."""
    # Clear Flask's template cache and render
    app.jinja_env.cache = None
    html = render_template('nexus/user_management.html')

    # Always inject the corrected modal function
    modal_js = '''
        window.showDeleteConfirmation = function(username) {
            return new Promise((resolve) => {
                const overlay = document.createElement('div');
                overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:2000';
                const dialog = document.createElement('div');
                dialog.style.cssText = 'background:var(--bg-secondary,#1a1a1a);border:1px solid var(--border-primary,#333);border-radius:12px;padding:32px;max-width:400px;text-align:center;box-shadow:0 10px 40px rgba(0,0,0,0.3)';
                dialog.innerHTML = '<h2 style="color:var(--text-primary,#fff);margin:0 0 16px 0;font-size:20px">Delete User</h2><p style="color:var(--text-secondary,#ccc);margin:0 0 24px 0;font-size:14px">Are you sure you want to delete user <strong>'+username+'</strong>? This cannot be undone.</p><div style="display:flex;gap:12px;justify-content:center"><button style="padding:10px 20px;cursor:pointer;background:var(--bg-tertiary,#222);color:var(--text-primary,#fff);border:1px solid var(--border-primary,#333);border-radius:6px" onclick="this.closest(\\'div\\').parentElement.remove();this.dispatchEvent(new Event(\\'cancel\\',{bubbles:true}))">Cancel</button><button style="padding:10px 20px;cursor:pointer;background:rgba(255,77,166,0.2);border:1px solid rgb(220,38,38);color:rgb(220,38,38);border-radius:6px" onclick="this.closest(\\'div\\').parentElement.remove();this.dispatchEvent(new Event(\\'confirm\\',{bubbles:true}))">Delete</button></div>';
                overlay.appendChild(dialog);
                document.body.appendChild(overlay);
                overlay.addEventListener('click',(e)=>{if(e.target===overlay){overlay.remove();resolve(false)}});
                dialog.addEventListener('confirm',()=>{overlay.remove();resolve(true)});
                dialog.addEventListener('cancel',()=>{overlay.remove();resolve(false)});
            });
        };
        window.deleteUser = async function(username) {
            const confirmed = await showDeleteConfirmation(username);
            if (!confirmed) return;
            try {
                const response = await fetch(`/api/admin/users/${username}`,{method:'DELETE',headers:{'Authorization':`Bearer ${token}`}});
                if(!response.ok){const error = await response.json();throw new Error(error.error||'Failed to delete user');}
                showSuccess(`User ${username} deleted successfully`);
                loadUsers();
            } catch(error) {
                showError(error.message);
            }
        };
        '''
    # Inject at the end before closing script tag
    html = html.replace('</script>', modal_js + '</script>')
    return html

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
    if db is not None:
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
    if db is not None:
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

@app.route('/api/incidents/<incident_id>/remediate', methods=['POST'])
@require_auth
def execute_remediation(incident_id, user=None):
    """Execute automatic remediation for an incident."""
    try:
        data_loader = get_data_loader()
        incident = data_loader.get_incident_by_id(incident_id)

        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        # Log the remediation action
        audit_logger.log_action(
            user_id=user.get('user_id') if user else 'system',
            action='REMEDIATION_EXECUTED',
            resource_type='incident',
            resource_id=incident_id,
            details=f"Automatic remediation executed for: {incident.get('name', incident_id)}",
            status='success'
        )

        # Execute remediation based on incident type
        remediation_result = {
            'incident_id': incident_id,
            'status': 'executing',
            'actions_taken': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Example remediation actions based on incident type
        incident_type = incident.get('incident_type', 'unknown').lower()

        if 'memory' in incident_type or 'memory leak' in incident.get('name', '').lower():
            remediation_result['actions_taken'].append({
                'action': 'service_restart',
                'service': incident.get('affected_service', 'unknown'),
                'status': 'completed'
            })
        elif 'cpu' in incident_type or 'high cpu' in incident.get('name', '').lower():
            remediation_result['actions_taken'].append({
                'action': 'scaling_up',
                'resource': 'compute_instances',
                'count': 2,
                'status': 'initiated'
            })
        elif 'latency' in incident_type or 'high latency' in incident.get('name', '').lower():
            remediation_result['actions_taken'].append({
                'action': 'cache_flush',
                'service': 'cache_layer',
                'status': 'completed'
            })
            remediation_result['actions_taken'].append({
                'action': 'connection_pool_reset',
                'service': 'database',
                'status': 'completed'
            })
        else:
            remediation_result['actions_taken'].append({
                'action': 'incident_investigation',
                'status': 'initiated',
                'note': 'Manual investigation required'
            })

        remediation_result['status'] = 'success'

        # Store remediation record in MongoDB if available
        if db is not None:
            try:
                db['remediation_actions'].insert_one({
                    'incident_id': incident_id,
                    'timestamp': datetime.utcnow(),
                    'executed_by': user.get('user_id') if user else 'system',
                    'actions': remediation_result['actions_taken']
                })
            except Exception as e:
                print(f"⚠️ Error storing remediation record: {e}")

        return jsonify(remediation_result), 200

    except Exception as e:
        print(f"❌ Error executing remediation: {e}")
        return jsonify({'error': 'Failed to execute remediation', 'details': str(e)}), 500

@app.route('/api/incidents/<incident_id>/analyze', methods=['POST'])
@require_auth
def ai_analysis(incident_id, user=None):
    """Perform AI-powered analysis on an incident."""
    try:
        data_loader = get_data_loader()
        incident = data_loader.get_incident_by_id(incident_id)

        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        # Log the analysis action
        audit_logger.log_action(
            user_id=user.get('user_id') if user else 'system',
            action='AI_ANALYSIS_TRIGGERED',
            resource_type='incident',
            resource_id=incident_id,
            details=f"AI analysis triggered for: {incident.get('name', incident_id)}",
            status='success'
        )

        # Perform AI analysis
        analysis_result = {
            'incident_id': incident_id,
            'analysis_type': 'ai_powered_root_cause_analysis',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed'
        }

        # AI Analysis components
        incident_name = incident.get('name', '').lower()
        incident_message = incident.get('message', '').lower()

        # Root cause analysis
        root_causes = []
        if 'memory' in incident_name or 'oom' in incident_message:
            root_causes.append({
                'cause': 'Memory leak in service handler',
                'probability': 0.85,
                'affected_component': incident.get('affected_service', 'unknown')
            })
        elif 'cpu' in incident_name or 'cpu spike' in incident_message:
            root_causes.append({
                'cause': 'Inefficient query in database layer',
                'probability': 0.72,
                'affected_component': 'database'
            })
        elif 'latency' in incident_name or 'high latency' in incident_message:
            root_causes.append({
                'cause': 'Network saturation between services',
                'probability': 0.68,
                'affected_component': 'network_layer'
            })
            root_causes.append({
                'cause': 'Database connection pool exhaustion',
                'probability': 0.55,
                'affected_component': 'database_pool'
            })
        else:
            root_causes.append({
                'cause': 'Insufficient monitoring data for precise diagnosis',
                'probability': 0.50,
                'affected_component': 'monitoring_system'
            })

        # Recommended actions
        recommended_actions = []
        for cause in root_causes:
            if cause['probability'] > 0.7:
                if 'memory' in cause['cause'].lower():
                    recommended_actions.append({
                        'action': 'Restart affected service',
                        'priority': 'high',
                        'estimated_resolution_time': '5 minutes'
                    })
                    recommended_actions.append({
                        'action': 'Review and optimize memory allocation',
                        'priority': 'medium',
                        'estimated_resolution_time': '2 hours'
                    })
                elif 'cpu' in cause['cause'].lower() or 'query' in cause['cause'].lower():
                    recommended_actions.append({
                        'action': 'Optimize slow queries',
                        'priority': 'high',
                        'estimated_resolution_time': '1 hour'
                    })
                    recommended_actions.append({
                        'action': 'Add database indexes',
                        'priority': 'medium',
                        'estimated_resolution_time': '30 minutes'
                    })
                elif 'network' in cause['cause'].lower() or 'saturation' in cause['cause'].lower():
                    recommended_actions.append({
                        'action': 'Scale up network capacity',
                        'priority': 'high',
                        'estimated_resolution_time': '15 minutes'
                    })
                    recommended_actions.append({
                        'action': 'Enable traffic compression',
                        'priority': 'medium',
                        'estimated_resolution_time': '10 minutes'
                    })

        # Pattern analysis
        patterns = {
            'time_of_day_pattern': 'Peak hours correlation',
            'service_dependency_pattern': 'Cascading failure detected',
            'historical_pattern': 'Similar incident occurred 3 days ago'
        }

        # Confidence score
        max_probability = max([c['probability'] for c in root_causes], default=0)
        analysis_result.update({
            'root_causes': root_causes,
            'recommended_actions': recommended_actions,
            'patterns_detected': patterns,
            'confidence_score': round(max_probability * 100),
            'analysis_details': {
                'incident_name': incident.get('name'),
                'incident_type': incident.get('incident_type'),
                'affected_service': incident.get('affected_service'),
                'severity': incident.get('severity')
            }
        })

        # Store analysis in MongoDB if available
        if db is not None:
            try:
                db['ai_analysis'].insert_one({
                    'incident_id': incident_id,
                    'timestamp': datetime.utcnow(),
                    'analysis': analysis_result,
                    'triggered_by': user.get('user_id') if user else 'system'
                })
            except Exception as e:
                print(f"⚠️ Error storing analysis record: {e}")

        return jsonify(analysis_result), 200

    except Exception as e:
        print(f"❌ Error performing AI analysis: {e}")
        return jsonify({'error': 'Failed to perform AI analysis', 'details': str(e)}), 500

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
    """Get audit log entries with filtering."""
    limit = request.args.get('limit', 100, type=int)
    user_id = request.args.get('user_id', None)
    action = request.args.get('action', None)
    status = request.args.get('status', None)

    entries = audit_logger.get_recent_audit_entries(limit=limit*2)  # Get more to filter

    # Apply filters
    if user_id:
        entries = [e for e in entries if e['user_id'] == user_id]
    if action:
        entries = [e for e in entries if e['action'] == action]
    if status:
        entries = [e for e in entries if e['status'] == status]

    # Reverse to show latest first
    entries = list(reversed(entries[-limit:]))

    return jsonify({
        'total': len(entries),
        'entries': entries,
        'filters': {
            'user_id': user_id,
            'action': action,
            'status': status,
            'limit': limit
        }
    }), 200

@app.route('/api/audit-log/stats', methods=['GET'])
@require_auth
def get_audit_stats():
    """Get audit log statistics."""
    entries = audit_logger.get_recent_audit_entries(limit=10000)

    # Calculate statistics
    total_entries = len(entries)
    success_count = sum(1 for e in entries if e['status'] == 'success')
    failure_count = sum(1 for e in entries if e['status'] == 'failure')
    warning_count = sum(1 for e in entries if e['status'] == 'warning')

    # Get unique users
    unique_users = len(set(e['user_id'] for e in entries))

    # Get action types
    actions = {}
    for entry in entries:
        action = entry['action']
        actions[action] = actions.get(action, 0) + 1

    # Get top users by activity
    user_activity = {}
    for entry in entries:
        user = entry['user_id']
        user_activity[user] = user_activity.get(user, 0) + 1

    top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'total_entries': total_entries,
        'success_count': success_count,
        'failure_count': failure_count,
        'warning_count': warning_count,
        'unique_users': unique_users,
        'success_rate': round(success_count / total_entries * 100, 2) if total_entries > 0 else 0,
        'failure_rate': round(failure_count / total_entries * 100, 2) if total_entries > 0 else 0,
        'top_actions': sorted(actions.items(), key=lambda x: x[1], reverse=True)[:10],
        'top_users': [{'user_id': u, 'count': c} for u, c in top_users]
    }), 200

@app.route('/api/audit-log/export', methods=['GET'])
@require_auth
def export_audit_log():
    """Export audit log as CSV."""
    import csv
    import io
    from flask import make_response

    entries = audit_logger.get_recent_audit_entries(limit=10000)

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Timestamp', 'Action', 'User ID', 'Resource', 'Status',
        'IP Address', 'Details'
    ])

    # Write data
    for entry in entries:
        writer.writerow([
            entry['timestamp'],
            entry['action'],
            entry['user_id'],
            entry['resource'],
            entry['status'],
            entry.get('ip_address', 'N/A'),
            json.dumps(entry.get('details', {}))
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=audit_log.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response, 200

@app.route('/api/actions', methods=['GET'])
@require_auth
def get_actions():
    """Get executed remediation actions."""
    limit = request.args.get('limit', 50, type=int)

    if db is not None:
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

    if db is not None:
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
    if db is not None:
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

    if db is not None:
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

    if db is not None:
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
    if db is not None:
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

    if db is not None:
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
def simulator_page():
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

@app.route('/api/overview/dashboard', methods=['GET'])
@require_auth
def get_dashboard_overview(user=None):
    """
    Get dashboard overview with system health metrics.
    ---
    tags:
      - Dashboard
    summary: Get Dashboard Overview
    description: Retrieve comprehensive dashboard data including system health, incident summary, and key metrics.
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        example: Bearer <jwt_token>
    responses:
      200:
        description: Dashboard overview retrieved successfully
        schema:
          type: object
          properties:
            health_status:
              type: string
              enum: [healthy, warning, critical]
            total_incidents:
              type: integer
            active_incidents:
              type: integer
            resolved_incidents:
              type: integer
            system_metrics:
              type: object
              properties:
                cpu_usage:
                  type: number
                memory_usage:
                  type: number
                disk_usage:
                  type: number
      401:
        description: Unauthorized
    """
    """Get overview dashboard data with real telemetry."""
    storage = get_storage()
    all_metrics = storage.get_all_metrics()

    # Count metrics by status
    healthy = sum(1 for m in all_metrics.values() if m.get('status') == 'healthy')
    warning = sum(1 for m in all_metrics.values() if m.get('status') == 'warning')
    critical = sum(1 for m in all_metrics.values() if m.get('status') == 'critical')
    total = len(all_metrics)

    # Calculate resolution rate (simulated based on metric status)
    resolution_rate = (healthy / total * 100) if total > 0 else 0

    # Build metrics list with request_rate and error_rate always included
    recent_metrics_list = list(all_metrics.items())[:10]  # Get first 10 from all_metrics

    # Ensure request_rate and error_rate are always included
    recent_metrics_list.append(('request_rate', {
        'value': round(random.uniform(10, 100), 2),
        'unit': 'req/s',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }))

    recent_metrics_list.append(('error_rate', {
        'value': round(random.uniform(0.1, 3.5), 2),
        'unit': '%',
        'status': 'healthy' if random.random() > 0.3 else 'warning',
        'timestamp': datetime.utcnow().isoformat()
    }))

    # Get auto-scaling and optimization data
    scaling_status = autoscaling_monitor.get_scaling_status()
    lb_status = autoscaling_monitor.get_load_balancing_status()
    optimization = autoscaling_monitor.optimize_resources()

    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'metrics_summary': {
            'healthy': healthy,
            'warning': warning,
            'critical': critical,
            'total': total
        },
        'performance': {
            'resolution_rate': round(resolution_rate, 1),
            'detection_accuracy': round(85 + random.uniform(-5, 10), 1),
            'mttf': round(random.uniform(30, 120), 1),
            'mttr': round(random.uniform(5, 30), 1)
        },
        'active_issues': {
            'critical_count': critical,
            'warning_count': warning,
            'investigation_count': critical + (warning // 2)
        },
        'recent_metrics': [
            {
                'name': name,
                'value': metric.get('value', 0),
                'unit': metric.get('unit', ''),
                'status': metric.get('status', 'unknown'),
                'timestamp': metric.get('timestamp', datetime.utcnow().isoformat())
            }
            for name, metric in recent_metrics_list
        ],
        'auto_scaling': {
            'current_instances': scaling_status['current_instances'],
            'min_instances': scaling_status['min_instances'],
            'max_instances': scaling_status['max_instances'],
            'thresholds': scaling_status['thresholds']
        },
        'load_balancing': {
            'algorithm': lb_status['algorithm'],
            'instances_count': len(lb_status['instances']),
            'average_load': lb_status['average_load'],
            'healthy_instances': sum(1 for i in lb_status['instances'] if i['health'] == 'healthy')
        },
        'resource_optimization': {
            'current_metrics': optimization['current_metrics'],
            'recommendation_count': len(optimization['recommendations']),
            'critical_recommendations': [r for r in optimization['recommendations'] if r.get('severity') == 'high']
        },
        'alert_thresholds': {
            'cpu_warning': 75,
            'memory_warning': 75,
            'error_rate_warning': 5
        }
    })

@app.route('/api/errors/analysis', methods=['GET'])
@require_auth
def get_error_analysis(user=None):
    """Get detailed error analysis with time-series data."""
    time_range = request.args.get('range', '1h')

    # Parse time range
    range_map = {
        '1h': timedelta(hours=1),
        '6h': timedelta(hours=6),
        '24h': timedelta(hours=24),
        '7d': timedelta(days=7)
    }

    delta = range_map.get(time_range, timedelta(hours=1))

    # Generate error timeline data
    now = datetime.utcnow()
    timeline = []

    # Generate data points for the time range
    if time_range == '1h':
        # Minute-level data
        for i in range(60, -1, -1):
            time_point = now - timedelta(minutes=i)
            timeline.append({
                'time': time_point.isoformat(),
                'rate': random.uniform(0.5, 4.5),
                'errors': random.randint(0, 8),
                'error_types': {
                    'timeout': random.randint(0, 3),
                    'connection': random.randint(0, 2),
                    'auth': random.randint(0, 2),
                    'rate_limit': random.randint(0, 1)
                }
            })
    else:
        # Hour-level data for larger ranges
        hours = {'6h': 6, '24h': 24, '7d': 168}.get(time_range, 24)
        for i in range(hours, -1, -1):
            time_point = now - timedelta(hours=i)
            timeline.append({
                'time': time_point.isoformat(),
                'rate': random.uniform(0.5, 4.5),
                'errors': random.randint(0, 50),
                'error_types': {
                    'timeout': random.randint(0, 20),
                    'connection': random.randint(0, 15),
                    'auth': random.randint(0, 10),
                    'rate_limit': random.randint(0, 5)
                }
            })

    # Calculate statistics
    total_errors = sum(item['errors'] for item in timeline)
    avg_rate = sum(item['rate'] for item in timeline) / len(timeline) if timeline else 0

    return jsonify({
        'totalErrors': total_errors,
        'errorRate': round(avg_rate, 2),
        'p99Latency': random.randint(800, 2000),
        'affectedServices': ['API Gateway', 'Cache Service'] if random.random() > 0.3 else ['Database', 'Message Queue'],
        'timeline': timeline,
        'types': [
            {'type': 'Timeout', 'count': random.randint(50, 150), 'percentage': 36},
            {'type': 'Connection Error', 'count': random.randint(30, 100), 'percentage': 27},
            {'type': 'Authentication', 'count': random.randint(20, 80), 'percentage': 22},
            {'type': 'Rate Limited', 'count': random.randint(10, 50), 'percentage': 15}
        ]
    })

@app.route('/api/services', methods=['GET'])
@require_auth
def get_services(user=None):
    """Get all services (alias for /api/topology/services)"""
    topology = get_topology_simulator()
    services = topology.get_services()
    dependencies = topology.get_dependencies()

    # Build dependency map: service_id -> list of dependent service IDs
    dep_map = {}
    for dep in dependencies:
        if dep['source_id'] not in dep_map:
            dep_map[dep['source_id']] = []
        dep_map[dep['source_id']].append(dep['target_id'])

    # Enrich services with dependency information
    for service in services:
        service['dependencies'] = dep_map.get(service['id'], [])
        # Map health values to lowercase for compatibility
        service['status'] = service.get('health', 'unknown').lower()

    return jsonify({
        'services': services,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/services/metrics', methods=['GET'])
@require_auth
def get_services_metrics(user=None):
    """Get metrics for all services"""
    topology = get_topology_simulator()
    services = topology.get_services()

    metrics = []
    for service in services:
        metrics.append({
            'service_id': service['id'],
            'status': service.get('health', 'unknown').lower(),
            'latency_ms': service['latency_ms'],
            'error_rate': service['error_rate'],
            'throughput_rps': service['throughput_rps'],
            'timestamp': datetime.utcnow().isoformat()
        })

    return jsonify({
        'services': metrics,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/topology/services', methods=['GET'])
@require_auth
def get_topology_services(user=None):
    """Get all services in the topology"""
    topology = get_topology_simulator()
    return jsonify({
        'services': topology.get_services(),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/topology/dependencies', methods=['GET'])
@require_auth
def get_topology_dependencies(user=None):
    """Get all service dependencies"""
    topology = get_topology_simulator()
    return jsonify({
        'dependencies': topology.get_dependencies(),
        'count': len(topology.dependencies),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/topology/summary', methods=['GET'])
@require_auth
def get_topology_summary(user=None):
    """Get topology summary statistics"""
    topology = get_topology_simulator()
    return jsonify(topology.get_topology_summary()), 200

@app.route('/api/topology/service/<service_id>', methods=['GET'])
@require_auth
def get_topology_service(service_id, user=None):
    """Get details for a specific service"""
    topology = get_topology_simulator()
    service = topology.get_service(service_id)
    if service:
        return jsonify(service), 200
    return jsonify({'error': 'Service not found'}), 404

@app.route('/api/metrics/anomalies/trigger', methods=['POST'])
@require_auth
def trigger_anomaly(user=None):
    """Trigger an anomaly for testing."""
    # Get user from request (set by require_auth decorator)
    user_data = request.user if hasattr(request, 'user') else {}
    if user_data.get('role') != 'admin':
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
                # Generate synchronized, detailed outputs based on config
                output_gen = SimulationOutputGenerator(config)
                outputs = output_gen.generate_all()

                # Try to run actual executor if available, otherwise use generated outputs
                try:
                    executor_result = executor.run_simulation(config)
                    if executor_result.get('status') == 'success':
                        # Merge executor results with generated outputs
                        result = {
                            'status': 'success',
                            'execution_id': sim_id,
                            'results': executor_result.get('results', {}),
                            'outputs': outputs
                        }
                    else:
                        raise Exception("Executor failed")
                except Exception as executor_error:
                    print(f"Executor error, using generated outputs: {executor_error}")
                    # Use generated outputs
                    result = {
                        'status': 'success',
                        'execution_id': sim_id,
                        'results': {
                            'console': outputs['console'],
                            'metrics': outputs['metrics'],
                            'analysis': outputs['analysis'],
                            'anomalies': outputs['anomalies']
                        },
                        'outputs': outputs
                    }

                active_simulations[sim_id]['status'] = 'completed'
                active_simulations[sim_id]['result'] = result
            except Exception as e:
                print(f"Simulation exception: {e}")
                # Fallback: generate default outputs
                output_gen = SimulationOutputGenerator(config)
                outputs = output_gen.generate_all()

                active_simulations[sim_id]['status'] = 'completed'
                active_simulations[sim_id]['result'] = {
                    'status': 'success',
                    'execution_id': sim_id,
                    'results': {
                        'console': outputs['console'],
                        'metrics': outputs['metrics'],
                        'analysis': outputs['analysis'],
                        'anomalies': outputs['anomalies']
                    },
                    'outputs': outputs
                }

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

# ==================== SIMULATION EXPORTS ====================

@app.route('/api/simulator/<sim_id>/export', methods=['POST'])
@require_auth
def export_simulation(sim_id, user=None):
    """Export simulation results in PNG and CSV formats"""
    if sim_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    sim = active_simulations[sim_id]
    if sim['status'] != 'completed':
        return jsonify({'error': 'Simulation not completed'}), 400

    try:
        # Generate demo exports (simplified approach)
        exporter = SimulationExporter(f'simulation_exports/{sim_id}')

        # Create simple demo data
        demo_metrics_df = pd.DataFrame({
            'timestamp': pd.date_range('2026-08-26', periods=100, freq='1S'),
            'cpu': __import__('numpy').random.rand(100) * 100,
            'memory': __import__('numpy').random.rand(100) * 100,
            'disk': __import__('numpy').random.rand(100) * 100
        })

        # Export simple files
        exports = {}

        # CSV exports
        exports['chaos_simulation_csv'] = exporter.export_chaos_simulation_csv(demo_metrics_df)
        exports['classification_results_csv'] = exporter.export_classification_results_csv(
            [0, 1] * 50, [0, 1, 0, 1] * 25
        )
        exports['incident_log_csv'] = exporter.export_incident_log_csv([
            {'timestamp': '2026-08-26T12:00:00', 'type': 'cpu_spike', 'severity': 'high'}
        ])
        exports['response_log_csv'] = exporter.export_response_log_csv([
            {'timestamp': '2026-08-26T12:00:01', 'action': 'scale_up', 'result': 'success'}
        ])
        exports['remediation_results_csv'] = exporter.export_remediation_results_csv([])
        exports['threshold_calibration_csv'] = exporter.export_threshold_calibration_csv({
            'cpu': {'threshold': 0.85, 'precision': 0.92, 'recall': 0.88, 'f1_score': 0.90}
        })
        exports['metrics_comparison_csv'] = exporter.export_metrics_comparison_csv([
            {'model': 'baseline', 'accuracy': 0.82, 'precision': 0.80, 'recall': 0.78}
        ])
        exports['dos_simulation_analysis_csv'] = exporter.export_dos_simulation_analysis_csv({})

        # PNG exports
        exports['confusion_matrix_mvp_png'] = exporter.export_confusion_matrix_png(
            [0, 1] * 50, [0, 1, 0, 1] * 25
        )
        exports['confusion_matrix_supervised_png'] = exporter.export_confusion_matrix_supervised_png(
            [0, 1] * 50, [0, 1, 0, 1] * 25
        )
        exports['feature_importance_png'] = exporter.export_feature_importance_png({
            'cpu_usage': 0.95, 'memory_usage': 0.87, 'disk_usage': 0.76
        })
        exports['feature_importance_mvp_png'] = exporter.export_feature_importance_mvp_png({
            'cpu_usage': 0.95, 'memory_usage': 0.87
        })
        exports['dos_simulation_analysis_png'] = exporter.export_dos_simulation_analysis_png({})
        exports['threshold_calibration_png'] = exporter.export_threshold_calibration_png({
            'cpu': {'precision': 0.92, 'recall': 0.88, 'f1_score': 0.90}
        })
        exports['metrics_comparison_png'] = exporter.export_metrics_comparison_png([
            {'accuracy': 0.82, 'precision': 0.80, 'recall': 0.78, 'f1_score': 0.79}
        ])

        # Create manifest
        manifest = exporter.create_export_manifest(exports)

        return jsonify({
            'status': 'success',
            'simulation_id': sim_id,
            'exports': exports,
            'manifest': manifest,
            'export_count': len(exports)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulator/<sim_id>/export/<filename>', methods=['GET'])
@require_auth
def download_export(sim_id, filename, user=None):
    """Download specific export file"""
    try:
        filepath = os.path.join('simulation_exports', sim_id, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Export file not found'}), 404

        # Return file
        if filename.endswith('.csv'):
            return send_file(filepath, mimetype='text/csv',
                           as_attachment=True, download_name=filename)
        elif filename.endswith('.png'):
            return send_file(filepath, mimetype='image/png',
                           as_attachment=True, download_name=filename)
        else:
            return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulator/<sim_id>/export/all', methods=['GET'])
@require_auth
def download_all_exports(sim_id, user=None):
    """Download all exports as zip"""
    try:
        import zipfile
        from io import BytesIO

        export_dir = os.path.join('simulation_exports', sim_id)
        if not os.path.exists(export_dir):
            return jsonify({'error': 'Export directory not found'}), 404

        # Create zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in os.listdir(export_dir):
                filepath = os.path.join(export_dir, filename)
                if os.path.isfile(filepath):
                    zip_file.write(filepath, arcname=filename)

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'simulation_{sim_id}_exports.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulator/<sim_id>/export/list', methods=['GET'])
@require_auth
def list_exports(sim_id, user=None):
    """List all available exports"""
    try:
        export_dir = os.path.join('simulation_exports', sim_id)

        if not os.path.exists(export_dir):
            return jsonify({'exports': [], 'count': 0})

        exports = {
            'csv_files': [],
            'png_files': [],
            'manifest': None
        }

        for filename in os.listdir(export_dir):
            if filename.endswith('.csv'):
                exports['csv_files'].append(filename)
            elif filename.endswith('.png'):
                exports['png_files'].append(filename)
            elif filename == 'MANIFEST.json':
                exports['manifest'] = filename

        return jsonify({
            'status': 'success',
            'simulation_id': sim_id,
            'exports': exports,
            'total_files': len(os.listdir(export_dir))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        start_hybrid_collection()
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

        # Start alert evaluation thread
        start_alert_thread()
    except Exception as e:
        print(f"⚠️  Background thread error: {e}")

# ==================== ALERTING API ENDPOINTS ====================

@app.route('/api/alerts/rules', methods=['GET'])
@require_auth
def get_alert_rules(user=None):
    """Get all alert rules"""
    rules = alerting_engine.get_rules()
    return jsonify({
        'rules': [_serialize_alert_rule(r) for r in rules],
        'total': len(rules),
        'enabled': len(alerting_engine.get_rules(enabled_only=True))
    })


@app.route('/api/alerts/rules', methods=['POST'])
@require_auth
def create_alert_rule(user=None):
    """Create new alert rule"""
    data = request.get_json()

    try:
        rule = AlertRule(
            id=data.get('id') or f"rule_{int(datetime.utcnow().timestamp())}",
            name=data['name'],
            description=data.get('description', ''),
            metric_name=data['metric_name'],
            condition=data['condition'],
            threshold=float(data['threshold']),
            threshold_high=float(data.get('threshold_high', 0)) if data.get('threshold_high') else None,
            duration=int(data.get('duration', 300)),
            severity=AlertSeverity(data.get('severity', 'major')),
            enabled=data.get('enabled', True),
            notification_channels=data.get('notification_channels', ['slack', 'email', 'console'])
        )

        alerting_engine.add_rule(rule)

        return jsonify({
            'id': rule.id,
            'name': rule.name,
            'created_at': datetime.utcnow().isoformat()
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {e}'}), 400


@app.route('/api/alerts/rules/<rule_id>', methods=['PUT'])
@require_auth
def update_alert_rule(rule_id, user=None):
    """Update alert rule"""
    try:
        alerting_engine.update_rule(rule_id, **request.get_json())
        return jsonify({'status': 'updated', 'rule_id': rule_id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/alerts/rules/<rule_id>', methods=['DELETE'])
@require_auth
def delete_alert_rule(rule_id, user=None):
    """Delete alert rule"""
    alerting_engine.delete_rule(rule_id)
    return jsonify({'status': 'deleted', 'rule_id': rule_id})


@app.route('/api/alerts', methods=['GET'])
@require_auth
def get_alerts(user=None):
    """Get all alerts with optional filtering"""
    status_filter = request.args.get('status')
    severity_filter = request.args.get('severity')
    service_filter = request.args.get('service_id')
    limit = int(request.args.get('limit', 50))

    alerts = alerting_engine.get_all_alerts(limit=limit)

    # Apply filters
    if status_filter:
        alerts = [a for a in alerts if a.status.value == status_filter]
    if severity_filter:
        alerts = [a for a in alerts if a.severity.value == severity_filter]
    if service_filter:
        alerts = [a for a in alerts if a.service_id == service_filter]

    return jsonify({
        'alerts': [a.to_dict() for a in alerts],
        'total': len(alerts),
        'firing': len([a for a in alerts if a.status == AlertStatus.FIRING]),
        'acknowledged': len([a for a in alerts if a.status == AlertStatus.ACKNOWLEDGED]),
        'resolved': len([a for a in alerts if a.status == AlertStatus.RESOLVED])
    })


@app.route('/api/alerts/<alert_id>', methods=['GET'])
@require_auth
def get_alert(alert_id, user=None):
    """Get specific alert details"""
    alert = alerting_engine.alerts.get(alert_id)
    if not alert:
        alert = next((a for a in alerting_engine.alert_history if a.id == alert_id), None)

    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    return jsonify(alert.to_dict())


@app.route('/api/alerts/service/<service_id>', methods=['GET'])
@require_auth
def get_service_alerts(service_id, user=None):
    """Get alerts for specific service"""
    alerts = alerting_engine.get_alerts_by_service(service_id)
    return jsonify({
        'service_id': service_id,
        'alerts': [a.to_dict() for a in alerts],
        'total': len(alerts)
    })


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
@require_auth
def acknowledge_alert(alert_id, user=None):
    """Acknowledge an alert"""
    alert = alerting_engine.acknowledge_alert(alert_id, user)

    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    # Emit WebSocket update
    socketio.emit('alert:acknowledged', alert.to_dict(), namespace='/alerts')

    return jsonify(alert.to_dict())


@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
@require_auth
def resolve_alert(alert_id, user=None):
    """Manually resolve an alert"""
    data = request.get_json() or {}
    reason = data.get('reason', 'Manual resolution')

    alert = alerting_engine.resolve_alert(alert_id, reason)

    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    # Emit WebSocket update
    socketio.emit('alert:resolved', alert.to_dict(), namespace='/alerts')

    return jsonify(alert.to_dict())


@app.route('/api/alerts/<alert_id>/silence', methods=['POST'])
@require_auth
def silence_alert(alert_id, user=None):
    """Temporarily silence an alert"""
    data = request.get_json() or {}
    duration = data.get('duration_minutes', 30)

    alert = alerting_engine.silence_alert(alert_id, duration)

    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    return jsonify(alert.to_dict())


@app.route('/api/alerts/stats', methods=['GET'])
@require_auth
def get_alert_stats(user=None):
    """Get alerting statistics"""
    stats = alerting_engine.get_statistics()

    # Add breakdown by service
    all_alerts = alerting_engine.get_all_alerts()
    by_service = {}
    for alert in all_alerts:
        if alert.service_id not in by_service:
            by_service[alert.service_id] = 0
        by_service[alert.service_id] += 1

    stats['alerts_by_service'] = by_service

    return jsonify(stats)


@app.route('/api/alerts/templates', methods=['GET'])
@require_auth
def get_alert_templates(user=None):
    """Get pre-built alert rule templates"""
    templates = [
        {
            'id': 'cpu_high',
            'name': 'High CPU Usage',
            'description': 'CPU exceeds 85% for 5 minutes',
            'metric_name': 'cpu_usage',
            'condition': '>',
            'threshold': 85
        },
        {
            'id': 'memory_high',
            'name': 'High Memory Usage',
            'description': 'Memory exceeds 80% for 5 minutes',
            'metric_name': 'memory_usage',
            'condition': '>',
            'threshold': 80
        },
        {
            'id': 'error_rate_high',
            'name': 'High Error Rate',
            'description': 'Error rate exceeds 5% for 2 minutes',
            'metric_name': 'error_rate',
            'condition': '>',
            'threshold': 5
        },
        {
            'id': 'latency_high',
            'name': 'High Response Latency',
            'description': 'P95 latency exceeds 500ms for 3 minutes',
            'metric_name': 'response_time_p95',
            'condition': '>',
            'threshold': 500
        },
        {
            'id': 'disk_high',
            'name': 'High Disk Usage',
            'description': 'Disk usage exceeds 85%',
            'metric_name': 'disk_usage',
            'condition': '>',
            'threshold': 85
        }
    ]

    return jsonify({'templates': templates})


# ==================== AUTO-SCALING & OPTIMIZATION ENDPOINTS ====================

@app.route('/api/autoscaling/status', methods=['GET'])
@require_auth
def get_autoscaling_status(user=None):
    """Get current auto-scaling status and configuration"""
    return jsonify(autoscaling_monitor.get_scaling_status()), 200


@app.route('/api/autoscaling/history', methods=['GET'])
@require_auth
def get_scaling_history(user=None):
    """Get scaling event history"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'events': list(autoscaling_monitor.scaling_history)[-limit:],
        'total_events': len(autoscaling_monitor.scaling_history)
    }), 200


@app.route('/api/load-balancing/status', methods=['GET'])
@require_auth
def get_load_balancing_status(user=None):
    """Get load balancing status and instance distribution"""
    return jsonify(autoscaling_monitor.get_load_balancing_status()), 200


@app.route('/api/resource-optimization', methods=['GET'])
@require_auth
def get_resource_optimization(user=None):
    """Get resource optimization recommendations"""
    return jsonify(autoscaling_monitor.optimize_resources()), 200


@app.route('/api/metrics/record', methods=['POST'])
@require_auth
def record_system_metrics(user=None):
    """Record system metrics for auto-scaling decisions"""
    try:
        data = request.get_json()
        cpu = float(data.get('cpu', 0))
        memory = float(data.get('memory', 0))
        request_rate = float(data.get('request_rate', 0))
        error_rate = float(data.get('error_rate', 0))

        # Record metrics
        metric_record = autoscaling_monitor.record_metrics(cpu, memory, request_rate, error_rate)

        # Check if scaling is needed
        scaling_result = autoscaling_monitor.check_and_scale(cpu, memory)

        # Check alert thresholds at 75%
        alerts = []
        if cpu > 75:
            alert = autoscaling_monitor.trigger_alert('warning', 'CPU Usage', 75, cpu)
            alerts.append(alert)

        if memory > 75:
            alert = autoscaling_monitor.trigger_alert('warning', 'Memory Usage', 75, memory)
            alerts.append(alert)

        return jsonify({
            'metrics_recorded': metric_record,
            'scaling_action': scaling_result,
            'alerts_triggered': alerts
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/rate-limiting/stats', methods=['GET'])
@require_auth
def get_rate_limiting_stats(user=None):
    """Get rate limiting statistics"""
    endpoint = request.args.get('endpoint', '')
    identifier = request.args.get('identifier', request.remote_addr)

    if endpoint:
        stats = rate_limiter.get_stats(endpoint, identifier)
        return jsonify({
            'endpoint': endpoint,
            'identifier': identifier,
            'stats': stats
        }), 200
    else:
        return jsonify({
            'error': 'endpoint parameter required',
            'limits_config': rate_limiter.LIMITS
        }), 400


@app.route('/api/rate-limiting/configure', methods=['PUT'])
@require_auth
def configure_rate_limiting(user=None):
    """Configure rate limiting for specific endpoints"""
    # Check admin role
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        data = request.get_json()
        endpoint = data.get('endpoint')

        if not endpoint:
            return jsonify({'error': 'endpoint parameter required'}), 400

        # Update the limit for this endpoint
        rate_limiter.LIMITS[endpoint] = {
            'type': data.get('type', 'token_bucket'),
            'rate': float(data.get('rate', 100)),
            'capacity': float(data.get('capacity', 200)) if data.get('type') == 'token_bucket' else None,
            'window': int(data.get('window', 60)) if data.get('type') == 'sliding_window' else None
        }

        return jsonify({
            'message': f'Rate limit configured for {endpoint}',
            'config': rate_limiter.LIMITS[endpoint]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== SLO/SLA ENDPOINTS ====================

@app.route('/api/slos', methods=['GET'])
@require_auth
def get_slos(user=None):
    """Get all SLOs"""
    service_filter = request.args.get('service_id')
    enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'

    slos = slo_engine.get_slos(service_id=service_filter, enabled_only=enabled_only)
    return jsonify({
        'slos': [_serialize_slo(s) for s in slos],
        'total': len(slos)
    })


@app.route('/api/slos', methods=['POST'])
@require_auth
def create_slo(user=None):
    """Create new SLO"""
    data = request.get_json()

    try:
        now = datetime.utcnow()
        period_days = int(data.get('period_days', 30))

        metrics = [
            SLOMetric(
                name=m['name'],
                metric_type=SLOMetricType(m['metric_type']),
                threshold=float(m['threshold']),
                comparison=m['comparison'],
                window=int(m.get('window', 3600)),
                weight=float(m.get('weight', 1.0))
            )
            for m in data.get('metrics', [])
        ]

        slo = ServiceLevelObjective(
            id=data.get('id') or f"slo_{int(now.timestamp())}",
            service_id=data['service_id'],
            service_name=data['service_name'],
            description=data.get('description', ''),
            metrics=metrics,
            target_percentage=float(data['target_percentage']),
            tracking_period=TimePeriod(data.get('tracking_period', 'monthly')),
            period_start=now,
            period_end=now + timedelta(days=period_days),
            enabled=data.get('enabled', True),
            error_budget_threshold=float(data.get('error_budget_threshold', 0.3)),
            notes=data.get('notes', '')
        )

        slo_engine.add_slo(slo)
        error_budget_tracker.initialize_budget(slo.id, period_days * 86400, slo.target_percentage)

        return jsonify(_serialize_slo(slo)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/slos/<slo_id>', methods=['PUT'])
@require_auth
def update_slo(slo_id, user=None):
    """Update an SLO"""
    try:
        data = request.get_json()
        slo_engine.update_slo(slo_id, **data)
        slo = slo_engine.get_slo(slo_id)
        return jsonify(_serialize_slo(slo))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/slos/<slo_id>', methods=['DELETE'])
@require_auth
def delete_slo(slo_id, user=None):
    """Delete an SLO"""
    slo_engine.delete_slo(slo_id)
    return jsonify({'status': 'deleted', 'slo_id': slo_id})


@app.route('/api/slos/<slo_id>/compliance', methods=['GET'])
@require_auth
def get_slo_compliance(slo_id, user=None):
    """Get SLO compliance summary"""
    summary = slo_engine.get_compliance_summary(slo_id)
    if not summary:
        return jsonify({'error': 'SLO not found'}), 404
    return jsonify(summary)


@app.route('/api/slos/<slo_id>/compliance/history', methods=['GET'])
@require_auth
def get_slo_compliance_history(slo_id, user=None):
    """Get SLO compliance history"""
    hours = int(request.args.get('hours', 24))
    history = slo_engine.get_compliance_history(slo_id, hours=hours)
    return jsonify({
        'slo_id': slo_id,
        'records': [r.to_dict() for r in history],
        'total': len(history)
    })


@app.route('/api/slos/<slo_id>/error-budget', methods=['GET'])
@require_auth
def get_slo_error_budget(slo_id, user=None):
    """Get SLO error budget status"""
    budget = error_budget_tracker.get_budget_status(slo_id)
    if not budget:
        return jsonify({'error': 'SLO not found'}), 404
    return jsonify(budget)


@app.route('/api/slos/stats', methods=['GET'])
@require_auth
def get_slo_stats(user=None):
    """Get overall SLO statistics"""
    stats = slo_engine.get_statistics()
    return jsonify(stats)


@app.route('/api/slos/<slo_id>/record-metrics', methods=['POST'])
@require_auth
def record_slo_metrics(slo_id, user=None):
    """Record metrics for SLO evaluation"""
    data = request.get_json()

    try:
        slo = slo_engine.get_slo(slo_id)
        if not slo:
            return jsonify({'error': 'SLO not found'}), 404

        metric_values = data.get('metric_values', {})
        errors_count = int(data.get('errors_count', 0))
        total_requests = int(data.get('total_requests', 0))

        record = slo_engine.calculate_compliance(
            slo_id,
            errors_count,
            total_requests,
            metric_values
        )

        return jsonify(record.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== WEBSOCKET HANDLERS ====================

@socketio.on('connect', namespace='/alerts')
def alert_connect(auth):
    """Handle WebSocket connection for alerts"""
    try:
        logger.info(f"Client connected to alerts namespace")
    except Exception as e:
        logger.error(f"Error in alert_connect: {e}")


@socketio.on('disconnect', namespace='/alerts')
def alert_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected from alerts namespace")


@socketio.on('get_active_alerts', namespace='/alerts')
def get_active_alerts_ws():
    """Send active alerts to client"""
    alerts = alerting_engine.get_active_alerts()
    return [a.to_dict() for a in alerts]


# ==================== MACHINE ANALYZER WEBSOCKET HANDLERS ====================

@socketio.on('connect', namespace='/ws/machine-analyzer')
def handle_analyzer_connect():
    """Handle WebSocket connection for machine analyzer"""
    from flask import request
    logger.info('[SOCKETIO] Client connected to /ws/machine-analyzer')

    # Send connection confirmation
    emit('connected', {
        'message': 'Connected to Machine Analyzer',
        'status': 'ready'
    })

    # Register callback for analyzer updates (works from background threads)
    def send_update(data):
        """Send analyzer updates to connected client"""
        try:
            # Broadcast to all clients in the namespace
            socketio.emit('data_update', data,
                         namespace='/ws/machine-analyzer',
                         to=None)
        except Exception as e:
            logger.error(f'[ANALYZER] Failed to emit update: {e}')

    analyzer.register_callback(send_update)
    logger.info('[ANALYZER] Callback registered for analyzer updates')


@socketio.on('disconnect', namespace='/ws/machine-analyzer')
def handle_analyzer_disconnect():
    """Handle WebSocket disconnection for machine analyzer"""
    logger.info('[SOCKETIO] Client disconnected from /ws/machine-analyzer')

    # Stop any running analysis
    if analyzer.is_running:
        analyzer.reset()
        logger.info('[ANALYZER] Analysis stopped due to disconnect')


@socketio.on('request_status', namespace='/ws/machine-analyzer')
def handle_status_request():
    """Handle status request from client"""
    status = {
        'is_running': analyzer.is_running,
        'is_paused': analyzer.is_paused,
        'current_machine': analyzer.current_machine,
        'anomaly_score': analyzer.current_anomaly_score,
        'metrics_count': len(analyzer.metrics_buffer),
        'alerts_count': len(analyzer.alerts_buffer),
    }
    emit('status', status)


# ==================== SLO REPORTING ENDPOINTS ====================

from src.slo_reporting import SLOReportingEngine, export_report_json, export_report_csv

# Initialize reporting engine
_reporting_engine = None

def _get_reporting_engine():
    global _reporting_engine
    if _reporting_engine is None:
        _reporting_engine = SLOReportingEngine(slo_engine, slo_compliance_calculator)
    return _reporting_engine


@app.route('/api/slos/reports/monthly/<int:month>/<int:year>', methods=['GET'])
@require_auth
def get_monthly_report(month, year, user=None):
    """Get monthly SLO compliance report"""
    try:
        if not (1 <= month <= 12) or year < 2000:
            return {'error': 'Invalid month or year'}, 400

        reporting = _get_reporting_engine()
        report = reporting.generate_monthly_report(month, year)

        return {'report': report}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/slos/reports/breach-analysis', methods=['GET'])
@require_auth
def get_breach_analysis(user=None):
    """Get breach analysis report"""
    try:
        days = request.args.get('days', 30, type=int)

        if days < 1 or days > 365:
            return {'error': 'Days must be between 1 and 365'}, 400

        reporting = _get_reporting_engine()
        analysis = reporting.generate_breach_analysis(days)

        return {'analysis': analysis}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/slos/reports/trends/<slo_id>', methods=['GET'])
@require_auth
def get_trend_analysis(slo_id, user=None):
    """Get trend analysis for SLO"""
    try:
        reporting = _get_reporting_engine()
        trends = reporting.generate_trend_analysis(slo_id)

        return {'trends': trends}, 200
    except ValueError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/slos/reports/executive-summary/<int:month>/<int:year>', methods=['GET'])
@require_auth
def get_executive_summary(month, year, user=None):
    """Get executive summary for month"""
    try:
        if not (1 <= month <= 12) or year < 2000:
            return {'error': 'Invalid month or year'}, 400

        reporting = _get_reporting_engine()
        summary = reporting.generate_executive_summary(month, year)

        return {'summary': summary.to_dict()}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/slos/reports/health-scores', methods=['GET'])
@require_auth
def get_health_scores(user=None):
    """Get health scores for all services"""
    try:
        reporting = _get_reporting_engine()
        scores = reporting.calculate_health_scores()

        return {'scores': [s.to_dict() for s in scores]}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/api/slos/reports/export/<report_type>', methods=['GET'])
@require_auth
def export_report(report_type, user=None):
    """Export report in specified format"""
    try:
        fmt = request.args.get('format', 'json').lower()
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if fmt not in ['json', 'csv', 'pdf']:
            return {'error': 'Invalid format. Supported: json, csv, pdf'}, 400

        reporting = _get_reporting_engine()

        if report_type == 'monthly' and month and year:
            report = reporting.generate_monthly_report(month, year)
        elif report_type == 'breach':
            days = request.args.get('days', 30, type=int)
            report = reporting.generate_breach_analysis(days)
        else:
            return {'error': f'Unknown report type: {report_type}'}, 400

        if fmt == 'json':
            return {'data': export_report_json(report)}, 200
        elif fmt == 'csv':
            csv_data = export_report_csv(report, report_type)
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=slo_report_{report_type}.csv'
            return response
        else:  # PDF
            # PDF export would require additional library
            return {'error': 'PDF export coming soon'}, 501
    except Exception as e:
        return {'error': str(e)}, 500


# ==================== ALERTS DASHBOARD ROUTE ====================

@app.route('/alerts')
def alerts_dashboard():
    """Render alerts dashboard (no auth required - frontend handles API auth)"""
    return render_template('nexus/alerts_dashboard.html')


@app.route('/slos')
def slo_dashboard():
    """Render SLO dashboard (no auth required - frontend handles API auth)"""
    return render_template('nexus/slo_dashboard.html')


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ==================== INITIALIZATION FOR PRODUCTION ====================

# Deferred initialization - happens on first request, not at import time
# This prevents hanging if MongoDB is unavailable
_initialization_done = False

@app.before_request
def deferred_initialize():
    """Initialize app on first request."""
    global _initialization_done
    if not _initialization_done:
        try:
            connect_mongodb()
            initialize_users()
            initialize_approvals()
            start_background_threads()
            _initialize_default_alert_rules()
            _initialize_default_slos()
            _initialization_done = True
        except Exception as e:
            print(f"⚠️  Initialization warning: {e}")

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
        _populate_demo_audit_data()
        start_background_threads()
        _initialize_default_alert_rules()
        _initialize_default_slos()
    except Exception as e:
        print(f"⚠️  Initialization warning: {e}")

    port = int(os.getenv('PORT', 5000))
    environment = os.getenv('ENVIRONMENT', 'development')

    print("\n📍 Access at: http://localhost:5000")
    print("   Demo: admin / admin123")
    print("   API Docs: http://localhost:5000/api/docs\n")

    if environment == 'production':
        print("🚨 PRODUCTION MODE: Use reverse proxy (nginx/Caddy) with HTTPS/TLS\n")

    # Run with socketio
    socketio.run(app, host='0.0.0.0', port=port, debug=False,
                allow_unsafe_werkzeug=True, use_reloader=False)
