# 🚀 Chaos Injection Simulator - Complete Guide

## Overview

The **Chaos Injection Simulator** is an interactive browser-based environment where you can simulate chaos scenarios and observe how the AIOps system detects and analyzes anomalies in real-time.

Think of it like **Jupyter Notebook in your browser** - specifically designed for chaos engineering and anomaly detection.

---

## 🎯 Features

### ✅ What You Can Do

1. **Run Chaos Simulations** - Inject various types of chaos (CPU spikes, memory leaks, network latency, etc.)
2. **Customize Scenarios** - Control intensity, duration, data size, and injection strategy
3. **Real-Time Console Output** - Watch the simulation execute step-by-step
4. **Multi-Tab Analysis** - Switch between console, metrics, analysis, and anomalies
5. **Live Anomaly Detection** - See how the ML model detects injected faults
6. **Detailed Metrics** - Detection rate, false positives, processing time, count

---

## 📱 Access the Simulator

### From the Web UI
1. Go to **http://localhost:5000** (or your Render URL)
2. Login with: `admin` / `admin123`
3. Sidebar → Testing & Simulation → Chaos Simulator

### On Mobile
- ✅ Sidebar works! Tap hamburger menu (☰) to open
- Interface is fully responsive
- Console & metrics stack on mobile

---

## ⚙️ Configuration Panel

### Chaos Type Options
- 💻 CPU Spike (Resource exhaustion)
- 🧠 Memory Leak (Gradual degradation)
- 💾 Disk I/O (Bottleneck performance)
- 🌐 Network Latency (Communication delays)
- 💥 Process Crash (Service failure)
- 🔒 Database Deadlock (Lock contention)

### Intensity (10-100%)
- Low: Subtle anomalies
- Medium: Clear deviations
- High: Severe faults

### Duration (10-300 seconds)
Longer = more samples

### Sample Size
- Small: 100 samples (quick)
- Medium: 1,000 samples (recommended)
- Large: 10,000 samples (comprehensive)

### Strategy
- Immediate: Instant start
- Gradual: Ramp up (realistic)
- Intermittent: Burst patterns

---

## 📊 Output Tabs

### Console Tab
Real-time execution logs showing every step.

### Metrics Tab
Key performance indicators:
- Detection Rate (%)
- Anomalies Detected (#)
- False Positive Rate (%)
- Processing Time (ms)

### Analysis Tab
Statistical details:
- Feature Mean
- Feature Std Dev
- Anomaly Score Range
- Detection Threshold

### Anomalies Tab
Table of detected anomalies with:
- Index
- Anomaly Score
- Severity (Critical/High/Medium)

---

## 🎬 How to Run

1. Configure scenario
2. Click "Run Simulation"
3. Watch Console tab
4. Check Metrics/Analysis/Anomalies tabs
5. Review detection performance

---

## 💡 Example Scenarios

### Scenario 1: CPU Spike
```
Intensity: 65% | Duration: 120s | Strategy: Gradual | Size: Large
Expected: High detection, few false positives
```

### Scenario 2: Subtle Memory Leak
```
Intensity: 25% | Duration: 60s | Strategy: Gradual | Size: Medium
Expected: Lower detection, harder to spot
```

### Scenario 3: Intermittent Failures
```
Intensity: 45% | Duration: 180s | Strategy: Intermittent | Size: Large
Expected: Burst patterns, variable detection
```

---

## 📈 Understanding Results

### Detection Rate
- >90%: Excellent
- 70-90%: Good
- <70%: Needs tuning

### False Positive Rate
- <1%: Excellent
- 1-5%: Good
- >5%: High

### Processing Time
- Typical: 100-500ms for 1K samples
- Lower is better

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Simulation timeout | Increase sample size or check logs |
| No anomalies found | Increase intensity to 80%+ |
| Too many false positives | Lower intensity or try different strategy |
| Mobile sidebar missing | Tap hamburger menu (☰) |

---

## 🚀 Next Steps

- Try different chaos types
- Vary intensity for sensitivity testing
- Use Large samples for comprehensive analysis
- Monitor detection rate vs false positives
- Compare with real incidents

**Your Nexus AIOps Chaos Simulator is ready! 🎉**
