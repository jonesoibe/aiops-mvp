# Incident Insights — machine-3-3

Generated 2026-09-24 04:55:56 from 23,703 real telemetry readings (threshold 0.52).

**168 incidents triggered** across **2 distinct fault types**, in **29 separate burst(s)**.

## Severity Breakdown

- **High**: 168 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 166 |
| Application Error Rate Spike | High | 2 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 166x)_
- Inspect cable connections _(recommended 166x)_
- Review network driver logs _(recommended 166x)_
- Monitor packet loss rate _(recommended 166x)_
- Review application logs _(recommended 2x)_
- Check database connectivity _(recommended 2x)_
- Restart application service _(recommended 2x)_
- Rollback recent changes _(recommended 2x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 229 | 277 | 49 readings |
| 421 | 421 | 1 readings |
| 1619 | 1656 | 38 readings |
| 1748 | 1773 | 26 readings |
| 2974 | 2976 | 3 readings |
| 3218 | 3220 | 3 readings |
| 4589 | 4659 | 71 readings |
| 5889 | 5889 | 1 readings |
| 6042 | 6042 | 1 readings |
| 6274 | 6299 | 26 readings |
| 7330 | 7386 | 57 readings |
| 7446 | 7456 | 11 readings |
| 8625 | 8625 | 1 readings |
| 9004 | 9010 | 7 readings |
| 10295 | 10301 | 7 readings |
| 10445 | 10448 | 4 readings |
| 11786 | 11788 | 3 readings |
| 11848 | 11889 | 42 readings |
| 13294 | 13318 | 25 readings |
| 14598 | 14645 | 48 readings |
| 14718 | 14726 | 9 readings |
| 16028 | 16028 | 1 readings |
| 17334 | 17334 | 1 readings |
| 17477 | 17566 | 90 readings |
| 18944 | 18971 | 28 readings |
| 19104 | 19119 | 16 readings |
| 20523 | 20574 | 52 readings |
| 21981 | 22000 | 20 readings |
| 23354 | 23423 | 70 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._