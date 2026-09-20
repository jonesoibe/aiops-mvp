# Analyzing 10 Machines: Complete Comparison Guide

## What You're Comparing

### The 10 Machines Being Loaded

```
MACHINE 1 (4 time periods):
├─ machine-1-1.txt  (Period 1)  20,000 rows
├─ machine-1-3.txt  (Period 3)  20,000 rows
├─ machine-1-5.txt  (Period 5)  20,000 rows
└─ machine-1-7.txt  (Period 7)  20,000 rows
   Subtotal: 80,000 rows

MACHINE 2 (4 time periods):
├─ machine-2-2.txt  (Period 2)  20,000 rows
├─ machine-2-4.txt  (Period 4)  20,000 rows
├─ machine-2-6.txt  (Period 6)  20,000 rows
└─ machine-2-8.txt  (Period 8)  20,000 rows
   Subtotal: 80,000 rows

MACHINE 3 (2 time periods):
├─ machine-3-3.txt  (Period 3)  20,000 rows
└─ machine-3-9.txt  (Period 9)  20,000 rows
   Subtotal: 40,000 rows

TOTAL: 200,000 rows across 10 files
```

## Time Period Analysis

### Understanding the Periods

Each period represents ~333 hours (2 weeks) of data:
```
20,000 rows × 1 minute per row = 20,000 minutes
20,000 minutes ÷ 60 = 333 hours  
333 hours ÷ 24 = ~14 days per file
```

### Comparing Time Periods

```
Period 1:  machine-1-1.txt   (early Sept 2016)
Period 2:  machine-2-2.txt   (few days later)
Period 3:  machine-1-3.txt, machine-3-3.txt (early Sept)
Period 4:  machine-2-4.txt   (mid Sept)
Period 5:  machine-1-5.txt   (mid Sept)
Period 6:  machine-2-6.txt   (late Sept)
Period 7:  machine-1-7.txt   (late Sept)
Period 8:  machine-2-8.txt   (late Sept)
Period 9:  machine-3-9.txt   (early Oct)
Period 11: machine-2-8.txt   (mid Oct, baseline)
```

### What Changed Over Time

```
Early September (Periods 1-3):
├─ Period 1: Machine 1 baseline
├─ Period 2: Machine 2 baseline  
└─ Period 3: Both running normally

Mid September (Periods 4-5):
├─ Period 4: Machine 2 continues
├─ Period 5: Machine 1 steady
└─ Expectation: Consistent metrics

Late September (Periods 6-7):
├─ Period 6: Machine 2
├─ Period 7: Machine 1
└─ Longer timeframe, may see degradation or anomalies

Early October (Periods 8-9):
├─ Period 8: Machine 2 later in month
├─ Period 9: Machine 3 new period
└─ Seasonal or month-end effects?
```

## Performance Characteristics by Machine

### Machine 1 vs Machine 2 vs Machine 3

Expected differences:

```
MACHINE 1:
├─ Purpose: ? (need to analyze)
├─ Load pattern: ? (need to observe)
├─ Resource utilization: ? (need to measure)
└─ Reliability: ? (error patterns unknown)

MACHINE 2:
├─ Purpose: ? (need to analyze)
├─ Load pattern: ? (need to observe)
├─ Resource utilization: ? (need to measure)
└─ Reliability: ? (error patterns unknown)

MACHINE 3:
├─ Purpose: ? (need to analyze)
├─ Load pattern: ? (need to observe)
├─ Resource utilization: ? (need to measure)
└─ Reliability: ? (error patterns unknown)
```

## Key Metrics to Compare

### 1. CPU Usage Across Machines

```
Average CPU by Machine:
┌─ Machine 1: ___% (baseline)
├─ Machine 2: ___% (compare)
└─ Machine 3: ___% (compare)

Peak CPU by Machine:
┌─ Machine 1: ___% (max stress)
├─ Machine 2: ___% (max stress)
└─ Machine 3: ___% (max stress)

Interpretation:
├─ Higher avg = busier machine
├─ Higher peaks = handling spikes
├─ Consistency = stable workload
└─ Variance = variable load
```

### 2. Memory Usage Comparison

