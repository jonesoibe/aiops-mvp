# MongoDB Setup Guide for Nexus AIOps

## Overview
Nexus AIOps uses MongoDB as its primary database for storing users, incidents, audit logs, and other operational data. This guide explains how to configure MongoDB for your deployment.

## Configuration Options

### 1. Local MongoDB (Development)
If you have MongoDB installed locally:

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=nexus_aiops
```

### 2. Remote MongoDB Server
If MongoDB is running on a remote server:

```
MONGODB_URI=mongodb://host.example.com:27017
MONGODB_DATABASE=nexus_aiops
```

### 3. MongoDB with Authentication
If your MongoDB requires username/password:

```
MONGODB_URI=mongodb://username:password@host:27017
MONGODB_DATABASE=nexus_aiops
```

### 4. MongoDB Atlas (Cloud)
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=nexus_aiops
```

## Quick Start

1. Update `.env` file with your MongoDB connection string
2. Restart the application
3. Look for this message in startup logs:
   ```
   ✅ MongoDB connected successfully with collections initialized
   ```

## Collections Created Automatically

- **users** - User accounts and authentication data
- **incidents** - Incident records and alerts
- **responses** - Remediation responses
- **audit_log** - Audit trail of all actions
- **actions** - Executed remediation actions
- **approvals** - Approval workflow records

## If MongoDB is Not Available

The application will fall back to **in-memory storage**:
- Data persists only during the session
- Data is lost when server restarts
- Suitable for development/testing only

**⚠️ Production Warning:** Always ensure MongoDB is configured in production.

## Troubleshooting

### Connection Refused
Make sure MongoDB service is running:
```bash
# Windows
net start MongoDB

# Linux
sudo systemctl start mongod
```

### Authentication Failed
Check username/password and URL encoding for special characters.

### Verify Data is Persisting
```bash
mongo mongodb://localhost:27017/nexus_aiops
db.users.find()
db.audit_log.find()
```

## Production Deployment

For production, use:
```
MONGODB_URI=mongodb+srv://prod_user:secure_password@prod-cluster.mongodb.net/
MONGODB_DATABASE=nexus_aiops_prod
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

Security best practices:
- ✅ Use strong passwords
- ✅ Enable MongoDB authentication
- ✅ Restrict network access
- ✅ Use IP whitelisting
- ✅ Enable SSL/TLS
- ✅ Regular backups
