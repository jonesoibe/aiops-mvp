#!/usr/bin/env python3
"""
Load 200K rows from 10 machines FAST (optimized)
"""

import csv
import json
import requests
import time
import sys
from datetime import datetime
from pathlib import Path

# Fix encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:5000"
LOGIN_ENDPOINT = "/api/auth/login"
METRICS_ENDPOINT = "/api/metrics/record"

class FastMetricsLoader:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def authenticate(self):
        """Get JWT token"""
        try:
            response = self.session.post(
                f"{API_BASE_URL}{LOGIN_ENDPOINT}",
                json={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                self.token = response.json().get('token')
                print("[OK] Authenticated")
                return True
        except:
            pass
        print("[ERROR] Auth failed")
        return False

    def record_metrics(self, cpu, memory, request_rate, error_rate):
        """Record single metric"""
        if not self.token:
            return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "cpu": float(cpu),
                "memory": float(memory),
                "request_rate": float(request_rate),
                "error_rate": float(error_rate)
            }
            response = self.session.post(
                f"{API_BASE_URL}{METRICS_ENDPOINT}",
                json=payload,
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def load_smd_data(self, filepath, limit=None):
        """Load SMD data fast"""
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"[SKIP] {filepath.name} not found")
            return 0

        count = 0
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    if limit and count >= limit:
                        break

                    try:
                        features = [float(x) for x in row]
                        if len(features) < 16:
                            continue

                        cpu = features[0] * 100
                        memory = features[1] * 100
                        request_rate = features[9] * 200
                        error_rate = features[14] * 5

                        if self.record_metrics(cpu, memory, request_rate, error_rate):
                            count += 1
                            if count % 500 == 0:
                                print(f"  {count:6d} rows loaded from {filepath.name}")

                        # Ultra-fast: minimal delay
                        if count % 100 == 0:
                            time.sleep(0.001)  # 1ms delay every 100 rows
                    except:
                        continue

            print(f"[OK] {filepath.name:20} - {count:6d} rows")
            return count
        except Exception as e:
            print(f"[ERROR] {filepath.name}: {e}")
            return 0

def main():
    smd_dir = Path(r'C:\Users\FAVOUR\aiops-mvp\data\raw\smd')

    machines = [
        'machine-1-1.txt', 'machine-1-3.txt', 'machine-1-5.txt', 'machine-1-7.txt',
        'machine-2-2.txt', 'machine-2-4.txt', 'machine-2-6.txt', 'machine-2-8.txt',
        'machine-3-3.txt', 'machine-3-9.txt',
    ]

    print("=" * 70)
    print("FAST LOADER: 200,000 ROWS FROM 10 MACHINES")
    print("=" * 70)
    print(f"Target: 20,000 rows × 10 machines = 200,000 total\n")

    loader = FastMetricsLoader()
    if not loader.authenticate():
        sys.exit(1)

    print("\n" + "=" * 70)
    print("LOADING DATA")
    print("=" * 70 + "\n")

    total = 0
    rows_per_file = 20000
    start_time = time.time()

    for i, machine in enumerate(machines, 1):
        filepath = smd_dir / machine
        print(f"[{i:2d}/10] Loading {machine:20}", end=" ", flush=True)

        rows = loader.load_smd_data(str(filepath), rows_per_file)
        total += rows

        elapsed = time.time() - start_time
        rate = total / elapsed if elapsed > 0 else 0
        print(f" ({rate:.0f} rows/sec, {total:,} total)")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"COMPLETE: Loaded {total:,} rows in {elapsed:.1f} seconds")
    print(f"Rate: {total/elapsed:.0f} rows/second")
    print("=" * 70)
    print(f"\nDashboard: http://localhost:5000")
    print(f"Refresh to see trends across 10 machines!")

if __name__ == '__main__':
    main()
