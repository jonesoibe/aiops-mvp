#!/usr/bin/env python3
"""
Load sample metrics from CSV files into the Nexus AIOps API
Supports Server Machine Dataset (SMD) and custom CSV formats
"""

import csv
import json
import requests
import time
import sys
import os
from datetime import datetime
from pathlib import Path
import argparse

# Fix encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
API_BASE_URL = "http://localhost:5000"
LOGIN_ENDPOINT = "/api/auth/login"
METRICS_ENDPOINT = "/api/metrics/record"

class MetricsLoader:
    def __init__(self, username="admin", password="admin123", api_url=API_BASE_URL):
        self.api_url = api_url
        self.token = None
        self.username = username
        self.password = password
        self.session = requests.Session()

    def authenticate(self):
        """Login and get JWT token"""
        try:
            response = self.session.post(
                f"{self.api_url}{LOGIN_ENDPOINT}",
                json={"username": self.username, "password": self.password}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print("[OK] Authenticated successfully")
                return True
            else:
                print(f"[ERROR] Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Authentication error: {e}")
            return False

    def record_metrics(self, cpu, memory, request_rate, error_rate):
        """Record a single metric to the API"""
        if not self.token:
            print("[ERROR] Not authenticated")
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
                f"{self.api_url}{METRICS_ENDPOINT}",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                return True
            else:
                print(f"[WARN] Error recording metrics: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def load_smd_data(self, filepath, skip_rows=0, limit=None, interval=0.5):
        """
        Load Server Machine Dataset (SMD) format data
        SMD has 38 features - we'll map select ones to our 4 metrics

        Mapping:
        - Feature 1 -> CPU Usage (scaled to 0-100)
        - Feature 2 -> Memory Usage (scaled to 0-100)
        - Feature 10 -> Request Rate (scaled to 0-200 req/s)
        - Feature 15 -> Error Rate (scaled to 0-5%)
        """
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"[ERROR] File not found: {filepath}")
            return 0

        print(f"[INFO] Loading SMD data from: {filepath.name}")
        count = 0
        skipped = 0

        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    if idx < skip_rows:
                        skipped += 1
                        continue

                    if limit and count >= limit:
                        break

                    try:
                        # SMD has 38 features (0-37)
                        features = [float(x) for x in row]
                        if len(features) < 16:
                            continue

                        # Map features to metrics (scale to realistic ranges)
                        cpu = features[0] * 100  # 0-100%
                        memory = features[1] * 100  # 0-100%
                        request_rate = features[9] * 200  # 0-200 req/s
                        error_rate = features[14] * 5  # 0-5%

                        if self.record_metrics(cpu, memory, request_rate, error_rate):
                            count += 1
                            if count % 100 == 0:
                                print(f"   --> {count} metrics recorded")
                            time.sleep(interval)  # Rate limit requests
                        else:
                            count += 1
                    except (ValueError, IndexError) as e:
                        skipped += 1
                        continue

            print(f"[OK] Loaded {count} metrics from SMD file")
            print(f"   Skipped: {skipped} rows")
            return count

        except Exception as e:
            print(f"[ERROR] Error loading file: {e}")
            return 0

    def load_custom_csv(self, filepath, cpu_col, memory_col, request_col, error_col,
                       skip_rows=0, limit=None, interval=0.5):
        """
        Load custom CSV format with specified column names/indices
        """
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"[ERROR] File not found: {filepath}")
            return 0

        print(f"[INFO] Loading custom CSV from: {filepath.name}")
        count = 0

        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    if idx < skip_rows:
                        continue

                    if limit and count >= limit:
                        break

                    try:
                        cpu = float(row.get(cpu_col, 0))
                        memory = float(row.get(memory_col, 0))
                        request_rate = float(row.get(request_col, 0))
                        error_rate = float(row.get(error_col, 0))

                        if self.record_metrics(cpu, memory, request_rate, error_rate):
                            count += 1
                            if count % 100 == 0:
                                print(f"   --> {count} metrics recorded")
                            time.sleep(interval)
                    except (ValueError, KeyError) as e:
                        print(f"[WARN] Skipping row {idx}: {e}")
                        continue

            print(f"[OK] Loaded {count} metrics from CSV")
            return count

        except Exception as e:
            print(f"[ERROR] Error loading file: {e}")
            return 0

    def generate_synthetic_metrics(self, count=1000, interval=0.1):
        """Generate realistic synthetic metrics for testing"""
        print(f"[INFO] Generating {count} synthetic metrics...")

        import random
        random.seed(42)

        for i in range(count):
            # Generate somewhat correlated metrics
            cpu = random.gauss(45, 15)  # Normal dist around 45%
            memory = random.gauss(55, 12)
            request_rate = random.gauss(75, 25)
            error_rate = random.gauss(1, 0.8)

            # Clamp to valid ranges
            cpu = max(5, min(95, cpu))
            memory = max(5, min(95, memory))
            request_rate = max(10, min(200, request_rate))
            error_rate = max(0, min(5, error_rate))

            if self.record_metrics(cpu, memory, request_rate, error_rate):
                if (i + 1) % 100 == 0:
                    print(f"   --> {i + 1} metrics recorded")
                time.sleep(interval)
            else:
                print(f"[WARN] Failed to record metric {i + 1}")

        print(f"[OK] Generated {count} synthetic metrics")
        return count


