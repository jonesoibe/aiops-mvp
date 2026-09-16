# Gmail SMTP Setup Guide for Nexus AIOps

## Overview
The Nexus AIOps platform uses Gmail SMTP to send verification emails, password reset links, and welcome emails. This guide walks through getting Gmail App Passwords configured.

## Prerequisites
- A Gmail account
- Access to your Google Account security settings

## Step-by-Step Setup

### 1. Enable 2-Step Verification (if not already enabled)
1. Go to https://myaccount.google.com/security
2. Look for "2-Step Verification" in the left sidebar
3. Click it and follow Google's instructions to enable it
4. You'll need to verify your phone number

### 2. Generate a Gmail App Password
1. After 2-Step Verification is enabled, go back to https://myaccount.google.com/security
2. Scroll down to find **"App passwords"** (it only appears after 2-Step Verification is on)
3. Click "App passwords"
4. Select:
   - **App:** Mail
   - **Device:** Windows Computer (or your device type)
5. Google will generate a **16-character password** (like: `abcd efgh ijkl mnop`)
6. Copy the entire password (including the spaces)

### 3. Update .env File
1. Open `.env` file in your project root
2. Replace `your-email@gmail.com` with your actual Gmail address
3. Replace `your-16-character-app-password` with the password from Step 2
4. Optionally update `FROM_EMAIL` to your company domain or Gmail address

Example:
```
SMTP_USERNAME=john.smith@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=notifications@example.com
```

### 4. Restart the Application
1. Stop the current Nexus AIOps server (Ctrl+C)
2. Start it again with: `python nexus_app.py`
3. The app will automatically load the `.env` file

### 5. Test Email Sending
1. Go to http://localhost:5000/signup
2. Create a new account with your email address
3. Check your inbox for the verification email
4. The email should arrive within seconds

## Verification Email Flow
When a user signs up:
1. They enter their email during signup
2. A 6-digit verification code is generated
3. An email is sent with the code
4. User enters the code on the verification page
5. Account is activated

## Password Reset Flow
When a user requests a password reset:
1. They enter their email on /forgot-password
2. A reset link with a token is sent to their email
3. User clicks the link and sets a new password

## Troubleshooting

### "SMTP authentication failed"
- Check that `SMTP_USERNAME` is your full Gmail address
- Check that `SMTP_PASSWORD` is the 16-character **App Password** (not your regular password)
- Verify you enabled 2-Step Verification before generating the app password

### "Failed to send email"
- Check that your Gmail account isn't blocking "Less secure apps"
- Verify the SMTP server and port settings:
  - Server: `smtp.gmail.com`
  - Port: `587`

### Emails not arriving
- Check spam/junk folder
- Verify the email address is correct in the form
- Check the server logs for errors

### "App passwords" option not visible
- You must enable 2-Step Verification first
- It can take a few minutes to appear after enabling 2-Step

## Environment Variables Reference

```
# Gmail SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com          # Gmail's SMTP server (don't change)
SMTP_PORT=587                       # Gmail's SMTP port (don't change)

# Gmail Account Credentials
SMTP_USERNAME=your-email@gmail.com  # Your Gmail email address
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Your 16-character App Password

# Email Sender Configuration
FROM_EMAIL=noreply@nexusaiops.com   # Email shown in "From" field to recipients

# Application Settings
ENVIRONMENT=development              # production or development
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR
```

## Security Best Practices

⚠️ **Important:**
- Never commit `.env` to git (it's in `.gitignore`)
- Never share your App Password
- Use Gmail App Passwords only for applications, not the account password
- Use a dedicated Gmail account for application emails if possible
- Monitor the "Connected apps & sites" section in your Google Account

## Alternative Email Providers

If you don't want to use Gmail, you can configure other SMTP providers:

### SendGrid
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxx
```

### AWS SES
```
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-username
SMTP_PASSWORD=your-ses-password
```

### Office 365 / Outlook
```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-password
```

## Next Steps
1. ✅ Complete the setup above
2. ✅ Restart the application
3. ✅ Test by creating an account at /signup
4. ✅ Verify emails are being sent successfully

For issues, check:
- Application logs: `logs/nexus_aiops.log`
- Error logs: `logs/nexus_aiops_errors.log`
- Email service logs: `logs/nexus_aiops_api.log`
