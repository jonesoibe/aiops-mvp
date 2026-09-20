# Machine Analyzer - Quick Start Guide

## 🚀 Installation (5 minutes)

### Step 1: Copy Files to Project
All files are already created in your project root:
```
✓ machine_analyzer.py
✓ machine_analyzer_routes.py
✓ templates/nexus/machine_analyzer.html
✓ MACHINE_ANALYZER_INTEGRATION.md
✓ WEBSOCKET_INTEGRATION_CODE.py
```

### Step 2: Update nexus_app.py

Find these locations in `nexus_app.py`:

**Location 1: Imports (top of file)**
```python
# Add after existing imports:
from machine_analyzer_routes import bp as machine_analyzer_bp
from machine_analyzer import analyzer
```

**Location 2: App Registration (after Flask app creation)**
```python
# Add after app = Flask(...) and other setup:
app.register_blueprint(machine_analyzer_bp)
```

**Location 3: WebSocket Handlers (after existing socketio handlers)**
```python
@socketio.on('connect', namespace='/ws/machine-analyzer')
def handle_analyzer_connect():
    print('[SOCKETIO] Machine Analyzer connected')
    emit('connected', {'status': 'ready'})
    
    def send_update(data):
        try:
            emit('data_update', data, broadcast=False)
        except Exception as e:
            print(f'[ERROR] {e}')
    
    analyzer.register_callback(send_update)

@socketio.on('disconnect', namespace='/ws/machine-analyzer')
def handle_analyzer_disconnect():
    print('[SOCKETIO] Machine Analyzer disconnected')
    if analyzer.is_running:
        analyzer.reset()
```

See `WEBSOCKET_INTEGRATION_CODE.py` for complete example.

### Step 3: Restart Flask App
```bash
python nexus_app.py
```

Expected output:
```
* Running on https://0.0.0.0:5000
* Machine Analyzer initialized
```

### Step 4: Open Dashboard
```
http://localhost:5000/machine-analyzer/page
```

## 📊 Using the Machine Analyzer

### Select a Machine
1. Click the **dropdown** in the top-left
2. Choose from **Machine 1**, **Machine 2**, or **Machine 3**
3. Each group contains 4-9 time periods

### Start Analysis
1. Click the **[Start]** button
2. Status badge changes to **"STREAMING"** (green)
3. Live data appears in the table

### Monitor Metrics
**Live Data Stream (Left side)**
- Shows last 38 metrics (one row at a time)
- Color coded:
  - 🟢 **Green**: Normal (deviation < 30%)
  - 🟡 **Yellow**: Warning (30-60% deviation)
  - 🔴 **Red**: Critical (> 60% deviation)

### Watch Anomaly Score (Top Right)
- **Gauge**: Visual 0-1 scale
- **Orange line**: Threshold at 0.52
- **Status badge**:
  - ✓ NORMAL (< 0.3)
  - ⚠ WARNING (0.3-0.52)
  - 🚨 ALERT (> 0.52)

### Review Alerts & Recommendations (Bottom Right)
- **Recent Alerts**: Last 5 anomalies with timestamps
- **Fault Detection**: Automatically detected issues
- **Priority Actions**: Ranked recommendations (1-4)

### Control Playback
- **[Pause]**: Stop streaming temporarily
- **[Resume]**: Continue from where paused
- **[Reset]**: Stop and clear all data

## 🎯 Example Workflow

### Scenario: Analyzing Machine-1-5.txt

1. **Select**: Machine 1 → machine-1-5.txt
2. **Start**: Click [Start] button
3. **Observe**: 
   - CPU values ranging 10-75%
   - Memory stable around 60-70%
   - Anomaly score usually 0.2-0.4 (normal)
4. **If alert triggers**:
   - Score jumps above 0.52 (red)
   - Fault detected (e.g., "CPU Exhaustion")
   - Recommendations appear with priority
5. **Take action**:
   - Review recommended actions
   - Understand which features triggered it

### Example Alert Output

```
🔴 CRITICAL - CPU Exhaustion
Affected: Feature #1 (CPU User), Feature #30 (Load Avg)

Recommended Actions:
1. Scale horizontally (add more instances)
2. Check for runaway processes
3. Optimize application code
```

## 🔧 Configuration

### Change Anomaly Threshold
Default is 0.52. To change:

```bash
curl -X POST http://localhost:5000/api/machine-analyzer/config \
  -H "Content-Type: application/json" \
  -d '{"anomaly_threshold": 0.60}'
```

### Adjust Update Frequency
Default is 0.5 seconds. Options: 0.1 (fast), 0.5 (normal), 1.0 (slow)

When starting analysis:
```javascript
// In browser console or HTML:
fetch('/api/machine-analyzer/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    machine: 'machine-1-5.txt',
    update_frequency: 0.2  // Faster updates
  })
})
```

### Custom Feature Weights
Edit `machine_analyzer.py`, update `FEATURE_CONFIG`:

```python
FEATURE_CONFIG = {
    "cpu": {"indices": [0,1,2,3], "weight": 1.2, "name": "CPU"},       # More important
    "memory": {"indices": [4,5,6,7,8], "weight": 0.8, "name": "Memory"}, # Less important
    "disk": {"indices": [9,10,11,12,13,14,15,16,17], "weight": 0.85, "name": "Disk I/O"},
    # ... more categories
}
```

