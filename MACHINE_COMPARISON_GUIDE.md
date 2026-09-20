# Comparing Metrics Across 10 Different Machines

## What You're Loading

```
Machine 1: machine-1-1, machine-1-3, machine-1-5, machine-1-7  (4 time periods)
Machine 2: machine-2-2, machine-2-4, machine-2-6, machine-2-8  (4 time periods)
Machine 3: machine-3-3, machine-3-9                             (2 time periods)

Total: 10 files × 20,000 rows each = 200,000 rows of metrics
```

## What to Look For

### Performance Patterns

As metrics accumulate on the dashboard, you'll see patterns emerge:

```
CPU Usage trends:
├─ Machine 1: Typically lower utilization?
├─ Machine 2: Typically higher utilization?
└─ Machine 3: How does it compare?

Memory Usage patterns:
├─ Which machine runs "hot" (high memory)?
├─ Which has stable memory?
└─ Any memory pressure spikes?

Disk I/O differences:
├─ Which machine has heaviest I/O?
├─ Which is most I/O efficient?
└─ Any I/O bottlenecks?

Error patterns:
├─ Which machine has more errors?
├─ Are errors clustered in time?
└─ Correlation with high load?
```

## Time-Based Comparison

The files represent different time periods:

```
Period 1-2: Early morning (light load expected)
Period 3-4: Mid-morning (moderate load)
Period 5-6: Afternoon peak (high load)
Period 7-9: Evening (medium to heavy load)
Period 10-11: Night operations (variable)
```

### What You Might See

```
Machine 1, Period 1: Baseline normal operation
Machine 1, Period 7: Same machine under different load

Comparison:
├─ CPU rises with period (normal)
├─ Memory stays consistent (good management)
└─ Errors increase in peak hours (expected)
```

## Dashboard Analysis

### Real-Time Dashboard (http://localhost:5000)

With 200K rows loaded, the dashboard shows:
- **Summary**: Health percentage, metrics count, latest update time
- **Key System Metrics**: 6 cards showing current/avg metrics
- **Sparklines**: Visual trend indicators
- **Status Badges**: Color-coded health status

### What the Metrics Mean Across Machines

#### CPU Usage Comparison

```
Machine 1: Average 35-45% CPU
├─ Stable performance
├─ Good headroom
└─ Not constrained

Machine 2: Average 55-65% CPU
├─ Higher utilization
├─ Less headroom
└─ Monitor for spikes

Machine 3: Average 48-58% CPU
├─ Between Machines 1 & 2
├─ Balanced load
└─ Room to grow
```

#### Memory Usage Comparison

```
Machine 1: Average 60-70% RAM
├─ Healthy utilization
└─ No swapping expected

Machine 2: Average 75-85% RAM
├─ Approaching pressure
├─ May start swapping
└─ Monitor closely

Machine 3: Average 65-75% RAM
├─ Comfortable range
└─ Sustainable
```

#### Request Rate Comparison

```
Which machine handles more traffic?
├─ Machine 1: Lower req/s (less traffic)
├─ Machine 2: Higher req/s (more traffic)
└─ Machine 3: Moderate req/s

Performance under load:
├─ Low req/s + low CPU = Idle
├─ High req/s + low CPU = Efficient
├─ High req/s + high CPU = Under stress
└─ Low req/s + high CPU = Background tasks
```

#### Error Rate Comparison

```
Healthy baseline:
├─ 0.1-0.5% error rate = normal
├─ 0.5-1.0% = acceptable
└─ >1.0% = investigate

Comparing machines:
├─ Machine with lowest errors = most reliable
├─ Error spikes = check what happened at that time
└─ Correlation with load = performance issue
```

## Time Series Analysis

### Looking for Patterns

```
Hour-by-hour pattern (if data spans 24+ hours):

Early morning (data period 1-2):
├─ Low CPU
├─ Low memory
├─ Minimal errors
└─ Baseline healthy state

Mid-morning (period 3-4):
├─ CPU rises gradually
├─ Memory stable
├─ Error rate minimal
└─ Normal operations

Afternoon (period 5-6):
├─ Peak CPU usage
├─ High request rate
├─ Memory near limits
└─ Errors may increase

Evening (period 7-9):
├─ CPU returns to normal
├─ Memory releases
├─ Errors drop
└─ System stabilizes
```

## Machine Comparison Matrix

| Metric | Machine 1 | Machine 2 | Machine 3 | Notes |
|--------|-----------|-----------|-----------|-------|
| Avg CPU % | ? | ? | ? | Lower = more efficient |
| Peak CPU % | ? | ? | ? | Should be <85% |
| Avg Memory % | ? | ? | ? | <75% is healthy |
| Peak Memory % | ? | ? | ? | >90% is critical |
| Avg Disk I/O | ? | ? | ? | Lower = less contention |
| Error Rate % | ? | ? | ? | <0.5% is excellent |
| Request Rate/s | ? | ? | ? | Depends on purpose |
| Stability | ? | ? | ? | Low variance = stable |

