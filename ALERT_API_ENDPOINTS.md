# Real-Time Alerting API Endpoints

## Overview
These endpoints manage alert rules, view active alerts, and control alert lifecycle.

---

## Alert Rules Management

### GET /api/alerts/rules
**Get all alert rules**

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/alerts/rules
```

**Response:**
```json
{
  "rules": [
    {
      "id": "cpu_spike",
      "name": "High CPU Usage",
      "description": "Alert when CPU exceeds 90%",
      "metric_name": "cpu_usage",
      "condition": ">",
      "threshold": 90,
      "duration": 300,
      "severity": "major",
      "enabled": true,
      "notification_channels": ["slack", "email"]
    }
  ],
  "total": 1,
  "enabled": 1
}
```

---

### POST /api/alerts/rules
**Create a new alert rule**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Memory Usage",
    "description": "Alert when memory exceeds 85%",
    "metric_name": "memory_usage",
    "condition": ">",
    "threshold": 85,
    "duration": 300,
    "severity": "major",
    "notification_channels": ["slack", "email"]
  }' http://localhost:5000/api/alerts/rules
```

**Required Fields:**
- `name` (string): Rule name
- `metric_name` (string): Metric to monitor
- `condition` (string): '>', '<', '>=', '<=', '==', '!=', 'range'
- `threshold` (number): Threshold value

**Optional Fields:**
- `description` (string): Rule description
- `duration` (number): How long condition must be true (seconds, default 300)
- `severity` (string): 'critical', 'major', 'minor', 'info' (default 'major')
- `notification_channels` (array): Channels to notify (default ['slack', 'email'])
- `threshold_high` (number): For 'range' condition

**Response:**
```json
{
  "id": "memory_high_xyz",
  "name": "High Memory Usage",
  "created_at": "2026-09-12T10:00:00Z"
}
```

---

### PUT /api/alerts/rules/{rule_id}
**Update an alert rule**

```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold": 90,
    "enabled": true
  }' http://localhost:5000/api/alerts/rules/memory_high_xyz
```

---

### DELETE /api/alerts/rules/{rule_id}
**Delete an alert rule**

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/rules/memory_high_xyz
```

---

## Active Alerts

### GET /api/alerts
**Get all active and recent alerts**

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/alerts
```

**Query Parameters:**
- `status` (string): Filter by status ('firing', 'acknowledged', 'resolved', 'silenced')
- `severity` (string): Filter by severity ('critical', 'major', 'minor', 'info')
- `service_id` (string): Filter by service
- `limit` (number): Max results (default 50)

**Response:**
```json
{
  "alerts": [
    {
      "id": "prod_cpu_spike_1",
      "rule_id": "cpu_spike",
      "rule_name": "High CPU Usage",
      "metric_name": "cpu_usage",
      "current_value": 95.5,
      "threshold": 90.0,
      "severity": "major",
      "status": "firing",
      "service_id": "api-gateway",
      "fired_at": "2026-09-12T10:15:30Z",
      "acknowledged_at": null,
      "resolved_at": null,
      "duration_seconds": 450
    }
  ],
  "total": 5,
  "firing": 3,
  "acknowledged": 1,
  "resolved": 1
}
```

---

### GET /api/alerts/{alert_id}
**Get specific alert details**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/prod_cpu_spike_1
```

---

### GET /api/alerts/service/{service_id}
**Get alerts for a specific service**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/service/api-gateway
```

---

## Alert Actions

### POST /api/alerts/{alert_id}/acknowledge
**Acknowledge an alert (mark as being worked on)**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john.doe"
  }' http://localhost:5000/api/alerts/prod_cpu_spike_1/acknowledge
```

**Response:**
```json
{
  "status": "acknowledged",
  "acknowledged_by": "john.doe",
  "acknowledged_at": "2026-09-12T10:20:00Z"
}
```

---

### POST /api/alerts/{alert_id}/resolve
**Manually resolve an alert**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Scaled service horizontally"
  }' http://localhost:5000/api/alerts/prod_cpu_spike_1/resolve
```

**Response:**
```json
{
  "status": "resolved",
  "resolved_at": "2026-09-12T10:25:00Z",
  "duration_minutes": 10
}
```

---

### POST /api/alerts/{alert_id}/silence
**Temporarily silence an alert**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 30
  }' http://localhost:5000/api/alerts/prod_cpu_spike_1/silence
```

---

## Alert Statistics

### GET /api/alerts/stats
**Get alerting statistics and insights**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/stats
```

