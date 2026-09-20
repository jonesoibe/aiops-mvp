#!/usr/bin/env python3
"""
Generate sample SMD (Server Machine Dataset) data for testing and deployment.
This script creates synthetic machine monitoring data when the data directory is empty.
"""

import os
import random
import csv
from pathlib import Path


def generate_smd_sample(machine_id: str, num_rows: int = 1000) -> list:
    """Generate synthetic SMD data for a machine."""
    data = []

    # 38 features in SMD dataset
    num_features = 38

    for _ in range(num_rows):
        # Generate realistic metric values (0-1 normalized range)
        row = []
        for feat_idx in range(num_features):
            # Vary values based on feature index for realism
            if feat_idx < 10:
                # CPU-like metrics (0-1)
                value = random.gauss(0.3, 0.2)
            elif feat_idx < 20:
                # Memory-like metrics
                value = random.gauss(0.4, 0.15)
            elif feat_idx < 30:
                # Disk/IO metrics
                value = random.gauss(0.2, 0.1)
            else:
                # Network metrics
                value = random.gauss(0.15, 0.1)

            # Clamp to [0, 1]
            value = max(0, min(1, value))
            row.append(f"{value:.6f}")

        data.append(row)

    return data


def create_sample_data(data_dir: str = "data/raw/smd", num_machines: int = 10):
    """Create sample SMD data files for testing."""
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    machines = []

    # Create multiple machines with different names
    for machine_num in range(1, num_machines + 1):
        # Machine-1-1, Machine-1-2, etc.
        machine_id = f"machine-{(machine_num // 5) + 1}-{(machine_num % 5) + 1}"
        machines.append(machine_id)

        filepath = os.path.join(data_dir, f"{machine_id}.txt")

        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"✓ {machine_id} already exists, skipping")
            continue

        print(f"Generating {machine_id}...")

        # Generate data (fewer rows for demo - 5000 instead of 100k+)
        data = generate_smd_sample(machine_id, num_rows=5000)

        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)

        print(f"  Created: {filepath} ({len(data)} rows)")

    print(f"\n✅ Sample data generated for {len(machines)} machines")
    return machines


if __name__ == "__main__":
    # Check if data directory is empty
    data_dir = "data/raw/smd"

    if os.path.exists(data_dir) and os.listdir(data_dir):
        print(f"Data directory '{data_dir}' already populated, skipping generation")
    else:
        print(f"Data directory empty, generating sample data...")
        create_sample_data(data_dir, num_machines=10)
