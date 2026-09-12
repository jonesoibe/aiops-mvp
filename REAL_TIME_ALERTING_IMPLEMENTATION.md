# Real-Time Alerting System - Implementation Guide

## Complete Installation & Setup

---

## 🚀 Phase 1: Backend Integration (2 hours)

### Step 1: Add Dependencies to requirements.txt

```bash
# Already installed, but verify:
requests>=2.31.0  # For webhooks
smtplib  # Built-in (for email)
```

No additional dependencies needed! ✅

### Step 2: Initialize Alerting Engine in nexus_app.py

Add to top of nexus_app.py:

```python
from src.alerting_engine import AlertingEngine, AlertRule, AlertSeverity, AlertStatus
from src.notification_channels import get_notification_manager, SlackChannel, EmailChannel

# Initialize alerting engine
alerting_engine = AlertingEngine()

# Initialize notification manager
notification_manager = get_notification_manager()

# Inject notification manager into alerting engine
alerting_engine.notifier = notification_manager
```

### Step 3: Create Preset Alert Rules

Add to app initialization:

```python
def _initialize_default_alert_rules():
    """Create default alert rules on startup"""
    
    from src.alerting_engine import AlertRule, AlertSeverity
    
    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU exceeds 85% for 5 minutes",
            metric_name="cpu_usage",
            condition=">",
            threshold=85,
            duration=300,
            severity=AlertSeverity.MAJOR
        ),
        AlertRule(
            id="memory_high",
            name="High Memory Usage",
            description="Memory exceeds 80% for 5 minutes",
            metric_name="memory_usage",
            condition=">",
            threshold=80,
            duration=300,
            severity=AlertSeverity.MAJOR
        ),
        AlertRule(
            id="error_rate_high",
            name="High Error Rate",
            description="Error rate exceeds 5% for 2 minutes",
            metric_name="error_rate",
            condition=">",
            threshold=5,
            duration=120,
            severity=AlertSeverity.CRITICAL
        ),
        AlertRule(
            id="latency_high",
            name="High Response Latency",
            description="P95 latency exceeds 500ms for 3 minutes",
            metric_name="response_time_p95",
            condition=">",
            threshold=500,
            duration=180,
            severity=AlertSeverity.MAJOR
        )
    ]
    
    for rule in rules:
        alerting_engine.add_rule(rule)

# Call during app initialization
_initialize_default_alert_rules()
```

### Step 4: Metric Evaluation Loop

Add background task to evaluate metrics periodically:

```python
import threading
from datetime import datetime

def _alert_evaluation_thread():
    """Background thread that evaluates metrics for alerts"""
    while True:
        try:
            # Get current metrics for all services
            all_metrics = storage.get_all_metrics()
            
            for service_id, metrics in all_metrics.items():
                # Evaluate metrics against alert rules
                changed_alerts = alerting_engine.evaluate_metrics(
                    service_id,
                    metrics
                )
                
                # Emit WebSocket updates for changed alerts
                for alert in changed_alerts:
                    socketio.emit(
                        'alert:fired' if alert.status == AlertStatus.FIRING else 'alert:resolved',
                        alert.to_dict(),
                        namespace='/alerts'
                    )
            
            time.sleep(30)  # Evaluate every 30 seconds
        except Exception as e:
            logger.error(f"Error in alert evaluation: {e}")
            time.sleep(30)

# Start background thread
alert_thread = threading.Thread(target=_alert_evaluation_thread, daemon=True)
alert_thread.start()
```

---

## 🔌 Phase 2: API Endpoints (1.5 hours)

Add these routes to nexus_app.py:

