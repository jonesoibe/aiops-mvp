#!/usr/bin/env python3
"""
Load SMD (Server Machine Dataset) files into MongoDB for persistent storage.
Run this once locally to populate MongoDB with machine data.
"""

import os
import csv
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('MONGODB_DATABASE', 'nexus_aiops')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'smd')


def load_smd_files_to_mongodb():
    """Load all SMD files from disk into MongoDB."""

    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

    db = client[DATABASE_NAME]
    machines_collection = db['machines']
    machine_data_collection = db['machine_data']

    if not os.path.isdir(DATA_DIR):
        print(f"❌ Data directory not found: {DATA_DIR}")
        return False

    smd_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.txt')])

    if not smd_files:
        print(f"❌ No SMD files found in {DATA_DIR}")
        return False

    print(f"Found {len(smd_files)} SMD files. Starting upload...\n")

    for filename in smd_files:
        filepath = os.path.join(DATA_DIR, filename)
        machine_id = filename.replace('.txt', '')

        # Check if machine already exists
        existing = machines_collection.find_one({'machine_id': machine_id})
        if existing:
            print(f"ℹ️  {machine_id} already in MongoDB, skipping...")
            continue

        try:
            # Get file size
            file_size = os.path.getsize(filepath)

            # Read data
            data_rows = []
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for row_num, row in enumerate(reader):
                    data_rows.append({
                        'machine_id': machine_id,
                        'row_num': row_num,
                        'values': [float(v) for v in row]
                    })

            print(f"Loading {machine_id} ({len(data_rows)} rows)...")

            # Insert machine metadata
            machines_collection.insert_one({
                'machine_id': machine_id,
                'label': machine_id.replace('-', ' ').title(),
                'filename': filename,
                'file_size': file_size,
                'num_rows': len(data_rows),
                'created_at': None,
                'status': 'active'
            })

            # Insert machine data
            if data_rows:
                machine_data_collection.insert_many(data_rows)

            print(f"  ✅ Uploaded {machine_id}")

        except Exception as e:
            print(f"  ❌ Error uploading {machine_id}: {e}")
            continue

    print(f"\n✅ All machines loaded to MongoDB!")
    print(f"   Collection: {DATABASE_NAME}.machines")
    print(f"   Data Collection: {DATABASE_NAME}.machine_data")

    # Create indexes for performance
    print("\nCreating indexes...")
    machines_collection.create_index('machine_id', unique=True)
    machine_data_collection.create_index('machine_id')
    machine_data_collection.create_index([('machine_id', 1), ('row_num', 1)])
    print("✅ Indexes created")

    client.close()
    return True


if __name__ == "__main__":
    print("Loading SMD files to MongoDB...\n")
    success = load_smd_files_to_mongodb()
    if success:
        print("\n🎉 Data loading complete!")
    else:
        print("\n⚠️  Data loading failed")