## 📈 Understanding the Data

### 38 SMD Features

The dashboard analyzes all 38 features from the Server Machine Dataset:

```
CPU Metrics:        Features 1-4    (Utilization, Wait I/O, Interrupts)
Memory:             Features 5-9    (Usage, Swap, Cache, Shared)
Disk I/O:           Features 10-18  (Reads, Writes, Queue, Latency)
Network:            Features 19-24  (Bytes, Packets, Errors)
Processes:          Features 25-30  (Counts, Load Average)
Services:           Features 31-38  (Apache, MySQL, SSH, FTP, Cron)
```

See `SMD_DATASET_EXPLAINED.md` for detailed feature descriptions.

## 🐛 Troubleshooting

### "Connection Failed" Error
**Problem**: Browser can't connect to WebSocket
```
WebSocket connection to 'ws://localhost:5000/ws/machine-analyzer' failed
```

**Solution**:
1. Ensure Flask app is running: `python nexus_app.py`
2. Check browser console (F12)
3. Verify imports in nexus_app.py
4. Restart Flask app with `use_reloader=False`

### Dropdown Shows "Loading..."
**Problem**: Machine selector not populating

**Solution**:
1. Check `/data/raw/smd/` directory exists
2. Verify machine-*.txt files are present
3. Check browser network tab for 404 on `/api/machine-analyzer/machines`

### No Data in Live Table
**Problem**: Table stays empty after clicking Start

**Solution**:
1. Check machine file path is correct
2. Check CSV is readable (try opening in text editor)
3. Check browser console for JavaScript errors
4. Try a different machine file

### Anomaly Score Stuck at 0.00
**Problem**: Gauge never updates

**Solution**:
1. Check WebSocket connection (F12 → Network → WS)
2. Verify `handle_analyzer_connect()` in nexus_app.py
3. Check Flask logs for errors
4. Try different browser or private window

## 📊 API Reference

### Start Analysis
```bash
curl -X POST http://localhost:5000/api/machine-analyzer/start \
  -H "Content-Type: application/json" \
  -d '{"machine": "machine-1-5.txt", "update_frequency": 0.5}'
```

### Get Current Status
```bash
curl http://localhost:5000/api/machine-analyzer/status
```

### Get Recent Metrics
```bash
curl http://localhost:5000/api/machine-analyzer/metrics
```

### Get Alerts
```bash
curl http://localhost:5000/api/machine-analyzer/alerts?limit=10
```

### Pause/Resume/Reset
```bash
curl -X POST http://localhost:5000/api/machine-analyzer/pause
curl -X POST http://localhost:5000/api/machine-analyzer/resume
curl -X POST http://localhost:5000/api/machine-analyzer/reset
```

## 📝 Fault Categories

| Fault | Severity | Triggers | Recommendations |
|-------|----------|----------|-----------------|
| CPU Exhaustion | CRITICAL | CPU > 85% + Load > 80% | Scale, optimize code |
| Memory Pressure | CRITICAL | Memory > 90% + Swapping | Increase RAM, check leaks |
| Disk Bottleneck | HIGH | Disk Time > 80% + Queue > 50% | Upgrade disk, optimize I/O |
| Network Errors | HIGH | Any errors detected | Check hardware/cables |
| Error Rate Spike | HIGH | Errors > 20% + Load > 60% | Review logs, restart |
| DB Performance | MEDIUM | Slow queries > 20% | Optimize queries, add indexes |
| Connection Limit | MEDIUM | Connections > 90% + Load > 70% | Increase pool, implement pooling |
| Unusual Activity | LOW | High syscalls + Low CPU | Monitor, check crons |

## 🎓 Learning More

- **Detailed Feature Guide**: `SMD_DATASET_EXPLAINED.md`
- **Integration Details**: `MACHINE_ANALYZER_INTEGRATION.md`
- **Code Examples**: `WEBSOCKET_INTEGRATION_CODE.py`
- **Comparison Guide**: `MACHINE_COMPARISON_GUIDE.md`

## 💡 Pro Tips

1. **Start with baseline**: Analyze a quiet period first to establish baseline
2. **Watch correlations**: See how CPU and memory move together
3. **Test fault detection**: Manually choose anomalies and see recommendations
4. **Compare machines**: Switch between machines to spot differences
5. **Use pause feature**: Pause to examine specific moment in detail
6. **Check recommendations**: Review all 8 fault types during analysis

## 🚀 Next Steps

1. ✅ Copy all files to project
2. ✅ Update nexus_app.py with WebSocket handlers
3. ✅ Restart Flask app
4. ✅ Open http://localhost:5000/machine-analyzer/page
5. ✅ Select a machine and click Start
6. ✅ Monitor real-time analysis
7. ✅ Review recommendations
8. ✅ Experiment with different machines

## 📞 Support

For issues or questions:
1. Check `MACHINE_ANALYZER_INTEGRATION.md` (detailed guide)
2. Check Flask logs: `python nexus_app.py` output
3. Check browser console: F12 → Console tab
4. Check network tab: F12 → Network → WS

---

**Machine Analyzer Ready!** 🎉

Your interactive real-time machine analysis dashboard is now available at:
```
http://localhost:5000/machine-analyzer/page
```
