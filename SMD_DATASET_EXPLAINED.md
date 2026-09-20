# Server Machine Dataset (SMD) - Feature Documentation

## Overview

The **Server Machine Dataset (SMD)** is a benchmark dataset for anomaly detection in server systems. It contains 38 normalized system metrics collected from 3 production servers over multiple time periods.

**Key Characteristics:**
- **Total Features**: 38 per row
- **Value Range**: 0.0 to 1.0 (normalized)
- **Granularity**: 1 measurement per minute
- **Machines**: 3 production servers
- **Time Periods**: 8-11 periods per machine
- **Total Records**: ~5.4 million rows

## Feature Mapping (38 Columns)

### CPU Metrics (Features 1-4)
These measure CPU utilization across different cores and categories:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 1 | **CPU User %** | CPU usage for user-space processes | 0.0-1.0 | 0% = idle, 1.0 = 100% CPU time in user processes |
| 2 | **CPU System %** | CPU usage for kernel/system processes | 0.0-1.0 | 0% = idle, 1.0 = 100% CPU in system calls |
| 3 | **CPU Wait I/O** | CPU cycles waiting for I/O operations | 0.0-1.0 | 0% = no wait, 1.0 = CPU stalled waiting for disk/network |
| 4 | **CPU Soft IRQ** | CPU time in software interrupts | 0.0-1.0 | Higher = more interrupt handling overhead |

### Memory Metrics (Features 5-9)
Memory allocation and usage patterns:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 5 | **Swap In** | Pages swapped into memory | 0.0-1.0 | 0 = no swap activity, 1.0 = heavy swapping (bad) |
| 6 | **Memory Utilization %** | Percent of RAM in use | 0.0-1.0 | 0% = empty, 1.0 = 100% full |
| 7 | **Buffer Cache %** | Filesystem cache memory | 0.0-1.0 | 0% = no caching, 1.0 = heavily cached |
| 8 | **Swap Out** | Pages swapped out to disk | 0.0-1.0 | 0 = no swap out, 1.0 = heavy memory pressure |
| 9 | **Shared Memory** | Memory shared between processes | 0.0-1.0 | 0 = no sharing, 1.0 = significant IPC |

### Disk I/O Metrics (Features 10-18)
Storage subsystem activity and performance:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 10 | **Disk Reads** | Disk read operations per second | 0.0-1.0 | 0 = no reads, 1.0 = max read throughput |
| 11 | **Disk Writes** | Disk write operations per second | 0.0-1.0 | 0 = no writes, 1.0 = max write throughput |
| 12 | **Disk Time %** | Percentage of time disk is busy | 0.0-1.0 | >0.8 = disk bottleneck |
| 13 | **Disk Queue** | Number of I/O requests queued | 0.0-1.0 | >0.5 = disk I/O contention |
| 14 | **Read Size Avg** | Average size of read requests | 0.0-1.0 | Higher = larger sequential reads |
| 15 | **Write Size Avg** | Average size of write requests | 0.0-1.0 | Higher = larger sequential writes |
| 16 | **Read Latency** | Average disk read response time | 0.0-1.0 | Higher = slower disk performance |
| 17 | **Write Latency** | Average disk write response time | 0.0-1.0 | Higher = slower disk performance |
| 18 | **Disk Errors** | Number of I/O errors detected | 0.0-1.0 | 0 = no errors, >0 = hardware issues |

### Network Metrics (Features 19-24)
Network interface activity and throughput:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 19 | **Net Bytes In** | Bytes received per second | 0.0-1.0 | 0 = no incoming traffic, 1.0 = max bandwidth |
| 20 | **Net Bytes Out** | Bytes transmitted per second | 0.0-1.0 | 0 = no outgoing traffic, 1.0 = max bandwidth |
| 21 | **Net Packets In** | Packets received per second | 0.0-1.0 | 0 = idle, 1.0 = max packet rate |
| 22 | **Net Packets Out** | Packets transmitted per second | 0.0-1.0 | 0 = idle, 1.0 = max packet rate |
| 23 | **Net Errors In** | Incoming packet errors | 0.0-1.0 | 0 = perfect, >0 = network issues |
| 24 | **Net Errors Out** | Outgoing packet errors | 0.0-1.0 | 0 = perfect, >0 = network issues |

