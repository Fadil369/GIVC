"""
NPHIES Analytics Service
Advanced analytics and insights for NPHIES transactions
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("analytics")


class NPHIESAnalytics:
    """Analytics service for NPHIES integration performance and insights"""
    
    def __init__(self):
        self.metrics = {
            "eligibility": defaultdict(int),
            "claims": defaultdict(int),
            "authorizations": defaultdict(int),
            "errors": []
        }
    
    def analyze_eligibility_results(self, results: List[Dict]) -> Dict:
        """
        Analyze eligibility check results
        
        Args:
            results: List of eligibility results
            
        Returns:
            Dictionary with analytics insights
        """
        analysis = {
            "total_checks": len(results),
            "successful_checks": 0,
            "failed_checks": 0,
            "eligible_members": 0,
            "ineligible_members": 0,
            "coverage_types": defaultdict(int),
            "payers": defaultdict(int),
            "average_response_time": 0,
            "error_patterns": defaultdict(int)
        }
        
        response_times = []
        
        for result in results:
            if result.get("success"):
                analysis["successful_checks"] += 1
                
                coverage_status = result.get("coverage_status", {})
                if coverage_status.get("eligible"):
                    analysis["eligible_members"] += 1
                else:
                    analysis["ineligible_members"] += 1
                
                # Track payer
                payer_id = result.get("request_data", {}).get("payer_id")
                if payer_id:
                    analysis["payers"][payer_id] += 1
            else:
                analysis["failed_checks"] += 1
                
                # Track error patterns
                error = result.get("error", "Unknown error")
                analysis["error_patterns"][error[:50]] += 1
        
        # Calculate success rate
        if analysis["total_checks"] > 0:
            analysis["success_rate"] = (
                analysis["successful_checks"] / analysis["total_checks"]
            ) * 100
            analysis["eligibility_rate"] = (
                analysis["eligible_members"] / analysis["total_checks"]
            ) * 100
        
        return analysis
    
    def analyze_claims_results(self, results: List[Dict]) -> Dict:
        """
        Analyze claims submission results
        
        Args:
            results: List of claim results
            
        Returns:
            Dictionary with claims analytics
        """
        analysis = {
            "total_claims": len(results),
            "successful_submissions": 0,
            "failed_submissions": 0,
            "approved_claims": 0,
            "denied_claims": 0,
            "pending_claims": 0,
            "total_claimed_amount": 0.0,
            "total_approved_amount": 0.0,
            "claim_types": defaultdict(int),
            "approval_rate": 0.0,
            "average_claim_amount": 0.0,
            "top_denial_reasons": defaultdict(int)
        }
        
        for result in results:
            if result.get("success"):
                analysis["successful_submissions"] += 1
                
                claim_response = result.get("claim_response", {})
                status = claim_response.get("status", "pending")
                
                if status == "active" and claim_response.get("outcome") == "complete":
                    analysis["approved_claims"] += 1
                    approved_amt = claim_response.get("total_approved", 0.0)
                    analysis["total_approved_amount"] += approved_amt
                elif claim_response.get("outcome") == "error":
                    analysis["denied_claims"] += 1
                    
                    # Track denial reasons
                    disposition = claim_response.get("disposition", "Unknown")
                    analysis["top_denial_reasons"][disposition] += 1
                else:
                    analysis["pending_claims"] += 1
                
                # Track claim type
                claim_type = result.get("request_data", {}).get("claim_type", "unknown")
                analysis["claim_types"][claim_type] += 1
                
                # Track amounts
                total_amt = result.get("request_data", {}).get("total_amount", 0.0)
                analysis["total_claimed_amount"] += total_amt
            else:
                analysis["failed_submissions"] += 1
        
        # Calculate rates
        if analysis["total_claims"] > 0:
            analysis["submission_success_rate"] = (
                analysis["successful_submissions"] / analysis["total_claims"]
            ) * 100
            analysis["average_claim_amount"] = (
                analysis["total_claimed_amount"] / analysis["total_claims"]
            )
        
        if analysis["successful_submissions"] > 0:
            analysis["approval_rate"] = (
                analysis["approved_claims"] / analysis["successful_submissions"]
            ) * 100
        
        # Calculate reimbursement rate
        if analysis["total_claimed_amount"] > 0:
            analysis["reimbursement_rate"] = (
                analysis["total_approved_amount"] / analysis["total_claimed_amount"]
            ) * 100
        
        return analysis
    
    def analyze_authorization_results(self, results: List[Dict]) -> Dict:
        """
        Analyze prior authorization results
        
        Args:
            results: List of authorization results
            
        Returns:
            Dictionary with authorization analytics
        """
        analysis = {
            "total_requests": len(results),
            "successful_submissions": 0,
            "approved_authorizations": 0,
            "denied_authorizations": 0,
            "pending_authorizations": 0,
            "approval_rate": 0.0,
            "average_turnaround_time": 0.0,
            "procedures": defaultdict(int),
            "denial_reasons": defaultdict(int)
        }
        
        for result in results:
            if result.get("success"):
                analysis["successful_submissions"] += 1
                
                auth_response = result.get("authorization_response", {})
                decision = auth_response.get("decision", "pending")
                
                if decision == "approved":
                    analysis["approved_authorizations"] += 1
                elif decision == "denied":
                    analysis["denied_authorizations"] += 1
                    
                    # Track denial reasons
                    disposition = auth_response.get("disposition", "Unknown")
                    analysis["denial_reasons"][disposition] += 1
                else:
                    analysis["pending_authorizations"] += 1
        
        # Calculate approval rate
        if analysis["successful_submissions"] > 0:
            analysis["approval_rate"] = (
                analysis["approved_authorizations"] / analysis["successful_submissions"]
            ) * 100
        
        return analysis
    
    def generate_performance_report(
        self,
        eligibility_results: List[Dict] = None,
        claims_results: List[Dict] = None,
        authorization_results: List[Dict] = None,
        period_start: datetime = None,
        period_end: datetime = None
    ) -> Dict:
        """
        Generate comprehensive performance report
        
        Args:
            eligibility_results: Eligibility results
            claims_results: Claims results
            authorization_results: Authorization results
            period_start: Report period start
            period_end: Report period end
            
        Returns:
            Complete performance report
        """
        if not period_start:
            period_start = datetime.now() - timedelta(days=30)
        if not period_end:
            period_end = datetime.now()
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": (period_end - period_start).days
            },
            "summary": {
                "total_transactions": 0,
                "successful_transactions": 0,
                "failed_transactions": 0,
                "overall_success_rate": 0.0
            },
            "eligibility": None,
            "claims": None,
            "authorizations": None,
            "recommendations": []
        }
        
        # Analyze each component
        if eligibility_results:
            report["eligibility"] = self.analyze_eligibility_results(eligibility_results)
            report["summary"]["total_transactions"] += report["eligibility"]["total_checks"]
            report["summary"]["successful_transactions"] += report["eligibility"]["successful_checks"]
        
        if claims_results:
            report["claims"] = self.analyze_claims_results(claims_results)
            report["summary"]["total_transactions"] += report["claims"]["total_claims"]
            report["summary"]["successful_transactions"] += report["claims"]["successful_submissions"]
        
        if authorization_results:
            report["authorizations"] = self.analyze_authorization_results(authorization_results)
            report["summary"]["total_transactions"] += report["authorizations"]["total_requests"]
            report["summary"]["successful_transactions"] += report["authorizations"]["successful_submissions"]
        
        # Calculate overall metrics
        if report["summary"]["total_transactions"] > 0:
            report["summary"]["overall_success_rate"] = (
                report["summary"]["successful_transactions"] /
                report["summary"]["total_transactions"]
            ) * 100
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        # Check overall success rate
        overall_rate = report["summary"]["overall_success_rate"]
        if overall_rate < 90:
            recommendations.append(
                f"⚠️ Overall success rate is {overall_rate:.1f}%. "
                "Review error logs and improve data validation."
            )
        
        # Check eligibility rate
        if report.get("eligibility"):
            elig_rate = report["eligibility"].get("eligibility_rate", 0)
            if elig_rate < 80:
                recommendations.append(
                    f"⚠️ Only {elig_rate:.1f}% of members are eligible. "
                    "Verify member data and insurance coverage status."
                )
        
        # Check claims approval rate
        if report.get("claims"):
            approval_rate = report["claims"].get("approval_rate", 0)
            if approval_rate < 70:
                recommendations.append(
                    f"⚠️ Claims approval rate is {approval_rate:.1f}%. "
                    "Review denial reasons and improve claim documentation."
                )
            
            # Check reimbursement rate
            reimb_rate = report["claims"].get("reimbursement_rate", 0)
            if reimb_rate < 85:
                recommendations.append(
                    f"💰 Reimbursement rate is {reimb_rate:.1f}%. "
                    "Consider negotiating better rates or reviewing claim amounts."
                )
        
        # Check authorization approval
        if report.get("authorizations"):
            auth_rate = report["authorizations"].get("approval_rate", 0)
            if auth_rate < 75:
                recommendations.append(
                    f"⚠️ Authorization approval rate is {auth_rate:.1f}%. "
                    "Strengthen medical justifications and documentation."
                )
        
        if not recommendations:
            recommendations.append("✅ All metrics are performing well. Keep up the good work!")
        
        return recommendations
    
    def export_report(self, report: Dict, output_file: str):
        """Export report to JSON file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analytics report exported to: {output_file}")
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
    
    def get_key_metrics(self, report: Dict) -> Dict:
        """Extract key performance indicators"""
        kpis = {
            "overall_success_rate": report["summary"]["overall_success_rate"],
            "total_transactions": report["summary"]["total_transactions"],
            "eligibility_rate": report.get("eligibility", {}).get("eligibility_rate", 0),
            "claims_approval_rate": report.get("claims", {}).get("approval_rate", 0),
            "reimbursement_rate": report.get("claims", {}).get("reimbursement_rate", 0),
            "authorization_approval_rate": report.get("authorizations", {}).get("approval_rate", 0),
            "total_claimed": report.get("claims", {}).get("total_claimed_amount", 0),
            "total_approved": report.get("claims", {}).get("total_approved_amount", 0)
        }
        
        return kpis
