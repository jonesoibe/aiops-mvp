# Real-Time Alerting System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Application
```bash
python nexus_app.py
```

You should see:
```
======================================================================
  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform
======================================================================
✅ NEXUS AIOPS initialized successfully
📍 Access at: http://localhost:5000
   Demo: admin / admin123

✅ Initialized 5 default alert rules
🔄 Starting alert evaluation thread
```

### Step 2: Open the Alerts Dashboard
Navigate to: **http://localhost:5000/alerts**

Login with:
- **Username:** admin
- **Password:** admin123

### Step 3: View Default Alert Rules
The dashboard shows 5 pre-configured rules:
1. **High CPU Usage** - triggers when CPU > 85% for 5 minutes
2. **High Memory Usage** - triggers when Memory > 80% for 5 minutes
3. **High Error Rate** - triggers when Error Rate > 5% for 2 minutes
4. **High Response Latency** - triggers when P95 > 500ms for 3 minutes
5. **High Disk Usage** - triggers when Disk Usage > 85% for 5 minutes

### Step 4: Create Your First Alert Rule (Optional)

**Via Dashboard:**
1. Click "Rules" tab
2. Click "Create Rule" button
3. Fill in:
   - **Name:** e.g., "Database Connections High"
   - **Metric:** `database_connections`
   - **Condition:** `>`
   - **Threshold:** `500`
   - **Duration:** `300` seconds
   - **Severity:** Major
4. Click "Save Rule"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Database Connections High",
    "description": "Alert when DB connections exceed 500",
    "metric_name": "database_connections",
    "condition": ">",
    "threshold": 500.0,
    "severity": "major",
    "notification_channels": ["slack", "console"]
  }'
```

### Step 5: View Active Alerts
```bash
# Get all firing alerts
curl -X GET "http://localhost:5000/api/alerts?status=firing" \
  -H "Authorization: Bearer test_token"

# Get alerts by severity
curl -X GET "http://localhost:5000/api/alerts?severity=critical" \
  -H "Authorization: Bearer test_token"

# Get alerts for specific service
curl -X GET "http://localhost:5000/api/alerts/service/api-gateway" \
  -H "Authorization: Bearer test_token"
```

### Step 6: Acknowledge and Resolve Alerts

**Acknowledge an alert:**
```bash
curl -X POST http://localhost:5000/api/alerts/{alert_id}/acknowledge \
  -H "Authorization: Bearer test_token"
```

**Resolve an alert:**
```bash
curl -X POST http://localhost:5000/api/alerts/{alert_id}/resolve \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Scaled service horizontally"}'
```

### Step 7: Enable Slack Notifications (Optional)

**Create a Slack App:**
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Select "From scratch"
4. Enter app name (e.g., "AIOps Alert Bot")
5. Select your workspace
6. Click "Create App"

**Enable Webhooks:**
1. In left menu, click "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to ON
3. Click "Add New Webhook to Workspace"
4. Select your alert channel (e.g., #alerts)
5. Click "Allow"
6. Copy the webhook URL

**Configure Application:**
1. Add to `.env` file or set environment variable:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_TEAM/YOUR_BOT/YOUR_TOKEN
```

2. Restart the application:
```bash
python nexus_app.py
```

3. Create an alert rule with `slack` in notification channels:
```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Slack Alert",
    "description": "Alert to test Slack integration",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 50.0,
    "notification_channels": ["slack", "console"]
  }'
```

---

## 📊 Dashboard Features

### Active Alerts Tab
- View all firing alerts
- Filter by status, severity, or service
- Acknowledge or resolve individual alerts
- See alert duration and current metric values

### Rules Tab
- View all alert rules
- Create new rules with visual editor
- Edit existing rules
- Delete rules
- See rule status (enabled/disabled)

### History Tab
- View resolved alerts timeline
- See resolution reasons and duration
- Analyze alert patterns

