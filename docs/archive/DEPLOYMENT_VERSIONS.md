# Deployment Versions Guide

## Overview

The AIOps MVP has **two different deployment configurations** designed for different use cases.

---

## 🚀 Version 1: Full-Featured (Production) - `nexus_app.py`

**Use Case:** Production deployment with all features

**What's Included:**
- ✅ Error Analysis (detailed error pages)
- ✅ Audit Trail (144+ audit entries with filtering)
- ✅ Service Topology (17 services, 21 dependencies)
- ✅ Real-Time Metrics (CPU, memory, disk, network)
- ✅ Machine Learning (Anomaly detection, classification)
- ✅ Chaos Simulation (Complete with exports)
- ✅ Advanced Analytics

**Features:**
- Real system metrics integration (psutil)
- WebSocket real-time updates
- MongoDB support (optional)
- Advanced filtering and export
- ML-based anomaly detection
- Incident classification

**Dependencies:** Full stack
```
Flask, PyJWT, bcrypt, pymongo
pandas, numpy, scikit-learn, matplotlib, seaborn
requests, joblib, pyyaml, python-dotenv
```

**Deployment Entry Point:**
```bash
python nexus_app.py
```

**How to Deploy on Render:**
```yaml
startCommand: python nexus_app.py
requirements: requirements.txt
```

**Current Status:**
- ✅ **GitHub:** Full version with all features
- ✅ **Local (localhost:5000):** Running nexus_app.py
- ⚠️ **Render.com:** May need redeployment to match

---

## 📱 Version 2: Lightweight - `dashboard_lite.py`

**Use Case:** Lightweight deployment, minimal dependencies, CI/CD friendly

**What's Included:**
- ✅ Basic Dashboard (cards for Problems, Infrastructure, Overview)
- ✅ Chaos Simulator (core functionality)
- ✅ Authentication (JWT + bcrypt)
- ✅ Simple Incident Tracking

**Features:**
- Minimal dependencies
- Fast startup
- Lower memory footprint
- No ML/ML libraries required
- Simpler database-free (demo mode)

**Dependencies:** Minimal stack
```
Flask, Flask-CORS, PyJWT, bcrypt
python-dotenv, requests
```

**Deployment Entry Point:**
```bash
python dashboard_lite.py
```

**How to Deploy on Render:**
```yaml
startCommand: python dashboard_lite.py
requirements: requirements_minimal.txt
```

**Current Status:**
- ✅ **Render.com:** Likely running dashboard_lite.py (based on visible interface)
- ❌ **Local:** Not running (using full version instead)

---

## 📊 Feature Comparison

| Feature | nexus_app.py | dashboard_lite.py |
|---------|--------------|-------------------|
| **Error Analysis** | ✅ Full | ❌ No |
| **Audit Trail** | ✅ 144+ entries | ❌ No |
| **Service Topology** | ✅ 17 services | ❌ No |
| **Real Metrics** | ✅ CPU/Memory/Disk | ❌ Demo only |
| **ML Models** | ✅ Isolation Forest, Random Forest | ❌ No |
| **Chaos Simulator** | ✅ Full with exports | ✅ Basic |
| **Authentication** | ✅ JWT + advanced | ✅ JWT basic |
| **Database Support** | ✅ MongoDB optional | ❌ No |
| **Dependencies** | 20+ packages | 6 packages |
| **Startup Time** | ~3-5 seconds | ~1-2 seconds |
| **Memory Usage** | ~150 MB | ~50 MB |

---

## 🔄 Why the Difference?

### nexus_app.py (Full)
- **Goal:** Comprehensive enterprise AIOps platform
- **Use:** Production, team collaboration, full visibility
- **Users:** DevOps engineers, SREs, platform teams
- **Requirements:** Advanced monitoring needs

### dashboard_lite.py (Lite)
- **Goal:** Quick demo, minimal deployment
- **Use:** Testing, lightweight environments, CI/CD
- **Users:** Developers, quick prototyping
- **Requirements:** Minimal resources

---

## 🎯 Current Deployment Status