```
Average Memory by Machine:
┌─ Machine 1: ___% (typical)
├─ Machine 2: ___% (typical)
└─ Machine 3: ___% (typical)

Peak Memory by Machine:
┌─ Machine 1: ___% (peak)
├─ Machine 2: ___% (peak)
└─ Machine 3: ___% (peak)

Low Memory Watermark:
┌─ Machine 1: ___% (low point)
├─ Machine 2: ___% (low point)
└─ Machine 3: ___% (low point)

Analysis:
├─ Constant memory = leaking?
├─ Rising memory = load growth
├─ Stable memory = good management
└─ Free memory = headroom available
```

### 3. Disk I/O Performance

```
Average Disk Utilization:
┌─ Machine 1: ___% 
├─ Machine 2: ___% 
└─ Machine 3: ___% 

Peak Disk Utilization:
┌─ Machine 1: ___% 
├─ Machine 2: ___% 
└─ Machine 3: ___% 

Interpretation:
├─ High disk = I/O bottleneck
├─ Variable disk = bursty workload
├─ Stable disk = steady I/O
└─ Low disk = memory-resident data
```

### 4. Error Rates Comparison

```
Average Error Rate:
┌─ Machine 1: ___% (reliability metric)
├─ Machine 2: ___% (reliability metric)
└─ Machine 3: ___% (reliability metric)

Peak Error Rate:
┌─ Machine 1: ___% (stress point)
├─ Machine 2: ___% (stress point)
└─ Machine 3: ___% (stress point)

Analysis:
├─ 0% errors = perfect (rare)
├─ <0.5% = excellent
├─ 0.5-1% = acceptable
├─ >1% = investigate
└─ Spikes = anomalies
```

## Correlation Analysis

### Metrics That Move Together

```
CPU + Memory:
├─ Both rise = application load ✓
├─ CPU high, Memory low = background tasks
└─ Memory high, CPU low = memory leak?

CPU + Requests:
├─ Both rise = normal scaling ✓
├─ Requests high, CPU low = efficient code
└─ CPU high, Requests low = overhead

CPU + Errors:
├─ Both rise = under stress
├─ CPU high, Errors low = handling well ✓
└─ Errors without CPU = odd behavior

Memory + Disk I/O:
├─ Both high = memory swapping (bad)
├─ Memory high, Disk low = good caching ✓
└─ Disk high, Memory low = I/O intensive
```

## Identifying Anomalies

### Red Flags to Look For

```
1. CPU Spikes Without Load
   ├─ What: High CPU, low request rate
   ├─ Cause: Background processes, backups, cron jobs
   └─ Action: Investigate at timestamps when spikes occur

2. Memory Constantly Increasing
   ├─ What: Memory usage trending upward
   ├─ Cause: Memory leak in application
   └─ Action: Restart process, analyze code

3. High Errors at Low Load
   ├─ What: Error rate > 0.5% with low CPU
   ├─ Cause: Configuration issue, connection limit
   └─ Action: Check logs for error messages

4. One Machine Different from Others
   ├─ What: Machine A shows pattern others don't
   ├─ Cause: Different hardware, config, or workload
   └─ Action: Investigate differences

5. Synchronized Spikes Across Machines
   ├─ What: All 3 machines spike at same time
   ├─ Cause: External event, network issue, deployment
   └─ Action: Check if correlated with system event

6. Degradation Over Time
   ├─ What: Metrics worsen in later periods
   ├─ Cause: Resource exhaustion, accumulation
   └─ Action: Monitor for eventual failure

7. Inconsistent Patterns
   ├─ What: Machine behaves erratically
   ├─ Cause: Intermittent issue, race condition
   └─ Action: Collect detailed logs during occurrence
```

## Dashboard Navigation Tips

### With 200K Rows Loaded

```
Dashboard View Features:
├─ Sparkline charts show ~7 days of trend
├─ 5-second refresh rate shows new data
├─ Color changes indicate status transitions
├─ Metric cards show current + average
└─ Updates accumulate over time

To Compare Machines:
1. Load data sequentially (already done)
2. Refresh dashboard (Ctrl+R)
3. Watch patterns over 5-10 minutes
4. Screenshot key insights
5. Note timestamps of anomalies
```

### Finding Specific Metrics

