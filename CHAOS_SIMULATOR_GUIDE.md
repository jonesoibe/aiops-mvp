# ⚡ Chaos Injection Simulator - Complete Guide

## Overview

**Nexus AIOps Chaos Injection Simulator** is a browser-based chaos engineering platform that executes the entire AIOps pipeline in real-time with live output streaming. It brings **Jupyter Notebook-level interactivity** to the web browser for data science and chaos engineering workflows.

---

## 🎯 What You Get

### Browser-Based Python Execution
- Run chaos injection scenarios directly in the browser
- No Jupyter needed—everything happens in your web app
- Real-time output streaming via WebSocket
- Granular execution visibility at each pipeline stage

### Complete AIOps Pipeline
The simulator executes all 5 stages of the ML/AI operations pipeline:

1. **Chaos Generation** - Fault injection into simulated services
2. **Preprocessing** - Feature engineering & normalization
3. **Anomaly Detection** - Isolation Forest model training
4. **Issue Classification** - Root cause identification
5. **Visualization** - Chart generation & analysis

---

## 🚀 How to Use

### Access the Simulator

1. **Navigate to:** http://localhost:5000 (or your Render deployment)
2. **Login with:**
   - Username: `admin`
   - Password: `admin123`
3. **Click sidebar:** "Chaos Simulator" (⚡ icon)
4. **Or direct URL:** `/simulator`

### Configure & Run

#### Left Panel: Configuration
```
🎛️ Configuration
├─ Metrics to Generate: 10-500 data points
├─ Noise Level: 0.0-1.0 (Gaussian noise)
└─ Random Seed: 0-9999 (for reproducibility)
```

**Example configs:**
- **Quick Demo:** 50 metrics, 0.1 noise
- **Detailed Analysis:** 200 metrics, 0.15 noise
- **Stress Test:** 500 metrics, 0.05 noise

#### Start Simulation
Click "⚡ Start Simulation" button to begin

---

## 📊 What Happens During Execution

### Real-Time Console (Middle Panel)
Watch live execution with color-coded output:

```
[14:30:22] INFO  🚀 Starting Chaos Injection Simulation...
[14:30:22] DEBUG    • Metrics: 50
[14:30:22] DEBUG    • Noise level: 0.10
[14:30:22] DEBUG    • Services: ['service_a', 'service_b', 'service_c']
[14:30:23] INFO  📊 Generating chaos-injected metrics...
[14:30:23] DEBUG    • Injecting memory_leak into service_a...
[14:30:24] SUCCESS ✅ Generated 50 metric samples from 3 services
[14:30:24] INFO  📝 Preprocessed 50 samples with 9 features
[14:30:25] INFO  🔍 Detecting anomalies...
[14:30:25] DEBUG    • Training Isolation Forest...
[14:30:26] SUCCESS ✅ Detected 5 anomalies (threshold: 0.7321)
[14:30:26] INFO  🏷️ Classifying issues...
[14:30:27] SUCCESS ✅ Classified 4 issues
[14:30:27] INFO  📈 Generating visualizations...
[14:30:28] SUCCESS ✅ Simulation completed successfully!
```

**Color Coding:**
- 🔵 **INFO** (Cyan) - General information
- 🟢 **SUCCESS** (Green) - Successful operations
- 🟡 **WARNING** (Orange) - Warnings
- 🔴 **ERROR** (Red/Pink) - Errors
- ⚫ **DEBUG** (Gray) - Debug details

### Execution Pipeline Tracker (Right Panel)

Each stage shows:
- ✅ **Status:** PENDING → RUNNING → COMPLETED/FAILED
- 📊 **Details:** Stage-specific metrics (e.g., anomalies found)
- ⏱️ **Real-time updates:** Status changes as pipeline progresses

**Pipeline Stages:**
```
📊 Chaos Generation
   ├─ Status: Completed
   └─ Services simulated: 3

🔧 Preprocessing
   ├─ Status: Completed
   └─ Features engineered: 9

🔍 Anomaly Detection
   ├─ Status: Completed
   └─ Anomalies found: 5

🏷️ Issue Classification
   ├─ Status: Completed
   └─ Issues classified: 4

📈 Visualization
   ├─ Status: Completed
   └─ Charts generated: 3
```

---

## 📈 Results & Outputs

### Generated Charts (Embedded in Browser)

#### 1. Time Series with Anomalies
- Line chart of all service metrics over time
- Red X markers showing detected anomalies
- Shows correlation and timing patterns

#### 2. Anomaly Score Distribution
- Histogram of Isolation Forest scores
- Red threshold line for anomaly cutoff
- Visual representation of score distribution

#### 3. Service Correlation Heatmap
- Service metrics correlation matrix
- Color scale: -1.0 (inverse) → 0 (uncorrelated) → 1.0 (perfect)
- Identifies relationships between services

### Classified Issues Table

| Type | Confidence | Timestamp |
|------|-----------|-----------|
| Memory Leak | 85% | T_24 |
| High Latency | 90% | T_18 |
| Error Spike | 75% | T_31 |
| ... | ... | ... |

