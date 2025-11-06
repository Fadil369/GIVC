import pandas as pd
import numpy as np
from datetime import datetime
import json

print("=" * 100)
print("PATTERN ANALYSIS, CATEGORIZATIONS & SOLUTIONS - NPHIES JAZAN AUGUST 2025")
print("=" * 100)

base_path = r"C:\Users\rcmrejection3\OneDrive\Desktop\nphies-export-jazan-aug-extracted\nphies-export-jazan-aug"
df = pd.read_csv(f"{base_path}\\merged_all_data.csv", low_memory=False)

print(f"\n✓ Loaded {len(df):,} records\n")

# ==================================================================================
# PATTERN #1: CLAIM VALUE DISTRIBUTION PATTERNS
# ==================================================================================
print("=" * 100)
print("🔍 PATTERN #1: CLAIM VALUE DISTRIBUTION & ANOMALIES")
print("=" * 100)

# Categorize claims by value
df['Value_Category'] = pd.cut(df['Net Amount'], 
                               bins=[0, 100, 500, 1000, 5000, 10000, 50000, float('inf')],
                               labels=['Micro (<100)', 'Small (100-500)', 'Medium (500-1K)', 
                                      'Large (1K-5K)', 'Very Large (5K-10K)', 
                                      'High Value (10K-50K)', 'Ultra High (>50K)'])

print("\n💵 CLAIM VALUE DISTRIBUTION:")
value_dist = df.groupby('Value_Category').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': ['sum', 'mean'],
    'Status': lambda x: (x.isin(['Rejected', 'Error', 'Cancelled'])).sum()
}).round(2)

for category in df['Value_Category'].cat.categories:
    cat_df = df[df['Value_Category'] == category]
    if len(cat_df) > 0:
        total_claimed = cat_df['Net Amount'].sum()
        total_approved = cat_df['Approved Amount'].sum()
        rejection_count = cat_df[cat_df['Status'].isin(['Rejected', 'Error', 'Cancelled'])].shape[0]
        rejection_rate = (rejection_count / len(cat_df) * 100)
        
        print(f"\n   {category}:")
        print(f"      • Count: {len(cat_df):,} claims ({len(cat_df)/len(df)*100:.1f}%)")
        print(f"      • Total Value: {total_claimed:,.2f} SAR")
        print(f"      • Avg Claim: {cat_df['Net Amount'].mean():,.2f} SAR")
        print(f"      • Rejection Rate: {rejection_rate:.1f}%")
        print(f"      • Loss Amount: {total_claimed - total_approved:,.2f} SAR")

# ==================================================================================
# PATTERN #2: PROVIDER PERFORMANCE PATTERNS
# ==================================================================================
print("\n" + "=" * 100)
print("🔍 PATTERN #2: PROVIDER PERFORMANCE PATTERNS")
print("=" * 100)

provider_analysis = df.groupby('Provider Name').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': ['sum', 'mean'],
    'Status': lambda x: (x == 'Approved').sum()
}).round(2)

provider_analysis.columns = ['Count', 'Total_Claimed', 'Avg_Claimed', 
                             'Total_Approved', 'Avg_Approved', 'Approved_Count']
provider_analysis['Approval_Rate'] = (provider_analysis['Approved_Count'] / 
                                     provider_analysis['Count'] * 100).round(2)
provider_analysis['Loss_Amount'] = provider_analysis['Total_Claimed'] - provider_analysis['Total_Approved']

# Filter providers with significant volume
significant_providers = provider_analysis[provider_analysis['Count'] >= 50].sort_values('Loss_Amount', ascending=False)

print(f"\n🏥 TOP 10 PROVIDERS BY LOSS (Min 50 claims):")
for idx, (provider, row) in enumerate(significant_providers.head(10).iterrows(), 1):
    print(f"\n   {idx}. {provider}")
    print(f"      • Claims: {int(row['Count']):,}")
    print(f"      • Total Loss: {row['Loss_Amount']:,.2f} SAR")
    print(f"      • Approval Rate: {row['Approval_Rate']:.1f}%")
    print(f"      • Avg Claim: {row['Avg_Claimed']:,.2f} SAR")

# ==================================================================================
# PATTERN #3: CLAIM TYPE + INSURER COMBINATION PATTERNS
# ==================================================================================
print("\n" + "=" * 100)
print("🔍 PATTERN #3: CLAIM TYPE × INSURER COMBINATION PATTERNS")
print("=" * 100)

