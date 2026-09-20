#!/usr/bin/env python3
"""
Load data from multiple SMD machines for comparison
"""

import subprocess
import sys
from pathlib import Path

# Fix encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_machine_data(machine_file, rows_per_machine=20000):
    """Load data from a specific machine file"""
    filepath = Path(machine_file)

    if not filepath.exists():
        print(f"[SKIP] File not found: {filepath.name}")
        return False

    print(f"\n[INFO] Loading from: {filepath.name} ({rows_per_machine} rows)")

    try:
        result = subprocess.run([
            sys.executable, 'load_sample_metrics.py',
            '--mode', 'smd',
            '--file', str(filepath),
            '--limit', str(rows_per_machine),
            '--interval', '0.02'  # Fast injection
        ], capture_output=True, text=True)

        if result.returncode == 0:
            # Extract success message
            for line in result.stdout.split('\n'):
                if '[OK]' in line or '[INFO]' in line:
                    print(f"   {line}")
            return True
        else:
            print(f"[ERROR] Failed to load {filepath.name}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Exception loading {filepath.name}: {e}")
        return False

def main():
    smd_dir = Path(r'C:\Users\FAVOUR\aiops-mvp\data\raw\smd')

    # Select 10 diverse machines/time periods
    machines = [
        'machine-1-1.txt',  # Machine 1, Period 1
        'machine-1-3.txt',  # Machine 1, Period 3
        'machine-1-5.txt',  # Machine 1, Period 5
        'machine-1-7.txt',  # Machine 1, Period 7
        'machine-2-2.txt',  # Machine 2, Period 2
        'machine-2-4.txt',  # Machine 2, Period 4
        'machine-2-6.txt',  # Machine 2, Period 6
        'machine-2-8.txt',  # Machine 2, Period 8
        'machine-3-3.txt',  # Machine 3, Period 3
        'machine-3-9.txt',  # Machine 3, Period 9
    ]

    print("=" * 80)
    print("LOADING DATA FROM 10 DIFFERENT MACHINES FOR COMPARISON")
    print("=" * 80)
    print(f"\nTarget: 200,000 rows (20,000 from each of 10 machines)")
    print(f"Data directory: {smd_dir}")

    # Verify files exist
    print("\n[INFO] Verifying files...")
    missing = []
    for machine in machines:
        filepath = smd_dir / machine
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024*1024)
            print(f"   [OK] {machine:20} ({size_mb:.1f} MB)")
        else:
            print(f"   [MISSING] {machine}")
            missing.append(machine)

    if missing:
        print(f"\n[ERROR] Missing {len(missing)} files:")
        for m in missing:
            print(f"   - {m}")
        print("\nAvailable machines:")
        available = list(smd_dir.glob('machine-*.txt'))
        for f in sorted(available)[:15]:
            print(f"   - {f.name}")
        sys.exit(1)

    # Load data from each machine
    print("\n" + "=" * 80)
    print("LOADING DATA")
    print("=" * 80)

    rows_per_machine = 20000
    total_rows = 0
    successful = 0

    for i, machine in enumerate(machines, 1):
        filepath = smd_dir / machine
        print(f"\n[{i}/10] Loading {machine}")

        if load_machine_data(str(filepath), rows_per_machine):
            total_rows += rows_per_machine
            successful += 1

        if i < len(machines):
            print(f"   --> Total so far: {total_rows:,} rows")

    # Summary
    print("\n" + "=" * 80)
    print("LOAD COMPLETE")
    print("=" * 80)
    print(f"\nSuccessfully loaded: {successful}/{len(machines)} machines")
    print(f"Total rows loaded: {total_rows:,}")
    print(f"\nMachines loaded:")
    for machine in machines[:successful]:
        print(f"  ✓ {machine}")

    print(f"\n[INFO] Dashboard URL: http://localhost:5000")
    print(f"[INFO] Refresh page to see new metrics")
    print(f"[INFO] Metrics update every 5 seconds")

if __name__ == '__main__':
    main()