```
Dashboard Metrics Available:
├─ CPU Usage (current + trend)
├─ Memory Usage (current + trend)
├─ Disk Usage (current + trend)
├─ Network I/O (current + trend)
├─ Request Rate (current + trend)
├─ Error Rate (current + trend)
└─ Active Anomalies (detected issues)
```

## Spreadsheet: Fill In As You Analyze

```
Metric              Machine 1   Machine 2   Machine 3   Best Performance
─────────────────────────────────────────────────────────────────────────
Avg CPU %           _____       _____       _____       Lowest is best
Peak CPU %          _____       _____       _____       Lowest is best
Avg Memory %        _____       _____       _____       Stable is best
Peak Memory %       _____       _____       _____       Under 80%
Avg Error Rate %    _____       _____       _____       Lowest is best
Peak Error Rate %   _____       _____       _____       Lowest is best
Disk I/O Peak %     _____       _____       _____       Lowest is best
Request Rate Avg    _____       _____       _____       Depends on purpose
Memory Stability    _____       _____       _____       Low variance
CPU Stability       _____       _____       _____       Low variance
─────────────────────────────────────────────────────────────────────────
Overall Rating      _____/10    _____/10    _____/10    See winner below
Recommendation      ?           ?           ?           Choose best
```

## Analysis Workflow

### Step 1: Load Data (In Progress)
```
[✓] Load 20K rows from machine-1-1.txt
[✓] Load 20K rows from machine-1-3.txt
[✓] Load 20K rows from machine-1-5.txt
[✓] Load 20K rows from machine-1-7.txt
[✓] Load 20K rows from machine-2-2.txt
[✓] Load 20K rows from machine-2-4.txt
[✓] Load 20K rows from machine-2-6.txt
[✓] Load 20K rows from machine-2-8.txt
[✓] Load 20K rows from machine-3-3.txt
[✓] Load 20K rows from machine-3-9.txt
Total: 200,000 rows
```

### Step 2: View Dashboard
```
1. Open http://localhost:5000
2. Refresh page (Ctrl+R)
3. Wait 5-10 seconds for metrics to load
4. Observe sparkline charts forming
```

### Step 3: Identify Patterns
```
1. Note CPU range across all machines
2. Note Memory range across all machines
3. Look for synchronized peaks
4. Identify which machine is busiest
5. Identify which machine is most reliable
```

### Step 4: Deep Dive Analysis
```
1. Focus on high CPU periods
2. Correlate with request rate
3. Check error rate at peaks
4. Look for memory leaks (rising trend)
5. Check for disk I/O bottlenecks
```

### Step 5: Make Recommendations
```
1. Which machine handles most load? → Machine X
2. Which machine is most reliable? → Machine Y
3. Which needs optimization? → Machine Z
4. Which should be primary? → Machine X
5. Which is backup-ready? → Machine Y
```

## Example Findings (To Look For)

```
Finding 1: "Machine 2 has 20% higher CPU than Machine 1"
Interpretation: Machine 2 handles more workload or is less efficient
Action: Investigate if intentional or needs tuning

Finding 2: "Machine 3 has lower error rate than 1 and 2"
Interpretation: Machine 3 is more reliable or less loaded
Action: Consider as primary system

Finding 3: "All machines spike at same time"
Interpretation: External event (peak hours, deployment, etc.)
Action: Check system logs for correlation

Finding 4: "Machine 1 memory trend is rising"
Interpretation: Possible memory leak
Action: Monitor closely, plan for restart

Finding 5: "Machine 2 disk I/O is 3x higher than others"
Interpretation: More I/O intensive workload
Action: Ensure sufficient disk performance, check for disk errors
```

## Next Steps After Analysis

1. **Document findings** - Screenshots + notes
2. **Identify root causes** - Why differences exist
3. **Plan optimization** - What to tune on each machine
4. **Set baselines** - Expected normal ranges
5. **Create alerts** - Threshold values for each machine
6. **Schedule monitoring** - Continuous oversight
7. **Plan capacity** - Growth projections
8. **Test failover** - Can Machine Y replace Machine X?

---

**Current Task**: Loading 200,000 rows from 10 different machines  
**Expected Completion**: ~5-10 minutes  
**Next**: View at http://localhost:5000 and compare patterns  
**Guide**: Use [MACHINE_COMPARISON_GUIDE.md](MACHINE_COMPARISON_GUIDE.md) for interpretation
