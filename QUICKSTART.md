# AIOps MVP - Quick Start Guide

Get the AIOps MVP system up and running in 5 minutes.

## Prerequisites

- Python 3.11+
- Git
- 4GB RAM minimum

## Installation

### 1. Clone & Setup

```bash
# Clone repository
git clone https://github.com/jonesoibe/aiops-mvp.git
cd aiops-mvp

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
# Windows
notepad .env

# macOS/Linux
nano .env
```

### 3. Create Data Directories

```bash
mkdir -p data/raw data/processed notebooks models config mlruns
```

## Running the System

### Option A: Web Dashboard (Recommended)

```bash
# Terminal 1: Start Flask server
python run_dashboard.py

# Open browser to http://localhost:5000
```

Dashboard features:
- 📊 Overview of chaos simulation results
- 🔥 Run chaos injection simulation
- 🔬 Learn detection methods
- 🔒 Security hardening guide
- 📚 API documentation with examples

### Option B: Python Notebook

```bash
# Start Jupyter
jupyter notebook

# Open notebooks/chaos_simulation.ipynb
# Run cells in order:
# 1. Setup & imports
# 2. Generate chaos simulation
# 3. Run anomaly detection
# 4. View results
```

### Option C: Command Line

```bash
# Run chaos simulation directly
python -c "
from src.chaos_simulator import run_chaos_simulation
df_faults, df_anomalies, df_incidents = run_chaos_simulation()
print(f'Detected {len(df_anomalies)} anomalies from {len(df_faults)} faults')
"
```

## API Usage

### Start Server

```bash
python run_dashboard.py
```

### Test Endpoints

```bash
# Set your API key
export API_KEY="demo_key_12345"

# Run chaos simulation
curl -X POST http://localhost:5000/api/chaos-simulation \
  -H "Authorization: Bearer $API_KEY"

# Get metrics
curl http://localhost:5000/api/metrics \
  -H "Authorization: Bearer $API_KEY" | jq .

# Get incidents
curl http://localhost:5000/api/incidents \
  -H "Authorization: Bearer $API_KEY" | jq .

# View API docs
curl http://localhost:5000/api/openapi.json | jq .
```

## Key Features

### 🔥 Chaos Simulation

Injects 3 simultaneous faults:
- **Service A:** Memory leak (gradual increase)
- **Service B:** High latency (spike then recovery)
- **Service C:** Error rate spike (sudden increase)

### 🔬 Detection Methods

Multi-strategy hybrid detection:
1. **Threshold Detection:** Values > baseline + 0.5σ
2. **Percentage Change:** Deviations > 20% flagged
3. **Fault Window Correlation:** ±2 time units around faults
4. **Drift Detection:** Values > 15% from baseline

### 📊 Classification

Anomalies categorized into 3 incident types:
- Resource Exhaustion (Service A)
- Performance Degradation (Service B)
- Service Unavailability (Service C)

### 📈 Performance

Compared to baseline threshold approach:
- **+37% Precision** - Fewer false positives
- **+30% Recall** - Catches more anomalies
- **+29% F1-Score** - Better overall performance
- **+38% ROC-AUC** - Better classification

## Configuration

Edit `config/settings.yaml` to tune:

```yaml
anomaly_detection:
  n_estimators: 200
  contamination: 0.05
  detection_threshold: 0.55

classification:
  n_estimators: 300
  automation_threshold: 0.85

response:
  simulate_only: true
  recovery_window_seconds: 60
```

## Security

### Enable Authentication

1. Generate secure API key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Add to `.env`:
```bash
AIOPS_API_KEY=your_generated_key_here
```

3. Use in requests:
```bash
curl -H "Authorization: Bearer your_generated_key_here" \
  http://localhost:5000/api/metrics
```

### Security Checklist

- [ ] Update `.env` with secure values
- [ ] Generate strong API key
- [ ] Enable HTTPS in production
- [ ] Configure CORS origins
- [ ] Set up logging
- [ ] Scan dependencies: `safety check`
- [ ] Run security scan: `bandit -r src/`

