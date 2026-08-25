# JWT Token Generation Guide - Nexus AIOps

## Quick Methods to Get JWT Token

### Method 1: Login via API (Easiest)

```bash
# Windows (Command Prompt)
curl -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Windows (PowerShell)
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body

# Mac/Linux
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNjk3NzA1NzMwLCJleHAiOjE2OTgzMTA1MzB9.xyzAbcDefGhijKlmNopQrstUvwXyzAbcDefGhij",
  "expires_in": 604800
}
```

---

### Method 2: Python Script (Programmatic)

```python
# generate_token.py
import jwt
from datetime import datetime, timedelta

# Your app's secret key
SECRET_KEY = "dev-secret-key-change-in-production"

# Token payload
payload = {
    'user_id': 'admin',
    'username': 'admin',
    'role': 'admin',
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(days=7)
}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

print("JWT Token:")
print(token)
print("\nToken expires in 7 days")
```

**Run it:**
```bash
python generate_token.py
```

---

### Method 3: Use the App's Token Generation (Python)

```python
# Inside your app
import sys
sys.path.insert(0, '.')
from nexus_app import generate_jwt_token

# Generate token for admin user
token = generate_jwt_token('admin', 'admin', 'admin', expires_in_days=7)
print(f"Token: {token}")
```

---

## Generate Tokens for Different Users

### All User Types Available

```bash
# Admin user (Full access)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Operator user (Operational access)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"operator","password":"operator123"}'

# Viewer user (Read-only access)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","password":"viewer123"}'
```

---

## Using the Token

### Add to API Requests

```bash
# Store token in variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in requests (Windows CMD)
curl -X GET http://localhost:5000/api/incidents ^
  -H "Authorization: Bearer %TOKEN%"

# Use in requests (Mac/Linux)
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer $TOKEN"

# Use in requests (PowerShell)
curl -X GET http://localhost:5000/api/incidents `
  -H "Authorization: Bearer $TOKEN"
```

### In JavaScript/Fetch

```javascript
// Get token from login
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    username: 'admin', 
    password: 'admin123' 
  })
});

const data = await response.json();
const token = data.token;

// Store in localStorage
localStorage.setItem('token', token);

// Use in subsequent requests
const apiResponse = await fetch('http://localhost:5000/api/incidents', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### In Python Requests

```python
import requests
import json

# Login to get token
login_response = requests.post(
    'http://localhost:5000/api/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)

token = login_response.json()['token']
print(f"Token: {token}")

# Use token in subsequent requests
headers = {'Authorization': f'Bearer {token}'}
incidents = requests.get(
    'http://localhost:5000/api/incidents',
    headers=headers
)

print(incidents.json())
```

---

## Token Details & Decoding

### Decode a Token (View Claims)

```bash
# Online tool
# Go to https://jwt.io/
# Paste your token to see decoded contents

# OR use Python
python -c "
import jwt
import base64
import json

token = 'your-token-here'

# Decode without verification (to see contents)
try:
    decoded = jwt.decode(token, options={'verify_signature': False})
    print(json.dumps(decoded, indent=2))
except Exception as e:
    print(f'Error: {e}')
"
```

### Token Structure

JWT tokens have 3 parts separated by dots: `header.payload.signature`

**Example:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 
  . 
eyJ1c2VyX2lkIjoiYWRtaW4iLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0 
  . 
xyzAbcDefGhijKlmNopQrstUvwXyzAbcDefGhij
```

**Decoded Payload:**
```json
{
  "user_id": "admin",
  "username": "admin",
  "role": "admin",
  "iat": 1697705730,
  "exp": 1698310530
}
```

---

## Token Expiration & Refresh

### Default Expiration
- **Duration:** 7 days
- **Seconds:** 604,800 seconds

### Refresh Token

```bash
# Get a new token before the old one expires
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CURRENT_TOKEN" \
  -d '{}'
```

### Check Token Expiration

```bash
# Token expires at timestamp: 1698310530
# Convert to readable date (Unix timestamp)

# Online: https://www.unixtimestamp.com/
# Or use Python:
python -c "
from datetime import datetime
timestamp = 1698310530
date = datetime.fromtimestamp(timestamp)
print(f'Token expires: {date}')
"
```

---

## Generate Custom Token (Python)

```python
# custom_token.py
import jwt
from datetime import datetime, timedelta

def generate_custom_token(user_id, username, role, secret_key, expires_days=7):
    """Generate a JWT token with custom parameters"""
    
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_days)
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

