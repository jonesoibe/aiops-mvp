# Starting Nexus AIOps - Commands & Environment Variables

## Quick Start

### Start the App (Local Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
python nexus_app.py

# OR with UTF-8 encoding (Windows)
set PYTHONIOENCODING=utf-8
python nexus_app.py

# OR with POSIX shell (Git Bash/Linux/Mac)
PYTHONIOENCODING=utf-8 python nexus_app.py
```

**Expected Output:**
```
======================================================================
  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform
======================================================================
✅ Initialized 5 approval requests in memory
📡 Telemetry emitted
📍 Access at: http://localhost:5000
   Demo: admin / admin123
 * Serving Flask app 'nexus_app'
 * Debug mode: off
```

**Then access:**
→ **http://localhost:5000**

---

## Environment Variables

### Required Variables (Optional - Defaults Provided)

```bash
# Database
MONGODB_URI=mongodb://localhost:27017/nexus_aiops
# OR for MongoDB Atlas:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/nexus_aiops?retryWrites=true&w=majority

# Authentication
JWT_SECRET_KEY=your-secret-key-here
# (Default: dev-secret-key-change-in-production)

# Server Port
PORT=5000
# (Default: 5000)

# Python Encoding (Important for Windows)
PYTHONIOENCODING=utf-8
```

### Set Environment Variables

#### Windows (Command Prompt)
```cmd
set PYTHONIOENCODING=utf-8
set MONGODB_URI=mongodb://localhost:27017/nexus_aiops
set JWT_SECRET_KEY=your-secret-key
python nexus_app.py
```

#### Windows (PowerShell)
```powershell
$env:PYTHONIOENCODING="utf-8"
$env:MONGODB_URI="mongodb://localhost:27017/nexus_aiops"
$env:JWT_SECRET_KEY="your-secret-key"
python nexus_app.py
```

#### Linux/Mac (Bash)
```bash
export PYTHONIOENCODING=utf-8
export MONGODB_URI=mongodb://localhost:27017/nexus_aiops
export JWT_SECRET_KEY=your-secret-key
python nexus_app.py
```

#### Linux/Mac (One Command)
```bash
PYTHONIOENCODING=utf-8 MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py
```

---

## Build Commands

### Install Dependencies
```bash
# Basic installation
pip install -r requirements.txt

# Upgrade pip first (recommended)
python -m pip install --upgrade pip
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements.txt
pip install pytest pytest-cov flake8
```

### Create Virtual Environment (Recommended)

#### Windows
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start app
python nexus_app.py
```

#### Linux/Mac
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start app
python nexus_app.py
```

### Deactivate Virtual Environment
```bash
# On any platform
deactivate
```

---

## requirements.txt

**Current dependencies:**

```txt
Flask==2.3.0
Flask-CORS==4.0.0
Flask-SocketIO==5.3.0
python-socketio==5.9.0
python-engineio==4.7.1
PyJWT==2.8.0
bcrypt==4.0.0
pymongo==4.5.0
python-dotenv==1.0.0
```

### Check Installed Packages
```bash
pip list
```

### Freeze Current Packages
```bash
pip freeze > requirements.txt
```

---

## Production Build (Render)

### Render Build Command
In Render dashboard, set:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT "nexus_app:app" --worker-class eventlet -k eventlet
```

### OR using Python built-in server (Simpler)
```bash
python nexus_app.py
```

### Environment in Render
Add environment variables in Render dashboard:

```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PORT=5000
MONGODB_URI=your_mongodb_uri_here
JWT_SECRET_KEY=your_secret_key_here
```

---

## Docker Build (Optional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PORT=5000

# Expose port
EXPOSE 5000

# Start app
CMD ["python", "nexus_app.py"]
```

### Build Docker Image
```bash
# Build
docker build -t nexus-aiops .

# Run
docker run -p 5000:5000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/nexus_aiops \
  nexus-aiops
```

---

## Complete Setup Script

### Windows (setup.bat)
```batch
@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! To start the app:
echo.
echo   1. Activate: venv\Scripts\activate.bat
echo   2. Run: python nexus_app.py
echo.
pause
```

### Linux/Mac (setup.sh)
```bash
#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! To start the app:"
echo ""
echo "  1. Activate: source venv/bin/activate"
echo "  2. Run: python nexus_app.py"
echo ""
```

### Make executable (Linux/Mac only)
```bash
chmod +x setup.sh
./setup.sh
```

---

## Troubleshooting Start Issues

### "Module not found" Error
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### "Port 5000 already in use" Error
```bash
# Option 1: Use different port
PORT=8000 python nexus_app.py

