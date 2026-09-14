# SLO/SLA API Reference

Complete REST API documentation for SLO tracking system.

---

## Base URL
```
http://localhost:5000/api/slos
```

## Authentication
All endpoints require Bearer token:
```
Authorization: Bearer test_token
```

---

## Endpoints

### 1. List All SLOs

**GET** `/slos`

List all SLOs with optional filtering.

**Query Parameters:**
- `service_id` (optional) - Filter by service ID
- `enabled_only` (optional) - "true" to show only enabled SLOs

**Example:**
```bash
curl "http://localhost:5000/api/slos?enabled_only=true" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "slos": [
    {
      "id": "slo_api_availability",
      "service_id": "api-gateway",
      "service_name": "API Gateway",
      "description": "API Gateway availability SLO - 99.9%",
      "target_percentage": 99.9,
      "tracking_period": "monthly",
      "period_start": "2026-09-15T00:00:00",
      "period_end": "2026-10-15T00:00:00",
      "enabled": true,
      "error_budget_threshold": 0.3,
      "metrics": [
        {
          "name": "availability",
          "metric_type": "availability",
          "threshold": 99.9,
          "comparison": ">",
          "window": 3600,
          "weight": 1.0
        }
      ],
      "notes": "Critical service - maintain high availability",
      "created_at": "2026-09-15T00:00:00"
    }
  ],
  "total": 3
}
```

---

### 2. Create New SLO

**POST** `/slos`

Create a new Service Level Objective.

**Request Body:**
```json
{
  "id": "slo_custom",
  "service_id": "cache-service",
  "service_name": "Cache Service",
  "description": "Cache service availability",
  "target_percentage": 99.0,
  "tracking_period": "weekly",
  "period_days": 7,
  "enabled": true,
  "error_budget_threshold": 0.25,
  "notes": "Optional notes",
  "metrics": [
    {
      "name": "availability",
      "metric_type": "availability",
      "threshold": 99.0,
      "comparison": ">",
      "window": 3600,
      "weight": 1.0
    }
  ]
}
```

**Metric Types:**
- `availability` - Uptime percentage
- `latency` - Response time
- `error_rate` - Failed requests percentage
- `throughput` - Requests per second
- `custom` - Custom metric

**Comparison Operators:**
- `<` - Less than
- `<=` - Less than or equal
- `>` - Greater than
- `>=` - Greater than or equal
- `==` - Equal
- `!=` - Not equal

**Response (201):**
```json
{
  "id": "slo_custom",
  "service_id": "cache-service",
  "service_name": "Cache Service",
  ...
}
```

**Errors:**
- `400` - Invalid input or missing required fields
- `409` - SLO with same ID already exists

---

### 3. Update SLO

**PUT** `/slos/{slo_id}`

Update an existing SLO.

**Example:**
```bash
curl -X PUT "http://localhost:5000/api/slos/slo_api_availability" \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "target_percentage": 99.95,
    "enabled": true
  }'
```

**Response (200):**
```json
{
  "id": "slo_api_availability",
  "target_percentage": 99.95,
  ...
}
```

---

### 4. Delete SLO

**DELETE** `/slos/{slo_id}`

Delete an SLO.

**Example:**
```bash
curl -X DELETE "http://localhost:5000/api/slos/slo_custom" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "status": "deleted",
  "slo_id": "slo_custom"
}
```

---

### 5. Get SLO Compliance Summary

**GET** `/slos/{slo_id}/compliance`

Get compliance status and statistics for an SLO.

**Example:**
```bash
curl "http://localhost:5000/api/slos/slo_api_availability/compliance" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "slo_id": "slo_api_availability",
  "service_name": "API Gateway",
  "target_percentage": 99.9,
  "average_compliance": 99.85,
  "min_compliance": 99.2,
  "max_compliance": 99.95,
  "violations": 0,
  "status": "healthy",
  "error_budget_remaining": 95.5,
  "days_remaining": 18,
  "last_updated": "2026-09-15T10:30:00Z"
}
```

**Possible Statuses:**
- `healthy` - Meeting SLO (>= target %)
- `warning` - Approaching threshold (95-100% of target)
- `violated` - Below target
- `no_data` - Insufficient data

---

### 6. Get Compliance History

**GET** `/slos/{slo_id}/compliance/history`

Get historical compliance records.

**Query Parameters:**
- `hours` (optional) - Hours of history to retrieve (default: 24)