# Usage
SECRET_KEY = "dev-secret-key-change-in-production"

# Generate tokens for different users
admin_token = generate_custom_token('admin', 'admin', 'admin', SECRET_KEY)
operator_token = generate_custom_token('op1', 'operator', 'operator', SECRET_KEY)
viewer_token = generate_custom_token('view1', 'viewer', 'viewer', SECRET_KEY)

print(f"Admin Token:\n{admin_token}\n")
print(f"Operator Token:\n{operator_token}\n")
print(f"Viewer Token:\n{viewer_token}\n")

# With custom expiration (3 days)
short_token = generate_custom_token('admin', 'admin', 'admin', SECRET_KEY, expires_days=3)
print(f"3-Day Token:\n{short_token}\n")
```

**Run it:**
```bash
python custom_token.py
```

---

## API Endpoints for Token Management

### Login & Get Token
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "token": "eyJhbGc...",
  "expires_in": 604800
}
```

### Refresh Token
```
POST /api/auth/refresh
Authorization: Bearer <current_token>

Response:
{
  "token": "eyJhbGc...",
  "expires_in": 604800
}
```

---

## Available Credentials

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| admin | admin123 | Admin | All features |
| operator | operator123 | Operator | Operational features |
| viewer | viewer123 | Viewer | Read-only access |

---

## Token Security Best Practices

### Development
✅ OK to use default secret key  
✅ OK to hardcode credentials in dev  
✅ OK to share demo tokens  

### Production (Render)
❌ **MUST** change `JWT_SECRET_KEY`  
❌ **MUST** set in environment variables  
❌ **MUST NOT** hardcode secrets  
❌ **MUST NOT** share tokens  

### Set Secret Key in Render

1. Go to Render Dashboard
2. Service → Environment
3. Add variable:
   ```
   JWT_SECRET_KEY=your-strong-random-key-12345-CHANGE-THIS
   ```
4. Redeploy

**Generate strong secret:**
```bash
# Windows PowerShell
-join ((0..31) | ForEach-Object { [char][int](33..126 | Get-Random) })

# Mac/Linux
openssl rand -base64 32
```

---

## Complete Example Script

```bash
#!/bin/bash
# get_token.sh - Get JWT token and use it

# Get token
echo "Getting JWT token..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

# Extract token
TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"
echo ""

# Use token to get incidents
echo "Fetching incidents..."
curl -s -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer $TOKEN" | json_pp

# Use token to get approvals
echo "Fetching approvals..."
curl -s -X GET http://localhost:5000/api/approvals?status=pending \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Run it:**
```bash
chmod +x get_token.sh
./get_token.sh
```

---

## Troubleshooting

### "Invalid credentials"
```bash
# Check credentials
# Admin: admin / admin123
# Operator: operator / operator123
# Viewer: viewer / viewer123
```

### "Missing authorization header"
```bash
# Add Authorization header to requests
-H "Authorization: Bearer TOKEN"
```

### "Token expired"
```bash
# Get a new token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### "Invalid token signature"
```bash
# Token was generated with different secret key
# Make sure JWT_SECRET_KEY matches
```

---

## Summary

| Task | Command |
|------|---------|
| **Get Token** | `curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'` |
| **Decode Token** | Go to https://jwt.io/ and paste token |
| **Use Token** | Add `Authorization: Bearer TOKEN` header to requests |
| **Refresh Token** | `curl -X POST http://localhost:5000/api/auth/refresh -H "Authorization: Bearer TOKEN"` |
| **Generate Custom** | Run `python custom_token.py` |
| **Check Expiration** | Decode token and check `exp` field |

---

## Quick Copy-Paste

```bash
# Get token
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4

# Use token in request
TOKEN="your-token-here"
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer $TOKEN"
```

---

**Ready to authenticate! 🔐**
