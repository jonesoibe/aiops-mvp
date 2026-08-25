#!/usr/bin/env python3
import sys
import os

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Try to import and check routes
try:
    from nexus_app import app
    
    print("Flask routes registered:")
    routes = sorted(list(set([str(rule) for rule in app.url_map.iter_rules()])))
    
    api_routes = [r for r in routes if r.startswith('/api')]
    for route in api_routes[-5:]:  # Last 5 API routes
        print(f"  {route}")
    
    # Check if approvals route is there
    if any('approvals' in r for r in routes):
        print("\nApprovals routes found!")
    else:
        print("\nNO APPROVALS ROUTES FOUND!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
