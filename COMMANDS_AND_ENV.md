# 🚀 NEXUS AIOPS - COMMANDS AND ENVIRONMENT VARIABLES

## START THE APP

### Simplest Way (Windows)
```bash
python nexus_app.py
```

### Simplest Way (Linux/Mac)
```bash
python3 nexus_app.py
```

### With UTF-8 Support (Windows - Recommended)
```bash
set PYTHONIOENCODING=utf-8
python nexus_app.py
```

### With UTF-8 Support (Linux/Mac)
```bash
PYTHONIOENCODING=utf-8 python nexus_app.py
```

---

## BUILD AND INSTALL

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variables (Optional)
```bash
# Windows Command Prompt
set PYTHONIOENCODING=utf-8
set MONGODB_URI=mongodb://localhost:27017/nexus_aiops

# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
$env:MONGODB_URI="mongodb://localhost:27017/nexus_aiops"

# Linux/Mac
export PYTHONIOENCODING=utf-8
export MONGODB_URI=mongodb://localhost:27017/nexus_aiops
```

### Step 3: Start the App
```bash
python nexus_app.py
```

### Access the App
→ **http://localhost:5000**

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## ENVIRONMENT VARIABLES

### Complete List

```bash
# ====================================
# REQUIRED (Set for Production)
# ====================================

# Database Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/nexus_aiops

# JWT Secret Key (for token encryption)
JWT_SECRET_KEY=your-secret-key-change-in-production

# Server Port
PORT=5000

# ====================================
# OPTIONAL (Development/Production)
# ====================================

# Python Encoding (Windows)
PYTHONIOENCODING=utf-8

# Flask Environment
FLASK_ENV=production  # or development

# Don't Write Bytecode (Production)
PYTHONDONTWRITEBYTECODE=1

# Unbuffered Output (Docker/Production)
PYTHONUNBUFFERED=1
```

---

## QUICK START COMMANDS

### **Windows Users**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start with UTF-8 support
set PYTHONIOENCODING=utf-8
python nexus_app.py
```

### **Mac/Linux Users**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
PYTHONIOENCODING=utf-8 python nexus_app.py

# OR for repeated use, set environment first
export PYTHONIOENCODING=utf-8
python nexus_app.py
```

### **Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start app
python nexus_app.py

# Deactivate when done
deactivate
```

---

## PRODUCTION DEPLOYMENT (Render)

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
# Simple (Python built-in)
python nexus_app.py

# OR Professional (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:$PORT "nexus_app:app" --worker-class eventlet
```

### Environment Variables (Set in Render Dashboard)

```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONIOENCODING=utf-8
PORT=5000
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/nexus_aiops
JWT_SECRET_KEY=your-secret-key-here
```

---

## COMMON USE CASES

### Use Case 1: Local Development (Default)
```bash
python nexus_app.py
# Uses in-memory storage, no MongoDB needed
# Data resets on restart
```

### Use Case 2: Development with MongoDB (Local)
```bash
# First, start MongoDB:
# Windows: mongod
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Then start app:
MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py
```

### Use Case 3: Development with MongoDB (Docker)
```bash
# Start MongoDB in Docker
docker run -d -p 27017:27017 mongo:latest

# Start app
MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py
```

### Use Case 4: Different Port
```bash
# Use port 8000 instead of 5000
PORT=8000 python nexus_app.py
# Access at http://localhost:8000
```

### Use Case 5: Production (Render)
```bash
# Via Render dashboard only
# Set environment variables, trigger deployment
# App runs with Gunicorn and MongoDB Atlas
```

---

## ENVIRONMENT VARIABLE DETAILS

### MONGODB_URI
**Purpose:** Connect to MongoDB database  
**Local:** `mongodb://localhost:27017/nexus_aiops`  
**Atlas:** `mongodb+srv://user:pass@cluster.mongodb.net/nexus_aiops?retryWrites=true&w=majority`  
**Required:** ❌ Optional (fallback to in-memory storage)

### JWT_SECRET_KEY
**Purpose:** Encrypt JWT authentication tokens  
**Default:** `dev-secret-key-change-in-production`  
**Production:** Change to strong random key  
**Example:** `AKLDJ2391@!XC92kjsd-random-key-12345`

### PORT
**Purpose:** Server listening port  
**Default:** `5000`  
**Local:** Can be any available port  
**Render:** Automatically set to 5000+

