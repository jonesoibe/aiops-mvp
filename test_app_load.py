#!/usr/bin/env python3
"""
Quick test to verify Flask app loads without errors
"""
import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to load Flask app...")
    from nexus_app import app
    print("✓ Flask app loaded successfully!")

    # Count routes
    route_count = len([r for r in app.url_map.iter_rules()])
    print(f"✓ Total routes registered: {route_count}")

    # List some key routes
    key_routes = [
        '/forgot-password',
        '/api/auth/forgot-password',
        '/reset-password',
        '/api/auth/reset-password',
        '/profile',
        '/api/user/profile',
        '/api/user/change-password'
    ]

    print("\nChecking new authentication routes:")
    registered_routes = {r.rule for r in app.url_map.iter_rules()}

    for route in key_routes:
        if route in registered_routes:
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route} NOT FOUND")

    print("\n✓ App is ready to run!")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error loading app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
