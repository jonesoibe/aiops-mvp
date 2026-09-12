# ==================== ALERTS INTEGRATION FOR nexus_app.py ====================
# Add these imports at the top of nexus_app.py

from src.alerting_engine import (
    AlertingEngine, AlertRule, AlertSeverity, AlertStatus, Alert
)
from src.notification_channels import (
    get_notification_manager, SlackChannel, EmailChannel
)
import threading
import time
from dataclasses import asdict

# ==================== INITIALIZATION ====================
# Add after app creation (around line 100)

# Initialize alerting engine
alerting_engine = AlertingEngine()

# Initialize notification manager
notification_manager = get_notification_manager()

# Inject notification manager into alerting engine
alerting_engine.notifier = notification_manager


def _initialize_default_alert_rules():
    """Create default alert rules on startup"""

    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU exceeds 85% for 5 minutes",
            metric_name="cpu_usage",
            condition=">",
            threshold=85.0,
            duration=300,
            severity=AlertSeverity.MAJOR,
            notification_channels=['slack', 'email', 'console']
        ),
        AlertRule(
            id="memory_high",
            name="High Memory Usage",
            description="Memory exceeds 80% for 5 minutes",
            metric_name="memory_usage",
            condition=">",
            threshold=80.0,
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

    logger.info(f"Initialized {len(rules)} default alert rules")


def _alert_evaluation_thread():
    """Background thread that continuously evaluates metrics for alerts"""
    logger.info("Starting alert evaluation thread")

    while True:
        try:
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
                    logger.info(f"Emitted {event_name} event: {alert.rule_name}")

            time.sleep(30)  # Evaluate every 30 seconds
        except Exception as e:
            logger.error(f"Error in alert evaluation thread: {e}", exc_info=True)
            time.sleep(30)


# Start alert evaluation thread (add in app.route('/') or similar startup location)
def start_alert_thread():
    """Start the alert evaluation background thread"""
    alert_thread = threading.Thread(target=_alert_evaluation_thread, daemon=True)
    alert_thread.start()
    logger.info("Alert evaluation thread started")


# ==================== API ENDPOINTS ====================
# Add these routes to nexus_app.py

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
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {e}'}), 400


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


# ==================== WEBSOCKET HANDLERS ====================
# Add these socket handlers

@socketio.on('connect', namespace='/alerts')
def alert_connect(auth):
    """Handle WebSocket connection for alerts"""
    try:
        # Verify token
        if auth and 'token' in auth:
            token = auth['token']
            # Token validation would happen here
        logger.info(f"Client connected to alerts namespace")
    except Exception as e:
        logger.error(f"Error in alert_connect: {e}")


@socketio.on('disconnect', namespace='/alerts')
def alert_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected from alerts namespace")


@socketio.on('get_active_alerts', namespace='/alerts')
def get_active_alerts():
    """Send active alerts to client"""
    alerts = alerting_engine.get_active_alerts()
    return [a.to_dict() for a in alerts]


# ==================== INITIALIZATION CALL ====================
# Add this at the end of the file, in the app initialization section

if __name__ == '__main__':
    _initialize_default_alert_rules()
    start_alert_thread()
    socketio.run(app, debug=os.getenv('FLASK_ENV') == 'development', port=5000)
