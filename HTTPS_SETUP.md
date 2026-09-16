# HTTPS/TLS Setup Guide - Nexus AIOps

## 🚨 CRITICAL SECURITY ISSUE

**Credentials are being sent in plaintext!**

All API authentication endpoints (login, signup, password reset) send credentials in the HTTP request body. Without HTTPS/TLS encryption, these can be intercepted by attackers on the network.

### The Fix
Enable HTTPS/TLS encryption to protect credentials in transit.

---

## Quick Start (Development)

### 1. Generate Self-Signed Certificate

```bash
python generate_ssl_cert.py
```

This creates:
- `cert.pem` - SSL certificate (valid for 365 days)
- `key.pem` - SSL private key

### 2. Update `.env` File

```env
ENVIRONMENT=development
SSL_CERT_PATH=cert.pem
SSL_KEY_PATH=key.pem
```

### 3. Start Server

```bash
python nexus_app.py
```

You'll see:
```
🔒 SSL/TLS Enabled
   Certificate: cert.pem
   Key: key.pem

📍 Access at: https://localhost:5000
```

### 4. Access in Browser

Navigate to: `https://localhost:5000`

⚠️ Browser shows "Not Secure" warning (expected for self-signed certs):
- Click "Advanced"
- Click "Proceed to localhost"

### 5. Test with curl

```bash
# Ignore SSL certificate warning with -k flag
curl -k -X POST https://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

✅ Response: JWT token (credentials were encrypted!)

---

## Production Setup

### Option 1: Reverse Proxy (Recommended)

Use nginx, Caddy, or AWS API Gateway with proper SSL certificates from Let's Encrypt.

**Benefits:**
- Automatic certificate renewal
- Better performance
- Easier certificate management
- Standard production setup

**Example nginx configuration:**

```nginx
# /etc/nginx/sites-available/nexus

server {
    listen 443 ssl http2;
    server_name nexus.example.com;

    # Let's Encrypt certificates
    ssl_certificate /etc/letsencrypt/live/nexus.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nexus.example.com/privkey.pem;

    # Security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Redirect to HTTPS
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Connection upgrade;
        proxy_set_header Upgrade $http_upgrade;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name nexus.example.com;
    return 301 https://$server_name$request_uri;
}
```

**Setup with Let's Encrypt:**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d nexus.example.com

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

**Configure Nexus AIOps (.env):**

```env
ENVIRONMENT=production
# No SSL_CERT_PATH/SSL_KEY_PATH needed - nginx handles HTTPS
```

### Option 2: Direct SSL Configuration

For direct SSL without a reverse proxy:

**Get production certificates:**

```bash
# From Let's Encrypt (using Certbot standalone)
sudo certbot certonly --standalone -d nexus.example.com

# Certificates will be at:
# /etc/letsencrypt/live/nexus.example.com/fullchain.pem
# /etc/letsencrypt/live/nexus.example.com/privkey.pem
```

**Configure Nexus AIOps (.env):**

```env
ENVIRONMENT=production
SSL_CERT_PATH=/etc/letsencrypt/live/nexus.example.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/nexus.example.com/privkey.pem
```

**Start server:**

```bash
python nexus_app.py
```

---

## Verification

### 1. Check HTTPS Connection

```bash
curl -I https://nexus.example.com/api/auth/login
```

Expected headers:
```
HTTP/2 200
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: ...
```

### 2. Test Login Endpoint

```bash
# With proper certificate
curl -X POST https://nexus.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

✅ Should return JWT token

### 3. Monitor HTTPS Traffic

Check server logs:
```bash
tail -f logs/nexus_api.log | grep -i "https\|ssl"
```

### 4. SSL Certificate Check

```bash
# View certificate details
openssl s_client -connect nexus.example.com:443 </dev/null

# Check certificate expiration
echo | openssl s_client -connect nexus.example.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

---

## Common Issues

### Issue 1: Browser Warning for Self-Signed Cert (Development)

**Problem:** "Not Secure" warning when accessing `https://localhost:5000`

**Solution:** This is normal for self-signed certificates in development.
- Click "Advanced"
- Click "Proceed to localhost"
- Certificate is valid, just not from a trusted authority

### Issue 2: Certificate Expiration

**Problem:** "ERR_CERT_DATE_INVALID" error

**Solution:** 
- Development: Regenerate with `python generate_ssl_cert.py`
- Production: Let's Encrypt certificates (auto-renewed by Certbot)

### Issue 3: "Connection Refused" After HTTPS Setup

**Problem:** Server won't start after enabling HTTPS

**Solution:** Check that certificate files exist:
```bash
ls -la cert.pem key.pem
```

If not found, run:
```bash
python generate_ssl_cert.py
```

### Issue 4: "SSL: WRONG_VERSION_NUMBER" Error

**Problem:** Connecting to HTTP endpoint with HTTPS client

**Solution:** Make sure you're using HTTPS:
```bash
# ❌ Wrong
curl http://localhost:5000/api/auth/login

# ✅ Correct
curl -k https://localhost:5000/api/auth/login
```

### Issue 5: Mixed Content Warning

**Problem:** Browser shows mixed content warning

**Solution:** Ensure all resources are loaded over HTTPS:
- Update any `http://` links to `https://`
- App already has Strict-Transport-Security header (forces HTTPS)

---

## Security Checklist

- [ ] HTTPS/TLS enabled (certificate configured)
- [ ] Credentials encrypted in transit
- [ ] `Strict-Transport-Security` header present
- [ ] SSL certificate valid (not expired)
- [ ] Browser shows "Secure" padlock icon
- [ ] Login test successful with HTTPS
- [ ] Logs show "SSL/TLS Enabled"
- [ ] No mixed content warnings
- [ ] Certificate auto-renewal configured (production)

---

## Testing Tools

### 1. Verify HTTPS with curl

```bash
# Test login
curl -k -X POST https://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test signup
curl -k -X POST https://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "username":"testuser",
    "first_name":"Test",
    "last_name":"User",
    "password":"TestPass123!",
    "role":"user",
    "department":"Engineering"
  }'

# Check security headers
curl -I https://localhost:5000
```

### 2. View Certificate Details

```bash
# Display certificate info
openssl x509 -in cert.pem -text -noout

# Check expiration
openssl x509 -in cert.pem -noout -dates
```

### 3. Network Traffic Analysis

```bash
# Monitor HTTPS traffic (macOS/Linux)
tcpdump -A 'tcp port 443'

# Check if passwords are visible in traffic
# (They should NOT be - should be encrypted)
```

---

## Reference

- [Let's Encrypt - Free SSL Certificates](https://letsencrypt.org/)
- [OWASP - Transport Layer Protection](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [SSL/TLS Security Best Practices](https://www.ssl.com/article/ssl-tls-security-best-practices-2023/)
- [HSTS - HTTP Strict Transport Security](https://tools.ietf.org/html/rfc6797)

---

**Last Updated:** 2026-09-16
**Status:** CRITICAL - Encryption Required for Production
