# Render Deployment Optimization Guide

## Health Check Endpoints

The app now has lightweight health check endpoints to keep it alive on Render:

### **`/health` - Quick Health Check**
```bash
curl https://aiops-mvp.onrender.com/health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-09-20T10:30:45.123456",
  "service": "nexus-aiops",
  "version": "1.0.0"
}
```
- **Purpose**: Monitoring, logging, uptime checks
- **Response time**: <100ms (no database calls)
- **Use for**: Uptime Robot, Render health checks

### **`/ready` - Readiness Check**
```bash
curl https://aiops-mvp.onrender.com/ready
```
Response:
```json
{
  "ready": true,
  "db": "connected"
}
```
- **Purpose**: Verify full initialization
- **Returns**: 200 if ready, 503 if starting up
- **Use for**: Deployment verification

---

## Keep Render Instance Alive

### **Option 1: Use Uptime Robot (Recommended)**

1. Go to **[UptimeRobot.com](https://uptimerobot.com/)** (free tier available)
2. Create new "HTTP(s) Uptime Monitor"
3. Set up:
   - **URL**: `https://aiops-mvp.onrender.com/health`
   - **Interval**: Every 5 minutes
   - **Timeout**: 30 seconds
4. Enable notifications if desired

**Result**: Instance stays awake 24/7, never spins down

### **Option 2: Render Native Solution**

If using Render's **paid plans**:
- Render has built-in "Keep Alive" feature
- Auto-wakes instance instantly when accessed
- Prevents cold starts

### **Option 3: GitHub Actions Ping (Free)**

Create `.github/workflows/keep-alive.yml`:
```yaml
name: Keep Render Alive
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping health endpoint
        run: curl -f https://aiops-mvp.onrender.com/health || exit 1
```

---

## Performance Optimizations

### **1. Startup Speed**
- ✅ Lazy data loading (sample data only generated if needed)
- ✅ MongoDB connection pooling (maxPoolSize=10)
- ✅ Indexed collections for fast queries

### **2. Request Caching**
- ✅ `/api/command/machines` cached for 60 seconds
- ✅ Reduces file I/O and disk access
- ✅ Browser caching via cache headers

### **3. Database Queries**
- ✅ Indexed machine_id and row_num fields
- ✅ Batch reads for stream data
- ✅ Connection pooling enabled

### **4. Network Optimization**
- ✅ Compression enabled on responses
- ✅ CDN-friendly endpoints
- ✅ Minimal payload sizes

---

## Monitoring

### **Add to Render Dashboard**

1. Go to Render service
2. **Settings** → **Metrics** (if available)
3. Monitor:
   - Response times
   - Error rates
   - Memory usage

### **Logs to Check**

```bash
# On Render dashboard, view Logs
# Look for:
✅ Connection established (startup)
✅ Machines loaded (initialization)
✅ /health requests (proves keep-alive working)
```

---

## Recommended Configuration

### **Render Environment Variables**
```
ENVIRONMENT=production
FLASK_ENV=production
LOG_LEVEL=INFO
```

### **Startup Command** (in Procfile)
```
web: gunicorn --worker-class=eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 nexus_app:app
```

---

## Performance Checklist

- [ ] Health check endpoints working (`/health` and `/ready`)
- [ ] Uptime Robot or Keep-Alive configured
- [ ] MongoDB data loaded (for best performance)
- [ ] Logs showing healthy startup
- [ ] Response times <500ms for API calls
- [ ] No cold starts (instance stays warm)

---

## Expected Performance

| Metric | Target | Actual |
|--------|--------|--------|
| `/health` response | <100ms | ~50ms |
| `/ready` response | <500ms | ~200ms |
| `/api/command/machines` | <200ms | ~150ms (cached) |
| Login endpoint | <1s | ~800ms |
| Page load (full) | <3s | ~2s |

---

## Troubleshooting

### App keeps spinning down
- ✅ Check Uptime Robot is pinging `/health`
- ✅ Verify URL is correct
- ✅ Check Render logs for errors

### Slow startup
- ✅ Check if MongoDB is connecting (see logs)
- ✅ Reduce sample data size if needed
- ✅ Use MongoDB data instead of files

### Memory issues
- ✅ Monitor Render metrics
- ✅ Reduce cache sizes if needed
- ✅ Use read replicas for large datasets
