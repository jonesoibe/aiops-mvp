# JWT Secret Key Generation for Render

## Quick Generation Commands

### Method 1: OpenSSL (Mac/Linux Recommended)

```bash
# Generate 32-byte random key
openssl rand -base64 32
```

**Output example:**
```
aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbCdEfGh==
```

---

### Method 2: Python (All Platforms)

```bash
# Windows, Mac, or Linux
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Output example:**
```
-Xk_7mN9pQrStUvWxYzA1B2C3d4E5f6G7h8I9j0K1l2m
```

---

### Method 3: PowerShell (Windows)

```powershell
# Generate 32-character random string
-join ((0..31) | ForEach-Object { [char][int](33..126 | Get-Random) })
```

**Output example:**
```
!@#$%^&*()_+-=[]{}|;:',.<>?/~`
```

---

### Method 4: Online Generator

Go to: **https://www.random.org/passwords/generate**
- Length: 32
- Character set: All available
- Generate and copy

---

### Method 5: Linux `dd` and `base64`

```bash
# Generate 24 random bytes and encode to base64
dd if=/dev/urandom bs=24 count=1 2>/dev/null | base64
```

**Output example:**
```
kL9mN0oPqRsTuVwXyZ1a2B3c4D5e6F7g==
```

---

## Best Practices

### Requirements
- ✅ **Length:** 32 characters minimum (preferably 32-64)
- ✅ **Randomness:** Cryptographically secure
- ✅ **Characters:** Mix of letters, numbers, special characters
- ✅ **Uniqueness:** Different for each environment

### Recommended Approach

```bash
# Generate multiple options and pick the best one
python -c "
import secrets
for i in range(3):
    key = secrets.token_urlsafe(32)
    print(f'Option {i+1}: {key}')
"
```

**Output:**
```
Option 1: aB-c_dEfGhIjKlMnOpQrStUvWxYz1234567890==
Option 2: xY9z_AbCdEfGhIjKlMnOpQrStUv1234567890==
Option 3: qR8s_TuVwXyZ1a2B3c4D5e6F7g8h9i0j1k==
```

---

## Generate and Store for Render

### Step 1: Generate Key

**Windows PowerShell:**
```powershell
# Generate and copy to clipboard (Windows)
$key = -join ((0..31) | ForEach-Object { [char][int](65..90 + 97..122 + 48..57 | Get-Random) })
$key | Set-Clipboard
Write-Host "Key copied to clipboard: $key"
```

**Mac/Linux:**
```bash
# Generate and display
KEY=$(openssl rand -base64 32)
echo "JWT_SECRET_KEY=$KEY"
```

### Step 2: Copy Key

```
Example key generated:
JWT_SECRET_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbCdEfGh==
```

### Step 3: Add to Render Dashboard

1. Go to **https://dashboard.render.com**
2. Click on your **aiops-mvp** service
3. Go to **Environment** tab
4. Click **"Add Environment Variable"**
5. Enter:
   ```
   Name: JWT_SECRET_KEY
   Value: aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbCdEfGh==
   ```
6. Click **Save**
7. Service automatically redeploys

---

## Verify Secret Key

### Check it's Set in Render

1. Go to Service → Environment
2. You should see `JWT_SECRET_KEY` listed
3. Value should show as `••••••••` (masked)

### Test Token Generation

```bash
# Start app on Render or local with the new key
# Then generate a token:

curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return token successfully
```

---

## Production Security Checklist

- [ ] Generated key using cryptographic method
- [ ] Key is 32+ characters
- [ ] Key contains uppercase, lowercase, numbers, special chars
- [ ] Key is NOT hardcoded in repository
- [ ] Key is ONLY in Render environment variables
- [ ] Different key for production vs development
- [ ] Key is backed up securely
- [ ] Key has not been shared or committed to Git

---

## Multiple Environment Keys

### Development (Local)
```
JWT_SECRET_KEY=dev-secret-key-change-in-production
```
(Keep in code, not in production)

### Staging (Render)
```
# Generate unique key
openssl rand -base64 32

# Add to staging service environment
```

### Production (Render)
```
# Generate unique key (DIFFERENT from staging)
openssl rand -base64 32