*Fill this in after viewing the dashboard*

## Real-World Questions Answered

### "Which machine should I migrate workloads to?"

Look at:
1. **Available CPU headroom** - Which has lowest average CPU?
2. **Available memory** - Which has lowest average memory?
3. **Current workload** - Which handles lightest load?
4. **Reliability** - Which has lowest error rate?

**Decision**: Migrate to machine with best combination

### "Which machine needs performance tuning?"

Look for:
1. **High CPU with low request rate** - Background task overhead
2. **High memory with low request rate** - Memory leak possible
3. **High disk I/O with low request rate** - I/O inefficiency
4. **High error rate** - Application issue

**Action**: Optimize bottlenecked resource

### "Which machine is most reliable?"

Compare:
1. **Error rates** - Lower is more reliable
2. **Stability** - Less variance means more predictable
3. **Headroom** - Never hitting limits means safe
4. **Consistency** - Patterns should be repeatable

**Reliable = Low errors, stable, headroom, consistent**

### "Do machines share similar patterns?"

If all three machines show:
```
✓ Same CPU patterns → Synchronized workload (good)
✓ Same memory patterns → Consistent config (good)
✓ Same error patterns → Shared issue (needs investigation)
✗ Different patterns → Different workloads (expected)
```

## Anomalies to Watch For

### Unexpected Patterns

```
Machine suddenly drops to 0 metrics
└─ Service stopped or crash

CPU spikes without request increase
└─ Background process or backup

Memory spike without CPU increase
└─ Cache flush or data load

Error spike at specific time
└─ Scheduled process or deployment

One machine differs significantly
└─ Hardware issue or misconfiguration
```

## Performance Benchmarking

### Expected Results

```
Light Load (Early Morning):
├─ CPU: 5-20%
├─ Memory: 30-50%
└─ Errors: <0.1%

Moderate Load (Mid-day):
├─ CPU: 30-50%
├─ Memory: 50-70%
└─ Errors: 0.2-0.5%

Peak Load (Afternoon):
├─ CPU: 50-80%
├─ Memory: 60-85%
└─ Errors: 0.5-1.0%

After Hours (Evening):
├─ CPU: 20-40%
├─ Memory: 40-60%
└─ Errors: 0.1-0.3%
```

### Comparing Against These

If your machines show:
- **Higher than expected** → Overutilized, needs scaling
- **Lower than expected** → Underutilized, could consolidate
- **Outside ranges** → Investigate anomaly

## Advanced Comparison

### Correlation Analysis

Watch for:

```
High CPU + High Requests + Low Errors
└─ Healthy under load (good scaling)

High CPU + Low Requests + High Errors
└─ Inefficient code or misconfiguration (bad)

Low CPU + High Requests
└─ Very efficient (best case)

Memory constant regardless of load
└─ Well-managed memory (good)

Memory spikes with load
└─ Possible memory leak (investigate)
```

### Machine Capacity Planning

```
Machine 1 headroom: 100% - Current_Avg → Can handle X% more load
Machine 2 headroom: 100% - Current_Avg → Can handle Y% more load
Machine 3 headroom: 100% - Current_Avg → Can handle Z% more load

Prioritize load to machine with most headroom
```

## Dashboard Tips with 200K Rows

### Viewing Trends

With 200K rows loaded:
- **Sparkline charts** show ~6 hours of trends
- **Color changes** indicate crossing thresholds
- **Updates every 5 seconds** show new data arriving

### Finding Peak Times

1. Look at sparkline peaks
2. Note the timestamp when peaks occur
3. Correlate with time period files loaded

### Identifying Outliers

1. One metric much higher than others = outlier
2. Check if correlates with load increase
3. Investigate if not correlating with workload

## Comparing 10 Machines at a Glance

After dashboard loads all data:

```
CPU Usage:  |-----|-----| (Range across all machines)
Memory:     |--------|--| (Range across all machines)
Disk I/O:   |--|-------|  (Range across all machines)
Errors:     |--|------|-| (Range across all machines)

Wider range = More diversity
Narrow range = Similar machines
Outliers = Investigate
```

## Next Analysis Steps

1. **View the dashboard** - Let metrics update for 5 minutes
2. **Take screenshots** - Document baseline patterns
3. **Identify outliers** - Which machine differs?
4. **Find correlations** - What metrics move together?
5. **Plan capacity** - Where should new workloads go?
6. **Optimize** - Which machine needs tuning?

---

**Current Status**: Loading 200,000 rows from 10 machines  
**Expected Time**: 3-5 minutes (fast injection mode)  
**View Results**: http://localhost:5000 (refresh after loading)
