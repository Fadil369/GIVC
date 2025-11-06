#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

class ExcelWorkbookGenerator:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def create_excel_workbook_structure(self):
        """Create structured data for Excel workbook with multiple sheets"""
        
        workbook_data = {}
        
        # Sheet 1: Executive Dashboard
        dashboard_data = []
        dashboard_data.append(['NPHIES Claims Analysis Dashboard', '', '', ''])
        dashboard_data.append([f'Generated: {datetime.now().strftime("%B %d, %Y")}', '', '', ''])
        dashboard_data.append(['', '', '', ''])
        
        # KPIs
        total_claims = len(self.data)
        rejected = len([r for r in self.data if r.get('Status') == 'Rejected'])
        approved = len([r for r in self.data if r.get('Status') == 'Approved'])
        partial = len([r for r in self.data if r.get('Status') == 'Partial'])
        
        total_net = sum(float(r.get('Net Amount', 0) or 0) for r in self.data)
        total_approved_amt = sum(float(r.get('Approved Amount', 0) or 0) for r in self.data)
        
        dashboard_data.extend([
            ['KEY PERFORMANCE INDICATORS', '', '', ''],
            ['Metric', 'Value', 'Percentage', 'Status'],
            ['Total Claims', total_claims, '100.0%', ''],
            ['Approved Claims', approved, f'{(approved/total_claims)*100:.1f}%', '✅ Good'],
            ['Rejected Claims', rejected, f'{(rejected/total_claims)*100:.1f}%', '❌ Needs Attention'],
            ['Partial Claims', partial, f'{(partial/total_claims)*100:.1f}%', '⚠️ Monitor'],
            ['', '', '', ''],
            ['FINANCIAL OVERVIEW', '', '', ''],
            ['Total Claim Value (SAR)', f'{total_net:,.2f}', '', ''],
            ['Approved Amount (SAR)', f'{total_approved_amt:,.2f}', '', ''],
            ['Financial Loss (SAR)', f'{total_net - total_approved_amt:,.2f}', '', '❌ Critical'],
            ['Recovery Rate', f'{(total_approved_amt/total_net)*100:.1f}%', '', '⚠️ Below Target']
        ])
        
        workbook_data['Dashboard'] = dashboard_data
        
        # Sheet 2: Insurer Analysis
        insurer_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'partial': 0, 'approved': 0, 'net_amount': 0, 'approved_amount': 0})
        
        for row in self.data:
            insurer = row.get('Insurer Name', 'Unknown')
            status = row.get('Status', 'Unknown')
            
            insurer_stats[insurer]['total'] += 1
            if status == 'Rejected':
                insurer_stats[insurer]['rejected'] += 1
            elif status == 'Partial':
                insurer_stats[insurer]['partial'] += 1
            elif status == 'Approved':
                insurer_stats[insurer]['approved'] += 1
            
            try:
                net_amt = float(row.get('Net Amount', 0) or 0)
                approved_amt = float(row.get('Approved Amount', 0) or 0)
                insurer_stats[insurer]['net_amount'] += net_amt
                insurer_stats[insurer]['approved_amount'] += approved_amt
            except:
                continue
        
        insurer_data = [
            ['INSURER PERFORMANCE ANALYSIS', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['Insurer Name', 'Total Claims', 'Approved', 'Rejected', 'Partial', 'Rejection Rate %', 'Net Amount SAR', 'Approved SAR', 'Financial Loss SAR']
        ]
        
        for insurer, stats in sorted(insurer_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            if stats['total'] >= 10:
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                financial_loss = stats['net_amount'] - stats['approved_amount']
                
                insurer_data.append([
                    insurer,
                    stats['total'],
                    stats['approved'],
                    stats['rejected'],
                    stats['partial'],
                    f'{rejection_rate:.1f}%',
                    f'{stats["net_amount"]:,.2f}',
                    f'{stats["approved_amount"]:,.2f}',
                    f'{financial_loss:,.2f}'
                ])
        
        workbook_data['Insurer_Analysis'] = insurer_data
        
        # Sheet 3: High-Value Rejections
        high_value_data = [
            ['HIGH-VALUE REJECTIONS FOR IMMEDIATE APPEAL', '', '', '', '', ''],
            ['Priority appeals for claims > 5,000 SAR', '', '', '', '', ''],
            ['', '', '', '', '', ''],
            ['Rank', 'Transaction ID', 'Amount SAR', 'Insurer', 'Submission Date', 'Patient ID']
        ]
        
        high_value_rejections = []
        for row in self.data:
            if row.get('Status') == 'Rejected':
                try:
                    amount = float(row.get('Net Amount', 0) or 0)
                    if amount > 5000:
                        high_value_rejections.append({
                            'trans_id': row.get('Transaction Identifier', ''),
                            'amount': amount,
                            'insurer': row.get('Insurer Name', ''),
                            'date': row.get('Submission Date', ''),
                            'patient': row.get('Patient Identifier', '')
                        })
                except:
                    continue
        
        high_value_rejections.sort(key=lambda x: x['amount'], reverse=True)
        
        for i, rejection in enumerate(high_value_rejections[:50], 1):
            high_value_data.append([
                i,
                rejection['trans_id'],
                f'{rejection["amount"]:,.2f}',
                rejection['insurer'],
                rejection['date'],
                rejection['patient']
            ])
        
        workbook_data['High_Value_Appeals'] = high_value_data
        
        # Sheet 4: Daily Trends
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
        
        trend_data = [
            ['DAILY SUBMISSION TRENDS', '', '', '', '', ''],
            ['Analysis of claim patterns by day of month', '', '', '', '', ''],
            ['', '', '', '', '', ''],
            ['Day', 'Total Claims', 'Approved', 'Rejected', 'Rejection Rate %', 'Total Value SAR']
        ]
        
        for day in sorted(daily_stats.keys()):
            stats = daily_stats[day]
            if stats['total'] > 0:
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                trend_data.append([
                    day,
                    stats['total'],
                    stats['approved'],
                    stats['rejected'],
                    f'{rejection_rate:.1f}%',
                    f'{stats["net_amount"]:,.2f}'
                ])
        
        workbook_data['Daily_Trends'] = trend_data
        
        # Sheet 5: Action Plan
        action_data = [
            ['CLAIMS RECOVERY ACTION PLAN', '', '', '', '', ''],
            [f'Generated: {datetime.now().strftime("%B %d, %Y")}', '', '', '', '', ''],
            ['', '', '', '', '', ''],
            ['Priority', 'Action Item', 'Description', 'Target Date', 'Owner', 'Status']
        ]
        
        # Add high-priority actions
        for i, rejection in enumerate(high_value_rejections[:10], 1):
            action_data.append([
                'CRITICAL',
                f'Appeal Transaction {rejection["trans_id"]}',
                f'{rejection["amount"]:,.0f} SAR rejection from {rejection["insurer"]}',
                'Within 7 days',
                'Claims Manager',
                'PENDING'
            ])
        
        # Add strategic actions
        strategic_actions = [
            ['HIGH', 'Meet with Bupa Arabia', 'Address high rejection rate (24.7%)', 'Within 14 days', 'Senior Management', 'PENDING'],
            ['HIGH', 'Meet with AL Jazira Takaful', 'Address critical rejection rate (52.9%)', 'Within 14 days', 'Senior Management', 'PENDING'],
            ['MEDIUM', 'Implement daily monitoring', 'Real-time rejection tracking dashboard', 'Within 30 days', 'IT Team', 'PENDING'],
            ['MEDIUM', 'Staff training program', 'Reduce common rejection patterns', 'Within 45 days', 'Training Team', 'PENDING'],
            ['LOW', 'Process automation', 'Automated pre-submission validation', 'Within 90 days', 'IT Team', 'PENDING']
        ]
        
        action_data.extend(strategic_actions)
        workbook_data['Action_Plan'] = action_data
        
        return workbook_data
    
    def export_excel_sheets(self):
        """Export all sheets as separate CSV files for Excel import"""
        
        workbook_data = self.create_excel_workbook_structure()
        
        print("📊 CREATING EXCEL WORKBOOK STRUCTURE")
        print("=" * 50)
        
        for sheet_name, sheet_data in workbook_data.items():
            filename = f'Excel_Sheet_{sheet_name}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(sheet_data)
            
            print(f"✅ Created: {filename}")
        
        # Create import instructions
        instructions = [
            "EXCEL IMPORT INSTRUCTIONS",
            "=" * 30,
            "",
            "To create the complete Excel workbook:",
            "",
            "1. Open Excel",
            "2. Create a new workbook",
            "3. Import each CSV file as a separate sheet:",
            "",
            "   Sheet 1: Dashboard (Excel_Sheet_Dashboard.csv)",
            "   Sheet 2: Insurer Analysis (Excel_Sheet_Insurer_Analysis.csv)", 
            "   Sheet 3: High-Value Appeals (Excel_Sheet_High_Value_Appeals.csv)",
            "   Sheet 4: Daily Trends (Excel_Sheet_Daily_Trends.csv)",
            "   Sheet 5: Action Plan (Excel_Sheet_Action_Plan.csv)",
            "",
            "4. Apply formatting:",
            "   - Bold headers",
            "   - Color-code priority levels",
            "   - Add charts for trends",
            "   - Format currency columns",
            "",
            "5. Save as Excel workbook (.xlsx)",
            "",
            "RECOMMENDED FORMATTING:",
            "- Critical items: Red background",
            "- High priority: Orange background", 
            "- Medium priority: Yellow background",
            "- Completed items: Green background"
        ]
        
        with open('Excel_Import_Instructions.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(instructions))
        
        print(f"📋 Created: Excel_Import_Instructions.txt")
        
        # Create summary statistics
        summary_stats = {
            'total_sheets': len(workbook_data),
            'high_value_rejections': len([r for r in self.data if r.get('Status') == 'Rejected' and float(r.get('Net Amount', 0) or 0) > 5000]),
            'total_potential_recovery': sum(float(r.get('Net Amount', 0) or 0) for r in self.data if r.get('Status') == 'Rejected' and float(r.get('Net Amount', 0) or 0) > 5000),
            'critical_actions': 10,
            'generated_at': datetime.now().isoformat()
        }
        
        with open('Excel_Workbook_Summary.json', 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print(f"📈 Created: Excel_Workbook_Summary.json")
        
        print("\n🎉 EXCEL WORKBOOK STRUCTURE COMPLETE!")
        print(f"\nTotal files created: {len(workbook_data) + 2}")
        print(f"High-value rejections identified: {summary_stats['high_value_rejections']}")
        print(f"Potential recovery value: {summary_stats['total_potential_recovery']:,.2f} SAR")

if __name__ == "__main__":
    generator = ExcelWorkbookGenerator('merged_all_data.csv')
    generator.export_excel_sheets()