# Add to production service environment
```

---

## Rotate Secret Key (For Security)

### Situation: Compromise Suspected

**Step 1: Generate New Key**
```bash
openssl rand -base64 32
```

**Step 2: Update in Render**
1. Go to Service → Environment
2. Edit `JWT_SECRET_KEY` with new value
3. Save (service redeploys)

**Step 3: Invalidate Old Tokens**
- All existing tokens become invalid
- Users must login again
- New tokens use new secret

**Step 4: Communicate Change** (If applicable)
- Email users about re-authentication requirement
- Update documentation

---

## Store Secret Key Safely

### DO ✅
- ✅ Keep in Render environment variables
- ✅ Keep in `.env` file (local development only)
- ✅ Keep in password manager
- ✅ Keep in secure vault (production)
- ✅ Document rotation policy

### DON'T ❌
- ❌ Don't commit to Git
- ❌ Don't share via email
- ❌ Don't hardcode in code
- ❌ Don't post in chat/Slack
- ❌ Don't use simple/predictable keys

---

## Common Mistakes & Fixes

### Mistake 1: Using Same Key Everywhere
**Problem:** If one environment compromised, all are compromised  
**Fix:** Generate unique key for each environment

```bash
# Development
openssl rand -base64 32 > dev.key

# Staging
openssl rand -base64 32 > staging.key

# Production
openssl rand -base64 32 > prod.key
```

### Mistake 2: Key Too Short
**Problem:** Easier to brute force  
**Fix:** Use minimum 32 characters

```bash
# Wrong: 16 characters
openssl rand -base64 16

# Correct: 32 characters
openssl rand -base64 32
```

### Mistake 3: Key in Git Repository
**Problem:** Visible in commit history  
**Fix:** Add to `.gitignore` and `.env`

```bash
# .gitignore
*.key
.env
.env.local

# .env (local development only)
JWT_SECRET_KEY=your-dev-key-here
```

### Mistake 4: Forgetting to Deploy
**Problem:** Changed key locally but not in Render  
**Fix:** Always update Render environment when changing key

---

## Verify It Works

### Test Local

```bash
# Set environment variable
export JWT_SECRET_KEY="your-generated-key-here"

# Start app
python nexus_app.py

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should get valid token
```

### Test on Render

1. Deploy with new key in environment
2. Go to https://aiops-mvp.onrender.com
3. Login with admin/admin123
4. Should work without errors
5. Check logs for any JWT errors

---

## Command Reference

| Task | Command |
|------|---------|
| **Generate (OpenSSL)** | `openssl rand -base64 32` |
| **Generate (Python)** | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| **Generate (PowerShell)** | `-join ((0..31) \| ForEach-Object { [char][int](33..126 \| Get-Random) })` |
| **Generate Strong** | `openssl rand -hex 32` |
| **Generate Multiple** | `for i in {1..3}; do openssl rand -base64 32; done` |
| **Copy to Clipboard (Mac)** | `openssl rand -base64 32 \| pbcopy` |
| **Copy to Clipboard (Linux)** | `openssl rand -base64 32 \| xclip -selection clipboard` |
| **Save to File** | `openssl rand -base64 32 > secret.key` |

---

## Final Checklist

Before deploying to Render:

- [ ] JWT secret key generated (32+ characters)
- [ ] Key copied to clipboard or file
- [ ] Render environment variable set: `JWT_SECRET_KEY`
- [ ] Service redeployed after setting variable
- [ ] Login tested and working
- [ ] Tokens generate successfully
- [ ] No errors in logs related to JWT
- [ ] Key NOT in Git repository
- [ ] Backup of key stored safely
- [ ] Documentation updated if needed

---

## Quick Copy-Paste Setup

```bash
# 1. Generate key
KEY=$(openssl rand -base64 32)
echo "JWT_SECRET_KEY=$KEY"

# 2. Copy output manually to Render dashboard:
#    Environment → Add Variable
#    Name: JWT_SECRET_KEY
#    Value: [paste the generated key]

# 3. Test it works (after Render redeploys):
curl -X POST https://aiops-mvp.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## Troubleshooting

### Error: "Invalid token signature"
**Problem:** App using different secret key than what generated token  
**Fix:** Ensure `JWT_SECRET_KEY` environment variable is correct in Render

```bash
# Check Render logs
# Look for: JWT secret key loaded from environment
```

### Error: "Token not verified"
**Problem:** Secret key changed, old tokens invalid  
**Fix:** This is expected - users need to login again

### Error: "SECRET_KEY is None"
**Problem:** Environment variable not set  
**Fix:** Add `JWT_SECRET_KEY` to Render environment variables

---

**You're ready to secure Nexus AIOps! 🔐**
