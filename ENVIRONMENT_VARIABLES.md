# Environment Variables Guide

Complete reference for all environment variables used in the AIOps platform.

---

## 🔐 JWT_SECRET_KEY

### What is it?
The secret key used to sign and verify JWT authentication tokens. This is the most critical security variable.

### Why it matters?
- If exposed, attackers can forge authentication tokens
- Longer and more random = more secure
- Should be unique per environment
- Never commit to GitHub

### Local Development
```bash
# Simple but NOT secure (dev only)
JWT_SECRET_KEY=dev-secret-key-change-this
```

### Production (SECURE)
Use a cryptographically random string:

**Option 1: Generate with Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: vF9kL2mP7qR4sT6uV8wX1yZ3aBcD5eF6gH9iJ0kL2mN4oP6qR8sT0uV2wX4yZ
```

**Option 2: Generate with OpenSSL**
```bash
openssl rand -hex 32
# Output: a3f5b8c1d9e2f7a4b6c8d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f
```

**Option 3: Use password manager generated key**
```
Generate 32+ character random string
Example: Kj#9$mL@vP2&xQ8!zR4%sT6^uV0*wX3(yZ1-BaC5=De7~Fg9|Hi0+Jk2_Mn4
```

### In Your .env File
```bash
JWT_SECRET_KEY=vF9kL2mP7qR4sT6uV8wX1yZ3aBcD5eF6gH9iJ0kL2mN4oP6qR8sT0uV2wX4yZ
```

### In Docker/Railway/Render
```bash
# Set as environment variable
# Don't include quotes
JWT_SECRET_KEY=vF9kL2mP7qR4sT6uV8wX1yZ3aBcD5eF6gH9iJ0kL2mN4oP6qR8sT0uV2wX4yZ
```

### Security Best Practices
✅ Generate random 32+ character string
✅ Use only alphanumeric + special chars
✅ Never hardcode in source code
✅ Rotate periodically (every 6 months)
✅ Store in secure vault (1Password, LastPass, etc.)
✅ Different keys per environment (dev, staging, prod)

---

## 🌍 FLASK_ENV

### What is it?
Controls Flask application behavior and debugging mode.

### Possible Values

#### Development
```bash
FLASK_ENV=development
# or
FLASK_ENV=dev
```
**Effects:**
- Debug mode ON (code reloads on file changes)
- Verbose error messages
- Interactive debugger available
- NOT SECURE - never use in production
- Slower performance

#### Production
```bash
FLASK_ENV=production
```
**Effects:**
- Debug mode OFF
- Minimal error details (security)
- Fast performance
- Production-grade error handling
- SECURE - required for production

#### Testing
```bash
FLASK_ENV=testing
```
**Effects:**
- Special testing mode
- Used for unit/integration tests
- Disables error catching during request handling

### Recommended Settings

**Local Development:**
```bash
FLASK_ENV=development
DEBUG=True
```

**Staging:**
```bash
FLASK_ENV=production
DEBUG=False
```

**Production:**
```bash
FLASK_ENV=production
DEBUG=False
```

### How to Set

**In .env file:**
```bash
FLASK_ENV=production
```

**In shell:**
```bash
# Linux/Mac
export FLASK_ENV=production

# Windows PowerShell
$env:FLASK_ENV = "production"

# Windows cmd
set FLASK_ENV=production
```

**In Docker:**
```dockerfile
ENV FLASK_ENV=production
```

**In Railway/Render:**
```
FLASK_ENV=production
```

---

## 🖨️ PYTHONUNBUFFERED

### What is it?
Controls Python's output buffering behavior.

### Possible Values

#### Unbuffered (1 or True)
```bash
PYTHONUNBUFFERED=1
# or
PYTHONUNBUFFERED=True
```
**Effects:**
- Print statements appear immediately
- No output buffering
- Real-time log display
- Recommended for Docker/containers

#### Buffered (0 or False)
```bash
PYTHONUNBUFFERED=0
# or  
PYTHONUNBUFFERED=False
```
**Effects:**
- Output is buffered
- Logs appear in chunks
- Slightly better performance
- Can lose logs if app crashes

### Why It Matters?

**Problem (with buffering):**
```python
print("Starting app...")  # Might not appear immediately
app.run()
```
If app crashes, you might not see the print statement!

**Solution (unbuffered):**
```bash
PYTHONUNBUFFERED=1
# Now you see output immediately
```

### Recommended Settings

**Local Development:**
```bash
PYTHONUNBUFFERED=1
```

**Docker/Production:**
```bash
PYTHONUNBUFFERED=1  # Essential for containers
```

**Logging:**
```bash
PYTHONUNBUFFERED=1  # Ensures logs appear immediately
```

### How to Set

**In .env file:**
```bash
PYTHONUNBUFFERED=1
```

**In Docker:**
```dockerfile
ENV PYTHONUNBUFFERED=1
```

**In Railway/Render:**
```
PYTHONUNBUFFERED=1
```

**In docker-compose.yml:**
```yaml
environment:
  PYTHONUNBUFFERED: 1
```

---

## 📦 MONGODB_URI (Optional)

### What is it?
Connection string for MongoDB database (optional).

### Format
```bash
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/

