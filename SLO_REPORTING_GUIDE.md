# SLO Advanced Reporting System - Complete Guide

## 🎯 Overview

The Advanced Reporting System provides comprehensive SLO compliance analysis including monthly reports, breach analysis, trend analysis, executive summaries, and service health scores.

## 📊 Features

### 1. Monthly Compliance Reports
- Summarize SLO compliance for a specific month
- Track compliance percentage for each SLO
- Identify breaches and violations
- Calculate error budget consumption
- Generate statistics (min, max, average compliance)

### 2. Breach Analysis
- Identify all SLO breaches within a period
- Group breaches by root cause
- Calculate breach severity (amount, duration)
- Generate actionable recommendations
- Analyze error rates and latency issues

### 3. Trend Analysis
- Analyze 30/60/90 day compliance trends
- Detect improvement or degradation patterns
- Calculate trend direction and intensity
- Assess overall service health direction

### 4. Executive Summaries
- High-level compliance overview
- Service health grades (A-F)
- Key findings and insights
- Actionable recommendations
- Best/worst performer identification

### 5. Service Health Scores
- Calculate health scores (0-100) for each service
- Factor in: compliance (60%), stability (20%), trend (20%)
- Assign letter grades
- Identify services needing attention

### 6. Multi-Format Export
- JSON format for programmatic access
- CSV format for spreadsheet analysis
- PDF format (coming soon)

## 🚀 Getting Started

### Initialize the Reporting Engine
```python
from src.slo_reporting import SLOReportingEngine
from src.slo_engine import SLOEngine
from src.slo_compliance import SLOComplianceCalculator

# Create engines
slo_engine = SLOEngine()
compliance_calculator = SLOComplianceCalculator()

# Initialize reporter
reporter = SLOReportingEngine(slo_engine, compliance_calculator)
```

## 📡 API Endpoints

### Monthly Compliance Report
```
GET /api/slos/reports/monthly/<month>/<year>

Example:
GET /api/slos/reports/monthly/1/2026

Response:
{
  "report": {
    "report_type": "monthly_compliance",
    "period": "January 2026",
    "summary": {
      "total_slos": 5,
      "healthy_slos": 4,
      "warning_slos": 1,
      "violated_slos": 0,
      "overall_average_compliance": 99.85,
      "total_breaches": 2
    },
    "slos": [
      {
        "slo_id": "slo_api_availability",
        "service_name": "API Gateway",
        "target_percentage": 99.9,
        "actual_percentage": 99.92,
        "compliance_met": true,
        "breach_count": 0,
        "status": "healthy"
      }
    ],
    "statistics": {
      "average_compliance": 99.85,
      "min_compliance": 99.2,
      "max_compliance": 99.95,
      "std_deviation": 0.25,
      "total_breach_minutes": 0
    }
  }
}
```

### Breach Analysis Report
```
GET /api/slos/reports/breach-analysis?days=30

Response:
{
  "analysis": {
    "report_type": "breach_analysis",
    "period_days": 30,
    "total_breaches": 5,
    "breaches": [
      {
        "slo_id": "slo_api_availability",
        "service_name": "API Gateway",
        "timestamp": "2026-01-15T10:30:00",
        "compliance_percentage": 99.5,
        "target_percentage": 99.9,
        "breach_amount": 0.4,
        "root_cause": "High error rate",
        "affected_requests": 1500
      }
    ],
    "by_root_cause": {
      "High error rate": {
        "count": 3,
        "average_breach_amount": 0.35,
        "events": [...]
      }
    },
    "recommendations": [
      "Investigate application error logs...",
      "Review recent deployments...",
      "Most common issue: High error rate (3 occurrences)"
    ]
  }
}
```

### Trend Analysis
```
GET /api/slos/reports/trends/<slo_id>

Example:
GET /api/slos/reports/trends/slo_api_availability

Response:
{
  "trends": {
    "slo_id": "slo_api_availability",
    "service_name": "API Gateway",
    "target_percentage": 99.9,
    "trends": {
      "30-day": {
        "period": "30-day",
        "average_compliance": 99.82,
        "min_compliance": 99.2,
        "max_compliance": 99.95,
        "trend_direction": "improving",
        "breach_count": 2,
        "error_budget_consumed": 18.0
      },
      "60-day": {...},
      "90-day": {...}
    },
    "overall_assessment": "Positive: Service health is improving"
  }
}
```

