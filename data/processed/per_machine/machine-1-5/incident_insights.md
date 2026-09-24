# Incident Insights — machine-1-5

Generated 2026-09-24 04:50:58 from 23,705 real telemetry readings (threshold 0.52).

**326 incidents triggered** across **1 distinct fault types**, in **13 separate burst(s)**.

## Severity Breakdown

- **High**: 326 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 326 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 326x)_
- Inspect cable connections _(recommended 326x)_
- Review network driver logs _(recommended 326x)_
- Monitor packet loss rate _(recommended 326x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 454 | 488 | 35 readings |
| 1878 | 1924 | 47 readings |
| 6204 | 6246 | 43 readings |
| 7650 | 7684 | 35 readings |
| 9098 | 9125 | 28 readings |
| 10534 | 10565 | 32 readings |
| 11928 | 12009 | 82 readings |
| 12234 | 12234 | 1 readings |
| 16292 | 16334 | 43 readings |
| 17724 | 17774 | 51 readings |
| 19167 | 19214 | 48 readings |
| 20599 | 20637 | 39 readings |
| 22049 | 22099 | 51 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._