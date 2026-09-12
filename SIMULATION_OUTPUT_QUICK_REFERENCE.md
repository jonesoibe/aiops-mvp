# Synchronized Simulation Output - Quick Reference

## 4 Tabs: Console | Metrics | Analysis | Anomalies

---

## 🖥️ CONSOLE TAB
**Real-time chaos injection logs synchronized with configuration**

```
Config Summary → Ramp-up Phase → Peak Phase → Ramp-down Phase → Completion
```

### What You See:
- Execution ID, chaos type, target service
- Duration breakdown (ramp-up/peak/ramp-down)
- Real-time logs of chaos activity
- Anomaly detection status
- Completion summary

### Example (CPU Spike, 70% intensity):
```
📋 SIMULATION CONFIGURATION:
  • Chaos Type: CPU SPIKE
  • Intensity: 70.0%
  • Duration: 60s

📈 RAMP-UP (5s):
  Ramping cpu_spike intensity to 14%...
  Ramping cpu_spike intensity to 28%...
  ... 70%

⚠️  PEAK (50s):
  [T+1s] CPU usage: 69.2%, context switches: 3421
  [T+2s] CPU usage: 71.5%, context switches: 4156
  ... (continues for 50s)

📉 RAMP-DOWN (5s):
  Reducing intensity to 56%...
  ... 0%

✅ SIMULATION COMPLETED
```

---

## 📊 METRICS TAB
**Time-series metrics synchronized with chaos type and intensity**

### Metrics Change by Chaos Type:

**CPU Spike:**
- CPU Usage: 25% → 95%
- Context Switches: 5K → 50K
- Thread Count: 80 → 500
- System Load: 2.5 → 32.0

**Memory Leak:**
- Memory Usage: 45% → 95%
- Memory Committed: 2GB → 8GB
- GC Pause Time: 50ms → 2s
- Heap Fragmentation: 15% → 85%

**Network Latency:**
- Latency: 5ms → 800ms
- Packet Loss: 0.1% → 25%
- Jitter: 2ms → 200ms
- Throughput: 5000 → 1000 req/s

**High Error Rate:**
- Error Rate: 0.1% → 50%
- Request Failures: 5 → 500/min
- Circuit Breaker Trips: 0 → 10/min
- P99 Response Time: 150ms → 8s

**Database Latency:**
- Query Latency: 10ms → 5s
- Slow Queries: 0 → 500/min
- Connection Pool: 40% → 100%
- Transaction Time: 100ms → 10s

**Cascading Failure:**
- Affected Services: 1 → 8
- Error Propagation: 0% → 100%
- Recovery Attempts: 0 → 5/min
- Cascade Depth: 1 → 5 hops

### Each Metric Shows:
```
METRIC NAME (in uppercase)
├── Min: 25.3 [unit]
├── Mean: 65.4 [unit]  ← Main value
└── Max: 94.8 [unit]
```

---

## 📈 ANALYSIS TAB
**Detailed analysis with model performance and recommendations**

### 5 Sections:

**1. Simulation Configuration**
- Exact parameters used
- Duration breakdown
- Intensity level

**2. Detection Results**
- Anomalies Detected: ~30 (based on duration × intensity)
- Detection Rate: 70-95% (70% baseline + 25% of intensity)
- False Positive Rate: 5-10% (10% baseline - 5% of intensity)
- Mean Anomaly Score: 0.45-0.90

**3. Affected Metrics**
Table showing: Metric | Baseline | Peak | Impact
```
cpu_usage        25.0%    95.0%    HIGH
memory_usage     45.0%    95.0%    HIGH
disk_io          150.0    2000.0   MEDIUM
```

**4. Model Performance**
```
Isolation Forest Score:  0.85-0.95
Classifier Accuracy:     85-98%
Precision:              82-96%
Recall:                 78-94%
F1 Score:               0.80-0.95
```

**5. Feature Importance** (Top 10)
```
1. cpu_usage              85%  ← Most important for CPU Spike
2. context_switches       78%
3. system_load           72%
4. memory_usage          20%
...
```

**6. Recommendations** (Chaos-Specific)
- Priority: Critical | High | Medium
- Action to take
- Description

**For CPU Spike:**
- 🔴 Scale horizontally
- 🔴 Optimize algorithms
- 🟠 Implement rate limiting
- 🟠 Monitor context switches

---

## 🚨 ANOMALIES TAB
**All detected anomalies with scores and classifications**

### Anomalies Change by Chaos Type:

**CPU Spike:** cpu_spike, high_system_load, thread_explosion
**Memory Leak:** memory_leak, heap_growth, gc_pause_elongation
**Network Latency:** network_latency, high_packet_loss, jitter_spike
**High Error Rate:** error_rate_spike, request_failure, timeout_surge
**Database Latency:** db_slow_query, connection_pool_exhaustion
**Cascading Failure:** cascade_start, service_correlation, propagation_detected

