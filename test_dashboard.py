#!/usr/bin/env python3
"""
Test script to verify dashboard is functional.
Runs the Flask app and performs basic API tests.
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.dashboard_app import app, simulation_state

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {"username": "admin", "password": "admin123"}
TEST_TOKEN = None

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_success(message):
    """Print success message."""
    print(f"✓ {message}")

def print_error(message):
    """Print error message."""
    print(f"✗ {message}")

def test_login():
    """Test user login."""
    global TEST_TOKEN
    print_header("TEST 1: User Login")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_USER,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            TEST_TOKEN = data['token']
            print_success(f"Login successful")
            print(f"  Token: {TEST_TOKEN[:20]}...")
            print(f"  User: {data['user']['username']} ({data['user']['role']})")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_simulation():
    """Test running chaos simulation."""
    print_header("TEST 2: Run Chaos Simulation")

    if not TEST_TOKEN:
        print_error("No auth token. Run test_login first.")
        return False

    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/api/chaos-simulation/run",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Simulation completed")
            print(f"  Faults injected: {data['summary']['faults_injected']}")
            print(f"  Anomalies detected: {data['summary']['anomalies_detected']}")
            print(f"  Incidents classified: {data['summary']['incidents_classified']}")
            print(f"  Detection rate: {data['summary']['detection_rate']}")

            if data.get('incidents'):
                print(f"  First incident: {data['incidents'][0]['id']}")

            return True
        else:
            print_error(f"Simulation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_incidents():
    """Test fetching incidents."""
    print_header("TEST 3: Get Incidents")

    if not TEST_TOKEN:
        print_error("No auth token. Run test_login first.")
        return False

    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.get(
            f"{BASE_URL}/api/incidents",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Incidents fetched")
            print(f"  Total incidents: {data['total']}")

            if data['incidents']:
                for incident in data['incidents'][:3]:
                    print(f"    - {incident['id']}: {incident['incident_type']} "
                          f"(severity: {incident['severity']}, "
                          f"confidence: {incident['confidence']:.1%})")

            return True
        else:
            print_error(f"Failed to fetch incidents: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_update_incident():
    """Test updating incident status."""
    print_header("TEST 4: Update Incident Status")

    if not TEST_TOKEN:
        print_error("No auth token. Run test_login first.")
        return False

    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

        # First get an incident
        response = requests.get(
            f"{BASE_URL}/api/incidents",
            headers=headers,
            timeout=5
        )

        if response.status_code != 200 or not response.json()['incidents']:
            print_error("No incidents found to update")
            return False

        incident_id = response.json()['incidents'][0]['id']

        # Update it
        response = requests.put(
            f"{BASE_URL}/api/incidents/{incident_id}/status",
            headers=headers,
            json={"status": "acknowledged"},
            timeout=5
        )

        if response.status_code == 200:
            print_success(f"Incident {incident_id} status updated")
            print(f"  New status: acknowledged")
            return True
        else:
            print_error(f"Failed to update incident: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_dashboard_pages():
    """Test dashboard pages load."""
    print_header("TEST 5: Dashboard Pages")

    pages = [
        ("/login", "Login Page"),
        ("/", "Home Page"),
        ("/problems", "Problems Dashboard"),
        ("/infrastructure", "Infrastructure Dashboard"),
        ("/demo", "Demo Simulator"),
    ]

    success_count = 0
    for url, name in pages:
        try:
            response = requests.get(
                f"{BASE_URL}{url}",
                timeout=5,
                allow_redirects=False
            )

            if response.status_code in [200, 302]:
                print_success(f"{name} ({url})")
                success_count += 1
            else:
                print_error(f"{name}: HTTP {response.status_code}")
        except Exception as e:
            print_error(f"{name}: {str(e)}")

    return success_count == len(pages)

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  AIOPS DASHBOARD - FUNCTIONAL TEST SUITE")
    print("  Starting Flask app on http://localhost:5000")
    print("=" * 70)

    # Start Flask in a thread
    import threading
    server_thread = threading.Thread(target=lambda: app.run(debug=False, port=5000, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to start
    print("\n⏳ Waiting for server to start...")
    time.sleep(3)

    # Run tests
    results = []
    results.append(("Login", test_login()))
    time.sleep(1)

    results.append(("Simulation", test_simulation()))
    time.sleep(1)

    results.append(("Get Incidents", test_get_incidents()))
    time.sleep(1)

    results.append(("Update Incident", test_update_incident()))
    time.sleep(1)

    results.append(("Dashboard Pages", test_dashboard_pages()))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Dashboard is functional.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
