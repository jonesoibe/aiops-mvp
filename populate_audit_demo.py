#!/usr/bin/env python3
"""
Populate audit trail with demo data for testing
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_logger import audit_logger

def populate_demo_audit_data():
    """Populate audit trail with demo entries"""

    print("🔄 Populating audit trail with demo data...")

    # Demo users
    users = ['admin', 'operator', 'viewer', 'analyst']

    # Demo actions
    actions = [
        ('LOGIN', 'authentication', 'success'),
        ('CREATE', 'detection_rule', 'success'),
        ('UPDATE', 'detection_rule', 'success'),
        ('DELETE', 'incident', 'success'),
        ('REMEDIATE', 'incident', 'success'),
        ('REMEDIATE', 'incident', 'failure'),
        ('VIEW', 'dashboard', 'success'),
        ('EXPORT', 'audit_log', 'success'),
        ('LOGOUT', 'authentication', 'success'),
        ('LOGIN', 'authentication', 'failure'),
        ('CREATE', 'playbook', 'success'),
        ('UPDATE', 'playbook', 'success'),
        ('VIEW', 'incident', 'success'),
    ]

    # Generate entries for the last 2 hours
    now = datetime.utcnow()

    entry_count = 0
    for hour_offset in range(0, 120, 10):  # Every 10 minutes
        for user in users:
            for action, resource, status in actions:
                timestamp = now - timedelta(minutes=hour_offset)

                audit_logger.log_action(
                    action=action,
                    user_id=user,
                    resource=resource,
                    status=status,
                    details={
                        'resource_name': f'{resource}_{entry_count}',
                        'severity': 'high' if status == 'failure' else 'info',
                        'duration_ms': 250 + (entry_count % 500)
                    },
                    ip_address=f'192.168.1.{100 + (entry_count % 100)}',
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                entry_count += 1

                # Limit entries to avoid too much data
                if entry_count >= 100:
                    break
            if entry_count >= 100:
                break
        if entry_count >= 100:
            break

    print(f"✅ Created {entry_count} demo audit entries")
    print(f"✅ Sample entries added to in-memory audit trail")

    # Display summary
    entries = audit_logger.get_recent_audit_entries(limit=10)
    print(f"\n📊 Latest 10 audit entries:")
    for i, entry in enumerate(entries, 1):
        print(f"  {i}. [{entry['status'].upper()}] {entry['action']} by {entry['user_id']} on {entry['resource']}")

if __name__ == '__main__':
    populate_demo_audit_data()
    print("\n✅ Audit trail demo data populated successfully!")
    print("🌐 Open http://localhost:5000/audit to view the audit trail")
