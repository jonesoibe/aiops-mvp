# AIOps MVP - Complete Dashboards Guide

## 📊 Overview

Your AIOps system now includes **5 professional-grade dashboards** (Dynatrace-style) for complete visibility into incident detection, infrastructure health, and system performance:

---

## 🎯 Available Dashboards

### **1. 🏠 Main Dashboard**

**URL:** `http://localhost:5000/`

The primary dashboard showing:

- ✅ Overview metrics (anomalies, incidents, classification)
- 🔥 Chaos simulation results with detection breakdown
- 🔬 Detection methods explanation
- 🔒 Security best practices guide
- 📚 API documentation

**Best for:** Getting started, understanding the system, running demos

---

### **2. 🚨 Problems Page** ⭐ NEW

**URL:** `http://localhost:5000/problems`

**Features:**

- 📋 **Problem List** - All detected incidents with full details
  - Problem ID, Title, Severity (Critical/High/Medium/Low)
  - Status (New/Acknowledged/Resolved)
  - Detected time, Duration
  - Root cause analysis
  - Impact metrics (users affected, error rate, performance impact)
  - Auto-actions taken
  - Manual review items pending

- 🔍 **Filtering & Sorting**
  - Filter by: All, Critical, High, Open, Resolved
  - Sort by: Latest First, Severity

- 📊 **Statistics Panel**
  - Open Problems count
  - Critical Issues count
  - Average Resolution Time
  - Affected Services

- 📈 **Impact Analysis**
  - Affected Services with health indicators
  - Performance Impact metrics
  - Remediation Status

- 🎯 **Action Buttons per Problem**
  - View Details
  - Root Cause Analysis
  - Acknowledge
  - Resolve

**Use case:** SysAdmin reviewing open problems, triaging incidents, tracking resolution progress

---

### **3. 🏗️ Infrastructure Page** ⭐ NEW

**URL:** `http://localhost:5000/infrastructure`

**Features:**

- 🌐 **Service Topology & Health**
  - 6 microservices shown with health status
  - Real-time health indicators:
    - API Gateway (Healthy)
    - API Server (Critical - 87% CPU)
    - Database (Critical - 450ms latency)
    - Cache Layer (Warning - 92% memory)
    - Message Queue (Healthy)
    - Search Engine (Healthy)
  - Key metrics per service (latency, errors, CPU, throughput)

- 📊 **Key Performance Metrics**
  - Response Time (P95): 450ms [Critical]
  - Error Rate: 2.3% [Warning]
  - API Server CPU: 87% [Critical]
  - Database Memory: 68% [Normal]
  - Cache Hit Ratio: 92% [Warning]
  - Throughput: 8.8k req/s [Normal]
  - Progress bars with threshold indicators
  - Color-coded status (Green/Yellow/Red)

- 💡 **Smart Recommendations**
  - Scale API server from 2→3 replicas
  - Add database index on user_sessions
  - Increase cache TTL for hot data
  - Review traffic spike patterns

- 📋 **Service Details Table**
  - Comprehensive view of all services
  - Columns: Service, Health, CPU, Memory, P95 Latency, Error Rate, Throughput, Last Alert
  - Sortable and interactive

- ⏱️ **Time Range Selection**
  - Last 2h (default)
  - Last 6h
  - Last 24h
  - Last 7d

**Use case:** Infrastructure monitoring, capacity planning, performance optimization, SLA tracking

---

### **4. 🚨 Incident Response Simulator**

**URL:** `http://localhost:5000/demo`

**Features:**

- ▶️ Start/Stop simulation controls
- ⚡ Speed controls (Normal/Fast)
- 📊 Step-by-step visualization of:
  - Anomaly Detection
  - Classification
  - Automated Actions
  - Manual Review Items
  - Decision Points
- 📈 Live metrics updates

**Use case:** Demonstration, training, understanding the complete workflow

---

## 🎨 Design Philosophy

All dashboards follow the **Dynatrace-inspired design** with:

- 🌙 Dark theme optimized for 24/7 monitoring
- 📊 Real-time metric visualization
- 🎯 Color-coded severity indicators
  - 🟢 Green = Healthy/Normal
  - 🟡 Yellow = Warning
  - 🔴 Red = Critical
- ⚡ Fast, responsive interface
- 📱 Responsive design (works on desktop, tablet, mobile)

---

## 🔄 Workflow: How to Use These Dashboards

### **Scenario 1: Incident Alert Arrives**

1. **Check Problems Page** (`/problems`)
   - See the alert in the problems list
   - Severity: Critical/High/Medium/Low
   - Status: New → Acknowledge → Resolve
   - Root cause displayed

2. **View Infrastructure Page** (`/infrastructure`)
   - Identify affected services
   - Check metric thresholds
   - See recommendations

3. **Take Action**
   - Click "Root Cause Analysis" button
   - Review auto-actions taken
   - Manually review pending items
   - Acknowledge/Resolve incident

4. **Track Resolution**
   - Monitor in Problems page
   - Watch metrics improve in Infrastructure page

---

### **Scenario 2: Capacity Planning**

1. **Open Infrastructure Page** (`/infrastructure`)
2. **Review Metrics:**
   - CPU usage trends
   - Memory utilization
   - Throughput capacity
   - Error rates

3. **Apply Recommendations:**
   - Scale services as suggested
   - Optimize queries
   - Adjust cache settings

4. **Verify in Problems Page:**
   - Ensure no new incidents
   - Check resolution status

---

### **Scenario 3: System Understanding (for new team members)**

