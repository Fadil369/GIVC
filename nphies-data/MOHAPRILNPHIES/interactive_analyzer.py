"""
Interactive NPHIES Data Analyzer
==================================
Interactive command-line interface for comprehensive NPHIES data analysis
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

class InteractiveNPHIESAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.output_folder = os.path.join(folder_path, 'analysis_output')
        os.makedirs(self.output_folder, exist_ok=True)
        
        self.claims_df = None
        self.payment_df = None
        self.eligibility_df = None
        self.auth_df = None
        self.comm_df = None
        
        self.loaded = False
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(title.center(80))
        print("=" * 80 + "\n")
    
    def print_menu(self):
        """Display main menu"""
        self.clear_screen()
        print("╔" + "=" * 78 + "╗")
        print("║" + "NPHIES INTERACTIVE DATA ANALYZER".center(78) + "║")
        print("║" + "Al-Hayat National Hospital - Unaizah - Al-Qassim".center(78) + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print("MAIN MENU:")
        print("-" * 80)
        print()
        print("  DATA OPERATIONS:")
        print("    1. Load Data Files")
        print("    2. View Data Summary")
        print()
        print("  ANALYSIS OPTIONS:")
        print("    3. Analyze Claims")
        print("    4. Analyze Payments")
        print("    5. Analyze Eligibility Requests")
        print("    6. Analyze Prior Authorization")
        print("    7. Analyze Communications")
        print()
        print("  ADVANCED ANALYSIS:")
        print("    8. Detect Issues & Patterns")
        print("    9. Relational Analysis")
        print("    10. Generate Recommendations")
        print()
        print("  REPORTS & EXPORTS:")
        print("    11. Export Excel Report")
        print("    12. Export Text Report")
        print("    13. Run Complete Analysis")
        print()
        print("  UTILITIES:")
        print("    14. Search Claims by Insurer")
        print("    15. Search Claims by Patient")
        print("    16. Calculate Custom Metrics")
        print()
        print("  0. Exit")
        print()
        print("-" * 80)
    
    def load_data(self):
        """Load all CSV files"""
        self.print_header("LOADING DATA FILES")
        
        try:
            print("Scanning folder for NPHIES files...")
            print()
            
            # Load Claims
            claim_files = [f for f in os.listdir(self.folder_path) if 'Claim_' in f and f.endswith('.csv')]
            if claim_files:
                self.claims_df = pd.read_csv(os.path.join(self.folder_path, claim_files[0]))
                print(f"✓ Claims: {len(self.claims_df):,} records loaded from {claim_files[0]}")
            else:
                print("⚠ No claims file found")
            
            # Load Payments
            payment_files = [f for f in os.listdir(self.folder_path) if 'PaymentReconciliation_' in f and f.endswith('.csv')]
            if payment_files:
                self.payment_df = pd.read_csv(os.path.join(self.folder_path, payment_files[0]))
                print(f"✓ Payments: {len(self.payment_df):,} records loaded from {payment_files[0]}")
            else:
                print("⚠ No payment file found")
            
            # Load Eligibility
            eligibility_files = [f for f in os.listdir(self.folder_path) if 'EligibilityRequest_' in f and f.endswith('.csv')]
            if eligibility_files:
                self.eligibility_df = pd.read_csv(os.path.join(self.folder_path, eligibility_files[0]))
                print(f"✓ Eligibility: {len(self.eligibility_df):,} records loaded from {eligibility_files[0]}")
            else:
                print("⚠ No eligibility file found")
            
            # Load Authorization
            auth_files = [f for f in os.listdir(self.folder_path) if 'AdvancedAuth_' in f and f.endswith('.csv')]
            if auth_files:
                self.auth_df = pd.read_csv(os.path.join(self.folder_path, auth_files[0]))
                print(f"✓ Authorization: {len(self.auth_df):,} records loaded from {auth_files[0]}")
            else:
                print("⚠ No authorization file found")
            
            # Load Communications
            comm_files = [f for f in os.listdir(self.folder_path) if 'CommunicationRequest_' in f and f.endswith('.csv')]
            if comm_files:
                self.comm_df = pd.read_csv(os.path.join(self.folder_path, comm_files[0]))
                print(f"✓ Communications: {len(self.comm_df):,} records loaded from {comm_files[0]}")
            else:
                print("⚠ No communication file found")
            
            self.loaded = True
            print()
            print("✅ Data loading complete!")
            
        except Exception as e:
            print(f"\n❌ Error loading data: {e}")
            self.loaded = False
        
        input("\nPress Enter to continue...")
    
    def view_summary(self):
        """Display data summary"""
        if not self.loaded:
            print("\n⚠ Please load data first (Option 1)")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("DATA SUMMARY")
        
        if self.claims_df is not None:
            print(f"📊 CLAIMS DATA:")
            print(f"   Total Records: {len(self.claims_df):,}")
            print(f"   Date Range: {self.claims_df['Submission Date'].min()} to {self.claims_df['Submission Date'].max()}")
            print(f"   Unique Patients: {self.claims_df['Patient Identifier'].nunique():,}")
            print(f"   Unique Insurers: {self.claims_df['Insurer Name'].nunique()}")
            print()
        
        if self.payment_df is not None:
            print(f"💳 PAYMENT DATA:")
            print(f"   Total Records: {len(self.payment_df):,}")
            print(f"   Total Amount: SAR {self.payment_df['Net Amount'].sum():,.2f}")
            print(f"   Unique Payers: {self.payment_df['Sender Name'].nunique()}")
            print()
        
        if self.eligibility_df is not None:
            print(f"🔍 ELIGIBILITY DATA:")
            print(f"   Total Records: {len(self.eligibility_df):,}")
            print(f"   Unique Patients: {self.eligibility_df['Patient Identifier'].nunique():,}")
            print()
        
        if self.auth_df is not None:
            print(f"📋 AUTHORIZATION DATA:")
            print(f"   Total Records: {len(self.auth_df):,}")
            print()
        
        if self.comm_df is not None:
            print(f"💬 COMMUNICATION DATA:")
            print(f"   Total Records: {len(self.comm_df):,}")
            print()
        
        input("\nPress Enter to continue...")
    
    def search_by_insurer(self):
        """Search claims by insurer"""
        if not self.loaded or self.claims_df is None:
            print("\n⚠ Please load claims data first")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("SEARCH CLAIMS BY INSURER")
        
        print("Available Insurers:")
        print("-" * 80)
        insurers = self.claims_df['Insurer Name'].value_counts()
        for i, (insurer, count) in enumerate(insurers.items(), 1):
            print(f"{i}. {insurer} ({count:,} claims)")
        
        print()
        choice = input("Enter insurer number (or 0 to cancel): ")
        
        try:
            idx = int(choice) - 1
            if idx < 0:
                return
            
            selected_insurer = insurers.index[idx]
            insurer_claims = self.claims_df[self.claims_df['Insurer Name'] == selected_insurer]
            
            print()
            print(f"\n{'='*80}")
            print(f"RESULTS FOR: {selected_insurer}")
            print(f"{'='*80}\n")
            
            print(f"Total Claims: {len(insurer_claims):,}")
            print()
            
            print("Status Distribution:")
            for status, count in insurer_claims['Status'].value_counts().items():
                pct = count / len(insurer_claims) * 100
                print(f"  {status:15s}: {count:6,} ({pct:5.1f}%)")
            
            print()
            print(f"Total Submitted: SAR {insurer_claims['Net Amount'].sum():,.2f}")
            print(f"Total Approved:  SAR {insurer_claims['Approved Amount'].sum():,.2f}")
            
        except (ValueError, IndexError):
            print("\n❌ Invalid selection")
        
        input("\nPress Enter to continue...")
    
    def search_by_patient(self):
        """Search claims by patient ID"""
        if not self.loaded or self.claims_df is None:
            print("\n⚠ Please load claims data first")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("SEARCH CLAIMS BY PATIENT")
        
        patient_id = input("Enter Patient Identifier: ").strip()
        
        if not patient_id:
            return
        
        patient_claims = self.claims_df[self.claims_df['Patient Identifier'].astype(str) == patient_id]
        
        if len(patient_claims) == 0:
            print(f"\n❌ No claims found for patient {patient_id}")
        else:
            print(f"\n{'='*80}")
            print(f"CLAIMS FOR PATIENT: {patient_id}")
            print(f"{'='*80}\n")
            
            print(f"Total Claims: {len(patient_claims)}")
            print()
            
            print("Claim Details:")
            for idx, row in patient_claims.iterrows():
                print(f"\n  Claim {row['Transaction Identifier']}:")
                print(f"    Date: {row['Submission Date']}")
                print(f"    Type: {row['Claim Type']} - {row['Claim Sub Type']}")
                print(f"    Status: {row['Status']}")
                print(f"    Amount: SAR {row['Net Amount']:,.2f}")
                print(f"    Insurer: {row['Insurer Name']}")
        
        input("\nPress Enter to continue...")
    
    def quick_claims_analysis(self):
        """Quick claims analysis"""
        if not self.loaded or self.claims_df is None:
            print("\n⚠ Please load claims data first")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("CLAIMS ANALYSIS")
        
        df = self.claims_df.copy()
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce')
        df['Approved Amount'] = pd.to_numeric(df['Approved Amount'], errors='coerce')
        
        print("STATUS DISTRIBUTION:")
        print("-" * 80)
        for status, count in df['Status'].value_counts().items():
            pct = count / len(df) * 100
            print(f"  {status:20s}: {count:6,} ({pct:5.2f}%)")
        
        print("\n\nFINANCIAL SUMMARY:")
        print("-" * 80)
        print(f"  Total Submitted: SAR {df['Net Amount'].sum():,.2f}")
        print(f"  Total Approved:  SAR {df['Approved Amount'].sum():,.2f}")
        print(f"  Loss Amount:     SAR {(df['Net Amount'].sum() - df['Approved Amount'].sum()):,.2f}")
        
        print("\n\nTOP 5 INSURERS:")
        print("-" * 80)
        for insurer, count in df['Insurer Name'].value_counts().head(5).items():
            print(f"  {insurer[:50]:50s}: {count:,} claims")
        
        input("\n\nPress Enter to continue...")
    
    def run_complete(self):
        """Run complete analysis"""
        if not self.loaded:
            print("\n⚠ Please load data first (Option 1)")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("RUNNING COMPLETE ANALYSIS")
        
        print("This will generate:")
        print("  • Comprehensive console output")
        print("  • Detailed text report")
        print("  • Excel report (if libraries available)")
        print()
        
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm != 'y':
            return
        
        print("\nRunning analysis...")
        
        # Import and run basic analyzer
        try:
            import nphies_analyzer
            analyzer = nphies_analyzer.NPHIESAnalyzer(self.folder_path)
            analyzer.claims_df = self.claims_df
            analyzer.payment_df = self.payment_df
            analyzer.eligibility_df = self.eligibility_df
            analyzer.auth_df = self.auth_df
            analyzer.comm_df = self.comm_df
            
            analyzer.analyze_claims()
            analyzer.analyze_payment_reconciliation()
            analyzer.analyze_eligibility()
            analyzer.analyze_prior_authorization()
            analyzer.analyze_communications()
            analyzer.find_patterns_and_issues()
            analyzer.relational_analysis()
            analyzer.generate_recommendations()
            analyzer.export_summary_report()
            
            print("\n✅ Analysis complete!")
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def run(self):
        """Main interactive loop"""
        while True:
            self.print_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == '0':
                print("\nThank you for using NPHIES Analyzer!")
                print()
                break
            elif choice == '1':
                self.load_data()
            elif choice == '2':
                self.view_summary()
            elif choice == '3':
                self.quick_claims_analysis()
            elif choice == '13':
                self.run_complete()
            elif choice == '14':
                self.search_by_insurer()
            elif choice == '15':
                self.search_by_patient()
            else:
                print("\n⚠ Feature coming soon or invalid option!")
                input("\nPress Enter to continue...")


def main():
    folder_path = r"c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
    analyzer = InteractiveNPHIESAnalyzer(folder_path)
    analyzer.run()


if __name__ == "__main__":
    main()
