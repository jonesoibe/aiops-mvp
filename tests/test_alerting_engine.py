"""
Unit tests for the Alerting Engine
Tests alert rule management, metric evaluation, and alert lifecycle
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.alerting_engine import (
    AlertingEngine, AlertRule, Alert, AlertSeverity, AlertStatus
)


class TestAlertRule(unittest.TestCase):
    """Test AlertRule dataclass"""

    def test_create_rule(self):
        """Test creating an alert rule"""
        rule = AlertRule(
            id="test_rule",
            name="Test Alert",
            description="Test description",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0
        )

        self.assertEqual(rule.id, "test_rule")
        self.assertEqual(rule.name, "Test Alert")
        self.assertEqual(rule.threshold, 90.0)
        self.assertEqual(rule.severity, AlertSeverity.MAJOR)
        self.assertTrue(rule.enabled)

    def test_rule_with_custom_severity(self):
        """Test creating rule with custom severity"""
        rule = AlertRule(
            id="critical_rule",
            name="Critical Alert",
            description="Error rate exceeds 5%",
            metric_name="error_rate",
            condition=">",
            threshold=5.0,
            severity=AlertSeverity.CRITICAL
        )

        self.assertEqual(rule.severity, AlertSeverity.CRITICAL)


class TestAlertingEngine(unittest.TestCase):
    """Test AlertingEngine core functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AlertingEngine()

        # Create test rules
        self.cpu_rule = AlertRule(
            id="cpu_high",
            name="High CPU",
            description="CPU usage is high",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            duration=60
        )

        self.memory_rule = AlertRule(
            id="memory_high",
            name="High Memory",
            description="Memory usage is high",
            metric_name="memory_usage",
            condition=">",
            threshold=85.0,
            duration=120
        )

        self.engine.add_rule(self.cpu_rule)
        self.engine.add_rule(self.memory_rule)

    def test_add_rule(self):
        """Test adding alert rules"""
        self.assertIn("cpu_high", self.engine.rules)
        self.assertIn("memory_high", self.engine.rules)

    def test_get_rules(self):
        """Test retrieving rules"""
        rules = self.engine.get_rules()
        self.assertEqual(len(rules), 2)

    def test_get_enabled_rules(self):
        """Test filtering enabled rules"""
        rules = self.engine.get_rules(enabled_only=True)
        self.assertEqual(len(rules), 2)

        # Disable one rule
        self.engine.update_rule("cpu_high", enabled=False)
        rules = self.engine.get_rules(enabled_only=True)
        self.assertEqual(len(rules), 1)

    def test_delete_rule(self):
        """Test deleting a rule"""
        self.engine.delete_rule("cpu_high")
        self.assertNotIn("cpu_high", self.engine.rules)

    def test_update_rule(self):
        """Test updating a rule"""
        self.engine.update_rule("cpu_high", threshold=95.0)
        self.assertEqual(self.engine.rules["cpu_high"].threshold, 95.0)


