# Incident Insights — machine-2-2

Generated 2026-09-24 04:52:49 from 23,699 real telemetry readings (threshold 0.52).

**10 incidents triggered** across **1 distinct fault types**, in **6 separate burst(s)**.

## Severity Breakdown

- **High**: 10 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 10 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 10x)_
- Inspect cable connections _(recommended 10x)_
- Review network driver logs _(recommended 10x)_
- Monitor packet loss rate _(recommended 10x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 6211 | 6229 | 19 readings |
| 9099 | 9119 | 21 readings |
| 11983 | 11983 | 1 readings |
| 19422 | 19422 | 1 readings |
| 20639 | 20639 | 1 readings |
| 22069 | 22069 | 1 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._