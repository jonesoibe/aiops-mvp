# Phase 2 - Real-Time Dashboard Testing Guide

## 🧪 Testing Overview

This guide walks you through comprehensive testing of the new real-time Overview dashboard with live metrics, WebSocket updates, and anomaly detection.

**Estimated Testing Time:** 30-45 minutes

---

## ✅ Pre-Flight Checklist

Before testing, verify:

```bash
# 1. App is running
python nexus_app.py

# 2. Check app started correctly
# Look for:
# ✅ Metrics collection started
# ✅ Prometheus storage initialized
# ✅ Access at: http://localhost:5000
```

**If app doesn't start:**
- Kill old processes: `Get-Process python | Stop-Process -Force`
- Check for port conflicts: `netstat -ano | findstr :5000`
- Restart: `python nexus_app.py`

---

## 📋 Testing Scenarios

### SCENARIO 1: Dashboard Loads & Metrics Display

**Duration:** 2 minutes

**Steps:**
1. Open browser: `http://localhost:5000`
2. Login with: `admin` / `admin123`
3. You should see Overview dashboard

**Expected Results:**
```
✅ Page loads without errors
✅ Summary panel shows:
   - Healthy Percentage (66-72%)
   - Warning Metrics (0-3)
   - Critical Metrics (2-5)
   - Live indicator (blinking dot)

✅ 6 Metric Cards visible:
   - CPU Usage (💻): ~37-45%
   - Memory Usage (🧠): ~45-65%
   - Disk Usage (💾): ~55-70%
   - Network I/O (🌐): ~100-200 ops/sec
   - Request Rate (📊): ~400-600 req/sec
   - Error Rate (⚠️): ~0.1-0.5%

✅ All cards show:
   - Current value
   - Unit (%, ops/sec, etc)
   - Status badge (green/yellow/red)
   - Timestamp
   - Sparkline chart
```

**Troubleshooting:**
- If metrics show "—": Check browser console (F12)
- If no values: Verify /api/metrics/all endpoint works
- If colors wrong: Check metric status calculation

---

### SCENARIO 2: Real-Time Updates

**Duration:** 3-5 minutes

**Steps:**
1. Stay on Overview dashboard
2. Watch metrics for 2-3 minutes
3. Note how values change every 5 seconds
4. Check the "Last Update" timestamp

**Expected Results:**
```
✅ Metrics update smoothly every 5 seconds
✅ Values change realistically (not jerky)
✅ Sparklines grow with new data points
✅ Timestamp shows "now" (00:05, 00:10, etc)
✅ Change indicator shows % change (📈/📉)
✅ No console errors in browser dev tools (F12 → Console)
```

**Verification:**
- Open browser DevTools: `F12`
- Go to Console tab
- Should see no red error messages
- Should see socket.io connection messages

**Troubleshooting:**
- If updates stop: Check WebSocket connection
  - Open DevTools → Network → WS (WebSockets)
  - Should see `/socket.io` connection
  - Status should be "101 Switching Protocols"
- If metrics freeze: Refresh page (F5)
- If values jump erratically: Check for network lag

---

### SCENARIO 3: Color Coding & Status

**Duration:** 5 minutes

**Steps:**
1. Watch dashboard for several updates
2. Note which cards are green/yellow/red
3. Compare values to thresholds

**Expected Results:**
```
✅ GREEN (Healthy):
   - CPU < 65%: Usually green
   - Memory < 65%: Sometimes green

✅ YELLOW (Warning):
   - CPU 65-85%: Occasional yellow
   - Memory 65-85%: Often yellow

✅ RED (Critical):
   - CPU > 85%: Rare (will be red)
   - Memory > 85%: Rare (will be red)

✅ Color Animations:
   - Red cards pulse/blink
   - Yellow cards pulse slightly
   - Green cards static
```

**Verification:**
```
Expected color distribution:
- Healthy: ~66% of metrics (12 cards)
- Warning: ~6% of metrics (1 card)
- Critical: ~28% of metrics (5 cards)

This matches the summary panel numbers!
```

**Troubleshooting:**
- If all green: Metrics not updating or threshold wrong
- If wrong colors: Check CSS in browser DevTools
- If no pulsing: Check CSS animations enabled

