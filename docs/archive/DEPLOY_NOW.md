# 🚀 Deploy to Render - Step by Step

## Current Status
✅ All changes pushed to GitHub (Commit: 0957dfe)
✅ Flask binding fixed (0.0.0.0)
✅ render.yaml configured correctly
✅ Ready to deploy!

---

## ⚡ QUICK DEPLOY (Option 1 - Recommended)

### If you have Auto-Deploy enabled:
1. Wait 1-2 minutes
2. Render will automatically detect the new commit
3. Deployment starts automatically
4. Check status at https://dashboard.render.com

**No action needed!** The platform will handle it.

---

## 🖱️ MANUAL DEPLOY (Option 2 - If auto-deploy is off)

### Step 1: Go to Render Dashboard
Visit: https://dashboard.render.com

### Step 2: Select Your Service
- Click on **aiops-mvp** service
- You should see the service list on the left

### Step 3: Trigger Redeploy
- Look for the **"Redeploy latest commit"** button
- It should be near the top right of the service page
- Click it

### Step 4: Monitor Deployment
- Watch the "Logs" tab for build/deployment progress
- Status will show: Building → Deploying → Live
- Takes about 2-5 minutes

### Step 5: Verify
- Once "Live" appears, click the service URL
- You should see your dashboard
- Try logging in: admin / admin123

---

## 🔧 MANUAL DEPLOY (Option 3 - API Method)

If you want me to trigger it via API, provide your Render API key:

```bash
RENDER_API_KEY=your_key_here
SERVICE_ID=srv_xxxxx
```

Then I can run:
```bash
curl -X POST https://api.render.com/v1/services/{SERVICE_ID}/deploys \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

---

## ✅ What Gets Deployed

**From Commit 0957dfe:**
- ✅ Fixed Flask to bind to 0.0.0.0 (fixes port detection)
- ✅ Uses PORT environment variable from Render
- ✅ Environment-aware debug mode

**From Commit 28d46fc:**
- ✅ System Settings page (/settings)
- ✅ Audit Trail page (/audit-trail)
- ✅ API Documentation page (/api-docs)
- ✅ Outputs & Results page (/outputs)
- ✅ 3 regeneration scripts
- ✅ Complete documentation

---

## 📊 Expected Result After Deployment

### Before (❌ Error):
```
==> No open ports detected on 0.0.0.0
==> Port scan timeout reached
==> Timed Out
```

### After (✅ Success):
```
==> Port scan detected port 5000
==> Service is live!
```

Your dashboard will be available at:
```
https://aiops-mvp-{random}.onrender.com
```

---

## 🆘 Troubleshooting

### Still seeing port errors?
1. Make sure commit 0957dfe is deployed
2. Check render.yaml has correct buildCommand
3. Verify FLASK_ENV=production is set

### Build fails?
1. Check requirements_minimal.txt exists
2. Ensure all dependencies are listed
3. Check Python 3.11 compatibility

### Service is "crashed"?
1. Check Logs tab for error messages
2. Verify PORT environment variable is set
3. Make sure dashboard_lite.py is executable

---

## 📞 Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Your Service Logs:** https://dashboard.render.com/services
- **Render Docs:** https://render.com/docs/web-services

---

## Next Steps

1. **If auto-deploy enabled:** Wait 1-2 minutes and check dashboard
2. **If manual deploy:** Click "Redeploy latest commit" button
3. **Monitor:** Watch the Logs tab
4. **Verify:** Test at your Render URL
5. **Celebrate:** 🎉 You're live!

---

**All done! The hard work is done - now just trigger the deployment!**
