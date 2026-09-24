# Incident Insights — machine-1-7

Generated 2026-09-24 04:51:40 from 23,697 real telemetry readings (threshold 0.52).

**996 incidents triggered** across **4 distinct fault types**, in **26 separate burst(s)**.

## Severity Breakdown

- **Critical**: 391 incidents
- **High**: 605 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 494 |
| Memory Pressure | Critical | 391 |
| Application Error Rate Spike | High | 109 |
| Disk I/O Bottleneck | High | 2 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 494x)_
- Inspect cable connections _(recommended 494x)_
- Review network driver logs _(recommended 494x)_
- Monitor packet loss rate _(recommended 494x)_
- Increase available memory _(recommended 391x)_
- Check for memory leaks _(recommended 391x)_
- Restart memory-heavy service _(recommended 391x)_
- Enable swap monitoring _(recommended 391x)_
- Review application logs _(recommended 109x)_
- Check database connectivity _(recommended 109x)_
- Restart application service _(recommended 109x)_
- Rollback recent changes _(recommended 109x)_
- Upgrade disk to SSD _(recommended 2x)_
- Optimize I/O patterns _(recommended 2x)_
- Distribute I/O across disks _(recommended 2x)_
- Check for runaway I/O operations _(recommended 2x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 399 | 462 | 64 readings |
| 1367 | 1368 | 2 readings |
| 1846 | 1883 | 38 readings |
| 2779 | 2801 | 23 readings |
| 4724 | 4766 | 43 readings |
| 5652 | 5680 | 29 readings |
| 6159 | 6202 | 44 readings |
| 7609 | 7639 | 31 readings |
| 8558 | 8565 | 8 readings |
| 10494 | 10521 | 28 readings |
| 11418 | 11441 | 24 readings |
| 11918 | 11963 | 46 readings |
| 12092 | 12136 | 45 readings |
| 12706 | 12707 | 2 readings |
| 13352 | 13407 | 56 readings |
| 14297 | 14332 | 36 readings |
| 14802 | 14841 | 40 readings |
| 15759 | 15759 | 1 readings |
| 16236 | 16284 | 49 readings |
| 17678 | 17693 | 16 readings |
| 19119 | 19160 | 42 readings |
| 20559 | 20601 | 43 readings |
| 21497 | 21519 | 23 readings |
| 21981 | 22042 | 62 readings |
| 22958 | 22963 | 6 readings |
| 23440 | 23489 | 50 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._