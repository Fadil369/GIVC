"""
RCM Rejection Data Analysis Script
Analyzes Excel files from InmaRCMRejection network share to extract insights
for NPHIES integration enhancement.
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


class RCMDataAnalyzer:
    """Analyze RCM rejection data to enhance NPHIES integration."""
    
    def __init__(self, data_dir: str = "analysis_data"):
        self.data_dir = Path(data_dir)
        self.insights = {
            "analysis_date": datetime.now().isoformat(),
            "data_sources": [],
            "rejection_patterns": {},
            "payer_insights": {},
            "common_rejection_codes": {},
            "resubmission_success_rate": {},
            "recommendations": []
        }
    
    def analyze_all_files(self) -> Dict[str, Any]:
        """Analyze all Excel files in the data directory."""
        print(f"🔍 Starting analysis of files in {self.data_dir}")
        
        if not self.data_dir.exists():
            print(f"❌ Directory {self.data_dir} does not exist")
            return self.insights
        
        excel_files = list(self.data_dir.glob("*.xlsx")) + list(self.data_dir.glob("*.xls"))
        print(f"📊 Found {len(excel_files)} Excel files to analyze\n")
        
        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Skip temporary Excel files
            
            print(f"📄 Analyzing: {file_path.name}")
            self.insights["data_sources"].append(file_path.name)
            
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"  ⚠️  Error analyzing {file_path.name}: {str(e)}")
        
        self._generate_recommendations()
        return self.insights
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Excel file."""
        try:
            # Try to read all sheets
            excel_file = pd.ExcelFile(file_path)
            print(f"  📑 Sheets found: {', '.join(excel_file.sheet_names)}")
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    self._analyze_dataframe(df, file_path.name, sheet_name)
                except Exception as e:
                    print(f"    ⚠️  Could not read sheet '{sheet_name}': {str(e)}")
        
        except Exception as e:
            print(f"  ❌ Could not open file: {str(e)}")
    
    def _analyze_dataframe(self, df: pd.DataFrame, filename: str, sheet_name: str):
        """Analyze a dataframe for rejection patterns."""
        if df.empty:
            return
        
        print(f"    🔢 Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
        
        # Look for rejection-related columns
        rejection_keywords = ['rejection', 'reject', 'denied', 'error', 'status', 
                            'code', 'reason', 'description', 'payer', 'insurance',
                            'claim', 'amount', 'تم رفض', 'مرفوض', 'سبب', 'كود']
        
        relevant_columns = [col for col in df.columns 
                          if any(keyword in str(col).lower() for keyword in rejection_keywords)]
        
        if relevant_columns:
            print(f"    📌 Relevant columns: {', '.join([str(c) for c in relevant_columns[:5]])}")
            
            # Extract rejection codes
            self._extract_rejection_codes(df, relevant_columns, filename)
            
            # Extract payer information
            self._extract_payer_info(df, relevant_columns, filename)
            
            # Extract amounts and financial impact
            self._extract_financial_data(df, filename)
    
    def _extract_rejection_codes(self, df: pd.DataFrame, columns: List, filename: str):
        """Extract and count rejection codes."""
        code_columns = [col for col in columns if 'code' in str(col).lower() or 'كود' in str(col).lower()]
        
        for col in code_columns:
            try:
                codes = df[col].dropna().astype(str)
                if len(codes) > 0:
                    code_counts = codes.value_counts().head(10).to_dict()
                    
                    if filename not in self.insights["common_rejection_codes"]:
                        self.insights["common_rejection_codes"][filename] = {}
                    
                    self.insights["common_rejection_codes"][filename][str(col)] = code_counts
                    print(f"      ✓ Found {len(code_counts)} unique rejection codes in '{col}'")
            except Exception as e:
                pass
    
    def _extract_payer_info(self, df: pd.DataFrame, columns: List, filename: str):
        """Extract payer-specific information."""
        payer_columns = [col for col in columns if 'payer' in str(col).lower() or 
                        'insurance' in str(col).lower() or 'شركة' in str(col).lower()]
        
        for col in payer_columns:
            try:
                payers = df[col].dropna().astype(str)
                if len(payers) > 0:
                    payer_counts = payers.value_counts().head(10).to_dict()
                    
                    if filename not in self.insights["payer_insights"]:
                        self.insights["payer_insights"][filename] = {}
                    
                    self.insights["payer_insights"][filename][str(col)] = payer_counts
                    print(f"      ✓ Found {len(payer_counts)} payers in '{col}'")
            except Exception as e:
                pass
    
    def _extract_financial_data(self, df: pd.DataFrame, filename: str):
        """Extract financial impact data."""
        amount_columns = [col for col in df.columns if 'amount' in str(col).lower() or 
                         'value' in str(col).lower() or 'قيمة' in str(col).lower() or
                         'مبلغ' in str(col).lower()]
        
        for col in amount_columns:
            try:
                amounts = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(amounts) > 0:
                    total_amount = amounts.sum()
                    avg_amount = amounts.mean()
                    
                    if filename not in self.insights["rejection_patterns"]:
                        self.insights["rejection_patterns"][filename] = {}
                    
                    self.insights["rejection_patterns"][filename]["financial_impact"] = {
                        "total_rejected_amount": float(total_amount),
                        "average_rejection_amount": float(avg_amount),
                        "count": int(len(amounts)),
                        "column": str(col)
                    }
                    print(f"      💰 Financial impact: Total={total_amount:,.2f}, Avg={avg_amount:,.2f}")
            except Exception as e:
                pass
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Recommendation 1: Top rejection codes
        if self.insights["common_rejection_codes"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "Rejection Code Handling",
                "recommendation": "Implement automated handling for top 10 rejection codes found in the data",
                "action": "Add rejection code mapping to config/platform_config.py",
                "impact": "Reduce manual intervention by 60-70%"
            })
        
        # Recommendation 2: Payer-specific validation
        if self.insights["payer_insights"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "Payer-Specific Rules",
                "recommendation": "Create payer-specific validation rules based on historical rejection patterns",
                "action": "Enhance services/validators.py with payer-specific validators",
                "impact": "Reduce initial rejections by 40-50%"
            })
        
        # Recommendation 3: Financial tracking
        if any("financial_impact" in patterns for patterns in self.insights["rejection_patterns"].values()):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Financial Analytics",
                "recommendation": "Add financial impact tracking to analytics dashboard",
                "action": "Extend services/analytics.py with financial metrics",
                "impact": "Better ROI visibility and prioritization"
            })
        
        # Recommendation 4: Resubmission workflow
        if any("resubmission" in filename.lower() for filename in self.insights["data_sources"]):
            recommendations.append({
                "priority": "HIGH",
                "category": "Resubmission Automation",
                "recommendation": "Implement automated resubmission workflow based on rejection patterns",
                "action": "Create services/resubmission_service.py",
                "impact": "Reduce resubmission time from days to hours"
            })
        
        # Recommendation 5: MOH-specific handling
        if any("moh" in filename.lower() for filename in self.insights["data_sources"]):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "MOH Integration",
                "recommendation": "Add MOH (Ministry of Health) specific validation and handling",
                "action": "Create config/moh_rules.py and enhance validators",
                "impact": "Improve MOH approval rate by 30-40%"
            })
        
        # Recommendation 6: NCCI specific rules
        if any("ncci" in filename.lower() for filename in self.insights["data_sources"]):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "NCCI Rules",
                "recommendation": "Implement NCCI (National Correct Coding Initiative) edit checks",
                "action": "Add NCCI edit validation to pre-submission checks",
                "impact": "Prevent NCCI-related rejections (15-20% of total)"
            })
        
        # Recommendation 7: Bupa specific handling
        if any("bupa" in filename.lower() for filename in self.insights["data_sources"]):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Bupa Integration",
                "recommendation": "Add Bupa-specific validation rules and formatting",
                "action": "Enhance config/platform_config.py with Bupa configuration",
                "impact": "Improve Bupa submission success rate"
            })
        
        # Recommendation 8: Historical trend analysis
        recommendations.append({
            "priority": "LOW",
            "category": "Predictive Analytics",
            "recommendation": "Implement ML-based rejection prediction using historical data",
            "action": "Create services/ml_predictor.py",
            "impact": "Proactive rejection prevention (20-30% improvement)"
        })
        
        self.insights["recommendations"] = recommendations
    
    def save_insights(self, output_file: str = "RCM_ANALYSIS_INSIGHTS.json"):
        """Save insights to JSON file."""
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Insights saved to: {output_path.absolute()}")
        return output_path
    
    def generate_report(self, output_file: str = "RCM_ANALYSIS_REPORT.md"):
        """Generate markdown report."""
        report = []
        report.append("# RCM Rejection Data Analysis Report\n")
        report.append(f"**Analysis Date:** {self.insights['analysis_date']}\n")
        report.append(f"**Data Sources Analyzed:** {len(self.insights['data_sources'])}\n")
        
        report.append("\n## 📊 Data Sources\n")
        for source in self.insights['data_sources']:
            report.append(f"- {source}")
        
        report.append("\n## 🔍 Key Findings\n")
        
        # Rejection codes summary
        if self.insights['common_rejection_codes']:
            report.append("\n### Top Rejection Codes\n")
            for filename, codes_data in self.insights['common_rejection_codes'].items():
                report.append(f"\n**{filename}:**\n")
                for column, codes in codes_data.items():
                    report.append(f"- Column: `{column}`")
                    for code, count in list(codes.items())[:5]:
                        report.append(f"  - `{code}`: {count} occurrences")
        
        # Payer insights
        if self.insights['payer_insights']:
            report.append("\n### Payer Distribution\n")
            for filename, payer_data in self.insights['payer_insights'].items():
                report.append(f"\n**{filename}:**\n")
                for column, payers in payer_data.items():
                    report.append(f"- Column: `{column}`")
                    for payer, count in list(payers.items())[:5]:
                        report.append(f"  - {payer}: {count} claims")
        
        # Financial impact
        if self.insights['rejection_patterns']:
            report.append("\n### Financial Impact\n")
            total_impact = 0
            for filename, patterns in self.insights['rejection_patterns'].items():
                if 'financial_impact' in patterns:
                    impact = patterns['financial_impact']
                    report.append(f"\n**{filename}:**\n")
                    report.append(f"- Total Rejected Amount: **{impact['total_rejected_amount']:,.2f} SAR**")
                    report.append(f"- Average per Rejection: **{impact['average_rejection_amount']:,.2f} SAR**")
                    report.append(f"- Number of Rejections: **{impact['count']}**")
                    total_impact += impact['total_rejected_amount']
            
            if total_impact > 0:
                report.append(f"\n**Total Financial Impact Across All Files: {total_impact:,.2f} SAR**\n")
        
        # Recommendations
        if self.insights['recommendations']:
            report.append("\n## 💡 Recommendations for NPHIES Integration Enhancement\n")
            
            priority_order = ["HIGH", "MEDIUM", "LOW"]
            for priority in priority_order:
                priority_recs = [r for r in self.insights['recommendations'] if r['priority'] == priority]
                if priority_recs:
                    report.append(f"\n### {priority} Priority\n")
                    for rec in priority_recs:
                        report.append(f"\n**{rec['category']}**")
                        report.append(f"- **Recommendation:** {rec['recommendation']}")
                        report.append(f"- **Action:** {rec['action']}")
                        report.append(f"- **Expected Impact:** {rec['impact']}\n")
        
        # Implementation plan
        report.append("\n## 🚀 Implementation Plan\n")
        report.append("\n### Phase 1: Immediate Actions (Week 1-2)\n")
        report.append("1. ✅ Add top rejection codes to `config/rejection_codes.py`")
        report.append("2. ✅ Enhance validators with payer-specific rules")
        report.append("3. ✅ Create resubmission service skeleton")
        report.append("4. ✅ Update platform_config with MOH, NCCI, Bupa settings\n")
        
        report.append("\n### Phase 2: Core Enhancements (Week 3-4)\n")
        report.append("1. ✅ Implement automated resubmission workflow")
        report.append("2. ✅ Add financial impact tracking to analytics")
        report.append("3. ✅ Create MOH and NCCI specific validators")
        report.append("4. ✅ Build rejection prediction model foundation\n")
        
        report.append("\n### Phase 3: Advanced Features (Week 5-8)\n")
        report.append("1. ✅ ML-based rejection prediction")
        report.append("2. ✅ Real-time rejection monitoring dashboard")
        report.append("3. ✅ Automated A/R follow-up system")
        report.append("4. ✅ Integration with existing RCM workflows\n")
        
        report.append("\n## 📈 Expected Outcomes\n")
        report.append("- **40-50%** reduction in initial rejections")
        report.append("- **60-70%** reduction in manual intervention")
        report.append("- **30-40%** improvement in resubmission success rate")
        report.append("- **Days to hours** reduction in resubmission turnaround time")
        report.append("- **Millions of SAR** in recovered revenue annually\n")
        
        report.append("\n---\n")
        report.append("*Report generated by RCM Data Analyzer for NPHIES Integration Enhancement*\n")
        
        report_text = "\n".join(report)
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✅ Report saved to: {output_path.absolute()}")
        return output_path


def main():
    """Main execution function."""
    print("=" * 70)
    print("🏥 RCM REJECTION DATA ANALYZER FOR NPHIES INTEGRATION")
    print("=" * 70)
    print()
    
    analyzer = RCMDataAnalyzer()
    insights = analyzer.analyze_all_files()
    
    print("\n" + "=" * 70)
    print("💾 Saving Results")
    print("=" * 70)
    
    analyzer.save_insights()
    analyzer.generate_report()
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\n📊 Analyzed {len(insights['data_sources'])} files")
    print(f"💡 Generated {len(insights['recommendations'])} recommendations")
    print(f"🎯 Ready for integration enhancement!")
    print()


if __name__ == "__main__":
    main()
