# Incident Insights — machine-3-9

Generated 2026-09-24 04:57:21 from 28,713 real telemetry readings (threshold 0.52).

**115 incidents triggered** across **1 distinct fault types**, in **19 separate burst(s)**.

## Severity Breakdown

- **High**: 115 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 115 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 115x)_
- Inspect cable connections _(recommended 115x)_
- Review network driver logs _(recommended 115x)_
- Monitor packet loss rate _(recommended 115x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 331 | 401 | 71 readings |
| 1780 | 1841 | 62 readings |
| 3220 | 3281 | 62 readings |
| 4712 | 4720 | 9 readings |
| 6120 | 6161 | 42 readings |
| 7591 | 7601 | 11 readings |
| 9000 | 9033 | 34 readings |
| 10439 | 10472 | 34 readings |
| 11879 | 11919 | 41 readings |
| 13299 | 13361 | 63 readings |
| 14759 | 14801 | 43 readings |
| 16199 | 16232 | 34 readings |
| 17639 | 17639 | 1 readings |
| 19109 | 19110 | 2 readings |
| 20519 | 20520 | 2 readings |
| 21989 | 21991 | 3 readings |
| 23399 | 23431 | 33 readings |
| 24869 | 24872 | 4 readings |
| 27719 | 27759 | 41 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._