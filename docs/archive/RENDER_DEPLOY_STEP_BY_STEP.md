# Deploy AIOps MVP to Render.com - Step-by-Step Guide

**Time Required:** 10-15 minutes  
**Cost:** 100% FREE (with free tier)

---

## ✅ Prerequisites

- GitHub account (to store your code)
- Render.com account (free at render.com)
- Your AIOps MVP project files

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Prepare Your GitHub Repository**

**1a. Create GitHub Repository**

1. Go to: https://github.com/new
2. Repository name: `aiops-mvp`
3. Description: `Autonomous AIOps Platform with ML anomaly detection`
4. Visibility: **Public** (important for Render)
5. Click **"Create repository"**

**1b. Push Your Code to GitHub**

```bash
cd /path/to/aiops-mvp

# Initialize git if not already done
git init

# Add all files
git add .

# Create commit
git commit -m "Initial AIOps MVP deployment ready for Render"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/aiops-mvp.git

# Rename to main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note:** Make sure your repository is **PUBLIC** for Render to access it.

---

### **STEP 2: Create Render Account**

1. Go to: https://render.com
2. Click **"Sign Up"**
3. Choose **"Sign up with GitHub"** (easiest method)
4. Authorize Render to access your GitHub
5. Complete signup

---

### **STEP 3: Create Web Service on Render**

1. In Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Search for: `aiops-mvp`
5. Click **"Connect"** next to your repository

---

### **STEP 4: Configure Service Settings**

Fill in the following fields:

**Name:**
```
aiops-mvp
```

**Environment:**
```
Python 3
```

**Region:**
```
Choose closest to you (e.g., Ohio, Singapore, etc.)
```

**Branch:**
```
main
```

**Build Command:**
```
pip install -r requirements_render.txt
```

**Start Command:**
```
gunicorn -w 4 -b 0.0.0.0:$PORT dashboard_lite:app
```

**Instance Type:**
```
Free (0.5 CPU, 512MB RAM)
```

---

### **STEP 5: Add Environment Variables**

In the Render dashboard:

1. Scroll down to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `JWT_SECRET_KEY` | (See next step) |
| `PYTHONUNBUFFERED` | `1` |
| `PORT` | `5000` |

**For JWT_SECRET_KEY:**
- Generate secure key:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Copy the output
- Paste into JWT_SECRET_KEY value field

---

### **STEP 6: Deploy**

1. Click **"Create Web Service"**
2. Render will start building (takes 3-5 minutes)
3. Watch the build logs
4. Once status shows **"Live"** (green), you're deployed!

---

### **STEP 7: Access Your App**

**Your app is now live!**

1. Render gives you a URL like: `https://aiops-mvp.onrender.com`
2. Click the URL in Render dashboard
3. You should see the **AIOps login page**

**Login with:**
```
Username: admin
Password: admin123
```

---

## 🎯 What to Expect

### **First Deploy:**
- Build time: 3-5 minutes (downloading dependencies)
- Takes time to compile scikit-learn
- Be patient!

### **After First Deploy:**
- App will spin down after 15 minutes of inactivity
- Takes ~30 seconds to wake up when accessed
- Free tier limitation (keeps costs down)

### **Subsequent Deploys:**
- Faster (cached dependencies)
- Only 1-2 minutes

---

## ⚙️ Deployment Verification

### **Check if Deployment Succeeded:**

1. **Green "Live" Status**
   - In Render dashboard
   - Service status should show "Live" in green

2. **Access the App**
   - Click the URL provided
   - Should load login page instantly

3. **Login Works**
   - Username: `admin`
   - Password: `admin123`
   - Should redirect to home page

4. **Dashboard Functions**
   - Go to Problems page
   - Click "Run Simulation" button (if available)
   - Should see incidents loading

---

## 🔧 If Deployment Fails

### **Build Failed - Check Logs**

1. In Render dashboard
2. Click **"Logs"** tab
3. Look for error messages
4. Common issues:

**Error: "requirements.txt not found"**
- Solution: Make sure `requirements_render.txt` is in your GitHub repo
- Push again: `git add . && git commit -m "fix" && git push`

**Error: "Module not found"**
- Solution: Check all imports in `dashboard_lite.py`
- Make sure dependencies are in `requirements_render.txt`

**Error: "Port already in use"**
- Solution: Use `gunicorn` instead of `python dashboard_lite.py`
- Build command should include gunicorn

