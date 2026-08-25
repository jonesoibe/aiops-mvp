# Render Deployment Guide - Nexus AIOps Platform

Complete step-by-step guide to deploy the latest version on Render.

## Prerequisites

✅ GitHub account with your repository pushed  
✅ Render account (free tier available)  
✅ (Optional) MongoDB Atlas account for persistent data

---

## Step 1: Verify Code is Pushed to GitHub

### Check Latest Commit

```bash
# View latest commits
git log --oneline -5

# Verify remote is up to date
git status

# Should see: "On branch main, nothing to commit"
```

### Expected Latest Commit
```
a7dfe09 Refactor: Clean up duplicate approval endpoints and add MongoDB setup guide
9515a0f Fix: Complete Approvals page with functional approve/reject
40ffd3e Fix: Authentication and MongoDB integration - Enable real data loading
```

If your local changes aren't pushed:
```bash
git add -A
git commit -m "Your commit message"
git push origin main
```

---

## Step 2: Access Render Dashboard

1. Go to **https://dashboard.render.com**
2. Log in with your Render account
3. Select your **aiops-mvp** service

---

## Step 3: Trigger Deployment (3 Options)

### Option A: Automatic Deployment (Recommended)
If you have continuous deployment enabled:
- Any push to `main` branch automatically triggers deployment
- Check "Deployments" tab to see status
- Estimated time: 2-5 minutes

### Option B: Manual Deploy
1. Go to your service dashboard
2. Click **"Manual Deploy"** button
3. Select **"Deploy latest commit"**
4. Wait for deployment to complete (2-5 minutes)

### Option C: Trigger via CLI
```bash
# Using curl to trigger deployment (requires API key)
curl -X POST https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys \
  -H "authorization: Bearer YOUR_API_KEY" \
  -H "content-type: application/json"
```

---

## Step 4: Monitor Deployment

### In Render Dashboard:

1. **Go to "Events" tab** - See deployment progress
2. **Logs appear in real-time**:
   - Yellow/Blue = Deploying
   - Green checkmark = Success ✅
   - Red X = Failed ❌

### Expected Startup Logs:
```
======================================================================
  🚀 NEXUS AIOPS - Enterprise Autonomous Observability Platform
======================================================================
✅ Initialized 5 approval requests in memory
📡 Telemetry emitted to room 'telemetry'
📍 Access at: http://localhost:5000
```

### Deployment Status
- Click "Deployments" tab
- See all previous deployments
- Current deployment shows at top

---

## Step 5: Configure Environment Variables (Optional but Recommended)

### For MongoDB Persistence

#### 5A: Set Up MongoDB Atlas (if not already done)
1. Go to **https://www.mongodb.com/cloud/atlas**
2. Create Free Tier cluster
3. Add database user
4. Allow network access (0.0.0.0/0)
5. Get connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/nexus_aiops?retryWrites=true&w=majority
   ```

#### 5B: Add to Render

1. In Render dashboard, go to **Settings** → **Environment**
2. Click **"Add Environment Variable"**
3. Add variable:
   ```
   Name: MONGODB_URI
   Value: mongodb+srv://username:password@cluster.mongodb.net/nexus_aiops?retryWrites=true&w=majority
   ```
4. Click **"Save Changes"**
5. Service automatically redeploys with new environment variable

### Other Optional Variables
```
# JWT Secret Key (default is dev-secret-key)
JWT_SECRET_KEY=your-secure-random-key-here

