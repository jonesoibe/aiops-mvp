# Data Loading & Metrics Documentation - Complete Index

## Overview

You now have complete documentation explaining:
1. **What the data is** - Server Machine Dataset (SMD)
2. **What each column means** - All 38 features explained
3. **How to convert values** - Real metrics vs normalized data
4. **How to load data** - 3 methods (SMD, CSV, Synthetic)
5. **How to interpret results** - Anomaly detection patterns

## File Guide

### 🚀 Quick Start (Start Here)

| File | Purpose | Read Time |
|------|---------|-----------|
| [QUICK_START_METRICS.md](QUICK_START_METRICS.md) | Common commands and use cases | 2 min |
| [METRICS_LOADING_SUMMARY.md](METRICS_LOADING_SUMMARY.md) | Complete solution overview | 3 min |

### 📊 Data Explanation (For Understanding)

| File | Purpose | Read Time |
|------|---------|-----------|
| [SMD_DATASET_EXPLAINED.md](SMD_DATASET_EXPLAINED.md) | **All 38 features detailed** - What each number means | 10 min |
| [SMD_QUICK_REFERENCE.txt](SMD_QUICK_REFERENCE.txt) | Cheat sheet - Thresholds and alert levels | 5 min |
| [CONVERTING_METRICS.md](CONVERTING_METRICS.md) | How to convert normalized → real values | 8 min |

### 🔧 Implementation (For Doing)

| File | Purpose | Use Case |
|------|---------|----------|
| [load_sample_metrics.py](load_sample_metrics.py) | Main data loader script | Load any metrics into dashboard |
| [SAMPLE_DATA_LOADING.md](SAMPLE_DATA_LOADING.md) | Detailed usage guide with examples | Advanced options and troubleshooting |
| [example_metrics.csv](example_metrics.csv) | Sample CSV template | Create your own metric files |

---

## The Data: Server Machine Dataset (SMD)

### Location
```
C:\Users\FAVOUR\aiops-mvp\data\raw\smd\
├── machine-1-1.txt through machine-1-8.txt    (200K rows each)
├── machine-2-1.txt through machine-2-9.txt    (200K rows each)
└── machine-3-1.txt through machine-3-11.txt   (200K rows each)

Total: ~5.4 million rows, 27 files, ~1.5 GB
```

### What It Contains

**38 system metrics per row, collected every minute:**

```
Row Format: Feature_1, Feature_2, Feature_3, ..., Feature_38

Example Row:
0.032, 0.039, 0.028, 0.024, 0.000, 0.915, 0.344, 0.000, 0.020, 0.000, ...
 |CPU |CPU  |CPU  |CPU  |Swap |Mem  |Cache|Swap |IPC  |Disk |  ...
 User |Sys  |Wait |IRQ  |In   |Util |%    |Out  |Mem  |Reads|
```

### Data Characteristics

- **Format**: Comma-separated values, no headers
- **Normalization**: All values 0.0-1.0 (min-max normalized)
- **Time Series**: 1 row = 1 minute
- **Real Data**: From production servers in 2016
- **Anomalies**: Known issues included for benchmark testing

---

## Understanding the Data

### Quick Lookup: Feature Meanings

**CPU (Features 1-4)**
- #1: CPU User % - user application CPU usage
- #2: CPU System % - kernel CPU usage
- #3: CPU Wait I/O - CPU waiting for disk/network
- #4: CPU Soft IRQ - interrupt handling overhead

**Memory (Features 5-9)**
- #5: Swap In - memory being swapped into RAM
- #6: Memory Util % - **percent of RAM in use** ⭐ KEY METRIC
- #7: Buffer Cache % - filesystem caching
- #8: Swap Out - memory being swapped to disk
- #9: Shared Memory - inter-process communication

**Disk (Features 10-18)**
- #10: Disk Reads - read operations/sec
- #11: Disk Writes - write operations/sec
- #12: Disk Time % - percent disk is busy ⭐ KEY METRIC
- #13: Disk Queue - I/O requests waiting
- #14-17: Latencies and sizes
- #18: Disk Errors - hardware failures

**Network (Features 19-24)**
- #19-22: Bytes/packets in/out
- #23-24: Network errors ⭐ KEY METRIC (0 = good)

**Processes (Features 25-30)**
- #25-29: Process counts and context switches
- #30: Load Average - system utilization ⭐ KEY METRIC

**Services (Features 31-38)**
- #31-32: Apache web server metrics
- #33-35: MySQL database metrics
- #36-38: SSH, FTP, Cron activity

### Value Interpretation

```
0.0-0.2  = Idle or minimal
0.2-0.5  = Light activity
0.5-0.8  = Moderate to heavy
0.8-1.0  = Critical/maximum
```

