"""
Email Service for Nexus AIOps
Handles SMTP email sending for verification codes, password resets, etc.
"""

import os
import smtplib
from typing import Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SMTP_USERNAME', '')
        self.sender_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@nexusaiops.com')
        self.from_name = 'Nexus AIOps'
        self.enabled = bool(self.sender_email and self.sender_password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback body

        Returns:
            Tuple of (success, message)
        """
        if not self.enabled:
            print(f"⚠️ Email service not configured. Email would be sent to: {to_email}")
            return True, "Email service not configured (development mode)"

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email

            # Attach text and HTML parts
            if text_body:
                message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
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

        reset_link = f"http://localhost:5000/reset-password?token={reset_token}"

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


# Create global instance
email_service = EmailService()
