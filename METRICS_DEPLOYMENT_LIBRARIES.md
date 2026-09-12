# AIOps Platform - Metrics, Deployment & Libraries Guide

## 📊 PART 1: METRICS & VARIABLES

### A. Dashboard Overview Metrics

#### **Route**: `GET /api/overview/dashboard`

**Variables Calculated:**

```python
all_metrics = storage.get_all_metrics()

# Health Status Count Metrics
healthy = sum(1 for m in all_metrics.values() if m.get('status') == 'healthy')
warning = sum(1 for m in all_metrics.values() if m.get('status') == 'warning')
critical = sum(1 for m in all_metrics.values() if m.get('status') == 'critical')
total = len(all_metrics)

# Resolution Rate Formula
resolution_rate = (healthy / total * 100) if total > 0 else 0
```

**Response Structure:**

```json
{
  "timestamp": "ISO-8601 timestamp",
  "metrics_summary": {
    "healthy": integer,
    "warning": integer,
    "critical": integer,
    "total": integer
  },
  "performance": {
    "resolution_rate": (healthy/total) × 100,
    "detection_accuracy": 85 ± random(5,10),
    "mttf": "Mean Time To Failure (30-120 min)",
    "mttr": "Mean Time To Recovery (5-30 min)"
  },
  "active_issues": {
    "critical_count": integer,
    "warning_count": integer,
    "investigation_count": critical + (warning // 2)
  },
  "recent_metrics": [
    {
      "name": string,
      "value": float,
      "unit": string,
      "status": "healthy|warning|critical",
      "timestamp": "ISO-8601"
    }
  ]
}
```

**Key Metric Formulas:**

