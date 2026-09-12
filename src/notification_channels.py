"""
Notification Channels for Alert Delivery
Supports: Slack, Email, Webhook, Console
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Base class for notification channels"""

    @abstractmethod
    def send_alert(self, alert: 'Alert', rule: 'AlertRule') -> bool:
        """Send alert notification"""
        pass

    @abstractmethod
    def send_resolution(self, alert: 'Alert') -> bool:
        """Send resolution notification"""
        pass


class SlackChannel(NotificationChannel):
    """Send alerts to Slack"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack channel.

        Args:
            webhook_url: Slack webhook URL (or env var SLACK_WEBHOOK_URL)
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')

        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")

    def send_alert(self, alert, rule=None) -> bool:
        """Send alert to Slack"""
        if not self.webhook_url:
            return False

        color = self._get_color_for_severity(alert.severity)

        payload = {
            "text": f"🚨 Alert: {alert.rule_name}",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Service",
                            "value": alert.service_id,
                            "short": True
                        },
                        {
                            "title": "Metric",
                            "value": alert.metric_name,
                            "short": True
                        },
                        {
                            "title": "Current Value",
                            "value": f"{alert.current_value:.2f}",
                            "short": True
                        },
                        {
                            "title": "Threshold",
                            "value": f"{alert.threshold:.2f}",
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert.fired_at.isoformat(),
                            "short": True
                        }
                    ],
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
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Slack alert sent for {alert.rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def send_resolution(self, alert) -> bool:
        """Send resolution message to Slack"""
        if not self.webhook_url:
            return False

        duration = int(alert.duration.total_seconds() / 60)  # Convert to minutes

        payload = {
            "text": f"✅ Resolved: {alert.rule_name}",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": "Service",
                            "value": alert.service_id,
                            "short": True
                        },
                        {
                            "title": "Duration",
                            "value": f"{duration} minutes",
                            "short": True
                        },
                        {
                            "title": "Resolved At",
                            "value": alert.resolved_at.isoformat(),
                            "short": False
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Slack resolution sent for {alert.rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack resolution: {e}")
            return False

    @staticmethod
    def _get_color_for_severity(severity) -> str:
        """Get Slack message color for severity"""
        colors = {
            'critical': 'danger',  # Red
            'major': 'warning',    # Orange
            'minor': '#0099ff',    # Blue
            'info': '#666666'      # Gray
        }
        return colors.get(severity.value, '#666666')


class EmailChannel(NotificationChannel):
    """Send alerts via Email"""

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        recipient_emails: Optional[list] = None
    ):
        """
        Initialize Email channel.

        Args:
            smtp_server: SMTP server address (or env var SMTP_SERVER)
            smtp_port: SMTP port (default 587 for TLS)
            sender_email: Sender email address (or env var SMTP_USER)
            sender_password: Sender password (or env var SMTP_PASSWORD)
            recipient_emails: List of recipient emails
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv('SMTP_USER')
        self.sender_password = sender_password or os.getenv('SMTP_PASSWORD')
        self.recipient_emails = recipient_emails or os.getenv('ALERT_EMAILS', '').split(',')

        if not self.sender_email or not self.sender_password:
            logger.warning("Email SMTP credentials not configured")

    def send_alert(self, alert, rule=None) -> bool:
        """Send alert via email"""
        if not self.sender_email or not self.sender_password or not self.recipient_emails:
            return False

        subject = f"🚨 Alert: {alert.rule_name} on {alert.service_id}"

        body = f"""
Alert Details:
==============
Rule: {alert.rule_name}
Service: {alert.service_id}
Metric: {alert.metric_name}

Current Value: {alert.current_value:.2f}
Threshold: {alert.threshold:.2f}
Severity: {alert.severity.value.upper()}

Fired At: {alert.fired_at.isoformat()}

Action Required:
- Review the dashboard: http://localhost:5000/problems#{alert.service_id}
- Acknowledge the alert
- Investigate and resolve the root cause

---
AIOps Alert System
"""

        try:
            self._send_email(subject, body)
            logger.info(f"Email alert sent for {alert.rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def send_resolution(self, alert) -> bool:
        """Send resolution email"""
        if not self.sender_email or not self.sender_password or not self.recipient_emails:
            return False

        duration = int(alert.duration.total_seconds() / 60)

        subject = f"✅ Resolved: {alert.rule_name} on {alert.service_id}"

        body = f"""
Alert Resolved:
===============
Rule: {alert.rule_name}
Service: {alert.service_id}

Duration: {duration} minutes
Fired At: {alert.fired_at.isoformat()}
Resolved At: {alert.resolved_at.isoformat()}

Resolution Reason: {alert.resolution_reason or 'Automatic resolution'}

---
AIOps Alert System
"""

        try:
            self._send_email(subject, body)
            logger.info(f"Email resolution sent for {alert.rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email resolution: {e}")
            return False

    def _send_email(self, subject: str, body: str) -> None:
        """Send email via SMTP"""
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = ', '.join(self.recipient_emails)
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)


