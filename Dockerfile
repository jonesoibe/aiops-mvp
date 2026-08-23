# Multi-stage build for AIOps Platform

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_minimal.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements_minimal.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=dashboard_lite.py
ENV PYTHONIOENCODING=utf-8

# Create necessary directories
RUN mkdir -p data/raw data/processed logs mlruns

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/simulation/status', timeout=5)" || exit 1

# Run application
CMD ["python", "dashboard_lite.py"]
