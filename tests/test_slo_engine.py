"""
Unit tests for SLO Engine and Compliance Calculator
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.slo_engine import (
    SLOEngine, ServiceLevelObjective, SLOMetric, SLOMetricType,
    SLOStatus, TimePeriod, SLOComplianceRecord
)
from src.slo_compliance import (
    MetricsCollector, ErrorBudgetTracker, SLOComplianceCalculator
)


class TestSLOMetric(unittest.TestCase):
    """Test SLOMetric conditions"""

    def test_less_than_condition(self):
        """Test < condition"""
        metric = SLOMetric(
            name="latency",
            metric_type=SLOMetricType.LATENCY,
            threshold=500.0,
            comparison="<",
            window=60
        )

        self.assertTrue(metric.check_condition(400.0))
        self.assertFalse(metric.check_condition(600.0))

    def test_greater_than_condition(self):
        """Test > condition"""
        metric = SLOMetric(
            name="availability",
            metric_type=SLOMetricType.AVAILABILITY,
            threshold=99.0,
            comparison=">",
            window=3600
        )

        self.assertTrue(metric.check_condition(99.5))
        self.assertFalse(metric.check_condition(98.5))

    def test_equal_condition(self):
        """Test == condition"""
        metric = SLOMetric(
            name="status",
            metric_type=SLOMetricType.CUSTOM,
            threshold=1.0,
            comparison="==",
            window=60
        )

        self.assertTrue(metric.check_condition(1.0))
        self.assertFalse(metric.check_condition(0.0))


class TestServiceLevelObjective(unittest.TestCase):
    """Test SLO definition and activation"""

    def setUp(self):
        """Create test SLO"""
        self.slo = ServiceLevelObjective(
            id="slo_1",
            service_id="api-gateway",
            service_name="API Gateway",
            description="API Gateway availability SLO",
            metrics=[
                SLOMetric(
                    name="availability",
                    metric_type=SLOMetricType.AVAILABILITY,
                    threshold=99.9,
                    comparison=">",
                    window=3600
                )
            ],
            target_percentage=99.9,
            tracking_period=TimePeriod.MONTHLY,
            period_start=datetime.utcnow() - timedelta(days=15),
            period_end=datetime.utcnow() + timedelta(days=15),
            enabled=True
        )

    def test_slo_is_active(self):
        """Test SLO activation check"""
        self.assertTrue(self.slo.is_active())

    def test_slo_inactive_when_disabled(self):
        """Test SLO is inactive when disabled"""
        self.slo.enabled = False
        self.assertFalse(self.slo.is_active())

    def test_days_remaining(self):
        """Test days remaining calculation"""
        days = self.slo.days_remaining()
        self.assertGreater(days, 0)
        self.assertLess(days, 31)

    def test_slo_to_dict(self):
        """Test SLO serialization"""
        slo_dict = self.slo.to_dict()

        self.assertEqual(slo_dict['id'], 'slo_1')
        self.assertEqual(slo_dict['service_name'], 'API Gateway')
        self.assertEqual(slo_dict['target_percentage'], 99.9)


class TestSLOEngine(unittest.TestCase):
    """Test SLO Engine core functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = SLOEngine()
        self.slo = ServiceLevelObjective(
            id="slo_test",
            service_id="test-service",
            service_name="Test Service",
            description="Test SLO",
            metrics=[],
            target_percentage=99.0,
            tracking_period=TimePeriod.DAILY,
            period_start=datetime.utcnow() - timedelta(hours=12),
            period_end=datetime.utcnow() + timedelta(hours=12),
            enabled=True
        )

    def test_add_slo(self):
        """Test adding an SLO"""
        result = self.engine.add_slo(self.slo)
        self.assertTrue(result)
        self.assertIn("slo_test", self.engine.slos)

    def test_add_duplicate_slo(self):
        """Test adding duplicate SLO fails"""
        self.engine.add_slo(self.slo)
        result = self.engine.add_slo(self.slo)
        self.assertFalse(result)

    def test_get_slo(self):
        """Test retrieving an SLO"""
        self.engine.add_slo(self.slo)
        retrieved = self.engine.get_slo("slo_test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "slo_test")

    def test_update_slo(self):
        """Test updating an SLO"""
        self.engine.add_slo(self.slo)
        updated = self.engine.update_slo(
            "slo_test",
            target_percentage=99.5
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.target_percentage, 99.5)

    def test_delete_slo(self):
        """Test deleting an SLO"""
        self.engine.add_slo(self.slo)
        result = self.engine.delete_slo("slo_test")
        self.assertTrue(result)
        self.assertNotIn("slo_test", self.engine.slos)

    def test_get_slos_by_service(self):
        """Test filtering SLOs by service"""
        self.engine.add_slo(self.slo)
        slos = self.engine.get_slos(service_id="test-service")
        self.assertEqual(len(slos), 1)

    def test_get_slos_enabled_only(self):
        """Test filtering enabled SLOs only"""
        self.engine.add_slo(self.slo)
        self.slo.enabled = False

        slos = self.engine.get_slos(enabled_only=True)
        self.assertEqual(len(slos), 0)


class TestComplianceCalculation(unittest.TestCase):
    """Test compliance calculation"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = SLOEngine()
        self.slo = ServiceLevelObjective(
            id="slo_compliance",
            service_id="api-gateway",
            service_name="API Gateway",
            description="Test SLO",
            metrics=[],
            target_percentage=99.0,
            tracking_period=TimePeriod.DAILY,
            period_start=datetime.utcnow() - timedelta(hours=12),
            period_end=datetime.utcnow() + timedelta(hours=12),
            enabled=True
        )
        self.engine.add_slo(self.slo)

    def test_calculate_compliance_healthy(self):
        """Test compliance calculation when healthy"""
        record = self.engine.calculate_compliance(
            slo_id="slo_compliance",
            errors_count=5,
            total_requests=1000,
            metric_values={}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.status, SLOStatus.HEALTHY)
        self.assertEqual(record.compliance_percentage, 99.5)

    def test_calculate_compliance_warning(self):
        """Test compliance calculation in warning state"""
        # 94.1% compliance (59 errors out of 1000)
        # This is between 94.05% (95% of 99%) and 99% target
        record = self.engine.calculate_compliance(
            slo_id="slo_compliance",
            errors_count=59,
            total_requests=1000,
            metric_values={}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.status, SLOStatus.WARNING)

    def test_calculate_compliance_violated(self):
        """Test compliance calculation when violated"""
        record = self.engine.calculate_compliance(
            slo_id="slo_compliance",
            errors_count=200,
            total_requests=1000,
            metric_values={}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.status, SLOStatus.VIOLATED)
        self.assertEqual(record.compliance_percentage, 80.0)


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection"""

    def setUp(self):
        """Set up test fixtures"""
        self.collector = MetricsCollector(window_size=3600)

    def test_record_metric(self):
        """Test recording a metric"""
        self.collector.record_metric("service1", "cpu_usage", 75.0)
        key = "service1_cpu_usage"
        self.assertIn(key, self.collector.metrics)
        self.assertEqual(len(self.collector.metrics[key]), 1)

    def test_record_request_success(self):
        """Test recording successful request"""
        self.collector.record_request("service1", 100.0, True)
        req = self.collector.requests["service1"]

        self.assertEqual(req['total'], 1)
        self.assertEqual(req['successful'], 1)
        self.assertEqual(req['failed'], 0)

    def test_record_request_failure(self):
        """Test recording failed request"""
        self.collector.record_request("service1", 100.0, False)
        req = self.collector.requests["service1"]

        self.assertEqual(req['total'], 1)
        self.assertEqual(req['failed'], 1)

    def test_get_availability(self):
        """Test availability calculation"""
        for i in range(100):
            self.collector.record_request("service1", 100.0, i % 10 != 0)

        availability = self.collector.get_availability("service1")
        self.assertAlmostEqual(availability, 90.0, places=0)

    def test_get_error_rate(self):
        """Test error rate calculation"""
        for i in range(100):
            self.collector.record_request("service1", 100.0, i % 10 != 0)

        error_rate = self.collector.get_error_rate("service1")
        self.assertAlmostEqual(error_rate, 10.0, places=0)

    def test_get_percentile(self):
        """Test percentile calculation"""
        for latency in range(0, 1000, 10):
            self.collector.record_request("service1", float(latency), True)

        p95 = self.collector.get_percentile("service1", 95)
        self.assertIsNotNone(p95)
        self.assertGreater(p95, 900)


class TestErrorBudgetTracker(unittest.TestCase):
    """Test error budget tracking"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = ErrorBudgetTracker()
        # 1 day period, 99% SLO = 14.4 minutes error budget
        self.tracker.initialize_budget("slo_1", 86400, 99.0)

    def test_initialize_budget(self):
        """Test budget initialization"""
        budget = self.tracker.get_budget_status("slo_1")

        self.assertIn('slo_1', self.tracker.budgets)
        self.assertEqual(budget['total_budget'], 864.0)  # ~14.4 minutes

    def test_consume_budget(self):
        """Test consuming error budget"""
        status = self.tracker.consume_budget("slo_1", 432.0)  # Half the budget

        self.assertEqual(status['consumed_percentage'], 50.0)
        self.assertEqual(status['remaining_budget'], 432.0)

    def test_budget_depletion_warning(self):
        """Test budget depletion detection"""
        # Consume 80% of budget
        self.tracker.consume_budget("slo_1", 691.2)
        status = self.tracker.get_budget_status("slo_1")

        self.assertGreater(status['consumed_percentage'], 75)


class TestComplianceCalculator(unittest.TestCase):
    """Test compliance calculation utilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = SLOComplianceCalculator()
        self.slo = ServiceLevelObjective(
            id="slo_calc",
            service_id="test-service",
            service_name="Test Service",
            description="Test",
            metrics=[
                SLOMetric(
                    name="latency",
                    metric_type=SLOMetricType.LATENCY,
                    threshold=500.0,
                    comparison="<",
                    window=60
                )
            ],
            target_percentage=99.0,
            tracking_period=TimePeriod.DAILY,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=1),
            enabled=True
        )

    def test_evaluate_slo_compliant(self):
        """Test SLO evaluation when compliant"""
        result = self.calculator.evaluate_slo(
            self.slo,
            {'latency': 400.0}
        )

        self.assertTrue(result['overall_compliance'])
        self.assertEqual(len(result['issues']), 0)

    def test_evaluate_slo_non_compliant(self):
        """Test SLO evaluation when non-compliant"""
        result = self.calculator.evaluate_slo(
            self.slo,
            {'latency': 600.0}
        )

        self.assertFalse(result['overall_compliance'])
        self.assertGreater(len(result['issues']), 0)


if __name__ == '__main__':
    unittest.main()
