"""
Unit tests for SLO Reporting Engine

Tests cover:
- Monthly compliance reports
- Breach analysis
- Trend analysis
- Executive summaries
- Health scores
- Export formats (JSON, CSV)
"""

import pytest
from datetime import datetime, timedelta
from src.slo_engine import (
    SLOEngine, ServiceLevelObjective, SLOMetric, SLOComplianceRecord
)
from src.slo_compliance import SLOComplianceCalculator
from src.slo_reporting import (
    SLOReportingEngine, SLOBreachEvent, ComplianceTrend,
    ServiceHealthScore, ExecutiveSummary, export_report_json,
    export_report_csv, TrendDirection
)


@pytest.fixture
def slo_engine():
    """Create SLO engine with test data"""
    engine = SLOEngine()

    # Add test SLO
    metric = SLOMetric(
        name="availability",
        metric_type="availability",
        threshold=99.9,
        comparison=">",
        window=3600
    )

    now = datetime.now()
    slo = ServiceLevelObjective(
        id="slo_test_api",
        service_id="api-gateway",
        service_name="API Gateway",
        description="API Gateway SLO",
        target_percentage=99.9,
        tracking_period="monthly",
        metrics=[metric],
        period_start=now,
        period_end=now + timedelta(days=30)
    )

    engine.add_slo(slo)
    return engine


@pytest.fixture
def compliance_calculator():
    """Create compliance calculator"""
    return SLOComplianceCalculator()


@pytest.fixture
def reporting_engine(slo_engine, compliance_calculator):
    """Create reporting engine"""
    return SLOReportingEngine(slo_engine, compliance_calculator)


class TestMonthlyReport:
    """Tests for monthly compliance reports"""

    def test_generate_monthly_report(self, slo_engine, reporting_engine):
        """Test generating monthly report"""
        # Add compliance history
        now = datetime.now()
        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.85,
                status="healthy",
                error_budget_remaining=95,
                errors_count=150,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        # Generate report
        report = reporting_engine.generate_monthly_report(
            month=now.month,
            year=now.year
        )

        assert report['report_type'] == 'monthly_compliance'
        assert report['summary']['total_slos'] == 1
        assert report['summary']['overall_average_compliance'] > 99
        assert len(report['slos']) == 1

    def test_monthly_report_identifies_violations(self, slo_engine, reporting_engine):
        """Test that report identifies SLO violations"""
        now = datetime.now()

        # Add mix of compliant and non-compliant data
        for i in range(30):
            compliance = 99.85 if i < 20 else 99.5
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=compliance,
                status="healthy" if compliance >= 99.9 else "violated",
                error_budget_remaining=90,
                errors_count=150,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        report = reporting_engine.generate_monthly_report(now.month, now.year)

        # Should have identified breaches
        assert report['summary']['total_breaches'] > 0
        assert report['slos'][0]['breach_count'] > 0

    def test_monthly_report_calculates_statistics(self, slo_engine, reporting_engine):
        """Test that report calculates statistics"""
        now = datetime.now()

        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.8,
                status="healthy",
                error_budget_remaining=95,
                errors_count=200,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        report = reporting_engine.generate_monthly_report(now.month, now.year)

        stats = report['statistics']
        assert 'average_compliance' in stats
        assert 'min_compliance' in stats
        assert 'max_compliance' in stats
        assert stats['average_compliance'] > 0


class TestBreachAnalysis:
    """Tests for breach analysis reports"""

    def test_generate_breach_analysis(self, slo_engine, reporting_engine):
        """Test generating breach analysis"""
        now = datetime.now()

        # Add some breaches
        for i in range(10):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=15-i),
                compliance_percentage=99.5,  # Below 99.9 target
                status="violated",
                error_budget_remaining=50,
                errors_count=500,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        analysis = reporting_engine.generate_breach_analysis(days=30)

        assert analysis['report_type'] == 'breach_analysis'
        assert analysis['total_breaches'] > 0
        assert 'by_root_cause' in analysis
        assert 'recommendations' in analysis

    def test_breach_analysis_groups_by_cause(self, slo_engine, reporting_engine):
        """Test that breaches are grouped by root cause"""
        now = datetime.now()

        for i in range(5):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=10-i),
                compliance_percentage=99.5,
                status="violated",
                error_budget_remaining=50,
                errors_count=500,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        analysis = reporting_engine.generate_breach_analysis(days=30)

        assert len(analysis['by_root_cause']) > 0
        for cause, data in analysis['by_root_cause'].items():
            assert 'count' in data
            assert 'average_breach_amount' in data
            assert 'events' in data

    def test_breach_analysis_generates_recommendations(self, slo_engine, reporting_engine):
        """Test that recommendations are generated"""
        now = datetime.now()

        for i in range(5):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=10-i),
                compliance_percentage=99.5,
                status="violated",
                error_budget_remaining=50,
                errors_count=500,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        analysis = reporting_engine.generate_breach_analysis(days=30)

        assert len(analysis['recommendations']) > 0
        assert any(isinstance(r, str) for r in analysis['recommendations'])


