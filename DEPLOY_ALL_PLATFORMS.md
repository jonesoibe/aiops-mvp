# Complete Deployment Guide - All Platforms

Deploy your AIOps platform **for FREE** on multiple cloud providers.

---

## 🚀 Quick Comparison

| Platform | Cost | Setup Time | Pros | Cons |
|----------|------|-----------|------|------|
| **Railway** | $5/mo free | 5 min | Simple, reliable | Limited free tier |
| **Render** | FREE | 5 min | Full free tier | Spins down after inactivity |
| **Fly.io** | FREE | 10 min | Distributed, fast | Learning curve |
| **AWS Free Tier** | FREE | 15 min | Most powerful | Complex setup |
| **Google Cloud** | FREE | 15 min | Good free quota | Requires card |
| **Heroku** | PAID (was free) | 5 min | Easiest | No longer free |
| **Docker locally** | FREE | 2 min | Full control | Only local access |

---

## 📋 Recommended Path

### For Beginners
→ **Start with Railway or Render** (easiest, free)

### For Scale
→ **Use AWS or Google Cloud** (more power, free tier)

### For Speed
→ **Use Fly.io** (distributed, fast)

---

## 🐳 Option 1: Docker (Local/Any Platform)

### Prerequisites
- Docker installed on your machine

### Deploy Locally with Docker

```bash
# Build image
docker build -t aiops-mvp .

# Run container
docker run -p 5000:5000 aiops-mvp

# Or with docker-compose
docker-compose up
```

Access: http://localhost:5000

### Deploy to Docker Hub & Cloud

```bash
# Build and push
docker build -t yourusername/aiops-mvp .
docker push yourusername/aiops-mvp

# Deploy anywhere Docker runs
docker run yourusername/aiops-mvp
```

---

## 🚂 Option 2: Railway.app (Recommended)

**EASIEST for beginners**

See: [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)

```bash
# 1. Fork to GitHub
# 2. Go to railway.app
# 3. Connect GitHub repo
# 4. Done!
```

---

## 🎨 Option 3: Render.com

**COMPLETELY FREE**

See: [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

```bash
# 1. Push to GitHub
# 2. Go to render.com
# 3. Select Web Service
# 4. Connect repo
# 5. Set env variables
# 6. Deploy!
```

---

## ✈️ Option 4: Fly.io

### Setup

```bash
# Install flyctl
curl https://fly.io/install.sh | sh

# Login
flyctl auth login

# Create app
flyctl launch --dockerignore=.dockerignore

# Deploy
flyctl deploy
```

Access your app:
```bash
flyctl open
```

**Benefits:**
- Global deployment
- Excellent performance
- Free tier available
- Automatic HTTPS

---

## ☁️ Option 5: AWS Free Tier

### Setup with App Runner

1. Go to: https://aws.amazon.com/apprunner/
2. Click "Create service"
3. Connect GitHub repo
4. Select `dashboard_lite.py` as start command
5. Deploy!

**Free for 1 year:**
- 1 vCPU core
- 1 GB memory
- 100 GB data transfer

---

## 🌐 Option 6: Google Cloud Run

### Setup

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

gcloud auth login

# Build and deploy
gcloud run deploy aiops-mvp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Free:**
- 2 million requests/month
- 360,000 GB-seconds/month

---

## 💾 Option 7: Self-Hosted (VPS)

### On DigitalOcean ($4/mo), Linode, etc.

```bash
# SSH to server
ssh root@your-vps-ip

# Clone repo
git clone https://github.com/yourusername/aiops-mvp.git
cd aiops-mvp

# Install dependencies
pip install -r requirements_minimal.txt

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard_lite:app
```

---

## 📦 Source Code Export

### Export as ZIP

```bash
git archive --format zip --output aiops-mvp.zip main
```

### Export for GitHub

```bash
# Create GitHub repo
git remote add origin https://github.com/yourusername/aiops-mvp.git
git branch -M main
git push -u origin main
```

### Export for Documentation

```bash
# Generate README
cat > README.md << EOF
# AIOps MVP Platform
Autonomous operations platform with ML-based anomaly detection.

## Quick Start
\`\`\`bash
python dashboard_lite.py
\`\`\`
EOF
```

---

## 🔑 Production Checklist

Before going live:

- [ ] Change `JWT_SECRET_KEY`
- [ ] Set up MongoDB or PostgreSQL
- [ ] Enable HTTPS
- [ ] Configure backup strategy
- [ ] Set up monitoring/alerts
- [ ] Configure logging
- [ ] Document API endpoints
- [ ] Set up CI/CD pipeline
- [ ] Create runbooks
- [ ] Test failover

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        run: |
          docker build -t myimage .
          docker push myimage:latest
      - name: Deploy
        run: |
          # Your deploy command here
```

---

## 📊 Performance Metrics

Target metrics for production:

| Metric | Target |
|--------|--------|
| API Response Time | <200ms |
| Uptime | 99.9% |
| Anomaly Detection | 85%+ |
| Incident Classification | 90%+ |
| Deployment Time | <5 min |

---

## 🚨 Monitoring Setup

### UptimeRobot (Free)

1. Go to: https://uptimerobot.com
2. Add monitor: `https://your-app.com/api/simulation/status`
3. Set interval: 5 minutes
4. Get alerts if down

### Sentry (Free)

1. Go to: https://sentry.io
2. Create project
3. Add to your app:
   ```python
   import sentry_sdk
   sentry_sdk.init("your-dsn-here")
   ```

### DataDog (Free Trial)

1. Go to: https://www.datadoghq.com
2. Create free account
3. Add APM to track performance

---

## 💰 Cost Summary

| Scenario | Monthly Cost |
|----------|--------------|
| Free tier only | $0 |
| Free + monitoring | $0-5 |
| Production (small) | $10-20 |
| Production (medium) | $50-100 |
| Production (enterprise) | $500+ |

---

## 🎯 Recommended Setup for Production

```
├── Web Server
│   ├── Railway or Render (UI)
│   └── CDN (static files)
├── Database
│   ├── MongoDB Atlas (free tier)
│   └── Backup (daily)
├── Monitoring
│   ├── UptimeRobot
│   └── Sentry
└── CI/CD
    └── GitHub Actions
```

---

## 🚀 Next Steps

1. **Choose a platform** (start with Railway/Render)
2. **Push code to GitHub**
3. **Connect and deploy**
4. **Configure environment variables**
5. **Test the dashboard**
6. **Share with team**

---

## 📞 Support

- **Documentation:** See README.md
- **API Docs:** See openapi.yaml
- **Issues:** GitHub Issues
- **Community:** GitHub Discussions

---

**Your AIOps platform is ready for production!** 🎉
