"""
ClaimLinc AI Rejection Analyzer
Provides AI-driven analysis of claim rejections using pattern recognition,
root cause analysis, and corrective action recommendations
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from dataclasses import dataclass
import statistics


@dataclass
class AnalysisInsight:
    """AI analysis insight"""
    title: str
    severity: str
    affected_claims: int
    potential_impact: float  # Amount at risk
    root_cause: str
    recommendation: str
    confidence_score: float  # 0-1
    data_points: List[Dict[str, Any]]


class RejectionAnalyzer:
    """AI-driven analysis of claim rejections"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.rules = self._initialize_rules()

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rejection patterns and rules"""
        return {
            "invalid_member": {
                "keywords": ["invalid member", "member not found", "membership expired", "no active"],
                "root_causes": ["Outdated patient records", "Incorrect member ID entry", "Enrollment data mismatch"],
                "actions": ["Verify member eligibility in payer system", "Update patient records", "Check enrollment status"]
            },
            "missing_authorization": {
                "keywords": ["authorization", "pre-auth", "pre-approval", "auth required"],
                "root_causes": ["Missing pre-authorization", "Expired authorization", "Wrong service authorized"],
                "actions": ["Obtain pre-authorization from payer", "Verify authorization dates", "Resubmit with auth number"]
            },
            "duplicate_claim": {
                "keywords": ["duplicate", "already submitted", "already processed"],
                "root_causes": ["Claim submitted twice", "System error resubmission", "Batch processing error"],
                "actions": ["Check original claim status", "Do not resubmit", "Contact payer to investigate"]
            },
            "incomplete_documentation": {
                "keywords": ["incomplete", "missing", "invoice", "documentation", "attachment"],
                "root_causes": ["Missing supporting documents", "Incomplete claim form", "Missing medical records"],
                "actions": ["Gather required documentation", "Attach missing invoices/receipts", "Complete claim form details"]
            },
            "service_not_covered": {
                "keywords": ["not covered", "excluded", "not in scope", "not allowed"],
                "root_causes": ["Service excluded from plan", "Patient age restrictions", "Benefit limits exceeded"],
                "actions": ["Review patient's plan coverage", "Check exclusions", "Consider alternative covered services"]
            },
            "invalid_date": {
                "keywords": ["invalid date", "outside", "expired", "not effective", "date range"],
                "root_causes": ["Service date before/after policy effective", "Past filing limit exceeded", "Admission date invalid"],
                "actions": ["Verify service dates", "Check policy effective dates", "Contact payer for date clarification"]
            },
            "out_of_network": {
                "keywords": ["out of network", "non-network", "network provider", "contracted"],
                "root_causes": ["Provider not in network", "Network changed", "Wrong facility used"],
                "actions": ["Verify network status", "Check patient's network options", "Route to in-network provider"]
            },
            "exceeds_limit": {
                "keywords": ["exceeds", "limit", "maximum", "annual", "aggregate"],
                "root_causes": ["Annual limit reached", "Deductible not met", "Co-pay threshold exceeded"],
                "actions": ["Check patient's remaining benefits", "Verify coverage limits", "Calculate actual patient responsibility"]
            }
        }

    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Initialize analysis rules"""
        return [
            {
                "name": "member_id_errors",
                "description": "Multiple invalid member ID errors from same provider",
                "threshold": 5,
                "window_days": 30,
                "metric": "rejection_count"
            },
            {
                "name": "duplicate_claims",
                "description": "Potential duplicate claim submissions",
                "threshold": 2,
                "window_days": 7,
                "metric": "same_claim_amount"
            },
            {
                "name": "missing_auth_pattern",
                "description": "Systematic missing authorization issues",
                "threshold": 3,
                "window_days": 60,
                "metric": "rejection_count"
            },
            {
                "name": "documentation_gaps",
                "description": "Consistent incomplete documentation",
                "threshold": 4,
                "window_days": 30,
                "metric": "rejection_count"
            }
        ]

    def analyze_rejections(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis on rejection records

        Args:
            records: List of rejection record dictionaries

        Returns:
            Comprehensive analysis results
        """
        analysis = {
            "summary": self._generate_summary(records),
            "insights": self._generate_insights(records),
            "patterns": self._identify_patterns(records),
            "predictions": self._generate_predictions(records),
            "recommendations": self._generate_recommendations(records),
            "branch_analysis": self._analyze_by_branch(records),
            "payer_analysis": self._analyze_by_payer(records),
            "temporal_analysis": self._analyze_temporal_trends(records),
            "generated_at": datetime.now().isoformat()
        }
        return analysis

    def _generate_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not records:
            return {
                "total_rejections": 0,
                "total_at_risk": 0,
                "rejection_rate": 0,
                "average_amount": 0
            }

        amounts = [r.get("claim_amount", 0) for r in records if r.get("claim_amount")]
        severities = [r.get("severity", "low") for r in records]

        return {
            "total_rejections": len(records),
            "total_at_risk": sum(amounts),
            "average_amount": statistics.mean(amounts) if amounts else 0,
            "median_amount": statistics.median(amounts) if amounts else 0,
            "by_severity": {
                "critical": severities.count("critical"),
                "high": severities.count("high"),
                "medium": severities.count("medium"),
                "low": severities.count("low")
            }
        }

    def _generate_insights(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI insights from rejection data"""
        insights = []

        # Analyze by reason code
        reason_counts = Counter(r.get("reason_code", "OTHER") for r in records)
        for reason_code, count in reason_counts.most_common(5):
            matching_records = [r for r in records if r.get("reason_code") == reason_code]
            total_amount = sum(r.get("claim_amount", 0) for r in matching_records if r.get("claim_amount"))

            pattern_info = self._get_pattern_info(reason_code)
            insight = {
                "type": "rejection_reason",
                "reason_code": reason_code,
                "count": count,
                "percentage": f"{(count / len(records) * 100):.1f}%",
                "total_at_risk": total_amount,
                "root_causes": pattern_info.get("root_causes", []),
                "recommended_actions": pattern_info.get("actions", []),
                "confidence": min(count / len(records), 0.95)
            }
            insights.append(insight)

        # Identify critical patterns
        critical_records = [r for r in records if r.get("severity") == "critical"]
        if critical_records:
            critical_amount = sum(r.get("claim_amount", 0) for r in critical_records if r.get("claim_amount"))
            insights.append({
                "type": "critical_issues",
                "count": len(critical_records),
                "total_at_risk": critical_amount,
                "message": f"⚠️ {len(critical_records)} critical rejections affecting SAR {critical_amount:,.2f}",
                "severity": "critical",
                "requires_action": True
            })

        # Analyze high-impact claims
        high_amount_records = sorted(records, key=lambda r: r.get("claim_amount", 0), reverse=True)[:5]
        if high_amount_records:
            high_total = sum(r.get("claim_amount", 0) for r in high_amount_records if r.get("claim_amount"))
            insights.append({
                "type": "high_impact_claims",
                "count": len(high_amount_records),
                "total_at_risk": high_total,
                "message": f"Top 5 high-value rejections: SAR {high_total:,.2f}",
                "claim_ids": [r.get("claim_id") for r in high_amount_records]
            })

        return insights

    def _identify_patterns(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify systematic patterns in rejections"""
        patterns = {}

        # Pattern 1: Same error from same provider/branch
        branch_errors = {}
        for record in records:
            branch = record.get("branch", "unknown")
            reason = record.get("reason_code", "other")
            key = f"{branch}:{reason}"

            if key not in branch_errors:
                branch_errors[key] = []
            branch_errors[key].append(record)

        for key, records_list in branch_errors.items():
            if len(records_list) >= 3:  # Pattern threshold
                branch, reason = key.split(":")
                patterns[f"repeated_{reason}_in_{branch}"] = {
                    "branch": branch,
                    "reason": reason,
                    "occurrence": len(records_list),
                    "records": records_list,
                    "pattern_severity": "high" if len(records_list) >= 5 else "medium"
                }

        # Pattern 2: Payer-specific issues
        payer_errors = {}
        for record in records:
            payer = record.get("payer_name", "unknown")
            reason = record.get("reason_code", "other")
            key = f"{payer}:{reason}"

            if key not in payer_errors:
                payer_errors[key] = []
            payer_errors[key].append(record)

        for key, records_list in payer_errors.items():
            if len(records_list) >= 3:
                payer, reason = key.split(":")
                patterns[f"payer_pattern_{payer}_{reason}"] = {
                    "payer": payer,
                    "reason": reason,
                    "occurrence": len(records_list),
                    "pattern_severity": "medium"
                }

        return patterns

    def _generate_predictions(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions based on trends"""
        if len(records) < 5:
            return {"insufficient_data": True, "message": "Need at least 5 rejection records for trend prediction"}

        # Analyze temporal trend
        sorted_records = sorted(records, key=lambda r: r.get("rejection_date", ""))
        recent_5 = len(sorted_records[-5:])
        older_5 = len(sorted_records[:5]) if len(sorted_records) > 5 else 5

        trend = "increasing" if recent_5 > older_5 else "decreasing" if recent_5 < older_5 else "stable"

        return {
            "rejection_trend": trend,
            "recent_rate": recent_5,
            "historical_rate": older_5,
            "predicted_monthly_rejections": int((len(records) / 30) * 30),
            "predicted_monthly_loss": sum(r.get("claim_amount", 0) for r in records) if records else 0,
            "confidence": 0.7 if len(records) < 20 else 0.85
        }

    def _generate_recommendations(self, records: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Count rejections by reason
        reason_counts = Counter(r.get("reason_code", "OTHER") for r in records)

        if reason_counts.get("INVALID_MEMBER", 0) >= 3:
            recommendations.append(
                "🔴 Priority: Audit patient records for accuracy. Invalid member IDs suggest data entry or enrollment issues."
            )

        if reason_counts.get("MISSING_AUTH", 0) >= 2:
            recommendations.append(
                "🟡 Implement pre-authorization verification before claim submission."
            )

        if reason_counts.get("INCOMPLETE_DOCS", 0) >= 3:
            recommendations.append(
                "🟡 Review claim submission process. Implement checklist for required documentation."
            )

        if reason_counts.get("DUPLICATE_CLAIM", 0) >= 1:
            recommendations.append(
                "🔴 Investigate duplicate submissions. Implement deduplication logic in claim system."
            )

        # Check for critical severity issues
        critical_count = sum(1 for r in records if r.get("severity") == "critical")
        if critical_count >= 3:
            recommendations.append(
                "🔴 URGENT: Address critical rejections immediately. Some cannot be resubmitted without major corrections."
            )

        # Check for high financial impact
        high_value_total = sum(r.get("claim_amount", 0) for r in records if r.get("claim_amount", 0) > 50000)
        if high_value_total > 500000:
            recommendations.append(
                f"💰 High financial impact detected (SAR {high_value_total:,.0f}). Escalate to management."
            )

        if not recommendations:
            recommendations.append(
                "✅ Current rejection patterns appear manageable. Continue monitoring for changes."
            )

        return recommendations

    def _analyze_by_branch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze rejections by branch"""
        branch_data = {}

        for record in records:
            branch = record.get("branch", "Unknown")
            if branch not in branch_data:
                branch_data[branch] = {
                    "count": 0,
                    "total_amount": 0,
                    "reasons": Counter(),
                    "severity_dist": Counter()
                }

            branch_data[branch]["count"] += 1
            branch_data[branch]["total_amount"] += record.get("claim_amount", 0)
            branch_data[branch]["reasons"][record.get("reason_code", "OTHER")] += 1
            branch_data[branch]["severity_dist"][record.get("severity", "low")] += 1

        # Convert Counters to dicts for JSON serialization
        for branch, data in branch_data.items():
            data["reasons"] = dict(data["reasons"])
            data["severity_dist"] = dict(data["severity_dist"])

        return branch_data

    def _analyze_by_payer(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze rejections by payer"""
        payer_data = {}

        for record in records:
            payer = record.get("payer_name", "Unknown")
            if payer not in payer_data:
                payer_data[payer] = {
                    "count": 0,
                    "total_amount": 0,
                    "top_reasons": Counter(),
                    "critical_count": 0
                }

            payer_data[payer]["count"] += 1
            payer_data[payer]["total_amount"] += record.get("claim_amount", 0)
            payer_data[payer]["top_reasons"][record.get("reason_code", "OTHER")] += 1

            if record.get("severity") == "critical":
                payer_data[payer]["critical_count"] += 1

        # Convert Counters to dicts
        for payer, data in payer_data.items():
            data["top_reasons"] = dict(data["top_reasons"].most_common(5))

        return payer_data

    def _analyze_temporal_trends(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal trends in rejections"""
        if not records:
            return {}

        # Group by date
        daily_counts = {}
        for record in records:
            date_str = record.get("rejection_date", "")[:10]  # YYYY-MM-DD
            if date_str:
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

        # Calculate weekly trend
        sorted_dates = sorted(daily_counts.keys())
        if len(sorted_dates) >= 7:
            week1 = sum(daily_counts[d] for d in sorted_dates[:7])
            week_last = sum(daily_counts[d] for d in sorted_dates[-7:])
            trend = "increasing" if week_last > week1 else "decreasing" if week_last < week1 else "stable"
        else:
            trend = "insufficient_data"

        return {
            "daily_distribution": daily_counts,
            "trend": trend,
            "earliest_rejection": sorted_dates[0] if sorted_dates else None,
            "latest_rejection": sorted_dates[-1] if sorted_dates else None
        }

    def _get_pattern_info(self, reason_code: str) -> Dict[str, Any]:
        """Get pattern information for a reason code"""
        for pattern_name, pattern_data in self.patterns.items():
            for keyword in pattern_data.get("keywords", []):
                if keyword.replace(" ", "_").upper() == reason_code:
                    return pattern_data

        # Default pattern
        return {
            "root_causes": ["Insufficient information"],
            "actions": ["Review claim details and payer correspondence"]
        }

    def generate_branch_report(self, records: List[Dict[str, Any]], branch: str) -> Dict[str, Any]:
        """Generate detailed report for specific branch"""
        branch_records = [r for r in records if r.get("branch") == branch]

        if not branch_records:
            return {"branch": branch, "message": "No rejection records found"}

        analysis = self.analyze_rejections(branch_records)

        return {
            "branch": branch,
            "analysis": analysis,
            "executive_summary": {
                "total_rejections": len(branch_records),
                "total_at_risk": sum(r.get("claim_amount", 0) for r in branch_records if r.get("claim_amount")),
                "top_reason": Counter(r.get("reason_code") for r in branch_records).most_common(1)[0][0],
                "immediate_actions_required": len([r for r in branch_records if r.get("severity") in ["critical", "high"]])
            },
            "generated_at": datetime.now().isoformat()
        }


# Utility functions
def analyze_rejections(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Utility function to analyze rejections"""
    analyzer = RejectionAnalyzer()
    return analyzer.analyze_rejections(records)


def generate_branch_report(records: List[Dict[str, Any]], branch: str) -> Dict[str, Any]:
    """Utility function to generate branch report"""
    analyzer = RejectionAnalyzer()
    return analyzer.generate_branch_report(records, branch)


if __name__ == "__main__":
    analyzer = RejectionAnalyzer()
    print("RejectionAnalyzer initialized")
    print(f"Patterns available: {list(analyzer.patterns.keys())}")
    print(f"Rules available: {len(analyzer.rules)}")
