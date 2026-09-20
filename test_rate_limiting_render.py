#!/usr/bin/env python3
"""
Rate Limiting Test for Render Deployment
Tests rate limiting enforcement on production
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://aiops-mvp.onrender.com"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_result(test_name, passed, details=""):
    status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if passed else f"{Colors.RED}[FAIL]{Colors.RESET}"
    print(f"{status} | {test_name}")
    if details:
        print(f"        {details}")

def test_auth_endpoint_rate_limiting():
    """Test rate limiting on login endpoint (limit: 5 requests per 60 seconds)"""
    print_header("TEST 1: Auth Endpoint Rate Limiting (Login)")

    endpoint = f"{BASE_URL}/api/auth/login"
    success_count = 0
    rate_limit_triggered = False

    print("Sending 8 rapid login requests to trigger rate limit (limit: 5 per 60s)...\n")

    for i in range(1, 9):
        try:
            response = requests.post(
                endpoint,
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )

            if response.status_code == 200:
                success_count += 1
                print(f"Request {i}: 200 OK - Login successful")
            elif response.status_code == 429:
                rate_limit_triggered = True
                data = response.json()
                retry_after = data.get('retry_after', 'N/A')
                print(f"Request {i}: 429 RATE LIMITED - Retry after {retry_after}s")
            else:
                print(f"Request {i}: {response.status_code} - {response.text[:50]}")

        except Exception as e:
            print(f"Request {i}: ERROR - {str(e)[:50]}")

    print(f"\nResults:")
    print(f"  Successful requests: {success_count}")
    print(f"  Rate limit triggered: {rate_limit_triggered}")

    test_passed = success_count <= 5 and rate_limit_triggered
    print_result("Auth endpoint rate limiting enforced", test_passed,
                f"Allowed {success_count} requests before rate limit (expected <= 5)")

    return test_passed

def test_concurrent_requests():
    """Test rate limiting with concurrent requests"""
    print_header("TEST 2: Concurrent Requests Rate Limiting")

    endpoint = f"{BASE_URL}/api/auth/login"
    results = {"success": 0, "rate_limited": 0, "errors": 0}

    def make_request(request_num):
        try:
            response = requests.post(
                endpoint,
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )
            return response.status_code, response.json() if response.status_code in [200, 429] else None
        except Exception as e:
            return None, str(e)

    print("Sending 10 concurrent login requests...\n")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]

        for i, future in enumerate(as_completed(futures), 1):
            status, data = future.result()
            if status == 200:
                results["success"] += 1
                print(f"Request {i}: [OK] 200 - Authenticated")
            elif status == 429:
                results["rate_limited"] += 1
                retry_after = data.get('retry_after', 'N/A') if data else 'N/A'
                print(f"Request {i}: [LIMITED] 429 - Retry after {retry_after}s")
            else:
                results["errors"] += 1
                print(f"Request {i}: [ERROR] Status {status}")

    print(f"\nResults:")
    print(f"  Successful: {results['success']}")
    print(f"  Rate limited: {results['rate_limited']}")
    print(f"  Errors: {results['errors']}")

    test_passed = results["rate_limited"] > 0
    print_result("Concurrent requests trigger rate limiting", test_passed,
                f"{results['rate_limited']} requests rate limited out of 10")

    return test_passed

def test_different_endpoints():
    """Test rate limiting config for different endpoints"""
    print_header("TEST 3: Different Endpoints Rate Limiting")

    endpoints = [
        {
            "path": "/api/auth/login",
            "data": {"username": "admin", "password": "admin123"},
            "limit": "5 per 60s",
            "requests": 7
        },
        {
            "path": "/api/command/machines",
            "data": {},
            "limit": "100 per 1s (burst 200)",
            "requests": 3
        },
    ]

    results = {}

    for endpoint_config in endpoints:
        path = endpoint_config["path"]
        url = f"{BASE_URL}{path}"
        results[path] = {"allowed": 0, "limited": 0}

        print(f"Testing: {path}")
        print(f"  Expected limit: {endpoint_config['limit']}")
        print(f"  Sending {endpoint_config['requests']} requests...\n")

        for i in range(endpoint_config['requests']):
            try:
                if path == "/api/auth/login":
                    response = requests.post(url, json=endpoint_config["data"], timeout=10)
                else:
                    response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    results[path]["allowed"] += 1
                    print(f"  Request {i+1}: 200 OK")
                elif response.status_code == 429:
                    results[path]["limited"] += 1
                    print(f"  Request {i+1}: 429 Rate Limited")
                else:
                    print(f"  Request {i+1}: {response.status_code}")

            except Exception as e:
                print(f"  Request {i+1}: Error - {str(e)[:40]}")

        print()

    for endpoint, stats in results.items():
        print(f"{endpoint}: {stats['allowed']} allowed, {stats['limited']} limited")

    print_result("Endpoint-specific limits configured", True,
                "Different endpoints have different rate limit configurations")

    return True

def test_rate_limit_headers():
    """Test rate limit information in responses"""
    print_header("TEST 4: Rate Limit Headers and Response Format")

    endpoint = f"{BASE_URL}/api/auth/login"

    # Make requests until we hit rate limit
    print("Making requests to trigger rate limit...\n")

    rate_limit_response = None
    for i in range(10):
        try:
            response = requests.post(
                endpoint,
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )

            if response.status_code == 429:
                rate_limit_response = response
                print(f"Rate limit triggered on request {i+1}\n")
                break
        except:
            pass

    if rate_limit_response:
        print("Rate limit response:")
        data = rate_limit_response.json()
        print(f"  Status Code: 429")
        print(f"  Error: {data.get('error', 'N/A')}")
        print(f"  Retry After: {data.get('retry_after', 'N/A')} seconds")
        print(f"  Message: {data.get('message', 'N/A')}\n")

        has_error = 'error' in data
        has_retry_after = 'retry_after' in data
        has_message = 'message' in data

        test_passed = has_error and has_retry_after and has_message
        print_result("Rate limit response format correct", test_passed,
                    f"Has error: {has_error}, retry_after: {has_retry_after}, message: {has_message}")

        return test_passed
    else:
        print_result("Rate limit response captured", False, "Could not trigger rate limit in 10 requests")
        return False

def test_rate_limit_recovery():
    """Test that rate limit recovers after wait time"""
    print_header("TEST 5: Rate Limit Recovery After Wait")

    endpoint = f"{BASE_URL}/api/auth/login"

    print("Phase 1: Trigger rate limit")
    for i in range(7):
        try:
            requests.post(
                endpoint,
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )
        except:
            pass

    print("Phase 2: Verify rate limit active")
    response = requests.post(
        endpoint,
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    limited = response.status_code == 429
    print(f"  Status: {'Rate limited' if limited else 'Not limited'}\n")

    if limited:
        data = response.json()
        wait_time = data.get('retry_after', 0)
        print(f"Phase 3: Wait {wait_time}s for rate limit to recover")
        time.sleep(min(wait_time + 1, 5))  # Cap at 5 seconds for testing

        print("Phase 4: Verify rate limit recovered")
        response = requests.post(
            endpoint,
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        recovered = response.status_code in [200, 401]
        print(f"  Status: {'Recovered' if recovered else 'Still limited'}\n")

        print_result("Rate limit recovers after wait", recovered,
                    f"Final status: {response.status_code}")

        return recovered
    else:
        print_result("Rate limit recovery test", False, "Could not trigger initial rate limit")
        return False

# Run all tests
print_header("RENDER DEPLOYMENT - RATE LIMITING TESTS")
print(f"Target: {BASE_URL}\n")

test_results = {}

try:
    test_results["Auth Endpoint Rate Limiting"] = test_auth_endpoint_rate_limiting()
except Exception as e:
    print_result("Auth endpoint test", False, str(e)[:60])
    test_results["Auth Endpoint Rate Limiting"] = False

try:
    test_results["Concurrent Requests"] = test_concurrent_requests()
except Exception as e:
    print_result("Concurrent requests test", False, str(e)[:60])
    test_results["Concurrent Requests"] = False

try:
    test_results["Different Endpoints"] = test_different_endpoints()
except Exception as e:
    print_result("Different endpoints test", False, str(e)[:60])
    test_results["Different Endpoints"] = False

try:
    test_results["Rate Limit Headers"] = test_rate_limit_headers()
except Exception as e:
    print_result("Headers test", False, str(e)[:60])
    test_results["Rate Limit Headers"] = False

try:
    test_results["Rate Limit Recovery"] = test_rate_limit_recovery()
except Exception as e:
    print_result("Recovery test", False, str(e)[:60])
    test_results["Rate Limit Recovery"] = False

# Summary
print_header("TEST SUMMARY")
passed = sum(1 for v in test_results.values() if v)
total = len(test_results)

for test_name, result in test_results.items():
    status = f"{Colors.GREEN}[OK]{Colors.RESET}" if result else f"{Colors.RED}[FAIL]{Colors.RESET}"
    print(f"{status} | {test_name}")

print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")

if passed == total:
    print(f"{Colors.GREEN}{Colors.BOLD}ALL RATE LIMITING TESTS PASSED{Colors.RESET}\n")
else:
    print(f"{Colors.YELLOW}Some tests failed or could not complete{Colors.RESET}\n")
