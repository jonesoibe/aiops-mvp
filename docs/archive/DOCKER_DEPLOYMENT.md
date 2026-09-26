# Docker Deployment Guide for Nexus AIOps with Auto-Scaling

## Overview

This guide explains how to deploy Nexus AIOps with Docker Compose including auto-scaling, load balancing, and all advanced features.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Nginx Load Balancer (port 8080)             │
│    Algorithm: Least Connections                     │
└──────────────┬──────────────┬───────────────────────┘
               │              │
        ┌──────▼──────┐  ┌────▼──────────┐
        │   App1      │  │   App2        │
        │ :5001       │  │ :5002         │
        │ Flask       │  │ Flask         │
        │ Metrics     │  │ Metrics       │
        └─────────────┘  └───────────────┘
               ▲              ▲
               │ Monitors     │
               └──────┬───────┘
                      │
               ┌──────▼──────────────┐
               │ Auto-Scaler Service │
               │ (Docker API)        │
               │ CPU/Memory Monitor  │
               └─────────────────────┘
```

## Files

### docker-compose.yml
- Defines all services (nginx, app1, app2, autoscaler)
- Configures networking (aiops-network)
- Sets environment variables
- Defines health checks
- Sets restart policies

### nginx.conf
- Load balancer configuration
- Rate limiting zones
- Upstream app servers
- Health check endpoint
- Request routing rules

### Dockerfile.autoscaler
- Python environment for auto-scaler
- Installs docker library
- Runs autoscaler.py service

### autoscaler.py
- Monitors Docker container metrics
- Makes scaling decisions
- Logs scaling events
- Provides status information

## Testing the Setup

### Test Load Balancer
```bash
curl http://localhost:8080/api/metrics/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Auto-Scaling
```bash
curl -X POST http://localhost:5000/api/metrics/record \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpu": 85.0,
    "memory": 80.0,
    "request_rate": 150.0,
    "error_rate": 2.5
  }'
```

### Check Scaling Status
```bash
curl http://localhost:5000/api/autoscaling/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Key Features Implemented

1. **Auto-Scaling**: Scales from 2 to 10 instances based on CPU/Memory
2. **Alert Thresholds**: Alerts trigger at 75% (not 90%)
3. **Resource Optimization**: Provides recommendations based on metrics
4. **Load Balancing**: Nginx with least-connections algorithm
5. **Rate Limiting**: Token bucket and sliding window algorithms

See INFRASTRUCTURE_FEATURES.md for detailed documentation.
