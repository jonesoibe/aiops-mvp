# AIOps Platform - Implementation Formulas & Calculations

## 📐 Complete Formula Reference

All mathematical formulas, calculations, and algorithms used throughout the AIOps monitoring system.

---

## 🏗️ Service Topology Formulas

### 1. Inter-Service Latency Calculation

**Base Latency Formula:**
```
latency = base_latency × variance_factor
```

Where:
- `base_latency` = target service's latency + tier adjustment
- `variance_factor` = random.uniform(0.8, 1.2) [±20% variance]

**Tier-Based Latency Adjustment:**
```
if source.tier == FRONTEND:
    base_latency = target.latency_ms + random.uniform(50, 100)
    
elif source.tier == API_GATEWAY:
    base_latency = target.latency_ms + random.uniform(10, 30)
    
else:
    base_latency = target.latency_ms
```

**Example:**
```
Payment Service → Stripe (External)
base_latency = 250.5 + 0 = 250.5ms
variance = 250.5 × 1.02 = 255.51ms (final latency)
```

### 2. Error Rate Propagation Formula

**Composite Error Rate:**
```
error_rate = (source.error_rate + target.error_rate) / 2 × variance_factor
```

Where:
- `source.error_rate` = source service error percentage
- `target.error_rate` = target service error percentage
- `variance_factor` = random.uniform(0.5, 1.5) [0.5x to 1.5x variance]
- Final: `min(error_rate, 0.5)` [capped at 50%]

**Example:**
```
Order Service (0.22%) → Order DB (0.15%)
error_rate = (0.22 + 0.15) / 2 = 0.185%
with variance: 0.185 × 1.2 = 0.222% ≈ 0.22%
```

### 3. Throughput Calculation

**Constrained Throughput:**
```
throughput = min(source.throughput_rps, target.throughput_rps) × utilization_factor
```

Where:
- `min()` = bottleneck principle (minimum of source and target)
- `utilization_factor` = random.uniform(0.3, 0.8) [30-80% utilization]

**Example:**
```
API Gateway (4300 RPS) → User Service (1200 RPS)
throughput = min(4300, 1200) × 0.65 = 780 RPS
```

### 4. System-Wide Aggregations

**Total System Throughput:**
```
total_throughput = Σ(all_service.throughput_rps)
```

**Average Latency:**
```
avg_latency = Σ(all_service.latency_ms) / count(services)
```

**Average Error Rate:**
```
avg_error_rate = Σ(all_service.error_rate) / count(services)
```

**Example Results:**
```
17 Services Total
total_throughput = 2500 + 1800 + 4300 + ... = 40,950 RPS
avg_latency = (45.2 + 52.5 + 28.3 + ... + 250.5) / 17 = 63.86 ms
avg_error_rate = (0.1 + 0.15 + 0.08 + ... + 0.005) / 17 = 0.062%
```

### 5. Health Status Determination

**Health Classification Logic:**
```
if latency > 200ms:
    health = CRITICAL

elif error_rate > 0.20% OR latency > 150ms:
    health = DEGRADED
    
else:
    health = HEALTHY
```

**Example:**
```
Order Service: latency=125.4ms, error_rate=0.22%
Since error_rate (0.22%) > 0.20%, health = DEGRADED

Order DB: latency=245.8ms, error_rate=0.15%
Since latency (245.8ms) > 200ms, health = CRITICAL
```

---

## 📊 Audit Trail Formulas

### 1. Success Rate Calculation

**Success Rate Percentage:**
```
success_rate = (success_count / total_count) × 100
```

Where:
- `success_count` = sum(1 for entry if entry['status'] == 'success')
- `total_count` = len(all_entries)

**Formula:**
```python
success_count = sum(1 for e in entries if e['status'] == 'success')
failure_count = sum(1 for e in entries if e['status'] == 'failure')
warning_count = sum(1 for e in entries if e['status'] == 'warning')

total = success_count + failure_count + warning_count

success_rate = (success_count / total) × 100 if total > 0 else 0
failure_rate = (failure_count / total) × 100 if total > 0 else 0
warning_rate = (warning_count / total) × 100 if total > 0 else 0
```

**Example (144 Demo Entries):**
```
Success entries: 144
Total entries: 144
Success rate = (144 / 144) × 100 = 100.0%
Failure rate = (0 / 144) × 100 = 0.0%
```

### 2. Active Users Count

**Unique User Count:**
```
active_users = count(unique user_ids in audit log)
```

**Formula:**
```python
unique_users = len(set(e['user_id'] for e in entries))
```

**Example:**
```
Users in demo data: {admin, operator, viewer}
Active users = 3
```

### 3. Audit Entry Aggregations

**Entries by Action Type:**
```
action_count[action] = sum(1 for e in entries if e['action'] == action)
```

**Entries by Resource Type:**
```
resource_count[resource] = sum(1 for e in entries if e['resource'] == resource)
```

---

## 📈 Error Analysis Formulas

### 1. Error Rate Over Time