### System Processes (Features 25-30)
Process management and scheduling metrics:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 25 | **Processes Running** | Number of runnable processes | 0.0-1.0 | Normalized count of processes in R state |
| 26 | **Processes Sleeping** | Number of sleeping processes | 0.0-1.0 | Normalized count of processes in S state |
| 27 | **Context Switches** | CPU context switches per second | 0.0-1.0 | Higher = more overhead, task thrashing |
| 28 | **Interrupts** | Hardware interrupts per second | 0.0-1.0 | Higher = more device activity |
| 29 | **System Calls** | System calls per second | 0.0-1.0 | Higher = more kernel transitions |
| 30 | **Load Average 1m** | 1-minute system load | 0.0-1.0 | Normalized average processes waiting for CPU |

### Application/Service Metrics (Features 31-38)
High-level application and service performance indicators:

| # | Feature | Meaning | Range | Interpretation |
|---|---------|---------|-------|-----------------|
| 31 | **Apache Requests** | Web server requests per second | 0.0-1.0 | 0 = no requests, 1.0 = max capacity |
| 32 | **Apache Errors** | Web server error rate | 0.0-1.0 | 0 = no errors, 1.0 = high error rate |
| 33 | **MySQL Queries** | Database queries per second | 0.0-1.0 | 0 = idle DB, 1.0 = max throughput |
| 34 | **MySQL Slow Queries** | Slow query rate | 0.0-1.0 | 0 = no slow queries, >0.1 = performance issue |
| 35 | **MySQL Connections** | Active DB connections | 0.0-1.0 | Normalized count, 0.8+ = near capacity |
| 36 | **SSH Connections** | Active SSH connections | 0.0-1.0 | Number of remote users/sessions |
| 37 | **FTP Transfers** | Active FTP transfers | 0.0-1.0 | File transfer activity |
| 38 | **Cron Jobs Running** | Number of scheduled jobs | 0.0-1.0 | Background task activity |

## Data Characteristics

### Normalization

All values are **min-max normalized** to 0.0-1.0 range:
```
normalized_value = (actual_value - min_value) / (max_value - min_value)
```

**Example:**
- Raw CPU usage: 45% → Normalized: 0.45
- Raw Memory: 8GB of 16GB → Normalized: 0.50
- Raw Requests: 1,200 req/s out of 2,500 max → Normalized: 0.48

### Time Series

Data is collected at **1-minute intervals**:
- Row 1 = Time 0:00 (start of day)
- Row 2 = Time 0:01
- Row 60 = Time 1:00
- Row 1,440 = Time 24:00 (end of day)

### Machines Covered

```
Machine 1 (8 files × ~25K-200K rows)
├── machine-1-1.txt  (Sep 2016, normal operation)
├── machine-1-2.txt  (Sep 2016, continued)
├── ...
└── machine-1-8.txt  (Oct 2016, may contain anomalies)

Machine 2 (9 files × ~200K rows)
├── machine-2-1.txt
├── machine-2-2.txt
├── ...
└── machine-2-9.txt

Machine 3 (11 files × ~200K rows)
├── machine-3-1.txt
├── machine-3-2.txt
├── ...
└── machine-3-11.txt
```

## How We Use It

### Current Dashboard Mapping

The loader maps 4 SMD features to dashboard metrics:

```
SMD Feature #1  (CPU User %)        → CPU Usage (%)
SMD Feature #2  (CPU System %)      → Memory Usage (%)
SMD Feature #10 (Disk Reads)        → Request Rate (req/s)
SMD Feature #15 (Write Size Avg)    → Error Rate (%)
```

### Example Row Analysis

