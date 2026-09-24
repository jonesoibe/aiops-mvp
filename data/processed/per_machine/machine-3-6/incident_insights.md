# Incident Insights — machine-3-6

Generated 2026-09-24 04:56:37 from 28,726 real telemetry readings (threshold 0.52).

**1199 incidents triggered** across **2 distinct fault types**, in **26 separate burst(s)**.

## Severity Breakdown

- **High**: 1199 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 1186 |
| Application Error Rate Spike | High | 13 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 1186x)_
- Inspect cable connections _(recommended 1186x)_
- Review network driver logs _(recommended 1186x)_
- Monitor packet loss rate _(recommended 1186x)_
- Review application logs _(recommended 13x)_
- Check database connectivity _(recommended 13x)_
- Restart application service _(recommended 13x)_
- Rollback recent changes _(recommended 13x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 361 | 472 | 112 readings |
| 1800 | 1916 | 117 readings |
| 3240 | 3361 | 122 readings |
| 4681 | 4793 | 113 readings |
| 6121 | 6229 | 109 readings |
| 7570 | 7604 | 35 readings |
| 7656 | 7700 | 45 readings |
| 9000 | 9121 | 122 readings |
| 9655 | 9655 | 1 readings |
| 10435 | 10490 | 56 readings |
| 10560 | 10581 | 22 readings |
| 11879 | 11992 | 114 readings |
| 13319 | 13426 | 108 readings |
| 13931 | 13931 | 1 readings |
| 14759 | 14875 | 117 readings |
| 16199 | 16313 | 115 readings |
| 17645 | 17742 | 98 readings |
| 19080 | 19191 | 112 readings |
| 20534 | 20628 | 95 readings |
| 21930 | 22081 | 152 readings |
| 22569 | 22580 | 12 readings |
| 23420 | 23512 | 93 readings |
| 24848 | 24952 | 105 readings |
| 26295 | 26393 | 99 readings |
| 27719 | 27769 | 51 readings |
| 27842 | 27850 | 9 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._