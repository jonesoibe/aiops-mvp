# Sample Metrics Data Loading - Complete Solution

## Overview

You now have a complete solution to feed sample data to the Nexus AIOps dashboard in three ways:

1. **Real Data**: Server Machine Dataset (SMD) with 38 system metrics per row
2. **Custom Data**: Your own CSV files in any format
3. **Synthetic Data**: Auto-generated realistic metrics for testing

## Files Created

| File | Purpose | Size |
|------|---------|------|
| [load_sample_metrics.py](load_sample_metrics.py) | Main data loader script | 11K |
| [QUICK_START_METRICS.md](QUICK_START_METRICS.md) | Quick reference guide | 3.6K |
| [SAMPLE_DATA_LOADING.md](SAMPLE_DATA_LOADING.md) | Detailed documentation | 5.8K |
| [example_metrics.csv](example_metrics.csv) | Example CSV template | 650B |

## Your Data Source

### Server Machine Dataset (SMD)

Located in: `C:\Users\FAVOUR\aiops-mvp\data\raw\smd\`

```
Available files (27 total):
├── machine-1-1.txt through machine-1-8.txt   (200K+ rows each)
├── machine-2-1.txt through machine-2-9.txt   (200K+ rows each)
└── machine-3-1.txt through machine-3-11.txt  (200K+ rows each)

Total: ~5.4 million rows of real system metrics
```

**Data Mapping (SMD → Dashboard):**
- SMD Feature 1  → CPU Usage (%)
- SMD Feature 2  → Memory Usage (%)
- SMD Feature 10 → Request Rate (req/s)
- SMD Feature 15 → Error Rate (%)

## Quick Usage

### Load SMD Data (Recommended)

```bash
# Fast: Load 50 metrics (for quick testing)
python load_sample_metrics.py --mode smd --limit 50

# Medium: Load 500 metrics (5-10 seconds)
python load_sample_metrics.py --mode smd --limit 500 --interval 0.1

# Large: Load 2000 metrics (30-60 seconds, shows good trends)
python load_sample_metrics.py --mode smd --limit 2000 --interval 0.1

# Load all (full dataset, several minutes)
python load_sample_metrics.py --mode smd --interval 0.1
```

### Load Custom CSV

```bash
# Default column names (cpu, memory, request_rate, error_rate)
python load_sample_metrics.py --mode csv --file my_data.csv

# Custom column names
python load_sample_metrics.py --mode csv --file data.csv \
  --cpu-col "CPU_Percent" \
  --mem-col "Memory_Percent" \
  --req-col "Requests_PerSec" \
  --err-col "Error_Percent"
```

### Generate Synthetic Data

```bash
# 1000 realistic metrics (10-15 seconds)
python load_sample_metrics.py --mode synthetic --limit 1000

# 500 metrics with very fast injection (testing)
python load_sample_metrics.py --mode synthetic --limit 500 --interval 0.01
```

## Example CSV Format

Create your own CSV file with this format:

```csv
cpu,memory,request_rate,error_rate
45.5,62.3,120,0.5
48.2,65.1,125,0.6
46.1,63.2,118,0.4
```

See [example_metrics.csv](example_metrics.csv) for a complete sample.

## What You Get on the Dashboard

After loading data, visit **http://localhost:5000** and you'll see:

**Summary Section:**
- Health Percentage: 100%
- Warning/Critical Metrics: 0
- Live timestamp

**Key System Metrics (6 cards):**
1. CPU Usage (with trend chart)
2. Memory Usage (with trend chart)
3. Disk Usage (with trend chart)
4. Network I/O (ops/sec)
5. Request Rate (req/s)
6. Error Rate (%)

**Active Anomalies:**
- 4 anomaly types (all shown as Inactive with test data)

**Real-Time Updates:**
- Metrics refresh every 5 seconds
- Sparkline charts show historical trends
- Status badges change based on thresholds

## Advanced Options

```bash
# Control injection speed
python load_sample_metrics.py --mode smd --limit 1000 --interval 0.2

# Skip initial rows
python load_sample_metrics.py --mode csv --file data.csv --skip 2 --limit 100

# Use custom API URL
python load_sample_metrics.py --mode smd --url http://192.168.1.100:5000 --limit 50

# Load from specific SMD machine
python load_sample_metrics.py --mode smd \
  --file data/raw/smd/machine-2-5.txt \
  --limit 1000
```

## Performance Notes

| Scenario | Command | Duration | Result |
|----------|---------|----------|--------|
| Quick test | `--limit 50 --interval 0.05` | 2-3 sec | Limited trend data |
| Small demo | `--limit 500 --interval 0.1` | 10-15 sec | Good sparklines |
| Medium load | `--limit 2000 --interval 0.1` | 30-50 sec | Excellent trends |
| Full load | no limit | 5-10 min | All data loaded |

## Integration with Your Workflow

1. **Development**: Use synthetic data for quick testing
2. **Demo**: Use SMD data (shows real metrics)
3. **Testing**: Use custom CSV with specific scenarios
4. **Production**: Connect real Prometheus/Grafana data sources

## Troubleshooting

**Q: "Authentication failed"**
- A: Make sure `python nexus_app.py` is running first

**Q: No metrics appear on dashboard**
- A: Refresh the page (F5) after loading completes

**Q: Metrics appear but don't update**
- A: Wait 5-10 seconds for real-time refresh timer

**Q: Loading is very slow**
- A: Use `--interval 0.05` or lower for faster injection

**Q: "File not found" for SMD**
- A: Verify path: `dir data\raw\smd\`

## API Endpoints

The loader uses these REST endpoints (for reference):

```
POST /api/auth/login
  Request:  {"username": "admin", "password": "admin123"}
  Response: {"token": "eyJ..."}

POST /api/metrics/record
  Headers:  Authorization: Bearer <token>
  Request:  {
    "cpu": 45.5,
    "memory": 62.3,
    "request_rate": 120,
    "error_rate": 0.5
  }
  Response: {
    "metrics_recorded": {...},
    "scaling_action": {...},
    "alerts_triggered": [...]
  }
```

## Next Steps

1. **Load Data**: Run one of the commands above
2. **View Dashboard**: Open http://localhost:5000
3. **Explore Metrics**: Click on metric cards to see details
4. **Create Alerts**: Use the dashboard to set up alert rules
5. **Monitor Trends**: Watch sparkline charts update in real-time

---

For detailed documentation, see:
- [QUICK_START_METRICS.md](QUICK_START_METRICS.md) - Quick reference
- [SAMPLE_DATA_LOADING.md](SAMPLE_DATA_LOADING.md) - Complete guide