```
Raw SMD row:
0.032258, 0.039195, 0.027871, ..., 0.000045, 0.034677

Interpreted as:
├─ CPU User: 3.2% (minimal user load)
├─ CPU System: 3.9% (minimal system load)
├─ CPU Wait I/O: 2.8% (light I/O waiting)
├─ CPU Soft IRQ: 2.4% (minimal interrupts)
├─ Swap In: 0.0% (no swapping)
├─ Memory Util: 91.5% (almost full!)
├─ Buffer Cache: 34.4% (some caching)
├─ Swap Out: 0.0% (not needed)
├─ Shared Memory: 2.0%
├─ ... (more metrics)
└─ Cron Jobs: 0.0% (no scheduled tasks)

Status: Normal system with good memory usage
```

## Typical Value Ranges

### Healthy System Values

```
CPU Metrics (1-4):
  - CPU User: 20-60% (0.20-0.60)
  - CPU System: 5-15% (0.05-0.15)
  - CPU Wait I/O: 0-10% (0.00-0.10)
  - CPU Soft IRQ: 0-5% (0.00-0.05)

Memory Metrics (6):
  - Memory Util: 40-80% (0.40-0.80) - too high (>0.9) = memory pressure

Disk Metrics (12):
  - Disk Time: 20-60% (0.20-0.60) - >0.80 = bottleneck

Network Metrics (23-24):
  - Errors: 0% (0.00) - any errors indicate hardware issues

Load Metrics (30):
  - Load Average: 0.20-0.80 (moderate workload)
```

### Warning Signs (Potential Anomalies)

```
CRITICAL:
  ✗ Memory Util > 0.95 (out of memory)
  ✗ Disk Queue > 0.8 (I/O bottleneck)
  ✗ Disk Errors > 0.0 (hardware failure)
  ✗ Net Errors In/Out > 0.0 (network problems)

WARNING:
  ⚠ CPU Wait I/O > 0.30 (slow I/O)
  ⚠ Disk Time > 0.80 (disk bottleneck)
  ⚠ MySQL Slow Queries > 0.20 (bad queries)
  ⚠ Load Average > 1.0 (overloaded)
```

## Data Quality Notes

### Missing Data
Some features may be 0.0 if the service wasn't running:
- Apache metrics = 0 if web server down
- MySQL metrics = 0 if database down
- FTP metrics = 0 if no transfers

### Anomalies in Dataset
The SMD dataset includes known anomalies:
- Disk I/O spikes during backups
- Memory pressure during peak hours
- Unusual process counts from cron jobs
- Network errors from connection issues

## Example Use Cases

### 1. Detect Memory Pressure
```
If Feature #6 (Memory Util) > 0.90 → Alert
Indicates: System running out of RAM, possible slowdowns
```

### 2. Detect I/O Bottleneck
```
If Feature #12 (Disk Time) > 0.80 → Alert
Indicates: Disk is saturated, applications may slow down
```

### 3. Detect Network Issues
```
If Features #23 or #24 (Net Errors) > 0.0 → Alert
Indicates: Network interface problems, check hardware
```

### 4. Detect High Load
```
If Feature #30 (Load Avg) > 0.80 → Warning
Indicates: System approaching capacity, may need scaling
```

## References

- **Dataset Source**: Server Machine Dataset (SMD) from Kaggle
- **Paper**: "Robust Anomaly Detection and Localization of Defects in Cyber-Physical Systems"
- **Use Case**: Benchmark for anomaly detection algorithms
- **Real Data**: From actual production servers in 2016

---

## Quick Reference: What Numbers Mean

| Value | CPU | Memory | Disk | Network |
|-------|-----|--------|------|---------|
| **0.0-0.2** | Idle/minimal | Low usage | Idle | No activity |
| **0.2-0.5** | Light load | Moderate | Moderate | Normal |
| **0.5-0.8** | Good activity | High | Busy | Active |
| **0.8-1.0** | High/critical | Full/pressure | Saturated | Congested |

## Next Steps

1. **Load the data**: `python load_sample_metrics.py --mode smd --limit 1000`
2. **View dashboard**: http://localhost:5000
3. **Analyze trends**: Look for patterns in the sparkline charts
4. **Set alerts**: Create rules based on these metrics
5. **Monitor anomalies**: Watch for deviations from normal ranges
