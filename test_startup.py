#!/usr/bin/env python3
"""Test if the app loads without hanging."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing app startup...")
print(f"MongoDB URI configured: {bool(os.getenv('MONGODB_URI'))}")
print(f"Environment: {os.getenv('ENVIRONMENT')}")
print(f"SSL Cert path: {os.getenv('SSL_CERT_PATH')}")
print(f"SSL Key path: {os.getenv('SSL_KEY_PATH')}")

print("\nLoading Flask app...")
try:
    from nexus_app import app, socketio
    print("✅ Flask app loaded successfully!")
except Exception as e:
    print(f"❌ Error loading app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting a simple route...")
with app.test_client() as client:
    try:
        response = client.get('/login')
        print(f"✅ GET /login returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n✅ Startup test completed!")
