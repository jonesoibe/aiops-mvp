#!/usr/bin/env python3
"""
Test the dashboard endpoint to verify it works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_app import app, in_memory_store
import json

def test_dashboard_endpoint():
    """Test the /api/overview/dashboard endpoint"""

    print("\n" + "="*70)
    print("TESTING DASHBOARD ENDPOINT")
    print("="*70 + "\n")

    with app.test_client() as client:
        # First, get a token
        print("1. Getting authentication token...")
        login_response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })

        if login_response.status_code != 200:
            print(f"   ERROR: Login failed with status {login_response.status_code}")
            print(f"   Response: {login_response.get_json()}")
            return False

        token = login_response.get_json().get('token')
        print(f"   ✅ Token received: {token[:20]}...\n")

        # Test the dashboard endpoint
        print("2. Testing /api/overview/dashboard...")
        response = client.get('/api/overview/dashboard', headers={
            'Authorization': f'Bearer {token}'
        })

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print("   ✅ Response successful!\n")
            print("   Response structure:")
            print(f"   - metrics_summary: {data.get('metrics_summary')}")
            print(f"   - active_issues: {data.get('active_issues')}")
            print(f"   - performance: {data.get('performance')}")
            print(f"   - recent_metrics count: {len(data.get('recent_metrics', []))}")

            if data.get('recent_metrics'):
                print("\n   First 3 metrics:")
                for metric in data.get('recent_metrics', [])[:3]:
                    print(f"     - {metric['name']}: {metric['value']} {metric.get('unit', '')} ({metric['status']})")

            print("\n   Full response:")
            print(json.dumps(data, indent=2, default=str))
            return True
        else:
            print(f"   ❌ Request failed!")
            print(f"   Response: {response.get_json()}")
            return False

if __name__ == '__main__':
    success = test_dashboard_endpoint()

    if success:
        print("\n" + "="*70)
        print("✅ DASHBOARD ENDPOINT WORKS CORRECTLY")
        print("="*70)
        print("\nThe endpoint is ready. The frontend should now load this data.")
        print("Check the browser console for any JavaScript errors.")
    else:
        print("\n" + "="*70)
        print("❌ DASHBOARD ENDPOINT TEST FAILED")
        print("="*70)
