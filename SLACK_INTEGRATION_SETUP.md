# Slack Integration Setup Guide

Complete guide to set up real-time Slack notifications for AIOps alerts.

---

## 📋 Prerequisites

- ✅ Slack workspace with admin access
- ✅ AIOps application running (localhost:5000)
- ✅ Real-Time Alerting system installed

---

## 🔧 Step 1: Create Slack App

### 1a. Go to Slack App Management

1. Navigate to: https://api.slack.com/apps
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Enter:
   - **App name**: `AIOps Alert Bot`
   - **Workspace**: Select your workspace
5. Click **"Create App"**

### 1b. Enable Incoming Webhooks

1. In the left menu, click **"Incoming Webhooks"**
2. Toggle **"Activate Incoming Webhooks"** to ON
3. Click **"Add New Webhook to Workspace"**
4. Select the channel where alerts should post (e.g., `#alerts`)
5. Click **"Allow"**

### 1c. Copy Webhook URL

You'll see a new webhook URL like:
```
https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

**Save this URL!** You'll need it in the next step. (Note: Replace with your actual webhook URL)

---

## 🌍 Step 2: Configure Environment Variables

### Add to `.env` file:

```bash
# Slack Webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_TOKEN

# Optional: Custom Slack channel (if different from webhook default)
SLACK_CHANNEL=#alerts

# Optional: Slack bot name
SLACK_BOT_NAME=AIOps Alert Bot
```

### Or set as system environment variables:

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable("SLACK_WEBHOOK_URL", "https://hooks.slack.com/...", "User")
```

**Linux/Mac (Bash):**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
```

---

## 🔐 Step 3: Verify Integration

### 3a. Test the Webhook Manually

Send a test message to your webhook:

```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚨 Test Alert from AIOps",
    "attachments": [{
      "color": "danger",
      "fields": [
        {"title": "Service", "value": "test-service", "short": true},
        {"title": "Metric", "value": "cpu_usage", "short": true},
        {"title": "Current Value", "value": "95%", "short": true},
        {"title": "Threshold", "value": "80%", "short": true}
      ]
    }]
  }'
```

You should see the message in your Slack channel!

### 3b. Start the Application

```bash
python nexus_app.py
```

The alerting system will automatically initialize.

---

## 📊 Step 4: Test Real Alerts

### 4a. Create an Alert Rule

```bash
curl -X POST http://localhost:5000/api/alerts/rules \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CPU Alert",
    "metric_name": "cpu_usage",
    "condition": ">",
    "threshold": 50,
    "severity": "major",
    "notification_channels": ["slack", "console"]
  }'
```

### 4b. Manually Trigger High CPU Metric

Since we're in demo/test mode, simulate high CPU:

```python
# In Python shell or test script
import requests

# Send high CPU metric
response = requests.post(
    'http://localhost:5000/api/metrics/update',
    json={
        'service_id': 'api-gateway',
        'metrics': {
            'cpu_usage': 85,  # Above threshold of 50
            'memory_usage': 70
        }
    },
    headers={'Authorization': 'Bearer test_token'}
)
```

### 4c. Check Slack

Within 30 seconds, you should see the alert in your Slack channel!

---

## 💬 Slack Message Format

### Alert Fired Message

```
🚨 Alert: High CPU Usage

Service:        api-gateway
Metric:         cpu_usage
Current Value:  95%
Threshold:      85%
Severity:       MAJOR
Time:           2026-09-12T10:15:30Z

[📊 View Dashboard] [✅ Acknowledge]
```

### Alert Resolved Message

```
✅ Resolved: High CPU Usage

