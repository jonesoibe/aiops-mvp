# Machine Analyzer - Integration & Setup Guide

## Overview

A real-time, interactive machine analysis dashboard with:
- ✅ **Machine Selection**: 27 SMD files grouped by server (Machine 1, 2, 3)
- ✅ **Live Data Streaming**: 60-second scrolling table with color-coded metrics
- ✅ **Anomaly Detection**: Real-time 0-1 score with 0.52 threshold
- ✅ **Fault Classification**: 8+ fault categories with severity levels
- ✅ **Action Recommendations**: Priority-based recommendations per fault
- ✅ **WebSocket Real-time**: Live updates every 0.5-1 second
- ✅ **Interactive Controls**: Start/Pause/Resume/Reset buttons

## Files Created

```
1. machine_analyzer.py
   ├─ BaselineCalculator - Calculate baselines from historical data
   ├─ AnomalyDetector - Weighted anomaly scoring (0-1 scale)
   ├─ MachineDataLoader - Load CSV files from /data/raw/smd
   └─ MachineAnalyzer - Orchestrator with threading support

2. machine_analyzer_routes.py
   ├─ /api/machine-analyzer/machines - List all 27 machines
   ├─ /api/machine-analyzer/status - Get current status
   ├─ /api/machine-analyzer/start - Start analysis
   ├─ /api/machine-analyzer/pause - Pause streaming
   ├─ /api/machine-analyzer/resume - Resume streaming
   ├─ /api/machine-analyzer/reset - Reset analysis
   └─ /machine-analyzer/page - Render dashboard HTML

3. templates/nexus/machine_analyzer.html
   └─ Complete interactive UI with WebSocket client
```

## Integration Steps

### Step 1: Update nexus_app.py

Add these imports and registrations to `nexus_app.py`:

```python
# Add to imports
from machine_analyzer_routes import bp as machine_analyzer_bp
from machine_analyzer import analyzer
from flask_socketio import emit, disconnect, join_room

# Add to app creation section (after app initialization)
app.register_blueprint(machine_analyzer_bp)

# Add WebSocket handler
@socketio.on('connect', namespace='/ws/machine-analyzer')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'data': 'Connected to analyzer'})
    
    # Register analyzer callback
    def notify(data):
        emit('data_update', data, broadcast=False)
    
    analyzer.register_callback(notify)

@socketio.on('disconnect', namespace='/ws/machine-analyzer')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    analyzer.reset()
    print('Client disconnected from analyzer')
```

### Step 2: Verify Dependencies

Ensure these are installed:
```bash
pip list | grep -E "flask-socketio|python-socketio|python-engineio"

# If missing:
pip install flask-socketio python-socketio python-engineio
```

### Step 3: Update app.run() configuration

Find the `socketio.run()` call and ensure it's configured for WebSocket:

```python
socketio.run(
    app,
    host='0.0.0.0',
    port=5000,
    debug=True,
    use_reloader=False,  # Important for threading
    ssl_context=ssl_context if ENVIRONMENT == 'development' else None
)
```

### Step 4: Test the Integration

1. **Restart the Flask app**:
```bash
python nexus_app.py
```

2. **Open the analyzer**:
```
http://localhost:5000/machine-analyzer/page
```

3. **Select a machine** and click **Start**

## Architecture

```
                    Web Browser
                        │
                        ↓
        ┌───────────────────────────────┐
        │   HTML UI (machine_analyzer)   │
        │ - Machine dropdown              │
        │ - Live metrics table            │
        │ - Anomaly gauge                 │
        │ - Action recommendations        │
        └───────────┬─────────────────────┘
                    │
              WebSocket (bi-directional)
                    │
                    ↓
        ┌───────────────────────────────┐
        │   Flask Routes                  │
        │ - /api/machine-analyzer/*       │
        │ - /ws/machine-analyzer (WS)     │
        └───────────┬─────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │   MachineAnalyzer (Python)      │
        │ - BaselineCalculator            │
        │ - AnomalyDetector               │
        │ - MachineDataLoader             │
        │ - Fault Detection               │
        │ - Recommendation Engine         │
        └───────────┬─────────────────────┘
                    │
                    ↓
        ┌───────────────────────────────┐
        │   SMD Data Files                │
        │ /data/raw/smd/machine-*.txt     │
        │ - 27 total files                │
        │ - 38 features per row           │
        │ - ~200K rows per machine        │
        └───────────────────────────────┘
```