### PYTHONIOENCODING
**Purpose:** Fix character encoding issues (Windows)  
**Value:** `utf-8`  
**Required:** ⚠️ Windows only, Linux/Mac don't need it

### FLASK_ENV
**Purpose:** Development vs production mode  
**Development:** `development` (debug mode on)  
**Production:** `production` (debug mode off)  

### PYTHONUNBUFFERED
**Purpose:** Show Python output immediately (Docker/Render)  
**Value:** `1`  
**Required:** Docker and Render only

---

## TROUBLESHOOTING COMMANDS

### Problem: "ModuleNotFoundError: No module named 'flask'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Problem: "Address already in use" (Port 5000)
```bash
# Option 1: Use different port
PORT=8000 python nexus_app.py

# Option 2: Kill process using port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :5000
kill -9 <PID>
```

### Problem: "UnicodeEncodeError" on Windows
```bash
# Solution: Set UTF-8 encoding
set PYTHONIOENCODING=utf-8
python nexus_app.py
```

### Problem: MongoDB connection refused
```bash
# This is OK - app uses fallback storage
# To use MongoDB, install and start it:

# Windows: Download from mongodb.com and run mongod
# Mac: brew install mongodb-community && mongod
# Linux: sudo apt install mongodb && mongod

# Then set connection:
MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py
```

### Problem: "Port already in use" on Render
```bash
# Render automatically assigns PORT environment variable
# Set Start Command to:
python nexus_app.py
# App will read PORT env var automatically
```

---

## VERIFICATION CHECKLIST

After starting the app, verify:

- [ ] App started without errors
- [ ] Terminal shows: "Access at: http://localhost:5000"
- [ ] Browser opens without error
- [ ] Login page appears
- [ ] Default credentials work (admin/admin123)
- [ ] Dashboard loads with data
- [ ] WebSocket shows telemetry

---

## REFERENCE TABLE

| Task | Command | Platform |
|------|---------|----------|
| Start app | `python nexus_app.py` | All |
| Start with UTF-8 | `set PYTHONIOENCODING=utf-8` → `python nexus_app.py` | Windows |
| Start with MongoDB | `MONGODB_URI=mongodb://... python nexus_app.py` | All |
| Different port | `PORT=8000 python nexus_app.py` | All |
| Install deps | `pip install -r requirements.txt` | All |
| Virtual env | `python -m venv venv` | All |
| Activate (Win) | `venv\Scripts\activate` | Windows |
| Activate (Mac) | `source venv/bin/activate` | Mac/Linux |
| Render start | `python nexus_app.py` | Render |
| Gunicorn prod | `gunicorn -w 4 "nexus_app:app"` | Production |

---

## COMPLETE SETUP (First Time)

### Windows
```batch
@REM Create virtual environment
python -m venv venv

@REM Activate it
venv\Scripts\activate

@REM Install dependencies
pip install -r requirements.txt

@REM Start the app
set PYTHONIOENCODING=utf-8
python nexus_app.py
```

### Mac/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the app
PYTHONIOENCODING=utf-8 python nexus_app.py
```

---

## QUICK COMMANDS COPY-PASTE

```bash
# Development (Windows)
pip install -r requirements.txt && set PYTHONIOENCODING=utf-8 && python nexus_app.py

# Development (Mac/Linux)
pip install -r requirements.txt && PYTHONIOENCODING=utf-8 python nexus_app.py

# With MongoDB (Windows)
set PYTHONIOENCODING=utf-8 && set MONGODB_URI=mongodb://localhost:27017/nexus_aiops && python nexus_app.py

# With MongoDB (Mac/Linux)
PYTHONIOENCODING=utf-8 MONGODB_URI=mongodb://localhost:27017/nexus_aiops python nexus_app.py
```

---

## GETTING HELP

**Problem?**
1. Check the error message in terminal
2. See "Troubleshooting Commands" section above
3. Check [START_AND_BUILD.md](START_AND_BUILD.md) for detailed guide
4. Check [MONGODB_SETUP.md](MONGODB_SETUP.md) for database issues
5. Check GitHub issues

**Default URL:**
→ http://localhost:5000

**Default Login:**
- Username: admin
- Password: admin123

---

**You're ready to build and run! 🚀**
