# 📊 Live Telemetry Data Sources for Injection

Guide to collecting real metrics and injecting them into your AIOPS dashboard.

---

## 🎯 Data Source Options

### **Option 1: Real System Metrics (Recommended for MVP)**
Collect metrics from your actual Windows machine using Python libraries.

**Advantages:**
- ✅ Real data from your system
- ✅ No dependencies on external services
- ✅ Works offline
- ✅ Easy to set up locally

**Tools:**
```python
# psutil - System metrics
pip install psutil

# windows-curses - Windows system info
pip install windows-curses

# pywin32 - Windows Performance Monitor
pip install pywin32
```

---

## 📈 Option 1A: Using psutil (EASIEST)

Real-time metrics from your Windows machine:

```python
import psutil
import time
from datetime import datetime

def get_real_metrics():
    """Collect real system metrics"""
    return {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'network_in': psutil.net_io_counters().bytes_recv,
        'network_out': psutil.net_io_counters().bytes_sent,
        'network_errors': psutil.net_io_counters().errin + psutil.net_io_counters().errout,
        'process_count': len(psutil.pids()),
        'open_connections': len(psutil.net_connections()),
        'disk_read_rate': psutil.disk_io_counters().read_bytes,
        'disk_write_rate': psutil.disk_io_counters().write_bytes,
        'timestamp': datetime.utcnow().isoformat()
    }

# Test it
if __name__ == '__main__':
    metrics = get_real_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
```

**Install psutil:**
```bash
pip install psutil
```

---

## 📈 Option 1B: Windows Performance Monitor

Access Windows native performance counters:

```python
import win32com.client
from datetime import datetime

def get_windows_perfmon_metrics():
    """Get metrics from Windows Performance Monitor"""
    objWMIService = win32com.client.GetObject("winmgmts:")
    
    # CPU Usage
    cpu = objWMIService.ExecQuery(
        "Select * from Win32_PerfFormattedData_PerfOS_Processor where Name='_Total'"
    )[0]
    
    # Memory
    memory = objWMIService.ExecQuery(
        "Select * from Win32_PerfFormattedData_PerfOS_Memory"
    )[0]
    
    # Disk
    disk = objWMIService.ExecQuery(
        "Select * from Win32_PerfFormattedData_PerfLogicalDisk where Name='C:'"
    )[0]
    
    return {
        'cpu_usage': float(cpu.PercentProcessorTime),
        'memory_usage': float(memory.PercentCommittedBytesInUse),
        'disk_read_rate': float(disk.DiskReadBytesPerSec),
        'disk_write_rate': float(disk.DiskWriteBytesPerSec),
        'timestamp': datetime.utcnow().isoformat()
    }
```

**Install pywin32:**
```bash
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

---

## 📈 Option 2: Prometheus Scraping

If you have Prometheus running locally or remotely:

```python
import requests
from datetime import datetime

def get_prometheus_metrics(prometheus_url="http://localhost:9090"):
    """Query metrics from Prometheus"""
    
    queries = {
        'cpu_usage': 'rate(cpu_time[5m])',
        'memory_usage': 'node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes',
        'disk_usage': 'node_filesystem_avail_bytes / node_filesystem_size_bytes',
        'network_in': 'rate(node_network_receive_bytes_total[5m])',
        'network_out': 'rate(node_network_transmit_bytes_total[5m])',
        'request_rate': 'rate(http_requests_total[5m])',
        'error_rate': 'rate(http_requests_total{status=~"5.."}[5m])',
    }
    
    metrics = {}
    
    for name, query in queries.items():
        url = f"{prometheus_url}/api/v1/query"
        response = requests.get(url, params={'query': query})
        
        if response.status_code == 200:
            result = response.json()['data']['result']
            if result:
                metrics[name] = float(result[0]['value'][1])
    
    return metrics

# Usage
prometheus_url = "http://localhost:9090"  # Adjust to your Prometheus
metrics = get_prometheus_metrics(prometheus_url)
print(metrics)
```

**Start local Prometheus:**
```bash
# Download from: https://prometheus.io/download/
# Create prometheus.yml with node exporter targets
# Run: ./prometheus.exe
```

---

## 📈 Option 3: Existing Application Logs

Parse metrics from application logs:

```python
import json
import re
from datetime import datetime
from pathlib import Path

