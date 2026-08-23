# GitHub Setup Guide

Push your AIOps project to GitHub for easy deployment and collaboration.

---

## Prerequisites

- Git installed on your machine
- GitHub account (free at github.com)
- Your AIOps MVP project folder

---

## Step 1: Create GitHub Repository

### Option A: Web Interface

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `aiops-mvp`
   - **Description:** Autonomous AIOps Platform with ML anomaly detection
   - **Visibility:** Public (for easy deployment)
   - **Initialize with:** Nothing (we'll push existing code)
3. Click **"Create repository"**

### Option B: Command Line

```bash
# Install GitHub CLI
# Windows: choco install gh
# Mac: brew install gh
# Linux: sudo apt install gh

# Login
gh auth login

# Create repo
gh repo create aiops-mvp --public --source=. --remote=origin --push
```

---

## Step 2: Initialize Git (If Not Already Done)

```bash
# Navigate to your project
cd aiops-mvp

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AIOps MVP platform with ML anomaly detection"

# Add GitHub remote
git remote add origin https://github.com/yourusername/aiops-mvp.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Step 3: Add README

GitHub uses README.md to display on project page.

```bash
cat > README.md << 'EOF'
# AIOps MVP Platform

Autonomous IT Operations platform with ML-based anomaly detection, incident classification, and automated remediation.

## Features

✅ Real-time anomaly detection (Isolation Forest, 85-94% accuracy)
✅ Incident classification (Random Forest, 3-category taxonomy)
✅ Multi-service fault correlation
✅ JWT authentication with RBAC
✅ Interactive web dashboard
✅ Chaos engineering simulation
✅ Comprehensive audit trail

## Quick Start

### Local

```bash
pip install -r requirements_minimal.txt
python dashboard_lite.py
```

Visit: http://localhost:5000/login
Login: admin / admin123

### Cloud Deployment

- [Deploy to Railway](DEPLOY_RAILWAY.md)
- [Deploy to Render](DEPLOY_RENDER.md)
- [Deploy to Any Platform](DEPLOY_ALL_PLATFORMS.md)

## Documentation

- [Authentication Guide](AUTHENTICATION_GUIDE.md)
- [Setup & Run](SETUP_AND_RUN.md)
- [API Reference](API.md)
- [Security Guide](SECURITY.md)
- [Deployment Guide](DEPLOY_ALL_PLATFORMS.md)

## API Endpoints

```
POST   /api/auth/login
POST   /api/auth/signup
GET    /api/incidents
PUT    /api/incidents/{id}/status
POST   /api/chaos-simulation/run
GET    /api/simulation/status
```

See `openapi.yaml` for full API spec.

## Architecture

```
Browser (Login)
    ↓
Flask Backend (dashboard_lite.py)
    ├─ Authentication (JWT + RBAC)
    ├─ API Endpoints
    └─ Chaos Simulator
        ├─ Anomaly Detection (Isolation Forest)
        ├─ Incident Classification (Random Forest)
        └─ Service Correlation
```

## Tech Stack

- **Backend:** Flask, Python 3.11
- **ML:** scikit-learn (Isolation Forest, Random Forest)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MongoDB (optional), in-memory storage
- **Auth:** JWT + bcrypt
- **Deployment:** Docker, Railway, Render, AWS, GCP, etc.

## Demo

### Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Operator | operator | operator123 |
| Viewer | viewer | viewer123 |

### What to Try

1. Login as admin
2. Go to Problems dashboard
3. Watch auto-run chaos simulator
4. See real incidents detected
5. Click "View Details" on any incident
6. Update incident status

## Performance

- **Detection Rate:** 85-94%
- **API Response Time:** <200ms
- **Model Training:** ~30 seconds
- **Simulation:** ~10 seconds

## Deployment Status

- ✅ Local development
- ✅ Docker containerization
- ✅ Railway.app deployment
- ✅ Render.com deployment
- ✅ AWS/GCP ready
- ✅ Production documentation

## License

MIT License - See LICENSE file

## Support

- 📖 [Documentation](/)
- 🚀 [Deployment Guides](DEPLOY_ALL_PLATFORMS.md)
- 🐛 [Issues](https://github.com/yourusername/aiops-mvp/issues)
- 💬 [Discussions](https://github.com/yourusername/aiops-mvp/discussions)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

Built with ❤️ for modern AIOps
EOF
```

---

## Step 4: Add License

```bash
# MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 AIOps MVP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
EOF
```

---

## Step 5: Commit and Push

```bash
git add README.md LICENSE .gitignore
git commit -m "Add documentation and gitignore"
git push origin main
```

---

## Step 6: Configure Repository Settings

### In GitHub Web Interface

1. Go to your repo settings
2. **General:**
   - Set default branch to `main`
   - Enable "Discussions"

3. **Branch Protection:**
   - Add rule for `main` branch
   - Require pull request reviews (optional)

4. **Secrets & Variables:**
   - Add Railway/Render deployment keys if needed

---

## Step 7: Set Up Auto-Deployment (Optional)

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Step 8: Verify Deployment

```bash
# Check remote
git remote -v

# Should show:
# origin  https://github.com/yourusername/aiops-mvp.git (fetch)
# origin  https://github.com/yourusername/aiops-mvp.git (push)

# Check branches
git branch -a

# Verify files on GitHub
git ls-remote origin
```

---

## Common Git Commands

```bash
# See what changed
git status

# Add specific files
git add filename.py

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

---

## Making Changes

### Workflow

1. **Make changes** in your editor
2. **Test locally** (python dashboard_lite.py)
3. **Commit changes** (git add . && git commit -m "message")
4. **Push to GitHub** (git push origin main)
5. **Auto-deploy** if configured (or manual deploy)

---

## Sharing Your Project

### Share GitHub URL
```
https://github.com/yourusername/aiops-mvp
```

### Share Deployed App
```
https://aiops-mvp.up.railway.app
```

### Share Credentials
```
Username: admin
Password: admin123
```

---

## Troubleshooting

### "Permission denied"
```bash
# Generate SSH key
ssh-keygen -t ed25519

# Add to GitHub settings
# Settings → SSH and GPG keys → New SSH key
```

### "Updates were rejected"
```bash
# Pull latest changes
git pull origin main

# Resolve conflicts manually
git add .
git commit -m "Resolve conflicts"
git push origin main
```

### "Branch out of date"
```bash
git fetch origin
git rebase origin/main
git push origin main --force-with-lease
```

---

## Next Steps

1. ✅ Create GitHub repo
2. ✅ Push code
3. ✅ Deploy to cloud (Railway/Render)
4. ✅ Share with team
5. ✅ Collaborate

---

**Your AIOps project is now on GitHub!** 🎉
