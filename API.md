# AIOps MVP - API Documentation

Complete REST API reference for the AIOps MVP system.

## Base URL

```
http://localhost:5000/api
```

## Authentication

All API endpoints require Bearer token authentication.

### Setup

1. Set your API key in `.env`:
```bash
AIOPS_API_KEY=your_secure_key_here
```

2. Include token in all requests:
```bash
Authorization: Bearer your_secure_key_here
```

## API Endpoints

### 1. Run Chaos Simulation

**POST** `/api/chaos-simulation`

Run multi-service fault injection with anomaly detection.

#### Request

```bash
curl -X POST http://localhost:5000/api/chaos-simulation \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json"
```

#### Response (200 OK)

```json
{
  "status": "success",
  "summary": {
    "faults_injected": 53,
    "anomalies_detected": 48,
    "incidents_classified": 48,
    "detection_rate": "90.6%"
  },
  "by_service": {
    "service_a": {
      "incident_type": 15,
      "confidence": 0.92
    },
    "service_b": {
      "incident_type": 20,
      "confidence": 0.89
    },
    "service_c": {
      "incident_type": 18,
      "confidence": 0.87
    }
  },
  "by_type": {
    "resource_exhaustion": 15,
    "performance_degradation": 20,
    "service_unavailability": 18
  },
  "timeline": [
    {
      "time": 20,
      "service": "service_a",
      "incident_type": "resource_exhaustion",
      "confidence": 0.92
    }
  ],
  "faults": [
    {
      "time": 20,
      "service": "service_a",
      "fault_type": "memory_leak"
    }
  ]
}
```

#### Error Response (401 Unauthorized)

```json
{
  "error": "Invalid API key"
}
```

---

### 2. Get Metrics

**GET** `/api/metrics`

Retrieve latest system metrics and model performance.

#### Request

```bash
curl -X GET http://localhost:5000/api/metrics \
  -H "Authorization: Bearer your_api_key"
```

#### Response (200 OK)

```json
{
  "anomalies_detected": 48,
  "alerts_generated": 48,
  "execution_time": 2.34,
  "precision": 0.85,
  "recall": 0.92,
  "f1_score": 0.88
}
```

---

### 3. Get Incidents

**GET** `/api/incidents`

Retrieve classified incidents from the latest analysis.

#### Request

```bash
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer your_api_key"
```

#### Response (200 OK)

```json
{
  "incidents": [
    {
      "time": 20,
      "service": "service_a",
      "incident_type": "resource_exhaustion",
      "confidence": 0.92,
      "metric_value": 650.5,
      "deviation_pct": 45.3
    },
    {
      "time": 15,
      "service": "service_b",
      "incident_type": "performance_degradation",
      "confidence": 0.89,
      "metric_value": 185.2,
      "deviation_pct": 38.1
    }
  ],
  "total": 48
}
```

---

### 4. Get Statistics

**GET** `/api/statistics`

Retrieve comprehensive model performance statistics.

#### Request

```bash
curl -X GET http://localhost:5000/api/statistics \
  -H "Authorization: Bearer your_api_key"
```

#### Response (200 OK)

```json
{
  "model_performance": {
    "precision": 0.85,
    "recall": 0.92,
    "f1_score": 0.88,
    "roc_auc": 0.94
  },
  "efficiency": {
    "latency_ms": 2340,
    "false_positive_rate": 0.023
  }
}
```

---

### 5. Run Analysis

**POST** `/api/run-analysis`

Execute end-to-end AIOps analysis on dataset.

#### Request

```bash
curl -X POST http://localhost:5000/api/run-analysis \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "smd",
    "machine_id": "machine-1-1",
    "config": "config/settings.yaml"
  }'
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data_source | string | smd | Data source: "smd" or "aiops" |
| machine_id | string | machine-1-1 | Machine identifier |
| config | string | config/settings.yaml | Path to config file |

#### Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "anomalies_detected": 15,
    "alerts_generated": 14,
    "execution_time_seconds": 5.23,
    "precision": 0.87,
    "recall": 0.91,
    "f1_score": 0.89,
    "roc_auc": 0.93,
    "false_positive_rate": 0.02
  },
  "timestamp": "2026-08-22T10:30:45.123456"
}
```

