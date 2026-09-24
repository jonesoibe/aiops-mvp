# Incident Insights — machine-2-9

Generated 2026-09-24 04:55:10 from 28,722 real telemetry readings (threshold 0.52).

**34 incidents triggered** across **1 distinct fault types**, in **12 separate burst(s)**.

## Severity Breakdown

- **High**: 34 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 34 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 34x)_
- Inspect cable connections _(recommended 34x)_
- Review network driver logs _(recommended 34x)_
- Monitor packet loss rate _(recommended 34x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 1892 | 1892 | 1 readings |
| 2355 | 2366 | 12 readings |
| 6647 | 6655 | 9 readings |
| 9182 | 9182 | 1 readings |
| 9835 | 9841 | 7 readings |
| 12159 | 12175 | 17 readings |
| 17799 | 17799 | 1 readings |
| 17860 | 17861 | 2 readings |
| 19233 | 19233 | 1 readings |
| 20684 | 20684 | 1 readings |
| 22082 | 22108 | 27 readings |
| 23552 | 23572 | 21 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._