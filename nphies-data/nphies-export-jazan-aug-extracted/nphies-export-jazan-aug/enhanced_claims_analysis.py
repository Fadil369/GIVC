#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from collections import defaultdict, Counter
from datetime import datetime

class EnhancedClaimsAnalyzer:
    def __init__(self, csv_file, excel_file=None):
        self.csv_file = csv_file
        self.excel_file = excel_file
        self.csv_data = []
        self.excel_data = []
        self.headers = []
        
    def load_csv_data(self):
        """Load CSV data"""
        print("Loading CSV data...")
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames
            self.csv_data = list(reader)
        print(f"Loaded {len(self.csv_data)} CSV records")
    
    def extract_excel_data(self):
        """Extract Excel data using csvkit if available, or provide manual instructions"""
        if not self.excel_file:
            return
            
        print(f"\nAttempting to extract Excel data from {self.excel_file}...")
        
        # Try to convert Excel to CSV using in2csv (from csvkit)
        try:
            result = subprocess.run(['in2csv', self.excel_file], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Parse the CSV output
                lines = result.stdout.strip().split('\n')
                if lines:
                    reader = csv.DictReader(lines)
                    self.excel_data = list(reader)
                    print(f"Successfully extracted {len(self.excel_data)} Excel records")
                    return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("Excel extraction failed. Manual analysis required.")
        print("To analyze Excel file manually:")
        print("1. Open the Excel file")
        print("2. Export each sheet as CSV")
        print("3. Run this script again with the CSV files")
    
    def advanced_rejection_patterns(self):
        """Advanced pattern analysis"""
        print("\n=== ADVANCED REJECTION PATTERNS ===")
        
        rejected_claims = [row for row in self.csv_data if row.get('Status') == 'Rejected']
        
        # Pattern 1: Rejection by encounter class and service type
        encounter_service_rejections = Counter()
        for row in rejected_claims:
            encounter = row.get('Encounter Class', 'Unknown')
            service = row.get('Service Event Type', 'Unknown')
            encounter_service_rejections[f"{encounter}-{service}"] += 1
        
        print("Rejection Patterns by Encounter-Service Type:")
        for pattern, count in encounter_service_rejections.most_common(10):
            print(f"  {pattern}: {count} rejections")
        
        # Pattern 2: High-value vs Low-value rejection rates
        high_value_rejections = 0
        low_value_rejections = 0
        high_value_total = 0
        low_value_total = 0
        
        for row in self.csv_data:
            try:
                net_amount = float(row.get('Net Amount', 0) or 0)
                status = row.get('Status', '')
                
                if net_amount > 1000:  # High value threshold
                    high_value_total += 1
                    if status == 'Rejected':
                        high_value_rejections += 1
                else:
                    low_value_total += 1
                    if status == 'Rejected':
                        low_value_rejections += 1
            except:
                continue
        
        if high_value_total > 0 and low_value_total > 0:
            high_value_rate = (high_value_rejections / high_value_total) * 100
            low_value_rate = (low_value_rejections / low_value_total) * 100
            
            print(f"\nValue-Based Rejection Analysis:")
            print(f"  High-value claims (>1000 SAR): {high_value_rate:.1f}% rejection rate")
            print(f"  Low-value claims (≤1000 SAR): {low_value_rate:.1f}% rejection rate")
    
    def insurer_specific_analysis(self):
        """Detailed insurer-specific analysis"""
        print("\n=== INSURER-SPECIFIC DEEP DIVE ===")
        
        insurer_stats = defaultdict(lambda: {
            'total': 0, 'rejected': 0, 'partial': 0, 'approved': 0,
            'net_amount': 0, 'approved_amount': 0, 'claim_types': Counter()
        })
        
        for row in self.csv_data:
            insurer = row.get('Insurer Name', 'Unknown')
            status = row.get('Status', 'Unknown')
            claim_type = row.get('Claim Type', 'Unknown')
            
            insurer_stats[insurer]['total'] += 1
            insurer_stats[insurer]['claim_types'][claim_type] += 1
            
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
        
        # Top problematic insurers
        problematic_insurers = []
        for insurer, stats in insurer_stats.items():
            if stats['total'] >= 50:  # Minimum volume threshold
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                financial_loss = stats['net_amount'] - stats['approved_amount']
                problematic_insurers.append((insurer, rejection_rate, stats['total'], financial_loss))
        
        problematic_insurers.sort(key=lambda x: x[3], reverse=True)  # Sort by financial loss
        
        print("Top Insurers by Financial Impact:")
        for insurer, rate, total, loss in problematic_insurers[:5]:
            print(f"  {insurer}:")
            print(f"    Rejection Rate: {rate:.1f}%")
            print(f"    Total Claims: {total}")
            print(f"    Financial Loss: {loss:,.2f} SAR")
    
    def generate_recovery_plan(self):
        """Generate specific recovery and improvement plan"""
        print("\n=== DETAILED RECOVERY PLAN ===")
        
        rejected_claims = [row for row in self.csv_data if row.get('Status') == 'Rejected']
        
        # Categorize rejections by potential recovery
        high_recovery_potential = []
        medium_recovery_potential = []
        
        for row in rejected_claims:
            try:
                net_amount = float(row.get('Net Amount', 0) or 0)
                insurer = row.get('Insurer Name', '')
                transaction_id = row.get('Transaction Identifier', '')
                
                if net_amount > 5000:  # High-value claims
                    high_recovery_potential.append((transaction_id, net_amount, insurer))
                elif net_amount > 1000:
                    medium_recovery_potential.append((transaction_id, net_amount, insurer))
            except:
                continue
        
        high_recovery_potential.sort(key=lambda x: x[1], reverse=True)
        medium_recovery_potential.sort(key=lambda x: x[1], reverse=True)
        
        print("PHASE 1 - HIGH PRIORITY RECOVERY (>5000 SAR):")
        total_high_value = sum(x[1] for x in high_recovery_potential)
        print(f"  Total Potential Recovery: {total_high_value:,.2f} SAR")
        print(f"  Number of Claims: {len(high_recovery_potential)}")
        
        print("\n  Top 10 Claims for Immediate Appeal:")
        for i, (trans_id, amount, insurer) in enumerate(high_recovery_potential[:10], 1):
            print(f"    {i}. Transaction {trans_id}: {amount:,.2f} SAR ({insurer})")
        
        print(f"\nPHASE 2 - MEDIUM PRIORITY RECOVERY (1000-5000 SAR):")
        total_medium_value = sum(x[1] for x in medium_recovery_potential)
        print(f"  Total Potential Recovery: {total_medium_value:,.2f} SAR")
        print(f"  Number of Claims: {len(medium_recovery_potential)}")
        
        # Process improvement recommendations
        print("\nPROCESS IMPROVEMENT ROADMAP:")
        print("Week 1-2:")
        print("  - Contact top 3 rejecting insurers for rejection reason clarification")
        print("  - Initiate appeals for top 20 high-value rejections")
        print("  - Implement daily rejection monitoring dashboard")
        
        print("\nWeek 3-4:")
        print("  - Develop insurer-specific submission checklists")
        print("  - Train staff on common rejection patterns")
        print("  - Establish weekly insurer communication schedule")
        
        print("\nMonth 2:")
        print("  - Implement automated pre-submission validation")
        print("  - Create rejection prediction model")
        print("  - Establish KPIs for approval rates by insurer")
    
    def export_actionable_reports(self):
        """Export specific actionable reports"""
        print("\n=== EXPORTING ACTIONABLE REPORTS ===")
        
        # High-value rejections for immediate action
        high_value_rejections = []
        for row in self.csv_data:
            if row.get('Status') == 'Rejected':
                try:
                    net_amount = float(row.get('Net Amount', 0) or 0)
                    if net_amount > 1000:
                        high_value_rejections.append(row)
                except:
                    continue
        
        # Sort by net amount descending
        high_value_rejections.sort(key=lambda x: float(x.get('Net Amount', 0) or 0), reverse=True)
        
        # Export high-value rejections
        with open('high_value_rejections_for_appeal.csv', 'w', newline='', encoding='utf-8') as f:
            if high_value_rejections:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(high_value_rejections)
        
        print(f"Exported {len(high_value_rejections)} high-value rejections to 'high_value_rejections_for_appeal.csv'")
        
        # Create insurer contact list
        insurer_contacts = {}
        rejection_counts = Counter()
        
        for row in self.csv_data:
            if row.get('Status') == 'Rejected':
                insurer = row.get('Insurer Name', 'Unknown')
                receiver_license = row.get('Receiver License', '')
                rejection_counts[insurer] += 1
                
                if insurer not in insurer_contacts:
                    insurer_contacts[insurer] = {
                        'license': receiver_license,
                        'rejections': 0,
                        'priority': 'Low'
                    }
                insurer_contacts[insurer]['rejections'] = rejection_counts[insurer]
        
        # Set priority levels
        for insurer, data in insurer_contacts.items():
            if data['rejections'] > 200:
                data['priority'] = 'Critical'
            elif data['rejections'] > 100:
                data['priority'] = 'High'
            elif data['rejections'] > 50:
                data['priority'] = 'Medium'
        
        # Export insurer contact plan
        with open('insurer_contact_priority_list.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Insurer Name', 'License', 'Rejection Count', 'Priority', 'Action Required'])
            
            for insurer, data in sorted(insurer_contacts.items(), 
                                      key=lambda x: x[1]['rejections'], reverse=True):
                action = "Immediate meeting required" if data['priority'] == 'Critical' else \
                        "Schedule call within 1 week" if data['priority'] == 'High' else \
                        "Email inquiry" if data['priority'] == 'Medium' else "Monitor"
                
                writer.writerow([insurer, data['license'], data['rejections'], 
                               data['priority'], action])
        
        print("Exported insurer contact priority list to 'insurer_contact_priority_list.csv'")
        
        # Create executive summary
        summary_stats = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_claims': len(self.csv_data),
            'total_rejections': len([r for r in self.csv_data if r.get('Status') == 'Rejected']),
            'total_financial_loss': sum(float(r.get('Net Amount', 0) or 0) - float(r.get('Approved Amount', 0) or 0) 
                                      for r in self.csv_data),
            'high_value_rejections_count': len(high_value_rejections),
            'top_rejecting_insurer': max(rejection_counts.items(), key=lambda x: x[1])[0] if rejection_counts else 'N/A',
            'immediate_actions_required': len([i for i in insurer_contacts.values() if i['priority'] in ['Critical', 'High']])
        }
        
        with open('executive_summary.json', 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print("Exported executive summary to 'executive_summary.json'")
    
    def run_enhanced_analysis(self):
        """Run complete enhanced analysis"""
        print("ENHANCED NPHIES CLAIMS ANALYSIS")
        print("=" * 60)
        
        self.load_csv_data()
        self.extract_excel_data()
        self.advanced_rejection_patterns()
        self.insurer_specific_analysis()
        self.generate_recovery_plan()
        self.export_actionable_reports()
        
        print("\n" + "=" * 60)
        print("ENHANCED ANALYSIS COMPLETE")
        print("\nGenerated Files:")
        print("- high_value_rejections_for_appeal.csv (Priority appeals)")
        print("- insurer_contact_priority_list.csv (Contact strategy)")
        print("- executive_summary.json (Key metrics)")

if __name__ == "__main__":
    analyzer = EnhancedClaimsAnalyzer('merged_all_data.csv', 'HANHJ_StatementOfAccount_08-2025.xlsx')
    analyzer.run_enhanced_analysis()