# Port (default: 5000)
PORT=5000
```

---

## Step 6: Test the Deployment

### Access Your Live Application

1. **Main URL**: https://aiops-mvp.onrender.com
2. **Login Page**: Redirect to /login
3. **Default Credentials**:
   - Username: `admin`
   - Password: `admin123`

### Test Each Section

#### Approvals Page
1. Navigate to **Left Sidebar → Remediation → Approvals**
2. Should see 2 pending approvals
3. Click "✓ Approve" - moves to approved list
4. Switch to "✓ Approved" tab - see approved requests
5. Click "✕ Reject" - moves to rejected list

#### Dashboard
1. **Overview** - Real incidents and statistics
2. **Problems** - All 10 incidents listed
3. **Live Operations** - Action buttons
4. **Infrastructure** - System metrics
5. **Settings** - Configuration options

#### Real-Time Features
1. Check **Logs** tab - Live log streaming
2. **Telemetry** - Real-time metrics
3. **Traces** - Distributed tracing

---

## Step 7: Verify Data Persistence

### Without MongoDB (In-Memory, Session-Only)
- ✅ Approvals work during session
- ⚠️ Data lost on app restart
- Perfect for demo/testing

### With MongoDB (Full Persistence)
1. Approve an application
2. Wait for deployment logs to confirm MongoDB connection
3. Restart the application
4. Check if approved status persists
5. ✅ Data survives restarts

To verify MongoDB is connected, check logs for:
```
✅ Retrieved X approvals from MongoDB
```

---

## Step 8: Troubleshooting

### Deployment Failed

**Check logs for errors:**
1. Go to "Events" tab
2. Click on failed deployment
3. See error message
4. Common issues:
   - Missing dependencies → Add to `requirements.txt`
   - Syntax errors → Check code in GitHub
   - Port conflicts → Render assigns port automatically

### Application Not Responding

**Check service status:**
1. Go to service settings
2. Click "Logs" → View recent logs
3. Look for startup errors
4. Verify `PORT` environment variable matches

### MongoDB Connection Failed

**If logs show MongoDB error:**
```
⚠️ MongoDB connection failed
Using in-memory storage as fallback
```

**Solution:**
1. Check `MONGODB_URI` environment variable is set correctly
2. Verify MongoDB Atlas network access allows Render's IP
3. Check username/password in connection string
4. Test connection locally first

### Approvals Not Persisting

**If approvals reset after restart:**
- MongoDB not connected
- Check logs for connection error
- Verify MONGODB_URI environment variable
- Or use in-memory storage (data lost on restart)

---

## Step 9: Deployment Checklist

Use this checklist to verify everything is working:

- [ ] Code pushed to GitHub (`main` branch)
- [ ] Render deployment started
- [ ] Deployment shows green checkmark (Success)
- [ ] Application accessible at https://aiops-mvp.onrender.com
- [ ] Login works (admin/admin123)
- [ ] Overview page loads with real data
- [ ] Problems page shows 10 incidents
- [ ] Approvals page shows pending items
- [ ] Approve button moves items to approved
- [ ] Reject button moves items to rejected
- [ ] (Optional) MongoDB connected and persisting data

---

## Step 10: Post-Deployment

### Monitor Application

1. **Set up alerts** (if available in Render plan)
2. **Check logs regularly** for errors
3. **Monitor performance** if plan supports it

### Keep Application Updated

```bash
# Make changes locally
git add -A
git commit -m "Update description"
git push origin main

# Render automatically deploys if continuous deployment enabled
# Or manually trigger deployment in Render dashboard
```

### Common Post-Deployment Tasks

**Update approval data:**
- Edit `nexus_app.py` → `initialize_approvals()` function
- Add more sample data
- Push to GitHub → Auto-deploy

**Change demo credentials:**
- Edit `initialize_users()` in `nexus_app.py`
- Modify default passwords
- Push to GitHub → Auto-deploy

**Connect real MongoDB Atlas:**
- Create MongoDB Atlas cluster
- Get connection string
- Add `MONGODB_URI` environment variable in Render
- Service redeploys automatically

---

## Quick Reference

### URLs
- **App**: https://aiops-mvp.onrender.com
- **GitHub**: https://github.com/jonesoibe/aiops-mvp
- **Render Dashboard**: https://dashboard.render.com
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas

### Default Credentials
- **Username**: admin
- **Password**: admin123

### Key Files
- **Main App**: `nexus_app.py` (1000+ lines)
- **Approvals Page**: `templates/nexus/approvals.html`
- **Design Tokens**: `static/design-tokens.css`
- **MongoDB Setup**: `MONGODB_SETUP.md`

### Support
- **Issues**: GitHub Issues tab
- **Render Support**: https://render.com/docs
- **MongoDB**: https://docs.mongodb.com

---

## Advanced Configuration

### Custom Domain (Paid Plan Required)
1. Go to Service Settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records per Render instructions

### SSL/TLS Certificate
- Automatically provided by Render
- No additional configuration needed
- HTTPS enabled by default

### Environment-Specific Config
```
# Production (Render)
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Development (Local)
FLASK_ENV=development
FLASK_DEBUG=1
```

### Scaling
- Free tier: 0.5 CPU, 512 MB RAM
- For high traffic: Upgrade to paid plan
- Auto-scaling available on higher tiers

---

## Success! 🎉

Your Nexus AIOps platform is now deployed on Render!

### Next Steps:
1. ✅ Share the link: https://aiops-mvp.onrender.com
2. ✅ Test with demo credentials
3. ✅ (Optional) Connect MongoDB for persistence
4. ✅ Monitor application in Render dashboard
5. ✅ Make updates and push to GitHub

**Questions?** Check logs in Render dashboard or review this guide!
