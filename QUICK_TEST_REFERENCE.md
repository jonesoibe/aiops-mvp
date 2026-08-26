# ⚡ Quick Test Reference

**Complete testing in < 10 minutes**

## 🚀 Start App

```powershell
python nexus_app.py
```

Wait for:
```
✅ Metrics collection started
✅ Prometheus storage initialized  
```

## 🌐 Access Dashboard

```
http://localhost:5000
Login: admin / admin123
```

## ✅ 4-Step Verification

### Step 1: Visual Check (1 min)
- ✅ Page loads
- ✅ 6 metric cards visible
- ✅ Summary shows counts (healthy%, warning, critical)
- ✅ Sparkline charts visible

### Step 2: Real-Time Updates (2 min)
- ✅ Watch metrics for 1-2 minutes
- ✅ Values change every 5 seconds
- ✅ Timestamp updates
- ✅ No console errors (F12)

### Step 3: Anomaly Trigger (5 min)

**Get Token:**
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
  
$token = $response.token
Write-Host "Token: $token"
```

**Trigger Memory Leak:**
```powershell
$headers = @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json"}
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body '{"anomaly_type":"memory_leak","duration":45}'
```

**Watch Dashboard:**
- ✅ Memory card turns red within 5 seconds
- ✅ Value increases faster
- ✅ Anomalies section shows "MEMORY LEAK: 🔴 ACTIVE"
- ✅ After 45 sec: Anomaly clears

### Step 4: Responsive Check (2 min)
- ✅ Press F12 → Device Toggle (📱)
- ✅ Test Mobile (375px)
- ✅ No horizontal scroll
- ✅ Cards stack vertically
- ✅ Readable on small screen

## 🧪 All 4 Anomalies (optional, 10 min)

```powershell
# Memory Leak (45 sec)
$body1 = '{"anomaly_type":"memory_leak","duration":45}'

# CPU Spike (30 sec)
$body2 = '{"anomaly_type":"cpu_spike","duration":30}'

# Network Latency (30 sec)
$body3 = '{"anomaly_type":"network_latency","duration":30}'

# High Error Rate (30 sec)
$body4 = '{"anomaly_type":"high_error_rate","duration":30}'

# Trigger each with:
Invoke-RestMethod -Uri "http://localhost:5000/api/metrics/anomalies/trigger" `
  -Method POST `
  -Headers $headers `
  -Body $bodyX
```

**Expected Results:**
| Anomaly | Watch For |
|---------|-----------|
| Memory Leak | Memory card ↑ red |
| CPU Spike | CPU card ↑ red |
| Network Latency | Response time ↑ |
| High Error Rate | Error rate ↑ red |

## 📊 Final Checklist

```
✅ Page loads without errors
✅ Metrics display with realistic values
✅ Values update every 5 seconds
✅ Color coding works (green/yellow/red)
✅ Sparklines render properly
✅ Anomalies trigger and clear
✅ Responsive on mobile
✅ No console errors
✅ WebSocket stays connected
```

## 🎯 Success Criteria

**PASS:** ✅ All items checked
**WARN:** ⚠️ 1-2 minor issues
**FAIL:** ❌ 3+ issues or crashes

---

## 📝 Report Issues

```
Issue: [Name]
Severity: Critical / High / Medium / Low
Reproduction: [Steps]
Expected: [What should happen]
Actual: [What happened]
Browser: [Chrome/Firefox/Safari]
Device: [Desktop/Mobile/Tablet]
Console Error: [Yes/No] [Message]
```

---

**Testing Time: ~10-15 minutes**
**Expected Status: PASS ✅**