class WebhookChannel(NotificationChannel):
    """Send alerts to custom webhook endpoint"""

    def __init__(self, webhook_url: str):
        """
        Initialize Webhook channel.

        Args:
            webhook_url: Webhook URL to POST to
        """
        self.webhook_url = webhook_url

    def send_alert(self, alert, rule=None) -> bool:
        """Send alert to webhook"""
        payload = {
            'event': 'alert_fired',
            'alert': alert.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Webhook alert sent to {self.webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False

    def send_resolution(self, alert) -> bool:
        """Send resolution to webhook"""
        payload = {
            'event': 'alert_resolved',
            'alert': alert.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Webhook resolution sent to {self.webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook resolution: {e}")
            return False


class ConsoleChannel(NotificationChannel):
    """Log alerts to console (for testing/development)"""

    def send_alert(self, alert, rule=None) -> bool:
        """Log alert to console"""
        logger.warning(
            f"🚨 ALERT: {alert.rule_name} on {alert.service_id} "
            f"({alert.metric_name}={alert.current_value:.2f} > {alert.threshold:.2f})"
        )
        return True

    def send_resolution(self, alert) -> bool:
        """Log resolution to console"""
        logger.info(
            f"✅ RESOLVED: {alert.rule_name} on {alert.service_id} "
            f"(Duration: {int(alert.duration.total_seconds() / 60)} minutes)"
        )
        return True


class NotificationManager:
    """Manages multiple notification channels"""

    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {
            'console': ConsoleChannel()
        }

    def register_channel(self, name: str, channel: NotificationChannel) -> None:
        """Register a notification channel"""
        self.channels[name] = channel
        logger.info(f"Registered notification channel: {name}")

    def initialize_from_env(self) -> None:
        """Initialize channels from environment variables"""
        # Slack
        if os.getenv('SLACK_WEBHOOK_URL'):
            self.register_channel('slack', SlackChannel())

        # Email
        if os.getenv('SMTP_USER') and os.getenv('SMTP_PASSWORD'):
            self.register_channel('email', EmailChannel())

        # Custom webhook
        if os.getenv('WEBHOOK_URL'):
            self.register_channel('webhook', WebhookChannel(os.getenv('WEBHOOK_URL')))

    def send_alert(self, alert, channel_name: str, rule=None) -> bool:
        """Send alert through specific channel"""
        channel = self.channels.get(channel_name)
        if not channel:
            logger.warning(f"Unknown channel: {channel_name}")
            return False

        return channel.send_alert(alert, rule)

    def send_resolution(self, alert, channel_name: str) -> bool:
        """Send resolution through specific channel"""
        channel = self.channels.get(channel_name)
        if not channel:
            logger.warning(f"Unknown channel: {channel_name}")
            return False

        return channel.send_resolution(alert)


# Global notification manager
notification_manager = NotificationManager()
notification_manager.initialize_from_env()


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager"""
    return notification_manager