| Metric | Formula | Example |
|--------|---------|---------|
| Resolution Rate | (healthy / total) × 100 | (15/17) × 100 = 88.2% |
| Investigation Count | critical + (warning // 2) | 1 + (1 // 2) = 1 |
| Request Rate | random.uniform(10, 100) req/s | 42.5 req/s |
| Error Rate | random.uniform(0.1, 3.5) % | 2.3% |

---

### B. Telemetry Metrics

#### **Route**: `GET /api/telemetry/current`

**Variables:**

```python
current_metrics = {
    'cpu_usage': float (0-100%),
    'memory_usage': float (0-100%),
    'disk_io': float (MB/s),
    'network_io': float (Mbps),
    'process_count': integer,
    'thread_count': integer,
    'timestamp': datetime
}
```

**Collection Method**: Real-time system metrics via `hybrid_metrics_simulator.py`

---

### C. Error Analysis Metrics

#### **Route**: `GET /api/errors/analysis?range=1h|6h|24h|7d`

**Time-Based Error Metrics:**

```python
# Generate timeline data for selected range
timeline = []

# For 1h: minute-level granularity
for i in range(60):
    timestamp = now - timedelta(minutes=i)
    errors = random.randint(20, 100)
    requests = 500  # baseline RPS
    error_rate = (errors / requests) * 100
    
    timeline.append({
        'timestamp': timestamp,
        'errors': errors,
        'rate': error_rate
    })

# For 24h: hour-level granularity
for i in range(24):
    timestamp = now - timedelta(hours=i)
    errors = random.randint(50, 300)
    requests = 12000  # 500 RPS × 60 minutes
    error_rate = (errors / requests) * 100
    
    timeline.append({
        'timestamp': timestamp,
        'errors': errors,
        'rate': error_rate
    })
```

**Error Type Breakdown:**

```python
error_types = [
    {'type': 'Timeout', 'count': random.randint(50, 150), 'percentage': 36},
    {'type': 'Connection Error', 'count': random.randint(30, 100), 'percentage': 27},
    {'type': 'Authentication', 'count': random.randint(20, 80), 'percentage': 22},
    {'type': 'Rate Limited', 'count': random.randint(10, 50), 'percentage': 15}
]

total_errors = sum(error['count'] for error in error_types)
avg_rate = sum(item['rate'] for item in timeline) / len(timeline)
```

**Response:**

```json
{
  "timeline": [
    {"timestamp": "...", "errors": N, "rate": percentage}
  ],
  "error_types": [
    {
      "type": "Timeout",
      "count": integer,
      "percentage": float,
      "trend": "up|down|stable"
    }
  ],
  "statistics": {
    "total_errors": sum(all),
    "error_rate": average,
    "p99_latency": milliseconds,
    "affected_services": integer
  },
  "heatmap": {
    "0-23": [count per hour]
  }
}
```

---

### D. Audit Trail Metrics

#### **Route**: `GET /api/audit-log/stats`

**Calculation:**

```python
entries = audit_logger.get_recent_audit_entries(limit=1000)

# Count by status
success_count = sum(1 for e in entries if e['status'] == 'success')
failure_count = sum(1 for e in entries if e['status'] == 'failure')
warning_count = sum(1 for e in entries if e['status'] == 'warning')
total = len(entries)

# Success/Failure Rates
success_rate = (success_count / total * 100) if total > 0 else 0
failure_rate = (failure_count / total * 100) if total > 0 else 0
warning_rate = (warning_count / total * 100) if total > 0 else 0

# Active Users (Unique)
active_users = len(set(e['user_id'] for e in entries))

# Entries by action type
actions = {}
for entry in entries:
    action = entry['action']
    actions[action] = actions.get(action, 0) + 1
```

**Response:**

```json
{
  "total_entries": integer,
  "success_rate": percentage,
  "failure_rate": percentage,
  "warning_rate": percentage,
  "active_users": integer,
  "actions_breakdown": {
    "LOGIN": count,
    "CREATE": count,
    "UPDATE": count,
    "DELETE": count,
    "VIEW": count
  }
}
```

---

### E. Service Topology Metrics

#### **Route**: `GET /api/topology/summary`

**Aggregation Formulas:**

```python
topology = get_topology_simulator()
services = topology.get_services()
dependencies = topology.get_dependencies()

# System Capacity
total_throughput = sum(s['throughput_rps'] for s in services)
avg_latency = sum(s['latency_ms'] for s in services) / len(services)
avg_error_rate = sum(s['error_rate'] for s in services) / len(services)

# Health Distribution
health_counts = {}
for service in services:
    health = service['health']
    health_counts[health] = health_counts.get(health, 0) + 1

# Services by Tier
tiers = {}
for service in services:
    tier = service['tier']
    tiers[tier] = tiers.get(tier, 0) + 1
```

**Response:**

```json
{
  "total_services": 17,
  "total_dependencies": 21,
  "avg_latency_ms": 63.86,
  "avg_error_rate": 0.062,
  "total_throughput_rps": 40950,
  "services_by_tier": {
    "frontend": 2,
    "api_gateway": 1,
    "microservice": 6,
    "database": 5,
    "cache": 1,
    "message_queue": 1,
    "external": 1
  },
  "health_distribution": {
    "healthy": 15,
    "degraded": 1,
    "critical": 1
  }
}
```

---

### F. Simulation Status Metrics

#### **Route**: `GET /api/simulator/<sim_id>/status`

**Variables Tracked:**

```python
simulation_status = {
    'execution_id': string,
    'status': 'running|completed|failed',
    'progress': float (0-100),
    'start_time': timestamp,
    'end_time': timestamp,
    'elapsed_seconds': integer,
    
    # Configuration
    'chaos_type': string,
    'target_service': string,
    'duration': integer,
    'intensity': float,
    
    # Current output
    'console_output': [],
    'metrics_collected': integer,
    'anomalies_detected': integer,
    
    # Results (when complete)
    'classification_accuracy': float,
    'confusion_matrix': 2D array,
    'feature_importance': dict
}
```

---

## 🚀 PART 2: DEPLOYMENT STRATEGY

### A. Local Development Deployment

**Setup:**
```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run application
python nexus_app.py
# Access at http://localhost:5000
```

**Local Metrics:**
- Real-time system metrics via `psutil`
- In-memory audit trail (144 demo entries)
- Simulated service topology (17 services)
- Local file logging (4 log files with rotation)

---

### B. Docker Container Deployment

**Dockerfile Architecture (Multi-Stage Build):**

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements_minimal.txt .
RUN pip install --user --no-cache-dir -r requirements_minimal.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=nexus_app.py
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/simulation/status')"
CMD ["python", "nexus_app.py"]
```

**Build & Run:**
```bash
# Build image
docker build -t aiops-mvp .

# Run container
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e JWT_SECRET_KEY=$(openssl rand -hex 32) \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  --name aiops-container \
  aiops-mvp
```

---

### C. Docker Compose Deployment

**Stack:**
```yaml
services:
  aiops-dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - JWT_SECRET_KEY=<generated>
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000')"]
      interval: 30s
      timeout: 10s
      retries: 3
      
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

**Deploy:**
```bash
docker-compose up -d
```

---

### D. Render.com Cloud Deployment

**Configuration (render.yaml):**
```yaml
services:
  - type: web
    name: aiops-mvp
    runtime: python
    runtimeVersion: 3.11.7
    buildCommand: pip install -r requirements.txt
    startCommand: python nexus_app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PORT
        value: "5000"
```

**Deployment Steps:**
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Create new Web Service
4. Select Python runtime
5. Point to render.yaml
6. Deploy automatically

**URL**: `https://aiops-mvp-{random}.onrender.com`

---

### E. Environment Variables

**Critical for All Deployments:**

```bash
# Flask Configuration
FLASK_ENV=production|development
SECRET_KEY=<32+ char random string>
JWT_SECRET_KEY=<32+ char random string>

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# Database (if using)
DB_HOST=localhost
DB_PORT=5432
DB_USER=aiops_user
DB_PASSWORD=<secure>
DB_NAME=aiops_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aiops.log

# Optional: Monitoring
SENTRY_DSN=https://...
```

---

### F. Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    DEPLOYMENT LAYERS                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐   │
│  │   Client    │  │   Browser   │  │  API Clients  │   │
│  └──────┬──────┘  └──────┬──────┘  └───────┬───────┘   │
│         │                 │                 │            │
│         └─────────────────┴─────────────────┘            │
│                    ▼ HTTPS/WebSocket                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Flask Web Application (5000)            │   │
│  │  • Authentication & JWT validation               │   │
│  │  • RESTful API endpoints                         │   │
│  │  • WebSocket real-time streaming                │   │
│  │  • Static file serving                          │   │
│  └──────────────────────────────────────────────────┘   │
│                    ▼                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Core Services & Modules                  │   │
│  │  • audit_logger.py (File rotation, in-memory)   │   │
│  │  • service_topology_simulator.py (17 services)  │   │
│  │  • simulation_output_generator.py (Chaos)       │   │
│  │  • hybrid_metrics_simulator.py (Real metrics)   │   │
│  └──────────────────────────────────────────────────┘   │
│                    ▼                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Persistent Storage & Logging             │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │ File-Based Logs (10MB rotation, 10 backups)│  │   │
│  │  │  • audit_trail.log                         │  │   │
│  │  │  • application.log                         │  │   │
│  │  │  • errors.log                              │  │   │
│  │  │  • security.log                            │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │ MongoDB (Optional - Production)            │  │   │
│  │  │  • Audit trail persistence                 │  │   │
│  │  │  • Metrics history                         │  │   │
│  │  │  • Simulation results                      │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 PART 3: LIBRARIES & DEPENDENCIES

### A. Web Framework & Server

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **Flask** | ≥3.0.0 | Web framework, routing | Core app |
| **Flask-CORS** | ≥4.0.0 | CORS headers | API endpoints |
| **Flask-SocketIO** | ≥5.3.0 | WebSocket support | Real-time updates |
| **python-socketio** | ≥5.9.0 | SocketIO protocol | WebSocket client |
| **python-engineio** | ≥4.7.0 | Engine.IO protocol | Transport layer |
| **gunicorn** | ≥21.0.0 | WSGI HTTP server | Production deployment |

---

### B. Authentication & Security

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **PyJWT** | ≥2.8.0 | JWT token creation/validation | `@require_auth` decorator |
| **bcrypt** | ≥4.0.0 | Password hashing | Login endpoint |

**Implementation:**
```python
# Hashing password
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Validating password
bcrypt.checkpw(password.encode(), hashed)

# Creating JWT token
token = jwt.encode(
    {'user': username, 'exp': datetime.utcnow() + timedelta(hours=24)},
    SECRET_KEY,
    algorithm='HS256'
)

# Validating JWT
decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

---

### C. Database

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **pymongo** | ≥4.5.0 | MongoDB driver | Optional persistence |

**Connection:**
```python
client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}")
db = client['aiops_db']
audit_collection = db['audit_logs']
```

---

### D. Data Processing & Science

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **pandas** | ≥2.0.0 | Data manipulation, analysis | Simulation output, CSV export |
| **numpy** | ≥1.24.0 | Numerical computing | Statistical calculations |
| **matplotlib** | ≥3.7.0 | Plotting & visualization | Graph generation |
| **seaborn** | ≥0.12.0 | Statistical visualization | Enhanced plots |
| **scikit-learn** | ≥1.3.0 | Machine learning | Anomaly detection, classification |

**Usage Examples:**
```python
# DataFrame operations
df = pd.DataFrame(audit_entries)
df_filtered = df[df['action'] == 'LOGIN']
df_stats = df.groupby('status').size()

