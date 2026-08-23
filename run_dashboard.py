#!/usr/bin/env python
"""Simple wrapper to run the Flask dashboard with proper path setup."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the app
from src.dashboard_app import app

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