### Health Indicators

```
✓ HEALTHY:
  Feature #6 (Memory) < 0.80
  Feature #12 (Disk Time) < 0.60
  Feature #23 (Net Errors) = 0.00
  Feature #30 (Load) < 0.80

⚠ WARNING:
  Feature #6 > 0.85 (memory pressure)
  Feature #12 > 0.75 (disk bottleneck)
  Feature #34 > 0.15 (slow queries)

🔴 CRITICAL:
  Feature #6 > 0.95 (out of memory!)
  Feature #18 > 0.00 (disk errors!)
  Feature #23 > 0.00 (network errors!)
  Feature #32 > 0.20 (error rate > 20%)
```

---

## Loading Data: Methods Comparison

| Method | Use Case | Duration | Command |
|--------|----------|----------|---------|
| **SMD** | Real server data | 1-10 min | `python load_sample_metrics.py --mode smd --limit 2000` |
| **CSV** | Your own metrics | Variable | `python load_sample_metrics.py --mode csv --file metrics.csv` |
| **Synthetic** | Testing/demo | <1 min | `python load_sample_metrics.py --mode synthetic --limit 1000` |

### Quick Commands

```bash
# Load real data fast (5 sec)
python load_sample_metrics.py --mode smd --limit 100

# Load real data with trends (30 sec)
python load_sample_metrics.py --mode smd --limit 1000 --interval 0.2

# Load all available SMD data (10 min)
python load_sample_metrics.py --mode smd

# Load your CSV file
python load_sample_metrics.py --mode csv --file my_metrics.csv

# Generate test data
python load_sample_metrics.py --mode synthetic --limit 500
```

---

## Typical Scenarios

### Scenario 1: "My memory usage seems high"

1. **Check Feature #6 (Memory Util %)**
   ```
   Value: 0.92
   Meaning: 92% of RAM is in use
   ```

2. **Look for correlations**
   ```
   High Memory (#6) + High Swap In (#5) → Memory pressure
   High Memory (#6) + Normal Disk (#12) → Data in RAM (OK)
   ```

3. **Check if swapping**
   ```
   Feature #5 > 0.0 → Pages being swapped to disk (bad)
   Feature #8 > 0.0 → Memory being evicted (pressure)
   ```

### Scenario 2: "Database is slow"

1. **Check database metrics**
   ```
   Feature #33 (QPS): 0.85 × 10000 = 8500 queries/sec (heavy!)
   Feature #34 (Slow): 0.25 = 25% of queries are slow
   Feature #35 (Conn): 0.92 × 100 = 92 of 100 max connections
   ```

2. **Look for root cause**
   ```
   High QPS (#33) + High Slow (#34) + High Load (#30) 
   → Database CPU-bound, needs optimization
   
   High QPS (#33) + High Disk (#12) + Low Memory (#6)
   → Database doing disk I/O, add more RAM
   ```

### Scenario 3: "Network is slow"

1. **Check network metrics**
   ```
   Feature #19: 0.75 × 1000 Mbps = 750 Mbps (heavy!)
   Feature #23: 0.05 = packet errors detected (5% loss)
   Feature #24: 0.00 = no send errors
   ```

2. **Diagnosis**
   ```
   High Bytes (#19-20) + Network Errors (#23) → Network congestion
   Network Errors (#23 or #24) > 0 → Hardware failure
   Low Throughput (#19-20) + Timeouts → Latency issues
   ```

---

## Converting Your Own Metrics

### If you have real values

```
Example: Your CSV has:
cpu,memory,request_rate,error_rate
45.5,62.3,1200,0.5

This means:
├─ CPU: 45.5% (out of 100%)
├─ Memory: 62.3% (out of 100%)  
├─ Requests: 1200 per second
└─ Errors: 0.5% error rate

Load it with:
python load_sample_metrics.py --mode csv --file my_metrics.csv
```

### If you have normalized SMD format

```
Example: You have SMD data:
0.455,0.623,0.60,0.05

To convert to real values:
├─ CPU: 0.455 × 100% = 45.5%
├─ Memory: 0.623 × 100% = 62.3%
├─ Request Rate: 0.60 × 2000 req/s = 1200/s
└─ Error Rate: 0.05 × 10% = 0.5%

See: CONVERTING_METRICS.md for detailed formulas
```

---

## Feature Reference by Use Case

### For Web Server Operations
```
Focus on: #31-32 (Apache metrics)
         #19-22 (Network)
         #1-4 (CPU)
         #30 (System Load)
```

### For Database Performance
```
Focus on: #33-35 (MySQL metrics)
         #10-17 (Disk I/O)
         #6 (Memory)
         #1-4 (CPU)
```