## Docker Deployment

### Build Image

```bash
docker build -t aiops-mvp:latest .
```

### Run Container

```bash
docker run -p 5000:5000 aiops-mvp:latest
# Access at http://localhost:5000
```

## Production Deployment

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-aiops-app

# Set environment variables
heroku config:set AIOPS_API_KEY=your_key

# Deploy
git push heroku main

# Open app
heroku open
```

### AWS EC2

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone repo
git clone https://github.com/yourusername/aiops-mvp.git
cd aiops-mvp

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn
pip install gunicorn
gunicorn -b 0.0.0.0:5000 src.dashboard_app:app
```

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy aiops-mvp \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars AIOPS_API_KEY=your_key
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:** Install in development mode:
```bash
pip install -e .
```

Or ensure you're running from project root:
```bash
cd aiops-mvp
python run_dashboard.py
```

### Issue: "Port 5000 already in use"

**Solution:** Kill process or use different port:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID process_id /F

# macOS/Linux
lsof -i :5000
kill -9 process_id

# Or use different port
python -c "from src.dashboard_app import app; app.run(port=5001)"
```

### Issue: "API returns 401 Unauthorized"

**Solution:** Check API key:
```bash
# Verify .env has AIOPS_API_KEY
cat .env | grep AIOPS_API_KEY

# Use correct format
curl -H "Authorization: Bearer your_api_key" http://localhost:5000/api/metrics
```

### Issue: Low anomaly detection (< 80%)

**Solution:** Update detection thresholds:
1. Open `config/settings.yaml`
2. Lower `detection_threshold` (try 0.45)
3. Increase `contamination` (try 0.1)
4. Restart server

## Next Steps

### 1. Read Full Documentation

- [README.md](README.md) - Project overview
- [SECURITY.md](SECURITY.md) - 21 security best practices
- [API.md](API.md) - Complete API reference

### 2. Explore Jupyter Notebooks

- `notebooks/` - Interactive analysis and visualization

### 3. Customize Configuration

- Edit `config/settings.yaml` for your environment
- Adjust thresholds for your anomaly types
- Configure alert thresholds

### 4. Integrate with Your Systems

- Use REST API for custom integrations
- Implement webhook handlers for incidents
- Set up monitoring/alerting rules

### 5. Deploy to Production

- Choose hosting platform (Heroku, AWS, GCP)
- Enable HTTPS and authentication
- Set up logging and monitoring
- Configure backups

## Support & Issues

- 📖 [Documentation](https://github.com/jonesoibe/aiops-mvp/wiki)
- 🐛 [Report Issues](https://github.com/jonesoibe/aiops-mvp/issues)
- 💬 [Discussions](https://github.com/jonesoibe/aiops-mvp/discussions)

## Key Files

| File | Purpose |
|------|---------|
| `src/chaos_simulator.py` | Fault injection & anomaly detection |
| `src/pipeline.py` | End-to-end analysis pipeline |
| `src/classify.py` | Incident classification |
| `src/dashboard_app.py` | Flask web server |
| `templates/dashboard.html` | Web UI |
| `config/settings.yaml` | Configuration parameters |
| `.env` | Environment variables (secret) |
| `requirements.txt` | Python dependencies |

## Performance Expectations

- **Anomaly Detection:** 85-94% accuracy
- **Processing Speed:** 2-5 seconds per analysis
- **Memory Usage:** 500MB-2GB
- **CPU:** Low utilization for most operations

## Version History

- **v1.0.0** (Aug 2026) - Initial release
  - Hybrid multi-strategy anomaly detection
  - 3-category incident classification
  - Web dashboard with visualizations
  - REST API with authentication
  - Security hardening

## License

MIT License - See [LICENSE](LICENSE) file

## Authors

AIOps MVP Team
- GitHub: [@jonesoibe](https://github.com/jonesoibe)
- Email: jonesoibe@gmail.com

---

**Last Updated:** August 2026

**Happy anomaly detecting! 🚀**
