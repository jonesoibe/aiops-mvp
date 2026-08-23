# AIOps MVP - Security Hardening Guide

This document outlines the 21 security best practices implemented and recommended for the AIOps MVP system.

## 1. Authentication & Authorization

### ✅ Hide API Keys
**Status:** Implemented

Store sensitive credentials in environment variables, not hardcoded.

```bash
# Create .env file
cp .env.example .env

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('AIOPS_API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

### ✅ Purge Git Secrets
**Status:** Partially Implemented

Remove sensitive data from git history:

```bash
# Install git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && make install

# Scan for secrets
git secrets --scan

# Prevent commits with secrets
git secrets --install
```

### ✅ Bearer Token Authentication
**Status:** Implemented

All API endpoints require Bearer token:

```bash
# Generate token (in production use JWT with expiration)
TOKEN="your_secure_token_here"

# Call API with auth
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/metrics
```

### ✅ Secure Session Cookies
**Status:** Implemented

Configure Flask to use secure cookies:

```python
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JS access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour expiration
)
```

### ✅ Enforce Server-Side Authentication
**Status:** Implemented

Never trust client-side auth. Always verify on server:

```python
@app.route('/api/protected')
@require_auth  # Server-side decorator
def protected_endpoint():
    # Token is verified server-side before execution
    return jsonify({'status': 'success'})
```

### ⏳ Hash Passwords
**Status:** Recommended

Install bcrypt for password hashing:

```bash
pip install bcrypt
```

```python
import bcrypt

# Hash password
password = "user_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verify password
bcrypt.checkpw(password.encode(), hashed)
```

## 2. Data Protection

### ✅ Add Security Headers
**Status:** Implemented

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

### ✅ Content Security Policy (CSP)
**Status:** Implemented

Prevent XSS attacks:

```python
response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline'"
)
```

### ✅ HTTPS Enforcement
**Status:** Recommended

In production, force HTTPS:

```python
from flask_talisman import Talisman

Talisman(app, force_https=True, strict_transport_security=True)
```

Install: `pip install flask-talisman`

### ⏳ Encrypt Sensitive Data
**Status:** Recommended

For database encryption at rest:

```bash
pip install cryptography
```

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_data = cipher.encrypt(b"sensitive_info")
decrypted_data = cipher.decrypt(encrypted_data)
```

### ⏳ Row-Level Security
**Status:** Recommended

Control data access by user role:

```python
def check_row_access(user_id, row_id):
    # Verify user can access this row
    user = User.query.get(user_id)
    row = Data.query.get(row_id)
    return row.owner_id == user.id
```

## 3. Input Validation & Sanitization

### ✅ Validate All Input
**Status:** Implemented

```python
from flask import request

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    
    # Validate data_source
    if data.get('data_source') not in ['smd', 'aiops']:
        return {'error': 'Invalid data_source'}, 400
    
    # Validate types
    if not isinstance(data.get('machine_id'), str):
        return {'error': 'Invalid machine_id'}, 400
    
    return {'status': 'success'}
```

### ✅ Parameterized Queries
**Status:** Implemented

Prevent SQL injection:

```python
# ❌ Bad - SQL Injection vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Good - Parameterized
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### ✅ Escape User Content
**Status:** Recommended

In HTML templates, use Jinja2 auto-escaping:

```html
<!-- Jinja2 auto-escapes by default -->
<p>{{ user_input }}</p>  <!-- Safe from XSS -->

<!-- If you need raw HTML, explicitly mark it -->
<p>{{ trusted_content | safe }}</p>
```

### ⏳ Restrict File Uploads
**Status:** Recommended

```python
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'json', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file'}, 400
    
    file = request.files['file']
    
    # Validate filename
    if not file.filename or '.' not in file.filename:
        return {'error': 'Invalid filename'}, 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {'error': 'File type not allowed'}, 400
    
    # Validate size
    if len(file.read()) > MAX_FILE_SIZE:
        return {'error': 'File too large'}, 400
    
    file.seek(0)  # Reset file pointer
    filename = secure_filename(file.filename)
    file.save(f'uploads/{filename}')
    
    return {'status': 'success', 'filename': filename}
```

## 4. API Security

### ✅ Trim API Responses
**Status:** Implemented

Return only necessary fields:

```python
@app.route('/api/user/<user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    
    # Only return public fields
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
        # Do NOT return: password_hash, secret_key, etc.
    })
```

### ✅ Rate Limiting
**Status:** Recommended

Install Flask-Limiter:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chaos-simulation', methods=['POST'])
@limiter.limit("5 per hour")  # 5 simulations per hour
@require_auth
def run_chaos():
    # Prevent abuse
    return {'status': 'success'}
```

### ✅ CORS Security
**Status:** Implemented

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### ⏳ Bot Protection
**Status:** Recommended

Implement CAPTCHA for user-facing endpoints:

```bash
pip install flask-recaptcha
```

```python
from flask_recaptcha import ReCaptcha

recaptcha = ReCaptcha(app=app)

@app.route('/login', methods=['POST'])
@recaptcha.verify
def login():
    if not recaptcha.is_valid:
        return {'error': 'CAPTCHA verification failed'}, 400
    
    # Proceed with login
    return {'status': 'success'}
```

## 5. Dependency & Compliance

### ✅ Scan Dependencies
**Status:** Implemented

Install security scanners:

```bash
pip install safety bandit pip-audit
```

Scan for vulnerabilities:

```bash
# Check for known vulnerabilities
safety check

# Find security issues in code
bandit -r src/

# Audit pip packages
pip-audit
```

Add to CI/CD pipeline:

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run safety check
        run: |
          pip install safety
          safety check
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
```

### ✅ API Documentation (Swagger)
**Status:** Implemented

OpenAPI/Swagger docs available at:
- `GET /api/docs` - JSON schema
- `GET /api/openapi.json` - OpenAPI 3.0 spec

View in Swagger UI:

```bash
# Install swagger-ui-py
pip install flask-swagger-ui

# Access at http://localhost:5000/api/swagger
```

### ⏳ Logging & Audit Trail
**Status:** Recommended

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

handler = RotatingFileHandler('logs/aiops.log', 
                             maxBytes=10000000, 
                             backupCount=10)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log all API calls
@app.before_request
def log_request():
    logger.info(f"API Call: {request.method} {request.path} - IP: {request.remote_addr}")
    logger.info(f"User: {request.headers.get('Authorization', 'unknown')}")

@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code}")
    return response
```

## 6. Environment Setup

### Create `.env` file:

```bash
# API Keys
AIOPS_API_KEY=your_secure_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=aiops_user
DB_PASSWORD=secure_password
DB_NAME=aiops_db

# Security
FLASK_ENV=production
SECRET_KEY=your_secret_key
SESSION_COOKIE_SECURE=true

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_BACKEND_STORE_URI=sqlite:///mlruns.db
```

### Load in application:

```python
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
```

## 7. Deployment Checklist

- [ ] All secrets moved to environment variables
- [ ] HTTPS enabled on production server
- [ ] Security headers configured
- [ ] API authentication enabled
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Logging enabled for audit trail
- [ ] Dependencies scanned for vulnerabilities
- [ ] CORS properly configured
- [ ] Database encryption enabled
- [ ] Regular backups configured
- [ ] Monitoring & alerts set up

## 8. Further Reading

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Last Updated:** August 2026
**Author:** AIOps Team