### **App Keeps Spinning Down**

This is normal on free tier! It means:
- App is inactive (no requests for 15 minutes)
- Automatically starts when you access it again
- No data is lost
- Just takes 20-30 seconds to wake up

**To prevent spin-down (optional):**
- Use UptimeRobot (free)
- Ping your app every 5 minutes
- See section below

---

## 📊 Keep App Always Active (Optional)

### **Use UptimeRobot**

1. Go to: https://uptimerobot.com
2. Sign up (free)
3. Click **"Add Monitor"**
4. Fill in:
   - **Monitoring Type:** HTTP(s)
   - **URL:** `https://aiops-mvp.onrender.com/api/simulation/status`
   - **Interval:** 5 minutes
5. Click **"Create Monitor"**

**Result:**
- App pings every 5 minutes
- Never goes to sleep
- Stays "warm" and responsive

---

## 🎯 Next Steps After Deployment

### **1. Test All Features**
```
✓ Login page works
✓ Home page loads
✓ Problems dashboard accessible
✓ Infrastructure page loads
✓ View Details button works
✓ Acknowledge/Resolve buttons work
```

### **2. Share with Team**
```
Send them:
- Your app URL (e.g., https://aiops-mvp.onrender.com)
- Login credentials (admin/admin123)
- Link to documentation (DASHBOARDS_GUIDE.md)
```

### **3. Monitor Deployment**
```
✓ Check Render dashboard regularly
✓ Review logs for errors
✓ Monitor performance
✓ Set up alerts if needed
```

### **4. Upgrade if Needed**
If you need:
- Always-on hosting → Upgrade to paid plan ($7/month)
- More resources → Choose higher tier
- Database → Add PostgreSQL or MongoDB

---

## 📈 Render Pricing

| Plan | Cost | Features |
|------|------|----------|
| Free | $0 | 0.5 CPU, 512MB RAM, spins down |
| Starter | $7/mo | Always on, 0.5 CPU, 512MB RAM |
| Standard | $12/mo | More resources |
| Pro | $19/mo | Even more resources |

**For this app:** Free tier is perfect to start!

---

## 🔐 Security Best Practices

Before going public:

- [ ] Change `JWT_SECRET_KEY` (done above)
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS (Render does this automatically)
- [ ] Don't commit `.env` file
- [ ] Keep `requirements.txt` updated
- [ ] Monitor logs for errors

---

## 📞 Troubleshooting

### **App deployed but gives error**

1. Check Render logs:
   - Dashboard → Logs tab
   - Look for red error messages

2. Common fixes:
   ```bash
   # Update code in GitHub
   git add .
   git commit -m "Fix error"
   git push
   
   # Render auto-redeploys
   # Check again in 2-3 minutes
   ```

### **App keeps timing out**

- Free tier spin-down is normal
- Use UptimeRobot to keep it warm
- Or upgrade to paid plan

### **Login doesn't work**

- Check credentials: `admin / admin123`
- Clear browser cache
- Try incognito window
- Check Render logs for errors

---

## ✅ Success Checklist

- [ ] GitHub repository created and code pushed
- [ ] Render account created
- [ ] Web Service connected to GitHub repo
- [ ] Build command set to: `pip install -r requirements_render.txt`
- [ ] Start command set to: `gunicorn -w 4 -b 0.0.0.0:$PORT dashboard_lite:app`
- [ ] Environment variables added (FLASK_ENV, JWT_SECRET_KEY, PYTHONUNBUFFERED)
- [ ] Deployment successful (status shows "Live")
- [ ] App accessible at provided URL
- [ ] Login works with admin/admin123
- [ ] All dashboards load correctly

---

## 🎉 You're Done!

Your AIOps platform is now **LIVE ON THE INTERNET!**

**Your app URL:**
```
https://aiops-mvp.onrender.com
```

**Share with team:**
```
URL: https://aiops-mvp.onrender.com
Username: admin
Password: admin123

Docs: See DASHBOARDS_GUIDE.md for how to use
API: See API.md for API reference
```

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Your App Dashboard](https://dashboard.render.com)
- [DASHBOARDS_GUIDE.md](DASHBOARDS_GUIDE.md) - How to use your app
- [API.md](API.md) - API reference
- [SECURITY.md](SECURITY.md) - Security best practices

---

**Deployment completed! Your AIOps platform is now accessible worldwide!** 🌍✨
