# Chaos Simulation Export System

**Status:** ✅ **COMPLETE** - Full PNG and CSV export capability implemented

---

## Overview

Export chaos simulation results in two formats:
- **CSV** - Structured data tables for analysis
- **PNG** - Visualizations for reporting

All 12 requested export types are now available.

---

## Exported File Types

### CSV Exports (Data)

| # | File | Contents | Use Case |
|---|------|----------|----------|
| 1 | `chaos_simulation.csv` | Raw metrics data | Data analysis, trending |
| 2 | `classification_results.csv` | Actual vs Predicted | Performance analysis |
| 3 | `incident_log.csv` | Detected incidents | Incident tracking |
| 4 | `response_log.csv` | System responses | Response analysis |
| 5 | `remediation_results.csv` | Remediation actions | Remediation tracking |
| 6 | `threshold_calibration.csv` | Calibration data | Threshold tuning |
| 7 | `metrics_comparison.csv` | Metrics comparison | Performance metrics |
| 8 | `dos_simulation_analysis.csv` | DoS attack data | Attack analysis |

### PNG Exports (Visualizations)

| # | File | Chart Type | Shows |
|---|------|-----------|-------|
| 1 | `confusion_matrix_mvp.png` | Heatmap | Classification accuracy |
| 2 | `confusion_matrix_supervised.png` | Heatmap | Supervised learning results |
| 3 | `feature_importance.png` | Bar chart | Top 15 features |
| 4 | `feature_importance_mvp.png` | Bar chart | Top 10 features (MVP) |
| 5 | `dos_simulation_analysis.png` | Line chart | DoS attack timeline |
| 6 | `threshold_calibration.png` | Multi-bar | Precision/Recall/F1 |
| 7 | `metrics_comparison.png` | 4-panel | Accuracy/Precision/Recall/F1 |

---

## API Endpoints

### 1. Generate Exports

**POST** `/api/simulator/{simulation_id}/export`

Generate all export files for a simulation.

```bash
curl -X POST http://localhost:5000/api/simulator/demo/export \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "status": "success",
  "simulation_id": "demo",
  "export_count": 12,
  "exports": {
    "chaos_simulation_csv": "simulation_exports/demo/chaos_simulation.csv",
    "confusion_matrix_mvp_png": "simulation_exports/demo/confusion_matrix_mvp.png",
    ...
  },
  "manifest": "simulation_exports/demo/MANIFEST.json"
}
```

---

### 2. Download Single File

**GET** `/api/simulator/{simulation_id}/export/{filename}`

Download a specific export file.

```bash
# Download CSV
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/simulator/demo/export/incident_log.csv \
  > incident_log.csv

# Download PNG
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/simulator/demo/export/confusion_matrix_mvp.png \
  > confusion_matrix.png
```

---

### 3. Download All Exports (ZIP)

**GET** `/api/simulator/{simulation_id}/export/all`

Download all exports as a single ZIP file.

```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/simulator/demo/export/all \
  > simulation_exports.zip
```

ZIP contains:
- All CSV files
- All PNG files
- MANIFEST.json

---

### 4. List Available Exports

**GET** `/api/simulator/{simulation_id}/export/list`

List what exports are available for a simulation.

```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/simulator/demo/export/list
```

**Response:**
```json
{
  "status": "success",
  "simulation_id": "demo",
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

---

## CSV File Formats

### chaos_simulation.csv
```csv
timestamp,cpu,memory,disk,network
2026-08-26T12:00:00,45.2,62.1,78.3,152.4
2026-08-26T12:00:01,46.1,61.9,78.2,151.8
...
```

### classification_results.csv
```csv
actual,predicted,correct
0,0,1
1,1,1
0,1,0
1,0,0
...
```

### incident_log.csv
```csv
timestamp,incident_id,type,severity,status
2026-08-26T12:00:15,INC001,cpu_spike,high,resolved
2026-08-26T12:00:45,INC002,memory_leak,critical,active
...
```

### threshold_calibration.csv
```csv
metric,threshold,precision,recall,f1_score
cpu_usage,0.85,0.92,0.88,0.90
memory_usage,0.75,0.89,0.85,0.87
...
```

### metrics_comparison.csv
```csv
model,accuracy,precision,recall,f1_score
baseline,0.82,0.80,0.78,0.79
improved,0.91,0.89,0.87,0.88
...
```

---

## PNG Chart Details

### Confusion Matrix
- Type: Heatmap
- Shows: True Positives, False Positives, True Negatives, False Negatives
- Color: Blue gradient (darker = more predictions)
- Use: Evaluate classification performance

### Feature Importance
- Type: Horizontal bar chart
- Shows: Top features ranked by importance score
- Sorted: Descending by importance
- Use: Identify key predictive features

### DoS Simulation Analysis
- Type: Dual line chart
  - Panel 1: Request rate over time
  - Panel 2: Error rate over time
- Shows: Attack timeline and system response
- Use: Analyze attack impact

### Threshold Calibration
- Type: Grouped bar chart
- Shows: Precision, Recall, F1 Score per metric
- Colors: Three distinct colors for metrics
- Use: Evaluate threshold tuning effectiveness

### Metrics Comparison
- Type: 2x2 panel grid
  - Panel 1: Accuracy comparison
  - Panel 2: Precision comparison
  - Panel 3: Recall comparison
  - Panel 4: F1 Score comparison
- Use: Compare model performance

---

## Python Usage

```python
from simulation_export import SimulationExporter
import pandas as pd