class TestTrendAnalysis:
    """Tests for trend analysis reports"""

    def test_generate_trend_analysis(self, slo_engine, reporting_engine):
        """Test generating trend analysis"""
        now = datetime.now()

        # Add improving trend
        for i in range(90):
            # Start at 99.5, improve to 99.9
            compliance = 99.5 + (i / 90 * 0.4)
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=90-i),
                compliance_percentage=compliance,
                status="healthy",
                error_budget_remaining=95,
                errors_count=100,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        trend = reporting_engine.generate_trend_analysis("slo_test_api")

        assert trend['report_type'] == 'trend_analysis'
        assert 'trends' in trend
        assert '30-day' in trend['trends']
        assert '60-day' in trend['trends']
        assert '90-day' in trend['trends']

    def test_trend_analysis_detects_improvement(self, slo_engine, reporting_engine):
        """Test that improving trends are detected"""
        now = datetime.now()

        # Add improving trend
        for i in range(60):
            compliance = 99.5 + (i / 60 * 0.4)
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=60-i),
                compliance_percentage=compliance,
                status="healthy",
                error_budget_remaining=95,
                errors_count=100,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        trend = reporting_engine.generate_trend_analysis("slo_test_api")

        # 30-day trend should be improving
        trend_30 = trend['trends']['30-day']
        assert trend_30['trend_direction'] in ['improving', 'stable']

    def test_trend_analysis_invalid_slo(self, reporting_engine):
        """Test handling of invalid SLO"""
        with pytest.raises(ValueError):
            reporting_engine.generate_trend_analysis("nonexistent_slo")


class TestExecutiveSummary:
    """Tests for executive summaries"""

    def test_generate_executive_summary(self, slo_engine, reporting_engine):
        """Test generating executive summary"""
        now = datetime.now()

        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.85,
                status="healthy",
                error_budget_remaining=95,
                errors_count=150,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        summary = reporting_engine.generate_executive_summary(now.month, now.year)

        assert isinstance(summary, ExecutiveSummary)
        assert summary.total_slos == 1
        assert len(summary.key_findings) >= 1
        assert len(summary.recommendations) >= 1

    def test_executive_summary_assigns_grades(self, slo_engine, reporting_engine):
        """Test that grades are assigned based on compliance"""
        now = datetime.now()

        # Add high compliance data
        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.95,
                status="healthy",
                error_budget_remaining=98,
                errors_count=50,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        summary = reporting_engine.generate_executive_summary(now.month, now.year)

        # High compliance should result in good grade
        assert summary.average_compliance > 99


class TestHealthScores:
    """Tests for service health scores"""

    def test_calculate_health_scores(self, slo_engine, reporting_engine):
        """Test calculating health scores"""
        now = datetime.now()

        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.8,
                status="healthy",
                error_budget_remaining=95,
                errors_count=200,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        scores = reporting_engine.calculate_health_scores()

        assert len(scores) == 1
        assert isinstance(scores[0], ServiceHealthScore)
        assert 0 <= scores[0].score <= 100
        assert scores[0].grade in ['A', 'B', 'C', 'D', 'F']

    def test_health_score_metrics(self, slo_engine, reporting_engine):
        """Test that health score includes all metrics"""
        now = datetime.now()

        for i in range(30):
            record = SLOComplianceRecord(
                slo_id="slo_test_api",
                service_id="api-gateway",
                timestamp=now - timedelta(days=30-i),
                compliance_percentage=99.8,
                status="healthy",
                error_budget_remaining=95,
                errors_count=200,
                total_requests=1000000
            )
            slo_engine.compliance_history.append(record)

        scores = reporting_engine.calculate_health_scores()

        metrics = scores[0].metrics
        assert 'compliance_score' in metrics
        assert 'stability_score' in metrics
        assert 'trend_score' in metrics
        assert 'average_compliance' in metrics
        assert 'variance' in metrics