def parse_application_logs(log_file):
    """Extract metrics from application logs"""
    
    metrics = {
        'request_rate': 0,
        'error_rate': 0,
        'response_time_ms': 0,
        'error_count': 0,
        'request_count': 0,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if not Path(log_file).exists():
        return metrics
    
    with open(log_file, 'r') as f:
        lines = f.readlines()[-1000:]  # Last 1000 lines
    
    for line in lines:
        # Parse your log format
        if 'ERROR' in line:
            metrics['error_count'] += 1
        if 'REQUEST' in line:
            metrics['request_count'] += 1
        
        # Extract response time if available
        match = re.search(r'response_time[=:](\d+)', line, re.IGNORECASE)
        if match:
            metrics['response_time_ms'] = float(match.group(1))
    
    # Calculate rates
    metrics['error_rate'] = metrics['error_count'] / max(1, metrics['request_count'])
    metrics['request_rate'] = metrics['request_count'] / 60  # per second
    
    return metrics

# Usage
app_logs = "C:\\path\\to\\app.log"
metrics = parse_application_logs(app_logs)
print(metrics)
```

---

## 📈 Option 4: Load Generation Tools (Create Load & Capture Metrics)

Generate realistic traffic to your app and capture metrics:

### **4A: Using Locust (Recommended)**

```python
# locustfile.py
from locust import HttpUser, task, between
import psutil
from datetime import datetime

class MetricsCollector:
    """Collect metrics during load test"""
    
    def __init__(self):
        self.metrics_log = []
    
    def record(self):
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'memory_usage': psutil.virtual_memory().percent,
            'request_count': len(self.metrics_log),
            'error_count': sum(1 for m in self.metrics_log if m.get('error'))
        }
        self.metrics_log.append(metrics)
        return metrics

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(1)
    def index(self):
        self.client.get("/")
    
    @task(2)
    def api_metrics(self):
        self.client.get("/api/metrics/all")
    
    @task(1)
    def api_anomaly(self):
        self.client.post("/api/metrics/anomalies/trigger", 
                        json={"anomaly_type": "cpu_spike", "duration": 10})

# Run: locust -f locustfile.py --host=http://localhost:5000
```

**Install Locust:**
```bash
pip install locust
```

**Run load test:**
```bash
locust -f locustfile.py --host=http://localhost:5000 -u 10 -r 2
```

### **4B: Using Apache JMeter**

```
1. Download from: https://jmeter.apache.org/
2. Create test plan with HTTP requests
3. Add listeners to capture metrics
4. Export results as CSV
5. Parse CSV and inject into dashboard
```

**Parse JMeter results:**
```python
import csv
from datetime import datetime

