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
        Send welcome email after successful registration.

        Args:
            to_email: Recipient email
            username: Username
            first_name: First name

        Returns:
            Tuple of (success, message)
        """
        subject = "Welcome to Nexus AIOps!"

        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Welcome, {first_name}!</h2>

                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Your account has been successfully created. You can now log in to Nexus AIOps and start monitoring your infrastructure.
                    </p>

                    <div style="background: #f0f0f0; padding: 20px; border-radius: 6px; margin: 30px 0;">
                        <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">Your login credentials:</p>
                        <p style="margin: 0; color: #333; font-weight: bold;">Username: {username}</p>
                    </div>

                    <h3 style="color: #333; margin-top: 30px; margin-bottom: 15px;">Getting Started</h3>

                    <ul style="color: #666; font-size: 14px; line-height: 1.8;">
                        <li>Log in to the platform with your credentials</li>
                        <li>Complete your profile information</li>
                        <li>Connect your infrastructure and services</li>
                        <li>Set up alerts and notifications</li>
                        <li>Start monitoring and analyzing your systems</li>
                    </ul>

                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                        If you have any questions or need assistance, please contact our support team.
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
Welcome to Nexus AIOps!

Hi {first_name},

Your account has been successfully created. You can now log in to Nexus AIOps.

Username: {username}

Getting Started:
- Log in to the platform
- Complete your profile
- Connect your infrastructure
- Set up alerts
- Start monitoring

For support, contact our team.

Nexus AIOps | Enterprise Observability Platform
        """

        return self.send_email(to_email, subject, html_body, text_body)


# Create global instance
email_service = EmailService()
