# 📋 Copy & Paste Commands

Complete command sequences for all three options. Just copy, paste, run!

---

## 🚀 Option 1: Real System Metrics (Easiest)

**Total time: 5 minutes**

### Step 1: Install (1 minute)
```bash
pip install psutil
```

### Step 2: Update Code (2 minutes)

Open `nexus_app.py` and find line ~20:

**FIND THIS:**
```python
from metrics_simulator import start_metrics_collection
```

**REPLACE WITH:**
```python
from hybrid_metrics_simulator import start_hybrid_collection
```

**THEN FIND THIS (in initialize_on_startup function):**
```python
start_metrics_collection()
```

**REPLACE WITH:**
```python
start_hybrid_collection()
```

### Step 3: Run (1 minute)
```bash
python nexus_app.py
```

Expected output:
```
✅ Metrics collection started
✅ Prometheus storage initialized
✅ Hybrid metrics collection started (real data + anomaly injection)
```

### Step 4: Test (1 minute)
```
Open: http://localhost:5000
Login: admin / admin123
Watch: Metrics update with YOUR real values!
```

---

## 🚀 Option 2: Real Metrics + Windows Performance Monitor

**Total time: 8 minutes**

### Step 1: Install (2 minutes)
```bash
pip install psutil pywin32
python Scripts/pywin32_postinstall.py -install
```

Expected output:
```
Copying pywintypes36.dll to C:\Python311\...\
```

### Step 2: Update Code (2 minutes)
Same as Option 1 above.

### Step 3: Run (1 minute)
```bash
python nexus_app.py
```

Expected output:
```
✅ Windows Performance Monitor initialized
✅ Hybrid metrics collection started (real data + anomaly injection)
```

### Step 4: Test (2 minutes)
```
http://localhost:5000
Login: admin / admin123
Verify: Detailed Windows metrics showing (CPU user/privileged time, etc)
```

---

## 🚀 Option 3: Full Load Testing (Most Realistic)

**Total time: 15 minutes**

### Step 1: Install (2 minutes)
```bash
pip install psutil locust
```

### Step 2: Update Code (2 minutes)
Same as Option 1 above.

### Step 3A: Start App (Terminal 1)
```bash
python nexus_app.py
```

Wait for:
```
✅ Metrics collection started
✅ Hybrid metrics collection started
```

### Step 3B: Start Load Test (Terminal 2)
```bash
locust -f locustfile.py --host=http://localhost:5000
```

Wait for:
```
[2026-08-26 ...] Locust 2.x started
Starting web interface at http://127.0.0.1:8089
```

### Step 3C: Open Locust Web UI (Terminal 3 or Browser)
```
http://localhost:8089
```

**In the web UI:**
1. Number of users: `10`
2. Spawn rate: `2`
3. Click **"Start swarming"**

### Step 4: Monitor Dashboard (Browser Tab 2)
```
http://localhost:5000
Login: admin / admin123
```

**Watch for:**
- Request rate increases (real traffic)
- Response time spikes (real load)
- Every 30-60 seconds: Anomalies trigger
- CPU/Memory/Error rate changes

### Step 5: Stop & Review (5-10 minutes)

In Locust:
1. Let it run for 2-5 minutes
2. Click **"Stop"**
3. Check the stats tab for detailed results

**Results file:**
```bash
# Review JSON report
type load_test_results.json
```

---

## 🧪 Test Anomalies During Load Test

While load test is running, trigger anomalies:

### Get Auth Token
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
$token = $response.token
Write-Host "Token: $token"
```

### Trigger Memory Leak (45 seconds)
```powershell
$headers = @{"Authorization"="Bearer $token"; "Content-Type"="application/json"}
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body '{"anomaly_type":"memory_leak","duration":45}'
```

### Trigger CPU Spike (30 seconds)
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body '{"anomaly_type":"cpu_spike","duration":30}'
```

### Trigger Network Latency (30 seconds)
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body '{"anomaly_type":"network_latency","duration":30}'
```

### Trigger High Error Rate (30 seconds)
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body '{"anomaly_type":"high_error_rate","duration":30}'
```

---

## ✅ Quick Verification Commands

### Check Real Metrics Work
```bash
# Test collector directly
python -c "
from real_metrics_collector import RealMetricsCollector
collector = RealMetricsCollector()
collector.print_metrics()
"
```

### Check Simulator
```bash
# Test simulator
python hybrid_metrics_simulator.py
```

### Monitor Metrics Live (PowerShell)
```powershell
while($true) {
    Clear-Host
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/all"
    Write-Host "=== LIVE METRICS ===" -ForegroundColor Green
    Write-Host "CPU:    $($response.cpu_usage.value)%"
    Write-Host "Memory: $($response.memory_usage.value)%"
    Write-Host "Disk:   $($response.disk_usage.value)%"
    Write-Host "Updated: $(Get-Date)"
    Start-Sleep -Seconds 5
}
```

### Check Dashboard Endpoint
```bash
curl http://localhost:5000/api/metrics/all
```

---

## 🔧 One-Time Setup Scripts

### Complete Option 1 Setup (Copy entire script)
```bash
# Install
pip install psutil

# Change nexus_app.py (requires manual edit - see above)

# Run
python nexus_app.py
```

### Complete Option 2 Setup (Copy entire script)
```bash
# Install
pip install psutil pywin32
python Scripts/pywin32_postinstall.py -install

# Change nexus_app.py (requires manual edit - see above)

# Run
python nexus_app.py
```

