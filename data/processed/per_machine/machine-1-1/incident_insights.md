# Incident Insights — machine-1-1

Generated 2026-09-24 04:49:46 from 28,479 real telemetry readings (threshold 0.52).

**180 incidents triggered** across **1 distinct fault types**, in **10 separate burst(s)**.

## Severity Breakdown

- **High**: 180 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 180 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 180x)_
- Inspect cable connections _(recommended 180x)_
- Review network driver logs _(recommended 180x)_
- Monitor packet loss rate _(recommended 180x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 11948 | 11952 | 5 readings |
| 13398 | 13407 | 10 readings |
| 14827 | 14864 | 38 readings |
| 16266 | 16304 | 39 readings |
| 17710 | 17743 | 34 readings |
| 19140 | 19184 | 45 readings |
| 20584 | 20619 | 36 readings |
| 23491 | 23555 | 65 readings |
| 24920 | 24935 | 16 readings |
| 26378 | 26384 | 7 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._