1. **Start with Main Dashboard** (`/`)
   - Understand system overview
   - Learn detection methods
   - Review security practices

2. **Explore Infrastructure Page** (`/infrastructure`)
   - See service dependencies
   - Learn about metrics
   - Understand thresholds

3. **Run Demo Simulation** (`/demo`)
   - Watch incident lifecycle
   - See automated vs manual actions
   - Understand decision points

4. **Review Documentation**
   - Read INCIDENT_RESPONSE_DEMO.md
   - Understand detection algorithms
   - Learn security guidelines

---

## 📊 Key Metrics Explained

### **Problems Page Metrics:**

- **Open Problems:** Number of unresolved incidents
- **Critical Issues:** High-priority incidents requiring immediate action
- **Avg Resolution Time:** Average time to resolve incidents (Last 30 days)
- **Affected Services:** Count of services currently experiencing issues

### **Infrastructure Page Metrics:**

- **Response Time (P95):** 95th percentile latency (should be < 200ms)
- **Error Rate:** % of failed requests (should be < 1%)
- **CPU Usage:** Service CPU consumption (should be < 75%)
- **Memory:** RAM usage per service (should be < 85%)
- **Cache Hit Ratio:** % of cache hits (should be > 95%)
- **Throughput:** Requests per second (shows capacity utilization)

---

## 🎯 Status Indicators Guide

### **Service Health Status:**

- 🟢 **Healthy** - All metrics normal, no issues
- 🟡 **Warning** - One or more metrics at threshold
- 🔴 **Critical** - One or more metrics exceeded threshold

### **Problem Status:**

- 🔴 **New** - Newly detected, needs acknowledgment (pulsing red)
- 🟡 **Acknowledged** - Team aware, in progress
- 🟢 **Resolved** - Incident closed

### **Severity Levels:**

- 🔴 **CRITICAL** - Immediate action required
- 🟠 **HIGH** - Urgent attention needed
- 🔵 **MEDIUM** - Monitor, plan resolution
- 🟢 **LOW** - Information only, no action needed

---

## 🔧 Customization Options

### **Time Range Filtering:**

Use time-range buttons on Infrastructure page to analyze:

- Last 2 hours (real-time monitoring)
- Last 6 hours (recent trends)
- Last 24 hours (daily patterns)
- Last 7 days (weekly capacity analysis)

### **Problem Filtering:**

Use filter buttons on Problems page:

- **All** - All incidents
- **Critical** - Only critical severity
- **High** - High severity and above
- **Open** - Unresolved incidents
- **Resolved** - Closed incidents

### **Sorting:**

- **Latest First** - Most recent incidents at top
- **Severity** - Highest severity incidents first

---

## 🚀 Integration with Your Workflow

### **For On-Call Engineers:**

1. Open Problems page on arrival
2. Check for NEW/critical incidents
3. Review root causes
4. Take manual actions as needed
5. Update status as you work

### **For SysAdmins:**

1. Monitor Infrastructure page continuously
2. Watch for warnings on metrics
3. Apply recommendations proactively
4. Scale services before incidents occur
5. Review trends daily/weekly

### **For Engineering Teams:**

1. Use Problems page for incident postmortems
2. Review root causes and patterns
3. Update code/configurations
4. Test changes on Infrastructure page
5. Verify resolution before closing ticket

### **For Management/Leadership:**

1. Check Problems page for incident status
2. Review MTTR (Mean Time To Resolution)
3. Monitor affected user count
4. Track SLA compliance
5. Plan capacity investments

---

## 📈 Performance Metrics Dashboard Features

| Dashboard          | Metrics   | Alerts     | Recommendations | Status  |
| ------------------ | --------- | ---------- | --------------- | ------- |
| **Main**           | Overview  | None       | General         | ✅ Live |
| **Problems**       | Incidents | Severity   | RCA             | ✅ Live |
| **Infrastructure** | Services  | Thresholds | Auto-generated  | ✅ Live |
| **Demo**           | Workflow  | None       | Educational     | ✅ Live |

---

## 🔐 Access & Permissions

All dashboards are **currently public** on localhost:5000

**Production Deployment:**

- Add authentication via Flask-Login
- Enable role-based access control (RBAC)
- Implement API key authentication
- Use HTTPS/TLS encryption

---

## 🎓 Training New Team Members

### **Day 1 Orientation:**

1. Show Main Dashboard (`/`)
2. Explain why each page exists
3. Run Demo (`/demo`)
4. Walk through one Problems page incident

### **Day 2-3 Hands-On:**

1. Monitor Infrastructure page
2. Identify metrics and thresholds
3. Apply recommendations
4. Track changes in Problems page

### **Week 1 Competency:**

1. Can identify incident severity
2. Understands service dependencies
3. Can apply recommendations
4. Knows when to escalate

---

## 📞 Quick Reference

**Dashboard URLs:**

- Main: `http://localhost:5000/`
- Problems: `http://localhost:5000/problems`
- Infrastructure: `http://localhost:5000/infrastructure`
- Demo: `http://localhost:5000/demo`

**Key Shortcuts:**

- Filter Critical: Click "Critical" button on Problems page
- View Service Details: Click on service name on Infrastructure page
- Check Status: Problems page status indicator (top-left)
- Get Recommendations: Scroll to "💡 Recommendations" on Infrastructure page

---

✅ Real-time problem tracking  
✅ Infrastructure health monitoring  
✅ Service topology visualization  
✅ Automated recommendations  
✅ Incident workflow management  
✅ Training & demo capabilities
