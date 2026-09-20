# Nexus AIOps - Advanced Infrastructure Features Implementation Guide

## Overview

This guide documents the implementation of five critical infrastructure features for the Nexus AIOps platform:
1. Auto-scaling to handle load spikes
2. Alerts when CPU/Memory exceed 75% (not 90%)
3. Resource optimization analysis
4. Load balancing across multiple instances
5. Rate limiting to prevent overload

---

## 1. AUTO-SCALING TO HANDLE LOAD SPIKES

### Architecture

Auto-scaling is implemented through the `autoscaling_monitor.py` module which monitors system metrics and automatically scales instances up or down based on configurable thresholds.

### How It Works

#### Thresholds
- Scale UP: When CPU > 75% OR Memory > 75%
- Scale DOWN: When CPU < 40% AND Memory < 40%
- Min instances: 2
- Max instances: 10

#### Scaling Decision Logic
```
if (cpu > 75 || memory > 75) and current_instances < max_instances:
    scale_up()
elif (cpu < 40 && memory < 40) and current_instances > min_instances:
    scale_down()
```

### Key Files Modified
- nexus_app.py: Added auto-scaling endpoints
- docker-compose.yml: Container orchestration configuration
- autoscaler.py: Auto-scaling decision engine
- autoscaling_monitor.py: Metrics tracking and recommendations

### API Endpoints

1. `GET /api/autoscaling/status` - Get current scaling status
   Returns: current instances, min/max limits, thresholds, recent events

2. `GET /api/autoscaling/history` - Get scaling event history
   Returns: list of scaling decisions with timestamps and reasons

3. `POST /api/metrics/record` - Record system metrics and trigger scaling
   Payload: {cpu, memory, request_rate, error_rate}
   Returns: metrics, scaling action, triggered alerts

### Integration with Docker Compose

The docker-compose.yml includes:
- Nginx load balancer on port 8080
- Two initial app instances (app1, app2)
- Autoscaler service that monitors and makes scaling decisions
- Health checks on all containers

### Scaling Events Logged

Each scaling event includes:
- Timestamp of decision
- Action (scale_up / scale_down / none)
- Reason (specific metric values)
- Instance count before and after
- Duration since last scaling event

---

## 2. ALERTS WHEN CPU/MEMORY EXCEED 75%

### Alert Configuration

#### Modified Thresholds
- CPU Warning: 75% (previously 85%)
- Memory Warning: 75% (previously 80%)
- Duration: 5 minutes before alert triggers

### Default Alert Rules

1. High CPU Usage
   - Metric: cpu_usage
   - Threshold: 75%
   - Duration: 5 minutes
   - Severity: MAJOR

2. High Memory Usage
   - Metric: memory_usage
   - Threshold: 75%
   - Duration: 5 minutes
   - Severity: MAJOR

### Alert Handling

When metrics exceed 75%:
1. System logs the alert with timestamp
2. Alert is categorized as 'warning'
3. Notification channels triggered: Slack, Email, Console
4. Alert can be acknowledged or resolved by operators
5. Auto-scaling is triggered to prevent further increase

### API Endpoints

1. `GET /api/alerts` - Get all active alerts
   Returns: alert list with severity, metric, threshold, actual value

2. `GET /api/alerts/stats` - Get alerting statistics
   Returns: total alerts, alerts by service, alerts by severity

3. `POST /api/alerts/<alert_id>/acknowledge` - Acknowledge an alert
   Returns: updated alert status

4. `POST /api/alerts/<alert_id>/resolve` - Mark alert as resolved
   Returns: resolution timestamp

### Alert Lifecycle

```
New Alert (75% threshold)
  ↓
Logged to Alert Store
  ↓
Notifications Sent
  ↓
Operator Acknowledges
  ↓
Scaling Action Triggered
  ↓
Metrics Return Below Threshold
  ↓
Operator Resolves Alert
```

---

## 3. REVIEW AND OPTIMIZE RESOURCE-INTENSIVE PROCESSES

### Resource Optimization Analysis

The `autoscaling_monitor.py` provides intelligent recommendations based on recent metrics history (last 50 datapoints).

### Analysis Criteria

#### CPU Optimization
- Triggers when: Average CPU > 70%
- Recommendations:
  1. Optimize expensive database queries
  2. Cache frequently accessed data
  3. Review and reduce large data transfers
  4. Batch process expensive operations

#### Memory Optimization
- Triggers when: Average Memory > 70%
- Recommendations:
  1. Implement connection pooling
  2. Reduce in-memory cache size
  3. Implement garbage collection
  4. Review and fix potential memory leaks

#### Error Rate Optimization
- Triggers when: Error Rate > 2%
- Recommendations:
  1. Add retry logic with exponential backoff
  2. Implement circuit breakers
  3. Review and adjust timeout settings
  4. Check health of dependencies