# NumPy for calculations
arr = np.array([latencies])
mean = np.mean(arr)
std = np.std(arr)
percentile_95 = np.percentile(arr, 95)

# Matplotlib for charts
plt.figure(figsize=(12, 6))
plt.plot(timestamps, error_rates)
plt.savefig('error_analysis.png')

# Scikit-learn for ML
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
```

---

### E. Environment & Configuration

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **python-dotenv** | ≥1.0.0 | Load .env files | Configuration |
| **PyYAML** | ≥6.0.0 | YAML parsing | Config files |

**Usage:**
```python
from dotenv import load_dotenv
load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')

import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
```

---

### F. Utilities

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| **requests** | ≥2.31.0 | HTTP client | API calls, external services |
| **joblib** | ≥1.3.0 | Parallel computing, caching | ML pipeline, model serialization |
| **setuptools** | Latest | Python packaging | Build process |
| **wheel** | Latest | Binary package format | Distribution |

---

### G. Custom Internal Modules

| Module | Purpose | Key Functions |
|--------|---------|---|
| **audit_logger.py** | Audit trail & logging | `log_action()`, `get_recent_audit_entries()`, `@audit_required` |
| **service_topology_simulator.py** | Microservice simulation | `get_topology_simulator()`, `get_services()`, `get_dependencies()` |
| **simulation_output_generator.py** | Chaos simulation output | `generate_all()`, `generate_metrics()`, `generate_anomalies()` |
| **hybrid_metrics_simulator.py** | Real-time metrics | `start_hybrid_collection()`, `get_current_metrics()` |
| **prometheus_client.py** | Metrics storage | `get_storage()`, `init_storage()` |
| **data_loader.py** | Data loading | `get_data_loader()` |
| **simulation_export.py** | Export utilities | `SimulationExporter` |

---

## 🔧 Dependency Installation

### Minimal (Production)
```bash
pip install -r requirements_minimal.txt
```

**Includes:** Flask, PyJWT, bcrypt, python-dotenv, requests

### Standard (Recommended)
```bash
pip install -r requirements.txt
```

**Includes:** All packages (web, auth, data science, ML)

### Render.com
```bash
pip install -r requirements_render.txt
```

**Optimized:** For Render.com cloud deployment

---

## 📊 System Requirements

### Development
- **Python**: 3.10+
- **RAM**: 4 GB minimum
- **Disk**: 2 GB for dependencies + logs
- **OS**: Windows, macOS, Linux

### Production (Docker)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: 2 GB minimum
- **CPU**: 2 cores
- **Disk**: 10 GB (logs rotation)

### Cloud (Render.com)
- **Runtime**: Python 3.11.7
- **Memory**: 512 MB
- **Disk**: 1 GB (ephemeral)
- **Auto-scaling**: Available

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] JWT_SECRET_KEY generated (32+ chars, random)
- [ ] Database credentials set (if using MongoDB)
- [ ] Logs directory created and writable
- [ ] Dependencies installed: `pip install -r requirements.txt`

### Deployment
- [ ] Application starts without errors
- [ ] Health check endpoint responds: `/api/simulation/status`
- [ ] Authentication works: `/api/auth/login`
- [ ] Metrics visible: `/api/overview/dashboard`
- [ ] Logs written to file: `logs/audit_trail.log`

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Test error analysis page: `/error-analysis`
- [ ] Verify audit trail: `/audit`
- [ ] Check topology: `/topology`
- [ ] Monitor resource usage (CPU, RAM, Disk)

---

## 📈 Performance Metrics

### Application Performance
- **Startup Time**: ~5 seconds
- **Memory Footprint**: ~150 MB
- **Max Concurrent Users**: 500+ (with proper scaling)
- **Request Latency**: <100 ms (p95)
- **Throughput**: ~40,000 RPS (simulated)

### Storage
- **Audit Logs**: 10 MB per file × 10 backups = 100 MB max
- **Application Logs**: 10 MB per file × 10 backups = 100 MB max
- **Error Logs**: 10 MB per file × 10 backups = 100 MB max
- **Security Logs**: 10 MB per file × 10 backups = 100 MB max
- **Total Possible**: ~400 MB maximum

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-07  
**Applicable To**: Nexus AIOps v1.0
