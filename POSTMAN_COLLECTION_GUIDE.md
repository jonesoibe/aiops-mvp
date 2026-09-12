# AIOPS API - Postman Collection Guide

**Complete collection with all endpoints, request bodies, and authentication**

---

## Quick Start

### 1. Import Collection
- Open Postman
- Click **Import** → **Link**
- Paste collection URL or upload `AIOPS_API_Postman_Collection.json`
- Collection loads with all requests

### 2. Setup Variables
In **Postman Variables**:
- `base_url` = `http://localhost:5000`
- `auth_token` = (auto-fill after login)
- `simulation_id` = (from simulation response)

### 3. First Request
1. Run **Authentication > Login**
2. Token auto-saves to `{{auth_token}}`
3. All subsequent requests use this token

---

## API Endpoints Included

### Authentication
```
POST /api/auth/login
```
**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGc...",
  "user": "admin"
}
```

---

### Real Metrics API

#### Get All Metrics
```
GET /api/metrics/all
```
Returns 18 metrics with current values, status, and units

**Response Sample:**
```json
{
  "cpu_usage": {
    "value": 45.2,
    "unit": "%",
    "status": "healthy",
    "timestamp": "2026-08-29T16:30:00"
  },
  "memory_usage": {
    "value": 62.1,
    "unit": "%",
    "status": "warning",
    "timestamp": "2026-08-29T16:30:00"
  },
  ...
}
```

#### Get Metrics Summary
```
GET /api/metrics/summary
```

**Response:**
```json
{
  "total_metrics": 18,
  "healthy_count": 10,
  "warning_count": 5,
  "critical_count": 3,
  "healthy_percentage": 55.6,
  "timestamp": "2026-08-29T16:30:00"
}
```

#### Get Single Metric
```
GET /api/metrics/{{metric_name}}?minutes=60
```

**Query Parameters:**
- `minutes`: Time window for history (default: 60)

**Response:**
```json
{
  "current": {
    "name": "cpu_usage",
    "value": 45.2,
    "unit": "%",
    "status": "healthy"
  },
  "history": [
    {"timestamp": "...", "value": 42.1},
    {"timestamp": "...", "value": 44.5},
    ...
  ]
}
```

#### Get Metrics by Status
```
GET /api/metrics/status/{{status}}
```

**Status Values:** `healthy`, `warning`, `critical`

#### Get Current Anomalies
```
GET /api/metrics/anomalies
```

**Response:**
```json
{
  "cpu_spike": false,
  "memory_leak": true,
  "network_latency": false,
  "high_error_rate": false
}
```

#### Trigger Anomaly
```
POST /api/metrics/anomalies/trigger
```

**Request Body:**
```json
{
  "anomaly_type": "memory_leak",
  "duration": 30
}
```

**Anomaly Types:**
- `cpu_spike` - CPU usage spikes
- `memory_leak` - Memory gradually increases
- `network_latency` - Response time increases
- `high_error_rate` - Error rate increases

#### Export Prometheus Format
```
GET /api/metrics/export/prometheus
```

Returns metrics in Prometheus text format

---

### Chaos Simulator

#### Start Simulation
```
POST /api/simulator/start
```

**Request Body:**
```json
{
  "execution_id": "sim_001",
  "config": {
    "chaos_type": "memory_leak",
    "duration": 60
  }
}
```

**Response:**
```json
{
  "status": "started",
  "simulation_id": "sim_001"
}
```

#### Get Simulation Status
```
GET /api/simulator/{{simulation_id}}/status
```

**Response:**
```json
{
  "simulation_id": "sim_001",
  "status": "running",
  "started": "2026-08-29T16:30:00",
  "result": null
}
```

**Status Values:** `running`, `completed`, `failed`

#### Get Simulation Result
```
GET /api/simulator/{{simulation_id}}/result
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "sim_001",
  "results": {
    "metrics": {
      "anomalies_count": 12,
      "detection_rate": 0.92,
      "processing_time_ms": 1250.5
    },
    "analysis": {
      "feature_mean": 45.23,
      "threshold": 0.65
    },
    "anomalies": [...]
  }
}
```

---

### Simulation Exports

#### Generate All Exports
```
POST /api/simulator/{{simulation_id}}/export
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "success",
  "simulation_id": "sim_001",
  "export_count": 15,
  "exports": {
    "chaos_simulation_csv": "simulation_exports/sim_001/chaos_simulation.csv",
    "confusion_matrix_mvp_png": "simulation_exports/sim_001/confusion_matrix_mvp.png",
    ...
  },
  "manifest": "simulation_exports/sim_001/MANIFEST.json"
}
```

#### List Available Exports
```
GET /api/simulator/{{simulation_id}}/export/list
```

**Response:**
```json
{
  "status": "success",
  "simulation_id": "sim_001",
  "total_files": 15,
  "exports": {
    "csv_files": [
      "chaos_simulation.csv",
      "classification_results.csv",
      ...
    ],
    "png_files": [
      "confusion_matrix_mvp.png",
      "feature_importance.png",
      ...
    ],
    "manifest": "MANIFEST.json"
  }
}
```

#### Download Single Export
```
GET /api/simulator/{{simulation_id}}/export/{{filename}}
```

**Filename Examples:**
- `incident_log.csv`
- `confusion_matrix_mvp.png`
- `dos_simulation_analysis.csv`
- `threshold_calibration.png`

#### Download All Exports (ZIP)
```
GET /api/simulator/{{simulation_id}}/export/all
```

Returns ZIP file with all 15 files

---

## Common Workflows

### Workflow 1: Full Simulation Test
```
1. POST /api/simulator/start
   - Copy simulation_id from response
   - Set {{simulation_id}} variable