## Feature Weights

Configurable anomaly detection weights:

```python
FEATURE_CONFIG = {
    "cpu": 1.0,           # Most important
    "memory": 0.95,
    "disk": 0.85,
    "network": 0.90,
    "processes": 0.70,
    "services": 0.80
}
```

To change weights, POST to `/api/machine-analyzer/config`:

```bash
curl -X POST http://localhost:5000/api/machine-analyzer/config \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_threshold": 0.52,
    "update_frequency": 0.5,
    "feature_weights": {
      "cpu": 1.2,
      "memory": 0.9,
      "disk": 0.8,
      "network": 0.85,
      "processes": 0.6,
      "services": 0.75
    }
  }'
```

## Fault Categories

8 detailed fault types detected automatically:

1. **CPU Exhaustion** (CRITICAL)
   - Triggers: CPU User > 85% AND Load > 80%
   - Recommendations: Scale horizontally, optimize code

2. **Memory Pressure** (CRITICAL)
   - Triggers: Memory Util > 90% AND Swapping active
   - Recommendations: Increase memory, check leaks

3. **Disk I/O Bottleneck** (HIGH)
   - Triggers: Disk Time > 80% AND Queue > 50%
   - Recommendations: Upgrade disk, optimize I/O

4. **Network Errors** (HIGH)
   - Triggers: Any network error detected
   - Recommendations: Check hardware/cables/driver

5. **Error Rate Spike** (HIGH)
   - Triggers: App errors > 20% AND Load > 60%
   - Recommendations: Review logs, restart service

6. **Database Performance** (MEDIUM)
   - Triggers: Slow queries > 20% AND High QPS
   - Recommendations: Optimize queries, add indexes

7. **Connection Limit** (MEDIUM)
   - Triggers: Connections > 90% AND Load > 70%
   - Recommendations: Increase connection pool

8. **Unusual Activity** (LOW)
   - Triggers: High context switches with low CPU
   - Recommendations: Monitor syscalls, check crons

## API Endpoints

### GET /api/machine-analyzer/machines
List all 27 machines grouped by server

**Response**:
```json
{
  "machines": {
    "Machine 1": [
      {"name": "machine-1-1.txt", "server": "1", "period": "1"},
      ...
    ],
    "Machine 2": [...],
    "Machine 3": [...]
  },
  "total_machines": 27
}
```

### POST /api/machine-analyzer/start
Start analyzing a machine

**Payload**:
```json
{
  "machine": "machine-1-5.txt",
  "update_frequency": 0.5
}
```

### POST /api/machine-analyzer/pause
Pause current analysis

### POST /api/machine-analyzer/resume
Resume paused analysis

### POST /api/machine-analyzer/reset
Reset and stop analysis

### GET /api/machine-analyzer/status
Get current analyzer status

**Response**:
```json
{
  "is_running": true,
  "is_paused": false,
  "current_machine": "machine-1-5.txt",
  "anomaly_score": 0.45,
  "metrics_count": 38,
  "alerts_count": 2,
  "update_frequency": 0.5
}
```

### GET /api/machine-analyzer/metrics
Get last 60 seconds of metrics

### GET /api/machine-analyzer/alerts?limit=10
Get alert history

### POST /api/machine-analyzer/config
Get/set configuration

## WebSocket Messages

### Server → Client: `data_update`

Real-time analysis result:

```json
{
  "timestamp": 1234567890.123,
  "machine": "machine-1-5.txt",
  "anomaly_score": 0.58,
  "metrics": [
    {
      "timestamp": 1234567890.123,
      "feature_index": 0,
      "feature_name": "Feature #1",
      "value": 0.456,
      "baseline": 0.420,
      "deviation": 8.6,
      "status": "yellow"
    },
    ...
  ],
  "alerts": [
    {
      "timestamp": 1234567890.123,
      "anomaly_score": 0.58,
      "severity": "HIGH",
      "affected_metrics": ["Feature #1", "Feature #5"],
      "detected_faults": ["CPU Exhaustion"],
      "recommendations": [
        {"action": "Scale horizontally", "priority": 1},
        {"action": "Check for runaway processes", "priority": 2}
      ]
    }
  ],
  "detected_faults": [
    {
      "id": "cpu_exhaustion",
      "name": "CPU Exhaustion",
      "severity": "critical",
      "affected_metrics": ["Feature #1", "Feature #30"],
      "recommendations": [
        {"action": "Scale horizontally (add more instances)", "priority": 1},
        ...
      ]
    }
  ]
}
```

