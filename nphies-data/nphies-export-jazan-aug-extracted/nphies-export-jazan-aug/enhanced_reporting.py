#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

class EnhancedReporter:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def create_executive_report(self):
        """Generate professional executive report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 80,
            "NPHIES CLAIMS ANALYSIS - EXECUTIVE REPORT".center(80),
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}".center(80),
            "=" * 80,
            ""
        ])
        
        # Executive Summary
        total_claims = len(self.data)
        rejected = len([r for r in self.data if r.get('Status') == 'Rejected'])
        approved = len([r for r in self.data if r.get('Status') == 'Approved'])
        partial = len([r for r in self.data if r.get('Status') == 'Partial'])
        
        total_net = sum(float(r.get('Net Amount', 0) or 0) for r in self.data)
        total_approved_amt = sum(float(r.get('Approved Amount', 0) or 0) for r in self.data)
        financial_loss = total_net - total_approved_amt
        
        report_lines.extend([
            "EXECUTIVE SUMMARY",
            "-" * 20,
            f"📊 Total Claims Processed: {total_claims:,}",
            f"✅ Approved Claims: {approved:,} ({(approved/total_claims)*100:.1f}%)",
            f"❌ Rejected Claims: {rejected:,} ({(rejected/total_claims)*100:.1f}%)",
            f"⚠️  Partial Claims: {partial:,} ({(partial/total_claims)*100:.1f}%)",
            "",
            f"💰 Financial Overview:",
            f"   • Total Claim Value: {total_net:,.2f} SAR",
            f"   • Approved Amount: {total_approved_amt:,.2f} SAR",
            f"   • Financial Loss: {financial_loss:,.2f} SAR",
            f"   • Recovery Rate: {(total_approved_amt/total_net)*100:.1f}%",
            "",
        ])
        
        # Top Issues
        insurer_rejections = Counter()
        for row in self.data:
            if row.get('Status') == 'Rejected':
                insurer_rejections[row.get('Insurer Name', 'Unknown')] += 1
        
        report_lines.extend([
            "🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION",
            "-" * 50,
            "Top Rejecting Insurers:",
        ])
        
        for i, (insurer, count) in enumerate(insurer_rejections.most_common(5), 1):
            report_lines.append(f"   {i}. {insurer}: {count} rejections")
        
        # High-value rejections
        high_value_rejections = []
        for row in self.data:
            if row.get('Status') == 'Rejected':
                try:
                    amount = float(row.get('Net Amount', 0) or 0)
                    if amount > 10000:
                        high_value_rejections.append((row.get('Transaction Identifier'), amount, row.get('Insurer Name')))
                except:
                    continue
        
        high_value_rejections.sort(key=lambda x: x[1], reverse=True)
        
        report_lines.extend([
            "",
            "💸 HIGH-VALUE REJECTIONS (>10,000 SAR):",
            f"   Total Count: {len(high_value_rejections)}",
            f"   Total Value: {sum(x[1] for x in high_value_rejections):,.2f} SAR",
            "",
            "   Top 10 Priority Appeals:",
        ])
        
        for i, (trans_id, amount, insurer) in enumerate(high_value_rejections[:10], 1):
            report_lines.append(f"   {i:2d}. Transaction {trans_id}: {amount:,.0f} SAR ({insurer})")
        
        # Action Plan
        report_lines.extend([
            "",
            "🎯 IMMEDIATE ACTION PLAN",
            "-" * 25,
            "WEEK 1 PRIORITIES:",
            "   □ Appeal top 10 high-value rejections",
            "   □ Schedule meetings with top 3 rejecting insurers",
            "   □ Implement daily rejection monitoring",
            "",
            "WEEK 2-4 PRIORITIES:",
            "   □ Develop insurer-specific submission guidelines",
            "   □ Train staff on rejection patterns",
            "   □ Establish weekly insurer communication",
            "",
            "MONTH 2 INITIATIVES:",
            "   □ Implement automated validation system",
            "   □ Create rejection prediction model",
            "   □ Establish performance KPIs",
            "",
            "=" * 80
        ])
        
        # Save report
        with open('Executive_Claims_Report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print("📄 Executive report saved to 'Executive_Claims_Report.txt'")
        return report_lines
    
    def create_detailed_excel_data(self):
        """Create structured data for Excel export"""
        
        # Summary sheet data
        summary_data = []
        status_counts = Counter(row.get('Status', 'Unknown') for row in self.data)
        
        summary_data.append(['Metric', 'Value', 'Percentage'])
        total_claims = len(self.data)
        
        for status, count in status_counts.most_common():
            percentage = (count / total_claims) * 100
            summary_data.append([f'{status} Claims', count, f'{percentage:.1f}%'])
        
        # Financial summary
        total_net = sum(float(r.get('Net Amount', 0) or 0) for r in self.data)
        total_approved = sum(float(r.get('Approved Amount', 0) or 0) for r in self.data)
        
        summary_data.extend([
            ['', '', ''],
            ['Financial Metrics', '', ''],
            ['Total Net Amount (SAR)', f'{total_net:,.2f}', ''],
            ['Total Approved (SAR)', f'{total_approved:,.2f}', ''],
            ['Financial Loss (SAR)', f'{total_net - total_approved:,.2f}', ''],
            ['Recovery Rate', f'{(total_approved/total_net)*100:.1f}%', '']
        ])
        
        # Insurer analysis
        insurer_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'net_amount': 0, 'approved_amount': 0})
        
        for row in self.data:
            insurer = row.get('Insurer Name', 'Unknown')
            insurer_stats[insurer]['total'] += 1
            if row.get('Status') == 'Rejected':
                insurer_stats[insurer]['rejected'] += 1
            
            try:
                insurer_stats[insurer]['net_amount'] += float(row.get('Net Amount', 0) or 0)
                insurer_stats[insurer]['approved_amount'] += float(row.get('Approved Amount', 0) or 0)
            except:
                continue
        
        insurer_data = [['Insurer Name', 'Total Claims', 'Rejected Claims', 'Rejection Rate %', 'Net Amount SAR', 'Approved Amount SAR', 'Financial Loss SAR']]
        
        for insurer, stats in sorted(insurer_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            if stats['total'] >= 10:  # Minimum threshold
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                financial_loss = stats['net_amount'] - stats['approved_amount']
                
                insurer_data.append([
                    insurer,
                    stats['total'],
                    stats['rejected'],
                    f'{rejection_rate:.1f}%',
                    f'{stats["net_amount"]:,.2f}',
                    f'{stats["approved_amount"]:,.2f}',
                    f'{financial_loss:,.2f}'
                ])
        
        # High-value rejections
        high_value_data = [['Transaction ID', 'Net Amount SAR', 'Insurer Name', 'Submission Date', 'Patient ID', 'Provider Name']]
        
        for row in self.data:
            if row.get('Status') == 'Rejected':
                try:
                    amount = float(row.get('Net Amount', 0) or 0)
                    if amount > 5000:  # High value threshold
                        high_value_data.append([
                            row.get('Transaction Identifier', ''),
                            f'{amount:,.2f}',
                            row.get('Insurer Name', ''),
                            row.get('Submission Date', ''),
                            row.get('Patient Identifier', ''),
                            row.get('Provider Name', '')
                        ])
                except:
                    continue
        
        # Sort high-value by amount
        high_value_data[1:] = sorted(high_value_data[1:], key=lambda x: float(x[1].replace(',', '')), reverse=True)
        
        # Export to CSV files (Excel-compatible)
        with open('Claims_Summary_Analysis.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(summary_data)
        
        with open('Insurer_Performance_Analysis.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(insurer_data)
        
        with open('High_Value_Rejections_Priority.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(high_value_data)
        
        print("📊 Excel-compatible files created:")
        print("   • Claims_Summary_Analysis.csv")
        print("   • Insurer_Performance_Analysis.csv")
        print("   • High_Value_Rejections_Priority.csv")
        
        return summary_data, insurer_data, high_value_data
    
    def create_trend_analysis(self):
        """Create detailed trend analysis"""
        
        # Daily trends
        daily_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'approved': 0, 'net_amount': 0})
        
        for row in self.data:
            date_str = row.get('Submission Date', '')
            if date_str:
                try:
                    date_parts = date_str.split(' ')[0].split('-')
                    if len(date_parts) == 3:
                        day = int(date_parts[0])
                        daily_stats[day]['total'] += 1
                        
                        status = row.get('Status', '')
                        if status == 'Rejected':
                            daily_stats[day]['rejected'] += 1
                        elif status == 'Approved':
                            daily_stats[day]['approved'] += 1
                        
                        try:
                            daily_stats[day]['net_amount'] += float(row.get('Net Amount', 0) or 0)
                        except:
                            continue
                except:
                    continue
        
        # Create trend report
        trend_data = [['Day of Month', 'Total Claims', 'Rejected Claims', 'Rejection Rate %', 'Total Value SAR']]
        
        for day in sorted(daily_stats.keys()):
            stats = daily_stats[day]
            if stats['total'] > 0:
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                trend_data.append([
                    day,
                    stats['total'],
                    stats['rejected'],
                    f'{rejection_rate:.1f}%',
                    f'{stats["net_amount"]:,.2f}'
                ])
        
        with open('Daily_Trend_Analysis.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(trend_data)
        
        print("📈 Trend analysis saved to 'Daily_Trend_Analysis.csv'")
        return trend_data
    
    def create_action_tracker(self):
        """Create actionable task tracker"""
        
        # Get high-priority items
        high_value_rejections = []
        critical_insurers = []
        
        insurer_rejections = Counter()
        for row in self.data:
            if row.get('Status') == 'Rejected':
                insurer = row.get('Insurer Name', 'Unknown')
                insurer_rejections[insurer] += 1
                
                try:
                    amount = float(row.get('Net Amount', 0) or 0)
                    if amount > 10000:
                        high_value_rejections.append({
                            'transaction_id': row.get('Transaction Identifier'),
                            'amount': amount,
                            'insurer': insurer,
                            'date': row.get('Submission Date')
                        })
                except:
                    continue
        
        # Critical insurers (>100 rejections)
        for insurer, count in insurer_rejections.items():
            if count > 100:
                critical_insurers.append({'insurer': insurer, 'rejections': count})
        
        # Create action tracker
        action_data = [['Priority', 'Action Item', 'Details', 'Target Date', 'Status', 'Owner']]
        
        # High-value appeals
        for i, rejection in enumerate(sorted(high_value_rejections, key=lambda x: x['amount'], reverse=True)[:20], 1):
            action_data.append([
                'Critical',
                f'Appeal Transaction {rejection["transaction_id"]}',
                f'{rejection["amount"]:,.0f} SAR - {rejection["insurer"]}',
                'Within 7 days',
                'Pending',
                'Claims Team'
            ])
        
        # Insurer meetings
        for insurer_info in sorted(critical_insurers, key=lambda x: x['rejections'], reverse=True)[:5]:
            action_data.append([
                'High',
                f'Schedule meeting with {insurer_info["insurer"]}',
                f'{insurer_info["rejections"]} rejections - discuss patterns',
                'Within 14 days',
                'Pending',
                'Management'
            ])
        
        # Process improvements
        process_actions = [
            ['Medium', 'Implement daily rejection monitoring', 'Dashboard for real-time tracking', 'Within 30 days', 'Pending', 'IT Team'],
            ['Medium', 'Create insurer-specific guidelines', 'Reduce common rejection patterns', 'Within 30 days', 'Pending', 'Operations'],
            ['Low', 'Staff training on rejection patterns', 'Improve submission quality', 'Within 60 days', 'Pending', 'Training Team']
        ]
        
        action_data.extend(process_actions)
        
        with open('Action_Tracker.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(action_data)
        
        print("✅ Action tracker saved to 'Action_Tracker.csv'")
        return action_data
    
    def generate_all_reports(self):
        """Generate all enhanced reports"""
        print("🚀 GENERATING ENHANCED REPORTS")
        print("=" * 50)
        
        self.create_executive_report()
        self.create_detailed_excel_data()
        self.create_trend_analysis()
        self.create_action_tracker()
        
        print("\n✨ ALL REPORTS GENERATED SUCCESSFULLY!")
        print("\nFiles created:")
        print("📄 Executive_Claims_Report.txt - Professional executive summary")
        print("📊 Claims_Summary_Analysis.csv - Key metrics and KPIs")
        print("🏢 Insurer_Performance_Analysis.csv - Detailed insurer breakdown")
        print("💰 High_Value_Rejections_Priority.csv - Priority appeals list")
        print("📈 Daily_Trend_Analysis.csv - Temporal patterns")
        print("✅ Action_Tracker.csv - Actionable task list")

if __name__ == "__main__":
    reporter = EnhancedReporter('merged_all_data.csv')
    reporter.generate_all_reports()