---

### 6. Get Chaos Data

**GET** `/api/chaos-data`

Retrieve stored chaos simulation data for visualization.

#### Request

```bash
curl -X GET http://localhost:5000/api/chaos-data \
  -H "Authorization: Bearer your_api_key"
```

#### Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "faults": [...],
    "anomalies": [...],
    "incidents": [...]
  }
}
```

---

### 7. API Documentation

**GET** `/api/docs`

Get OpenAPI/Swagger specification.

#### Request

```bash
curl -X GET http://localhost:5000/api/docs
```

#### Response (200 OK)

Returns complete OpenAPI 3.0 specification in JSON format.

---

**GET** `/api/openapi.json`

Alternative endpoint for OpenAPI specification.

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Request completed successfully |
| 400 | Bad Request - Invalid parameters or malformed request |
| 401 | Unauthorized - Missing or invalid API key |
| 404 | Not Found - Endpoint does not exist |
| 500 | Server Error - Internal server error |
| 503 | Service Unavailable - Server temporarily unavailable |

## Error Handling

All errors return JSON with error details:

```json
{
  "error": "Error description",
  "status": "error"
}
```

### Examples

**Missing Auth Header**
```bash
curl -X GET http://localhost:5000/api/metrics
# Returns 401: {"error": "Missing or invalid authorization header"}
```

**Invalid API Key**
```bash
curl -X GET http://localhost:5000/api/metrics \
  -H "Authorization: Bearer invalid_key"
# Returns 401: {"error": "Invalid API key"}
```

**Invalid Parameters**
```bash
curl -X POST http://localhost:5000/api/run-analysis \
  -H "Authorization: Bearer your_key" \
  -d '{"data_source": "invalid"}'
# Returns 400: {"error": "Invalid data_source"}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **General limit:** 50 requests per hour per IP
- **Chaos simulation:** 5 per hour (resource-intensive)

Rate limit headers in response:

```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1629898800
```

## Security

### Headers Sent in Responses

```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

### CORS

CORS is enabled for specified origins only. Configure in `.env`:

```bash
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Examples

### Python

```python
import requests

API_KEY = "your_api_key"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Get metrics
response = requests.get(
    "http://localhost:5000/api/metrics",
    headers=headers
)
print(response.json())

# Run chaos simulation
response = requests.post(
    "http://localhost:5000/api/chaos-simulation",
    headers=headers
)
incidents = response.json()['timeline']
print(f"Detected {len(incidents)} incidents")
```

### JavaScript/Node.js

```javascript
const API_KEY = "your_api_key";

async function getMetrics() {
  const response = await fetch('http://localhost:5000/api/metrics', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}

getMetrics().then(data => {
  console.log(`Precision: ${data.precision}`);
  console.log(`Recall: ${data.recall}`);
  console.log(`F1-Score: ${data.f1_score}`);
});
```

### cURL

```bash
# Set API key
export API_KEY="your_api_key"

# Get metrics
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:5000/api/metrics | jq .

# Run simulation
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  http://localhost:5000/api/chaos-simulation | jq .

# Get incidents
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:5000/api/incidents | jq '.incidents | length'
```

## Webhook Support

Not yet implemented. Coming in v2.0.

## Rate Limit Best Practices

1. Cache responses when possible
2. Use exponential backoff for retries
3. Monitor X-RateLimit-Remaining header
4. Request higher limits for production use

## API Versioning

Current version: **1.0.0**

Endpoints follow REST conventions. Version will be included in URL for future versions: `/api/v2/`

## Support

For issues or questions:
- Open an issue: https://github.com/jonesoibe/aiops-mvp/issues
- Check documentation: https://github.com/jonesoibe/aiops-mvp/wiki
- Email: support@aiops-mvp.dev

---

**Last Updated:** August 2026
**API Version:** 1.0.0