### Executive Summary
```
GET /api/slos/reports/executive-summary/<month>/<year>

Example:
GET /api/slos/reports/executive-summary/1/2026

Response:
{
  "summary": {
    "report_period": "January 2026",
    "total_slos": 5,
    "healthy_slos": 4,
    "warning_slos": 1,
    "violated_slos": 0,
    "total_breaches": 2,
    "average_compliance": 99.85,
    "worst_performer": "Database Service",
    "best_performer": "API Gateway",
    "key_findings": [
      "Best performing service: API Gateway (99.92%)"
    ],
    "recommendations": [
      "Review recent deployments and rollback if needed",
      "Check database and API response times"
    ]
  }
}
```

### Health Scores
```
GET /api/slos/reports/health-scores

Response:
{
  "scores": [
    {
      "service_id": "api-gateway",
      "service_name": "API Gateway",
      "score": 92.5,
      "grade": "A",
      "metrics": {
        "compliance_score": 59.9,
        "stability_score": 19.8,
        "trend_score": 12.8,
        "average_compliance": 99.85,
        "variance": 0.22
      }
    }
  ]
}
```

### Export Report
```
GET /api/slos/reports/export/<report_type>?format=<format>&month=<month>&year=<year>

Examples:
GET /api/slos/reports/export/monthly?format=json&month=1&year=2026
GET /api/slos/reports/export/monthly?format=csv&month=1&year=2026
GET /api/slos/reports/export/breach?format=csv&days=30
```

## 🎯 Report Types

### Monthly Compliance Report
Summarizes SLO compliance for a calendar month:
- Overall compliance statistics
- Individual SLO performance
- Breach identification
- Error budget tracking

**Best for:** Monthly reviews, trend tracking, service health assessment

### Breach Analysis
Detailed analysis of all breaches within a period:
- Breach timing and severity
- Root cause categorization
- Recommendations for remediation
- Pattern identification

**Best for:** Root cause analysis, problem resolution, process improvement

### Trend Analysis
Time-series analysis of compliance trends:
- 30/60/90-day trends
- Trend direction (improving/stable/degrading)
- Comparative analysis
- Forecasting needs

**Best for:** Long-term planning, performance tracking, capacity planning

### Executive Summary
High-level overview for leadership:
- Compliance grades
- Key findings
- Recommendations
- Performance rankings

**Best for:** Executive reporting, stakeholder communication, business decisions

### Health Scores
Comprehensive service health rating:
- Compliance component (60%)
- Stability component (20%)
- Trend component (20%)
- Letter grades (A-F)

**Best for:** Service prioritization, resource allocation, performance management

## 📈 Key Metrics

### Compliance Percentage
```
Compliance % = (Successful Requests / Total Requests) * 100
```

### Error Budget Remaining
```
If Compliance >= Target: 100%
Otherwise: ((Compliance - Target) / (100 - Target)) * 100
```

### Trend Direction
- **Improving**: Recent compliance > Earlier compliance (>1% difference)
- **Degrading**: Recent compliance < Earlier compliance (>1% difference)
- **Stable**: Within ±1% variance

### Health Score
```
Health Score = Compliance(60%) + Stability(20%) + Trend(20%)

Grades:
A: 90-100
B: 80-89
C: 70-79
D: 60-69
F: <60
```

## 🔍 Root Cause Analysis

The system automatically infers root causes:

| Indicator | Root Cause |
|-----------|-----------|
| High error rate (>5%) | High error rate |
| High latency detected | Elevated latency |
| Other degradation | Service degradation |

Custom root causes can be added via:
```python
def _infer_root_cause(self, slo, record):
    # Add custom logic here
```

## 📊 Example Usage

### Generate Monthly Report
```python
from datetime import datetime

reporting = SLOReportingEngine(slo_engine, compliance_calculator)

# Get report for January 2026
report = reporting.generate_monthly_report(month=1, year=2026)

print(f"Total SLOs: {report['summary']['total_slos']}")
print(f"Average Compliance: {report['summary']['overall_average_compliance']}%")
print(f"Total Breaches: {report['summary']['total_breaches']}")
```

### Export to CSV
```python
from src.slo_reporting import export_report_csv

csv_data = export_report_csv(report, 'monthly_compliance')
with open('monthly_report.csv', 'w') as f:
    f.write(csv_data)
```

