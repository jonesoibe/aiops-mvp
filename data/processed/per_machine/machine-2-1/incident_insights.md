# Incident Insights — machine-2-1

Generated 2026-09-24 04:52:24 from 23,693 real telemetry readings (threshold 0.52).

**304 incidents triggered** across **3 distinct fault types**, in **39 separate burst(s)**.

## Severity Breakdown

- **Critical**: 20 incidents
- **High**: 284 incidents

## Top Fault Types

| Fault Type | Severity | Occurrences |
|---|---|---|
| Network Interface Issues | High | 267 |
| Memory Pressure | Critical | 20 |
| Application Error Rate Spike | High | 17 |

## Prioritized Recommendations

Deduplicated across every triggered incident, ranked by how often each was recommended (most-recommended actions address the most frequent faults):

- Check network hardware _(recommended 267x)_
- Inspect cable connections _(recommended 267x)_
- Review network driver logs _(recommended 267x)_
- Monitor packet loss rate _(recommended 267x)_
- Increase available memory _(recommended 20x)_
- Check for memory leaks _(recommended 20x)_
- Restart memory-heavy service _(recommended 20x)_
- Enable swap monitoring _(recommended 20x)_
- Review application logs _(recommended 17x)_
- Check database connectivity _(recommended 17x)_
- Restart application service _(recommended 17x)_
- Rollback recent changes _(recommended 17x)_

## Incident Clusters (contiguous bursts)

Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):

| Start Row | End Row | Span |
|---|---|---|
| 294 | 376 | 83 readings |
| 437 | 437 | 1 readings |
| 721 | 721 | 1 readings |
| 776 | 777 | 2 readings |
| 6063 | 6097 | 35 readings |
| 6513 | 6513 | 1 readings |
| 7497 | 7533 | 37 readings |
| 7951 | 7951 | 1 readings |
| 8002 | 8002 | 1 readings |
| 8948 | 8977 | 30 readings |
| 10383 | 10413 | 31 readings |
| 10806 | 10821 | 16 readings |
| 11827 | 11827 | 1 readings |
| 11881 | 11884 | 4 readings |
| 13307 | 13308 | 2 readings |
| 13397 | 13402 | 6 readings |
| 14697 | 14833 | 137 readings |
| 15124 | 15137 | 14 readings |
| 16141 | 16213 | 73 readings |
| 16273 | 16273 | 1 readings |
| 16575 | 16581 | 7 readings |
| 17471 | 17490 | 20 readings |
| 17552 | 17640 | 89 readings |
| 17742 | 17743 | 2 readings |
| 18024 | 18061 | 38 readings |
| 18833 | 18833 | 1 readings |
| 18958 | 19078 | 121 readings |
| 19132 | 19153 | 22 readings |
| 20212 | 20212 | 1 readings |
| 20392 | 20545 | 154 readings |
| 20871 | 20881 | 11 readings |
| 21651 | 21691 | 41 readings |
| 21811 | 22059 | 249 readings |
| 22321 | 22346 | 26 readings |
| 23091 | 23091 | 1 readings |
| 23151 | 23151 | 1 readings |
| 23226 | 23226 | 1 readings |
| 23331 | 23416 | 86 readings |
| 23473 | 23522 | 50 readings |

---
_Full per-incident detail (timestamp, exact score, affected features) is in `incident_log.json` / `incident_log.csv` alongside this file._