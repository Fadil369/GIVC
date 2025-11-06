"""
NPHIES Data Analysis Script
============================
Comprehensive analysis of NPHIES (Saudi Arabian Health Insurance) data including:
- Claims, Payment Reconciliation, Eligibility Requests, Prior Authorization, Communication Requests
- Trend analysis, pattern detection, issue identification, and relational insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
from pathlib import Path

warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', None)

class NPHIESAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.claims_df = None
        self.payment_df = None
        self.eligibility_df = None
        self.auth_df = None
        self.comm_df = None
        self.output_folder = os.path.join(folder_path, 'analysis_output')
        os.makedirs(self.output_folder, exist_ok=True)
        
    def load_data(self):
        """Load all CSV files from the folder"""
        print("=" * 80)
        print("LOADING NPHIES DATA FILES")
        print("=" * 80)
        
        try:
            # Load Claims
            claim_files = [f for f in os.listdir(self.folder_path) if 'Claim_' in f and f.endswith('.csv')]
            if claim_files:
                self.claims_df = pd.read_csv(os.path.join(self.folder_path, claim_files[0]))
                print(f"✓ Claims Data Loaded: {len(self.claims_df)} records")
            
            # Load Payment Reconciliation
            payment_files = [f for f in os.listdir(self.folder_path) if 'PaymentReconciliation_' in f and f.endswith('.csv')]
            if payment_files:
                self.payment_df = pd.read_csv(os.path.join(self.folder_path, payment_files[0]))
                print(f"✓ Payment Reconciliation Data Loaded: {len(self.payment_df)} records")
            
            # Load Eligibility Requests
            eligibility_files = [f for f in os.listdir(self.folder_path) if 'EligibilityRequest_' in f and f.endswith('.csv')]
            if eligibility_files:
                self.eligibility_df = pd.read_csv(os.path.join(self.folder_path, eligibility_files[0]))
                print(f"✓ Eligibility Request Data Loaded: {len(self.eligibility_df)} records")
            
            # Load Prior Authorization
            auth_files = [f for f in os.listdir(self.folder_path) if 'AdvancedAuth_' in f and f.endswith('.csv')]
            if auth_files:
                self.auth_df = pd.read_csv(os.path.join(self.folder_path, auth_files[0]))
                print(f"✓ Prior Authorization Data Loaded: {len(self.auth_df)} records")
            
            # Load Communication Requests
            comm_files = [f for f in os.listdir(self.folder_path) if 'CommunicationRequest_' in f and f.endswith('.csv')]
            if comm_files:
                self.comm_df = pd.read_csv(os.path.join(self.folder_path, comm_files[0]))
                print(f"✓ Communication Request Data Loaded: {len(self.comm_df)} records")
            
            print("\n")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_claims(self):
        """Comprehensive claims analysis"""
        if self.claims_df is None or len(self.claims_df) == 0:
            return
        
        print("=" * 80)
        print("CLAIMS ANALYSIS")
        print("=" * 80)
        
        df = self.claims_df.copy()
        
        # 1. STATUS DISTRIBUTION
        print("\n📊 CLAIM STATUS DISTRIBUTION:")
        print("-" * 80)
        status_dist = df['Status'].value_counts()
        status_pct = df['Status'].value_counts(normalize=True) * 100
        for status, count in status_dist.items():
            print(f"  {status:20s}: {count:6d} ({status_pct[status]:5.2f}%)")
        
        # 2. REJECTION ANALYSIS
        print("\n❌ REJECTION & ERROR ANALYSIS:")
        print("-" * 80)
        rejected = df[df['Status'].isin(['Rejected', 'Error', 'Cancelled'])]
        print(f"  Total Rejected/Error/Cancelled: {len(rejected)} ({len(rejected)/len(df)*100:.2f}%)")
        
        if len(rejected) > 0:
            # Top rejecting insurers
            print("\n  Top 5 Insurers with Most Rejections:")
            top_reject_insurers = rejected['Insurer Name'].value_counts().head(5)
            for insurer, count in top_reject_insurers.items():
                print(f"    - {insurer}: {count} rejections")
        
        # 3. FINANCIAL ANALYSIS
        print("\n💰 FINANCIAL ANALYSIS:")
        print("-" * 80)
        
        # Convert amounts to numeric
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Approved Amount'] = pd.to_numeric(df['Approved Amount'], errors='coerce')
        
        total_submitted = df['Net Amount'].sum()
        total_approved = df['Approved Amount'].sum()
        
        print(f"  Total Amount Submitted: SAR {total_submitted:,.2f}")
        print(f"  Total Amount Approved:  SAR {total_approved:,.2f}")
        
        if total_submitted > 0:
            approval_rate = (total_approved / total_submitted) * 100
            loss_amount = total_submitted - total_approved
            print(f"  Approval Rate: {approval_rate:.2f}%")
            print(f"  Loss Amount: SAR {loss_amount:,.2f}")
        
        # 4. CLAIM TYPE DISTRIBUTION
        print("\n📋 CLAIM TYPE DISTRIBUTION:")
        print("-" * 80)
        claim_type_dist = df['Claim Type'].value_counts()
        for ctype, count in claim_type_dist.items():
            avg_amount = df[df['Claim Type'] == ctype]['Net Amount'].mean()
            print(f"  {ctype:20s}: {count:6d} claims (Avg: SAR {avg_amount:,.2f})")
        
        # 5. INSURER PERFORMANCE
        print("\n🏥 TOP INSURERS BY VOLUME:")
        print("-" * 80)
        top_insurers = df['Insurer Name'].value_counts().head(5)
        for insurer, count in top_insurers.items():
            insurer_df = df[df['Insurer Name'] == insurer]
            approved = len(insurer_df[insurer_df['Status'] == 'Approved'])
            approval_rate = (approved / count * 100) if count > 0 else 0
            total_amt = insurer_df['Net Amount'].sum()
            print(f"  {insurer[:50]:50s}")
            print(f"    Claims: {count:4d} | Approval Rate: {approval_rate:5.1f}% | Total: SAR {total_amt:,.2f}")
        
        # 6. ENCOUNTER CLASS ANALYSIS
        if 'Encounter Class' in df.columns:
            print("\n🏥 ENCOUNTER CLASS DISTRIBUTION:")
            print("-" * 80)
            encounter_dist = df['Encounter Class'].value_counts()
            for enc, count in encounter_dist.items():
                print(f"  {enc:10s}: {count:6d}")
        
        # 7. TEMPORAL ANALYSIS
        if 'Submission Date' in df.columns:
            print("\n📅 TEMPORAL ANALYSIS:")
            print("-" * 80)
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Date'] = df['Submission Date'].dt.date
            daily_claims = df.groupby('Date').size()
            print(f"  Average Daily Claims: {daily_claims.mean():.0f}")
            print(f"  Peak Day: {daily_claims.idxmax()} ({daily_claims.max()} claims)")
            print(f"  Lowest Day: {daily_claims.idxmin()} ({daily_claims.min()} claims)")
        
        # 8. PARTIAL APPROVAL ANALYSIS
        partial = df[df['Status'] == 'Partial']
        if len(partial) > 0:
            print("\n⚠️ PARTIAL APPROVAL ANALYSIS:")
            print("-" * 80)
            print(f"  Total Partial Approvals: {len(partial)}")
            partial_loss = (partial['Net Amount'] - partial['Approved Amount']).sum()
            print(f"  Amount Lost in Partial Approvals: SAR {partial_loss:,.2f}")
        
        print("\n")
    
    def analyze_payment_reconciliation(self):
        """Analyze payment reconciliation data"""
        if self.payment_df is None or len(self.payment_df) == 0:
            return
        
        print("=" * 80)
        print("PAYMENT RECONCILIATION ANALYSIS")
        print("=" * 80)
        
        df = self.payment_df.copy()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Number Of Claims'] = pd.to_numeric(df['Number Of Claims'], errors='coerce')
        
        # Overall Statistics
        print("\n💳 PAYMENT SUMMARY:")
        print("-" * 80)
        total_payments = df['Net Amount'].sum()
        total_bundles = len(df)
        total_claims = df['Number Of Claims'].sum()
        avg_payment = df['Net Amount'].mean()
        
        print(f"  Total Payment Bundles: {total_bundles}")
        print(f"  Total Claims in Payments: {total_claims:.0f}")
        print(f"  Total Payment Amount: SAR {total_payments:,.2f}")
        print(f"  Average Payment per Bundle: SAR {avg_payment:,.2f}")
        
        # Zero Payment Analysis
        zero_payments = df[df['Net Amount'] == 0]
        print(f"\n  ⚠️ Zero Payment Bundles: {len(zero_payments)} ({len(zero_payments)/len(df)*100:.2f}%)")
        
        # Sender Analysis
        print("\n🏢 TOP PAYERS (SENDERS):")
        print("-" * 80)
        sender_analysis = df.groupby('Sender Name').agg({
            'Net Amount': 'sum',
            'Number Of Claims': 'sum',
            'Bundle ID': 'count'
        }).sort_values('Net Amount', ascending=False).head(5)
        
        for sender, row in sender_analysis.iterrows():
            print(f"  {sender[:50]:50s}")
            print(f"    Amount Paid: SAR {row['Net Amount']:,.2f} | Claims: {row['Number Of Claims']:.0f} | Bundles: {row['Bundle ID']}")
        
        # Daily Payment Pattern
        if 'Submission Date' in df.columns:
            print("\n📅 PAYMENT TIMELINE:")
            print("-" * 80)
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Date'] = df['Submission Date'].dt.date
            daily_payments = df.groupby('Date')['Net Amount'].sum()
            print(f"  Average Daily Payment: SAR {daily_payments.mean():,.2f}")
            print(f"  Highest Payment Day: {daily_payments.idxmax()} (SAR {daily_payments.max():,.2f})")
        
        print("\n")
    
    def analyze_eligibility(self):
        """Analyze eligibility requests"""
        if self.eligibility_df is None or len(self.eligibility_df) == 0:
            return
        
        print("=" * 80)
        print("ELIGIBILITY REQUEST ANALYSIS")
        print("=" * 80)
        
        df = self.eligibility_df.copy()
        
        # Status Distribution
        print("\n📊 ELIGIBILITY STATUS:")
        print("-" * 80)
        status_dist = df['Status'].value_counts()
        for status, count in status_dist.items():
            pct = (count / len(df)) * 100
            print(f"  {status:15s}: {count:6d} ({pct:5.2f}%)")
        
        # Error Analysis
        errors = df[df['Status'] == 'Error']
        if len(errors) > 0:
            print(f"\n  ⚠️ Total Errors: {len(errors)} ({len(errors)/len(df)*100:.2f}%)")
            print("\n  Top 5 Patients with Most Eligibility Errors:")
            error_patients = errors['Patient Identifier'].value_counts().head(5)
            for patient, count in error_patients.items():
                print(f"    Patient {patient}: {count} errors")
        
        # Insurer Analysis
        print("\n🏢 INSURERS QUERIED:")
        print("-" * 80)
        insurer_dist = df['Insurer Name'].value_counts().head(10)
        for insurer, count in insurer_dist.items():
            print(f"  {insurer[:60]:60s}: {count:4d}")
        
        print("\n")
    
    def analyze_prior_authorization(self):
        """Analyze prior authorization data"""
        if self.auth_df is None or len(self.auth_df) == 0:
            return
        
        print("=" * 80)
        print("PRIOR AUTHORIZATION ANALYSIS")
        print("=" * 80)
        
        df = self.auth_df.copy()
        
        print(f"\n📋 Total Prior Authorization Requests: {len(df)}")
        
        # Claim Type Distribution
        if 'Claim Type' in df.columns:
            print("\n📊 AUTHORIZATION BY CLAIM TYPE:")
            print("-" * 80)
            claim_type_dist = df['Claim Type'].value_counts()
            for ctype, count in claim_type_dist.items():
                pct = (count / len(df)) * 100
                print(f"  {ctype:20s}: {count:4d} ({pct:5.2f}%)")
        
        # Insurer Distribution
        print("\n🏢 TOP INSURERS FOR PRIOR AUTH:")
        print("-" * 80)
        insurer_dist = df['Insurer Name'].value_counts().head(5)
        for insurer, count in insurer_dist.items():
            print(f"  {insurer[:60]:60s}: {count:4d}")
        
        # Temporal Analysis
        if 'Submission Date' in df.columns:
            df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df['Date'] = df['Submission Date'].dt.date
            daily_auth = df.groupby('Date').size()
            print(f"\n📅 Daily Authorization Requests:")
            print(f"  Average: {daily_auth.mean():.0f} per day")
            print(f"  Peak: {daily_auth.max()} requests on {daily_auth.idxmax()}")
        
        print("\n")
    
    def analyze_communications(self):
        """Analyze communication requests"""
        if self.comm_df is None or len(self.comm_df) == 0:
            return
        
        print("=" * 80)
        print("COMMUNICATION REQUEST ANALYSIS")
        print("=" * 80)
        
        df = self.comm_df.copy()
        
        print(f"\n📨 Total Communication Requests: {len(df)}")
        
        # Communication patterns
        if 'Associated Transaction' in df.columns:
            print("\n🔗 COMMUNICATION PATTERNS:")
            print("-" * 80)
            comm_per_transaction = df.groupby('Associated Transaction').size()
            print(f"  Average Communications per Transaction: {comm_per_transaction.mean():.2f}")
            print(f"  Max Communications for Single Transaction: {comm_per_transaction.max()}")
            
            # Find transactions with most communications
            top_comm_transactions = comm_per_transaction.nlargest(5)
            print("\n  Transactions with Most Communications:")
            for trans, count in top_comm_transactions.items():
                print(f"    Transaction {trans}: {count} communications")
        
        # Sender Analysis
        print("\n🏢 TOP COMMUNICATION SENDERS:")
        print("-" * 80)
        sender_dist = df['Sender Name'].value_counts().head(5)
        for sender, count in sender_dist.items():
            print(f"  {sender[:60]:60s}: {count:4d}")
        
        print("\n")
    
    def find_patterns_and_issues(self):
        """Identify patterns, trends, and potential issues"""
        print("=" * 80)
        print("PATTERNS, TRENDS & ISSUE DETECTION")
        print("=" * 80)
        
        issues_found = []
        
        # Issue 1: High Rejection Rate
        if self.claims_df is not None:
            rejected_pct = len(self.claims_df[self.claims_df['Status'].isin(['Rejected', 'Cancelled', 'Error'])]) / len(self.claims_df) * 100
            if rejected_pct > 30:
                issues_found.append(f"⚠️ HIGH REJECTION RATE: {rejected_pct:.1f}% of claims are rejected/cancelled/error")
        
        # Issue 2: Zero Payments
        if self.payment_df is not None:
            zero_pct = len(self.payment_df[self.payment_df['Net Amount'] == 0]) / len(self.payment_df) * 100
            if zero_pct > 20:
                issues_found.append(f"⚠️ HIGH ZERO PAYMENTS: {zero_pct:.1f}% of payment bundles have zero amount")
        
        # Issue 3: Eligibility Errors
        if self.eligibility_df is not None:
            error_pct = len(self.eligibility_df[self.eligibility_df['Status'] == 'Error']) / len(self.eligibility_df) * 100
            if error_pct > 50:
                issues_found.append(f"⚠️ HIGH ELIGIBILITY ERRORS: {error_pct:.1f}% of eligibility checks fail")
        
        # Issue 4: Repeated Patient Errors
        if self.eligibility_df is not None:
            errors = self.eligibility_df[self.eligibility_df['Status'] == 'Error']
            if len(errors) > 0:
                repeated_errors = errors['Patient Identifier'].value_counts()
                if repeated_errors.max() >= 5:
                    issues_found.append(f"⚠️ REPEATED ELIGIBILITY FAILURES: Some patients have {repeated_errors.max()} failed eligibility checks")
        
        # Issue 5: Excessive Communications
        if self.comm_df is not None and 'Associated Transaction' in self.comm_df.columns:
            comm_per_trans = self.comm_df.groupby('Associated Transaction').size()
            if comm_per_trans.max() >= 10:
                issues_found.append(f"⚠️ EXCESSIVE COMMUNICATIONS: Some transactions have {comm_per_trans.max()} communication requests")
        
        if issues_found:
            print("\n🔴 ISSUES DETECTED:")
            print("-" * 80)
            for i, issue in enumerate(issues_found, 1):
                print(f"{i}. {issue}")
        else:
            print("\n✅ No major issues detected")
        
        # POSITIVE PATTERNS
        print("\n\n✅ POSITIVE PATTERNS:")
        print("-" * 80)
        
        if self.claims_df is not None:
            approved = len(self.claims_df[self.claims_df['Status'] == 'Approved'])
            if approved > 0:
                approved_pct = approved / len(self.claims_df) * 100
                print(f"• {approved_pct:.1f}% of claims are fully approved")
        
        print("\n")
    
    def relational_analysis(self):
        """Deep relational analysis across datasets"""
        print("=" * 80)
        print("RELATIONAL DEEP-DIVE ANALYSIS")
        print("=" * 80)
        
        # 1. Claims to Payment Reconciliation
        if self.claims_df is not None and self.payment_df is not None:
            print("\n🔗 CLAIMS vs PAYMENTS:")
            print("-" * 80)
            
            total_claim_amount = self.claims_df['Net Amount'].sum()
            total_payment_amount = self.payment_df['Net Amount'].sum()
            
            print(f"  Total Claimed Amount: SAR {total_claim_amount:,.2f}")
            print(f"  Total Paid Amount:    SAR {total_payment_amount:,.2f}")
            
            if total_claim_amount > 0:
                payment_ratio = (total_payment_amount / total_claim_amount) * 100
                print(f"  Payment to Claim Ratio: {payment_ratio:.2f}%")
        
        # 2. Prior Auth to Claims
        if self.auth_df is not None and self.claims_df is not None:
            print("\n🔗 PRIOR AUTH vs CLAIMS:")
            print("-" * 80)
            print(f"  Prior Auth Requests: {len(self.auth_df)}")
            print(f"  Total Claims: {len(self.claims_df)}")
            
            # Match by patient identifier
            if 'Patient Identifier' in self.auth_df.columns and 'Patient Identifier' in self.claims_df.columns:
                auth_patients = set(self.auth_df['Patient Identifier'].dropna())
                claim_patients = set(self.claims_df['Patient Identifier'].dropna())
                common_patients = auth_patients.intersection(claim_patients)
                print(f"  Patients with both Auth & Claims: {len(common_patients)}")
        
        # 3. Eligibility to Claims
        if self.eligibility_df is not None and self.claims_df is not None:
            print("\n🔗 ELIGIBILITY vs CLAIMS:")
            print("-" * 80)
            print(f"  Eligibility Checks: {len(self.eligibility_df)}")
            print(f"  Total Claims: {len(self.claims_df)}")
            
            if 'Patient Identifier' in self.eligibility_df.columns and 'Patient Identifier' in self.claims_df.columns:
                elig_patients = set(self.eligibility_df['Patient Identifier'].dropna())
                claim_patients = set(self.claims_df['Patient Identifier'].dropna())
                claims_without_elig = claim_patients - elig_patients
                print(f"  Claims submitted without prior eligibility check: {len(claims_without_elig)}")
        
        # 4. Communication Patterns
        if self.comm_df is not None:
            print("\n🔗 COMMUNICATION PATTERNS:")
            print("-" * 80)
            if 'Associated Transaction' in self.comm_df.columns:
                transactions_with_comm = self.comm_df['Associated Transaction'].nunique()
                total_comms = len(self.comm_df)
                print(f"  Transactions with Communications: {transactions_with_comm}")
                print(f"  Total Communications: {total_comms}")
                print(f"  Avg Communications per Transaction: {total_comms/transactions_with_comm:.2f}")
        
        print("\n")
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        print("=" * 80)
        print("RECOMMENDATIONS & ACTION ITEMS")
        print("=" * 80)
        print()
        
        recommendations = []
        
        # Based on claims analysis
        if self.claims_df is not None:
            rejected_pct = len(self.claims_df[self.claims_df['Status'].isin(['Rejected', 'Cancelled', 'Error'])]) / len(self.claims_df) * 100
            
            if rejected_pct > 20:
                recommendations.append(
                    "1. REDUCE CLAIM REJECTIONS:\n"
                    "   • Review rejection reasons with top rejecting insurers\n"
                    "   • Implement pre-submission validation\n"
                    "   • Staff training on claim coding and documentation"
                )
            
            # Partial approvals
            partial = self.claims_df[self.claims_df['Status'] == 'Partial']
            if len(partial) > 0:
                recommendations.append(
                    "2. MINIMIZE PARTIAL APPROVALS:\n"
                    "   • Analyze partial approval patterns\n"
                    "   • Review service bundling strategies\n"
                    "   • Negotiate better terms with insurers"
                )
        
        # Based on eligibility
        if self.eligibility_df is not None:
            error_pct = len(self.eligibility_df[self.eligibility_df['Status'] == 'Error']) / len(self.eligibility_df) * 100
            if error_pct > 50:
                recommendations.append(
                    "3. FIX ELIGIBILITY CHECKING ISSUES:\n"
                    "   • Investigate technical integration problems\n"
                    "   • Verify patient identifier formats\n"
                    "   • Contact NPHIES support for persistent errors"
                )
        
        # Based on communications
        if self.comm_df is not None and 'Associated Transaction' in self.comm_df.columns:
            comm_per_trans = self.comm_df.groupby('Associated Transaction').size()
            if comm_per_trans.mean() > 2:
                recommendations.append(
                    "4. STREAMLINE COMMUNICATION PROCESS:\n"
                    "   • Reduce back-and-forth communications\n"
                    "   • Improve initial claim documentation\n"
                    "   • Implement automated response templates"
                )
        
        # Financial recommendations
        if self.claims_df is not None:
            total_submitted = self.claims_df['Net Amount'].sum()
            total_approved = self.claims_df['Approved Amount'].sum()
            if total_submitted > 0:
                loss_pct = ((total_submitted - total_approved) / total_submitted) * 100
                if loss_pct > 20:
                    recommendations.append(
                        f"5. REVENUE OPTIMIZATION:\n"
                        f"   • Current loss rate: {loss_pct:.1f}%\n"
                        "   • Implement revenue cycle analytics\n"
                        "   • Focus on high-value claim accuracy\n"
                        "   • Appeal rejected high-value claims"
                    )
        
        if recommendations:
            for rec in recommendations:
                print(rec)
                print()
        else:
            print("✅ Operations appear to be running smoothly!")
            print()
    
    def export_summary_report(self):
        """Export detailed summary to text file"""
        report_path = os.path.join(self.output_folder, 'nphies_analysis_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("NPHIES DATA ANALYSIS SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary statistics
            if self.claims_df is not None:
                f.write("CLAIMS SUMMARY:\n")
                f.write(f"  Total Claims: {len(self.claims_df)}\n")
                f.write(f"  Status Distribution:\n")
                for status, count in self.claims_df['Status'].value_counts().items():
                    f.write(f"    {status}: {count}\n")
                f.write("\n")
            
            if self.payment_df is not None:
                f.write("PAYMENT RECONCILIATION SUMMARY:\n")
                f.write(f"  Total Payment Bundles: {len(self.payment_df)}\n")
                f.write(f"  Total Amount: SAR {self.payment_df['Net Amount'].sum():,.2f}\n")
                f.write("\n")
            
            if self.eligibility_df is not None:
                f.write("ELIGIBILITY REQUESTS SUMMARY:\n")
                f.write(f"  Total Requests: {len(self.eligibility_df)}\n")
                f.write(f"  Status Distribution:\n")
                for status, count in self.eligibility_df['Status'].value_counts().items():
                    f.write(f"    {status}: {count}\n")
                f.write("\n")
        
        print(f"📄 Detailed report exported to: {report_path}\n")
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        if not self.load_data():
            print("Failed to load data. Exiting...")
            return
        
        # Run all analyses
        self.analyze_claims()
        self.analyze_payment_reconciliation()
        self.analyze_eligibility()
        self.analyze_prior_authorization()
        self.analyze_communications()
        self.find_patterns_and_issues()
        self.relational_analysis()
        self.generate_recommendations()
        self.export_summary_report()
        
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nOutput folder: {self.output_folder}")
        print("\nThank you for using NPHIES Analyzer!")
        print()


def main():
    """Main execution function"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "     NPHIES DATA ANALYZER - Comprehensive Healthcare Data Insights".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    # Set folder path
    folder_path = r"c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
    
    # Create analyzer instance
    analyzer = NPHIESAnalyzer(folder_path)
    
    # Run full analysis
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