**Time Window Error Rate:**
```
error_rate(time_window) = (errors_in_window / requests_in_window) × 100
```

Where:
- `errors_in_window` = count of errors in time range
- `requests_in_window` = total requests in time range

**Implementation:**
```python
timeline = []
for time_point in time_range:
    errors = random.randint(20, 100)
    rate = (errors / 500) × 100  # Assuming 500 RPS baseline
    timeline.append({
        'timestamp': time_point,
        'errors': errors,
        'rate': rate
    })
```

### 2. Error Type Distribution

**Type Percentage Calculation:**
```
type_percentage = (type_count / total_errors) × 100
```

**Error Type Breakdown (Demo):**
```
Timeout:              (count × 36%) of total
Connection Error:     (count × 27%) of total
Authentication:       (count × 22%) of total
Rate Limited:         (count × 15%) of total
```

### 3. Aggregate Error Statistics

**Total Errors in Period:**
```
total_errors = Σ(errors in all time windows)
```

**Average Error Rate:**
```
avg_error_rate = Σ(all rates) / count(time_windows)
```

**Peak Error Rate:**
```
peak_error_rate = max(all rates in period)
```

**Example:**
```
Period: Last 24 hours
Total errors: 2,400
Total requests: 40,000
Average error rate = (2,400 / 40,000) × 100 = 6.0%
Peak error rate = 12.5%
```

### 4. Error Activity Heatmap

**Heatmap Cell Calculation:**
```
heatmap[hour][intensity] = count(errors during that hour)
```

Where:
- `hour` = 0-23 (24-hour format)
- `intensity` = color based on error density

---

## 💡 Chaos Simulation Formulas

### 1. Ramp-Up Phase Scaling

**Linear Ramp-Up:**
```
intensity_at_t = (t / ramp_up_time) × target_intensity
```

Where:
- `t` = current time in ramp-up phase
- `ramp_up_time` = duration of ramp-up (seconds)
- `target_intensity` = desired peak intensity (0.0-1.0)

**Example:**
```
Ramp-up time: 5 seconds
Target intensity: 0.7
At t=2.5s: intensity = (2.5 / 5) × 0.7 = 0.35 (50% of peak)
```

### 2. CPU Spike Injection

**CPU Usage During Spike:**
```
cpu_value = baseline_cpu + (intensity × random.uniform(15, 40))
```

Where:
- `baseline_cpu` = normal CPU usage
- `intensity` = chaos intensity multiplier (0.0-1.0)

**Example:**
```
Baseline: 20% CPU
Intensity: 0.7
Spike: 20 + (0.7 × 30) = 20 + 21 = 41% CPU
```

### 3. Memory Leak Injection

**Memory Usage Over Time:**
```
memory = baseline_memory + (elapsed_time × leak_rate × intensity)
```

Where:
- `baseline_memory` = initial memory usage
- `leak_rate` = MB per second leaked
- `elapsed_time` = seconds since injection started

**Example:**
```
Baseline: 512 MB
Leak rate: 2 MB/sec
Intensity: 0.8
After 30 seconds: 512 + (30 × 2 × 0.8) = 512 + 48 = 560 MB
```

### 4. Network Latency Injection

**Latency with Random Jitter:**
```
latency = baseline_latency + (intensity × random.uniform(100, 500)) + jitter
jitter = random.gauss(0, 5)  # Gaussian noise
```

**Example:**
```
Baseline: 50ms
Intensity: 0.7
Injected: 50 + (0.7 × 300) + N(0,5) = 50 + 210 + 3 = 263ms
```

### 5. Error Rate Injection

**High Error Rate:**
```
error_rate = baseline_error_rate + (intensity × random.uniform(2, 5))
error_rate = min(error_rate, 10%)  # Cap at 10%
```

**Normal Variation:**
```
error_rate = baseline_error_rate + random.gauss(0, 0.1)
error_rate = max(0, min(1, error_rate))  # Bound to [0,1]%
```

---

## 🎯 Dashboard Metrics Formulas

### 1. Service Health Summary

**Health Distribution:**
```
healthy_count = sum(1 for s in services if s.health == 'healthy')
warning_count = sum(1 for s in services if s.health == 'degraded')
critical_count = sum(1 for s in services if s.health == 'critical')

healthy_pct = (healthy_count / total_services) × 100
warning_pct = (warning_count / total_services) × 100
critical_pct = (critical_count / total_services) × 100
```

**Example:**
```
15 healthy + 1 degraded + 1 critical = 17 total
Healthy: (15/17) × 100 = 88.2%
Degraded: (1/17) × 100 = 5.9%
Critical: (1/17) × 100 = 5.9%
```

### 2. Request Rate Calculation

**Requests Per Second (RPS):**
```
request_rate = Σ(all_service.throughput_rps)
```

**Average Response Time:**
```
response_time = Σ(all_service.latency_ms) / count(services)
```

### 3. Error Rate Summary

**System-Wide Error Rate:**
```
error_rate = Σ(all_errors) / Σ(all_requests) × 100
```