---

### SCENARIO 4: Sparkline Charts

**Duration:** 3 minutes

**Steps:**
1. Watch sparklines update
2. Watch how they visualize trends
3. Observe as new data points are added

**Expected Results:**
```
✅ Sparklines visible on each card
✅ Line shows metric trend over time
✅ Updates smoothly as new data arrives
✅ Scales to show min-max range
✅ Color matches theme (info color - cyan)

✅ After 20 updates (~100 seconds):
   - Sparkline filled with 20 data points
   - Old points fade out
   - Shows complete trend visualization
```

**Verification:**
- Sparklines should form a visible line
- Line should move up/down with metric changes
- Should not look flat or stuck

**Troubleshooting:**
- If sparklines blank: Check SVG rendering
- If no line visible: Check metric history array
- If crashes: Check for NaN values

---

### SCENARIO 5: Anomaly Injection

**Duration:** 10 minutes

**This is the critical test!**

**Preparation:**
```bash
# Terminal 1: Keep app running
python nexus_app.py

# Terminal 2: Get fresh auth token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python -m json.tool

# Copy the "token" value from response
TOKEN="eyJhbGc... (your token)"
```

**Test 5A: Memory Leak Anomaly**

```bash
# Trigger memory leak for 45 seconds
curl -X POST http://localhost:5000/api/metrics/anomalies/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"anomaly_type":"memory_leak","duration":45}'
```

**Watch Dashboard For:**
```
✅ Response shows: {"status": "triggered", "anomaly": "memory_leak", "duration": 45}

✅ Within 5 seconds on dashboard:
   - Memory card changes color (yellow → red)
   - Memory value starts increasing faster
   - Change indicator shows 📈 (up)
   - Anomalies section shows "MEMORY LEAK: 🔴 ACTIVE"

✅ After 45 seconds:
   - Anomaly indicator turns off
   - Status shows "✅ Inactive"
   - Memory growth slows down (anomaly over)
```

**Verification Checklist:**
- [ ] Dashboard responds to anomaly within 5 seconds
- [ ] Memory card color changes appropriately
- [ ] Anomaly section updates in real-time
- [ ] After duration expires, anomaly deactivates
- [ ] No console errors during anomaly

**Test 5B: CPU Spike Anomaly**

```bash
curl -X POST http://localhost:5000/api/metrics/anomalies/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"anomaly_type":"cpu_spike","duration":30}'
```

**Watch For:**
```
✅ CPU card turns yellow/red
✅ CPU value jumps higher
✅ Sparkline shows spike
✅ Anomalies section: "CPU SPIKE: 🔴 ACTIVE"
✅ After 30 seconds: Returns to normal
```

**Test 5C: Network Latency Anomaly**

```bash
curl -X POST http://localhost:5000/api/metrics/anomalies/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"anomaly_type":"network_latency","duration":30}'
```

**Watch For:**
```
✅ Response Time increases significantly
✅ Card color changes appropriately
✅ Anomaly listed as "NETWORK LATENCY: 🔴 ACTIVE"
```

**Test 5D: High Error Rate Anomaly**

```bash
curl -X POST http://localhost:5000/api/metrics/anomalies/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"anomaly_type":"high_error_rate","duration":30}'
```

**Watch For:**
```
✅ Error Rate card shows increase
✅ Status changes to critical
✅ Anomaly shows "HIGH ERROR RATE: 🔴 ACTIVE"
```

---

## 📱 SCENARIO 6: Responsive Design

**Duration:** 5 minutes

**Steps:**
1. Keep dashboard open
2. Resize browser window
3. Test different screen sizes

**Expected Results:**
```
✅ Desktop (1920px+):
   - 6 cards in 2 rows
   - Full sparklines visible
   - Optimal spacing

✅ Tablet (768px - 1024px):
   - 3-4 cards per row
   - Responsive spacing
   - Still readable

✅ Mobile (375px):
   - 1 card per row
   - Stacked vertically
   - Touch-friendly sizing
   - No horizontal scroll
```

**Verification:**
- Open DevTools (F12)
- Click device toggle (📱 icon)
- Test presets: Mobile, Tablet, Desktop
- Verify no layout breaks

