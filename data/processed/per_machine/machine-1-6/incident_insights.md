# Incident Insights — machine-1-6

Generated 2026-09-24 04:51:19 from 23,688 real telemetry readings (threshold 0.52).

**96 incidents triggered** across **2 distinct fault types**, in **18 separate burst(s)**.

## Severity Breakdown

- **Critical**: 4 incidents
- **High**: 92 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 92 |
| Memory Pressure | Critical | 4 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 92x)_
- Inspect cable connections _(recommended 92x)_
- Review network driver logs _(recommended 92x)_
- Monitor packet loss rate _(recommended 92x)_
- Increase available memory _(recommended 4x)_
- Check for memory leaks _(recommended 4x)_
- Restart memory-heavy service _(recommended 4x)_
- Enable swap monitoring _(recommended 4x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 378 | 405 | 28 readings |
| 1319 | 1319 | 1 readings |
| 1829 | 1829 | 1 readings |
| 2742 | 2743 | 2 readings |
| 2931 | 2951 | 21 readings |
| 3293 | 3326 | 34 readings |
| 4673 | 4673 | 1 readings |
| 5633 | 5640 | 8 readings |
| 8995 | 9015 | 21 readings |
| 10428 | 10433 | 6 readings |
| 11871 | 11890 | 20 readings |
| 13316 | 13345 | 30 readings |
| 16190 | 16231 | 42 readings |
| 18584 | 18584 | 1 readings |
| 19075 | 19093 | 19 readings |
| 20534 | 20551 | 18 readings |
| 21976 | 21976 | 1 readings |
| 23392 | 23394 | 3 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._