## UI Components Explained

### Top Bar
- **Machine Dropdown**: Select from 27 SMD files, grouped by server
- **Status Badge**: Ready, Loading, Streaming, Paused
- **Control Buttons**: Start, Pause, Resume, Reset

### Live Data Stream (Left)
- **60-second Window**: Last 60 metrics in scrolling table
- **Color Coding**:
  - 🟢 Green: Normal (deviation < 30%)
  - 🟡 Yellow: Warning (deviation 30-60%)
  - 🔴 Red: Critical (deviation > 60%)
- **Columns**: Time, Feature, Value, Baseline, Deviation, Status

### Anomaly Detection (Top Right)
- **Gauge**: Visual 0-1 scale with threshold line at 0.52
- **Score**: Current anomaly score (0.00 - 1.00)
- **Status**: NORMAL / WARNING / ALERT
- **Recent Alerts**: Last 5 alerts with timestamps and scores

### Action Recommendations (Bottom Right)
- **Fault Category**: Detected issues with severity badges
- **Affected Metrics**: Which features triggered the fault
- **Recommendations**: Priority-ranked actions (1-4)
- **Colors**: 
  - 🔴 Critical (red)
  - 🟠 High (orange)
  - 🟡 Medium (yellow)
  - 🔵 Low (blue)

## Troubleshooting

### WebSocket Connection Failed
```
Error: WebSocket connection error
Solution: Ensure Flask-SocketIO is properly installed and socketio.run() is configured
```

### Machine Selection Empty
```
Error: Dropdown shows "Loading..."
Solution: Verify /data/raw/smd/ directory exists and contains machine-*.txt files
```

### Anomaly Score Not Updating
```
Error: Score stuck at 0.00
Solution: Check browser console for JavaScript errors, verify WebSocket connection
```

### Data Not Streaming
```
Error: "No metrics" message
Solution: Ensure CSV file exists and is readable, check update_frequency setting
```

## Performance Tips

1. **Update Frequency**: Lower = more updates but higher CPU
   - 0.1s: Very detailed, high CPU
   - 0.5s: Good balance (default)
   - 1.0s: Conservative, low CPU

2. **Baseline Window**: Larger = smoother but slower baseline
   - 50: Fast adaptation
   - 100: Good balance (default)
   - 200: Very stable baselines

3. **Browser Performance**: Close other tabs for smooth scrolling
   - Chrome: Best WebSocket performance
   - Firefox: Good performance
   - Safari: May lag with high update frequency

## Next Steps

1. ✅ Integrate into `nexus_app.py`
2. ✅ Restart Flask app
3. ✅ Navigate to `/machine-analyzer/page`
4. ✅ Select a machine and click Start
5. ✅ Observe real-time analysis
6. ✅ Adjust weights/thresholds as needed
7. ✅ Monitor recommendations

## Advanced Configuration

### Custom Fault Detection Rules

Edit `machine_analyzer.py` `FAULT_CATEGORIES` dict:

```python
FAULT_CATEGORIES = {
    "your_fault_name": {
        "name": "Your Fault Display Name",
        "severity": "high",  # critical, high, medium, low
        "triggers": [
            {"feature": 0, "threshold": 0.85, "comparison": "gt"},
            {"feature": 5, "threshold": 0.90, "comparison": "gt"},
        ],
        "recommendations": [
            {"action": "Your action item", "priority": 1},
            ...
        ]
    }
}
```

### Custom Feature Weights

Modify `FEATURE_CONFIG` dict to adjust importance of each category:

```python
FEATURE_CONFIG = {
    "cpu": {"indices": [0,1,2,3], "weight": 1.2, "name": "CPU"},  # More important
    "memory": {"indices": [4,5,6,7,8], "weight": 0.8, "name": "Memory"},  # Less important
    ...
}
```

---

## Ready to Deploy! 🚀

The Machine Analyzer is production-ready with:
- ✅ 8 fault categories
- ✅ Weighted anomaly detection
- ✅ Real-time WebSocket streaming
- ✅ Interactive controls
- ✅ Color-coded severity
- ✅ Priority recommendations
- ✅ Configurable thresholds