---

## 🔧 Technical Architecture

### Backend Components

#### `chaos_executor.py` (New)
```python
class ChaosExecutor:
    """Execute chaos simulations with output capture and streaming"""
    
    Methods:
    ├─ run_simulation(config) → Execute full pipeline
    ├─ _chaos_generation() → Inject faults
    ├─ _preprocess_data() → Feature engineering
    ├─ _anomaly_detection() → Isolation Forest
    ├─ _issue_classification() → Root cause inference
    ├─ _generate_visualizations() → Chart generation
    └─ _emit_* → WebSocket streaming functions
```

#### Flask Routes (nexus_app.py)
```python
POST   /api/simulator/start          # Start simulation
GET    /api/simulator/<id>/status    # Get progress
GET    /api/simulator/<id>/result    # Get results
GET    /simulator                    # Simulator UI page
```

#### WebSocket Events
```python
simulation_event   # General event wrapper
├─ simulation_output    # Console output
├─ simulation_step      # Stage updates
├─ simulation_chart     # Chart images (base64)
└─ simulation_data      # Data tables (JSON)
```

### Frontend (simulator.html)

**Three-Column Layout:**

1. **Left (350px):** Configuration panel + status info
2. **Middle (1fr):** Console output + live logs
3. **Right (1fr):** Pipeline stages + execution status

**Bottom Section:** Results grid (2x2)
- Charts displayed as PNG images
- Data tables with scrollable content

---

## 📊 Chaos Injection Details

### Service A: Memory Leak
```
Fault Type: Gradual Memory Increase
Pattern: Linear growth (10MB per time step)
Duration: 15 time units
Start Time: T=20

Timeline:
T=20: 0 MB additional
T=21: 10 MB additional
T=22: 20 MB additional
...
T=35: 150 MB additional
T=36+: Plateau
```

### Service B: High Latency
```
Fault Type: Latency Spike
Pattern: Sudden spike with gradual recovery
Duration: 20 time units
Start Time: T=15

Timeline:
T=15: Spike begins (5x baseline)
T=16-30: Gradual recovery
T=31+: Back to baseline
```

### Service C: Error Spike
```
Fault Type: Increased Error Rate
Pattern: Sudden error rate jump
Duration: 18 time units
Start Time: T=18

Timeline:
T=18: Error rate jumps (10x baseline)
T=19-28: Sustained high rate
T=29+: Recovery
```

---

## 🎓 Execution Flow

```
User clicks "Start Simulation"
          ↓
┌─────────────────────────────────┐
│ Step 1: Chaos Generation        │
├─────────────────────────────────┤
│ • Generate healthy baseline      │
│ • Inject memory leak (Service A) │
│ • Inject latency spike (Service B)│
│ • Inject error spike (Service C) │
│ • Output: 50 metric samples      │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│ Step 2: Preprocessing           │
├─────────────────────────────────┤
│ • Feature engineering           │
│ • Normalization with scaling    │
│ • Output: 50 samples × 9 features│
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│ Step 3: Anomaly Detection       │
├─────────────────────────────────┤
│ • Train Isolation Forest        │
│ • Score all observations        │
│ • Calibrate threshold           │
│ • Output: Anomaly scores + mask │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│ Step 4: Classification          │
├─────────────────────────────────┤
│ • Analyze anomaly patterns      │
│ • Infer issue types             │
│ • Calculate confidence scores   │
│ • Output: Classified issues     │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│ Step 5: Visualization           │
├─────────────────────────────────┤
│ • Time series chart             │
│ • Score distribution histogram  │
│ • Correlation heatmap           │
│ • Output: PNG images (base64)   │
└─────────────────────────────────┘
          ↓
    Results Displayed ✅
```

---

## 💾 Data Flow

### Input → Processing → Output

```
Configuration
├─ num_metrics: 50
├─ noise_level: 0.1
└─ random_seed: 42
          ↓
    [Chaos Generation]
          ↓
DataFrame (50 × 3)
  Columns: service_a, service_b, service_c
  + Fault log with timestamps
          ↓
    [Preprocessing]
          ↓
DataFrame (50 × 9)
  Features: Min, Max, Mean, Std, etc.
  Normalized to μ=0, σ=1
          ↓
    [Anomaly Detection]
          ↓
Anomaly Scores Array (50,)
  Values: 0.0 - 1.0
  Threshold: 0.732 (90th percentile)
          ↓
    [Classification]
          ↓
Issues List
  [{type, confidence, timestamp}, ...]
          ↓
    [Visualization]
          ↓
Charts + Tables
  └─ PNG images (base64 encoded)
```

---

## 🔌 API Reference

### Start Simulation
```bash
POST /api/simulator/start
Content-Type: application/json
Authorization: Bearer <token>

{
  "execution_id": "sim_20240801_143022",
  "num_metrics": 50,
  "noise_level": 0.1
}

Response (202 Accepted):
{
  "status": "started",
  "simulation_id": "sim_20240801_143022"
}
```

