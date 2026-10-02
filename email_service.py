"""
Email Service for Nexus AIOps
Sends verification codes, password resets, invites and welcome emails.

Delivery provider is chosen by which credentials are present, in this order:
  1. BREVO_API_KEY   - Brevo HTTPS API (works on Render's free tier)
  2. RESEND_API_KEY  - Resend HTTPS API (works on Render's free tier)
  3. SMTP_USERNAME (or SMTP_USER) + SMTP_PASSWORD - plain SMTP

Render's free web services block outbound SMTP ports 25/465/587, so SMTP only
works locally or on a paid instance; use one of the HTTPS APIs there.
"""

import html
import os
import smtplib
from typing import Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import requests

# Seconds. Without a timeout, a blocked/filtered port can hang the request
# thread (and therefore the signup page) for minutes.
SEND_TIMEOUT = 15

class EmailService:
    """Service for sending emails via an HTTPS API or SMTP."""

    def __init__(self):
        """Initialize email service from environment configuration."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        # src/notification_channels.py (alert emails) reads SMTP_USER while this
        # module historically read SMTP_USERNAME; accept either so one set of
        # credentials works for both.
        self.sender_email = os.getenv('SMTP_USERNAME') or os.getenv('SMTP_USER', '')
        self.sender_password = os.getenv('SMTP_PASSWORD', '')
        self.brevo_api_key = os.getenv('BREVO_API_KEY', '')
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@nexusaiops.com')
        self.from_name = 'Nexus AIOps'
        # Public base URL used in emailed links (reset/invite). Taken from config,
        # never the request Host header, which an attacker can forge to poison
        # password-reset links. APP_BASE_URL wins (needed for a custom domain);
        # otherwise use RENDER_EXTERNAL_URL, which Render sets itself on every web
        # service, so deployed links never silently fall back to localhost.
        self.base_url = (
            os.getenv('APP_BASE_URL')
            or os.getenv('RENDER_EXTERNAL_URL')
            or 'http://localhost:5000'
        ).rstrip('/')

        if self.brevo_api_key:
            self.provider = 'brevo'
        elif self.resend_api_key:
            self.provider = 'resend'
        elif self.sender_email and self.sender_password:
            self.provider = 'smtp'
        else:
            self.provider = None
        self.enabled = self.provider is not None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send an email via the configured provider.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback body

        Returns:
            Tuple of (success, message). success is False when nothing was sent,
            including when no provider is configured -- callers must not tell
            users an email went out in that case.
        """
        if not self.enabled:
            print("[*] Email service not configured: set BREVO_API_KEY, RESEND_API_KEY, "
                  "or SMTP_USERNAME/SMTP_PASSWORD. Email was NOT sent.")
            return False, "Email service not configured"

        if self.provider == 'brevo':
            return self._send_via_brevo(to_email, subject, html_body, text_body)
        if self.provider == 'resend':
            return self._send_via_resend(to_email, subject, html_body, text_body)
        return self._send_via_smtp(to_email, subject, html_body, text_body)

    def _send_via_brevo(self, to_email, subject, html_body, text_body) -> Tuple[bool, str]:
        payload = {
            'sender': {'name': self.from_name, 'email': self.from_email},
            'to': [{'email': to_email}],
            'subject': subject,
            'htmlContent': html_body,
        }
        if text_body:
            payload['textContent'] = text_body
        try:
            resp = requests.post(
                'https://api.brevo.com/v3/smtp/email',
                headers={'api-key': self.brevo_api_key, 'accept': 'application/json'},
                json=payload,
                timeout=SEND_TIMEOUT,
            )
        except requests.RequestException as e:
            return False, f"Brevo request failed: {e}"
        if resp.status_code in (200, 201, 202):
            return True, f"Email sent to {to_email}"
        return False, f"Brevo API error {resp.status_code}: {resp.text[:200]}"

    def _send_via_resend(self, to_email, subject, html_body, text_body) -> Tuple[bool, str]:
        payload = {
            'from': f"{self.from_name} <{self.from_email}>",
            'to': [to_email],
            'subject': subject,
            'html': html_body,
        }
        if text_body:
            payload['text'] = text_body
        try:
            resp = requests.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {self.resend_api_key}'},
                json=payload,
                timeout=SEND_TIMEOUT,
            )
        except requests.RequestException as e:
            return False, f"Resend request failed: {e}"
        if resp.status_code in (200, 201):
            return True, f"Email sent to {to_email}"
        return False, f"Resend API error {resp.status_code}: {resp.text[:200]}"

    def _send_via_smtp(self, to_email, subject, html_body, text_body) -> Tuple[bool, str]:
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email

            if text_body:
                message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=SEND_TIMEOUT) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            return True, f"Email sent to {to_email}"

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed. Check email credentials."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"

    def send_verification_email(self, to_email: str, code: str) -> Tuple[bool, str]:
        """
        Send email verification code.

        Args:
            to_email: Recipient email
            code: 6-digit verification code

        Returns:
            Tuple of (success, message)
        """
        subject = "Verify Your Email - Nexus AIOps"

        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Welcome to Nexus AIOps!</h2>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Thank you for signing up. Please verify your email address using the code below:
                    </p>

                    <div style="background: #f0f0f0; padding: 20px; border-radius: 6px; margin: 30px 0; text-align: center;">
                        <p style="margin: 0; color: #999; font-size: 14px; margin-bottom: 10px;">Verification Code</p>
                        <h1 style="margin: 0; color: #2d5aa0; font-size: 48px; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                            {code}
                        </h1>
                    </div>

                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        This code will expire in <strong>15 minutes</strong>. Do not share this code with anyone.
                    </p>

                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                        If you didn't create this account, please ignore this email.
                    </p>

                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                    <p style="color: #999; font-size: 12px;">
                        Nexus AIOps | Enterprise Observability Platform<br>
                        © {datetime.now().year} All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """

        text_body = f"""
