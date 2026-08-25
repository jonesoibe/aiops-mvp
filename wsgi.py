"""
WSGI entry point for production deployment (Gunicorn)
"""

import os
import sys

# Set environment for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Import the Flask app
from nexus_app import app, socketio

# For Gunicorn with eventlet worker
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