### Check Status
```bash
GET /api/simulator/sim_20240801_143022/status
Authorization: Bearer <token>

Response:
{
  "simulation_id": "sim_20240801_143022",
  "status": "running",  # or "completed", "failed"
  "started": "2024-08-01T14:30:22.123Z",
  "result": null  # Populated when completed
}
```

### Get Results
```bash
GET /api/simulator/sim_20240801_143022/result
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "execution_id": "sim_20240801_143022",
  "results": {
    "metrics": [...],
    "preprocessed": [...],
    "scores": [...],
    "anomalies": [...],
    "classified_issues": [...]
  },
  "outputs": [...]
}
```

---

## 📱 WebSocket Events

### Connect & Join Room
```javascript
// Automatically joins when you navigate to simulator
socket.emit('join_simulation', {
  simulation_id: 'sim_20240801_143022'
});
```

### Console Output
```javascript
socket.on('simulation_output', (data) => {
  // {
  //   timestamp: "2024-08-01T14:30:22.123Z",
  //   message: "🚀 Starting...",
  //   level: "info",
  //   execution_id: "sim_..."
  // }
});
```

### Step Updates
```javascript
socket.on('simulation_step', (data) => {
  // {
  //   timestamp: "...",
  //   step: "chaos_generation",
  //   status: "completed",  # or "running", "failed"
  //   details: {
  //     services_simulated: 3,
  //     anomalies_found: 5
  //   }
  // }
});
```

### Chart Images
```javascript
socket.on('simulation_chart', (data) => {
  // {
  //   timestamp: "...",
  //   chart_name: "Time_Series_With_Anomalies",
  //   image: "data:image/png;base64,...",
  //   execution_id: "sim_..."
  // }
});
```

### Data Tables
```javascript
socket.on('simulation_data', (data) => {
  // {
  //   timestamp: "...",
  //   data: {
  //     name: "Raw_Metrics",
  //     shape: [50, 3],
  //     columns: ["service_a", "service_b", "service_c"],
  //     head: [{...}, {...}, ...],  # First 10 rows
  //     dtypes: {...},
  //     stats: {...}  # Summary statistics
  //   }
  // }
});
```

---

## 🧪 Testing

### Quick Test
```bash
# 1. Navigate to http://localhost:5000/simulator
# 2. Click "⚡ Start Simulation" (uses default config)
# 3. Watch console for real-time output
# 4. Wait for all 5 stages to complete (~10 seconds)
# 5. View generated charts and tables
```

### Custom Configuration
```
1. Adjust "Metrics to Generate": 100
2. Adjust "Noise Level": 0.2 (drag slider)
3. Set "Random Seed": 12345
4. Click "⚡ Start Simulation"
```

### Error Handling
If simulation fails:
1. Check browser console for errors
2. Review Flask server logs
3. Verify MongoDB connection (if configured)
4. Check network connectivity

---

## 📦 Deployment to Render

### After Deployment
```bash
# 1. Go to https://dashboard.render.com
# 2. Trigger redeploy (automatic or manual)
# 3. Wait 3-5 minutes for deployment
# 4. Navigate to https://aiops-mvp.onrender.com/simulator
# 5. Login with admin/admin123
# 6. Run simulation (works exactly same as local)
```

### WebSocket Support on Render
- Already configured with Flask-SocketIO
- Works with both Python server and Gunicorn + eventlet
- No additional configuration needed

---

## 🎯 Key Features

✅ **Jupyter-Like Interactivity** - Run Python code in browser  
✅ **Real-Time Streaming** - WebSocket output as it executes  
✅ **Multi-Stage Pipeline** - All 5 AIOps stages visible  
✅ **Visual Feedback** - Charts, tables, and progress tracking  
✅ **Production Ready** - Non-blocking async execution  
✅ **No Downloads** - Everything stays in browser  
✅ **Reproducible** - Random seed for consistent results  
✅ **Customizable** - Adjust parameters on the fly  

---

## 🔮 Future Enhancements

Possible additions:
- [ ] Save/load simulation configs
- [ ] Compare multiple simulations side-by-side
- [ ] Export results (JSON, CSV, PDF)
- [ ] Custom fault injection patterns
- [ ] Real incident data injection
- [ ] Performance benchmarking
- [ ] Model performance metrics
- [ ] Hyperparameter tuning interface

---

## 📝 Code Structure

```
aiops-mvp/
├── chaos_executor.py           # Simulation engine
├── nexus_app.py                # Flask routes + WebSocket
├── templates/nexus/
│   └── simulator.html          # UI (3-column layout)
├── src/
│   ├── chaos_simulator.py      # Chaos injection
│   ├── preprocess.py           # Feature engineering
│   ├── detect.py               # Anomaly detection
│   ├── classify.py             # Issue classification
│   └── ...
└── ...
```

---

**Created:** 2026-08-25  
**Latest Commit:** `0f5fe6e - Feature: Add Chaos Injection Simulator`  
**Status:** ✅ Production Ready

