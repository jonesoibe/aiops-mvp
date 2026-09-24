# Incident Insights — machine-2-3

Generated 2026-09-24 04:53:11 from 23,688 real telemetry readings (threshold 0.52).

**70 incidents triggered** across **5 distinct fault types**, in **17 separate burst(s)**.

## Severity Breakdown

- **Critical**: 3 incidents
- **High**: 65 incidents
- **Medium**: 2 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 47 |
| Application Error Rate Spike | High | 18 |
| CPU Exhaustion | Critical | 3 |
| Database Performance Degradation | Medium | 1 |
| Connection Limit Approaching | Medium | 1 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 47x)_
- Inspect cable connections _(recommended 47x)_
- Review network driver logs _(recommended 47x)_
- Monitor packet loss rate _(recommended 47x)_
- Review application logs _(recommended 18x)_
- Check database connectivity _(recommended 18x)_
- Restart application service _(recommended 18x)_
- Rollback recent changes _(recommended 18x)_
- Scale horizontally (add more instances) _(recommended 3x)_
- Check for runaway processes _(recommended 3x)_
- Optimize application code _(recommended 3x)_
- Analyze slow query log _(recommended 1x)_
- Add database indexes _(recommended 1x)_
- Optimize query patterns _(recommended 1x)_
- Scale database resources _(recommended 1x)_
- Increase connection pool size _(recommended 1x)_
- Implement connection pooling _(recommended 1x)_
- Close idle connections _(recommended 1x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 1317 | 1317 | 1 readings |
| 1673 | 1699 | 27 readings |
| 4192 | 4200 | 9 readings |
| 4563 | 4578 | 16 readings |
| 6210 | 6217 | 8 readings |
| 7448 | 7450 | 3 readings |
| 8521 | 8535 | 15 readings |
| 11774 | 11774 | 1 readings |
| 11857 | 11857 | 1 readings |
| 12145 | 12145 | 1 readings |
| 12451 | 12451 | 1 readings |
| 13207 | 13207 | 1 readings |
| 14678 | 14678 | 1 readings |
| 17170 | 17170 | 1 readings |
| 17549 | 17549 | 1 readings |
| 20025 | 20027 | 3 readings |
| 21880 | 21880 | 1 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._