```python
# ==================== ALERT RULES ====================

@app.route('/api/alerts/rules', methods=['GET'])
@require_auth
def get_alert_rules(user=None):
    """Get all alert rules"""
    rules = alerting_engine.get_rules()
    return jsonify({
        'rules': [asdict(r) for r in rules],
        'total': len(rules),
        'enabled': len(alerting_engine.get_rules(enabled_only=True))
    })


@app.route('/api/alerts/rules', methods=['POST'])
@require_auth
@audit_required('CREATE', 'alert_rule')
def create_alert_rule(user=None):
    """Create new alert rule"""
    data = request.get_json()
    
    try:
        rule = AlertRule(
            id=data.get('id') or f"rule_{datetime.utcnow().timestamp()}",
            name=data['name'],
            description=data.get('description', ''),
            metric_name=data['metric_name'],
            condition=data['condition'],
            threshold=float(data['threshold']),
            threshold_high=float(data.get('threshold_high', 0)) if data.get('threshold_high') else None,
            duration=int(data.get('duration', 300)),
            severity=AlertSeverity(data.get('severity', 'major')),
            notification_channels=data.get('notification_channels', ['slack', 'email'])
        )
        
        alerting_engine.add_rule(rule)
        
        return jsonify({
            'id': rule.id,
            'name': rule.name,
            'created_at': datetime.utcnow().isoformat()
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e}'}), 400


@app.route('/api/alerts/rules/<rule_id>', methods=['PUT'])
@require_auth
@audit_required('UPDATE', 'alert_rule')
def update_alert_rule(rule_id, user=None):
    """Update alert rule"""
    try:
        alerting_engine.update_rule(rule_id, **request.get_json())
        return jsonify({'status': 'updated', 'rule_id': rule_id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/alerts/rules/<rule_id>', methods=['DELETE'])
@require_auth
@audit_required('DELETE', 'alert_rule')
def delete_alert_rule(rule_id, user=None):
    """Delete alert rule"""
    alerting_engine.delete_rule(rule_id)
    return jsonify({'status': 'deleted', 'rule_id': rule_id})


# ==================== ACTIVE ALERTS ====================

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
        # Check historical
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


# ==================== ALERT ACTIONS ====================

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
@require_auth
@audit_required('ACKNOWLEDGE', 'alert')
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
@audit_required('RESOLVE', 'alert')
def resolve_alert(alert_id, user=None):
    """Manually resolve an alert"""
    data = request.get_json()
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
    data = request.get_json()
    duration = data.get('duration_minutes', 30)
    
    alert = alerting_engine.silence_alert(alert_id, duration)
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    return jsonify(alert.to_dict())


# ==================== ALERT STATISTICS ====================

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
        }
    ]
    
    return jsonify({'templates': templates})


# ==================== WEBSOCKET ====================

@socketio.on('connect', namespace='/alerts')
def alert_connect():
    """Handle WebSocket connection for alerts"""
    logger.info(f"Client connected to alerts namespace")

@socketio.on('disconnect', namespace='/alerts')
def alert_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected from alerts namespace")
```

---

## 🎨 Phase 3: Frontend Dashboard (2 hours)