**Example:**
```bash
curl "http://localhost:5000/api/slos/slo_api_availability/compliance/history?hours=168" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "slo_id": "slo_api_availability",
  "records": [
    {
      "slo_id": "slo_api_availability",
      "service_id": "api-gateway",
      "timestamp": "2026-09-15T10:30:00Z",
      "compliance_percentage": 99.85,
      "status": "healthy",
      "error_budget_remaining": 95.5,
      "errors_count": 1500,
      "total_requests": 1000000,
      "details": {
        "target_percentage": 99.9,
        "availability": 99.85,
        "meets_slo": true,
        "days_remaining": 18
      }
    }
  ],
  "total": 120
}
```

---

### 7. Get Error Budget Status

**GET** `/slos/{slo_id}/error-budget`

Get error budget information for an SLO.

**Example:**
```bash
curl "http://localhost:5000/api/slos/slo_api_availability/error-budget" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "slo_id": "slo_api_availability",
  "total_budget": 2592.0,
  "remaining_budget": 2462.0,
  "consumed_budget": 130.0,
  "consumed_percentage": 5.02,
  "burndown_rate": 0.0015,
  "last_update": "2026-09-15T10:30:00Z"
}
```

**Note:** Error budget is in seconds. A 99.9% SLO for 30 days = 2592 seconds (43.2 minutes) of acceptable downtime.

---

### 8. Record Metrics

**POST** `/slos/{slo_id}/record-metrics`

Record metric values for SLO evaluation.

**Request Body:**
```json
{
  "metric_values": {
    "availability": 99.85,
    "p95_latency": 450.0,
    "error_rate": 0.15
  },
  "total_requests": 1000000,
  "errors_count": 1500
}
```

**Example:**
```bash
curl -X POST "http://localhost:5000/api/slos/slo_api_availability/record-metrics" \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_values": {
      "availability": 99.85
    },
    "total_requests": 1000000,
    "errors_count": 1500
  }'
```

**Response (200):**
```json
{
  "slo_id": "slo_api_availability",
  "service_id": "api-gateway",
  "timestamp": "2026-09-15T10:30:00Z",
  "compliance_percentage": 99.85,
  "status": "healthy",
  "error_budget_remaining": 95.5,
  "errors_count": 1500,
  "total_requests": 1000000,
  "details": {
    "target_percentage": 99.9,
    "availability": 99.85,
    "meets_slo": true,
    "days_remaining": 18
  }
}
```

---

### 9. Get SLO Statistics

**GET** `/slos/stats`

Get overall SLO statistics.

**Example:**
```bash
curl "http://localhost:5000/api/slos/stats" \
  -H "Authorization: Bearer test_token"
```

**Response (200):**
```json
{
  "total_slos": 3,
  "active_slos": 2,
  "status_counts": {
    "healthy": 2,
    "warning": 0,
    "violated": 0,
    "no_data": 1
  },
  "compliance_records": 145,
  "largest_error_budget": 95.5
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required field: service_id"
}
```

### 404 Not Found
```json
{
  "error": "SLO not found"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing authorization header"
}
```

---

## Rate Limits
None currently implemented. Recommended: 100 requests/minute per user.

---

## Data Types

### SLOMetric
```typescript
{
  name: string              // Metric name
  metric_type: string       // "availability" | "latency" | "error_rate" | "throughput" | "custom"
  threshold: number         // Threshold value
  comparison: string        // "<" | "<=" | ">" | ">=" | "==" | "!="
  window: number           // Time window in seconds
  weight: number           // Importance weight (0-1)
}
```

### SLOComplianceRecord
```typescript
{
  slo_id: string           // SLO ID
  service_id: string       // Service ID
  timestamp: string        // ISO 8601 timestamp
  compliance_percentage: number  // 0-100
  status: string           // "healthy" | "warning" | "violated" | "no_data"
  error_budget_remaining: number // Percentage remaining
  errors_count: number     // Total errors
  total_requests: number   // Total requests
  details: object          // Additional details
}
```

---

## Example Workflow

```bash
# 1. Create SLO
curl -X POST "http://localhost:5000/api/slos" \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{...}'

# 2. Record metrics
curl -X POST "http://localhost:5000/api/slos/slo_id/record-metrics" \
  -H "Authorization: Bearer test_token" \
  -d '{...}'

# 3. Check compliance
curl "http://localhost:5000/api/slos/slo_id/compliance" \
  -H "Authorization: Bearer test_token"

# 4. Get error budget status
curl "http://localhost:5000/api/slos/slo_id/error-budget" \
  -H "Authorization: Bearer test_token"

# 5. Get history
curl "http://localhost:5000/api/slos/slo_id/compliance/history" \
  -H "Authorization: Bearer test_token"
```

---

## Testing with cURL

See [SLO_TRACKING_GUIDE.md](SLO_TRACKING_GUIDE.md) for examples.

---

**API Version:** 1.0  
**Status:** Production-ready  
**Last Updated:** 2026-09-15
