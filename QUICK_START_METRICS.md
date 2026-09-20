# Quick Start: Loading Metrics into Nexus AIOps

## The Script

The `load_sample_metrics.py` script loads real or synthetic metrics into your dashboard.

## Three Easy Ways to Load Data

### 1. Load Real Server Machine Dataset (SMD)

You already have this data in `data/raw/smd/` - real system metrics from Kaggle:

```bash
# Load 100 metrics
python load_sample_metrics.py --mode smd --limit 100

# Load 500 metrics with slower injection (more realistic)
python load_sample_metrics.py --mode smd --limit 500 --interval 0.5

# Load all data from specific machine file
python load_sample_metrics.py --mode smd --file data/raw/smd/machine-2-3.txt
```

### 2. Load Your Own CSV File

Create a CSV with columns: `cpu`, `memory`, `request_rate`, `error_rate`

```bash
# Simple CSV load
python load_sample_metrics.py --mode csv --file my_metrics.csv

# CSV with different column names
python load_sample_metrics.py --mode csv --file metrics.csv \
  --cpu-col "CPU_PCT" \
  --mem-col "MEM_PCT" \
  --req-col "REQUESTS_PS" \
  --err-col "ERROR_PCT"
```

### 3. Generate Synthetic Data

No files needed - generates realistic synthetic metrics:

```bash
# Generate 1000 metrics
python load_sample_metrics.py --mode synthetic --limit 1000

# Fast injection for testing
python load_sample_metrics.py --mode synthetic --limit 500 --interval 0.05
```

## View Results

Open the dashboard in your browser:

```
http://localhost:5000
```

You'll see:
- ✓ Key System Metrics (CPU, Memory, Disk, Network, Requests, Errors)
- ✓ Real-time updates every 5 seconds
- ✓ Sparkline charts showing trends
- ✓ Status badges (HEALTHY/WARNING/CRITICAL)

## Common Use Cases

### Load test data quickly (10 seconds)
```bash
python load_sample_metrics.py --mode synthetic --limit 500 --interval 0.01
```

### Load real data slowly (realistic ingestion, 1-2 minutes)
```bash
python load_sample_metrics.py --mode smd --limit 2000 --interval 0.2
```

### Load from a Kaggle dataset CSV
```bash
python load_sample_metrics.py --mode csv --file kaggle_metrics.csv --limit 5000
```

### Load multiple SMD machines
```bash
# Machine 1
python load_sample_metrics.py --mode smd --file data/raw/smd/machine-1-5.txt --limit 1000

# Machine 2
python load_sample_metrics.py --mode smd --file data/raw/smd/machine-2-7.txt --limit 1000

# Machine 3
python load_sample_metrics.py --mode smd --file data/raw/smd/machine-3-9.txt --limit 1000
```

## Available SMD Files

```
data/raw/smd/
├── machine-1-1.txt through machine-1-8.txt   (8 periods)
├── machine-2-1.txt through machine-2-9.txt   (9 periods)
└── machine-3-1.txt through machine-3-11.txt  (11 periods)

Total: ~200,000+ rows of metrics per machine
```

## What Data is Mapped?

### SMD Format (38 features)
```
Feature  1  → CPU Usage (%)
Feature  2  → Memory Usage (%)
Feature 10  → Request Rate (req/s)
Feature 15  → Error Rate (%)
```

### Custom CSV Format
```csv
cpu,memory,request_rate,error_rate
45.5,62.3,120,0.5
48.2,65.1,125,0.6
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Make sure `python nexus_app.py` is running |
| No metrics appear | Refresh the dashboard page (F5) |
| Slow loading | Use `--interval 0.05` for faster injection |
| "File not found" | Check path: `dir data/raw/smd/` |

## API Details (if you need it)

The script uses two endpoints:

1. **Login**: `POST /api/auth/login`
2. **Record Metrics**: `POST /api/metrics/record`

Payload format:
```json
{
  "cpu": 45.5,
  "memory": 62.3,
  "request_rate": 120,
  "error_rate": 0.5
}
```

---

For more details, see [SAMPLE_DATA_LOADING.md](SAMPLE_DATA_LOADING.md)
