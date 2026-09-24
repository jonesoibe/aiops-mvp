# Incident Insights — machine-2-8

Generated 2026-09-24 04:54:53 from 23,702 real telemetry readings (threshold 0.52).

**312 incidents triggered** across **2 distinct fault types**, in **18 separate burst(s)**.

## Severity Breakdown

- **Critical**: 156 incidents
- **High**: 156 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Memory Pressure | Critical | 156 |
| Network Interface Issues | High | 156 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Increase available memory _(recommended 156x)_
- Check for memory leaks _(recommended 156x)_
- Restart memory-heavy service _(recommended 156x)_
- Enable swap monitoring _(recommended 156x)_
- Check network hardware _(recommended 156x)_
- Inspect cable connections _(recommended 156x)_
- Review network driver logs _(recommended 156x)_
- Monitor packet loss rate _(recommended 156x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 322 | 331 | 10 readings |
| 1720 | 1738 | 19 readings |
| 3140 | 3184 | 45 readings |
| 4580 | 4585 | 6 readings |
| 6043 | 6055 | 13 readings |
| 7459 | 7512 | 54 readings |
| 8921 | 8943 | 23 readings |
| 10351 | 10385 | 35 readings |
| 11814 | 11832 | 19 readings |
| 13225 | 13279 | 55 readings |
| 14679 | 14723 | 45 readings |
| 16109 | 16117 | 9 readings |
| 17559 | 17589 | 31 readings |
| 19015 | 19035 | 21 readings |
| 19628 | 19664 | 37 readings |
| 20426 | 20475 | 50 readings |
| 21859 | 21897 | 39 readings |
| 23287 | 23395 | 109 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._