# Incident Insights — machine-3-2

Generated 2026-09-24 04:55:41 from 23,702 real telemetry readings (threshold 0.52).

**46 incidents triggered** across **2 distinct fault types**, in **28 separate burst(s)**.

## Severity Breakdown

- **High**: 46 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 45 |
| Application Error Rate Spike | High | 1 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 45x)_
- Inspect cable connections _(recommended 45x)_
- Review network driver logs _(recommended 45x)_
- Monitor packet loss rate _(recommended 45x)_
- Review application logs _(recommended 1x)_
- Check database connectivity _(recommended 1x)_
- Restart application service _(recommended 1x)_
- Rollback recent changes _(recommended 1x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 301 | 397 | 97 readings |
| 4642 | 4644 | 3 readings |
| 6082 | 6082 | 1 readings |
| 6862 | 6862 | 1 readings |
| 7042 | 7042 | 1 readings |
| 7103 | 7103 | 1 readings |
| 7522 | 7523 | 2 readings |
| 8482 | 8483 | 2 readings |
| 8902 | 8902 | 1 readings |
| 9922 | 9922 | 1 readings |
| 10342 | 10343 | 2 readings |
| 10462 | 10462 | 1 readings |
| 11302 | 11302 | 1 readings |
| 12742 | 12742 | 1 readings |
| 12802 | 12802 | 1 readings |
| 13282 | 13283 | 2 readings |
| 14303 | 14303 | 1 readings |
| 14722 | 14722 | 1 readings |
| 17002 | 17002 | 1 readings |
| 17122 | 17122 | 1 readings |
| 17542 | 17542 | 1 readings |
| 18502 | 18502 | 1 readings |
| 18564 | 18564 | 1 readings |
| 19103 | 19103 | 1 readings |
| 19996 | 20008 | 13 readings |
| 20483 | 20483 | 1 readings |
| 22223 | 22223 | 1 readings |
| 23607 | 23608 | 2 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._