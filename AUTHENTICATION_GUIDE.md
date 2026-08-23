# AIOps MVP - Authentication & RBAC Guide

## 🔐 Complete Security Implementation

Your AIOps MVP system now includes enterprise-grade authentication with Role-Based Access Control (RBAC), MongoDB integration, and comprehensive audit logging.

---

## 📋 Quick Start

### **Default Demo Accounts**

Use these credentials to test the system without MongoDB:

| Username | Password | Role | Access Level |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full system access |
| `operator` | `operator123` | Operator | Dashboard & incident management |
| `viewer` | `viewer123` | Viewer | Read-only access |

### **Login Steps**

1. Navigate to: `http://localhost:5000/login`
2. Enter credentials from table above
3. Click "Sign In"
4. You'll be redirected to the home page with full access based on your role

---

## 👥 Role-Based Access Control (RBAC)

### **Role Definitions**

#### **🔴 Admin**
- **Full system access**
- User management (create, edit, delete users)
- Access to all dashboards and features
- Audit trail review
- System settings configuration
- API access with `admin` role requirement

**Permissions:**
- ✅ View all dashboards (Problems, Infrastructure, Demo)
- ✅ Manage users (create, update, delete)
- ✅ View audit trail
- ✅ Run chaos simulations
- ✅ Access settings & configuration
- ✅ API access to all endpoints

#### **🟠 Operator**
- **Dashboard access & incident management**
- Can acknowledge and resolve problems
- Can monitor infrastructure
- Can run analysis
- Cannot manage users or access audit logs

**Permissions:**
- ✅ View Problems dashboard
- ✅ View Infrastructure dashboard
- ✅ View Demo simulator
- ✅ Run chaos simulations
- ✅ Access metrics APIs
- ❌ Cannot create/delete users
- ❌ Cannot access admin features
- ❌ Cannot view audit trail

#### **🔵 Viewer**
- **Read-only access**
- Can view all dashboards
- Cannot make changes or execute actions
- Passive monitoring only

**Permissions:**
- ✅ View Problems dashboard (read-only)
- ✅ View Infrastructure dashboard (read-only)
- ✅ View Demo simulator
- ✅ View metrics (read-only)
- ❌ Cannot create/modify/delete anything
- ❌ Cannot run simulations
- ❌ Cannot access admin features

---

## 🔐 Authentication System

### **Login Flow**

```
User credentials
    ↓
Dashboard_app.py /api/auth/login
    ↓
Verify username & password
    ↓
Generate JWT token (valid 7 days)
    ↓
Return token + user info
    ↓
Client stores token in localStorage
    ↓
Token sent in Authorization header for API calls
```

### **Token Structure**

JWT tokens include:
- `user_id` - Unique user identifier
- `username` - Display username
- `role` - User role (admin/operator/viewer)
- `exp` - Expiration (7 days from issue)

**Example Usage:**
```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/problems
```

### **Password Security**

- Passwords hashed using **bcrypt** with salt
- Stored as hashed values only (never plaintext)
- Demo mode stores passwords in memory only
- Production mode uses MongoDB for secure storage

---

## 👥 User Management

### **Creating Users (Admin Only)**

**Via Web UI:**
1. Login as Admin
2. Click "User Management" in admin section
3. Fill in user details:
   - Username
   - Email
   - Password
   - Role (Admin/Operator/Viewer)
4. Click "Create User"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "secure_password",
    "role": "operator"
  }'
```

### **User Database Schema (MongoDB)**

```javascript
{
  _id: ObjectId,
  username: "operator",
  email: "operator@example.com",
  password_hash: "$2b$12$...",  // bcrypt hash
  role: "operator",              // admin/operator/viewer
  active: true,
  created_at: ISODate,
  last_login: ISODate
}
```

---

## 📋 Audit Trail

### **What Gets Logged**

Every action is logged with:
- **Timestamp** - When action occurred
- **User** - Who performed the action
- **Action** - Type of action (login, user_created, access_denied, etc.)
- **Details** - Additional context
- **IP Address** - Source IP
- **Endpoint** - API/page accessed
- **Method** - HTTP method (GET, POST, DELETE)

### **Logged Actions**

- `login_success` - Successful login
- `login_failed` - Failed login attempt
- `user_created` - New user created
- `user_deleted` - User deleted
- `user_updated` - User modified
- `access_denied` - Unauthorized access attempt
- `chaos_simulation_started` - Simulation started
- `chaos_simulation_error` - Simulation error
- `api_call` - API endpoint accessed

### **Viewing Audit Trail (Admin Only)**

**Via Web UI:**
1. Click "Audit Trail" in admin section
2. View all system actions with timestamps
3. Filter by user, action, or date

**Via API:**
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:5000/api/audit-trail?limit=100
```

### **Audit Database Schema (MongoDB)**

```javascript
{
  _id: ObjectId,
  timestamp: ISODate,
  action: "login_success",
  user: "admin",
  details: "Additional info",
  ip: "192.168.1.100",
  endpoint: "/api/users",
  method: "GET"
}
```

---

## 🔗 Navigation & Access

### **Home Page (/)**
- Shows all available dashboards
- Displays user info and role in navbar
- Admin section visible only to admins

### **Dashboard Links**
- **Problems** (`/problems`) - Incident management (all authenticated users)
- **Infrastructure** (`/infrastructure`) - System monitoring (all users)
- **Demo** (`/demo`) - Incident simulator (all users)

### **Admin-Only Links**
- **User Management** (`/users`) - Admin only
- **Audit Trail** (`/audit-trail`) - Admin only
- **Settings** (`/settings`) - Admin only (coming soon)