### For System Health
```
Focus on: #6 (Memory %)
         #12 (Disk Time %)
         #30 (Load Average)
         #23-24 (Network Errors)
         #18 (Disk Errors)
```

### For Anomaly Detection
```
Monitor: Any feature > 0.90 (high)
        Any feature < 0.05 and previously > 0.20 (dropped)
        Errors (#18, #23, #24) > 0.00 (new errors)
        Load (#30) > 0.90 (spike)
```

---

## Example Analysis

### Raw SMD Row
```csv
0.32, 0.04, 0.03, 0.02, 0.00, 0.92, 0.34, 0.00, 0.02, 0.00, 0.11, 0.08, 
0.03, 0.06, 0.09, 0.12, 0.00, 0.00, 0.06, 0.04, 0.04, 0.03, 0.53, 0.01, 
0.01, 0.01, 0.00, 0.04, 0.00, 0.00, 0.03, 0.02, 0.00, 0.00, 0.03, 0.03, 
0.00, 0.00
```

### Interpreted as (on Medium Server)
```
CPU Metrics:
├─ User CPU: 32% (moderate)
├─ System CPU: 4% (low)
├─ Wait I/O: 3% (minimal)
└─ Soft IRQ: 2% (minimal)

Memory: 92% of 32GB = 29.4 GB in use (ALERT! Memory pressure)

Disk: 8% disk time (very light I/O)

Network: 6% Bytes in, 4% out (light traffic)

Database: MySQL at 1% QPS (quiet)

Overall Status: SYSTEM MOSTLY IDLE, BUT MEMORY NEARLY FULL
```

---

## Documentation Files Summary

```
📁 Project Root (C:\Users\FAVOUR\aiops-mvp\)
│
├─ 📄 DATA_DOCUMENTATION_INDEX.md (this file)
│  └─ Overview of all documentation
│
├─ 🚀 QUICK_START_METRICS.md
│  └─ Common commands (2 min read)
│
├─ 📊 SMD_DATASET_EXPLAINED.md ⭐ MOST DETAILED
│  └─ All 38 features with examples (10 min read)
│
├─ 📋 SMD_QUICK_REFERENCE.txt
│  └─ Thresholds and decision tree (5 min read)
│
├─ 🔄 CONVERTING_METRICS.md
│  └─ How to convert values (8 min read)
│
├─ 💾 METRICS_LOADING_SUMMARY.md
│  └─ Full solution overview (5 min read)
│
├─ 📖 SAMPLE_DATA_LOADING.md
│  └─ Detailed usage guide (10 min read)
│
├─ 🐍 load_sample_metrics.py
│  └─ Loader script (11KB)
│
├─ 📝 example_metrics.csv
│  └─ CSV template for your data
│
└─ 📂 data/raw/smd/
   └─ 27 SMD files (~1.5 GB total)
```

---

## Next Steps

1. **Read [SMD_DATASET_EXPLAINED.md](SMD_DATASET_EXPLAINED.md)** ← Start here to understand the data
2. **Load some data**: `python load_sample_metrics.py --mode smd --limit 500`
3. **View dashboard**: Open http://localhost:5000
4. **Check [SMD_QUICK_REFERENCE.txt](SMD_QUICK_REFERENCE.txt)** ← Refer while analyzing
5. **Create alerts** based on thresholds in the documentation
6. **Load your own CSV** using the converter guide

---

## Troubleshooting & FAQ

**Q: What does a Feature value of 0.75 really mean?**  
A: It depends on the feature. See [SMD_DATASET_EXPLAINED.md](SMD_DATASET_EXPLAINED.md) for your specific feature.

**Q: How do I know if my system is healthy?**  
A: Check [SMD_QUICK_REFERENCE.txt](SMD_QUICK_REFERENCE.txt) - Feature #6 < 0.80, #12 < 0.60, #23/24 = 0.00

**Q: Can I load my own CSV with different column names?**  
A: Yes! See [CONVERTING_METRICS.md](CONVERTING_METRICS.md) or use `--cpu-col` option

**Q: What's the difference between normalized (0.0-1.0) and real values?**  
A: See [CONVERTING_METRICS.md](CONVERTING_METRICS.md) - explains formulas and conversion

**Q: Where should I start reading?**  
A: Start with [QUICK_START_METRICS.md](QUICK_START_METRICS.md), then [SMD_DATASET_EXPLAINED.md](SMD_DATASET_EXPLAINED.md)

---

**Created**: 2026-09-20  
**Last Updated**: 2026-09-20  
**Total Documentation**: 45KB across 7 files  
**Data Available**: ~5.4 million rows, 27 machines, 38 metrics each
