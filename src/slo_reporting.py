"""
SLO Compliance Reporting Engine

Generates comprehensive SLO compliance reports with:
- Monthly compliance summaries
- Breach analysis with root cause correlation
- Executive summaries with KPIs
- Trend analysis (30/60/90 day)
- Service-level health scores
- Multi-format export (PDF, CSV, JSON)
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from statistics import mean, stdev


class TrendDirection(Enum):
    """Trend direction indicator"""
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"


class ReportFormat(Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"


@dataclass
class SLOBreachEvent:
    """Represents an SLO breach event"""
    slo_id: str
    service_name: str
    timestamp: str
    compliance_percentage: float
    target_percentage: float
    breach_amount: float
    root_cause: Optional[str] = None
    impact_duration: Optional[int] = None  # minutes
    affected_requests: Optional[int] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ComplianceTrend:
    """Represents compliance trend over time"""
    period: str  # "30-day", "60-day", "90-day"
    average_compliance: float
    min_compliance: float
    max_compliance: float
    trend_direction: str
    breach_count: int
    error_budget_consumed: float

    def to_dict(self):
        return asdict(self)


@dataclass
class ServiceHealthScore:
    """Overall service health score"""
    service_id: str
    service_name: str
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    metrics: Dict

    def to_dict(self):
        return asdict(self)


@dataclass
class ExecutiveSummary:
    """Executive summary for reports"""
    report_period: str
    total_slos: int
    healthy_slos: int
    warning_slos: int
    violated_slos: int
    total_breaches: int
    average_compliance: float
    worst_performer: str
    best_performer: str
    key_findings: List[str]
    recommendations: List[str]

    def to_dict(self):
        return asdict(self)


class SLOReportingEngine:
    """Core SLO reporting engine"""

    def __init__(self, slo_engine, compliance_calculator):
        """
        Initialize reporting engine

        Args:
            slo_engine: SLOEngine instance
            compliance_calculator: SLOComplianceCalculator instance
        """
        self.slo_engine = slo_engine
        self.compliance_calculator = compliance_calculator

    def generate_monthly_report(self, month: int, year: int) -> Dict:
        """
        Generate monthly compliance report

        Args:
            month: Month number (1-12)
            year: Year

        Returns:
            Dictionary containing monthly report data
        """
        period_start = datetime(year, month, 1)

        # Calculate period end (first day of next month)
        if month == 12:
            period_end = datetime(year + 1, 1, 1)
        else:
            period_end = datetime(year, month + 1, 1)

        period_label = period_start.strftime("%B %Y")

        # Get all SLOs
        slos = self.slo_engine.get_slos()

        # Collect compliance data for each SLO
        slo_data = []
        total_compliance = []

        for slo in slos:
            compliance_history = self.slo_engine.get_compliance_history(
                slo.id,
                hours=int((period_end - period_start).total_seconds() / 3600)
            )

            if compliance_history:
                # Calculate average compliance for period
                compliances = [record.compliance_percentage for record in compliance_history]
                avg_compliance = mean(compliances) if compliances else 0
                total_compliance.append(avg_compliance)

                # Identify breaches
                breaches = [r for r in compliance_history if r.compliance_percentage < slo.target_percentage]

                slo_data.append({
                    'slo_id': slo.id,
                    'service_id': slo.service_id,
                    'service_name': slo.service_name,
                    'target_percentage': slo.target_percentage,
                    'actual_percentage': avg_compliance,
                    'compliance_met': avg_compliance >= slo.target_percentage,
                    'breach_count': len(breaches),
                    'breach_duration_minutes': sum([
                        (compliance_history[i+1].timestamp - record.timestamp).total_seconds() / 60
                        for i, record in enumerate(breaches[:-1])
                    ]) if len(breaches) > 1 else 0,
                    'error_budget_remaining': self._calculate_error_budget_remaining(slo, compliance_history),
                    'status': self._get_compliance_status(avg_compliance, slo.target_percentage)
                })

        # Calculate overall metrics
        overall_average = mean(total_compliance) if total_compliance else 0
        healthy_count = sum(1 for s in slo_data if s['compliance_met'])
        warning_count = sum(1 for s in slo_data if not s['compliance_met'] and s['actual_percentage'] >= slo.target_percentage * 0.95)
        violated_count = sum(1 for s in slo_data if s['actual_percentage'] < slo.target_percentage * 0.95)

        return {
            'report_type': 'monthly_compliance',
            'period': period_label,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_slos': len(slos),
                'healthy_slos': healthy_count,
                'warning_slos': warning_count,
                'violated_slos': violated_count,
                'overall_average_compliance': round(overall_average, 2),
                'total_breaches': sum(s['breach_count'] for s in slo_data),
            },
            'slos': slo_data,
            'statistics': self._calculate_statistics(slo_data)
        }

    def generate_breach_analysis(self, days: int = 30) -> Dict:
        """
        Generate breach analysis with root cause correlation

        Args:
            days: Number of days to analyze

        Returns:
            Breach analysis report
        """
        period_start = datetime.now() - timedelta(days=days)

        # Collect all breaches
        breaches = []
        slos = self.slo_engine.get_slos()

        for slo in slos:
            compliance_history = self.slo_engine.get_compliance_history(slo.id, hours=days*24)

            for record in compliance_history:
                if record.compliance_percentage < slo.target_percentage:
                    breach = SLOBreachEvent(
                        slo_id=slo.id,
                        service_name=slo.service_name,
                        timestamp=record.timestamp.isoformat(),
                        compliance_percentage=record.compliance_percentage,
                        target_percentage=slo.target_percentage,
                        breach_amount=slo.target_percentage - record.compliance_percentage,
                        root_cause=self._infer_root_cause(slo, record),
                        affected_requests=getattr(record, 'total_requests', None)
                    )
                    breaches.append(breach)

        # Sort by severity (breach amount)
        breaches.sort(key=lambda b: b.breach_amount, reverse=True)

        # Group by root cause
        by_cause = {}
        for breach in breaches:
            cause = breach.root_cause or "Unknown"
            if cause not in by_cause:
                by_cause[cause] = []
            by_cause[cause].append(breach)

        return {
            'report_type': 'breach_analysis',
            'period_days': days,
            'period_start': period_start.isoformat(),
            'period_end': datetime.now().isoformat(),
            'total_breaches': len(breaches),
            'breaches': [b.to_dict() for b in breaches[:50]],  # Top 50
            'by_root_cause': {
                cause: {
                    'count': len(events),
                    'average_breach_amount': round(mean([e.breach_amount for e in events]), 2),
                    'events': [e.to_dict() for e in events[:5]]  # Top 5 per cause
                }
                for cause, events in by_cause.items()
            },
            'recommendations': self._generate_breach_recommendations(breaches)
        }

    def generate_trend_analysis(self, slo_id: str) -> Dict:
        """
        Generate trend analysis for specific SLO

        Args:
            slo_id: SLO ID

        Returns:
            Trend analysis report
        """
        slo = self.slo_engine.get_slo(slo_id)
        if not slo:
            raise ValueError(f"SLO {slo_id} not found")

        trends = {}

        # Analyze 30, 60, 90 day trends
        for days in [30, 60, 90]:
            compliance_history = self.slo_engine.get_compliance_history(slo_id, hours=days*24)

            if compliance_history:
                compliances = [r.compliance_percentage for r in compliance_history]
                breaches = [r for r in compliance_history if r.compliance_percentage < slo.target_percentage]

                # Calculate trend direction
                if len(compliances) > 1:
                    first_half = mean(compliances[:len(compliances)//2])
                    second_half = mean(compliances[len(compliances)//2:])

                    if second_half > first_half + 1:
                        direction = TrendDirection.IMPROVING.value
                    elif second_half < first_half - 1:
                        direction = TrendDirection.DEGRADING.value
                    else:
                        direction = TrendDirection.STABLE.value
                else:
                    direction = TrendDirection.STABLE.value

                trend = ComplianceTrend(
                    period=f"{days}-day",
                    average_compliance=round(mean(compliances), 2),
                    min_compliance=round(min(compliances), 2),
                    max_compliance=round(max(compliances), 2),
                    trend_direction=direction,
                    breach_count=len(breaches),
                    error_budget_consumed=round(
                        (slo.target_percentage - mean(compliances)) / (100 - slo.target_percentage) * 100
                        if slo.target_percentage < 100 else 0,
                        2
                    )
                )
                trends[f"{days}-day"] = trend.to_dict()

        return {
            'report_type': 'trend_analysis',
            'slo_id': slo_id,
            'service_name': slo.service_name,
            'target_percentage': slo.target_percentage,
            'trends': trends,
            'overall_assessment': self._assess_trend(trends)
        }

    def generate_executive_summary(self, month: int, year: int) -> ExecutiveSummary:
        """
        Generate executive summary for month

        Args:
            month: Month number (1-12)
            year: Year

        Returns:
            ExecutiveSummary object
        """
        monthly_report = self.generate_monthly_report(month, year)
        summary_data = monthly_report['summary']
        slo_data = monthly_report['slos']

        # Find best and worst performers
        best = max(slo_data, key=lambda s: s['actual_percentage']) if slo_data else None
        worst = min(slo_data, key=lambda s: s['actual_percentage']) if slo_data else None

        key_findings = []
        recommendations = []

        # Generate findings
        if summary_data['violated_slos'] > 0:
            key_findings.append(
                f"{summary_data['violated_slos']} SLO(s) failed to meet target during this period"
            )
            recommendations.append("Review and investigate root causes of SLO violations")

        if summary_data['total_breaches'] > 10:
            key_findings.append(
                f"High number of breaches ({summary_data['total_breaches']}) detected"
            )
            recommendations.append("Implement additional monitoring and alerting for critical services")

        if best:
            key_findings.append(
                f"Best performing service: {best['service_name']} ({best['actual_percentage']}%)"
            )

        # Calculate grade
        if summary_data['overall_average_compliance'] >= 99.9:
            overall_grade = "A"
        elif summary_data['overall_average_compliance'] >= 99:
            overall_grade = "B"
        elif summary_data['overall_average_compliance'] >= 98:
            overall_grade = "C"
        elif summary_data['overall_average_compliance'] >= 95:
            overall_grade = "D"
        else:
            overall_grade = "F"

        period_label = datetime(year, month, 1).strftime("%B %Y")

        return ExecutiveSummary(
            report_period=period_label,
            total_slos=summary_data['total_slos'],
            healthy_slos=summary_data['healthy_slos'],
            warning_slos=summary_data['warning_slos'],
            violated_slos=summary_data['violated_slos'],
            total_breaches=summary_data['total_breaches'],
            average_compliance=summary_data['overall_average_compliance'],
            worst_performer=worst['service_name'] if worst else "N/A",
            best_performer=best['service_name'] if best else "N/A",
            key_findings=key_findings,
            recommendations=recommendations
        )

    def calculate_health_scores(self) -> List[ServiceHealthScore]:
        """
        Calculate health scores for all services

        Returns:
            List of ServiceHealthScore objects
        """
        slos = self.slo_engine.get_slos()
        scores = []

        for slo in slos:
            # Get last 30 days compliance
            compliance_history = self.slo_engine.get_compliance_history(slo.id, hours=30*24)

            if compliance_history:
                compliances = [r.compliance_percentage for r in compliance_history]
                avg = mean(compliances)

                # Calculate health score (0-100)
                # Weight: compliance (60%), stability (20%), trend (20%)
                compliance_score = min(avg, 100) / 100 * 60

                # Stability score (low variance is good)
                std = stdev(compliances) if len(compliances) > 1 else 0
                stability_score = max(0, (20 - std)) / 20 * 20

                # Trend score (improving is good)
                if len(compliances) > 1:
                    recent = mean(compliances[-len(compliances)//3:])
                    older = mean(compliances[:len(compliances)//3])
                    trend_score = min(20, max(-20, (recent - older) / 2)) + 20
                else:
                    trend_score = 10

                health_score = compliance_score + stability_score + trend_score

                # Convert to grade
                if health_score >= 90:
                    grade = "A"
                elif health_score >= 80:
                    grade = "B"
                elif health_score >= 70:
                    grade = "C"
                elif health_score >= 60:
                    grade = "D"
                else:
                    grade = "F"

                score = ServiceHealthScore(
                    service_id=slo.service_id,
                    service_name=slo.service_name,
                    score=round(health_score, 1),
                    grade=grade,
                    metrics={
                        'compliance_score': round(compliance_score, 1),
                        'stability_score': round(stability_score, 1),
                        'trend_score': round(trend_score, 1),
                        'average_compliance': round(avg, 2),
                        'variance': round(std, 2)
                    }
                )
                scores.append(score)

        # Sort by score (descending)
        scores.sort(key=lambda s: s.score, reverse=True)

        return scores

    # Helper methods
    def _calculate_error_budget_remaining(self, slo, compliance_history):
        """Calculate remaining error budget"""
        if not compliance_history:
            return 100

        avg_compliance = mean([r.compliance_percentage for r in compliance_history])
        target = slo.target_percentage

        if avg_compliance >= target:
            return 100

        # Error budget is: (target - actual) / (100 - target) * 100
        if target >= 100:
            return 0

        remaining = ((avg_compliance - target) / (100 - target)) * 100
        return max(0, min(100, remaining))

    def _get_compliance_status(self, actual, target):
        """Get compliance status"""
        if actual >= target:
            return "healthy"
        elif actual >= target * 0.95:
            return "warning"
        else:
            return "violated"

    def _calculate_statistics(self, slo_data):
        """Calculate additional statistics"""
        if not slo_data:
            return {}

        compliances = [s['actual_percentage'] for s in slo_data]

        return {
            'average_compliance': round(mean(compliances), 2),
            'min_compliance': round(min(compliances), 2),
            'max_compliance': round(max(compliances), 2),
            'std_deviation': round(stdev(compliances), 2) if len(compliances) > 1 else 0,
            'total_breach_minutes': sum(s['breach_duration_minutes'] for s in slo_data)
        }

    def _infer_root_cause(self, slo, record):
        """Infer likely root cause of breach"""
        # Simple heuristic - can be enhanced with ML
        error_rate = getattr(record, 'errors_count', 0) / max(1, getattr(record, 'total_requests', 1)) * 100

        if error_rate > 5:
            return "High error rate"
        elif getattr(record, 'high_latency', False):
            return "Elevated latency"
        else:
            return "Service degradation"

    def _generate_breach_recommendations(self, breaches):
        """Generate recommendations based on breaches"""
        recommendations = []

        if not breaches:
            return ["Continue monitoring SLOs as they are performing well"]

        # Most common cause
        causes = {}
        for breach in breaches:
            cause = breach.root_cause or "Unknown"
            causes[cause] = causes.get(cause, 0) + 1

        top_cause = max(causes, key=causes.get)

        if "error rate" in top_cause.lower():
            recommendations.append("Investigate application error logs and error rates")
            recommendations.append("Review recent deployments and rollback if needed")
        elif "latency" in top_cause.lower():
            recommendations.append("Check database and API response times")
            recommendations.append("Review resource utilization and scaling policies")
        else:
            recommendations.append("Review service dependency health")

        recommendations.append(f"Most common issue: {top_cause} ({causes[top_cause]} occurrences)")

        return recommendations

    def _assess_trend(self, trends):
        """Assess overall trend"""
        if not trends:
            return "No trend data available"

        # Look at 30-day trend
        trend_30 = trends.get('30-day', {})
        direction = trend_30.get('trend_direction', 'stable')

        if direction == 'improving':
            return "Positive: Service health is improving"
        elif direction == 'degrading':
            return "Negative: Service health is degrading - immediate action recommended"
        else:
            return "Neutral: Service health is stable"


def export_report_json(report_data: Dict) -> str:
    """Export report as JSON"""
    return json.dumps(report_data, indent=2, default=str)


def export_report_csv(report_data: Dict, report_type: str) -> str:
    """Export report as CSV"""
    if report_type == 'monthly_compliance':
        return _export_monthly_csv(report_data)
    elif report_type == 'breach_analysis':
        return _export_breach_csv(report_data)
    else:
        return ""


def _export_monthly_csv(report_data: Dict) -> str:
    """Export monthly report as CSV"""
    lines = [
        f"SLO Compliance Report - {report_data['period']}",
        f"Generated: {report_data['generated_at']}",
        ""
    ]

    # Summary section
    summary = report_data['summary']
    lines.append("SUMMARY")
    lines.append(f"Total SLOs,{summary['total_slos']}")
    lines.append(f"Healthy,{summary['healthy_slos']}")
    lines.append(f"Warning,{summary['warning_slos']}")
    lines.append(f"Violated,{summary['violated_slos']}")
    lines.append(f"Overall Average Compliance,{summary['overall_average_compliance']}%")
    lines.append(f"Total Breaches,{summary['total_breaches']}")
    lines.append("")

    # SLO Details
    lines.append("SLO DETAILS")
    lines.append("Service,Target %,Actual %,Status,Breaches,Error Budget %")

    for slo in report_data['slos']:
        lines.append(
            f"{slo['service_name']},{slo['target_percentage']},"
            f"{slo['actual_percentage']},{slo['status']},{slo['breach_count']},0"
        )

    return "\n".join(lines)


def _export_breach_csv(report_data: Dict) -> str:
    """Export breach analysis as CSV"""
    lines = [
        f"SLO Breach Analysis Report - {report_data['period_days']} Days",
        f"Generated: {report_data.get('period_end', 'N/A')}",
        ""
    ]

    lines.append(f"Total Breaches,{report_data['total_breaches']}")
    lines.append("")

    lines.append("BREACH DETAILS")
    lines.append("Service,Timestamp,Compliance %,Target %,Breach Amount,Root Cause")

    for breach in report_data.get('breaches', [])[:100]:
        lines.append(
            f"{breach['service_name']},{breach['timestamp']},"
            f"{breach['compliance_percentage']},{breach['target_percentage']},"
            f"{breach['breach_amount']},{breach.get('root_cause', 'Unknown')}"
        )

    return "\n".join(lines)
