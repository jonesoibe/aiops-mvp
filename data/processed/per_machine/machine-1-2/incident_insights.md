# Incident Insights — machine-1-2

Generated 2026-09-24 04:50:03 from 23,694 real telemetry readings (threshold 0.52).

**219 incidents triggered** across **3 distinct fault types**, in **50 separate burst(s)**.

## Severity Breakdown

- **Critical**: 67 incidents
- **High**: 151 incidents
- **Medium**: 1 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 151 |
| Memory Pressure | Critical | 67 |
| Database Performance Degradation | Medium | 1 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 151x)_
- Inspect cable connections _(recommended 151x)_
- Review network driver logs _(recommended 151x)_
- Monitor packet loss rate _(recommended 151x)_
- Increase available memory _(recommended 67x)_
- Check for memory leaks _(recommended 67x)_
- Restart memory-heavy service _(recommended 67x)_
- Enable swap monitoring _(recommended 67x)_
- Analyze slow query log _(recommended 1x)_
- Add database indexes _(recommended 1x)_
- Optimize query patterns _(recommended 1x)_
- Scale database resources _(recommended 1x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 824 | 863 | 40 readings |
| 960 | 960 | 1 readings |
| 1335 | 1335 | 1 readings |
| 1650 | 1650 | 1 readings |
| 1825 | 1895 | 71 readings |
| 1966 | 1966 | 1 readings |
| 2335 | 2335 | 1 readings |
| 2400 | 2400 | 1 readings |
| 2520 | 2520 | 1 readings |
| 2580 | 2581 | 2 readings |
| 2671 | 2671 | 1 readings |
| 2764 | 2774 | 11 readings |
| 2878 | 2878 | 1 readings |
| 3219 | 3243 | 25 readings |
| 3376 | 3419 | 44 readings |
| 10136 | 10136 | 1 readings |
| 10425 | 10484 | 60 readings |
| 10554 | 10560 | 7 readings |
| 11101 | 11101 | 1 readings |
| 11402 | 11403 | 2 readings |
| 11862 | 11876 | 15 readings |
| 11929 | 11936 | 8 readings |
| 12359 | 12359 | 1 readings |
| 12844 | 12860 | 17 readings |
| 13078 | 13078 | 1 readings |
| 13353 | 13382 | 30 readings |
| 13470 | 13470 | 1 readings |
| 14835 | 14866 | 32 readings |
| 15596 | 15596 | 1 readings |
| 15719 | 15724 | 6 readings |
| 16210 | 16255 | 46 readings |
| 17489 | 17489 | 1 readings |
| 17630 | 17640 | 11 readings |
| 17742 | 17760 | 19 readings |
| 18332 | 18332 | 1 readings |
| 18603 | 18606 | 4 readings |
| 19184 | 19247 | 64 readings |
| 19442 | 19442 | 1 readings |
| 20594 | 20637 | 44 readings |
| 21033 | 21033 | 1 readings |
| 21512 | 21515 | 4 readings |
| 21949 | 22013 | 65 readings |
| 22258 | 22317 | 60 readings |
| 22500 | 22512 | 13 readings |
| 22620 | 22621 | 2 readings |
| 22800 | 22800 | 1 readings |
| 22860 | 22869 | 10 readings |
| 23029 | 23069 | 41 readings |
| 23182 | 23204 | 23 readings |
| 23389 | 23432 | 44 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._