Verify Your Email - Nexus AIOps

Thank you for signing up. Please use this code to verify your email:

{code}

This code will expire in 15 minutes.

If you didn't create this account, please ignore this email.

Nexus AIOps | Enterprise Observability Platform
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_password_reset_email(self, to_email: str, reset_token: str, username: str) -> Tuple[bool, str]:
        """
        Send password reset email.

        Args:
            to_email: Recipient email
            reset_token: Password reset token
            username: Username

        Returns:
            Tuple of (success, message)
        """
        subject = "Reset Your Password - Nexus AIOps"

        reset_link = f"{self.base_url}/reset-password?token={reset_token}"

        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Password Reset Request</h2>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Hi {username},
                    </p>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        We received a request to reset your password. Click the button below to set a new password:
                    </p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="display: inline-block; background: #2d5aa0; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>

                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Or copy this link: <br>
                        <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; word-break: break-all;">
                            {reset_link}
                        </code>
                    </p>

                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                        This link will expire in <strong>1 hour</strong>.
                    </p>

                    <p style="color: #999; font-size: 14px; line-height: 1.6;">
                        If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                    </p>

                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                    <p style="color: #999; font-size: 12px;">
                        Nexus AIOps | Enterprise Observability Platform<br>
                        © {datetime.now().year} All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """

        text_body = f"""
Password Reset Request - Nexus AIOps

Hi {username},

We received a request to reset your password. Visit this link to set a new password:

