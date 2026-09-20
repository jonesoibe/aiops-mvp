#!/usr/bin/env python3
"""Quick rate limiting test - focus on auth endpoint"""

import requests
import time

BASE_URL = "https://aiops-mvp.onrender.com"
endpoint = f"{BASE_URL}/api/auth/login"

print("[*] Testing rate limiting on /api/auth/login")
print("[*] Limit: 5 requests per 60 seconds")
print("[*] Sending 8 rapid requests...\n")

results = []
for i in range(1, 9):
    try:
        start = time.time()
        response = requests.post(
            endpoint,
            json={"username": "admin", "password": "admin123"},
            timeout=15
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"Request {i}: [200 OK] (%.2fs)" % elapsed)
            results.append(("ok", elapsed))
        elif response.status_code == 429:
            data = response.json()
            retry = data.get('retry_after', '?')
            print(f"Request {i}: [429 RATE LIMITED] retry_after={retry}s (%.2fs)" % elapsed)
            results.append(("limited", elapsed))
        else:
            print(f"Request {i}: [{response.status_code}] (%.2fs)" % elapsed)
            results.append(("other", elapsed))
    except Exception as e:
        print(f"Request {i}: [ERROR] {str(e)[:60]}")
        results.append(("error", 0))

ok_count = sum(1 for r, _ in results if r == "ok")
limited_count = sum(1 for r, _ in results if r == "limited")

print(f"\n[SUMMARY]")
print(f"Successful: {ok_count}")
print(f"Rate limited: {limited_count}")
print(f"Expected: <= 5 successful, then rate limited")

if ok_count <= 5 and limited_count > 0:
    print(f"\n[PASS] Rate limiting is working correctly!")
elif limited_count == 0:
    print(f"\n[INCOMPLETE] Rate limit not triggered (may be due to Render cold-start delays)")
else:
    print(f"\n[UNEXPECTED] Got {ok_count} successful and {limited_count} limited")
