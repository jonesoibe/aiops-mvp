# Deploy AIOps to Render.com (FREE TIER)

Render offers **free tier** with 750 hours/month - perfect for this project!

## Prerequisites
- GitHub account
- Render.com account (free)

## Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial AIOps commit"
git remote add origin https://github.com/yourusername/aiops-mvp.git
git push -u origin main
```

## Step 2: Deploy to Render

1. Go to: https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Fill in details:
   - **Name:** aiops-mvp
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements_minimal.txt`
   - **Start command:** `python dashboard_lite.py`
   - **Instance Type:** Free

## Step 3: Set Environment Variables

In Render dashboard:
1. Go to your service
2. Click **"Environment"**
3. Add variables:
   ```
   JWT_SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

## Step 4: Connect Database (Optional)

1. In Render, click **"+ New"** → **"PostgreSQL"**
2. Create free PostgreSQL instance
3. Copy connection string
4. Add to environment:
   ```
   DATABASE_URL=postgresql://...
   ```

## Step 5: Deploy

1. Render auto-deploys on GitHub push
2. Watch build logs in dashboard
3. Once "Live", visit your URL

---

## Access Your App

```
https://aiops-mvp.onrender.com
```

Login:
- Username: `admin`
- Password: `admin123`

---

## Important Notes

### Render Free Tier Limits
- 750 free compute hours/month
- Auto-spins down after 15 mins inactivity
- Takes ~30 seconds to wake up

### To Prevent Spin-Down
Keep it alive with monitoring:
```bash
# Add monitoring tool like UptimeRobot
# Ping endpoint every 5 minutes
# Keeps instance active
```

---

## Cost Breakdown

| Item | Free Tier |
|------|-----------|
| Web Service | 750 hrs/month |
| PostgreSQL | 256 MB storage |
| Bandwidth | Unlimited |
| **Total** | **FREE** |

---

## Upgrade Options

If you outgrow free tier:

| Plan | Cost | Benefits |
|------|------|----------|
| Starter | $7/month | Always on |
| Pro | $12/month | More resources |
| Business | Custom | Advanced features |

---

## Troubleshooting

### "Build Failed"
- Check logs in Render dashboard
- Make sure requirements_minimal.txt is in repo

### "Port 5000 in use"
- Render assigns random port
- Set: `PORT=$PORT` in start command

### App spins down
- Use monitoring service to keep alive
- Or upgrade to paid plan

---

## GitHub Auto-Deploy

Every push triggers automatic deployment:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

Render automatically rebuilds and deploys! ✨

---

**Your AIOps platform is live!** 🎉