# Create combination analysis
combo_analysis = df.groupby(['Claim Type', 'Insurer Name']).agg({
    'Net Amount': ['count', 'sum'],
    'Approved Amount': 'sum',
    'Status': lambda x: (x == 'Rejected').sum()
}).round(2)

combo_analysis.columns = ['Count', 'Claimed', 'Approved', 'Rejected_Count']
combo_analysis['Loss'] = combo_analysis['Claimed'] - combo_analysis['Approved']
combo_analysis['Rejection_Rate'] = (combo_analysis['Rejected_Count'] / combo_analysis['Count'] * 100).round(2)

# Find problematic combinations
problematic_combos = combo_analysis[
    (combo_analysis['Count'] >= 20) & 
    (combo_analysis['Rejection_Rate'] > 30)
].sort_values('Loss', ascending=False)

print(f"\n⚠ PROBLEMATIC CLAIM TYPE × INSURER COMBINATIONS:")
print(f"   (Min 20 claims, >30% rejection rate)\n")

for idx, ((claim_type, insurer), row) in enumerate(problematic_combos.head(15).iterrows(), 1):
    print(f"   {idx}. {claim_type.upper()} claims with {insurer}")
    print(f"      • Count: {int(row['Count'])} | Rejection Rate: {row['Rejection_Rate']:.1f}%")
    print(f"      • Loss: {row['Loss']:,.2f} SAR")

# ==================================================================================
# PATTERN #4: TEMPORAL PATTERNS (Day of Week, Time of Day)
# ==================================================================================
print("\n" + "=" * 100)
print("🔍 PATTERN #4: TEMPORAL SUBMISSION PATTERNS")
print("=" * 100)

df['Submission_DT'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
df['DayOfWeek'] = df['Submission_DT'].dt.day_name()
df['Hour'] = df['Submission_DT'].dt.hour

# Day of week patterns
dow_analysis = df.groupby('DayOfWeek').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': 'sum',
    'Status': lambda x: (x.isin(['Rejected', 'Error'])).sum()
}).round(2)

print("\n📅 DAY OF WEEK PATTERNS:")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in day_order:
    if day in df['DayOfWeek'].values:
        day_df = df[df['DayOfWeek'] == day]
        claimed = day_df['Net Amount'].sum()
        approved = day_df['Approved Amount'].sum()
        error_rate = (day_df['Status'].isin(['Rejected', 'Error']).sum() / len(day_df) * 100)
        
        print(f"\n   {day}:")
        print(f"      • Claims: {len(day_df):,}")
        print(f"      • Total Claimed: {claimed:,.2f} SAR")
        print(f"      • Loss: {claimed - approved:,.2f} SAR")
        print(f"      • Error/Rejection Rate: {error_rate:.1f}%")

# ==================================================================================
# PATTERN #5: PATIENT-LEVEL PATTERNS
# ==================================================================================
print("\n" + "=" * 100)
print("🔍 PATTERN #5: PATIENT-LEVEL PATTERNS")
print("=" * 100)

patient_analysis = df.groupby('Patient Identifier').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': 'sum',
    'Status': lambda x: (x == 'Rejected').sum()
}).round(2)

patient_analysis.columns = ['Claim_Count', 'Total_Claimed', 'Avg_Claimed', 
                           'Total_Approved', 'Rejected_Count']
patient_analysis['Loss'] = patient_analysis['Total_Claimed'] - patient_analysis['Total_Approved']

# High-frequency patients
high_freq_patients = patient_analysis[patient_analysis['Claim_Count'] >= 10].sort_values('Claim_Count', ascending=False)

print(f"\n👥 HIGH-FREQUENCY PATIENTS (≥10 claims):")
print(f"   • Total Patients: {len(high_freq_patients):,}")
print(f"   • Total Claims: {high_freq_patients['Claim_Count'].sum():,.0f}")
print(f"   • Total Value: {high_freq_patients['Total_Claimed'].sum():,.2f} SAR")

# Patients with high losses
high_loss_patients = patient_analysis[patient_analysis['Loss'] >= 50000].sort_values('Loss', ascending=False)

print(f"\n💸 HIGH-LOSS PATIENTS (≥50K SAR loss):")
print(f"   • Total Patients: {len(high_loss_patients):,}")
print(f"   • Total Loss: {high_loss_patients['Loss'].sum():,.2f} SAR")

