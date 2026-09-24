# Incident Insights — machine-1-3

Generated 2026-09-24 04:50:20 from 23,702 real telemetry readings (threshold 0.52).

**61 incidents triggered** across **4 distinct fault types**, in **7 separate burst(s)**.

## Severity Breakdown

- **Critical**: 26 incidents
- **High**: 35 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 34 |
| Memory Pressure | Critical | 25 |
| CPU Exhaustion | Critical | 1 |
| Application Error Rate Spike | High | 1 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 34x)_
- Inspect cable connections _(recommended 34x)_
- Review network driver logs _(recommended 34x)_
- Monitor packet loss rate _(recommended 34x)_
- Increase available memory _(recommended 25x)_
- Check for memory leaks _(recommended 25x)_
- Restart memory-heavy service _(recommended 25x)_
- Enable swap monitoring _(recommended 25x)_
- Scale horizontally (add more instances) _(recommended 1x)_
- Check for runaway processes _(recommended 1x)_
- Optimize application code _(recommended 1x)_
- Review application logs _(recommended 1x)_
- Check database connectivity _(recommended 1x)_
- Restart application service _(recommended 1x)_
- Rollback recent changes _(recommended 1x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 3205 | 3230 | 26 readings |
| 4660 | 4671 | 12 readings |
| 13276 | 13306 | 31 readings |
| 14723 | 14756 | 34 readings |
| 20951 | 20964 | 14 readings |
| 21302 | 21337 | 36 readings |
| 23375 | 23412 | 38 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._