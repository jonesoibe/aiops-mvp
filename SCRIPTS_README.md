# AIOps MVP - Regeneration Scripts

This directory contains scripts to run and regenerate AIOps MVP outputs and visualizations.

## Quick Start

### 1. Run Full Pipeline
Execute the complete data processing pipeline end-to-end:

```bash
python run_full_pipeline.py
```

**What it does:**
- Loads data from `data/raw/data.csv` (or generates synthetic data)
- Performs feature engineering
- Detects anomalies using Isolation Forest
- Classifies incidents into categories
- Generates detection statistics
- Saves results to `data/processed/`

**Options:**
```bash
python run_full_pipeline.py --data custom_data.csv --output results/
```

---

### 2. Run Chaos Simulation
Inject controlled faults into simulated services and generate visualizations:

```bash
python run_chaos_simulation.py
```

**What it does:**
- Simulates 3 services (SERVICE_A, SERVICE_B, SERVICE_C)
- Injects 53 fault events over 5 minutes
- Detects anomalies in real-time
- Classifies incidents by type
- Analyzes correlations between faults
- Generates 2 visualization files:
  - `chaos_simulation.png` - Fault timeline and anomaly detection
  - `dos_simulation_analysis.png` - Correlation matrix and incident heatmap

**Options:**
```bash
# Custom duration (600 seconds)
python run_chaos_simulation.py --duration 600

# Custom services
python run_chaos_simulation.py --services SERVICE_A SERVICE_B

# Enable correlated faults
python run_chaos_simulation.py --correlation

# Custom output directory
python run_chaos_simulation.py --output results/
```

---

### 3. Regenerate All Outputs
Regenerate all outputs and visualizations in one step:

```bash
python regenerate_all_outputs.py
```

**What it does:**
- Runs complete chaos simulation
- Detects anomalies
- Classifies incidents
- Generates all visualizations
- Saves results to `data/processed/`

**Options:**
```bash
# Custom simulation parameters
python regenerate_all_outputs.py --duration 600 --noise 0.2

# Custom services
python regenerate_all_outputs.py --services SERVICE_A SERVICE_B SERVICE_C

# Combine options
python regenerate_all_outputs.py --duration 600 --services SERVICE_X SERVICE_Y --noise 0.25
```

---

## Output Files

After running any script, check `data/processed/` for:

| File | Description |
|------|-------------|
| `chaos_simulation.png` | Fault injection timeline with anomaly detection overlay |
| `dos_simulation_analysis.png` | Correlation heatmap and incident classification |
| `threshold_calibration.png` | F1-score vs detection threshold (if validation data) |
| `pipeline_results.csv` | Full results with anomaly scores |
| `detected_anomalies.csv` | Only anomalies detected by Isolation Forest |

---

## Example Workflows

### Scenario 1: Quick Demo
```bash
# Run 2-minute simulation with 2 services
python run_chaos_simulation.py --duration 120 --services SERVICE_A SERVICE_B
```

### Scenario 2: Extended Testing
```bash
# Run 10-minute simulation with high noise
python run_chaos_simulation.py --duration 600 --noise 0.25 --correlation
```

### Scenario 3: Full Analysis Pipeline
```bash
# Step 1: Generate data
python regenerate_all_outputs.py --duration 300

# Step 2: Run full pipeline (if you have your own data)
python run_full_pipeline.py --data data/raw/my_data.csv
```

### Scenario 4: Production Simulation
```bash
# Long-running simulation with correlation analysis
python run_chaos_simulation.py \
    --duration 1800 \
    --services SERVICE_A SERVICE_B SERVICE_C SERVICE_D \
    --correlation \
    --noise 0.15
```

---

## Parameters Reference

### Common Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--duration` | int | 300 | Simulation duration in seconds |
| `--services` | list | SERVICE_A SERVICE_B SERVICE_C | Services to simulate |
| `--output` | str | data/processed | Output directory |
| `--noise` | float | 0.15 | Noise level (0.0-1.0) |
| `--correlation` | flag | false | Enable correlated fault injection |

### Pipeline-Specific Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--data` | str | data/raw/data.csv | Input data file |

---

## Expected Output

### Console Output Example:
```
================================================================================
🔥 Chaos Engineering Simulation
================================================================================
Start time: 2026-08-23 15:57:42
Duration: 300 seconds
Services: SERVICE_A, SERVICE_B, SERVICE_C
================================================================================

📊 Initializing simulator...
🎯 Injecting faults into 3 services...
🔍 Detecting anomalies...
📋 Classifying incidents...
🔗 Analyzing correlations...
📈 Generating visualizations...

================================================================================
📊 SIMULATION RESULTS
================================================================================

Fault Injection:
  • Total faults injected: 53
  • Services affected: 3
  • Fault types: 4

Anomaly Detection:
  • Total anomalies detected: 47
  • Detection rate: 88.7%

Incident Classification:
  • Total incidents: 8
    - Performance Degradation: 5 (62.5%)
    - Service Unavailability: 3 (37.5%)

Generated Files:
  • chaos_simulation.png - Fault timeline and anomalies
  • dos_simulation_analysis.png - Correlation heatmap and incidents

Execution:
  • Duration: 300 seconds
  • End time: 2026-08-23 16:02:42
  • Status: SUCCESS ✓
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Solution:** Run scripts from the root `aiops-mvp` directory
```bash
cd aiops-mvp
python run_chaos_simulation.py
```

### "FileNotFoundError: data/processed/"
**Solution:** Scripts automatically create the directory
- If it still fails, create manually: `mkdir -p data/processed`

### "No output files generated"
**Solution:** Check console output for errors
- Ensure all dependencies are installed: `pip install -r requirements_minimal.txt`
- Check disk space for output directory

### Slow performance
**Solution:** Reduce parameters
```bash
# Shorter simulation
python run_chaos_simulation.py --duration 120

# Fewer services
python run_chaos_simulation.py --services SERVICE_A
```

---

## Integration with Dashboard

These scripts can be called from the web dashboard:

1. Navigate to **Outputs & Results** page
2. Click **🔄 Regenerate All Outputs**
3. System runs `regenerate_all_outputs.py` in background
4. Results appear in gallery within minutes

---

## Advanced: Custom Configuration

To modify default parameters, edit the relevant script or create a wrapper:

```python
# wrapper.py
import subprocess
import sys

subprocess.run([
    sys.executable,
    'run_chaos_simulation.py',
    '--duration', '600',
    '--services', 'SERVICE_X', 'SERVICE_Y',
    '--correlation',
    '--noise', '0.25'
])
```

Then run: `python wrapper.py`

---

## Data Requirements

For `run_full_pipeline.py`, provide a CSV file with columns:
- **time**: Timestamp or time index
- **service**: Service name
- **metric_value**: Metric measurement
- **deviation_pct**: Percentage deviation
- **label** (optional): Ground truth label (0/1)

Example format:
```csv
time,service,metric_value,deviation_pct
0,SERVICE_A,45.2,5.1
1,SERVICE_A,47.8,3.2
2,SERVICE_A,88.5,92.1
```

---

## Version Information

- **AIOps MVP**: v1.0
- **Python**: 3.8+
- **Key Dependencies**: pandas, scikit-learn, matplotlib, seaborn
- **Last Updated**: August 23, 2026

---

## Support

For issues or questions:
1. Check the console error messages
2. Review this README's troubleshooting section
3. Ensure dependencies are installed: `pip install -r requirements_minimal.txt`
4. Check the dashboard's **System Settings** for ML configuration status