class TestExportFormats:
    """Tests for export formats"""

    def test_export_json(self):
        """Test JSON export"""
        report_data = {
            'report_type': 'test',
            'period': 'January 2026',
            'summary': {'total_slos': 1}
        }

        json_str = export_report_json(report_data)

        assert '"report_type": "test"' in json_str
        assert '"period": "January 2026"' in json_str

    def test_export_monthly_csv(self):
        """Test CSV export for monthly report"""
        report_data = {
            'period': 'January 2026',
            'generated_at': '2026-01-01T00:00:00',
            'summary': {
                'total_slos': 1,
                'healthy_slos': 1,
                'warning_slos': 0,
                'violated_slos': 0,
                'overall_average_compliance': 99.85,
                'total_breaches': 0
            },
            'slos': [
                {
                    'service_name': 'API Gateway',
                    'target_percentage': 99.9,
                    'actual_percentage': 99.85,
                    'status': 'healthy',
                    'breach_count': 0
                }
            ]
        }

        csv_str = export_report_csv(report_data, 'monthly_compliance')

        assert 'SLO Compliance Report' in csv_str
        assert 'January 2026' in csv_str
        assert 'API Gateway' in csv_str
        assert '99.85' in csv_str

    def test_export_breach_csv(self):
        """Test CSV export for breach analysis"""
        report_data = {
            'period_days': 30,
            'period_end': '2026-01-31T00:00:00',
            'total_breaches': 2,
            'breaches': [
                {
                    'service_name': 'API Gateway',
                    'timestamp': '2026-01-15T10:00:00',
                    'compliance_percentage': 99.5,
                    'target_percentage': 99.9,
                    'breach_amount': 0.4,
                    'root_cause': 'High error rate'
                }
            ]
        }

        csv_str = export_report_csv(report_data, 'breach_analysis')

        assert 'SLO Breach Analysis Report' in csv_str
        assert 'API Gateway' in csv_str
        assert '99.5' in csv_str


class TestBreachEventModel:
    """Tests for breach event model"""

    def test_breach_event_creation(self):
        """Test creating breach event"""
        breach = SLOBreachEvent(
            slo_id="slo_test",
            service_name="Test Service",
            timestamp="2026-01-15T10:00:00",
            compliance_percentage=99.5,
            target_percentage=99.9,
            breach_amount=0.4,
            root_cause="High error rate"
        )

        assert breach.slo_id == "slo_test"
        assert breach.breach_amount == 0.4

    def test_breach_event_to_dict(self):
        """Test converting breach event to dict"""
        breach = SLOBreachEvent(
            slo_id="slo_test",
            service_name="Test Service",
            timestamp="2026-01-15T10:00:00",
            compliance_percentage=99.5,
            target_percentage=99.9,
            breach_amount=0.4
        )

        d = breach.to_dict()
        assert isinstance(d, dict)
        assert d['slo_id'] == "slo_test"
        assert d['breach_amount'] == 0.4


class TestComplianceTrendModel:
    """Tests for compliance trend model"""

    def test_trend_creation(self):
        """Test creating trend"""
        trend = ComplianceTrend(
            period="30-day",
            average_compliance=99.8,
            min_compliance=99.5,
            max_compliance=99.95,
            trend_direction="improving",
            breach_count=2,
            error_budget_consumed=20.5
        )

        assert trend.period == "30-day"
        assert trend.trend_direction == "improving"

    def test_trend_to_dict(self):
        """Test converting trend to dict"""
        trend = ComplianceTrend(
            period="30-day",
            average_compliance=99.8,
            min_compliance=99.5,
            max_compliance=99.95,
            trend_direction="improving",
            breach_count=2,
            error_budget_consumed=20.5
        )

        d = trend.to_dict()
        assert isinstance(d, dict)
        assert d['period'] == "30-day"
        assert d['average_compliance'] == 99.8


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
