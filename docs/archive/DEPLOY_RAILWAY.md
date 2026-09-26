# Deploy AIOps to Railway.app (FREE TIER)

Railway.app offers **$5/month free credit** - enough to run this project for free!

## Prerequisites
- GitHub account (to fork the repo)
- Railway account (free at railway.app)

## Step 1: Fork Repository to GitHub

1. Go to: https://github.com/new/import
2. Repository URL: `https://github.com/yourusername/aiops-mvp`
3. Click "Begin Import"
4. Create your own fork

## Step 2: Deploy to Railway

1. Go to: https://railway.app
2. Login with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your forked repository
6. Railway auto-detects it's a Python app
7. Click **"Deploy"**

## Step 3: Configure Environment

In Railway dashboard:
1. Go to your project
2. Click **"Variables"**
3. Add these variables:
   ```
   JWT_SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   PORT=5000
   ```

## Step 4: Add Custom Domain (Optional)

1. In Railway, go to **"Settings"**
2. Add a custom domain (or use Railway's free subdomain)
3. Example: `aiops-mvp.up.railway.app`

## Step 5: Monitor Deployment

1. Go to **"Deployments"** tab
2. Watch build and deployment logs
3. Once green, your app is live!

## Access Your App

```
https://your-app.up.railway.app
```

Login with:
- Username: `admin`
- Password: `admin123`

---

## Database (MongoDB)

### Option 1: Use Railway's MongoDB Plugin
1. In Railway project, click **"Add Service"**
2. Select **"MongoDB"**
3. Railway auto-connects it
4. Set environment variable: `MONGODB_URI` will be auto-filled

### Option 2: Use MongoDB Atlas (Free)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create free cluster
4. Get connection string
5. In Railway Variables, set:
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/aiops_mvp
   ```

---

## Troubleshooting

### Build Failed
- Check logs in Railway dashboard
- Make sure all files are committed to GitHub
- Verify `requirements_minimal.txt` exists

### App Crashes
- Check Railway logs for errors
- Verify environment variables are set
- Check if port is set to 5000

### Deployment Takes Long
- First deployment can take 5-10 minutes
- Building ML dependencies is time-consuming
- Be patient!

---

## Cost Estimate

| Item | Cost |
|------|------|
| Railway free tier | $5/month |
| Monthly usage | ~$2-3 |
| **Total** | **FREE** |

---

## Production Tips

1. **Change JWT Secret**
   ```
   JWT_SECRET_KEY=use-a-strong-random-string
   ```

2. **Enable HTTPS**
   - Railway provides free HTTPS automatically

3. **Set up monitoring**
   - Railway includes monitoring in dashboard
   - Check logs regularly

4. **Scale if needed**
   - Railway scales automatically
   - Upgrade plan if hitting limits

---

## Next Steps

After deployment, you can:
1. Access from anywhere
2. Share link with team
3. Integrate with other services
4. Add monitoring/alerts
5. Connect real data sources

---

**Deployed!** Your AIOps platform is now live on the internet! 🚀