### What's Running Where?

| Location | Version | Entry Point | Status |
|----------|---------|-------------|--------|
| **Local** | Full | nexus_app.py | ✅ Running |
| **GitHub** | Full | nexus_app.py | ✅ Latest code |
| **Render.com** | Lite? | dashboard_lite.py? | ⚠️ Check |

### The Issue You Noticed

**Local (localhost:5000):**
- Shows: "Real-Time System Overview"
- Metrics: CPU 87.3%, Memory 88.3%, Disk 87.9%
- Features: Sidebar, advanced filtering, topology
- Running: `nexus_app.py` ✅

**Render (aiops-mvp-1.onrender.com):**
- Shows: Simple card dashboard
- Metrics: Open Problems (3), Affected Services (4)
- Features: Basic cards, simple layout
- Running: `dashboard_lite.py` (probably)

**They are different because they're different applications!**

---

## ✅ How to Fix

### Option A: Deploy Full Version to Render

**Update render.yaml:**
```yaml
startCommand: python nexus_app.py
```

**Then redeploy on Render:**
1. Go to Render dashboard
2. Navigate to your aiops-mvp service
3. Click "Manual Deploy"
4. Wait for rebuild (uses nexus_app.py now)

**Result:** Render will show same interface as localhost ✅

### Option B: Keep Both Versions

**Create separate Render deployments:**

1. **Production (Full):** aiops-mvp-prod → nexus_app.py
2. **Demo (Lite):** aiops-mvp-demo → dashboard_lite.py

**Each serves a different purpose.**

---

## 🔧 Configuration for Each Version

### nexus_app.py (Full)
```yaml
# render.yaml for FULL version
services:
  - type: web
    name: aiops-mvp-prod
    runtime: python
    runtimeVersion: 3.11.7
    buildCommand: pip install -r requirements.txt
    startCommand: python nexus_app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: JWT_SECRET_KEY
        generateValue: true
```

### dashboard_lite.py (Lite)
```yaml
# render_lite.yaml for LITE version
services:
  - type: web
    name: aiops-mvp-lite
    runtime: python
    runtimeVersion: 3.11.7
    buildCommand: pip install -r requirements_minimal.txt
    startCommand: python dashboard_lite.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: JWT_SECRET_KEY
        generateValue: true
```

---

## 📋 Requirements Files

### Full Version (requirements.txt)
```
# Web Framework
Flask>=3.0.0
Flask-CORS>=4.0.0
Flask-SocketIO>=5.3.0

# Auth & Security
PyJWT>=2.8.0
bcrypt>=4.0.0

# Data Science/ML
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Database
pymongo>=4.5.0

# Config & Utils
python-dotenv>=1.0.0
requests>=2.31.0
pyyaml>=6.0.0
joblib>=1.3.0

# Production
gunicorn>=21.0.0
```

### Lite Version (requirements_minimal.txt)
```
# Web Framework
Flask>=3.0.0
Flask-CORS>=4.0.0

# Auth & Security
PyJWT>=2.8.0
bcrypt>=4.0.0

# Config & Utils
python-dotenv>=1.0.0
requests>=2.31.0

# Production
gunicorn>=21.0.0
```

---

## 🚀 Recommended Setup

### For Your Use Case:

1. **Local Development:** Use `nexus_app.py` (you're already doing this ✅)
2. **GitHub Repo:** Keep full version as default (you're already doing this ✅)
3. **Render Production:** Deploy full version (`nexus_app.py`)
4. **Optional Demo:** Create separate lightweight deployment if needed

---

## 📝 Next Steps

1. **Verify current Render deployment:**
   - Check which file is running on Render.com
   - Look at Render logs to confirm

2. **Update Render to full version:**
   - Update `startCommand: python nexus_app.py`
   - Trigger manual deploy
   - Verify both versions match

3. **Document in README:**
   - Add deployment version guide
   - Include comparison table
   - Link to this document

---

**Document Version:** 1.0  
**Updated:** 2026-09-12  
**Status:** Both versions functional  