#### Scaling Recommendations
- Triggered when: Current Load > 60% AND Instances < Max
- Recommendation: Scale up to better distribute load

### API Endpoints

1. `GET /api/resource-optimization` - Get optimization recommendations
   Returns: current metrics, list of recommendations with severity

### Optimization Response Structure

```json
{
  "timestamp": "2026-09-20T...",
  "current_metrics": {
    "cpu": 72.5,
    "memory": 68.3,
    "error_rate": 2.1
  },
  "recommendations": [
    {
      "type": "cpu_optimization",
      "severity": "medium",
      "recommendation": "CPU usage is high...",
      "metric": "Current CPU: 72.5%"
    }
  ]
}
```

### Implementation Steps for Optimization

1. Review recommendations from API
2. Identify high-severity items
3. Implement suggested optimizations
4. Monitor metrics for improvement
5. Auto-scaling will handle immediate load
6. Optimizations prevent future issues

---

## 4. LOAD BALANCING ACROSS MULTIPLE INSTANCES

### Load Balancing Architecture

#### Nginx Configuration
- Algorithm: Least Connections (least_conn)
- Load distribution: Even across healthy instances
- Health checks: HTTP health checks on each instance
- Sticky sessions: Not implemented (stateless)

#### Instance Management
- Each instance gets unique ID and port
- Health status tracked: healthy/unhealthy
- Load percentage tracked per instance
- Automatic removal of unhealthy instances

### Load Balancer Features

1. **Least Connections Algorithm**
   - Routes request to instance with fewest active connections
   - Prevents uneven load distribution
   - Better for variable request processing times

2. **Rate Limiting by Endpoint**
   - Different limits for different endpoint types
   - Auth endpoints: Very strict (5 req/min)
   - API endpoints: Moderate (20 req/s)
   - Metrics endpoints: Relaxed (100 req/s)

3. **Health Checks**
   - Interval: 10 seconds
   - Timeout: 5 seconds
   - Consecutive failures to mark unhealthy: 3

### API Endpoints

1. `GET /api/load-balancing/status` - Get LB status
   Returns: algorithm, instances, load distribution

### Load Balancing Response

```json
{
  "algorithm": "least_conn",
  "instances": [
    {
      "id": 1,
      "name": "app1",
      "port": 5001,
      "health": "healthy",
      "load": 45.2
    },
    {
      "id": 2,
      "name": "app2",
      "port": 5002,
      "health": "healthy",
      "load": 52.1
    }
  ],
  "total_load": 97.3,
  "average_load": 48.65,
  "max_load": 52.1,
  "min_load": 45.2
}
```

### How Requests Are Distributed

```
Incoming Request (port 8080)
  ↓
Nginx Load Balancer
  ↓
Check Health Status
  ↓
Apply Least Connections Algorithm
  ↓
Route to Instance with Fewest Connections
  ↓
Forward Request with X-Instance-ID Header
  ↓
Instance Processes Request
  ↓
Response Sent Back Through Load Balancer
```

---

## 5. RATE LIMITING TO PREVENT OVERLOAD

### Rate Limiting Implementation

Two algorithms implemented with configurable per-endpoint settings:

#### Algorithm 1: Token Bucket
- Allows bursts up to capacity
- Smooth out requests over time
- Better for APIs that handle variable load
- Token generation rate: Configurable per endpoint

#### Algorithm 2: Sliding Window
- Strict limit per time window
- No bursts allowed
- Predictable behavior
- Better for APIs with strict SLAs

### Default Rate Limits

```
Login/Signup Endpoints:
  - Algorithm: Sliding Window
  - Rate: 5 requests per 60 seconds
  - Purpose: Prevent brute force attacks

Auth Endpoints (forgot password):
  - Algorithm: Sliding Window
  - Rate: 3 requests per 60 seconds
  - Purpose: Prevent password reset abuse

User Management:
  - Algorithm: Token Bucket
  - Rate: 20 req/s with 30 token capacity
  - Purpose: Reasonable admin access

Metrics APIs:
  - Algorithm: Token Bucket
  - Rate: 100 req/s with 200 token capacity
  - Purpose: Allow monitoring dashboards

General APIs (default):
  - Algorithm: Token Bucket
  - Rate: 100 req/s with 200 token capacity
  - Purpose: Standard API protection
```

### API Endpoints

1. `GET /api/rate-limiting/stats` - Get rate limiting statistics
   Query params: endpoint, identifier
   Returns: current tokens/requests, limits, wait time

2. `PUT /api/rate-limiting/configure` - Configure rate limits (admin only)
   Payload: {endpoint, type, rate, capacity/window}
   Returns: confirmation of new configuration

### Rate Limiting Response

