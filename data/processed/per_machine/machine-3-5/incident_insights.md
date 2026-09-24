# Incident Insights — machine-3-5

Generated 2026-09-24 04:56:21 from 23,690 real telemetry readings (threshold 0.52).

**3 incidents triggered** across **1 distinct fault types**, in **1 separate burst(s)**.

## Severity Breakdown

- **High**: 3 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 3 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 3x)_
- Inspect cable connections _(recommended 3x)_
- Review network driver logs _(recommended 3x)_
- Monitor packet loss rate _(recommended 3x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 288 | 314 | 27 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._