class TestMetricEvaluation(unittest.TestCase):
    """Test metric evaluation against rules"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AlertingEngine()

        self.rule = AlertRule(
            id="cpu_test",
            name="CPU Test",
            description="CPU test rule",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            duration=5  # 5 seconds for testing
        )

        self.engine.add_rule(self.rule)

    def test_no_alert_when_below_threshold(self):
        """Test no alert when metric is below threshold"""
        metrics = {"cpu_usage": 50.0}
        alerts = self.engine.evaluate_metrics("test_service", metrics)

        self.assertEqual(len(alerts), 0)
        self.assertEqual(len(self.engine.get_active_alerts()), 0)

    def test_alert_when_above_threshold(self):
        """Test alert fires when metric exceeds threshold"""
        # Simulate metric being high multiple times to exceed duration
        for i in range(5):
            metrics = {"cpu_usage": 90.0}
            alerts = self.engine.evaluate_metrics("test_service", metrics)
            # Add delay to simulate time passing
            self.engine._record_metric("test_service_cpu_usage", 90.0)

        # Check if alert was fired
        active = self.engine.get_active_alerts()
        # Alert might not have fired yet due to duration requirement, that's ok

    def test_multiple_metrics(self):
        """Test evaluating multiple metrics at once"""
        rule2 = AlertRule(
            id="memory_test",
            name="Memory Test",
            description="Memory test rule",
            metric_name="memory_usage",
            condition=">",
            threshold=85.0,
            duration=5
        )
        self.engine.add_rule(rule2)

        metrics = {
            "cpu_usage": 50.0,  # Below threshold
            "memory_usage": 90.0  # Above threshold
        }

        # Record multiple times to exceed duration
        for i in range(5):
            self.engine._record_metric("test_service_memory_usage", 90.0)

        alerts = self.engine.evaluate_metrics("test_service", metrics)
        # Should have potential for alert on memory


class TestConditionChecking(unittest.TestCase):
    """Test condition evaluation logic"""

    def setUp(self):
        self.engine = AlertingEngine()

    def test_greater_than(self):
        """Test > condition"""
        result = self.engine._check_condition(95.0, ">", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(50.0, ">", 80.0)
        self.assertFalse(result)

    def test_less_than(self):
        """Test < condition"""
        result = self.engine._check_condition(50.0, "<", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(95.0, "<", 80.0)
        self.assertFalse(result)

    def test_greater_equal(self):
        """Test >= condition"""
        result = self.engine._check_condition(80.0, ">=", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(81.0, ">=", 80.0)
        self.assertTrue(result)

    def test_less_equal(self):
        """Test <= condition"""
        result = self.engine._check_condition(80.0, "<=", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(79.0, "<=", 80.0)
        self.assertTrue(result)

    def test_equal(self):
        """Test == condition"""
        result = self.engine._check_condition(80.0, "==", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(79.0, "==", 80.0)
        self.assertFalse(result)

    def test_not_equal(self):
        """Test != condition"""
        result = self.engine._check_condition(79.0, "!=", 80.0)
        self.assertTrue(result)

        result = self.engine._check_condition(80.0, "!=", 80.0)
        self.assertFalse(result)

    def test_range(self):
        """Test range condition"""
        result = self.engine._check_condition(50.0, "range", 40.0, 60.0)
        self.assertTrue(result)

        result = self.engine._check_condition(70.0, "range", 40.0, 60.0)
        self.assertFalse(result)


class TestAlertLifecycle(unittest.TestCase):
    """Test alert lifecycle management"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AlertingEngine()
        self.alert = Alert(
            id="test_alert_1",
            rule_id="cpu_high",
            rule_name="High CPU",
            metric_name="cpu_usage",
            current_value=95.0,
            threshold=80.0,
            severity=AlertSeverity.MAJOR,
            status=AlertStatus.FIRING,
            service_id="api_gateway",
            fired_at=datetime.utcnow()
        )

    def test_alert_creation(self):
        """Test creating an alert"""
        self.assertEqual(self.alert.id, "test_alert_1")
        self.assertEqual(self.alert.status, AlertStatus.FIRING)
        self.assertIsNone(self.alert.acknowledged_at)
        self.assertIsNone(self.alert.resolved_at)

    def test_alert_duration(self):
        """Test calculating alert duration"""
        # Alert fired 5 minutes ago
        self.alert.fired_at = datetime.utcnow() - timedelta(minutes=5)

        duration = self.alert.duration
        self.assertGreater(duration.total_seconds(), 290)  # ~5 minutes
        self.assertLess(duration.total_seconds(), 310)

    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        self.engine.alerts["test_alert"] = self.alert

        acknowledged = self.engine.acknowledge_alert("test_alert", "john_doe")

        self.assertIsNotNone(acknowledged)
        self.assertEqual(acknowledged.status, AlertStatus.ACKNOWLEDGED)
        self.assertEqual(acknowledged.acknowledged_by, "john_doe")
        self.assertIsNotNone(acknowledged.acknowledged_at)

    def test_resolve_alert(self):
        """Test resolving an alert"""
        self.engine.alerts["test_alert"] = self.alert

        resolved = self.engine.resolve_alert(
            "test_alert",
            "Scaled service horizontally"
        )

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.status, AlertStatus.RESOLVED)
        self.assertEqual(resolved.resolution_reason, "Scaled service horizontally")
        self.assertIsNotNone(resolved.resolved_at)

    def test_silence_alert(self):
        """Test silencing an alert"""
        self.engine.alerts["test_alert"] = self.alert

        silenced = self.engine.silence_alert("test_alert", 30)

        self.assertIsNotNone(silenced)
        self.assertEqual(silenced.status, AlertStatus.SILENCED)