---

## 🔍 SCENARIO 7: WebSocket Stability

**Duration:** 8 minutes

**Steps:**
1. Keep dashboard running
2. Open DevTools → Network → WS
3. Watch for disconnections
4. Monitor for message frequency

**Expected Results:**
```
✅ WebSocket Status: "101 Switching Protocols"
✅ Connected for full test duration
✅ Messages arriving every 5 seconds
✅ No reconnection attempts (unless intentional)

✅ Messages should show:
   - telemetry_update events
   - Payload with metrics, summary, anomalies
   - Proper JSON structure
```

**Verification:**
- Click on /socket.io connection in Network tab
- Check "Messages" subtab
- Count events per minute
- Should see ~12 events per minute (one every 5 sec)

**Troubleshooting:**
- If messages stop: Check server logs
- If frequent reconnects: Network instability
- If wrong frequency: Check interval in app

---

## 📊 SCENARIO 8: Performance & Memory

**Duration:** 5 minutes

**Steps:**
1. Open DevTools → Performance tab
2. Click Record
3. Wait 30 seconds
4. Stop recording
5. Analyze results

**Expected Results:**
```
✅ CPU Usage: < 5% most of the time
✅ Frame Rate: 60 FPS (smooth)
✅ No janky frames
✅ Memory stable (not growing unbounded)

✅ Network Traffic: < 10KB per update
✅ No memory leaks
✅ Clean garbage collection

Performance Metrics:
- Page Load: < 2 seconds
- First Paint: < 1 second
- DOM Interactive: < 1.5 seconds
- DOM Complete: < 2 seconds
```

**Verification:**
- Check DevTools Performance report
- Look for red bars (indicates performance issues)
- Check Memory timeline
- Should be relatively flat line (not climbing)

---

## 📋 Testing Completion Checklist

Run through this final checklist:

```
METRICS & DATA:
☐ All 6 metrics visible and displaying values
☐ Values are realistic (not extreme)
☐ Summary statistics match metric count
☐ Timestamps update every 5 seconds

VISUAL & STYLING:
☐ Color coding works correctly (green/yellow/red)
☐ Sparklines render without errors
☐ Change indicators show (📈/📉)
☐ Pulsing animations on critical metrics
☐ Responsive layout on different screen sizes

REAL-TIME UPDATES:
☐ Metrics update every 5 seconds
☐ WebSocket connection stable
☐ No console errors
☐ Smooth transitions, no jumps

ANOMALIES:
☐ Memory leak anomaly triggers correctly
☐ CPU spike anomaly works
☐ Network latency anomaly responds
☐ High error rate anomaly functions
☐ Anomalies clear after duration expires
☐ Anomaly section updates in real-time

PERFORMANCE:
☐ Page responsive (no lag)
☐ Smooth animations
☐ No memory leaks
☐ WebSocket messages consistent
☐ CPU usage reasonable (< 5%)

ACCESSIBILITY:
☐ Dashboard loads on mobile
☐ Touch interactions work
☐ Text is readable
☐ No layout breaks
```

---

## 🐛 Issue Tracking

If you find issues, document them:

### Issue Template
```
**Title:** [Brief description]
**Severity:** Critical / High / Medium / Low
**Reproduction:**
1. Step 1
2. Step 2
3. Expected result
4. Actual result

**Details:**
- Browser: Chrome/Firefox/Safari
- Device: Desktop/Tablet/Mobile
- Console errors: [Yes/No] - [Error message if any]

**Screenshots:** [If helpful]
```

---

## ✨ Expected Test Outcomes

**If all tests pass:** Dashboard is ready for Phase 2 Steps 2-5!

**If minor issues found:**
- Document them
- Create GitHub issues
- Plan fixes for next phase

**If critical issues found:**
- Fix immediately
- Re-test affected scenarios
- Document root causes

---

## 🎯 Next Steps After Testing

1. **If tests pass (95%+):** Proceed to Phase 2 Steps 2-5
2. **If issues found:** Create GitHub issues and fix before continuing
3. **If major problems:** Investigate root causes and redesign

---

**Happy Testing! 🚀**

Report back with your findings!
