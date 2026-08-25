#!/usr/bin/env python3
"""
Data Loader - Loads real incident and response data from CSV files
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class DataLoader:
    """Load and manage real AIOps data from CSV files."""

    def __init__(self, data_dir='data/processed'):
        self.data_dir = data_dir
        self.incidents = []
        self.responses = []
        self.load_data()

    def load_data(self):
        """Load incident and response data from CSV files."""
        self.load_incidents()
        self.load_responses()
        self.enrich_incidents()

    def load_incidents(self):
        """Load incidents from incident_log.csv"""
        incident_file = os.path.join(self.data_dir, 'incident_log.csv')

        if not os.path.exists(incident_file):
            print(f"⚠️  Incident file not found: {incident_file}")
            return

        try:
            with open(incident_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    incident = {
                        'incident_id': row['incident_id'],
                        'timestamp': row['timestamp'],
                        'machine': row['machine'],
                        'issue_type': row['issue_type'],
                        'severity': row['severity'].upper(),
                        'confidence': float(row['confidence']),
                        'message': row['message'],
                        'status': 'active'  # Will be updated from responses
                    }
                    self.incidents.append(incident)

            print(f"✅ Loaded {len(self.incidents)} incidents")
        except Exception as e:
            print(f"❌ Error loading incidents: {e}")

    def load_responses(self):
        """Load responses from response_log.csv"""
        response_file = os.path.join(self.data_dir, 'response_log.csv')

        if not os.path.exists(response_file):
            print(f"⚠️  Response file not found: {response_file}")
            return

        try:
            with open(response_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    response = {
                        'incident_id': row['incident_id'],
                        'timestamp': row['timestamp'],
                        'action': row['action'],
                        'target': row['target'],
                        'status': row['status'],
                        'message': row['message'],
                        'simulated': row['simulated'] == 'True'
                    }
                    self.responses.append(response)

            print(f"✅ Loaded {len(self.responses)} responses")
        except Exception as e:
            print(f"❌ Error loading responses: {e}")

    def enrich_incidents(self):
        """Add response data to incidents."""
        response_map = {}
        for response in self.responses:
            incident_id = response['incident_id']
            if incident_id not in response_map:
                response_map[incident_id] = []
            response_map[incident_id].append(response)

        for incident in self.incidents:
            incident_id = incident['incident_id']
            if incident_id in response_map:
                incident['responses'] = response_map[incident_id]
                incident['status'] = response_map[incident_id][0]['status']
            else:
                incident['responses'] = []

    def get_all_incidents(self) -> List[Dict]:
        """Get all incidents."""
        return self.incidents

    def get_incident_by_id(self, incident_id: str) -> Dict:
        """Get specific incident by ID."""
        for incident in self.incidents:
            if incident['incident_id'] == incident_id:
                return incident
        return None

    def get_active_incidents(self) -> List[Dict]:
        """Get active incidents only."""
        return [inc for inc in self.incidents if inc['status'] in ['active', 'pending_review', 'in_progress']]

    def get_incidents_by_severity(self, severity: str) -> List[Dict]:
        """Get incidents by severity level."""
        return [inc for inc in self.incidents if inc['severity'] == severity.upper()]

    def get_incidents_by_machine(self, machine: str) -> List[Dict]:
        """Get incidents for a specific machine."""
        return [inc for inc in self.incidents if inc['machine'] == machine]

    def get_incidents_by_type(self, issue_type: str) -> List[Dict]:
        """Get incidents by type."""
        return [inc for inc in self.incidents if inc['issue_type'] == issue_type]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        active = self.get_active_incidents()

        severity_counts = {}
        issue_type_counts = {}

        for incident in self.incidents:
            severity = incident['severity']
            issue_type = incident['issue_type']

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1

        # Calculate resolution rate
        resolved = len([inc for inc in self.incidents if inc['status'] == 'resolved'])
        resolution_rate = (resolved / len(self.incidents) * 100) if self.incidents else 0

        # Calculate avg confidence for active incidents
        avg_confidence = 0
        if active:
            avg_confidence = sum(inc['confidence'] for inc in active) / len(active)

        return {
            'total_incidents': len(self.incidents),
            'active_incidents': len(active),
            'resolved_incidents': resolved,
            'resolution_rate': round(resolution_rate, 1),
            'avg_confidence': round(avg_confidence, 2),
            'severity_distribution': severity_counts,
            'issue_types': issue_type_counts,
            'machines_affected': len(set(inc['machine'] for inc in self.incidents))
        }

    def get_high_confidence_incidents(self, threshold: float = 0.7) -> List[Dict]:
        """Get high-confidence incidents."""
        return [inc for inc in self.incidents if inc['confidence'] >= threshold]

    def export_json(self) -> str:
        """Export all incidents as JSON."""
        return json.dumps(self.incidents, indent=2, default=str)


# Global data loader instance
_data_loader = None

def get_data_loader():
    """Get or create the global data loader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
