# ⚡ Quick Start: Real Metrics (2 minutes)

Copy & paste commands to test real system metrics immediately.

---

## 🚀 Option 1: Real System Metrics Only (Easiest)

**Setup (2 minutes):**

```bash
# Install core dependency
pip install psutil

# Update nexus_app.py (one line change)
# Change this line (around line 20):
#   from metrics_simulator import start_metrics_collection
# To this:
#   from hybrid_metrics_simulator import start_hybrid_collection

# Then find initialize_on_startup() and change:
#   start_metrics_collection()
# To:
#   start_hybrid_collection()
```

**Run (1 command):**

```bash
python nexus_app.py
```

**Test (browser):**

```
http://localhost:5000
Login: admin / admin123

Watch metrics update with YOUR real values!
```

---

## 🚀 Option 2: Real Metrics + Windows PerfMon (Detailed)

**Setup (3 minutes):**

```bash
# Install everything
pip install psutil pywin32

# Post-install pywin32
python Scripts/pywin32_postinstall.py -install

# Update nexus_app.py (same as Option 1)
```

**Run:**

```bash
python nexus_app.py
```

**Expected output:**
```
✅ Windows Performance Monitor initialized
✅ Hybrid metrics collection started
```

---

## 🚀 Option 3: Full Load Test with Anomalies (Most Realistic)

**Setup (3 minutes):**

```bash
# Install everything
pip install psutil locust

# Update nexus_app.py (same as above)
```

**Run 3 terminals:**

```bash
# Terminal 1: Start app
python nexus_app.py

# Terminal 2: Start load test
locust -f locustfile.py --host=http://localhost:5000

# Terminal 3: Open browser
http://localhost:8089        # Locust web UI
http://localhost:5000        # Dashboard
```

**On Locust UI (http://localhost:8089):**
- Number of users: 10
- Spawn rate: 2
- Click "Start swarming"

**Watch dashboard:**
- Real metrics + real load + anomalies = Full test!

---

## ✅ Verify It's Working

### Check metrics updating:
```powershell
# PowerShell - monitor in real-time
while($true) {
    Clear-Host
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/all"
    Write-Host "CPU: $($response.cpu_usage.value)%"
    Write-Host "Memory: $($response.memory_usage.value)%"
    Write-Host "Disk: $($response.disk_usage.value)%"
    Start-Sleep -Seconds 5
}
```

### Quick anomaly test:
```powershell
# Get token
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
$token = $response.token

# Trigger memory leak
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -ContentType "application/json" `
  -Body '{"anomaly_type":"memory_leak","duration":30}'

# Watch dashboard memory card go RED!
```

---

## 📊 What You Should See

**Option 1: Real Metrics**
```
✅ CPU card shows YOUR actual CPU usage (not simulated)
✅ Memory card shows YOUR actual RAM usage
✅ All values update from real system data
✅ Anomalies still work (overlay on real data)
```

**Option 2: Real Metrics + PerfMon**
```
✅ Everything from Option 1 PLUS
✅ More detailed CPU metrics
✅ More detailed Memory metrics
✅ Disk I/O rates
✅ Network utilization by interface
```

**Option 3: Load Test**
```
✅ Dashboard shows 10 concurrent users
✅ Request rate spikes (real traffic)
✅ Response time increases (real load)
✅ Every 30-60 seconds, anomalies trigger
✅ Memory card spikes with memory leak
✅ CPU card spikes with cpu_spike
✅ JSON report saved with all metrics
```

---

## 🔧 One-File Code Change

**Location:** `nexus_app.py` around line 20

**Before:**
```python
from metrics_simulator import start_metrics_collection

def initialize_on_startup():
    start_metrics_collection()
    init_storage()
    # ...
```

**After:**
```python
from hybrid_metrics_simulator import start_hybrid_collection

def initialize_on_startup():
    start_hybrid_collection()
    init_storage()
    # ...
```

That's it! Everything else is automatic.

---

## 🎯 Testing Checklist

- [ ] Install dependencies (psutil, locust, pywin32)
- [ ] Update nexus_app.py (1 line change)
- [ ] Run `python nexus_app.py`
- [ ] Open http://localhost:5000
- [ ] Login (admin/admin123)
- [ ] Verify metrics show YOUR real values
- [ ] Watch metrics update every 5 seconds
- [ ] Trigger anomaly via PowerShell
- [ ] See dashboard respond in real-time
- [ ] (Optional) Run load test with Locust

---

## 📁 Files You Got

| File | What It Does |
|------|-------------|
| `real_metrics_collector.py` | Collects real system metrics via psutil + PerfMon |
| `hybrid_metrics_simulator.py` | Blends real data with simulated anomalies |
| `locustfile.py` | Load testing script that generates realistic traffic |
| `REAL_METRICS_INTEGRATION.md` | Full integration guide (detailed) |
| `QUICK_START_REAL_METRICS.md` | This file (quick start) |

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError: No module named 'psutil' | `pip install psutil` |
| ImportError: No module named 'locust' | `pip install locust` |
| PerfMon not working | `pip install pywin32` then `python Scripts/pywin32_postinstall.py -install` |
| Metrics show "—" | Check app console for errors, refresh browser (F5) |
| Locust won't start | Make sure app is running at http://localhost:5000 |
| Load test won't trigger anomalies | Check auth: Run PowerShell commands to get fresh token |

---

## 🚀 Ready?

**Just run:**

```bash
pip install psutil locust
python nexus_app.py
```

**Then open:**

```
http://localhost:5000
```

**And watch YOUR system metrics in real-time! 🎉**

---

**Need more details? See [REAL_METRICS_INTEGRATION.md](REAL_METRICS_INTEGRATION.md)**