def main():
    parser = argparse.ArgumentParser(
        description="Load sample metrics into Nexus AIOps API"
    )
    parser.add_argument(
        '--mode',
        choices=['smd', 'csv', 'synthetic'],
        default='smd',
        help='Data source mode (default: smd)'
    )
    parser.add_argument(
        '--file',
        help='CSV file path'
    )
    parser.add_argument(
        '--smd-dir',
        default=r'C:\Users\FAVOUR\aiops-mvp\data\raw\smd',
        help='SMD directory path'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of records to load'
    )
    parser.add_argument(
        '--skip',
        type=int,
        default=0,
        help='Skip first N rows'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=0.1,
        help='Delay between requests (seconds)'
    )
    parser.add_argument(
        '--url',
        default=API_BASE_URL,
        help=f'API URL (default: {API_BASE_URL})'
    )

    # Custom CSV columns
    parser.add_argument('--cpu-col', default='cpu', help='CPU column name')
    parser.add_argument('--mem-col', default='memory', help='Memory column name')
    parser.add_argument('--req-col', default='request_rate', help='Request rate column name')
    parser.add_argument('--err-col', default='error_rate', help='Error rate column name')

    args = parser.parse_args()

    # Initialize loader
    loader = MetricsLoader(api_url=args.url)

    # Authenticate
    if not loader.authenticate():
        sys.exit(1)

    # Load data based on mode
    if args.mode == 'smd':
        if not args.file:
            # Find first SMD file
            smd_dir = Path(args.smd_dir)
            files = list(smd_dir.glob('machine-*.txt'))
            if not files:
                print(f"[ERROR] No SMD files found in {args.smd_dir}")
                sys.exit(1)
            args.file = str(files[0])
            print(f"[INFO] Using SMD file: {files[0].name}")

        loader.load_smd_data(args.file, skip_rows=args.skip, limit=args.limit, interval=args.interval)

    elif args.mode == 'csv':
        if not args.file:
            print("[ERROR] --file required for CSV mode")
            sys.exit(1)

        loader.load_custom_csv(
            args.file,
            cpu_col=args.cpu_col,
            memory_col=args.mem_col,
            request_col=args.req_col,
            error_col=args.err_col,
            skip_rows=args.skip,
            limit=args.limit,
            interval=args.interval
        )

    elif args.mode == 'synthetic':
        count = args.limit or 1000
        loader.generate_synthetic_metrics(count=count, interval=args.interval)

    print("[OK] Data loading complete!")
    print("[INFO] Visit http://localhost:5000 to view the metrics in the dashboard")


if __name__ == '__main__':
    main()
