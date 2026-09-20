# Converting Metrics: SMD to Real Values

## Understanding the Normalization

All SMD values are **min-max normalized** to a 0.0-1.0 range. To convert back to real values, you need to know the original ranges.

### General Formula

```
Real_Value = Normalized_Value × (Max_Value - Min_Value) + Min_Value
```

## Feature Conversion Examples

### Feature #1: CPU User %

**SMD Value**: 0.45  
**Interpretation**: 45% of CPU (if max possible is 100%)

```
Real CPU % = 0.45 × 100 = 45%
```

### Feature #6: Memory Utilization %

**SMD Value**: 0.72  
**Interpretation**: 72% of available RAM

```
If server has 64GB RAM:
Real Memory Used = 0.72 × 64 = 46.08 GB in use
Available = 17.92 GB free
```

### Feature #10: Disk Reads

**SMD Value**: 0.35  
**Interpretation**: 35% of max read capacity

```
If max disk read = 1000 IOPS:
Real Disk Reads = 0.35 × 1000 = 350 IOPS

If max disk read = 500 MB/s:
Real Disk Reads = 0.35 × 500 = 175 MB/s
```

### Feature #19: Network Bytes In

**SMD Value**: 0.28  
**Interpretation**: 28% of network bandwidth

```
If server has 1 Gbps network:
Real Throughput = 0.28 × 1000 Mbps = 280 Mbps incoming

If server has 10 Gbps network:
Real Throughput = 0.28 × 10000 Mbps = 2800 Mbps incoming
```

## Real-World Server Baseline Values

### Typical Server Specifications

```
Machine Size: Medium VM
├─ CPU: 8 cores (e.g., 8 × 2.4 GHz)
├─ Memory: 32 GB RAM
├─ Disk: SSD with 50,000 IOPS capacity
├─ Network: 1 Gbps (1000 Mbps)
└─ Services: Apache web + MySQL database

Max Capacity Values:
├─ CPU: 100% (8 cores = 800% if counting all)
├─ Memory: 32 GB
├─ Disk Reads: 50,000 IOPS
├─ Disk Writes: 50,000 IOPS  
├─ Disk Throughput: 1000 MB/s
├─ Network Bandwidth: 1000 Mbps
└─ Connections: 10,000
```

## Converting SMD Data to Real Metrics

### Example: One row from machine-1-1.txt

**Raw SMD Values:**
```
0.032258, 0.039195, 0.027871, 0.024390, 0.000000, 0.915385, 0.343691, 0.000000, 
0.020011, 0.000122, 0.106312, 0.081081, 0.027397, 0.060266, 0.085018, 0.122516, 
0.000000, 0.000000, 0.062195, 0.041221, 0.043242, 0.031607, 0.533195, 0.010224, ...
```

**Converted to Real Values (Medium Server):**

```
CPU METRICS:
├─ User %:        0.032258 × 100 = 3.2%
├─ System %:      0.039195 × 100 = 3.9%
├─ Wait I/O %:    0.027871 × 100 = 2.8%
└─ Soft IRQ %:    0.024390 × 100 = 2.4%
   Total CPU: ~12.3% utilized (very light)

MEMORY METRICS:
├─ Swap In:       0.000000 = 0 pages/sec (no swapping)
├─ Memory Util:   0.915385 × 32 GB = 29.3 GB used / 2.7 GB free
├─ Buffer Cache:  0.343691 × 32 GB = 11 GB for caching
├─ Swap Out:      0.000000 = 0 pages/sec (no pressure)
└─ Shared Memory: 0.020011 = minimal IPC

DISK METRICS:
├─ Reads/sec:     0.000122 × 50,000 = 6 IOPS
├─ Writes/sec:    0.106312 × 50,000 = 5,315 IOPS
├─ Disk Time:     0.081081 = disk busy 8.1% (light load)
├─ Queue Depth:   0.027397 (very few requests waiting)
├─ Avg Read Size: 0.060266 (small reads)
└─ Read Latency:  0.085018 × 10ms = 0.85ms (fast)

NETWORK METRICS:
├─ Bytes In:      0.062195 × 1000 Mbps = 62.2 Mbps incoming
├─ Bytes Out:     0.041221 × 1000 Mbps = 41.2 Mbps outgoing
├─ Packets In:    0.043242 (light packet rate)
├─ Packets Out:   0.031607 (light packet rate)
├─ Errors In:     0.533195 (500+ errors/sec if normalized)
└─ Errors Out:    0.010224 (10-20 errors/sec)

SERVICE METRICS:
├─ Apache Req/s:  0.533195 × 2000 req/s = 1,066 requests/sec
├─ MySQL QPS:     0.010224 × 10,000 = 102 queries/sec
└─ Slow Queries:  0.010224 (1% slow)

TIMESTAMP: Current minute in the dataset
```

**Status**: System is **LIGHTLY LOADED**
- Low CPU utilization (12%)
- Memory nearly full (91% used - potential concern)
- Very light disk activity
- Light network activity
- Moderate web traffic, light database activity

## Creating Your Own CSV with Real Values

### Option 1: Use Real Server Metrics Directly

```csv
cpu,memory,request_rate,error_rate
45.5,62.3,1200,0.5
48.2,65.1,1250,0.6
46.1,63.2,1180,0.4
```