# MongoDB Atlas (Cloud)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/aiops_mvp?retryWrites=true&w=majority

# With authentication
MONGODB_URI=mongodb://user:password@host:27017/database_name
```

### Getting Connection String

**MongoDB Atlas (Recommended):**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Click "Connect"
4. Copy connection string
5. Replace `<password>` with your password

**Example MongoDB Atlas:**
```bash
MONGODB_URI=mongodb+srv://admin:myPassword123@cluster0.abc123.mongodb.net/aiops_mvp?retryWrites=true&w=majority
```

**Local MongoDB:**
```bash
MONGODB_URI=mongodb://localhost:27017/aiops_mvp
```

### When to Set
- Only needed if using MongoDB persistence
- Dashboard works without it (demo mode)
- Required for production data storage

---

## 📧 SMTP Settings (Optional)

### For Email Notifications

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

### Gmail Setup
1. Enable 2-factor authentication
2. Create app password (not account password)
3. Use app password in SMTP_PASSWORD

---

## 🎯 Complete Example .env File

### Development Setup
```bash
# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-for-development-only

# JWT Configuration
JWT_SECRET_KEY=dev-jwt-key-change-this-in-production

# Python Configuration
PYTHONUNBUFFERED=1

# Optional: Database
# MONGODB_URI=mongodb://localhost:27017/aiops_mvp

# Optional: Email
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
```

### Production Setup
```bash
# Flask Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=vF9kL2mP7qR4sT6uV8wX1yZ3aBcD5eF6gH9iJ0kL2mN4oP6qR8sT0uV2wX4yZ

# JWT Configuration (CRITICAL)
JWT_SECRET_KEY=a3f5b8c1d9e2f7a4b6c8d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f

# Python Configuration
PYTHONUNBUFFERED=1

# Database
MONGODB_URI=mongodb+srv://admin:securePassword@cluster0.xyz.mongodb.net/aiops_mvp

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@yourdomain.com
SMTP_PASSWORD=secure-app-password-here

# Optional Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

---

## 🚀 How to Use in Your App

### In Python Code
```python
import os

# Get environment variables
jwt_secret = os.getenv('JWT_SECRET_KEY', 'fallback-dev-key')
flask_env = os.getenv('FLASK_ENV', 'development')
unbuffered = os.getenv('PYTHONUNBUFFERED', '0')

print(f"Running in {flask_env} mode")
print(f"Using JWT secret: {jwt_secret[:20]}...")
```

### In Flask App
```python
from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'
```

### In Docker
```dockerfile
ENV JWT_SECRET_KEY=production-secret-key-here
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
```

### In docker-compose.yml
```yaml
services:
  app:
    environment:
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      FLASK_ENV: ${FLASK_ENV}
      PYTHONUNBUFFERED: 1
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] JWT_SECRET_KEY is 32+ characters
- [ ] JWT_SECRET_KEY is NOT in GitHub
- [ ] FLASK_ENV is set to "production"
- [ ] DEBUG is False
- [ ] PYTHONUNBUFFERED is 1
- [ ] MONGODB_URI has secure password
- [ ] All secrets are in .env file
- [ ] .env file is in .gitignore
- [ ] Environment variables set in deployment platform
- [ ] No credentials in source code

---

## 🚨 Common Mistakes

### ❌ WRONG
```bash
# Don't hardcode secrets
JWT_SECRET_KEY=my-secret-key  # Too short, too simple

# Don't commit .env to GitHub
git add .env  # Never do this!

# Don't use same secret for all environments
PROD_KEY=same-as-dev-key  # Security risk
```

### ✅ RIGHT
```bash
# Use long random strings
JWT_SECRET_KEY=vF9kL2mP7qR4sT6uV8wX1yZ3aBcD5eF6gH9iJ0kL2mN4oP6qR8sT0uV2wX4yZ

# Keep .env file local only
# (Listed in .gitignore)

# Use different keys per environment
DEV_KEY=xxx...
PROD_KEY=yyy...
```

---

## 🔄 Rotating Secrets

### JWT_SECRET_KEY Rotation (Every 6 months)

1. **Generate new key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update in deployment platform:**
   - Railway: Settings → Environment Variables
   - Render: Environment
   - Docker: .env file

3. **Redeploy app:**
   ```bash
   git push origin main  # If using CD
   ```

4. **Old tokens expire after 7 days:**
   - Users automatically re-login
   - No manual action needed

---

## 📝 Quick Reference

| Variable | Local | Production | Required |
|----------|-------|-----------|----------|
| JWT_SECRET_KEY | dev-key | 32+ char random | YES |
| FLASK_ENV | development | production | YES |
| PYTHONUNBUFFERED | 1 | 1 | YES |
| MONGODB_URI | localhost:27017 | MongoDB Atlas | NO* |
| DEBUG | True | False | NO** |

*Only needed for persistent storage
**Flask manages automatically

---

## 🎯 Next Steps

1. **Generate secure JWT_SECRET_KEY**
2. **Create .env file with all variables**
3. **Add .env to .gitignore**
4. **Set variables in deployment platform**
5. **Test that app runs with variables**

---

**Your environment is secure and ready!** 🔒