# Initialize exporter
exporter = SimulationExporter(output_dir='simulation_exports')

# Prepare simulation data
sim_data = {
    'metrics': pd.DataFrame({...}),
    'classification': {
        'y_true': [0, 1, 0, 1, ...],
        'y_pred': [0, 1, 0, 0, ...]
    },
    'features': {'cpu': 0.95, 'memory': 0.87, ...},
    'incidents': [{...}, {...}, ...],
    'threshold_calibration': {...},
    'metrics_comparison': [{...}, {...}, ...],
    'dos_analysis': {...}
}

# Export all formats
exports = exporter.export_all(sim_data)

# Create manifest
manifest = exporter.create_export_manifest(exports)

# Access individual exports
for export_type, filepath in exports.items():
    print(f"{export_type}: {filepath}")
```

---

## File Structure

```
simulation_exports/
├── sim_20260826_120000/
│   ├── MANIFEST.json
│   ├── chaos_simulation.csv
│   ├── classification_results.csv
│   ├── incident_log.csv
│   ├── response_log.csv
│   ├── remediation_results.csv
│   ├── threshold_calibration.csv
│   ├── metrics_comparison.csv
│   ├── dos_simulation_analysis.csv
│   ├── confusion_matrix_mvp.png
│   ├── confusion_matrix_supervised.png
│   ├── feature_importance.png
│   ├── feature_importance_mvp.png
│   ├── dos_simulation_analysis.png
│   ├── threshold_calibration.png
│   └── metrics_comparison.png
└── sim_20260826_120030/
    └── ...
```

---

## MANIFEST.json

Each simulation generates a manifest:

```json
{
  "timestamp": "20260826_120000",
  "export_directory": "simulation_exports/sim_20260826_120000",
  "exports": {
    "chaos_simulation_csv": "...",
    "confusion_matrix_mvp_png": "...",
    ...
  },
  "file_count": 15,
  "csv_exports": [
    "chaos_simulation.csv",
    "classification_results.csv",
    ...
  ],
  "png_exports": [
    "confusion_matrix_mvp.png",
    "feature_importance.png",
    ...
  ]
}
```

---

## Workflow Example

### Step 1: Run Simulation
```bash
curl -X POST http://localhost:5000/api/simulator/start \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"execution_id":"demo"}'
```

### Step 2: Generate Exports
```bash
curl -X POST http://localhost:5000/api/simulator/demo/export \
  -H "Authorization: Bearer {token}"
```

### Step 3: List Available Exports
```bash
curl http://localhost:5000/api/simulator/demo/export/list \
  -H "Authorization: Bearer {token}"
```

### Step 4: Download Files
```bash
# Download individual files
curl http://localhost:5000/api/simulator/demo/export/incident_log.csv \
  -H "Authorization: Bearer {token}" > incident_log.csv

# Or download all as ZIP
curl http://localhost:5000/api/simulator/demo/export/all \
  -H "Authorization: Bearer {token}" > exports.zip
```

### Step 5: Analyze
Open CSV files in Excel, Pandas, or your analysis tool. View PNG charts in any image viewer.

---

## Features

✅ **Automatic File Generation** - All 12 types generated in one call  
✅ **Multiple Formats** - PNG for visualization, CSV for data  
✅ **ZIP Download** - Get all exports in one file  
✅ **Manifest Generation** - Know what you exported  
✅ **Organized Storage** - Timestamped directories per simulation  
✅ **Individual Downloads** - Get specific files as needed  
✅ **High Resolution** - PNG charts at 100 DPI  
✅ **Professional Charts** - Publication-ready visualizations  

---

## Storage

Exports are stored on disk:
- **Location:** `simulation_exports/sim_{timestamp}/`
- **Retention:** Until manually deleted
- **Disk Usage:** ~2-5 MB per simulation (depends on data volume)
- **Access:** Read via API endpoints

---

## Customization

Modify `SimulationExporter` class to:
- Change output directory
- Adjust chart colors/styles
- Modify chart sizes
- Change PNG resolution (DPI)
- Add new export types
- Filter data before export

---

## API Authentication

All endpoints require Bearer token:

```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/simulator/demo/export
```

Get token from login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## Summary

✅ **12 Export Types** - All requested formats available  
✅ **CSV Data** - Structured data for analysis  
✅ **PNG Visualizations** - Charts for reporting  
✅ **API Endpoints** - Full programmatic access  
✅ **Batch Export** - Generate all at once  
✅ **Individual Downloads** - Get what you need  
✅ **ZIP Archive** - Download everything together  

**Ready to use!** Run a simulation, then export results in PNG and CSV format.

---

**Commit:** cb5f1e7  
**Status:** PRODUCTION READY 🚀