2. GET /api/simulator/{{simulation_id}}/status
   - Poll until status = "completed"

3. GET /api/simulator/{{simulation_id}}/result
   - View complete results

4. POST /api/simulator/{{simulation_id}}/export
   - Generate exports

5. GET /api/simulator/{{simulation_id}}/export/list
   - See available files

6. GET /api/simulator/{{simulation_id}}/export/{{filename}}
   - Download individual files
```

### Workflow 2: Monitor Real Metrics
```
1. GET /api/metrics/summary
   - Check overall health

2. GET /api/metrics/all
   - Get all metric values

3. GET /api/metrics/status/critical
   - Find critical metrics

4. POST /api/metrics/anomalies/trigger
   - Inject anomaly to test

5. GET /api/metrics/anomalies
   - Verify anomaly is active

6. GET /api/metrics/all
   - Watch metrics respond
```

### Workflow 3: Anomaly Testing
```
1. POST /api/metrics/anomalies/trigger
   - Type: "memory_leak"
   - Duration: 30 seconds

2. GET /api/metrics/anomalies
   - Verify active

3. GET /api/metrics/all
   - Watch memory spike

4. (Wait 30 seconds)

5. GET /api/metrics/anomalies
   - Verify cleared

6. GET /api/metrics/all
   - Memory returns to normal
```

---

## Export File Types

### CSV Files (8)
- `chaos_simulation.csv` - Raw metrics data
- `classification_results.csv` - Classification accuracy
- `incident_log.csv` - Detected incidents
- `response_log.csv` - System responses
- `remediation_results.csv` - Remediation actions
- `threshold_calibration.csv` - Calibration statistics
- `metrics_comparison.csv` - Model performance
- `dos_simulation_analysis.csv` - DoS attack data

### PNG Charts (7)
- `confusion_matrix_mvp.png` - Classification heatmap
- `confusion_matrix_supervised.png` - Supervised results
- `feature_importance.png` - Top 15 features
- `feature_importance_mvp.png` - Top 10 features
- `dos_simulation_analysis.png` - Attack timeline
- `threshold_calibration.png` - Precision/Recall/F1
- `metrics_comparison.png` - Performance grid

---

## Authentication

All endpoints except dashboard pages require Bearer token:

```
Authorization: Bearer {{auth_token}}
```

Token obtained from:
```
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

---

## Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `base_url` | API base URL | `http://localhost:5000` |
| `auth_token` | JWT authentication token | `eyJhbGc...` |
| `simulation_id` | Current simulation ID | `sim_001` |

---

## Request Headers

### Standard Headers
```
Content-Type: application/json
Authorization: Bearer {{auth_token}}
```

### Example Full Request
```bash
curl -X GET http://localhost:5000/api/metrics/all \
  -H "Authorization: Bearer {{auth_token}}" \
  -H "Content-Type: application/json"
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 202 | Accepted (async operation) |
| 400 | Bad request |
| 401 | Unauthorized (invalid/missing token) |
| 404 | Not found |
| 500 | Server error |

---

## Tips & Tricks

### Auto-Token Capture
After login request, add script to auto-save token:
```javascript
if (pm.response.code === 200) {
  pm.environment.set("auth_token", pm.response.json().token);
}
```

### Simulate Multiple Anomalies
Use Collection Runner to trigger multiple anomalies:
1. Create request copies with different anomaly types
2. Use Runner to execute all
3. Monitor metrics in parallel

### Export Batch Download
Instead of downloading individually:
1. Use `export/all` endpoint
2. Get complete ZIP
3. Extract all files at once

### Monitor Anomaly Progress
Chain requests in Postman flows:
```
1. POST trigger anomaly
2. Wait (variable timer)
3. GET anomaly status
4. GET metrics affected
5. Repeat until clear
```

---

## API Response Times

| Endpoint | Typical Time |
|----------|--------------|
| `/api/metrics/all` | 100-200ms |
| `/api/metrics/summary` | 50-100ms |
| `/api/simulator/start` | 50ms |
| `/api/simulator/status` | 20-50ms |
| `/api/export/generate` | 2-5 seconds |
| `/api/export/all` (ZIP) | 3-8 seconds |

---

## Troubleshooting

### 401 Unauthorized
- Check `{{auth_token}}` is set
- Re-run login request
- Verify token hasn't expired

### 404 Not Found
- Check simulation ID exists
- Verify export files were generated
- Confirm endpoint path

### Exports Not Generated
- Ensure simulation completed
- Check simulation has results
- POST export endpoint first

### Slow Response
- Check server load
- Monitor network tab
- Review server logs

---

## Collection Structure

```
AIOPS API Collection
├── Authentication
│   └── Login
├── Real Metrics API
│   ├── Get All Metrics
│   ├── Get Metrics Summary
│   ├── Get Single Metric
│   ├── Get Metrics by Status
│   ├── Get Anomalies
│   ├── Trigger Anomaly
│   └── Export Prometheus Format
├── Chaos Simulator
│   ├── Start Simulation
│   ├── Get Simulation Status
│   └── Get Simulation Result
├── Simulation Exports
│   ├── Generate All Exports
│   ├── List Available Exports
│   ├── Download Single Export
│   └── Download All Exports (ZIP)
└── Dashboard
    ├── Overview Page
    └── Simulator Page
```

---

## Using Collection in Code

### JavaScript/Node.js
```javascript
const token = "{{auth_token}}";
const response = await fetch('http://localhost:5000/api/metrics/all', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const metrics = await response.json();
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/metrics/all', headers=headers)
metrics = response.json()
```

### cURL
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/metrics/all
```

---

**Ready to use! Import the collection and start testing.** 🚀

Last updated: August 29, 2026
