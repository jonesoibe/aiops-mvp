# Loading Sample Metrics into Nexus AIOps

This guide shows how to populate the Real-Time System Overview dashboard with real or synthetic metrics data.

## Quick Start

### 1. Ensure the API is Running

```bash
python nexus_app.py
```

The server will run on `http://localhost:5000`

### 2. Load Sample Data

Choose one of three options:

#### Option A: Load Server Machine Dataset (SMD)

The SMD files in `data/raw/smd/` contain real server metrics from Kaggle.

```bash
# Load the first 500 records from the first SMD file
python load_sample_metrics.py --mode smd --limit 500

# Load from a specific SMD file
python load_sample_metrics.py --mode smd --file data/raw/smd/machine-1-2.txt --limit 1000

# Load all available data with 0.5 second delay between requests
python load_sample_metrics.py --mode smd --interval 0.5
```

**What it does:**
- Maps SMD's 38 features to 4 key metrics:
  - Feature 1 → CPU Usage (0-100%)
  - Feature 2 → Memory Usage (0-100%)
  - Feature 10 → Request Rate (0-200 req/s)
  - Feature 15 → Error Rate (0-5%)

#### Option B: Load Custom CSV

If you have your own CSV file with metrics:

```bash
# CSV with default column names (cpu, memory, request_rate, error_rate)
python load_sample_metrics.py --mode csv --file metrics.csv

# CSV with custom column names
python load_sample_metrics.py --mode csv \
  --file custom_metrics.csv \
  --cpu-col "CPU%" \
  --mem-col "Memory%" \
  --req-col "ReqPerSec" \
  --err-col "ErrorPercent"

# Load only first 100 records, skip header rows
python load_sample_metrics.py --mode csv --file metrics.csv --limit 100 --skip 1
```

**CSV Format Requirements:**
```csv
cpu,memory,request_rate,error_rate
45.5,62.3,120,0.5
48.2,65.1,125,0.6
...
```

#### Option C: Generate Synthetic Metrics

For testing without external data:

```bash
# Generate 1000 realistic synthetic metrics
python load_sample_metrics.py --mode synthetic --limit 1000

# Generate with faster injection (0.05s between requests)
python load_sample_metrics.py --mode synthetic --limit 2000 --interval 0.05
```

## Advanced Usage

### Control Request Rate

The `--interval` parameter controls delay between API calls (in seconds):

```bash
# Fast injection (testing)
python load_sample_metrics.py --mode smd --interval 0.05

# Realistic rate (slow injection)
python load_sample_metrics.py --mode smd --interval 1.0
```

### Skip Rows

Skip header rows or initial data:

```bash
python load_sample_metrics.py --mode csv --file metrics.csv --skip 2
```

### Specify API URL

If using a different host/port:

```bash
python load_sample_metrics.py --mode smd --url http://192.168.1.100:5000
```

## View the Loaded Data

After loading metrics, visit the dashboard:

**http://localhost:5000**

You should see:
- ✅ **Key System Metrics** section populated with CPU, Memory, Disk, Network, Request Rate, Error Rate
- ✅ **Real-time updates** every 5 seconds
- ✅ **Sparkline charts** showing metric trends
- ✅ **Status badges** (HEALTHY/WARNING/CRITICAL)

## Understanding SMD Data

The Server Machine Dataset contains 38 time-series features for 5 machines:
- **Files**: `machine-1-1.txt` through `machine-3-11.txt`
- **Size**: ~200,000 rows per machine
- **Features**: CPU, memory, network, disk, and application metrics (normalized 0-1)

### Available SMD Files

```
data/raw/smd/
├── machine-1-1.txt through machine-1-8.txt (Machine 1, 8 time periods)
├── machine-2-1.txt through machine-2-9.txt (Machine 2, 9 time periods)
└── machine-3-1.txt through machine-3-11.txt (Machine 3, 11 time periods)
```

Each file contains one row per minute of system metrics.

## Creating Your Own CSV

Example format for custom metrics:

```csv
timestamp,cpu,memory,request_rate,error_rate
2024-01-01 10:00:00,45.5,62.3,120,0.5
2024-01-01 10:01:00,48.2,65.1,125,0.6
2024-01-01 10:02:00,46.1,63.2,118,0.4
```

Or simplified (without timestamp):

```csv
cpu,memory,request_rate,error_rate
45.5,62.3,120,0.5
48.2,65.1,125,0.6
46.1,63.2,118,0.4
```

## Troubleshooting

### "Authentication failed"

Make sure the API is running and credentials are correct:

```bash
# Check API is running on localhost:5000
curl http://localhost:5000

# Or specify custom URL
python load_sample_metrics.py --url http://your-ip:5000
```

### No metrics appear on dashboard

1. Check if loading completed successfully (should show "✅ Loaded X metrics")
2. Refresh the dashboard page
3. Wait 5-10 seconds for real-time updates
4. Check browser console for JavaScript errors

### "File not found" for SMD

Verify SMD directory path:

```bash
# Windows
dir C:\Users\FAVOUR\aiops-mvp\data\raw\smd\

# Linux/Mac
ls -la ~/aiops-mvp/data/raw/smd/
```

### Slow loading

Reduce interval for faster injection:

```bash
# Inject 10 requests per second instead of 2
python load_sample_metrics.py --mode smd --interval 0.1 --limit 1000
```

## API Endpoints Used

The loader uses these REST endpoints:

```
POST /api/auth/login
  - Payload: {"username": "admin", "password": "admin123"}
  - Returns: JWT token

POST /api/metrics/record
  - Headers: Authorization: Bearer <token>
  - Payload: {"cpu": 45.5, "memory": 62.3, "request_rate": 120, "error_rate": 0.5}
  - Returns: {"metrics_recorded": {...}, "scaling_action": {...}, "alerts_triggered": [...]}
```

## Example Workflow

```bash
# 1. Start the application
python nexus_app.py &

# 2. Wait for it to be ready (should see "Running on http://...")
sleep 5

# 3. Load 2000 metrics from SMD files
python load_sample_metrics.py --mode smd --limit 2000 --interval 0.1

# 4. Open browser to view dashboard
# http://localhost:5000

# 5. Watch metrics update in real-time!
```

## Performance Tips

- **Fast load (few seconds)**: `--interval 0.05 --limit 500`
- **Medium load (1-2 min)**: `--interval 0.2 --limit 2000`
- **Full load (10+ min)**: `--interval 0.1` (all 200K+ rows)

Larger datasets will show more realistic trends and patterns in the sparkline charts.
