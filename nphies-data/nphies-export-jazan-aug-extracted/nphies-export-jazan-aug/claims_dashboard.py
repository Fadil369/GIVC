#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

class ClaimsDashboard:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def generate_dashboard_report(self):
        """Generate comprehensive dashboard report"""
        print("NPHIES CLAIMS DASHBOARD - EXECUTIVE SUMMARY")
        print("=" * 70)
        
        # Key Performance Indicators
        total_claims = len(self.data)
        rejected_claims = len([r for r in self.data if r.get('Status') == 'Rejected'])
        approved_claims = len([r for r in self.data if r.get('Status') == 'Approved'])
        partial_claims = len([r for r in self.data if r.get('Status') == 'Partial'])
        
        total_net = sum(float(r.get('Net Amount', 0) or 0) for r in self.data)
        total_approved_amount = sum(float(r.get('Approved Amount', 0) or 0) for r in self.data)
        
        print(f"📊 KEY PERFORMANCE INDICATORS")
        print(f"   Total Claims Processed: {total_claims:,}")
        print(f"   Approval Rate: {(approved_claims/total_claims)*100:.1f}%")
        print(f"   Rejection Rate: {(rejected_claims/total_claims)*100:.1f}%")
        print(f"   Partial Approval Rate: {(partial_claims/total_claims)*100:.1f}%")
        print(f"   Financial Recovery Rate: {(total_approved_amount/total_net)*100:.1f}%")
        print(f"   Total Revenue at Risk: {total_net-total_approved_amount:,.2f} SAR")
        
        # Critical Alerts
        print(f"\n🚨 CRITICAL ALERTS")
        
        # High rejection rate insurers
        insurer_rejections = defaultdict(lambda: {'total': 0, 'rejected': 0})
        for row in self.data:
            insurer = row.get('Insurer Name', 'Unknown')
            insurer_rejections[insurer]['total'] += 1
            if row.get('Status') == 'Rejected':
                insurer_rejections[insurer]['rejected'] += 1
        
        critical_insurers = []
        for insurer, stats in insurer_rejections.items():
            if stats['total'] >= 100:  # Minimum volume
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                if rejection_rate > 20:  # Critical threshold
                    critical_insurers.append((insurer, rejection_rate, stats['rejected']))
        
        critical_insurers.sort(key=lambda x: x[1], reverse=True)
        
        if critical_insurers:
            print(f"   High Rejection Rate Insurers (>20%):")
            for insurer, rate, count in critical_insurers[:5]:
                print(f"   ⚠️  {insurer}: {rate:.1f}% ({count} rejections)")
        
        # Financial impact analysis
        print(f"\n💰 FINANCIAL IMPACT ANALYSIS")
        
        # Top financial losses by insurer
        insurer_losses = defaultdict(float)
        for row in self.data:
            insurer = row.get('Insurer Name', 'Unknown')
            try:
                net_amt = float(row.get('Net Amount', 0) or 0)
                approved_amt = float(row.get('Approved Amount', 0) or 0)
                loss = net_amt - approved_amt
                insurer_losses[insurer] += loss
            except:
                continue
        
        top_losses = sorted(insurer_losses.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   Top Financial Losses by Insurer:")
        for insurer, loss in top_losses:
            print(f"   💸 {insurer}: {loss:,.2f} SAR")
        
        # Trend analysis
        print(f"\n📈 TREND ANALYSIS")
        
        # Daily submission patterns
        daily_stats = defaultdict(lambda: {'total': 0, 'rejected': 0})
        for row in self.data:
            date_str = row.get('Submission Date', '')
            if date_str:
                try:
                    date_parts = date_str.split(' ')[0].split('-')
                    if len(date_parts) == 3:
                        day = int(date_parts[0])
                        daily_stats[day]['total'] += 1
                        if row.get('Status') == 'Rejected':
                            daily_stats[day]['rejected'] += 1
                except:
                    continue
        
        # Find peak rejection days
        peak_rejection_days = []
        for day, stats in daily_stats.items():
            if stats['total'] >= 50:  # Minimum volume
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                peak_rejection_days.append((day, rejection_rate, stats['total']))
        
        peak_rejection_days.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   Peak Rejection Days:")
        for day, rate, total in peak_rejection_days[:5]:
            print(f"   📅 Day {day}: {rate:.1f}% rejection rate ({total} claims)")
        
        # Operational insights
        print(f"\n🔍 OPERATIONAL INSIGHTS")
        
        # Claim type performance
        claim_type_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'revenue': 0})
        for row in self.data:
            claim_type = f"{row.get('Claim Type', 'Unknown')}-{row.get('Claim Sub Type', 'Unknown')}"
            claim_type_stats[claim_type]['total'] += 1
            if row.get('Status') == 'Rejected':
                claim_type_stats[claim_type]['rejected'] += 1
            try:
                claim_type_stats[claim_type]['revenue'] += float(row.get('Net Amount', 0) or 0)
            except:
                continue
        
        print(f"   Claim Type Performance:")
        for claim_type, stats in sorted(claim_type_stats.items(), 
                                       key=lambda x: x[1]['revenue'], reverse=True)[:5]:
            if stats['total'] > 0:
                rejection_rate = (stats['rejected'] / stats['total']) * 100
                print(f"   📋 {claim_type}: {rejection_rate:.1f}% rejection, {stats['revenue']:,.0f} SAR")
        
        # Action priorities
        print(f"\n🎯 IMMEDIATE ACTION PRIORITIES")
        
        # High-value rejections needing immediate attention
        high_value_rejections = []
        for row in self.data:
            if row.get('Status') == 'Rejected':
                try:
                    net_amount = float(row.get('Net Amount', 0) or 0)
                    if net_amount > 10000:  # Very high value
                        high_value_rejections.append((
                            row.get('Transaction Identifier'),
                            net_amount,
                            row.get('Insurer Name'),
                            row.get('Submission Date')
                        ))
                except:
                    continue
        
        high_value_rejections.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   Priority 1 - Ultra High-Value Rejections (>10K SAR):")
        for trans_id, amount, insurer, date in high_value_rejections[:10]:
            print(f"   🔥 Transaction {trans_id}: {amount:,.0f} SAR ({insurer}) - {date}")
        
        # Recovery potential
        total_recovery_potential = sum(x[1] for x in high_value_rejections)
        print(f"\n💡 RECOVERY POTENTIAL")
        print(f"   Ultra High-Value Claims: {total_recovery_potential:,.2f} SAR")
        print(f"   Estimated Recovery (30% success): {total_recovery_potential * 0.3:,.2f} SAR")
        
        # Recommendations
        print(f"\n📋 STRATEGIC RECOMMENDATIONS")
        print(f"   1. Immediate: Appeal top 20 high-value rejections")
        print(f"   2. This Week: Meet with top 3 rejecting insurers")
        print(f"   3. This Month: Implement automated validation for common rejection patterns")
        print(f"   4. Ongoing: Daily monitoring dashboard for rejection trends")
        
        return {
            'total_claims': total_claims,
            'rejection_rate': (rejected_claims/total_claims)*100,
            'financial_loss': total_net - total_approved_amount,
            'recovery_potential': total_recovery_potential,
            'critical_insurers': len(critical_insurers)
        }
    
    def export_dashboard_data(self):
        """Export dashboard data for external visualization"""
        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.generate_dashboard_report(),
            'charts_data': {
                'status_distribution': dict(Counter(row.get('Status', 'Unknown') for row in self.data)),
                'insurer_performance': {},
                'daily_trends': {},
                'claim_type_analysis': {}
            }
        }
        
        # Insurer performance data
        insurer_stats = defaultdict(lambda: {'total': 0, 'rejected': 0, 'revenue': 0})
        for row in self.data:
            insurer = row.get('Insurer Name', 'Unknown')
            insurer_stats[insurer]['total'] += 1
            if row.get('Status') == 'Rejected':
                insurer_stats[insurer]['rejected'] += 1
            try:
                insurer_stats[insurer]['revenue'] += float(row.get('Net Amount', 0) or 0)
            except:
                continue
        
        for insurer, stats in insurer_stats.items():
            if stats['total'] >= 50:  # Minimum threshold
                dashboard_data['charts_data']['insurer_performance'][insurer] = {
                    'rejection_rate': (stats['rejected'] / stats['total']) * 100,
                    'total_claims': stats['total'],
                    'total_revenue': stats['revenue']
                }
        
        with open('dashboard_data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print(f"\n📊 Dashboard data exported to 'dashboard_data.json'")

if __name__ == "__main__":
    dashboard = ClaimsDashboard('merged_all_data.csv')
    dashboard.generate_dashboard_report()
    dashboard.export_dashboard_data()