if len(high_loss_patients) > 0:
    print(f"\n   Top 5 by Loss:")
    for idx, (patient_id, row) in enumerate(high_loss_patients.head(5).iterrows(), 1):
        print(f"   {idx}. Patient {patient_id}")
        print(f"      • Claims: {int(row['Claim_Count'])}")
        print(f"      • Total Loss: {row['Loss']:,.2f} SAR")

# ==================================================================================
# CATEGORIZATION: ISSUE CATEGORIES
# ==================================================================================
print("\n" + "=" * 100)
print("📂 CATEGORIZATION: ISSUE CATEGORIES & ROOT CAUSES")
print("=" * 100)

# Categorize claims by issue type
def categorize_issue(row):
    status = row['Status']
    claim_type = row['Claim Type']
    approved_amt = row['Approved Amount']
    claimed_amt = row['Net Amount']
    
    if status == 'Rejected':
        return 'Complete Rejection'
    elif status == 'Error':
        return 'Technical Error'
    elif status == 'Pended':
        return 'Documentation Issue'
    elif status == 'Partial':
        if approved_amt < claimed_amt * 0.5:
            return 'Major Partial Denial'
        else:
            return 'Minor Partial Denial'
    elif status == 'Cancelled':
        return 'Cancelled Claim'
    elif status == 'Approved':
        return 'Fully Approved'
    else:
        return 'Other Status'

df['Issue_Category'] = df.apply(categorize_issue, axis=1)

print("\n🏷 ISSUE CATEGORY DISTRIBUTION:")
issue_summary = df.groupby('Issue_Category').agg({
    'Net Amount': ['count', 'sum'],
    'Approved Amount': 'sum'
}).round(2)

issue_summary.columns = ['Count', 'Claimed', 'Approved']
issue_summary['Loss'] = issue_summary['Claimed'] - issue_summary['Approved']
issue_summary = issue_summary.sort_values('Loss', ascending=False)

for category, row in issue_summary.iterrows():
    print(f"\n   {category}:")
    print(f"      • Count: {int(row['Count']):,} claims")
    print(f"      • Claimed: {row['Claimed']:,.2f} SAR")
    print(f"      • Loss: {row['Loss']:,.2f} SAR")

# ==================================================================================
# SOLUTIONS & RECOMMENDATIONS
# ==================================================================================
print("\n" + "=" * 100)
print("💡 SOLUTIONS & RECOMMENDATIONS FRAMEWORK")
print("=" * 100)

solutions = {
    "Complete Rejection": {
        "priority": "🔴 CRITICAL",
        "immediate_actions": [
            "Review rejection reasons through NPHIES portal",
            "Categorize rejections by error code",
            "Prepare appeal documentation for valid claims",
            "Schedule meetings with top 3 rejecting insurers"
        ],
        "short_term": [
            "Implement pre-submission validation checklist",
            "Train billing team on common rejection causes",
            "Create rejection reason database for tracking"
        ],
        "long_term": [
            "Develop automated validation system",
            "Establish direct communication channels with insurers",
            "Implement AI-based claim review before submission"
        ]
    },
    "Major Partial Denial": {
        "priority": "🔴 CRITICAL",
        "immediate_actions": [
            "Analyze partial denial patterns by service type",
            "Review pricing agreements with insurers",
            "Document discrepancies for negotiation",
            "Initiate appeals for high-value partials"
        ],
        "short_term": [
            "Create service code mapping validation",
            "Review and update fee schedules",
            "Implement partial denial tracking system"
        ],
        "long_term": [
            "Renegotiate contracts with problematic insurers",
            "Establish clear pricing transparency",
            "Implement predictive approval modeling"
        ]
    },
    "Technical Error": {
        "priority": "🟠 HIGH",
        "immediate_actions": [
            "Review all error status claims",
            "Identify common technical issues",
            "Resubmit corrected claims within 24 hours",
            "Contact NPHIES support for persistent errors"
        ],
        "short_term": [
            "Implement robust error handling in billing system",
            "Create technical error playbook",
            "Schedule NPHIES integration review"
        ],
        "long_term": [
            "Upgrade billing system with better validation",
            "Implement automated error detection and correction",
            "Establish redundant submission pathways"
        ]
    },
    "Documentation Issue": {
        "priority": "🟡 MEDIUM",
        "immediate_actions": [
            "Review all pended claims daily",
            "Prepare required documentation promptly",
            "Set up daily pending claims monitoring",
            "Assign dedicated team for pending follow-ups"
        ],
        "short_term": [
            "Create documentation checklist by claim type",
            "Implement document management system",
            "Train clinical staff on documentation requirements"
        ],
        "long_term": [
            "Implement EMR integration with billing",
            "Create automated documentation generation",
            "Establish proactive documentation review process"
        ]
    }
}