def parse_jmeter_results(csv_file):
    """Parse JMeter results and extract metrics"""
    
    metrics = {
        'request_count': 0,
        'error_count': 0,
        'avg_response_time': 0,
        'max_response_time': 0,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    response_times = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metrics['request_count'] += 1
            
            if row['success'] == 'false':
                metrics['error_count'] += 1
            
            response_times.append(float(row['elapsed']))
    
    if response_times:
        metrics['avg_response_time'] = sum(response_times) / len(response_times)
        metrics['max_response_time'] = max(response_times)
    
    return metrics
```

---

## 🔗 Option 5: Connect to Existing Monitoring Platforms

### **Prometheus (Most Compatible)**
```python
# Already covered above
prometheus_url = "http://localhost:9090"
```

### **InfluxDB**
```python
from influxdb import InfluxDBClient

def get_influxdb_metrics(host='localhost', port=8086, db='mydb'):
    """Query InfluxDB for metrics"""
    
    client = InfluxDBClient(host=host, port=port, database=db)
    
    query = 'SELECT last("value") FROM "cpu_usage" WHERE time > now() - 1h'
    result = client.query(query)
    
    metrics = {}
    for measurement in result:
        for point in measurement:
            metrics[measurement.name] = point['value']
    
    return metrics

# Usage
# pip install influxdb
metrics = get_influxdb_metrics()
```

### **Grafana (Datasource)**
```python
import requests

def get_grafana_data(grafana_url, datasource_id, query):
    """Query Grafana datasource"""
    
    url = f"{grafana_url}/api/datasources/proxy/{datasource_id}/query"
    
    response = requests.post(url, json={'query': query})
    data = response.json()
    
    return data

# Usage
grafana_url = "http://localhost:3000"
datasource_id = 1  # Prometheus
query = 'rate(cpu_usage[5m])'

metrics = get_grafana_data(grafana_url, datasource_id, query)
```

### **Datadog / New Relic / AWS CloudWatch**
```python
# Datadog
from datadog import api

api.api_key = "YOUR_API_KEY"
api.app_key = "YOUR_APP_KEY"

# Query metrics
metrics = api.Metric.query(
    start=1234567890,
    query='avg:system.cpu{*}'
)
```

---

## 🧪 Recommended Setup for MVP

**For fastest testing, use this combination:**

### **Step 1: Collect Real System Metrics**
```bash
pip install psutil
```

### **Step 2: Modify metrics_simulator.py to use real data**

```python
# metrics_simulator.py - Add real data collection

import psutil
from metrics_simulator import MetricsSimulator

class HybridMetricsSimulator(MetricsSimulator):
    """Blend real system metrics with simulated data"""
    
    def __init__(self, use_real=True):
        super().__init__()
        self.use_real = use_real
    
    def update_metrics(self):
        """Override to use real data"""
        
        if self.use_real:
            # Real metrics
            self.metrics['cpu_usage']['value'] = psutil.cpu_percent(interval=0.5)
            self.metrics['memory_usage']['value'] = psutil.virtual_memory().percent
            self.metrics['disk_usage']['value'] = psutil.disk_usage('/').percent
            
            net = psutil.net_io_counters()
            self.metrics['network_in']['value'] = net.bytes_recv / (1024*1024)  # MB
            self.metrics['network_out']['value'] = net.bytes_sent / (1024*1024)  # MB
            
            self.metrics['process_count']['value'] = len(psutil.pids())
            self.metrics['open_connections']['value'] = len(psutil.net_connections())
        
        # Call parent to apply anomalies on top
        return super().update_metrics()
```

### **Step 3: Use in your app**

```python
# In nexus_app.py

from hybrid_metrics_simulator import HybridMetricsSimulator

def initialize_on_startup():
    # Use hybrid simulator with real data
    simulator = HybridMetricsSimulator(use_real=True)
    start_metrics_collection()
    init_storage()
    # ... rest of initialization
```

---

## 🚀 Quick Start: Real System Metrics

**Complete example to inject real metrics:**

```python
# real_metrics_injector.py
import psutil
import requests
import time
from datetime import datetime
import json

class RealMetricsInjector:
    """Inject real system metrics into your dashboard"""
    
    def __init__(self, api_url="http://localhost:5000", interval=5):
        self.api_url = api_url
        self.interval = interval
        self.token = None
        self.authenticate()
    
    def authenticate(self):
        """Get auth token"""
        response = requests.post(
            f"{self.api_url}/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        self.token = response.json().get('token')
        print(f"✅ Authenticated: {self.token[:20]}...")
    
    def get_real_metrics(self):
        """Collect real system metrics"""
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        
        return {
            'cpu_usage': cpu,
            'memory_usage': mem.percent,
            'disk_usage': disk.percent,
            'network_in': net.bytes_recv / (1024*1024),  # MB
            'network_out': net.bytes_sent / (1024*1024),  # MB
            'process_count': len(psutil.pids()),
            'open_connections': len(psutil.net_connections()),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def inject_metrics(self):
        """Send metrics to dashboard"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        metrics = self.get_real_metrics()
        
        # Your custom endpoint to inject metrics
        response = requests.post(
            f"{self.api_url}/api/metrics/inject",
            headers=headers,
            json=metrics
        )
        
        print(f"✅ Injected: CPU={metrics['cpu_usage']:.1f}%, "
              f"Mem={metrics['memory_usage']:.1f}%")
        
        return response.status_code == 200
    
    def run_continuously(self):
        """Continuously inject metrics"""
        print(f"🚀 Starting metric injection every {self.interval}s...")
        
        try:
            while True:
                self.inject_metrics()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")

if __name__ == '__main__':
    injector = RealMetricsInjector()
    injector.run_continuously()
```

**Run it:**
```bash
python real_metrics_injector.py
```

---

## 📋 Data Source Comparison

| Source | Setup Time | Real Data | Offline | Best For |
|--------|-----------|-----------|---------|----------|
| **psutil** | 5 min | ✅ | ✅ | MVP testing |
| **Windows PerfMon** | 10 min | ✅ | ✅ | Detailed metrics |
| **Prometheus** | 30 min | ✅ | ⚠️ | Production |
| **Locust** | 20 min | ✅ | ✅ | Load testing |
| **Application Logs** | 15 min | ✅ | ✅ | App-specific data |
| **InfluxDB** | 30 min | ✅ | ⚠️ | Time-series DB |
| **Datadog/CloudWatch** | 45 min | ✅ | ❌ | Cloud platforms |

---

## 🎯 Recommendation for Your MVP

**Start with Option 1A (psutil):**

1. ✅ Simplest to set up (1 command: `pip install psutil`)
2. ✅ No external dependencies
3. ✅ Real data from your machine
4. ✅ Works offline
5. ✅ Perfect for testing dashboard
6. ✅ Can add anomalies on top

**After MVP testing passes:**
- Integrate with production Prometheus/InfluxDB
- Add log parsing for app metrics
- Connect to cloud monitoring (AWS/Azure/GCP)

---

## 🔄 Integration Steps

1. **Install psutil:**
   ```bash
   pip install psutil
   ```

2. **Create hybrid simulator** (uses real + simulated data)
   ```python
   # See code example above
   ```

3. **Update nexus_app.py** to use HybridMetricsSimulator

4. **Start dashboard with real metrics:**
   ```bash
   python nexus_app.py
   ```

5. **Test with real system load:**
   ```bash
   # Open dashboard
   # Run: Get-Process python | Measure-Object -Sum Handles
   # CPU/memory usage shows real values
   ```

---

**Ready to inject live telemetry? Let me know which source you want to use!** 🚀
