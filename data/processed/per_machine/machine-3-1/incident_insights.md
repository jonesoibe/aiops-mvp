# Incident Insights — machine-3-1

Generated 2026-09-24 04:55:27 from 28,700 real telemetry readings (threshold 0.52).

**78 incidents triggered** across **1 distinct fault types**, in **17 separate burst(s)**.

## Severity Breakdown

- **High**: 78 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 78 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 78x)_
- Inspect cable connections _(recommended 78x)_
- Review network driver logs _(recommended 78x)_
- Monitor packet loss rate _(recommended 78x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 340 | 401 | 62 readings |
| 1781 | 1841 | 61 readings |
| 3220 | 3281 | 62 readings |
| 4682 | 4712 | 31 readings |
| 6152 | 6153 | 2 readings |
| 7561 | 7600 | 40 readings |
| 9031 | 9041 | 11 readings |
| 10440 | 10472 | 33 readings |
| 11880 | 11912 | 33 readings |
| 13301 | 13362 | 62 readings |
| 14740 | 14800 | 61 readings |
| 16200 | 16241 | 42 readings |
| 17672 | 17672 | 1 readings |
| 20551 | 20552 | 2 readings |
| 24840 | 24840 | 1 readings |
| 26311 | 26311 | 1 readings |
| 27720 | 27720 | 1 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._