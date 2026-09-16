#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insert demo users directly into MongoDB Atlas
"""

import sys
import os

# Fix Windows encoding issue
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pymongo import MongoClient
from datetime import datetime
import bcrypt

# MongoDB connection
MONGODB_URI = "mongodb+srv://aiops_user:admin123@altschool.m511v.mongodb.net/?appName=AltSchool"
DATABASE_NAME = "nexus_aiops"

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def insert_demo_users():
    """Insert demo users into MongoDB"""

    try:
        print("\n" + "="*70)
        print("  📝 Inserting Demo Users into MongoDB Atlas")
        print("="*70 + "\n")

        # Connect to MongoDB
        print("🔄 Connecting to MongoDB...")
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            retryWrites=True
        )

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB\n")

        db = client[DATABASE_NAME]
        users_collection = db['users']

        # Demo users
        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@nexus.local',
                'first_name': 'Admin',
                'last_name': 'User',
                'password_hash': hash_password('admin123'),
                'role': 'admin',
                'department': 'Administration',
                'created_at': datetime.utcnow().isoformat(),
                'verified': True,
                'verified_at': datetime.utcnow().isoformat(),
                'last_login': None
            },
            {
                'username': 'operator',
                'email': 'operator@nexus.local',
                'first_name': 'Operator',
                'last_name': 'User',
                'password_hash': hash_password('operator123'),
                'role': 'operator',
                'department': 'Operations',
                'created_at': datetime.utcnow().isoformat(),
                'verified': True,
                'verified_at': datetime.utcnow().isoformat(),
                'last_login': None
            },
            {
                'username': 'viewer',
                'email': 'viewer@nexus.local',
                'first_name': 'Viewer',
                'last_name': 'User',
                'password_hash': hash_password('viewer123'),
                'role': 'viewer',
                'department': 'Reporting',
                'created_at': datetime.utcnow().isoformat(),
                'verified': True,
                'verified_at': datetime.utcnow().isoformat(),
                'last_login': None
            }
        ]

        # Insert users
        inserted_count = 0
        for user in demo_users:
            try:
                # Use update_one with upsert to avoid duplicates
                result = users_collection.update_one(
                    {'username': user['username']},
                    {'$set': user},
                    upsert=True
                )

                if result.upserted_id:
                    print(f"✅ Created: {user['username']} ({user['email']})")
                    inserted_count += 1
                elif result.modified_count > 0:
                    print(f"🔄 Updated: {user['username']} ({user['email']})")
                else:
                    print(f"ℹ️  Exists: {user['username']} ({user['email']})")

            except Exception as e:
                print(f"❌ Error inserting {user['username']}: {str(e)}")

        # Verify
        total_users = users_collection.count_documents({})

        print(f"\n{'='*70}")
        print(f"  📊 Summary")
        print(f"{'='*70}")
        print(f"  Total users in MongoDB: {total_users}")
        print(f"{'='*70}\n")

        # List all users
        print("📋 Users in database:")
        for user in users_collection.find({}, {'username': 1, 'email': 1, 'role': 1}):
            print(f"   • {user['username']:15} | {user['email']:25} | {user['role']}")

        print("\n✅ Demo users inserted successfully!\n")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        return False

if __name__ == '__main__':
    insert_demo_users()
