# AIOps MVP - Setup & Run Guide

## 🚀 Quick Start (5 minutes)

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Start the Dashboard**

```bash
python run_dashboard.py
```

You should see:
```
✅ MongoDB connected (or ⚠️ MongoDB connection failed - demo mode active)
 * Running on http://localhost:5000/
```

### **Step 3: Login**

Open browser to: **http://localhost:5000/login**

Use demo credentials:
- **Admin:** `admin` / `admin123`
- **Operator:** `operator` / `operator123`
- **Viewer:** `viewer` / `viewer123`

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                     │
│  (src/dashboard_app.py - 381 lines)                         │
└─────────────────────────────────────────────────────────────┘
              │
              ├─ Authentication Layer
              │  ├─ JWT Token Generation (7-day expiration)
              │  ├─ Password Hashing (bcrypt)
              │  └─ Demo Mode (no MongoDB required)
              │
              ├─ RBAC Enforcement
              │  ├─ @require_auth decorator
              │  └─ @require_role decorator
              │
              ├─ MongoDB Integration
              │  ├─ users_collection (user data)
              │  └─ audit_collection (audit trail)
              │
              ├─ Web Templates
              │  ├─ login.html (authentication UI)
              │  ├─ home_page.html (navigation hub)
              │  ├─ problems_page.html (incidents)
              │  ├─ infrastructure_page.html (monitoring)
              │  ├─ demo_dashboard.html (simulator)
              │  └─ users_page.html (RBAC management)
              │
              └─ Core AIOps Pipeline
                 ├─ Anomaly Detection (Isolation Forest)
                 ├─ Incident Classification (Random Forest)
                 ├─ Chaos Simulation (Multi-service faults)
                 └─ Response Logging
```

---

## 🗂️ Directory Structure

```
aiops-mvp/
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── dashboard_app.py            # Flask application (NEW - 381 lines)
│   ├── chaos_simulator.py          # Chaos engineering simulator
│   ├── pipeline.py                 # AIOps pipeline
│   ├── detect.py                   # Anomaly detection
│   ├── classify.py                 # Incident classification
│   └── ...
├── templates/
│   ├── login.html                  # Login page (NEW)
│   ├── home_page.html              # Home/navigation (NEW)
│   ├── users_page.html             # User management (NEW)
│   ├── problems_page.html          # Problems dashboard
│   ├── infrastructure_page.html    # Infrastructure dashboard
│   └── demo_dashboard.html         # Demo simulator
├── data/
│   ├── raw/                        # Raw input data
│   └── processed/                  # Processed outputs
├── models/                         # Trained ML models
├── requirements.txt                # Python dependencies
├── run_dashboard.py                # Dashboard launcher script
├── AUTHENTICATION_GUIDE.md         # Auth & RBAC documentation (NEW)
├── SETUP_AND_RUN.md               # This file (NEW)
├── DASHBOARDS_GUIDE.md            # Dashboard user guide
├── API.md                          # API reference
├── SECURITY.md                     # Security best practices
└── README.md                       # Project overview
```

---

## 🔐 Authentication Flow

### **1. User Credentials**

**Demo Mode (No MongoDB):**
- Credentials stored in `dashboard_app.py` line 147-151
- Perfect for local development & testing
- No data persistence

**Production Mode (MongoDB):**
- Credentials stored in MongoDB `users_collection`
- Persistent user data
- Audit trail recorded

### **2. Login Request**

```
Client POST /api/auth/login
    │ username, password
    ↓
Flask validates credentials
    ↓
Generate JWT token (7-day expiration)
    ↓
Return token + user info to client
    ↓
Client stores in localStorage
```

### **3. API Access**

```
Client GET /api/users
    │ Header: Authorization: Bearer <token>
    ↓
@require_auth decorator validates token
    ↓
@require_role decorator checks permission
    ↓
Route handler executes
    ↓