{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.

Nexus AIOps | Enterprise Observability Platform
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_welcome_email(self, to_email: str, username: str, first_name: str) -> Tuple[bool, str]:
        """
        Send comprehensive welcome/onboarding email after successful registration.

        Args:
            to_email: Recipient email
            username: Username
            first_name: First name

        Returns:
            Tuple of (success, message)
        """
        subject = "Welcome to Nexus AIOps - Get Started with Your Enterprise Observability Platform"

        html_body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; margin: 0;">
                <div style="max-width: 700px; margin: 0 auto;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; border-radius: 8px 8px 0 0; text-align: center;">
                        <h1 style="margin: 0 0 10px 0; font-size: 28px;">Welcome to Nexus AIOps, {first_name}!</h1>
                        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Your Enterprise Autonomous Observability Platform</p>
                    </div>

                    <!-- Main Content -->
                    <div style="background: white; padding: 40px 30px; color: #333;">
                        <p style="font-size: 16px; line-height: 1.6; color: #555; margin: 0 0 20px 0;">
                            Hey {first_name},
                        </p>

                        <p style="font-size: 16px; line-height: 1.6; color: #555;">
                            Your account has been successfully created! We're excited to have you on board. Nexus AIOps is an enterprise-grade autonomous observability platform designed to help you monitor, analyze, and automatically remediate infrastructure issues.
                        </p>

                        <!-- Login Info Box -->
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 6px; margin: 30px 0;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Your Login Details</p>
                            <p style="margin: 0; font-size: 16px; font-weight: bold;">Username: <span style="font-family: monospace; background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px;">{username}</span></p>
                            <p style="margin: 10px 0 0 0; font-size: 13px; opacity: 0.9;">Use your password to log in</p>
                        </div>

                        <!-- Quick Navigation Guide -->
                        <h3 style="color: #667eea; font-size: 18px; margin: 30px 0 15px 0;">Navigate Your Dashboard</h3>

                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin-bottom: 15px;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">📊 Dashboard</strong>
                            <p style="margin: 0; font-size: 14px; color: #666;">Your central hub showing system health, key metrics, and active incidents at a glance.</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #f5576c; margin-bottom: 15px;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">🚨 Incidents & Problems</strong>
                            <p style="margin: 0; font-size: 14px; color: #666;">Track and manage incidents with AI-powered root cause analysis and automated remediation suggestions.</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #4facfe; margin-bottom: 15px;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">🔗 Service Topology</strong>
                            <p style="margin: 0; font-size: 14px; color: #666;">Visualize your service architecture with interactive mapping showing dependencies and traffic flow.</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #43e97b; margin-bottom: 15px;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">⚙️ Configuration & Alerts</strong>
                            <p style="margin: 0; font-size: 14px; color: #666;">Set up alert rules, notifications, SLOs, and customize the platform to match your needs.</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #fa709a; margin-bottom: 20px;">
                            <strong style="color: #333; display: block; margin-bottom: 5px;">👤 Your Profile</strong>
                            <p style="margin: 0; font-size: 14px; color: #666;">Manage your account settings, preferences, and notification channels.</p>
                        </div>

                        <!-- Getting Started Steps -->
                        <h3 style="color: #667eea; font-size: 18px; margin: 30px 0 15px 0;">Getting Started in 5 Steps</h3>

                        <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                            <li><strong>Log In:</strong> Visit the login page and enter your username and password</li>
                            <li><strong>Explore Dashboard:</strong> Review your infrastructure health and active incidents</li>
                            <li><strong>Check Topology:</strong> Understand your service dependencies and connections</li>
                            <li><strong>Configure Alerts:</strong> Set up notification channels and alert rules for critical issues</li>
                            <li><strong>Define SLOs:</strong> Create Service Level Objectives to track your reliability targets</li>
                        </ol>

                        <!-- Key Features -->
                        <h3 style="color: #667eea; font-size: 18px; margin: 30px 0 15px 0;">Platform Highlights</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                            <li><strong>AI-Powered Analysis:</strong> Intelligent root cause analysis for faster problem resolution</li>
                            <li><strong>Automated Remediation:</strong> Automatic incident resolution with approval workflows</li>
                            <li><strong>Real-Time Monitoring:</strong> Live streaming metrics and instant alerts</li>
                            <li><strong>Service Visualization:</strong> Interactive topology mapping of your infrastructure</li>
                            <li><strong>SLO Tracking:</strong> Monitor and manage Service Level Objectives with compliance reporting</li>
                            <li><strong>Enterprise Security:</strong> HTTPS/TLS encryption and role-based access control</li>
                        </ul>

                        <!-- Security Notice -->
                        <div style="background: #e8f4f8; border-left: 4px solid #2196F3; padding: 15px; margin: 30px 0;">
                            <p style="margin: 0; font-size: 13px; color: #1565c0;">
                                <strong>Security:</strong> All your data is encrypted in transit with HTTPS/TLS. Your password is never stored in plain text and is hashed with bcrypt.
                            </p>
                        </div>

                        <!-- Support Info -->
                        <p style="font-size: 14px; line-height: 1.6; color: #666; margin-top: 30px;">
                            <strong>Need Help?</strong> If you have any questions or need assistance getting started, refer to the platform documentation or contact our support team.
                        </p>

                        <p style="font-size: 14px; line-height: 1.6; color: #666;">
                            Happy monitoring!<br>
                            <strong>Favour from Nexus AIOps</strong><br>
                            <em style="color: #888;">Your Operational Buddy</em>
                        </p>
                    </div>

                    <!-- Footer -->
                    <div style="background: #f8f9fa; padding: 20px 30px; border-radius: 0 0 8px 8px; text-align: center; border-top: 1px solid #e0e0e0;">
                        <p style="margin: 0 0 10px 0; color: #999; font-size: 12px;">
                            Nexus AIOps | Enterprise Autonomous Observability Platform<br>
                            © {datetime.now().year} All Rights Reserved
                        </p>
                        <p style="margin: 0; color: #999; font-size: 11px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

        text_body = f"""
WELCOME TO NEXUS AIOPS!
Enterprise Autonomous Observability Platform

Hey {first_name},

Great to have you on board! Your account has been successfully created. I'm Favour, your operational buddy, and I'm here to help you get the most out of Nexus AIOps.

LOGIN DETAILS:
Username: {username}
Use your password to log in

NAVIGATE YOUR DASHBOARD:

1. Dashboard - Your central hub with system health, metrics, and active incidents
2. Incidents - Track issues with AI-powered analysis and automated remediation suggestions
3. Topology - Interactive visualization of your entire service architecture
4. Configuration - Set up alerts, notifications, SLOs, and customize your experience
5. Profile - Manage your account settings and preferences

GETTING STARTED IN 5 STEPS:

Step 1: Log in with your credentials
Step 2: Explore the Dashboard to see your infrastructure health
Step 3: Check the Service Topology to understand your services
Step 4: Configure Alerts to get notified of important issues
Step 5: Define SLOs to track your reliability goals

KEY FEATURES:

✓ AI-Powered Analysis - Intelligent root cause identification
✓ Automated Remediation - Automatic issue resolution with workflows
✓ Real-Time Monitoring - Live metrics and instant alerts
✓ Service Topology - Interactive mapping of your infrastructure
✓ SLO Tracking - Monitor and track Service Level Objectives
✓ Enterprise Security - HTTPS/TLS encryption for all data

SECURITY:
All your data is encrypted in transit with HTTPS/TLS encryption. Your password is securely hashed using bcrypt and never stored in plain text.

NEED HELP?
The platform includes comprehensive guides. Don't hesitate to explore and ask questions.

Let's make your operations smooth and efficient!

Best regards,
Favour from Nexus AIOps
Your Operational Buddy

Enterprise Autonomous Observability Platform
© {datetime.now().year} All Rights Reserved
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_invite_email(self, to_email: str, username: str, first_name: str, invite_token: str) -> Tuple[bool, str]:
        """
        Send the account-setup invitation an admin triggers from user management.

        Args:
            to_email: Recipient email
            username: Username assigned to the invited user
            first_name: First name
            invite_token: Single-use setup token (valid 48 hours)

        Returns:
            Tuple of (success, message)
        """
        subject = "You're invited to Nexus AIOps - Set Up Your Account"
        setup_link = f"{self.base_url}/setup-account?token={invite_token}"
        safe_name = html.escape(first_name or username)
        safe_username = html.escape(username)

        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">You've been invited to Nexus AIOps</h2>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">Hi {safe_name},</p>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        An administrator created an account for you (username: <strong>{safe_username}</strong>).
                        Click the button below to choose your password and finish setting it up:
                    </p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{setup_link}" style="display: inline-block; background: #2d5aa0; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Set Up Account
                        </a>
                    </div>

                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Or copy this link: <br>
                        <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; word-break: break-all;">{setup_link}</code>
                    </p>

                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                        This link will expire in <strong>48 hours</strong>.
                    </p>

                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                    <p style="color: #999; font-size: 12px;">
                        Nexus AIOps | Enterprise Observability Platform<br>
                        &copy; {datetime.now().year} All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """

        text_body = f"""
You've been invited to Nexus AIOps

Hi {first_name or username},

An administrator created an account for you (username: {username}).
Open this link to choose your password and finish setting it up:

{setup_link}

This link will expire in 48 hours.

Nexus AIOps | Enterprise Observability Platform
        """

        return self.send_email(to_email, subject, html_body, text_body)


# Create global instance
email_service = EmailService()