### Statistics Cards
- **Critical Alerts:** Number of critical severity alerts
- **Major Alerts:** Number of major severity alerts
- **Active Alerts:** Total currently firing alerts
- **Total Rules:** Number of configured alert rules

---

## 🔄 Real-Time Updates

The dashboard automatically:
- Refreshes every minute
- Updates in real-time via WebSocket
- Shows new alerts instantly
- Updates alert status immediately

---

## 📊 API Quick Reference

### Get Statistics
```bash
curl http://localhost:5000/api/alerts/stats \
  -H "Authorization: Bearer test_token" | jq
```

### Get Alert Templates
```bash
curl http://localhost:5000/api/alerts/templates \
  -H "Authorization: Bearer test_token" | jq
```

### Get Alert Details
```bash
curl http://localhost:5000/api/alerts/{alert_id} \
  -H "Authorization: Bearer test_token" | jq
```

### Silence an Alert (30 minutes)
```bash
curl -X POST http://localhost:5000/api/alerts/{alert_id}/silence \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 30}'
```

---

## 🧪 Testing the System

### Test Alert Evaluation
The system evaluates metrics every 30 seconds. To test:

1. Create a rule with low threshold (e.g., CPU > 10%)
2. Wait up to 30 seconds
3. The alert should fire when metrics exceed threshold
4. You should see it on the dashboard
5. If Slack is configured, you should get a notification

### Run Unit Tests
```bash
python -m pytest tests/test_alerting_engine.py -v
```

All 26 tests should pass ✅

---

## 🔑 Key Concepts

### Alert Rule
Defines **when** to trigger an alert:
- Metric name (e.g., `cpu_usage`, `error_rate`)
- Condition operator (>, <, >=, <=, ==, !=, range)
- Threshold value
- Duration (must persist for this long)
- Severity level (CRITICAL, MAJOR, MINOR, INFO)

### Alert
The **actual alert instance** that fires when a rule condition is met:
- Status: FIRING, ACKNOWLEDGED, RESOLVED, SILENCED
- Timestamp when it fired
- Current metric value
- Who acknowledged it (if applicable)
- Resolution reason (if applicable)

### Notification Channel
How alerts are delivered:
- **Slack** - Messages to Slack channels
- **Email** - Sent to configured email addresses
- **Webhooks** - Custom HTTP POST endpoints
- **Console** - Logged to application logs

---

## ❌ Troubleshooting

**Dashboard not loading?**
- Verify you're logged in (admin/admin123)
- Check browser console for JavaScript errors
- Ensure Flask application is running on port 5000

**Alerts not triggering?**
- Check if rule is enabled in Rules tab
- Verify threshold is reasonable for your metrics
- Wait up to 30 seconds for evaluation cycle
- Check application logs for evaluation errors

**Slack notifications not working?**
- Verify webhook URL is set in `.env`
- Restart the application after setting `SLACK_WEBHOOK_URL`
- Test webhook URL with: `curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' -d '{"text":"test"}'`
- Ensure rule has `slack` in notification channels

**Can't connect WebSocket?**
- Check if you're using HTTPS (WebSocket requires secure connection in production)
- Verify Flask-SocketIO is initialized
- Check browser console for connection errors
- Try refreshing the page

---

## 📚 Learn More

- See `docs/archive/ALERTING_INTEGRATION_COMPLETE.md` for full feature documentation
- See `SLACK_INTEGRATION_SETUP.md` for detailed Slack setup
- See `ALERT_API_ENDPOINTS.md` for complete API reference
- See `REAL_TIME_ALERTING_IMPLEMENTATION.md` for implementation details

---

## ✅ What's Next?

1. **Set up Slack integration** for production alerts
2. **Configure email notifications** for escalation
3. **Create custom alert rules** for your services
4. **Set up escalation policies** for critical alerts
5. **Monitor alert evaluation logs** for issues
6. **Train your team** on dashboard usage

---

**Happy alerting! 🚀**