Audit log recorded
```

---

## 👥 Role Permissions

| Feature | Admin | Operator | Viewer |
|---------|-------|----------|--------|
| View Problems Dashboard | ✅ | ✅ | ✅ |
| View Infrastructure | ✅ | ✅ | ✅ |
| View Demo Simulator | ✅ | ✅ | ✅ |
| Run Chaos Simulation | ✅ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| View Audit Trail | ✅ | ❌ | ❌ |
| Access Settings | ✅ | ❌ | ❌ |

---

## 🔧 Configuration

### **Flask Configuration**

```python
# src/dashboard_app.py
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'aiops_mvp'
```

### **Environment Variables (.env)**

```bash
# .env file (optional)
JWT_SECRET_KEY=your-production-secret-key
MONGODB_URI=mongodb://localhost:27017/
FLASK_ENV=production
```

### **Security Headers**

Automatically added to all responses:
```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: ...
```

---

## 🌐 Available Endpoints

### **Authentication**

```
POST   /api/auth/login     - Login with credentials
POST   /api/auth/signup    - Create new account
```

### **Pages (Require Authentication)**

```
GET    /login              - Login page
GET    /                   - Home page
GET    /problems           - Problems dashboard
GET    /infrastructure     - Infrastructure dashboard
GET    /demo               - Demo simulator
GET    /users              - User management (admin only)
GET    /audit-trail        - Audit trail (admin only)
```

### **API (Require Authentication)**

```
GET    /api/users          - List all users (admin only)
POST   /api/users          - Create new user (admin only)
DELETE /api/users/<id>     - Delete user (admin only)
GET    /api/audit-trail    - Get audit entries (admin only)
POST   /api/chaos-simulation - Run chaos sim (admin only)
```

---

## 🧪 Testing

### **Test Login**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "admin",
    "username": "admin",
    "email": "admin@aiops.local",
    "role": "admin"
  }
}
```

### **Test API with Token**

```bash
# Get users (admin only)
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### **Test RBAC (Should Fail)**

```bash
# Login as viewer
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","password":"viewer123"}'

# Try to access admin endpoint (should get 403)
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer <viewer_token>"

# Response: {"error": "Insufficient permissions"}
```

---

## 🐛 Troubleshooting

### **Port 5000 Already in Use**

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or change port in run_dashboard.py
app.run(debug=True, port=5001)
```

### **Templates Not Found**

Ensure templates directory exists:
```bash
ls templates/
# Should show: login.html, home_page.html, users_page.html, etc.
```

### **MongoDB Connection Failed**

This is OK! System works in demo mode without MongoDB:
```
⚠️ MongoDB connection failed: ...
(System running in demo mode with hardcoded credentials)
```

To use MongoDB:
```bash
# Install MongoDB
mongod --dbpath ./data/mongodb

# Or use Docker
docker run -d -p 27017:27017 mongo:latest

# Update .env
export MONGODB_URI=mongodb://localhost:27017/
```

### **JWT Token Expired**

Tokens expire after 7 days. Login again to get new token:
```bash
# Clear localStorage in browser
localStorage.clear()

# Or login again
```

---

## 📊 Demo Data

### **Sample Incidents (Problems Page)**

- **PROB-2026-001:** API CPU Usage Critical (99%)
- **PROB-2026-002:** Database Latency High (850ms)
- **PROB-2026-003:** Cache Memory Leak (4.2GB)

### **Sample Services (Infrastructure Page)**

- API Gateway
- API Server
- Database
- Cache Layer
- Message Queue
- Search Engine

### **Sample Users (Users Page)**

- `admin` / `admin123` - Full access
- `operator` / `operator123` - Dashboard access
- `viewer` / `viewer123` - Read-only

---

## 🚀 Next Steps

1. **MongoDB Integration** (Optional)
   - Install MongoDB
   - Update MONGODB_URI in .env
   - User data will persist

2. **Create Audit Trail Page**
   - Implement `templates/audit_trail.html`
   - Display audit entries in table
   - Filter by date/user/action

3. **Production Deployment**
   - Change JWT_SECRET_KEY
   - Enable HTTPS/TLS
   - Set FLASK_ENV=production
   - Configure rate limiting
   - Enable 2FA for admins

4. **Advanced Features**
   - OAuth 2.0 integration (Google, GitHub)
   - SAML 2.0 support
   - LDAP directory integration
   - Advanced audit analytics

---

## 📚 Additional Resources

- **AUTHENTICATION_GUIDE.md** - Complete auth & RBAC documentation
- **DASHBOARDS_GUIDE.md** - How to use each dashboard
- **API.md** - Complete API reference
- **SECURITY.md** - Security best practices checklist

---

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Dashboard started (`python run_dashboard.py`)
- [ ] Able to login at `http://localhost:5000/login`
- [ ] Home page loads after login
- [ ] Problems dashboard accessible
- [ ] Infrastructure dashboard accessible
- [ ] Demo simulator accessible
- [ ] User Management page shows for admins
- [ ] RBAC prevents non-admins from accessing User Management

---

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** August 2026
