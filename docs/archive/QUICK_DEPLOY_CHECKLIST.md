# 🚀 Quick Render Deployment - 5 Minutes

## Deploy in 5 Steps

### Step 1: Verify GitHub Push ✅
```bash
git log --oneline -1
# Should show: 1135a10 Add: Comprehensive Render deployment guide
```

### Step 2: Go to Render Dashboard
**URL**: https://dashboard.render.com

### Step 3: Select Your Service
1. Click on **aiops-mvp** service
2. Go to **Deployments** tab

### Step 4: Deploy
**Option A (Automatic):**
- If continuous deployment is enabled, push to main automatically triggers
- Watch "Events" tab for deployment progress

**Option B (Manual):**
1. Click **"Manual Deploy"** button
2. Select **"Deploy latest commit"**
3. Status shows: Blue (deploying) → Green (success) → Access your app

### Step 5: Access Your App
**URL**: https://aiops-mvp.onrender.com

**Login:**
- Username: `admin`
- Password: `admin123`

---

## Test Deployment (30 Seconds)

- [ ] Page loads at https://aiops-mvp.onrender.com
- [ ] Login with admin/admin123 works
- [ ] Overview page shows real data
- [ ] Click Remediation → Approvals
- [ ] See pending approvals listed
- [ ] Click Approve button
- [ ] Approval moves to approved section

---

## Optional: Add MongoDB (5 Minutes)

### 1. Get MongoDB Connection String

**If you don't have MongoDB Atlas yet:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster (M0 free tier)
4. Create database user (username/password)
5. Allow network access (0.0.0.0/0)
6. Click "Connect" → "Connect your application"
7. Copy connection string:
   ```
   mongodb+srv://username:password@cluster.xxx.mongodb.net/nexus_aiops
   ```

### 2. Add to Render

1. Go to https://dashboard.render.com
2. Click **aiops-mvp** service
3. Go to **Environment** section
4. Click **"Add Environment Variable"**
5. Enter:
   ```
   Name: MONGODB_URI
   Value: mongodb+srv://username:password@cluster.xxx.mongodb.net/nexus_aiops
   ```
6. Click **Save**
7. Service automatically redeploys (2-5 minutes)

### 3. Verify MongoDB Connected

- Check logs for: `✅ Initialized 5 approval requests in MongoDB`
- Test: Approve an application, restart app, check if it persists

---

## Troubleshooting

### Deployment Stuck/Failed
1. Click on failed deployment
2. Scroll to see error message
3. Common fixes:
   - Wait 5 minutes and retry
   - Check GitHub for syntax errors
   - Verify all code is pushed: `git push origin main`

### App Not Loading
1. Go to Render dashboard
2. Check "Events" tab for errors
3. Check "Logs" for startup errors
4. Common fixes:
   - Wait 3-5 minutes (still loading)
   - Check if service is in free tier sleep mode

### MongoDB Connection Failed
1. Check MONGODB_URI is correct
2. Verify network access in MongoDB Atlas (0.0.0.0/0)
3. Test connection locally first
4. If stuck, use in-memory storage (data lost on restart)

---

## Current Status

**Latest Commit:** `1135a10`  
**Branch:** `main`  
**Status:** Ready for deployment ✅

### What's Deployed
- ✅ Fully functional Approvals page
- ✅ Real incident data (10 incidents)
- ✅ Complete dashboard with all features
- ✅ Live telemetry and logging
- ✅ Authentication system
- ✅ Remediation actions
- ✅ Audit trail

### Optional
- 🔧 MongoDB persistence (if configured)
- 🔧 Custom domain (if upgraded plan)
- 🔧 Advanced scaling (if needed)

---

## Key Links

| Component | URL |
|-----------|-----|
| Render Dashboard | https://dashboard.render.com |
| Live App | https://aiops-mvp.onrender.com |
| GitHub Repo | https://github.com/jonesoibe/aiops-mvp |
| MongoDB Atlas | https://www.mongodb.com/cloud/atlas |
| Render Docs | https://render.com/docs |

## Default Credentials

```
Email: admin@nexus.local
Username: admin
Password: admin123
Role: Admin
```

---

## Timeline

- **0-1 min**: Navigate to Render dashboard
- **1-2 min**: Trigger deployment
- **2-5 min**: Deployment running (watch Events tab)
- **5 min**: App is live! ✅
- **Optional +5 min**: Add MongoDB for persistence

---

## Need Help?

1. **Check [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)** - Full detailed guide
2. **Check [MONGODB_SETUP.md](MONGODB_SETUP.md)** - MongoDB configuration
3. **GitHub Issues** - Report problems
4. **Render Support** - Technical issues with Render

---

**You're all set! Your app is deployed on Render! 🎉**