```json
{
  "endpoint": "/api/metrics/",
  "identifier": "192.168.1.100",
  "stats": {
    "type": "token_bucket",
    "tokens": 85.4,
    "capacity": 200,
    "rate": 100
  }
}
```

### Rate Limit Exceeded Response

```json
HTTP 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "retry_after": 2.5,
  "message": "Too many requests. Please retry after 2.5 seconds."
}
```

### How Rate Limiting Works

#### Token Bucket Algorithm
```
1. Start with full bucket (capacity tokens)
2. On request:
   - Calculate new tokens = tokens + (elapsed_time * rate)
   - Cap at capacity
   - If tokens >= 1:
     - Deduct 1 token
     - Allow request
   - Else:
     - Deny request
     - Calculate wait time
```

#### Sliding Window Algorithm
```
1. Maintain deque of request timestamps
2. On request:
   - Remove all requests older than window
   - If count < limit:
     - Add current timestamp
     - Allow request
   - Else:
     - Deny request
     - Calculate wait time
```

---

## API Integration

### Complete Feature Dashboard

Access all features via the overview dashboard:
```
GET /api/overview/dashboard
```

Returns comprehensive data including:
- System health metrics
- Auto-scaling status
- Load balancing distribution
- Resource optimization recommendations
- Active alerts with 75% thresholds
- Rate limiting configuration

### Typical Request Flow with All Features

```
1. Client sends API request
   ↓
2. Rate limiter checks (before_request hook)
   ↓
3. Authentication verified
   ↓
4. Request processed
   ↓
5. Metrics recorded
   ↓
6. Auto-scaler checks thresholds
   - If CPU/Memory > 75%: Trigger warning alert
   - If threshold exceeded: Scale up instances
   ↓
7. Load balancer routes response
   ↓
8. Response returned to client
```

---

## Configuration and Deployment

### Environment Variables

```bash
# Auto-scaling
MIN_INSTANCES=2
MAX_INSTANCES=10
CPU_THRESHOLD_UP=75
CPU_THRESHOLD_DOWN=40
MEMORY_THRESHOLD_UP=75
MEMORY_THRESHOLD_DOWN=40

# Rate Limiting (configured in code)
# See rate_limiter.py LIMITS dictionary
```

### Starting Services

```bash
# With Docker Compose (all features)
docker-compose up -d

# With Python directly (development)
python nexus_app.py

# Scaling up instances (Docker)
docker-compose up -d --scale app=5
```

### Monitoring

Check all features via:
1. Dashboard: `http://localhost:5000/` (or 8080 with load balancer)
2. API docs: `http://localhost:5000/api/docs`
3. Individual endpoints for specific metrics

---

## Performance Considerations

### CPU/Memory Optimization
- Auto-scaling triggered at 75% (early action)
- Scale down only when both CPU AND Memory are low
- Prevents thrashing with conservative thresholds

### Rate Limiting Impact
- Minimal overhead (in-memory tracking)
- Token bucket allows short bursts
- Sliding window for strict enforcement
- Per-client tracking prevents user abuse

### Load Balancing Efficiency
- Least connections optimal for variable load
- Health checks prevent routing to dead instances
- No session affinity needed (stateless design)

---

## Troubleshooting

### Alerts Not Triggering
- Check threshold: Should be 75%, not 90%
- Verify alert rule is enabled
- Check notification channels configuration

### Scaling Not Happening
- Verify min/max instance settings
- Check Docker daemon is running
- Review autoscaler service logs
- Ensure metrics are being recorded

### Rate Limiting Issues
- Check endpoint configuration in LIMITS dict
- Verify identifier (IP address) is correct
- Ensure before_request hook is active
- Check for exceptions in rate limiter code

### Load Balancer Not Working
- Verify nginx.conf syntax
- Check instance health endpoints
- Ensure docker-compose networks are correct
- Verify port mappings (8080 for LB)

---

## Future Enhancements

1. Predictive scaling based on historical patterns
2. Machine learning for optimal threshold determination
3. Custom rate limiting per user/API key
4. Distributed rate limiting across multiple servers
5. Advanced load balancing algorithms (weighted, geographically aware)
6. Real-time metric dashboard for scaling decisions
7. Automatic rollback on scaling failures
8. Integration with cloud providers (AWS auto-scaling groups)

---

## Summary

These five features work together to create a self-healing, auto-scaling infrastructure:

1. **Auto-scaling** prevents outages by adding capacity when needed
2. **Early alerts (75%)** give operators time to respond before crisis
3. **Optimization recommendations** improve long-term performance
4. **Load balancing** distributes requests efficiently
5. **Rate limiting** prevents any single client from overwhelming the system

Together, they ensure the Nexus AIOps platform remains stable, performant, and responsive under varying loads.