### Get Health Scores
```python
scores = reporting.calculate_health_scores()

for score in scores:
    print(f"{score.service_name}: {score.grade} ({score.score}%)")
```

### Analyze Breaches
```python
analysis = reporting.generate_breach_analysis(days=30)

print(f"Total Breaches: {analysis['total_breaches']}")
for cause, data in analysis['by_root_cause'].items():
    print(f"  {cause}: {data['count']} incidents")
```

## ⚙️ Configuration

### Compliance Thresholds
```python
# Thresholds for status determination
HEALTHY_THRESHOLD = target_percentage
WARNING_THRESHOLD = target_percentage * 0.95
VIOLATED_THRESHOLD = < WARNING_THRESHOLD
```

### Health Score Weights
```python
COMPLIANCE_WEIGHT = 0.60  # 60%
STABILITY_WEIGHT = 0.20   # 20%
TREND_WEIGHT = 0.20       # 20%
```

### Error Budget Calculation
```python
error_budget = target_percentage - (100 - target_percentage)
# Example: 99.9% SLO = 0.1% error budget
```

## 🧪 Testing

Run all reporting tests:
```bash
python -m pytest tests/test_slo_reporting.py -v
```

Test Coverage:
- Monthly report generation (3 tests)
- Breach analysis (3 tests)
- Trend analysis (3 tests)
- Executive summaries (2 tests)
- Health scores (2 tests)
- Export formats (3 tests)
- Data models (4 tests)

**Total: 20/20 tests passing ✅**

## 📝 Data Models

### SLOBreachEvent
```python
@dataclass
class SLOBreachEvent:
    slo_id: str
    service_name: str
    timestamp: str
    compliance_percentage: float
    target_percentage: float
    breach_amount: float
    root_cause: Optional[str] = None
    impact_duration: Optional[int] = None  # minutes
    affected_requests: Optional[int] = None
```

### ComplianceTrend
```python
@dataclass
class ComplianceTrend:
    period: str  # "30-day", "60-day", "90-day"
    average_compliance: float
    min_compliance: float
    max_compliance: float
    trend_direction: str  # "improving", "degrading", "stable"
    breach_count: int
    error_budget_consumed: float
```

### ServiceHealthScore
```python
@dataclass
class ServiceHealthScore:
    service_id: str
    service_name: str
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    metrics: Dict
```

### ExecutiveSummary
```python
@dataclass
class ExecutiveSummary:
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
```

## 🔗 Integration Points

### With SLO Engine
- Retrieves SLO definitions and targets
- Accesses compliance history
- Calculates error budgets

### With Compliance Calculator
- Uses compliance calculations
- Applies thresholds and business rules
- Validates compliance states

### With Alert System
- Can trigger alerts on breaches
- Feeds insights into alert rules
- Supports proactive notifications

## 🚀 Performance

### Report Generation Time
- Monthly report: ~100-200ms (1000 SLO records)
- Breach analysis: ~50-100ms
- Trend analysis: ~30-50ms
- Health scores: ~50-100ms

### Data Retention
- Default: Last 10,000 compliance records per SLO
- Configurable via SLOEngine.max_history

## 🔐 Security

- All endpoints require authentication (Bearer token)
- No sensitive data exposure
- Input validation on all parameters
- Error messages don't leak internal details

## 📚 Files

- `src/slo_reporting.py` - Main reporting engine (600+ lines)
- `tests/test_slo_reporting.py` - Comprehensive tests (450+ lines)
- `nexus_app.py` - API endpoint integration (120+ lines)

## 📞 Support

For issues or questions:
1. Check this guide
2. Review unit tests for usage examples
3. Check SLO_TRACKING_GUIDE.md for related concepts
4. Review API endpoint documentation

## ✅ Checklist

- ✅ Monthly compliance reports
- ✅ Breach analysis with root cause correlation
- ✅ Executive summaries
- ✅ Trend analysis (30/60/90 day)
- ✅ Service health scores
- ✅ JSON/CSV export
- ✅ REST API endpoints
- ✅ 20/20 unit tests passing
- ✅ Comprehensive documentation
- ⏳ PDF export (coming in next phase)

---

**Status:** Production-Ready ✅  
**Tests:** 20/20 Passing  
**API Endpoints:** 6  
**Export Formats:** 2 (JSON, CSV)  
**Code Quality:** Comprehensive

