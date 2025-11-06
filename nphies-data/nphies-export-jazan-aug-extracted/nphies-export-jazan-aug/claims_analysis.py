#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
import os

class ClaimsAnalyzer:
    def __init__(self, csv_file, excel_file=None):
        self.csv_file = csv_file
        self.excel_file = excel_file
        self.data = []
        self.headers = []
        self.analysis_results = {}
        
    def load_csv_data(self):
        """Load and parse CSV data"""
        print("Loading CSV data...")
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames
            self.data = list(reader)
        print(f"Loaded {len(self.data)} records")
        
    def basic_statistics(self):
        """Generate basic statistics"""
        print("\n=== BASIC STATISTICS ===")
        
        # Status distribution
        status_counts = Counter(row.get('Status', 'Unknown') for row in self.data)
        total_records = len(self.data)
        
        print(f"Total Records: {total_records}")
        print("\nStatus Distribution:")
        for status, count in status_counts.most_common():
            percentage = (count / total_records) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        # Financial analysis
        net_amounts = []
        approved_amounts = []
        
        for row in self.data:
            try:
                net_amt = float(row.get('Net Amount', 0) or 0)
                approved_amt = float(row.get('Approved Amount', 0) or 0)
                net_amounts.append(net_amt)
                approved_amounts.append(approved_amt)
            except (ValueError, TypeError):
                continue
        
        if net_amounts:
            total_net = sum(net_amounts)
            total_approved = sum(approved_amounts)
            rejection_loss = total_net - total_approved
            
            print(f"\nFinancial Summary:")
            print(f"  Total Net Amount: {total_net:,.2f} SAR")
            print(f"  Total Approved: {total_approved:,.2f} SAR")
            print(f"  Financial Loss (Rejections): {rejection_loss:,.2f} SAR")
            print(f"  Approval Rate: {(total_approved/total_net)*100:.1f}%")
        
        return status_counts
    
    def rejection_analysis(self):
        """Detailed rejection analysis"""
        print("\n=== REJECTION ANALYSIS ===")
        
        rejected_claims = [row for row in self.data if row.get('Status') == 'Rejected']
        partial_claims = [row for row in self.data if row.get('Status') == 'Partial']
        
        print(f"Rejected Claims: {len(rejected_claims)}")
        print(f"Partial Claims: {len(partial_claims)}")
        
        # Rejection by insurer
        rejection_by_insurer = Counter()
        partial_by_insurer = Counter()
        
        for row in rejected_claims:
            insurer = row.get('Insurer Name', 'Unknown')
            rejection_by_insurer[insurer] += 1
            
        for row in partial_claims:
            insurer = row.get('Insurer Name', 'Unknown')
            partial_by_insurer[insurer] += 1
        
        print("\nTop Rejecting Insurers:")
        for insurer, count in rejection_by_insurer.most_common(10):
            print(f"  {insurer}: {count} rejections")
        
        # Rejection by claim type
        rejection_by_type = Counter()
        for row in rejected_claims:
            claim_type = f"{row.get('Claim Type', 'Unknown')}-{row.get('Claim Sub Type', 'Unknown')}"
            rejection_by_type[claim_type] += 1
        
        print("\nRejections by Claim Type:")
        for claim_type, count in rejection_by_type.most_common(5):
            print(f"  {claim_type}: {count} rejections")
        
        return rejected_claims, partial_claims
    
    def temporal_analysis(self):
        """Analyze trends over time"""
        print("\n=== TEMPORAL ANALYSIS ===")
        
        # Group by submission date
        daily_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'approved': 0, 'partial': 0})
        
        for row in self.data:
            date_str = row.get('Submission Date', '')
            if date_str:
                try:
                    # Parse date (assuming DD-MM-YYYY format)
                    date_parts = date_str.split(' ')[0].split('-')
                    if len(date_parts) == 3:
                        day = date_parts[0]
                        month = date_parts[1]
                        date_key = f"{month}-{day}"
                        
                        daily_stats[date_key]['total'] += 1
                        status = row.get('Status', 'Unknown')
                        if status == 'Rejected':
                            daily_stats[date_key]['rejected'] += 1
                        elif status == 'Approved':
                            daily_stats[date_key]['approved'] += 1
                        elif status == 'Partial':
                            daily_stats[date_key]['partial'] += 1
                except:
                    continue
        
        print("Daily Rejection Rates (Top 10 worst days):")
        daily_rejection_rates = []
        for date, stats in daily_stats.items():
            if stats['total'] > 0:
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                daily_rejection_rates.append((date, rejection_rate, stats['total'], stats['rejected']))
        
        daily_rejection_rates.sort(key=lambda x: x[1], reverse=True)
        for date, rate, total, rejected in daily_rejection_rates[:10]:
            print(f"  {date}: {rate:.1f}% ({rejected}/{total})")
    
    def provider_analysis(self):
        """Analyze provider performance"""
        print("\n=== PROVIDER ANALYSIS ===")
        
        provider_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'net_amount': 0, 'approved_amount': 0})
        
        for row in self.data:
            provider = row.get('Provider Name', 'Unknown')
            status = row.get('Status', 'Unknown')
            
            provider_stats[provider]['total'] += 1
            if status == 'Rejected':
                provider_stats[provider]['rejected'] += 1
            
            try:
                net_amt = float(row.get('Net Amount', 0) or 0)
                approved_amt = float(row.get('Approved Amount', 0) or 0)
                provider_stats[provider]['net_amount'] += net_amt
                provider_stats[provider]['approved_amount'] += approved_amt
            except:
                continue
        
        # Calculate rejection rates
        provider_rejection_rates = []
        for provider, stats in provider_stats.items():
            if stats['total'] >= 10:  # Only providers with significant volume
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                financial_loss = stats['net_amount'] - stats['approved_amount']
                provider_rejection_rates.append((provider, rejection_rate, stats['total'], financial_loss))
        
        provider_rejection_rates.sort(key=lambda x: x[1], reverse=True)
        
        print("Provider Rejection Rates (min 10 claims):")
        for provider, rate, total, loss in provider_rejection_rates[:10]:
            print(f"  {provider}: {rate:.1f}% ({total} claims, {loss:,.2f} SAR loss)")
    
    def generate_action_plan(self):
        """Generate actionable recommendations"""
        print("\n=== ACTION PLAN & RECOMMENDATIONS ===")
        
        rejected_claims = [row for row in self.data if row.get('Status') == 'Rejected']
        
        # Top rejection reasons by insurer
        insurer_rejections = Counter()
        for row in rejected_claims:
            insurer = row.get('Insurer Name', 'Unknown')
            insurer_rejections[insurer] += 1
        
        print("IMMEDIATE ACTIONS:")
        print("1. Focus on Top Rejecting Insurers:")
        for insurer, count in insurer_rejections.most_common(3):
            print(f"   - Contact {insurer} ({count} rejections) for rejection reason analysis")
        
        # High-value rejections
        high_value_rejections = []
        for row in rejected_claims:
            try:
                net_amt = float(row.get('Net Amount', 0) or 0)
                if net_amt > 1000:  # High-value threshold
                    high_value_rejections.append((row.get('Transaction Identifier'), net_amt, row.get('Insurer Name')))
            except:
                continue
        
        high_value_rejections.sort(key=lambda x: x[1], reverse=True)
        
        print("\n2. Priority High-Value Rejections for Review:")
        for trans_id, amount, insurer in high_value_rejections[:5]:
            print(f"   - Transaction {trans_id}: {amount:,.2f} SAR ({insurer})")
        
        print("\n3. Process Improvements:")
        print("   - Implement pre-submission validation for top rejection patterns")
        print("   - Establish direct communication channels with high-rejection insurers")
        print("   - Create insurer-specific submission guidelines")
        print("   - Implement real-time claim status monitoring")
        
        print("\n4. Financial Recovery:")
        total_rejected_value = sum(float(row.get('Net Amount', 0) or 0) for row in rejected_claims)
        print(f"   - Total rejected value: {total_rejected_value:,.2f} SAR")
        print("   - Prioritize appeals for high-value rejections")
        print("   - Implement rejection trend alerts")
    
    def export_detailed_report(self):
        """Export detailed analysis to files"""
        print("\n=== EXPORTING DETAILED REPORTS ===")
        
        # Create rejection details CSV
        rejected_claims = [row for row in self.data if row.get('Status') in ['Rejected', 'Partial']]
        
        with open('rejection_analysis_detailed.csv', 'w', newline='', encoding='utf-8') as f:
            if rejected_claims:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(rejected_claims)
        
        print(f"Exported {len(rejected_claims)} rejected/partial claims to 'rejection_analysis_detailed.csv'")
        
        # Create summary report
        summary = {
            'total_claims': len(self.data),
            'rejected_claims': len([r for r in self.data if r.get('Status') == 'Rejected']),
            'partial_claims': len([r for r in self.data if r.get('Status') == 'Partial']),
            'approved_claims': len([r for r in self.data if r.get('Status') == 'Approved']),
            'analysis_date': datetime.now().isoformat()
        }
        
        with open('claims_analysis_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("Exported summary to 'claims_analysis_summary.json'")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        print("NPHIES CLAIMS REJECTION ANALYSIS")
        print("=" * 50)
        
        self.load_csv_data()
        self.basic_statistics()
        self.rejection_analysis()
        self.temporal_analysis()
        self.provider_analysis()
        self.generate_action_plan()
        self.export_detailed_report()
        
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE")

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = ClaimsAnalyzer('merged_all_data.csv', 'HANHJ_StatementOfAccount_08-2025.xlsx')
    
    # Run analysis
    analyzer.run_full_analysis()