for issue_type, solution in solutions.items():
    issue_data = issue_summary[issue_summary.index == issue_type]
    if len(issue_data) > 0:
        print(f"\n{'='*100}")
        print(f"🎯 {issue_type.upper()} - Priority: {solution['priority']}")
        print(f"   Impact: {int(issue_data['Count'].values[0]):,} claims | {issue_data['Loss'].values[0]:,.2f} SAR loss")
        print(f"{'='*100}")
        
        print(f"\n   ⚡ IMMEDIATE ACTIONS (Next 48 hours):")
        for action in solution['immediate_actions']:
            print(f"      • {action}")
        
        print(f"\n   📋 SHORT-TERM SOLUTIONS (1-2 weeks):")
        for action in solution['short_term']:
            print(f"      • {action}")
        
        print(f"\n   🎯 LONG-TERM STRATEGY (1-3 months):")
        for action in solution['long_term']:
            print(f"      • {action}")

# ==================================================================================
# SAVE DETAILED PATTERN ANALYSIS
# ==================================================================================
print("\n" + "=" * 100)
print("💾 SAVING PATTERN ANALYSIS REPORTS")
print("=" * 100)

# Save value category analysis
value_category_report = df.groupby('Value_Category').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': ['sum', 'mean'],
    'Status': lambda x: list(x.value_counts().to_dict().items())
}).round(2)
value_category_report.to_csv(f'{base_path}\\value_category_analysis.csv')
print(f"✓ value_category_analysis.csv")

# Save provider performance
significant_providers.to_csv(f'{base_path}\\provider_performance_analysis.csv')
print(f"✓ provider_performance_analysis.csv")

# Save problematic combinations
problematic_combos.to_csv(f'{base_path}\\problematic_claim_insurer_combinations.csv')
print(f"✓ problematic_claim_insurer_combinations.csv")

# Save issue categorization
issue_summary.to_csv(f'{base_path}\\issue_categorization_summary.csv')
print(f"✓ issue_categorization_summary.csv")

# Save high-loss patients
if len(high_loss_patients) > 0:
    high_loss_patients.to_csv(f'{base_path}\\high_loss_patients.csv')
    print(f"✓ high_loss_patients.csv")

# Create comprehensive solutions guide
solutions_guide = {
    "analysis_date": datetime.now().isoformat(),
    "total_claims": len(df),
    "total_loss": float(df['Net Amount'].sum() - df['Approved Amount'].sum()),
    "issue_categories": {
        category: {
            "count": int(row['Count']),
            "claimed": float(row['Claimed']),
            "loss": float(row['Loss']),
            "solutions": solutions.get(category, {})
        }
        for category, row in issue_summary.iterrows()
    },
    "critical_patterns": {
        "high_value_claims": int(len(df[df['Value_Category'] == 'Ultra High (>50K)'])),
        "problematic_combinations": len(problematic_combos),
        "high_loss_patients": len(high_loss_patients),
        "significant_providers": len(significant_providers)
    }
}

with open(f'{base_path}\\comprehensive_solutions_guide.json', 'w', encoding='utf-8') as f:
    json.dump(solutions_guide, f, indent=2, ensure_ascii=False)
print(f"✓ comprehensive_solutions_guide.json")

print("\n" + "=" * 100)
print("✅ PATTERN ANALYSIS & SOLUTIONS COMPLETE!")
print("=" * 100)

print(f"\n📊 SUMMARY OF FINDINGS:")
print(f"   • {len(df['Value_Category'].unique())} value categories identified")
print(f"   • {len(significant_providers)} significant providers analyzed")
print(f"   • {len(problematic_combos)} problematic claim-insurer combinations found")
print(f"   • {len(issue_summary)} distinct issue categories")
print(f"   • {len(high_loss_patients)} high-loss patients identified")

print(f"\n🎯 NEXT STEPS:")
print(f"   1. Review comprehensive_solutions_guide.json for detailed action plans")
print(f"   2. Prioritize actions based on financial impact")
print(f"   3. Assign teams to execute immediate actions")
print(f"   4. Set up weekly monitoring of KPIs")
print(f"   5. Schedule follow-up analysis in 30 days")

print("\n" + "=" * 100)