**What these mean:**
- CPU: 45.5% utilization
- Memory: 62.3 GB used (on 100 GB server)
- Request Rate: 1,200 requests/second
- Error Rate: 0.5% of requests failed

### Option 2: Normalize Your Data to SMD Format

If you want to match SMD's normalized format (0.0-1.0):

```python
# Example Python code to normalize your metrics
import csv

def normalize(value, min_val, max_val):
    """Convert real value to 0.0-1.0 normalized format"""
    return (value - min_val) / (max_val - min_val)

# Example: Normalize CPU 45% on a system where max is 100%
cpu_normalized = normalize(45, 0, 100)  # Result: 0.45

# Example: Normalize 62 GB memory on 100 GB system
memory_normalized = normalize(62, 0, 100)  # Result: 0.62

# For your CSV:
with open('metrics.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cpu_real = float(row['cpu'])
        memory_real = float(row['memory'])
        
        # Normalize to 0.0-1.0
        cpu_normalized = cpu_real / 100  # Assuming 0-100%
        memory_normalized = memory_real / 100  # Assuming 0-100 GB
        
        print(f"{cpu_normalized:.2f},{memory_normalized:.2f}")
```

## Reverse Conversion: Understanding Dashboard Values

### Dashboard Shows Real Values

When you load data, the dashboard displays:

```
CPU Usage: 45.5%        ← This is the REAL percentage
Memory Usage: 62.3%     ← This is the REAL percentage
Request Rate: 1200 req/s ← This is the REAL rate
Error Rate: 0.5%        ← This is the REAL percentage
```

### How the Conversion Works

```
If SMD Feature #1 = 0.45 (normalized)
and we know max CPU = 100%

Dashboard shows: 0.45 × 100 = 45% ✓

If SMD Feature #6 = 0.72 (normalized)  
and we know server has 32GB RAM

Dashboard shows: 0.72 × 32 = 23 GB used (internal calculation)
But displays as: 72% utilized (percentage) ✓
```

## Common Conversion Scenarios

### Scenario 1: Apache Web Server

```
SMD Feature #31 (Apache Requests):    0.65 normalized
Apache Max Capacity:                  2000 req/s
Dashboard shows:  0.65 × 2000 = 1,300 requests/sec

Status: Server at 65% capacity
Recommendation: Still room to scale
```

### Scenario 2: MySQL Database

```
SMD Feature #33 (MySQL Queries):      0.88 normalized
SMD Feature #34 (Slow Queries):       0.15 normalized
SMD Feature #35 (MySQL Connections):  0.92 normalized

Database Max QPS:    10,000 queries/sec
Max Connections:     100

Real Values:
├─ Queries/sec:      0.88 × 10,000 = 8,800 QPS
├─ Slow Queries:     0.15 = 15% of queries are slow
└─ Connections:      0.92 × 100 = 92 of 100 max

Status: DATABASE CRITICAL
- Running 88% of max queries
- 92% of max connections
- 15% are slow (performance issue)
Recommendation: Scale database or optimize queries
```

### Scenario 3: Memory Pressure

```
SMD Feature #6 (Memory):      0.95 normalized
Server Max RAM:               64 GB

Real Value: 0.95 × 64 = 60.8 GB of 64 GB used

Status: CRITICAL MEMORY PRESSURE
- Only 3.2 GB free (5%)
- System may start swapping to disk
- Performance will degrade
Recommendation: Urgent: Free memory or scale up
```

## Using Real Metrics in Your CSV

### Format Option A: Percentages (0-100)

```csv
cpu,memory,request_rate,error_rate
45.5,62.3,1200,0.5
```

Usage:
```bash
python load_sample_metrics.py --mode csv --file metrics.csv
# Loader expects 0-100 for cpu/memory, 0-1000+ for request_rate, 0-10 for error_rate
```

### Format Option B: Normalized (0-1)

```csv
cpu_norm,mem_norm,req_norm,err_norm
0.455,0.623,0.60,0.05
```

Usage: Convert back to real values before loading

### Format Option C: Real Values with Units

```csv
timestamp,cpu_percent,memory_gb,requests_per_sec,error_percent
2024-01-01 10:00:00,45.5,62.3,1200,0.5
2024-01-01 10:01:00,48.2,65.1,1250,0.6
```

Usage:
```bash
# Create script to normalize and load
python convert_and_load.py metrics_with_units.csv
```

## Verification: Are My Conversions Correct?

After loading data, check the dashboard:

1. **Values should match your input**
   - If you loaded CPU: 45.5% → Dashboard should show ~45.5%
   - If you loaded Memory: 62.3% → Dashboard should show ~62.3%

2. **Trends should make sense**
   - Increasing CPU → Requests spike (correlated)
   - Increasing Memory → No disk activity (data in RAM)
   - Increasing Disk Activity → No memory pressure (healthy)

3. **Ranges should be realistic**
   - CPU: 5-95% (not 0.05-0.95)
   - Memory: 20-90% (not 0.20-0.90)
   - Requests: 100-2000/s (not 0.5-1.0)
   - Errors: 0.1-5% (not 0.001-0.05)

---

For detailed SMD information: [SMD_DATASET_EXPLAINED.md](SMD_DATASET_EXPLAINED.md)  
For quick reference: [SMD_QUICK_REFERENCE.txt](SMD_QUICK_REFERENCE.txt)