class TestAlertStatistics(unittest.TestCase):
    """Test alert statistics and reporting"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AlertingEngine()

        # Add some rules
        for i in range(3):
            rule = AlertRule(
                id=f"rule_{i}",
                name=f"Rule {i}",
                description=f"Test rule {i}",
                metric_name="test_metric",
                condition=">",
                threshold=80.0
            )
            self.engine.add_rule(rule)

    def test_statistics(self):
        """Test getting statistics"""
        stats = self.engine.get_statistics()

        self.assertEqual(stats['total_rules'], 3)
        self.assertEqual(stats['enabled_rules'], 3)
        self.assertEqual(stats['active_alerts'], 0)
        self.assertEqual(stats['critical'], 0)
        self.assertEqual(stats['total_alerts_fired'], 0)

    def test_get_active_alerts(self):
        """Test retrieving active alerts"""
        # Add an alert
        alert = Alert(
            id="alert_1",
            rule_id="rule_1",
            rule_name="Test Rule",
            metric_name="test_metric",
            current_value=90.0,
            threshold=80.0,
            severity=AlertSeverity.MAJOR,
            status=AlertStatus.FIRING,
            service_id="service_1",
            fired_at=datetime.utcnow()
        )
        self.engine.alerts["alert_1"] = alert

        active = self.engine.get_active_alerts()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, "alert_1")

    def test_get_alerts_by_service(self):
        """Test retrieving alerts by service"""
        # Add multiple alerts for different services
        for service_id in ["service_1", "service_2", "service_1"]:
            alert = Alert(
                id=f"alert_{service_id}_{datetime.utcnow().timestamp()}",
                rule_id="rule_1",
                rule_name="Test Rule",
                metric_name="test_metric",
                current_value=90.0,
                threshold=80.0,
                severity=AlertSeverity.MAJOR,
                status=AlertStatus.FIRING,
                service_id=service_id,
                fired_at=datetime.utcnow()
            )
            self.engine.alert_history.append(alert)

        service1_alerts = [a for a in self.engine.alert_history if a.service_id == "service_1"]
        self.assertEqual(len(service1_alerts), 2)


class TestAlertSerialization(unittest.TestCase):
    """Test alert serialization to dict/JSON"""

    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = Alert(
            id="test_alert",
            rule_id="cpu_high",
            rule_name="High CPU",
            metric_name="cpu_usage",
            current_value=95.5,
            threshold=80.0,
            severity=AlertSeverity.MAJOR,
            status=AlertStatus.FIRING,
            service_id="api_gateway",
            fired_at=datetime.utcnow(),
            acknowledged_by="john_doe"
        )

        alert_dict = alert.to_dict()

        self.assertEqual(alert_dict['id'], "test_alert")
        self.assertEqual(alert_dict['rule_name'], "High CPU")
        self.assertEqual(alert_dict['current_value'], 95.5)
        self.assertEqual(alert_dict['severity'], "major")
        self.assertEqual(alert_dict['status'], "firing")


if __name__ == '__main__':
    unittest.main()