# Option 2: Kill process using port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### "MongoDB connection refused" Error
```bash
# This is OK - app uses in-memory storage as fallback
# To use MongoDB, start MongoDB:

# Windows:
mongod

# Linux/Mac:
brew services start mongodb-community
# OR
sudo systemctl start mongod
```

### "UnicodeEncodeError" on Windows
```bash
# Solution: Set UTF-8 encoding
set PYTHONIOENCODING=utf-8
python nexus_app.py
```

### "Permission denied" on Linux/Mac
```bash
# Make file executable
chmod +x nexus_app.py

# Or just run with python
python nexus_app.py
```

---

## Development vs Production

### Development (Local)
```bash
# With debug features
PYTHONIOENCODING=utf-8 python nexus_app.py
```

**Characteristics:**
- ✅ Verbose logging
- ✅ Easy to test
- ✅ In-memory storage (fast)
- ⚠️ Single process
- ⚠️ No data persistence

### Production (Render/Docker)
```bash
# With proper server
gunicorn -w 4 -b 0.0.0.0:$PORT "nexus_app:app" --worker-class eventlet

# Environment variables
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
MONGODB_URI=mongodb+srv://...
```

**Characteristics:**
- ✅ Multiple workers
- ✅ MongoDB persistence
- ✅ Proper error handling
- ✅ Performance optimized
- ✅ Security hardened

---

## Development Tools

### Install Development Dependencies
```bash
pip install flask-debugtoolbar
pip install pytest pytest-cov
pip install black flake8
```

### Run Tests
```bash
pytest
pytest --cov=. --cov-report=html
```

### Code Formatting
```bash
# Format code
black .

# Check style
flake8 .
```

### Hot Reload (Development)
```bash
# Install watchdog
pip install watchdog

# Or use Flask development server
FLASK_ENV=development FLASK_DEBUG=1 python nexus_app.py
```

---

## Performance Optimization

### Production Server (Gunicorn)
```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 "nexus_app:app"

# With eventlet for WebSocket support
pip install eventlet
gunicorn -w 4 -b 0.0.0.0:5000 "nexus_app:app" --worker-class eventlet -k eventlet

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile - \
  "nexus_app:app" --worker-class eventlet
```

### Memory/CPU Settings
```bash
# Limit memory usage
gunicorn -w 2 -b 0.0.0.0:5000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  "nexus_app:app"
```

---

## Quick Reference

```bash
# START DEV
python nexus_app.py

# START WITH MONGODB
MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py

# START ON DIFFERENT PORT
PORT=8000 python nexus_app.py

# VIRTUAL ENV
python -m venv venv              # Create
source venv/bin/activate          # Activate (Linux/Mac)
venv\Scripts\activate            # Activate (Windows)
deactivate                        # Deactivate

# DEPENDENCIES
pip install -r requirements.txt   # Install
pip freeze > requirements.txt     # Update

# PRODUCTION (Render)
gunicorn -w 4 -b 0.0.0.0:5000 "nexus_app:app"

# DOCKER
docker build -t nexus-aiops .
docker run -p 5000:5000 nexus-aiops
```

---

## Environment Variables Summary

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `PYTHONIOENCODING` | Character encoding | `utf-8` | ⚠️ Windows only |
| `MONGODB_URI` | Database connection | `mongodb://localhost:27017/nexus_aiops` | ❌ Optional |
| `JWT_SECRET_KEY` | Token secret | `your-secret-key-123` | ❌ Optional |
| `PORT` | Server port | `5000` | ❌ Default: 5000 |
| `FLASK_ENV` | Dev/Prod mode | `development` | ❌ Optional |
| `FLASK_DEBUG` | Debug mode | `1` | ❌ Optional |

---

## Verify Installation

```bash
# Check Python version
python --version
# Should be 3.8+

# Check pip packages
pip list | grep -E "Flask|MongoDB|PyJWT"
# Should show installed packages

# Test app starts
python nexus_app.py
# Should show startup messages and "Access at: http://localhost:5000"
```

---

## Support

**Issues starting the app?**
1. Check error messages in terminal
2. Verify Python 3.8+ installed: `python --version`
3. Verify dependencies: `pip list`
4. Check environment variables: `set` (Windows) or `env` (Linux/Mac)
5. Try in virtual environment

**Questions?**
- Check [README.md](README.md)
- Check logs in terminal
- Review [MONGODB_SETUP.md](MONGODB_SETUP.md)

---

**You're ready to develop and deploy! 🚀**
