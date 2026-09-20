"""
WebSocket Integration Code for Machine Analyzer
Add this to nexus_app.py after socketio initialization

Location in nexus_app.py: After "app = Flask(...)" and before app.run()
"""

# ==================== ADD THESE IMPORTS ====================
# Add to the top of nexus_app.py after existing imports:

from machine_analyzer_routes import bp as machine_analyzer_bp
from machine_analyzer import analyzer


# ==================== REGISTER BLUEPRINT ====================
# Add after app creation (around line 100 in nexus_app.py):

# Register Machine Analyzer Blueprint
app.register_blueprint(machine_analyzer_bp)


# ==================== WEBSOCKET HANDLERS ====================
# Add after socketio initialization (around line 200-300):

@socketio.on('connect', namespace='/ws/machine-analyzer')
def handle_analyzer_connect():
    """Handle WebSocket connection for machine analyzer"""
    print('[SOCKETIO] Client connected to /ws/machine-analyzer')

    # Send connection confirmation
    emit('connected', {
        'message': 'Connected to Machine Analyzer',
        'status': 'ready'
    })

    # Register callback for analyzer updates
    def send_update(data):
        """Send analyzer updates to connected client"""
        try:
            emit('data_update', data, broadcast=False)
        except Exception as e:
            print(f'[ERROR] Failed to emit update: {e}')

    analyzer.register_callback(send_update)
    print('[SOCKETIO] Analyzer callback registered')


@socketio.on('disconnect', namespace='/ws/machine-analyzer')
def handle_analyzer_disconnect():
    """Handle WebSocket disconnection for machine analyzer"""
    print('[SOCKETIO] Client disconnected from /ws/machine-analyzer')

    # Stop any running analysis
    if analyzer.is_running:
        analyzer.reset()
        print('[ANALYZER] Analysis stopped due to disconnect')


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


# ==================== COMPLETE EXAMPLE ====================
"""
Complete integration in nexus_app.py:

```python
# At the top with other imports:
import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# ... existing imports ...

# ADD THESE:
from machine_analyzer_routes import bp as machine_analyzer_bp
from machine_analyzer import analyzer

# Create app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Setup SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# ... existing app configuration ...

# ADD THIS AFTER APP CREATION:
# Register Machine Analyzer Blueprint
app.register_blueprint(machine_analyzer_bp)

# ... existing routes and blueprints ...

# ADD THIS AFTER EXISTING SOCKETIO HANDLERS:
@socketio.on('connect', namespace='/ws/machine-analyzer')
def handle_analyzer_connect():
    """Handle WebSocket connection for machine analyzer"""
    print('[SOCKETIO] Client connected to /ws/machine-analyzer')

    emit('connected', {
        'message': 'Connected to Machine Analyzer',
        'status': 'ready'
    })

    def send_update(data):
        try:
            emit('data_update', data, broadcast=False)
        except Exception as e:
            print(f'[ERROR] Failed to emit update: {e}')

    analyzer.register_callback(send_update)


@socketio.on('disconnect', namespace='/ws/machine-analyzer')
def handle_analyzer_disconnect():
    """Handle WebSocket disconnection"""
    print('[SOCKETIO] Client disconnected from /ws/machine-analyzer')

    if analyzer.is_running:
        analyzer.reset()


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


# At the very end of nexus_app.py:
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,  # Important: prevents multiple analyzer instances
        ssl_context=ssl_context if ENVIRONMENT == 'development' else None
    )
```
"""


# ==================== TROUBLESHOOTING CHECKLIST ====================
"""
1. Imports added to nexus_app.py?
   - from machine_analyzer_routes import bp as machine_analyzer_bp
   - from machine_analyzer import analyzer

2. Blueprint registered?
   - app.register_blueprint(machine_analyzer_bp)

3. WebSocket handlers added?
   - handle_analyzer_connect()
   - handle_analyzer_disconnect()
   - handle_status_request()

4. Flask-SocketIO configured?
   - socketio = SocketIO(app, cors_allowed_origins="*")
   - use_reloader=False in socketio.run()

5. Required files in place?
   - machine_analyzer.py
   - machine_analyzer_routes.py
   - templates/nexus/machine_analyzer.html

6. SMD data available?
   - /data/raw/smd/machine-*.txt exists

7. Restart Flask app?
   - python nexus_app.py

8. Test connection?
   - Open http://localhost:5000/machine-analyzer/page
   - Browser console should show: "Connected to Machine Analyzer"
"""