Create `templates/nexus/alerts.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Alerts - AIOps</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div class="alerts-dashboard">
        <!-- Alert Statistics -->
        <div class="stats-row">
            <div class="stat-card critical">
                <div class="stat-value" id="critical-count">0</div>
                <div class="stat-label">Critical Alerts</div>
            </div>
            <div class="stat-card major">
                <div class="stat-value" id="major-count">0</div>
                <div class="stat-label">Major Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-count">0</div>
                <div class="stat-label">Total Active</div>
            </div>
        </div>

        <!-- Alert Rules -->
        <div class="section">
            <h2>Alert Rules</h2>
            <button class="btn-primary" onclick="openCreateRuleModal()">+ Create Rule</button>
            <table class="rules-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Metric</th>
                        <th>Condition</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="rules-tbody">
                </tbody>
            </table>
        </div>

        <!-- Active Alerts -->
        <div class="section">
            <h2>Active Alerts</h2>
            <div class="filters">
                <select id="status-filter" onchange="filterAlerts()">
                    <option value="">All Statuses</option>
                    <option value="firing">Firing</option>
                    <option value="acknowledged">Acknowledged</option>
                </select>
            </div>
            <table class="alerts-table">
                <thead>
                    <tr>
                        <th>Rule</th>
                        <th>Service</th>
                        <th>Current Value</th>
                        <th>Threshold</th>
                        <th>Duration</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="alerts-tbody">
                </tbody>
            </table>
        </div>
    </div>

    <style>
        .alerts-dashboard {
            padding: 20px;
        }

        .stats-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 8px;
            color: white;
        }

        .stat-card.critical {
            background: linear-gradient(135deg, #ff4757 0%, #ee5a6f 100%);
        }

        .stat-card.major {
            background: linear-gradient(135deg, #ff9f43 0%, #ffa502 100%);
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
        }

        .stat-label {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
        }

        .section {
            margin-bottom: 30px;
        }

        .rules-table, .alerts-table {
            width: 100%;
            border-collapse: collapse;
        }

        tbody tr:hover {
            background-color: rgba(255,255,255,0.05);
        }

        td, th {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .btn-action {
            padding: 6px 12px;
            margin-right: 5px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .btn-acknowledge {
            background: #2ecc71;
            color: white;
        }

        .btn-resolve {
            background: #3498db;
            color: white;
        }
    </style>

    <script>
        // Connect to WebSocket for real-time updates
        const socket = io('/alerts', {
            auth: {
                token: localStorage.getItem('token')
            }
        });

        // Listen for new alerts
        socket.on('alert:fired', (alert) => {
            console.log('New alert:', alert);
            loadAlerts();
            showNotification(`🚨 ${alert.rule_name} on ${alert.service_id}`);
        });

        socket.on('alert:resolved', (alert) => {
            console.log('Alert resolved:', alert);
            loadAlerts();
            showNotification(`✅ ${alert.rule_name} resolved`);
        });

        // Load data on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadRules();
            loadAlerts();
            setInterval(loadAlerts, 30000);  // Refresh every 30 seconds
        });

        async function loadRules() {
            const response = await fetch('/api/alerts/rules', {
                headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
            });
            const data = await response.json();

            const tbody = document.getElementById('rules-tbody');
            tbody.innerHTML = '';

            for (const rule of data.rules) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${rule.name}</td>
                    <td>${rule.metric_name}</td>
                    <td>${rule.condition} ${rule.threshold}</td>
                    <td><span class="badge ${rule.severity}">${rule.severity}</span></td>
                    <td>${rule.enabled ? '✓ Enabled' : '✗ Disabled'}</td>
                    <td>
                        <button class="btn-action" onclick="editRule('${rule.id}')">Edit</button>
                        <button class="btn-action" onclick="deleteRule('${rule.id}')">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            }
        }

        async function loadAlerts() {
            const status = document.getElementById('status-filter').value;
            const url = `/api/alerts${status ? `?status=${status}` : ''}`;
            
            const response = await fetch(url, {
                headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
            });
            const data = await response.json();

            // Update stats
            document.getElementById('critical-count').textContent = data.alerts.filter(a => a.severity === 'critical').length;
            document.getElementById('major-count').textContent = data.alerts.filter(a => a.severity === 'major').length;
            document.getElementById('total-count').textContent = data.total;

            // Update table
            const tbody = document.getElementById('alerts-tbody');
            tbody.innerHTML = '';

            for (const alert of data.alerts) {
                const tr = document.createElement('tr');
                const duration = Math.floor(alert.duration_seconds / 60);
                tr.innerHTML = `
                    <td>${alert.rule_name}</td>
                    <td>${alert.service_id}</td>
                    <td>${alert.current_value.toFixed(2)}</td>
                    <td>${alert.threshold.toFixed(2)}</td>
                    <td>${duration} min</td>
                    <td><span class="badge ${alert.status}">${alert.status}</span></td>
                    <td>
                        ${alert.status === 'firing' ? 
                            `<button class="btn-action btn-acknowledge" onclick="acknowledgeAlert('${alert.id}')">Acknowledge</button>` :
                            ''
                        }
                        <button class="btn-action btn-resolve" onclick="resolveAlert('${alert.id}')">Resolve</button>
                    </td>
                `;
                tbody.appendChild(tr);
            }
        }

        async function acknowledgeAlert(alertId) {
            await fetch(`/api/alerts/${alertId}/acknowledge`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({user_id: 'current_user'})
            });
            loadAlerts();
        }

        async function resolveAlert(alertId) {
            const reason = prompt('Resolution reason:');
            if (reason) {
                await fetch(`/api/alerts/${alertId}/resolve`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({reason})
                });
                loadAlerts();
            }
        }

        function filterAlerts() {
            loadAlerts();
        }

        function showNotification(message) {
            // Browser notification
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('AIOps Alert', {body: message});
            }
        }
    </script>
</body>
</html>
```

---

## 📋 Configuration

### Environment Variables (.env)

```bash
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAILS=admin@company.com,team@company.com

# Custom Webhook
WEBHOOK_URL=https://your-endpoint.com/alerts
```

---

## ✅ Testing

### 1. Create an alert rule
```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CPU Alert",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 80
  }'
```

### 2. Trigger metrics
Ensure metrics are being collected and exceed thresholds

### 3. Check alerts
```bash
curl http://localhost:5000/api/alerts \
  -H "Authorization: Bearer test"
```

### 4. Acknowledge alert
```bash
curl -X POST http://localhost:5000/api/alerts/ALERT_ID/acknowledge \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "john"}'
```

---

## 🎯 Next Steps

1. ✅ Deploy changes to GitHub
2. ✅ Test Slack integration
3. ✅ Configure email notifications
4. ✅ Add to sidebar navigation
5. ✅ Create dashboard widget

---

**Implementation Status:** Ready to deploy  
**Estimated Time:** 5-6 hours total  
**Complexity:** Medium  
**Impact:** HIGH - Transforms platform from visibility-only to actionable
