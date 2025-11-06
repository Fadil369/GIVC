"""
Advanced NPHIES Data Analysis with Visualizations
===================================================
Enhanced analysis with charts, graphs, and advanced pattern detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class AdvancedNPHIESAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.output_folder = os.path.join(folder_path, 'analysis_output')
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Data containers
        self.claims_df = None
        self.payment_df = None
        self.eligibility_df = None
        self.auth_df = None
        self.comm_df = None
    
    def load_data(self):
        """Load all CSV files"""
        print("Loading data...")
        
        try:
            # Load Claims
            claim_files = [f for f in os.listdir(self.folder_path) if 'Claim_' in f and f.endswith('.csv')]
            if claim_files:
                self.claims_df = pd.read_csv(os.path.join(self.folder_path, claim_files[0]))
                print(f"✓ Claims: {len(self.claims_df)} records")
            
            # Load Payment Reconciliation
            payment_files = [f for f in os.listdir(self.folder_path) if 'PaymentReconciliation_' in f and f.endswith('.csv')]
            if payment_files:
                self.payment_df = pd.read_csv(os.path.join(self.folder_path, payment_files[0]))
                print(f"✓ Payments: {len(self.payment_df)} records")
            
            # Load Eligibility
            eligibility_files = [f for f in os.listdir(self.folder_path) if 'EligibilityRequest_' in f and f.endswith('.csv')]
            if eligibility_files:
                self.eligibility_df = pd.read_csv(os.path.join(self.folder_path, eligibility_files[0]))
                print(f"✓ Eligibility: {len(self.eligibility_df)} records")
            
            # Load Authorization
            auth_files = [f for f in os.listdir(self.folder_path) if 'AdvancedAuth_' in f and f.endswith('.csv')]
            if auth_files:
                self.auth_df = pd.read_csv(os.path.join(self.folder_path, auth_files[0]))
                print(f"✓ Authorization: {len(self.auth_df)} records")
            
            # Load Communications
            comm_files = [f for f in os.listdir(self.folder_path) if 'CommunicationRequest_' in f and f.endswith('.csv')]
            if comm_files:
                self.comm_df = pd.read_csv(os.path.join(self.folder_path, comm_files[0]))
                print(f"✓ Communications: {len(self.comm_df)} records")
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_claims_dashboard(self):
        """Create comprehensive claims visualization dashboard"""
        if self.claims_df is None:
            return
        
        print("\nGenerating Claims Dashboard...")
        df = self.claims_df.copy()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Approved Amount'] = pd.to_numeric(df['Approved Amount'], errors='coerce')
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('NPHIES Claims Analysis Dashboard', fontsize=20, fontweight='bold')
        
        # 1. Status Distribution
        status_counts = df['Status'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#95a5a6', '#3498db']
        axes[0, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
                       colors=colors[:len(status_counts)], startangle=90)
        axes[0, 0].set_title('Claim Status Distribution', fontweight='bold', fontsize=12)
        
        # 2. Claim Type Distribution
        claim_type_counts = df['Claim Type'].value_counts()
        axes[0, 1].bar(range(len(claim_type_counts)), claim_type_counts.values, color='skyblue')
        axes[0, 1].set_xticks(range(len(claim_type_counts)))
        axes[0, 1].set_xticklabels(claim_type_counts.index, rotation=45)
        axes[0, 1].set_title('Claims by Type', fontweight='bold', fontsize=12)
        axes[0, 1].set_ylabel('Count')
        
        # 3. Top 10 Insurers
        top_insurers = df['Insurer Name'].value_counts().head(10)
        axes[0, 2].barh(range(len(top_insurers)), top_insurers.values, color='coral')
        axes[0, 2].set_yticks(range(len(top_insurers)))
        axes[0, 2].set_yticklabels([name[:30] for name in top_insurers.index], fontsize=8)
        axes[0, 2].set_title('Top 10 Insurers by Volume', fontweight='bold', fontsize=12)
        axes[0, 2].set_xlabel('Number of Claims')
        
        # 4. Financial Analysis
        financial_data = {
            'Submitted': df['Net Amount'].sum(),
            'Approved': df['Approved Amount'].sum(),
            'Lost': df['Net Amount'].sum() - df['Approved Amount'].sum()
        }
        axes[1, 0].bar(financial_data.keys(), financial_data.values(), color=['blue', 'green', 'red'])
        axes[1, 0].set_title('Financial Overview (SAR)', fontweight='bold', fontsize=12)
        axes[1, 0].set_ylabel('Amount (SAR)')
        for i, (k, v) in enumerate(financial_data.items()):
            axes[1, 0].text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=8)
        
        # 5. Encounter Class Distribution
        if 'Encounter Class' in df.columns:
            encounter_counts = df['Encounter Class'].value_counts()
            axes[1, 1].bar(range(len(encounter_counts)), encounter_counts.values, color='lightgreen')
            axes[1, 1].set_xticks(range(len(encounter_counts)))
            axes[1, 1].set_xticklabels(encounter_counts.index, rotation=45)
            axes[1, 1].set_title('Encounter Class Distribution', fontweight='bold', fontsize=12)
            axes[1, 1].set_ylabel('Count')
        
        # 6. Daily Trend
        if 'Submission Date' in df.columns:
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Date'] = df['Submission Date'].dt.date
            daily_claims = df.groupby('Date').size()
            axes[1, 2].plot(daily_claims.index, daily_claims.values, marker='o', linewidth=2, color='purple')
            axes[1, 2].set_title('Daily Claims Trend', fontweight='bold', fontsize=12)
            axes[1, 2].set_xlabel('Date')
            axes[1, 2].set_ylabel('Number of Claims')
            axes[1, 2].tick_params(axis='x', rotation=45)
            plt.setp(axes[1, 2].xaxis.get_majorticklabels(), fontsize=8)
        
        plt.tight_layout()
        dashboard_path = os.path.join(self.output_folder, 'claims_dashboard.png')
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Claims dashboard saved: {dashboard_path}")
    
    def create_insurer_analysis(self):
        """Detailed insurer performance analysis"""
        if self.claims_df is None:
            return
        
        print("Generating Insurer Analysis...")
        df = self.claims_df.copy()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Approved Amount'] = pd.to_numeric(df['Approved Amount'], errors='coerce')
        
        # Get top 10 insurers
        top_insurers = df['Insurer Name'].value_counts().head(10).index
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Insurer Performance Analysis', fontsize=18, fontweight='bold')
        
        # 1. Approval Rate by Insurer
        approval_rates = []
        insurer_names = []
        for insurer in top_insurers:
            insurer_df = df[df['Insurer Name'] == insurer]
            approved = len(insurer_df[insurer_df['Status'] == 'Approved'])
            rate = (approved / len(insurer_df)) * 100 if len(insurer_df) > 0 else 0
            approval_rates.append(rate)
            insurer_names.append(insurer[:25])
        
        axes[0, 0].barh(range(len(approval_rates)), approval_rates, color='lightblue')
        axes[0, 0].set_yticks(range(len(insurer_names)))
        axes[0, 0].set_yticklabels(insurer_names, fontsize=9)
        axes[0, 0].set_title('Approval Rate by Insurer (%)', fontweight='bold')
        axes[0, 0].set_xlabel('Approval Rate (%)')
        
        # 2. Total Amount by Insurer
        insurer_amounts = df.groupby('Insurer Name')['Net Amount'].sum().nlargest(10)
        axes[0, 1].bar(range(len(insurer_amounts)), insurer_amounts.values, color='lightcoral')
        axes[0, 1].set_xticks(range(len(insurer_amounts)))
        axes[0, 1].set_xticklabels([name[:20] for name in insurer_amounts.index], rotation=45, ha='right', fontsize=8)
        axes[0, 1].set_title('Total Claim Amount by Insurer (SAR)', fontweight='bold')
        axes[0, 1].set_ylabel('Amount (SAR)')
        
        # 3. Rejection Rate by Insurer
        rejection_rates = []
        for insurer in top_insurers:
            insurer_df = df[df['Insurer Name'] == insurer]
            rejected = len(insurer_df[insurer_df['Status'].isin(['Rejected', 'Cancelled', 'Error'])])
            rate = (rejected / len(insurer_df)) * 100 if len(insurer_df) > 0 else 0
            rejection_rates.append(rate)
        
        axes[1, 0].barh(range(len(rejection_rates)), rejection_rates, color='salmon')
        axes[1, 0].set_yticks(range(len(insurer_names)))
        axes[1, 0].set_yticklabels(insurer_names, fontsize=9)
        axes[1, 0].set_title('Rejection Rate by Insurer (%)', fontweight='bold')
        axes[1, 0].set_xlabel('Rejection Rate (%)')
        
        # 4. Average Claim Amount by Insurer
        avg_amounts = df.groupby('Insurer Name')['Net Amount'].mean().nlargest(10)
        axes[1, 1].bar(range(len(avg_amounts)), avg_amounts.values, color='lightgreen')
        axes[1, 1].set_xticks(range(len(avg_amounts)))
        axes[1, 1].set_xticklabels([name[:20] for name in avg_amounts.index], rotation=45, ha='right', fontsize=8)
        axes[1, 1].set_title('Average Claim Amount by Insurer (SAR)', fontweight='bold')
        axes[1, 1].set_ylabel('Amount (SAR)')
        
        plt.tight_layout()
        insurer_path = os.path.join(self.output_folder, 'insurer_analysis.png')
        plt.savefig(insurer_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Insurer analysis saved: {insurer_path}")
    
    def create_payment_analysis(self):
        """Payment reconciliation visualization"""
        if self.payment_df is None:
            return
        
        print("Generating Payment Analysis...")
        df = self.payment_df.copy()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Number Of Claims'] = pd.to_numeric(df['Number Of Claims'], errors='coerce')
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Payment Reconciliation Analysis', fontsize=18, fontweight='bold')
        
        # 1. Payment Distribution
        non_zero = df[df['Net Amount'] > 0]['Net Amount']
        axes[0, 0].hist(non_zero, bins=30, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Payment Amount Distribution (Non-Zero)', fontweight='bold')
        axes[0, 0].set_xlabel('Payment Amount (SAR)')
        axes[0, 0].set_ylabel('Frequency')
        
        # 2. Top Payers
        top_payers = df.groupby('Sender Name')['Net Amount'].sum().nlargest(10)
        axes[0, 1].barh(range(len(top_payers)), top_payers.values, color='lightgreen')
        axes[0, 1].set_yticks(range(len(top_payers)))
        axes[0, 1].set_yticklabels([name[:30] for name in top_payers.index], fontsize=9)
        axes[0, 1].set_title('Top 10 Payers by Total Amount', fontweight='bold')
        axes[0, 1].set_xlabel('Total Amount Paid (SAR)')
        
        # 3. Daily Payment Trend
        if 'Submission Date' in df.columns:
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Date'] = df['Submission Date'].dt.date
            daily_payments = df.groupby('Date')['Net Amount'].sum()
            axes[1, 0].plot(daily_payments.index, daily_payments.values, marker='o', linewidth=2, color='green')
            axes[1, 0].set_title('Daily Payment Trend', fontweight='bold')
            axes[1, 0].set_xlabel('Date')
            axes[1, 0].set_ylabel('Payment Amount (SAR)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            plt.setp(axes[1, 0].xaxis.get_majorticklabels(), fontsize=8)
        
        # 4. Zero vs Non-Zero Payments
        zero_count = len(df[df['Net Amount'] == 0])
        non_zero_count = len(df[df['Net Amount'] > 0])
        axes[1, 1].pie([non_zero_count, zero_count], labels=['Non-Zero', 'Zero'], 
                       autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'], startangle=90)
        axes[1, 1].set_title('Payment Bundles: Zero vs Non-Zero', fontweight='bold')
        
        plt.tight_layout()
        payment_path = os.path.join(self.output_folder, 'payment_analysis.png')
        plt.savefig(payment_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Payment analysis saved: {payment_path}")
    
    def create_temporal_heatmap(self):
        """Create temporal heatmap of claim submissions"""
        if self.claims_df is None:
            return
        
        print("Generating Temporal Heatmap...")
        df = self.claims_df.copy()
        
        if 'Submission Date' in df.columns:
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Hour'] = df['Submission Date'].dt.hour
            df['DayOfWeek'] = df['Submission Date'].dt.day_name()
            
            # Create pivot table
            heatmap_data = df.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
            
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex([d for d in days_order if d in heatmap_data.index])
            
            plt.figure(figsize=(16, 6))
            sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False, fmt='d', cbar_kws={'label': 'Number of Claims'})
            plt.title('Claim Submission Heatmap by Day and Hour', fontsize=16, fontweight='bold')
            plt.xlabel('Hour of Day', fontsize=12)
            plt.ylabel('Day of Week', fontsize=12)
            
            heatmap_path = os.path.join(self.output_folder, 'temporal_heatmap.png')
            plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Temporal heatmap saved: {heatmap_path}")
    
    def export_detailed_excel_report(self):
        """Export comprehensive analysis to Excel"""
        print("Generating Excel Report...")
        excel_path = os.path.join(self.output_folder, 'nphies_detailed_report.xlsx')
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Claims Summary
            if self.claims_df is not None:
                df = self.claims_df.copy()
                
                # Status summary
                status_summary = pd.DataFrame({
                    'Status': df['Status'].value_counts().index,
                    'Count': df['Status'].value_counts().values,
                    'Percentage': (df['Status'].value_counts() / len(df) * 100).values
                })
                status_summary.to_excel(writer, sheet_name='Claim_Status', index=False)
                
                # Insurer summary
                insurer_summary = df.groupby('Insurer Name').agg({
                    'Bundle ID': 'count',
                    'Net Amount': 'sum',
                    'Approved Amount': 'sum'
                }).reset_index()
                insurer_summary.columns = ['Insurer', 'Total Claims', 'Submitted Amount', 'Approved Amount']
                insurer_summary['Loss Amount'] = insurer_summary['Submitted Amount'] - insurer_summary['Approved Amount']
                insurer_summary = insurer_summary.sort_values('Total Claims', ascending=False)
                insurer_summary.to_excel(writer, sheet_name='Insurer_Summary', index=False)
            
            # Payment Summary
            if self.payment_df is not None:
                payment_summary = self.payment_df.groupby('Sender Name').agg({
                    'Net Amount': 'sum',
                    'Number Of Claims': 'sum',
                    'Bundle ID': 'count'
                }).reset_index()
                payment_summary.columns = ['Payer', 'Total Amount', 'Total Claims', 'Number of Bundles']
                payment_summary = payment_summary.sort_values('Total Amount', ascending=False)
                payment_summary.to_excel(writer, sheet_name='Payment_Summary', index=False)
            
            # Eligibility Summary
            if self.eligibility_df is not None:
                elig_summary = pd.DataFrame({
                    'Status': self.eligibility_df['Status'].value_counts().index,
                    'Count': self.eligibility_df['Status'].value_counts().values
                })
                elig_summary.to_excel(writer, sheet_name='Eligibility_Status', index=False)
        
        print(f"  ✓ Excel report saved: {excel_path}")
    
    def generate_insights_report(self):
        """Generate comprehensive text insights report"""
        print("Generating Insights Report...")
        report_path = os.path.join(self.output_folder, 'insights_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("NPHIES COMPREHENSIVE INSIGHTS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 100 + "\n\n")
            
            if self.claims_df is not None:
                total_claims = len(self.claims_df)
                approved = len(self.claims_df[self.claims_df['Status'] == 'Approved'])
                rejected = len(self.claims_df[self.claims_df['Status'].isin(['Rejected', 'Cancelled', 'Error'])])
                
                f.write(f"Total Claims Processed: {total_claims:,}\n")
                f.write(f"Approved Claims: {approved:,} ({approved/total_claims*100:.1f}%)\n")
                f.write(f"Rejected/Error Claims: {rejected:,} ({rejected/total_claims*100:.1f}%)\n\n")
                
                total_submitted = self.claims_df['Net Amount'].sum()
                total_approved_amt = self.claims_df['Approved Amount'].sum()
                f.write(f"Total Amount Submitted: SAR {total_submitted:,.2f}\n")
                f.write(f"Total Amount Approved: SAR {total_approved_amt:,.2f}\n")
                f.write(f"Revenue Loss: SAR {total_submitted - total_approved_amt:,.2f}\n\n")
            
            # Key Issues
            f.write("\nKEY ISSUES IDENTIFIED\n")
            f.write("-" * 100 + "\n\n")
            
            if self.claims_df is not None:
                rejection_rate = rejected / total_claims * 100
                if rejection_rate > 20:
                    f.write(f"⚠️ High Rejection Rate: {rejection_rate:.1f}% of claims are rejected\n")
                    f.write("   Recommendation: Review submission process and documentation requirements\n\n")
            
            if self.eligibility_df is not None:
                error_pct = len(self.eligibility_df[self.eligibility_df['Status'] == 'Error']) / len(self.eligibility_df) * 100
                if error_pct > 30:
                    f.write(f"⚠️ High Eligibility Error Rate: {error_pct:.1f}%\n")
                    f.write("   Recommendation: Check system integration and data quality\n\n")
            
            # Opportunities
            f.write("\nOPPORTUNITIES FOR IMPROVEMENT\n")
            f.write("-" * 100 + "\n\n")
            f.write("1. Focus on high-volume insurers with low approval rates\n")
            f.write("2. Implement automated eligibility checking before claim submission\n")
            f.write("3. Analyze partial approval patterns to optimize claim amounts\n")
            f.write("4. Reduce communication cycle time for faster processing\n")
            f.write("5. Develop insurer-specific submission guidelines\n\n")
        
        print(f"  ✓ Insights report saved: {report_path}")
    
    def run_complete_analysis(self):
        """Execute full advanced analysis"""
        print("\n" + "=" * 80)
        print("ADVANCED NPHIES DATA ANALYZER")
        print("=" * 80 + "\n")
        
        if not self.load_data():
            print("Failed to load data.")
            return
        
        print("\nGenerating visualizations and reports...\n")
        
        # Generate all visualizations
        self.create_claims_dashboard()
        self.create_insurer_analysis()
        self.create_payment_analysis()
        self.create_temporal_heatmap()
        
        # Generate reports
        self.export_detailed_excel_report()
        self.generate_insights_report()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"\nAll outputs saved to: {self.output_folder}")
        print("\nGenerated files:")
        print("  • claims_dashboard.png - Comprehensive claims visualization")
        print("  • insurer_analysis.png - Insurer performance metrics")
        print("  • payment_analysis.png - Payment reconciliation charts")
        print("  • temporal_heatmap.png - Submission patterns by day/hour")
        print("  • nphies_detailed_report.xlsx - Excel report with all summaries")
        print("  • insights_report.txt - Text-based insights and recommendations")
        print()


def main():
    folder_path = r"c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
    analyzer = AdvancedNPHIESAnalyzer(folder_path)
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