**Per-Service Error Rate:**
```
service_error_rate = service.error_rate
```

---

## 🔢 Data Size Calculations

### 1. Memory Footprint Estimation

**Service Record Size:**
```
size_per_service ≈ (11 fields × 8 bytes) + string overhead ≈ 500 bytes
total_services_size = 17 × 500 bytes ≈ 8.5 KB
```

**Dependency Record Size:**
```
size_per_dependency ≈ (7 fields × 8 bytes) + string overhead ≈ 200 bytes
total_dependencies_size = 21 × 200 bytes ≈ 4.2 KB
```

**Audit Entry Size:**
```
size_per_entry ≈ (8 fields × 8 bytes) + JSON overhead ≈ 500 bytes
total_audit_size = 144 × 500 bytes ≈ 72 KB
```

### 2. File Rotation Sizing

**Log File Rotation:**
```
max_file_size = 10 MB
backup_count = 10
total_possible_logs = 10 MB × (1 + 10 backups) = 110 MB per log type
total_system_logs = 110 MB × 4 log types = 440 MB maximum
```

### 3. Cache Capacity

**In-Memory Cache Limit:**
```
max_cache_entries = 1000
avg_entry_size = 0.5 KB
cache_capacity = 1000 × 0.5 KB = 500 KB maximum
```

---

## 📊 Statistical Formulas

### 1. Percentile Calculations

**P95 Latency (95th Percentile):**
```
P95 = sorted_latencies[ceil(0.95 × N)]
```

Where N = total number of measurements

**Example:**
```
Latencies: [20, 25, 30, 35, 40, 45, 50, 55, 60, 100]
P95 = latencies[ceil(0.95 × 10)] = latencies[9] = 100ms
```

### 2. Standard Deviation (Variance)

**Latency Variance:**
```
σ = sqrt(Σ((x - mean)²) / N)
```

Where:
- `x` = individual latency measurement
- `mean` = average latency
- `N` = count of measurements

### 3. Correlation Formulas

**Service-to-Error Correlation:**
```
correlation = Σ((service_latency - avg_latency) × (error_rate - avg_error)) 
            / sqrt(var(latencies) × var(error_rates))
```

---

## 🔄 Dependency Path Calculations

### 1. Cumulative Latency

**End-to-End Latency (Multi-hop):**
```
e2e_latency = Σ(latency for each hop in path)
```

**Example:**
```
Path: Web UI → API Gateway → User Service → User DB
= 102.33 + 28.3 + 35.8 + 3.2 = 169.63 ms
```

### 2. Compound Error Rate (Series)

**Cascading Error Probability:**
```
P(total_error) = 1 - Π(1 - P(hop_error))
```

Where Π = product of all hop error probabilities

**Example:**
```
Path with 3 hops, each with 1% error rate:
P(total_error) = 1 - (0.99 × 0.99 × 0.99) = 1 - 0.9703 = 0.0297 ≈ 3%
```

### 3. Critical Path Analysis

**Slowest Path Identification:**
```
critical_path = path_with_max(cumulative_latency)
```

---

## 📈 Time-Series Formulas

### 1. Moving Average

**Simple Moving Average (SMA):**
```
SMA[t] = Σ(values from t-window to t) / window_size
```

### 2. Exponential Moving Average (EMA)

**EMA with Alpha:**
```
EMA[t] = α × value[t] + (1 - α) × EMA[t-1]
```

Where `α = 2 / (window_size + 1)`

### 3. Trend Detection

**Linear Trend:**
```
slope = (N × Σ(xy) - Σ(x) × Σ(y)) / (N × Σ(x²) - (Σ(x))²)
```

Where:
- `x` = time index
- `y` = metric value
- `N` = number of points

---

## 🎯 Summary of Key Metrics

| Metric | Formula | Example |
|--------|---------|---------|
| **Request Rate** | Σ(throughput_rps) | 40,950 RPS |
| **Avg Latency** | Σ(latency) / count | 63.86 ms |
| **Avg Error Rate** | Σ(error_rate) / count | 0.062% |
| **Success Rate** | (success / total) × 100 | 100.0% |
| **P95 Latency** | 95th percentile | ~180 ms |
| **Health Score** | (healthy / total) × 100 | 88.2% |
| **Dependency Chain Latency** | Σ(hop latencies) | 169.63 ms |
| **Service Availability** | uptime / (uptime + downtime) | 99.95% |

---

## 🔐 Implementation Notes

1. **Randomization**: All formulas use `random.uniform()` or `random.gauss()` for realistic variance
2. **Capping**: Error rates are capped at 50% to prevent unrealistic values
3. **Bottleneck Principle**: Throughput is constrained by minimum of source/target
4. **Tier Correlation**: Latency increases are based on service tiers
5. **Fault Propagation**: Errors cascade through dependency chains
6. **Time Windows**: Analysis supports 1h, 6h, 24h, 7d granularity

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-07  
**Applicable To**: AIOps Platform v1.0 (17 services, 21 dependencies)
