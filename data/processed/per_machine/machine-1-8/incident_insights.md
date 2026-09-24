# Incident Insights — machine-1-8

Generated 2026-09-24 04:52:04 from 23,698 real telemetry readings (threshold 0.52).

**1211 incidents triggered** across **2 distinct fault types**, in **31 separate burst(s)**.

## Severity Breakdown

- **High**: 1208 incidents
- **Medium**: 3 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 1208 |
| Database Performance Degradation | Medium | 3 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 1208x)_
- Inspect cable connections _(recommended 1208x)_
- Review network driver logs _(recommended 1208x)_
- Monitor packet loss rate _(recommended 1208x)_
- Analyze slow query log _(recommended 3x)_
- Add database indexes _(recommended 3x)_
- Optimize query patterns _(recommended 3x)_
- Scale database resources _(recommended 3x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 269 | 429 | 161 readings |
| 844 | 885 | 42 readings |
| 1690 | 1698 | 9 readings |
| 1788 | 1851 | 64 readings |
| 2298 | 2326 | 29 readings |
| 3168 | 3283 | 116 readings |
| 4616 | 4688 | 73 readings |
| 5999 | 6177 | 179 readings |
| 6607 | 6645 | 39 readings |
| 7453 | 7611 | 159 readings |
| 8044 | 8086 | 43 readings |
| 8888 | 9051 | 164 readings |
| 9486 | 9525 | 40 readings |
| 10438 | 10439 | 2 readings |
| 11764 | 11929 | 166 readings |
| 12374 | 12396 | 23 readings |
| 13238 | 13349 | 112 readings |
| 14684 | 14764 | 81 readings |
| 16098 | 16258 | 161 readings |
| 16690 | 16726 | 37 readings |
| 17544 | 17692 | 149 readings |
| 18132 | 18166 | 35 readings |
| 18982 | 19008 | 27 readings |
| 19060 | 19130 | 71 readings |
| 19572 | 19602 | 31 readings |
| 20425 | 20428 | 4 readings |
| 20519 | 20574 | 56 readings |
| 21001 | 21044 | 44 readings |
| 21888 | 22010 | 123 readings |
| 22451 | 22486 | 36 readings |
| 23411 | 23411 | 1 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._