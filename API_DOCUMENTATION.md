# Nexus AIOps API Documentation

## Access Swagger UI

Once the server is running, access the interactive API documentation at:

**http://localhost:5000/api/docs**

This provides an interactive Swagger UI where you can:
- View all API endpoints
- See request/response schemas
- Try out API calls directly
- View authentication requirements
- See error responses

## API Base URL

```
http://localhost:5000/api
```

## Authentication

### JWT Token Authentication

Most endpoints require a JWT (JSON Web Token) for authentication.

**Step 1: Login to get token**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "email": "admin@nexus.local",
    "role": "admin"
  }
}
```

**Step 2: Use token in subsequent requests**
```bash
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
  http://localhost:5000/api/user/profile
```

## API Endpoints Overview

### Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/login` | No | User login |
| POST | `/auth/signup` | No | User registration |
| POST | `/auth/verify-email` | No | Verify email address |
| POST | `/auth/forgot-password` | No | Request password reset |
| POST | `/auth/password-reset` | No | Reset password with code |

### User Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/user/profile` | Yes | Get user profile |
| POST | `/user/profile` | Yes | Update user profile |
| POST | `/user/change-password` | Yes | Change password |
| DELETE | `/admin/users/<username>` | Admin | Delete user |

### Dashboard Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/overview/dashboard` | Yes | Get dashboard overview |
| GET | `/metrics/summary` | Yes | Get metrics summary |
| GET | `/metrics/all` | Yes | Get all metrics |
| GET | `/metrics/<metric_name>` | Yes | Get specific metric |

### Incidents Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/incidents` | Yes | List all incidents |
| GET | `/incidents/<id>` | Yes | Get incident details |
| POST | `/incidents/<id>/remediate` | Yes | Trigger remediation |
| POST | `/incidents/<id>/analyze` | Yes | Get AI analysis |

### Topology Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/topology/services` | Yes | List services |
| GET | `/topology/dependencies` | Yes | Get service dependencies |
| GET | `/topology/summary` | Yes | Get topology summary |
| GET | `/topology/service/<id>` | Yes | Get service details |

### Alerts Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/alerts/rules` | Yes | List alert rules |
| POST | `/alerts/rules` | Admin | Create alert rule |
| PUT | `/alerts/rules/<id>` | Admin | Update alert rule |
| DELETE | `/alerts/rules/<id>` | Admin | Delete alert rule |

### SLO Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/slos` | Yes | List SLOs |
| POST | `/slos` | Admin | Create SLO |
| PUT | `/slos/<id>` | Admin | Update SLO |
| DELETE | `/slos/<id>` | Admin | Delete SLO |

## Common Response Formats

### Success Response (200 OK)
```json
{
  "status": "success",
  "data": { /* response data */ }
}
```

### Error Response (4xx/5xx)
```json
{
  "error": "Error message",
  "status_code": 400
}
```

### Paginated Response
```json
{
  "data": [ /* items */ ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 500 | Server Error | Internal server error |

## Rate Limiting

Currently no rate limiting is implemented. Production deployments should add rate limiting using Flask-Limiter.

## CORS

CORS is enabled for all origins. In production, configure CORS to specific domains in the CORS configuration.

## Security Headers

All responses include security headers:
- `Strict-Transport-Security`: Enforces HTTPS for 1 year
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: Prevents XSS attacks
- `Content-Security-Policy`: Restricts resource loading

## WebSocket Endpoints

Real-time data is available via WebSocket connections:

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for real-time events
socket.on('incident_alert', (data) => {
  console.log('New incident:', data);
});

socket.on('metric_update', (data) => {
  console.log('Metrics updated:', data);
});
```

## Example Requests

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Get Dashboard
```bash
curl -X GET http://localhost:5000/api/overview/dashboard \
  -H "Authorization: Bearer <TOKEN>"
```

### Get Incidents
```bash
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer <TOKEN>"
```

### Create Alert Rule (Admin)
```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -d '{
    "name": "High CPU Alert",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 80,
    "severity": "warning",
    "duration": 300
  }'
```

### Update User Profile
```bash
curl -X POST http://localhost:5000/api/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "department": "Operations"
  }'
```

## Testing the API

### Using cURL
All examples above use cURL and can be run from the terminal.

### Using Postman
1. Import the Swagger spec from `http://localhost:5000/apispec.json`
2. Create environment with:
   - `base_url`: http://localhost:5000
   - `token`: (get from login response)
3. Use pre-built requests

### Using Python
```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']

# Get dashboard
headers = {'Authorization': f'Bearer {token}'}
dashboard = requests.get('http://localhost:5000/api/overview/dashboard', headers=headers)
print(dashboard.json())
```

### Using JavaScript/Node.js
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});

const { token } = await loginResponse.json();

// Get dashboard
const dashResponse = await fetch('http://localhost:5000/api/overview/dashboard', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const dashboard = await dashResponse.json();
console.log(dashboard);
```

## API Versioning

Current API version: **1.0.0**

The API follows semantic versioning. Breaking changes will increment the major version.

## Support & Issues

For API issues or questions:
1. Check the Swagger documentation at `/api/docs`
2. Review example requests above
3. Check server logs for detailed error messages
4. Verify authentication token is valid and not expired

---

**Last Updated:** 2026-09-16
**Version:** 1.0.0