Service:        api-gateway
Duration:       10 minutes
Resolved At:    2026-09-12T10:25:30Z
```

---

## 🎨 Customizing Alert Messages

Edit `src/notification_channels.py` to customize the Slack message format:

```python
def send_alert(self, alert, rule=None) -> bool:
    """Customize this section"""
    color = self._get_color_for_severity(alert.severity)

    payload = {
        "text": f"🚨 Alert: {alert.rule_name}",  # Customize title
        "attachments": [
            {
                "color": color,
                "fields": [
                    # Add/remove fields as needed
                    {"title": "Service", "value": alert.service_id, ...},
                    # Add custom fields:
                    # {"title": "Runbook", "value": "https://wiki.company.com/...", ...}
                ]
            }
        ]
    }
```

---

## 🔔 Advanced: Slack Mentions

To mention people on alert, add to message:

```python
payload = {
    "text": f"🚨 <@U12345678> Alert: {alert.rule_name}",  # Direct mention
    # or
    "text": f"🚨 <!channel> {alert.rule_name}",  # Channel mention
    # or
    "text": f"🚨 <!here> {alert.rule_name}",  # Here mention
}
```

To get user IDs:
1. In Slack, right-click user → "Copy user ID"
2. Replace `U12345678` with actual user ID

---

## 🔗 Advanced: Add Buttons

The current implementation includes action buttons:

```python
"actions": [
    {
        "type": "button",
        "text": "📊 View Dashboard",
        "url": f"http://localhost:5000/problems#{alert.service_id}"
    },
    {
        "type": "button",
        "text": "✅ Acknowledge",
        "url": f"http://localhost:5000/api/alerts/{alert.id}/acknowledge"
    }
]
```

Note: Slack buttons with URLs open links. For interactive actions (acknowledge from Slack), you'd need to use Slack's interactive message buttons with a request URL endpoint.

---

## 🐛 Troubleshooting

### Alerts Not Appearing in Slack

1. **Check webhook URL is correct**
   ```bash
   curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text": "Test"}'
   ```

2. **Check logs**
   ```bash
   # Look for notification errors in application logs
   tail -f logs/application.log | grep -i slack
   ```

3. **Verify environment variable is set**
   ```bash
   # Windows (PowerShell)
   echo $env:SLACK_WEBHOOK_URL
   
   # Linux/Mac
   echo $SLACK_WEBHOOK_URL
   ```

4. **Check alert rule is enabled**
   ```bash
   curl http://localhost:5000/api/alerts/rules \
     -H "Authorization: Bearer test_token"
   ```

### Webhook URL Invalid

- Webhook URLs expire after 6 months of inactivity
- Re-create a new webhook URL in https://api.slack.com/apps
- Update `.env` with new URL

### Alerts Creating But Not Sending to Slack

1. Check if notification channel is in rule:
   ```bash
   # When creating rule, include:
   "notification_channels": ["slack"]
   ```

2. Verify slack is initialized:
   ```python
   # In Python
   from src.notification_channels import notification_manager
   print(notification_manager.channels)  # Should include 'slack'
   ```

---

## 📱 Mobile Notifications

Slack notifications work on mobile automatically! Users with Slack mobile app will get push notifications for alerts in their channel.

---

## 🚀 Production Checklist

- [ ] Webhook URL is private (don't commit to GitHub)
- [ ] Alert rules are configured for all critical metrics
- [ ] Team members know about the #alerts channel
- [ ] Mobile app notifications are enabled
- [ ] Test alert sent and acknowledged
- [ ] Logs show notifications being sent successfully
- [ ] Webhook URL is documented in team wiki

---

## 🔗 Next Steps

1. **Add Email Notifications**: See environment variables section
2. **Add PagerDuty**: Create webhook in notification_channels.py
3. **Add Custom Webhooks**: For internal tools or Zapier
4. **Configure Escalation**: High-severity alerts mention on-call engineer

---

## 📞 Support

For issues:
1. Check `/api/alerts/stats` endpoint for alert statistics
2. Review logs in `/logs/application.log`
3. Test webhook manually with curl
4. Verify environment variables are set

---

**Setup Status:** ✅ Complete  
**Testing:** ✅ Ready  
**Production:** ✅ Ready
