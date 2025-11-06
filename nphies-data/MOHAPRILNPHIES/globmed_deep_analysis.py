"""
GlobMed Comprehensive Analysis - April 2025
Detailed service-level and rejection analysis for all GlobMed claims
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class GlobMedAnalyzer:
    def __init__(self):
        self.claims_df = None
        self.globmed_claims = None
        self.output_folder = 'globmed_analysis'
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def load_data(self):
        """Load claims data"""
        print("📂 Loading Claims Data...")
        try:
            self.claims_df = pd.read_csv('Claim_0555a8fb-8ec7-460f-b92f-06ba0bd3fb2d_part1_2025-04-06_2025-04-27.csv')
            print(f"   ✅ Loaded {len(self.claims_df):,} total claims")
            
            # Filter for GlobeMed only (using "Receiver Name" column)
            # Note: It's "GlobeMed" not "GlobMed" in the data
            self.globmed_claims = self.claims_df[
                self.claims_df['Receiver Name'].str.contains('GlobeMed', case=False, na=False)
            ].copy()
            
            print(f"   ✅ Filtered to {len(self.globmed_claims):,} GlobMed claims")
            return True
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            return False
    
    def analyze_overview(self):
        """Generate overview statistics"""
        print("\n" + "="*100)
        print("📊 GLOBMED OVERVIEW - APRIL 2025")
        print("="*100)
        
        total_claims = len(self.globmed_claims)
        
        # Status breakdown
        status_counts = self.globmed_claims['Status'].value_counts()
        
        print(f"\n📋 Total GlobMed Claims: {total_claims:,}")
        print(f"📅 Date Range: April 6 - April 27, 2025")
        print(f"\n{'Status':<20} {'Count':<10} {'Percentage':<15}")
        print("-" * 50)
        
        for status, count in status_counts.items():
            pct = (count / total_claims) * 100
            print(f"{status:<20} {count:<10,} {pct:>6.2f}%")
        
        # Financial overview
        if 'Net Amount' in self.globmed_claims.columns:
            total_billed = self.globmed_claims['Net Amount'].sum()
            
            if 'Approved Amount' in self.globmed_claims.columns:
                total_approved = self.globmed_claims['Approved Amount'].sum()
                total_loss = total_billed - total_approved
                recovery_rate = (total_approved / total_billed * 100) if total_billed > 0 else 0
                
                print(f"\n💰 Financial Summary:")
                print(f"   Total Billed:     SAR {total_billed:,.2f}")
                print(f"   Total Approved:   SAR {total_approved:,.2f}")
                print(f"   Total Loss:       SAR {total_loss:,.2f}")
                print(f"   Recovery Rate:    {recovery_rate:.2f}%")
        
        return {
            'total_claims': total_claims,
            'status_breakdown': status_counts.to_dict()
        }
    
    def analyze_by_service_type(self):
        """Analyze rejections by service type"""
        print("\n" + "="*100)
        print("🏥 ANALYSIS BY SERVICE TYPE")
        print("="*100)
        
        # Check available service columns
        service_cols = [col for col in self.globmed_claims.columns if 'Type' in col or 'Service' in col]
        
        if 'Service Event Type' in self.globmed_claims.columns:
            service_col = 'Service Event Type'
        elif 'Claim Type' in self.globmed_claims.columns:
            service_col = 'Claim Type'
        else:
            service_col = None
        
        results = []
        
        if service_col and service_col in self.globmed_claims.columns:
            service_analysis = self.globmed_claims.groupby(service_col).agg({
                'Transaction Identifier': 'count',
                'Status': lambda x: (x == 'Approved').sum(),
                'Net Amount': 'sum',
                'Approved Amount': 'sum' if 'Approved Amount' in self.globmed_claims.columns else 'count'
            }).reset_index()
            
            service_analysis.columns = ['ServiceType', 'TotalClaims', 'ApprovedClaims', 'TotalBilled', 'TotalApproved']
            service_analysis['RejectionRate'] = ((service_analysis['TotalClaims'] - service_analysis['ApprovedClaims']) / service_analysis['TotalClaims'] * 100)
            service_analysis['ApprovalRate'] = (service_analysis['ApprovedClaims'] / service_analysis['TotalClaims'] * 100)
            
            if 'Approved Amount' in self.globmed_claims.columns:
                service_analysis['Loss'] = service_analysis['TotalBilled'] - service_analysis['TotalApproved']
            
            service_analysis = service_analysis.sort_values('RejectionRate', ascending=False)
            
            print(f"\n{'Service Type':<30} {'Total':<10} {'Approved':<12} {'Approval%':<12} {'Total Billed':<20}")
            print("-" * 100)
            
            for _, row in service_analysis.head(20).iterrows():
                print(f"{str(row['ServiceType'])[:28]:<30} {row['TotalClaims']:<10,} {row['ApprovedClaims']:<12,} {row['ApprovalRate']:>6.2f}%     SAR {row['TotalBilled']:>15,.2f}")
            
            results.append(('service_type', service_analysis))
        
        # Analyze by diagnosis if available (skip for now as column not in main data)
        if 'Diagnosis' in self.globmed_claims.columns:
            print(f"\n\n🔬 ANALYSIS BY DIAGNOSIS CODE")
            print("-" * 100)
            
            diag_analysis = self.globmed_claims.groupby('Diagnosis').agg({
                'Transaction Identifier': 'count',
                'Status': lambda x: (x == 'Approved').sum(),
                'Net Amount': 'sum'
            }).reset_index()
            
            diag_analysis.columns = ['Diagnosis', 'TotalClaims', 'ApprovedClaims', 'TotalBilled']
            diag_analysis['ApprovalRate'] = (diag_analysis['ApprovedClaims'] / diag_analysis['TotalClaims'] * 100)
            diag_analysis = diag_analysis.sort_values('TotalClaims', ascending=False)
            
            print(f"{'Diagnosis Code':<20} {'Total':<10} {'Approved':<12} {'Approval%':<12} {'Total Billed':<20}")
            print("-" * 100)
            
            for _, row in diag_analysis.head(15).iterrows():
                print(f"{str(row['Diagnosis'])[:18]:<20} {row['TotalClaims']:<10,} {row['ApprovedClaims']:<12,} {row['ApprovalRate']:>6.2f}%     SAR {row['TotalBilled']:>15,.2f}")
            
            results.append(('diagnosis', diag_analysis))
        
        return results
    
    def analyze_rejection_reasons(self):
        """Deep dive into rejection reasons"""
        print("\n" + "="*100)
        print("❌ DETAILED REJECTION ANALYSIS")
        print("="*100)
        
        # Filter rejected claims
        rejected_claims = self.globmed_claims[
            self.globmed_claims['Status'].isin(['Rejected', 'Denied', 'Cancelled', 'Error'])
        ].copy()
        
        print(f"\n📊 Total Rejected Claims: {len(rejected_claims):,}")
        
        results = []
        
        # Analyze by status
        print(f"\n{'Rejection Status':<25} {'Count':<10} {'Percentage':<15} {'Total Amount':<20}")
        print("-" * 80)
        
        status_analysis = rejected_claims.groupby('Status').agg({
            'Transaction Identifier': 'count',
            'Net Amount': 'sum'
        }).reset_index()
        status_analysis.columns = ['Status', 'Count', 'TotalAmount']
        status_analysis['Percentage'] = (status_analysis['Count'] / len(rejected_claims) * 100)
        
        for _, row in status_analysis.iterrows():
            print(f"{row['Status']:<25} {row['Count']:<10,} {row['Percentage']:>6.2f}%        SAR {row['TotalAmount']:>15,.2f}")
        
        results.append(('rejection_status', status_analysis))
        
        # Look for error codes or rejection reasons
        error_cols = [col for col in rejected_claims.columns if 'error' in col.lower() or 'reason' in col.lower() or 'message' in col.lower()]
        
        for col in error_cols[:3]:  # Analyze top 3 error columns
            if rejected_claims[col].notna().any():
                print(f"\n\n🔍 Analysis by {col}:")
                print("-" * 100)
                
                error_analysis = rejected_claims[rejected_claims[col].notna()].groupby(col).agg({
                    'Transaction Identifier': 'count',
                    'Net Amount': 'sum'
                }).reset_index()
                error_analysis.columns = ['Reason', 'Count', 'TotalAmount']
                error_analysis = error_analysis.sort_values('Count', ascending=False)
                
                print(f"{'Reason':<60} {'Count':<10} {'Total Amount':<20}")
                print("-" * 100)
                
                for _, row in error_analysis.head(15).iterrows():
                    reason = str(row['Reason'])[:58]
                    print(f"{reason:<60} {row['Count']:<10,} SAR {row['TotalAmount']:>15,.2f}")
                
                results.append((f'error_{col}', error_analysis))
        
        return rejected_claims, results
    
    def analyze_high_value_claims(self):
        """Analyze high-value claims (over SAR 5,000)"""
        print("\n" + "="*100)
        print("💎 HIGH-VALUE CLAIMS ANALYSIS (> SAR 5,000)")
        print("="*100)
        
        high_value = self.globmed_claims[self.globmed_claims['Net Amount'] > 5000].copy()
        
        print(f"\n📊 Total High-Value Claims: {len(high_value):,}")
        
        # Status breakdown for high-value claims
        hv_status = high_value['Status'].value_counts()
        
        print(f"\n{'Status':<20} {'Count':<10} {'Percentage':<15} {'Total Amount':<20}")
        print("-" * 80)
        
        for status, count in hv_status.items():
            pct = (count / len(high_value)) * 100
            amount = high_value[high_value['Status'] == status]['Net Amount'].sum()
            print(f"{status:<20} {count:<10,} {pct:>6.2f}%        SAR {amount:>15,.2f}")
        
        # Top 20 highest rejected claims
        rejected_high_value = high_value[
            high_value['Status'].isin(['Rejected', 'Denied', 'Cancelled', 'Error'])
        ].copy()
        
        if len(rejected_high_value) > 0:
            print(f"\n\n🚨 TOP 20 REJECTED HIGH-VALUE CLAIMS:")
            print("-" * 120)
            print(f"{'Transaction ID':<20} {'Amount':<18} {'Status':<15} {'Date':<12}")
            print("-" * 120)
            
            rejected_high_value_sorted = rejected_high_value.sort_values('Net Amount', ascending=False)
            
            for _, row in rejected_high_value_sorted.head(20).iterrows():
                trans_id = str(row.get('Transaction Identifier', 'N/A'))[:18]
                amount = row['Net Amount']
                status = str(row['Status'])[:13]
                date = str(row.get('Submission Date', row.get('Date', 'N/A')))[:10]
                
                print(f"{trans_id:<20} SAR {amount:>12,.2f}   {status:<15} {date:<12}")
            
            total_rejected_hv = rejected_high_value['Net Amount'].sum()
            print(f"\n💰 Total Rejected High-Value Amount: SAR {total_rejected_hv:,.2f}")
        
        return high_value, rejected_high_value
    
    def analyze_claim_level_details(self):
        """Detailed claim-by-claim analysis"""
        print("\n" + "="*100)
        print("📋 CLAIM-LEVEL DETAILED ANALYSIS")
        print("="*100)
        
        # Create detailed claim summary
        claim_details = []
        
        for _, claim in self.globmed_claims.iterrows():
            detail = {
                'TransactionID': claim.get('Transaction Identifier', 'N/A'),
                'Status': claim.get('Status', 'N/A'),
                'BilledAmount': claim.get('Net Amount', 0),
                'ApprovedAmount': claim.get('Approved Amount', 0),
                'Loss': claim.get('Net Amount', 0) - claim.get('Approved Amount', 0),
                'Date': claim.get('Submission Date', claim.get('Date', 'N/A')),
                'PatientID': claim.get('Patient Identifier', claim.get('PatientId', 'N/A')),
            }
            
            # Add service type if available
            for col in ['Service Event Type', 'Claim Type', 'Claim Sub Type']:
                if col in claim:
                    detail['ServiceType'] = claim[col]
                    break
            
            # Add insurer if available
            if 'Insurer Name' in claim:
                detail['Insurer'] = claim['Insurer Name']
            
            claim_details.append(detail)
        
        details_df = pd.DataFrame(claim_details)
        
        # Summary statistics
        print(f"\n📊 Claim Statistics:")
        print(f"   Total Claims: {len(details_df):,}")
        print(f"   Average Billed: SAR {details_df['BilledAmount'].mean():,.2f}")
        print(f"   Average Approved: SAR {details_df['ApprovedAmount'].mean():,.2f}")
        print(f"   Average Loss per Claim: SAR {details_df['Loss'].mean():,.2f}")
        print(f"   Median Billed: SAR {details_df['BilledAmount'].median():,.2f}")
        print(f"   Median Approved: SAR {details_df['ApprovedAmount'].median():,.2f}")
        
        # Amount ranges
        print(f"\n💰 Claim Amount Distribution:")
        print(f"{'Amount Range':<25} {'Count':<10} {'Percentage':<15}")
        print("-" * 55)
        
        ranges = [
            (0, 500, 'SAR 0 - 500'),
            (500, 1000, 'SAR 500 - 1,000'),
            (1000, 2500, 'SAR 1,000 - 2,500'),
            (2500, 5000, 'SAR 2,500 - 5,000'),
            (5000, 10000, 'SAR 5,000 - 10,000'),
            (10000, float('inf'), 'SAR 10,000+')
        ]
        
        for min_val, max_val, label in ranges:
            count = len(details_df[(details_df['BilledAmount'] >= min_val) & (details_df['BilledAmount'] < max_val)])
            pct = (count / len(details_df) * 100) if len(details_df) > 0 else 0
            print(f"{label:<25} {count:<10,} {pct:>6.2f}%")
        
        return details_df
    
    def analyze_temporal_patterns(self):
        """Analyze patterns over time"""
        print("\n" + "="*100)
        print("📅 TEMPORAL ANALYSIS - DAILY PATTERNS")
        print("="*100)
        
        # Try to find date column
        date_col = None
        for col in ['Submission Date', 'Claim Response Polled At', 'Date']:
            if col in self.globmed_claims.columns:
                date_col = col
                break
        
        if date_col:
            try:
                self.globmed_claims['ParsedDate'] = pd.to_datetime(self.globmed_claims[date_col], errors='coerce')
                self.globmed_claims['Day'] = self.globmed_claims['ParsedDate'].dt.date
                
                daily_analysis = self.globmed_claims.groupby('Day').agg({
                    'Transaction Identifier': 'count',
                    'Status': lambda x: (x == 'Approved').sum(),
                    'Net Amount': 'sum'
                }).reset_index()
                
                daily_analysis.columns = ['Date', 'TotalClaims', 'ApprovedClaims', 'TotalBilled']
                daily_analysis['ApprovalRate'] = (daily_analysis['ApprovedClaims'] / daily_analysis['TotalClaims'] * 100)
                daily_analysis['AvgClaimAmount'] = daily_analysis['TotalBilled'] / daily_analysis['TotalClaims']
                
                print(f"\n{'Date':<15} {'Total Claims':<15} {'Approved':<12} {'Approval%':<12} {'Avg Amount':<18}")
                print("-" * 85)
                
                for _, row in daily_analysis.sort_values('Date').iterrows():
                    print(f"{str(row['Date']):<15} {row['TotalClaims']:<15,} {row['ApprovedClaims']:<12,} {row['ApprovalRate']:>6.2f}%     SAR {row['AvgClaimAmount']:>12,.2f}")
                
                # Identify worst days
                worst_days = daily_analysis.sort_values('ApprovalRate').head(5)
                print(f"\n\n🚨 WORST PERFORMING DAYS (Lowest Approval Rate):")
                print("-" * 85)
                for _, row in worst_days.iterrows():
                    print(f"{str(row['Date']):<15} Approval: {row['ApprovalRate']:>5.2f}%  |  {row['TotalClaims']:,} claims  |  SAR {row['TotalBilled']:,.2f}")
                
                return daily_analysis
            except Exception as e:
                print(f"   ⚠️  Could not parse dates: {e}")
        else:
            print("   ⚠️  No date column found for temporal analysis")
        
        return None
    
    def generate_excel_report(self, all_results):
        """Generate comprehensive Excel report"""
        print("\n" + "="*100)
        print("📊 GENERATING EXCEL REPORT...")
        print("="*100)
        
        import os
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        filename = f'{self.output_folder}/globmed_detailed_analysis_{self.timestamp}.xlsx'
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet 1: Overview
                overview_data = {
                    'Metric': ['Total Claims', 'Approved', 'Rejected', 'Partial', 'Other',
                               'Total Billed', 'Total Approved', 'Total Loss', 'Recovery Rate'],
                    'Value': []
                }
                
                status_counts = self.globmed_claims['Status'].value_counts()
                overview_data['Value'] = [
                    len(self.globmed_claims),
                    status_counts.get('Approved', 0),
                    status_counts.get('Rejected', 0) + status_counts.get('Denied', 0),
                    status_counts.get('Partial', 0),
                    len(self.globmed_claims) - sum([status_counts.get('Approved', 0), 
                                                      status_counts.get('Rejected', 0),
                                                      status_counts.get('Denied', 0),
                                                      status_counts.get('Partial', 0)]),
                    self.globmed_claims['Net Amount'].sum(),
                    self.globmed_claims.get('Approved Amount', pd.Series([0])).sum(),
                    self.globmed_claims['Net Amount'].sum() - self.globmed_claims.get('Approved Amount', pd.Series([0])).sum(),
                    (self.globmed_claims.get('Approved Amount', pd.Series([0])).sum() / self.globmed_claims['Net Amount'].sum() * 100) if self.globmed_claims['Net Amount'].sum() > 0 else 0
                ]
                
                pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)
                
                # Sheet 2: All Claims Details
                claims_export = self.globmed_claims.copy()
                # Select relevant columns
                export_cols = ['Transaction Identifier', 'Status', 'Net Amount', 'Approved Amount',
                               'Submission Date', 'Patient Identifier', 'Insurer Name']
                export_cols = [col for col in export_cols if col in claims_export.columns]
                
                claims_export[export_cols].to_excel(writer, sheet_name='All Claims', index=False)
                
                # Sheet 3+: Additional analysis results
                sheet_num = 3
                for name, df in all_results:
                    if isinstance(df, pd.DataFrame) and len(df) > 0:
                        sheet_name = name[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        sheet_num += 1
            
            print(f"   ✅ Excel report saved: {filename}")
            return filename
        except Exception as e:
            print(f"   ❌ Error creating Excel: {e}")
            return None
    
    def generate_text_report(self):
        """Generate comprehensive text report"""
        print("\n" + "="*100)
        print("📝 GENERATING TEXT REPORT...")
        print("="*100)
        
        import os
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        filename = f'{self.output_folder}/globmed_analysis_report_{self.timestamp}.txt'
        
        # The console output is comprehensive, so we just inform the user
        print(f"   ✅ Complete analysis displayed above")
        print(f"   💡 TIP: Scroll up to review all sections")
        
        return filename
    
    def run_complete_analysis(self):
        """Run all analysis modules"""
        print("\n")
        print("╔" + "="*98 + "╗")
        print("║" + " "*98 + "║")
        print("║" + "GLOBMED COMPREHENSIVE ANALYSIS - APRIL 2025".center(98) + "║")
        print("║" + "Service-Level & Rejection Analysis".center(98) + "║")
        print("║" + " "*98 + "║")
        print("╚" + "="*98 + "╝")
        
        if not self.load_data():
            print("\n❌ Failed to load data. Exiting.")
            return
        
        if len(self.globmed_claims) == 0:
            print("\n⚠️  No GlobMed claims found in the dataset.")
            return
        
        all_results = []
        
        # Run all analysis modules
        print("\n\n🔍 Starting Comprehensive Analysis...")
        print("="*100)
        
        # 1. Overview
        overview = self.analyze_overview()
        
        # 2. Service type analysis
        service_results = self.analyze_by_service_type()
        all_results.extend(service_results)
        
        # 3. Rejection analysis
        rejected_claims, rejection_results = self.analyze_rejection_reasons()
        all_results.extend(rejection_results)
        
        # 4. High-value claims
        high_value, rejected_hv = self.analyze_high_value_claims()
        if len(high_value) > 0:
            all_results.append(('high_value_claims', high_value))
        
        # 5. Claim-level details
        details_df = self.analyze_claim_level_details()
        all_results.append(('claim_details', details_df))
        
        # 6. Temporal patterns
        temporal_df = self.analyze_temporal_patterns()
        if temporal_df is not None:
            all_results.append(('daily_analysis', temporal_df))
        
        # Generate reports
        excel_file = self.generate_excel_report(all_results)
        
        # Final summary
        print("\n\n")
        print("╔" + "="*98 + "╗")
        print("║" + " "*98 + "║")
        print("║" + "ANALYSIS COMPLETE".center(98) + "║")
        print("║" + " "*98 + "║")
        print("╚" + "="*98 + "╝")
        
        print(f"\n📁 Output Location: {self.output_folder}/")
        if excel_file:
            print(f"   📊 Excel Report: {excel_file}")
        
        print("\n" + "="*100)
        print("💡 KEY FINDINGS SUMMARY")
        print("="*100)
        
        total_claims = len(self.globmed_claims)
        approved = len(self.globmed_claims[self.globmed_claims['Status'] == 'Approved'])
        rejected = len(self.globmed_claims[self.globmed_claims['Status'].isin(['Rejected', 'Denied', 'Cancelled'])])
        
        approval_rate = (approved / total_claims * 100) if total_claims > 0 else 0
        rejection_rate = (rejected / total_claims * 100) if total_claims > 0 else 0
        
        print(f"\n✅ Approval Rate: {approval_rate:.2f}%")
        print(f"❌ Rejection Rate: {rejection_rate:.2f}%")
        
        if 'Net Amount' in self.globmed_claims.columns:
            total_billed = self.globmed_claims['Net Amount'].sum()
            total_approved = self.globmed_claims.get('Approved Amount', pd.Series([0])).sum()
            print(f"💰 Total Billed: SAR {total_billed:,.2f}")
            print(f"💰 Total Approved: SAR {total_approved:,.2f}")
            print(f"📉 Financial Loss: SAR {total_billed - total_approved:,.2f}")
        
        print("\n" + "="*100)
        print("🎯 RECOMMENDED NEXT STEPS:")
        print("="*100)
        print("1. Review high-value rejected claims immediately (potential recovery)")
        print("2. Investigate top rejection reasons and address root causes")
        print("3. Analyze worst-performing days for operational issues")
        print("4. Create service-specific improvement plans")
        print("5. Schedule meeting with GlobMed representative to discuss patterns")
        
        print("\n✨ Analysis complete! Review the Excel file for detailed data.\n")


if __name__ == "__main__":
    analyzer = GlobMedAnalyzer()
    analyzer.run_complete_analysis()