**Response:**
```json
{
  "active_alerts": 3,
  "critical": 0,
  "major": 3,
  "minor": 0,
  "total_rules": 8,
  "enabled_rules": 7,
  "total_alerts_fired": 145,
  "avg_resolution_time_minutes": 12.5,
  "alerts_by_service": {
    "api-gateway": 2,
    "order-service": 1
  },
  "alerts_by_severity": {
    "critical": 0,
    "major": 3,
    "minor": 0
  }
}
```

---

### GET /api/alerts/trends
**Get alert trends over time**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/alerts/trends?days=7"
```

**Query Parameters:**
- `days` (number): Time period to analyze (default 7)

**Response:**
```json
{
  "period_days": 7,
  "total_alerts_fired": 145,
  "alerts_per_day": [
    {"date": "2026-09-05", "count": 15},
    {"date": "2026-09-06", "count": 22},
    {"date": "2026-09-07", "count": 18},
    ...
  ],
  "top_rules": [
    {"rule_name": "High CPU Usage", "count": 45},
    {"rule_name": "High Memory Usage", "count": 32},
    {"rule_name": "High Error Rate", "count": 28}
  ],
  "avg_resolution_time_minutes": 12.5
}
```

---

## Preset Rules

### GET /api/alerts/templates
**Get pre-built alert rule templates**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/templates
```

**Response:**
```json
{
  "templates": [
    {
      "id": "cpu_spike",
      "name": "High CPU Usage",
      "description": "Alert when CPU exceeds 90% for 5 minutes",
      "metric_name": "cpu_usage",
      "condition": ">",
      "threshold": 90,
      "duration": 300
    },
    {
      "id": "memory_high",
      "name": "High Memory Usage",
      "description": "Alert when memory exceeds 85% for 5 minutes",
      "metric_name": "memory_usage",
      "condition": ">",
      "threshold": 85,
      "duration": 300
    },
    {
      "id": "error_rate_high",
      "name": "High Error Rate",
      "description": "Alert when error rate exceeds 5% for 2 minutes",
      "metric_name": "error_rate",
      "condition": ">",
      "threshold": 5,
      "duration": 120
    }
  ]
}
```

---

### POST /api/alerts/templates/{template_id}
**Create alert rule from template**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alerts/templates/cpu_spike
```

**Response:**
```json
{
  "id": "cpu_spike_prod",
  "created_from_template": "cpu_spike"
}
```

---

## WebSocket: Real-Time Alert Stream

**Connect to WebSocket for real-time alerts:**

```javascript
const socket = io('http://localhost:5000', {
  auth: {
    token: 'YOUR_JWT_TOKEN'
  }
});

// Join alerts namespace
socket.on('connect', () => {
  socket.emit('join', 'alerts');
});

// Listen for new alerts
socket.on('alert:fired', (alert) => {
  console.log('New alert:', alert);
  // Display notification, update UI, etc.
});

// Listen for resolved alerts
socket.on('alert:resolved', (alert) => {
  console.log('Alert resolved:', alert);
});

// Listen for acknowledged alerts
socket.on('alert:acknowledged', (alert) => {
  console.log('Alert acknowledged:', alert);
});
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid alert rule",
  "details": "Threshold is required"
}
```

### 404 Not Found
```json
{
  "error": "Alert not found",
  "alert_id": "prod_cpu_spike_1"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Missing or invalid token"
}
```

---

## Integration Examples

### Python (Requests)
```python
import requests

TOKEN = "your_jwt_token"
BASE_URL = "http://localhost:5000"

# Create alert rule
rule = {
    "name": "High CPU Usage",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 90,
    "severity": "major"
}

response = requests.post(
    f"{BASE_URL}/api/alerts/rules",
    json=rule,
    headers={"Authorization": f"Bearer {TOKEN}"}
)
print(response.json())
```

### JavaScript (Fetch)
```javascript
const TOKEN = "your_jwt_token";
const BASE_URL = "http://localhost:5000";

async function getAlerts() {
  const response = await fetch(
    `${BASE_URL}/api/alerts`,
    {
      headers: {
        "Authorization": `Bearer ${TOKEN}`
      }
    }
  );
  
  const data = await response.json();
  console.log(data.alerts);
}

getAlerts();
```

---

## Testing with cURL

### 1. Create alert rule
```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CPU Alert",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 80,
    "severity": "major"
  }'
```

### 2. Get all alerts
```bash
curl http://localhost:5000/api/alerts \
  -H "Authorization: Bearer test_token"
```

### 3. Acknowledge alert
```bash
curl -X POST http://localhost:5000/api/alerts/ALERT_ID/acknowledge \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "john.doe"}'
```

---

**API Version:** 1.0  
**Last Updated:** 2026-09-12