### Anomaly Table Columns:
```
ID      | Timestamp        | Type              | Severity | Score | Metric
--------|------------------|-------------------|----------|-------|----------
ANM_001 | 16:30:15         | cpu_spike         | 🔴 HIGH  | 0.854 | cpu_usage
ANM_002 | 16:30:28         | high_system_load  | 🟠 HIGH  | 0.762 | system_load
ANM_003 | 16:30:34         | thread_explosion  | 🟡 MED   | 0.643 | thread_count
```

### Severity Assignment:
- 🔴 **Critical** - Score > 0.8 (only at 80%+ intensity)
- 🟠 **High** - Score > 0.5 (typical for chaos)
- 🟡 **Medium** - Score ≤ 0.5 (lower intensity)

### Anomaly Count Formula:
```
anomalies = (duration / 3) * (0.5 + intensity)

Examples:
60s @ 50% intensity = 20 × 1.0 = 20 anomalies
60s @ 75% intensity = 20 × 1.25 = 25 anomalies
60s @ 100% intensity = 20 × 1.5 = 30 anomalies
```

---

## 🔧 CONFIGURATION PARAMETERS

### Basic
```javascript
chaos_type: "cpu_spike"           // 6 types available
intensity: 75                     // 0-100% (slider)
duration: 60                      // 10-300 seconds
```

### Advanced (Auto-calculated)
```javascript
ramp_up_time: 5          // Intensity ramps from 0% to 100%
peak_duration: 50        // Full chaos at configured intensity
ramp_down_time: 5        // Intensity ramps from 100% to 0%
```

### Service Target
```javascript
target_service: "api-gateway"    // Always api-gateway
```

---

## 📋 CHAOS TYPES & THEIR OUTPUTS

| Type | Key Metric | Baseline → Peak | Anomaly Types |
|------|-----------|-----------------|---------------|
| **CPU Spike** | CPU Usage | 25% → 95% | 3 types |
| **Memory Leak** | Memory % | 45% → 95% | 3 types |
| **Network Latency** | Latency | 5ms → 800ms | 3 types |
| **High Error Rate** | Error % | 0.1% → 50% | 3 types |
| **DB Latency** | Query ms | 10ms → 5s | 3 types |
| **Cascading Fail** | Services | 1 → 8 | 3 types |

---

## ⚡ QUICK START

1. **Configure:**
   - Select Chaos Type
   - Set Intensity (10-100%)
   - Set Duration (10-300s)

2. **Run:**
   - Click "▶️ Run Simulation"
   - Watch status badge turn "RUNNING"

3. **View Results (Wait 2-5 seconds):**
   - **Console Tab** - Watch logs in real-time
   - **Metrics Tab** - View affected metrics
   - **Analysis Tab** - Check performance & recommendations
   - **Anomalies Tab** - See all detected anomalies

---

## ✅ SYNCHRONIZATION EXAMPLES

### Example 1: CPU Spike @ 50% Intensity
```
Config:
  intensity: 50%
  duration: 60s

Results:
  CPU Usage: 25% → 60% (baseline + 50% of peak range)
  Anomalies: ~20 (60÷3 × 1.0)
  Detection Rate: 82.5% (70% + 25% of 50%)
  Feature Rank #1: cpu_usage (85%)
```

### Example 2: Memory Leak @ 80% Intensity
```
Config:
  intensity: 80%
  duration: 60s

Results:
  Memory: 45% → 85% (baseline + 80% of peak range)
  Anomalies: ~26 (60÷3 × 1.3)
  Detection Rate: 90% (70% + 25% of 80%)
  Feature Rank #1: memory_usage (88%)
```

### Example 3: Network Latency @ 30% Intensity
```
Config:
  intensity: 30%
  duration: 60s

Results:
  Latency: 5ms → 245ms (baseline + 30% of peak range)
  Anomalies: ~16 (60÷3 × 0.8)
  Detection Rate: 77.5% (70% + 25% of 30%)
  Feature Rank #1: network_latency (82%)
```

---

## 🎯 KEY FEATURES

✅ **Parameter-Synchronized** - Outputs match your config exactly  
✅ **Chaos-Specific Metrics** - Only relevant metrics per chaos type  
✅ **Realistic Anomalies** - Distributed throughout peak phase  
✅ **Intensity-Aware** - All values scale with intensity  
✅ **Time-Phased** - Ramp-up, peak, ramp-down reflected  
✅ **Actionable Recommendations** - Specific to chaos type  
✅ **Detailed Analysis** - Features, performance, classifications  
✅ **Real-Time Console** - Step-by-step log of what's happening  

---

## 🚀 STATUS: READY TO USE

All 4 tabs now display:
- ✅ **Console** - Granular injection logs
- ✅ **Metrics** - Chaos-specific time series
- ✅ **Analysis** - Model performance & recommendations
- ✅ **Anomalies** - Detailed anomaly records

**Configuration synchronization is complete!**

