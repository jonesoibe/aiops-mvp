# Incident Insights — machine-1-4

Generated 2026-09-24 04:50:40 from 23,706 real telemetry readings (threshold 0.52).

**49 incidents triggered** across **2 distinct fault types**, in **8 separate burst(s)**.

## Severity Breakdown

- **Critical**: 17 incidents
- **High**: 32 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 32 |
| Memory Pressure | Critical | 17 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 32x)_
- Inspect cable connections _(recommended 32x)_
- Review network driver logs _(recommended 32x)_
- Monitor packet loss rate _(recommended 32x)_
- Increase available memory _(recommended 17x)_
- Check for memory leaks _(recommended 17x)_
- Restart memory-heavy service _(recommended 17x)_
- Enable swap monitoring _(recommended 17x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 1754 | 1754 | 1 readings |
| 3186 | 3224 | 39 readings |
| 4662 | 4676 | 15 readings |
| 7488 | 7488 | 1 readings |
| 13286 | 13316 | 31 readings |
| 14745 | 14758 | 14 readings |
| 20957 | 20967 | 11 readings |
| 23358 | 23418 | 61 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._