---

## 🛡️ Security Features

### **Implemented**

✅ **JWT Authentication**
- Stateless token-based auth
- 7-day expiration
- Secure token generation

✅ **Password Security**
- bcrypt hashing with salt
- Never stored in plaintext
- Strong password requirements

✅ **Role-Based Access Control**
- Three-tier permission system
- Decorator-based enforcement
- Fine-grained API control

✅ **Audit Logging**
- Complete action tracking
- MongoDB persistence
- Timestamp & IP logging

✅ **Security Headers**
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- Strict-Transport-Security
- Content-Security-Policy

✅ **CORS Protection**
- Flask-CORS configured
- Origin validation
- Credential handling

### **Recommended for Production**

⏳ **HTTPS/TLS**
- Required for all deployments
- Use Nginx reverse proxy
- Let's Encrypt certificates

⏳ **MongoDB SSL/TLS**
- Secure database connections
- Authentication credentials
- Network isolation

⏳ **Rate Limiting**
- Implement on login endpoint
- Prevent brute force attacks
- Track failed attempts

⏳ **2FA/MFA**
- Two-factor authentication
- TOTP or email-based
- Enhanced security for admins

---

## ⚙️ Configuration

### **Environment Variables**

Create `.env` file:

```bash
# JWT Secret (change in production!)
JWT_SECRET_KEY=your-secret-key-change-this

# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=production-secret-key

# Session Configuration
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### **Development (Demo Mode)**

Without MongoDB:
- Uses demo accounts (admin/operator/viewer)
- Users stored in memory
- No persistence between restarts
- Perfect for testing & demos

### **Production (MongoDB Mode)**

With MongoDB:
- User data persisted
- Audit trail stored
- Scalable architecture
- Enterprise-ready

---

## 🚀 Deploy with MongoDB

### **1. Start MongoDB**

```bash
# Local MongoDB
mongod --dbpath ./data/mongodb

# Docker
docker run -d -p 27017:27017 --name mongo mongo:latest
```

### **2. Set Environment Variable**

```bash
export MONGODB_URI=mongodb://localhost:27017/
```

### **3. Update Dashboard App**

```python
from pymongo import MongoClient

mongo_client = MongoClient(os.getenv('MONGODB_URI'))
db = mongo_client['aiops_mvp']
```

### **4. Create Initial Users**

```bash
python scripts/create_users.py
```

---

## 🔄 API Authentication Flow

### **Step 1: Login**
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

Response:
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

### **Step 2: Store Token**
```javascript
localStorage.setItem('token', response.token);
localStorage.setItem('user', JSON.stringify(response.user));
```

### **Step 3: Use Token in Requests**
```javascript
fetch('/api/users', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### **Step 4: Token Validation**
```python
@app.route('/api/users')
@require_auth
def get_users():
    # Token automatically validated
    # request.user contains decoded payload
    return jsonify({'users': [...]})
```

---

## 🐛 Troubleshooting

### **"Invalid credentials" on Login**

- Check username/password in demo accounts table
- Verify MongoDB connection if using production mode
- Check browser console for error details

### **"Insufficient permissions" Error**

- Verify user role allows the action
- Check RBAC table for required role
- Admin-only features need admin role

### **Token Expired**

- Tokens valid for 7 days
- Login again to get new token
- Check token timestamp

### **MongoDB Connection Failed**

- Ensure MongoDB is running
- Check connection string in .env
- Verify network connectivity

---

## 📊 User Management Best Practices

### **For Admins**

1. **Create accounts for team members**
   - Assign appropriate role (operator most common)
   - Use strong temporary passwords
   - Ask users to change password on first login

2. **Audit trail review**
   - Weekly review of access logs
   - Monitor failed login attempts
   - Track user actions

3. **User lifecycle**
   - Deactivate (not delete) unused accounts
   - Regular access reviews
   - Remove when staff leaves

### **For Users**

1. **Protect your credentials**
   - Never share password
   - Use strong passwords
   - Enable 2FA when available

2. **Session management**
   - Logout when done
   - Don't share tokens
   - Be careful on shared computers

3. **Reporting issues**
   - Report suspicious activity
   - Alert admin of account compromise
   - Use audit trail for accountability

---

## 🔄 Extending the System

### **Add New Roles**

Edit `dashboard_app.py`:

```python
# Add new role
role_permissions = {
    'admin': ['read', 'write', 'delete', 'admin'],
    'operator': ['read', 'write', 'execute'],
    'viewer': ['read'],
    'analyst': ['read', 'execute', 'report']  # New
}
```

### **Add Custom RBAC Rules**

```python
@app.route('/api/advanced-config')
@require_auth
@require_role('admin', 'analyst')  # Multiple roles
def advanced_config():
    return jsonify({...})
```

### **Integrate SSO/OAuth**

Coming in v2.0:
- OAuth 2.0 providers (Google, GitHub, Azure AD)
- SAML 2.0 support
- LDAP directory integration

---

## ✅ Security Checklist

- [ ] Change JWT_SECRET_KEY in production
- [ ] Enable HTTPS/TLS
- [ ] Configure MongoDB with authentication
- [ ] Set up rate limiting on login
- [ ] Enable 2FA for admin accounts
- [ ] Regular audit trail reviews
- [ ] Backup MongoDB regularly
- [ ] Monitor failed login attempts
- [ ] Implement IP whitelisting (optional)
- [ ] Document access policies

---

**Version:** 1.0  
**Last Updated:** August 2026  
**Status:** Production Ready ✅