### Complete Option 3 Setup (Copy entire script)
```bash
# Install
pip install psutil locust

# Change nexus_app.py (requires manual edit - see above)

# Terminal 1:
python nexus_app.py

# Terminal 2 (wait 5 seconds for app to start):
locust -f locustfile.py --host=http://localhost:5000

# Terminal 3:
# Open http://localhost:8089 in browser
```

---

## 📊 Real-Time Monitoring Commands

### Monitor CPU Every 1 Second
```powershell
while($true) {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/all"
    $cpu = $response.cpu_usage.value
    Write-Host "$(Get-Date): CPU = $cpu%" -ForegroundColor $(if([double]$cpu -gt 80) {"Red"} else {"Green"})
    Start-Sleep -Seconds 1
}
```

### Monitor All Metrics Every 5 Seconds
```powershell
while($true) {
    Clear-Host
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/all"
    $time = Get-Date
    
    Write-Host "=== AIOPS METRICS ($time) ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "CPU:     $($response.cpu_usage.value)%   [$($response.cpu_usage.status)]"
    Write-Host "Memory:  $($response.memory_usage.value)%   [$($response.memory_usage.status)]"
    Write-Host "Disk:    $($response.disk_usage.value)%   [$($response.disk_usage.status)]"
    Write-Host "Network: $($response.network_in.value) MB/s in, $($response.network_out.value) MB/s out"
    Write-Host "Requests: $($response.request_rate.value) req/sec"
    Write-Host "Errors:  $($response.error_rate.value)%"
    Write-Host ""
    
    Start-Sleep -Seconds 5
}
```

### Check Anomaly Status
```powershell
while($true) {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies"
    Write-Host "Anomaly Status: $(Get-Date)"
    foreach ($anomaly in $response.PSObject.Properties) {
        $status = if ($anomaly.Value) {"🔴 ACTIVE"} else {"✅ Inactive"}
        Write-Host "  $($anomaly.Name): $status"
    }
    Write-Host ""
    Start-Sleep -Seconds 2
}
```

---

## 🎯 Full Test Workflow (Copy Entire Section)

### Run Complete Test (All 3 options in sequence)

**Terminal 1 - Start App:**
```bash
python nexus_app.py
```

**Wait 5 seconds, then Terminal 2 - Test Option 1 (Real Metrics):**
```bash
# Verify metrics endpoint
curl http://localhost:5000/api/metrics/all | python -m json.tool

# Monitor live
while($true) {
    $r = Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/all"
    Write-Host "CPU: $($r.cpu_usage.value)% | Memory: $($r.memory_usage.value)%"
    Start-Sleep -Seconds 5
}
```

**After 2 minutes, Terminal 3 - Test Anomalies:**
```powershell
# Get token
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
$token = $response.token
$headers = @{"Authorization"="Bearer $token"; "Content-Type"="application/json"}

# Trigger memory leak
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST -Headers $headers `
  -Body '{"anomaly_type":"memory_leak","duration":30}'

# Watch memory card spike on dashboard!
```

**Terminal 4 - Optional Load Test:**
```bash
# Install if needed
pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:5000
```

Then open: `http://localhost:8089` and click "Start swarming"

---

## 💾 Environment Variables (Optional)

If you want to configure via environment variables:

```powershell
# Windows PowerShell
$env:AIOPS_USE_REAL_METRICS = "true"
$env:AIOPS_USE_PERFMON = "true"
$env:METRICS_UPDATE_INTERVAL = "5"

python nexus_app.py
```

```bash
# Linux/Mac Bash
export AIOPS_USE_REAL_METRICS=true
export AIOPS_USE_PERFMON=true
export METRICS_UPDATE_INTERVAL=5

python nexus_app.py
```

---

## 🆘 Troubleshooting Commands

### Check if psutil works
```python
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')"
```

### Check if pywin32 works
```python
python -c "import win32com.client; print('pywin32 OK')"
```

### Check if locust works
```bash
locust --version
```

### Kill app on port 5000
```powershell
# PowerShell
Get-Process -Name python | Where-Object {$_.Handles -gt 0} | Stop-Process -Force

# Or more specific:
lsof -i :5000  # Get PID
kill -9 <PID>  # Kill it
```

### Restart everything
```bash
# PowerShell
Get-Process python | Stop-Process -Force
Start-Sleep -Seconds 2
python nexus_app.py
```

---

## 📈 Expected Output

### Option 1 (Real Metrics)
```
Dashboard CPU: 8% (YOUR actual value)
Dashboard Memory: 48% (YOUR actual value)
Dashboard Disk: 32% (YOUR actual value)
Updates every 5 seconds with real values
```

### Option 2 (+ PerfMon)
```
All of Option 1, PLUS:
CPU user time: X%
CPU privileged time: Y%
Memory page faults: Z/sec
Disk queue: N
```

### Option 3 (Load Test)
```
Load test metrics shown in Locust UI
Dashboard shows:
  - Request rate: 50+ req/sec
  - Response time: 50-200ms
  - Every 30-60s: Anomalies spike
JSON report: load_test_results.json
```

---

## 🎉 Success!

If you see:
- ✅ Dashboard metrics updating with real values
- ✅ Anomalies triggering correctly
- ✅ Load test showing realistic traffic
- ✅ No errors in console

**You're done! Real telemetry is working! 🚀**

---

**Pick one option above and run it now!**

Questions? Check: [REAL_METRICS_INTEGRATION.md](REAL_METRICS_INTEGRATION.md)
