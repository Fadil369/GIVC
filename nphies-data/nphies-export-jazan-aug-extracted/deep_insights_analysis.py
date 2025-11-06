import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import defaultdict

print("=" * 100)
print("DEEP INSIGHTS & STRATEGIC ANALYSIS - NPHIES JAZAN AUGUST 2025")
print("=" * 100)

base_path = r"C:\Users\rcmrejection3\OneDrive\Desktop\nphies-export-jazan-aug-extracted\nphies-export-jazan-aug"
df = pd.read_csv(f"{base_path}\\merged_all_data.csv", low_memory=False)

print(f"\n✓ Loaded {len(df):,} records for deep analysis\n")

# Parse dates
df['Submission_Date_Parsed'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')

# ==================================================================================
# CRITICAL INSIGHTS #1: FINANCIAL IMPACT ANALYSIS
# ==================================================================================
print("=" * 100)
print("📊 CRITICAL INSIGHT #1: FINANCIAL IMPACT ANALYSIS")
print("=" * 100)

total_claimed = df['Net Amount'].sum()
total_approved = df['Approved Amount'].sum()
total_rejected = total_claimed - total_approved
rejection_rate = (total_rejected / total_claimed * 100) if total_claimed > 0 else 0

print(f"\n💰 FINANCIAL OVERVIEW:")
print(f"   ╔══════════════════════════════════════════════════════════╗")
print(f"   ║ Total Claimed Amount:        {total_claimed:>18,.2f} SAR ║")
print(f"   ║ Total Approved Amount:       {total_approved:>18,.2f} SAR ║")
print(f"   ║ Total Rejected/Lost Amount:  {total_rejected:>18,.2f} SAR ║")
print(f"   ║ Financial Loss Rate:         {rejection_rate:>18.2f} %   ║")
print(f"   ╚══════════════════════════════════════════════════════════╝")

# Average claim values
avg_claim = df['Net Amount'].mean()
avg_approved = df['Approved Amount'].mean()
print(f"\n📈 AVERAGE VALUES:")
print(f"   • Average Claim Value:    {avg_claim:>12,.2f} SAR")
print(f"   • Average Approved Value: {avg_approved:>12,.2f} SAR")
print(f"   • Average Loss per Claim: {avg_claim - avg_approved:>12,.2f} SAR")

# ==================================================================================
# CRITICAL INSIGHTS #2: STATUS BREAKDOWN WITH FINANCIAL IMPACT
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #2: STATUS BREAKDOWN WITH FINANCIAL IMPACT")
print("=" * 100)

status_analysis = df.groupby('Status').agg({
    'Net Amount': ['count', 'sum', 'mean', 'median'],
    'Approved Amount': ['sum', 'mean']
}).round(2)

print("\n🔍 DETAILED STATUS ANALYSIS:")
print("-" * 100)

for status in df['Status'].dropna().unique():
    status_df = df[df['Status'] == status]
    count = len(status_df)
    pct = (count / len(df) * 100)
    claimed = status_df['Net Amount'].sum()
    approved = status_df['Approved Amount'].sum()
    lost = claimed - approved
    
    print(f"\n📌 {status.upper()}")
    print(f"   • Count: {count:,} claims ({pct:.1f}%)")
    print(f"   • Total Claimed: {claimed:,.2f} SAR")
    print(f"   • Total Approved: {approved:,.2f} SAR")
    print(f"   • Amount Lost: {lost:,.2f} SAR ({(lost/claimed*100):.1f}% loss rate)")
    print(f"   • Avg Claim: {status_df['Net Amount'].mean():,.2f} SAR")

# ==================================================================================
# CRITICAL INSIGHTS #3: INSURER PERFORMANCE ANALYSIS
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #3: INSURER PERFORMANCE ANALYSIS")
print("=" * 100)

insurer_analysis = df.groupby('Insurer Name').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': ['sum', 'mean'],
    'Status': lambda x: (x == 'Approved').sum()
}).round(2)

insurer_analysis.columns = ['Claims_Count', 'Total_Claimed', 'Avg_Claimed', 
                            'Total_Approved', 'Avg_Approved', 'Approved_Count']
insurer_analysis['Approval_Rate'] = (insurer_analysis['Approved_Count'] / 
                                     insurer_analysis['Claims_Count'] * 100).round(2)
insurer_analysis['Loss_Amount'] = insurer_analysis['Total_Claimed'] - insurer_analysis['Total_Approved']
insurer_analysis['Loss_Rate'] = ((insurer_analysis['Loss_Amount'] / 
                                 insurer_analysis['Total_Claimed']) * 100).round(2)

insurer_analysis = insurer_analysis.sort_values('Loss_Amount', ascending=False)

print("\n🏢 TOP 10 INSURERS BY FINANCIAL LOSS:")
print("-" * 100)

for idx, (insurer, row) in enumerate(insurer_analysis.head(10).iterrows(), 1):
    print(f"\n{idx}. {insurer}")
    print(f"   • Total Claims: {int(row['Claims_Count']):,}")
    print(f"   • Total Claimed: {row['Total_Claimed']:,.2f} SAR")
    print(f"   • Total Approved: {row['Total_Approved']:,.2f} SAR")
    print(f"   • 🚨 AMOUNT LOST: {row['Loss_Amount']:,.2f} SAR ({row['Loss_Rate']:.1f}% loss rate)")
    print(f"   • Approval Rate: {row['Approval_Rate']:.1f}%")
    print(f"   • Avg Claim Value: {row['Avg_Claimed']:,.2f} SAR")

# ==================================================================================
# CRITICAL INSIGHTS #4: HIGH-VALUE CLAIMS ANALYSIS
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #4: HIGH-VALUE CLAIMS ANALYSIS")
print("=" * 100)

# Define high-value threshold
high_value_threshold = df['Net Amount'].quantile(0.90)  # Top 10%
high_value_df = df[df['Net Amount'] >= high_value_threshold]

print(f"\n💎 HIGH-VALUE CLAIMS (Top 10% - Above {high_value_threshold:,.2f} SAR):")
print(f"   • Count: {len(high_value_df):,} claims ({len(high_value_df)/len(df)*100:.1f}%)")
print(f"   • Total Value: {high_value_df['Net Amount'].sum():,.2f} SAR")
print(f"   • Percentage of Total Value: {high_value_df['Net Amount'].sum()/df['Net Amount'].sum()*100:.1f}%")

# High-value claims by status
print("\n📊 High-Value Claims by Status:")
for status in high_value_df['Status'].value_counts().head(5).index:
    status_hv = high_value_df[high_value_df['Status'] == status]
    count = len(status_hv)
    value = status_hv['Net Amount'].sum()
    print(f"   • {status}: {count:,} claims | {value:,.2f} SAR")

# High-value rejections
high_value_rejected = high_value_df[high_value_df['Status'].isin(['Rejected', 'Partial'])]
print(f"\n🚨 HIGH-VALUE REJECTIONS/PARTIAL:")
print(f"   • Count: {len(high_value_rejected):,}")
print(f"   • Total Lost: {(high_value_rejected['Net Amount'].sum() - high_value_rejected['Approved Amount'].sum()):,.2f} SAR")
print(f"   • PRIORITY FOR APPEAL! 💰")

# ==================================================================================
# CRITICAL INSIGHTS #5: TEMPORAL TRENDS
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #5: TEMPORAL TRENDS")
print("=" * 100)

# Daily trends
df['Date'] = df['Submission_Date_Parsed'].dt.date
daily_trends = df.groupby('Date').agg({
    'Net Amount': ['count', 'sum'],
    'Approved Amount': 'sum'
}).round(2)

daily_trends.columns = ['Claim_Count', 'Total_Claimed', 'Total_Approved']
daily_trends['Loss_Amount'] = daily_trends['Total_Claimed'] - daily_trends['Total_Approved']
daily_trends['Loss_Rate'] = ((daily_trends['Loss_Amount'] / daily_trends['Total_Claimed']) * 100).round(2)

print(f"\n📅 DAILY TRENDS:")
print(f"   • Date Range: {df['Date'].min()} to {df['Date'].max()}")
print(f"   • Total Days: {df['Date'].nunique()}")
print(f"   • Avg Claims/Day: {df.groupby('Date').size().mean():.0f}")

print("\n🔝 TOP 5 DAYS BY LOSS AMOUNT:")
top_loss_days = daily_trends.nlargest(5, 'Loss_Amount')
for date, row in top_loss_days.iterrows():
    print(f"   • {date}: {row['Loss_Amount']:,.2f} SAR lost ({row['Claim_Count']:.0f} claims)")

# Day of week analysis
df['DayOfWeek'] = df['Submission_Date_Parsed'].dt.day_name()
dow_analysis = df.groupby('DayOfWeek').agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': 'sum'
}).round(2)

# ==================================================================================
# CRITICAL INSIGHTS #6: CLAIM TYPE ANALYSIS
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #6: CLAIM TYPE ANALYSIS")
print("=" * 100)

claim_type_analysis = df.groupby(['Claim Type', 'Claim Sub Type']).agg({
    'Net Amount': ['count', 'sum', 'mean'],
    'Approved Amount': ['sum', 'mean']
}).round(2)

print("\n📋 CLAIM TYPES BREAKDOWN:")
for claim_type in df['Claim Type'].dropna().unique():
    type_df = df[df['Claim Type'] == claim_type]
    count = len(type_df)
    claimed = type_df['Net Amount'].sum()
    approved = type_df['Approved Amount'].sum()
    loss = claimed - approved
    
    print(f"\n   {claim_type.upper()}:")
    print(f"      • Claims: {count:,} ({count/len(df)*100:.1f}%)")
    print(f"      • Total Value: {claimed:,.2f} SAR")
    print(f"      • Approved: {approved:,.2f} SAR")
    print(f"      • Lost: {loss:,.2f} SAR ({loss/claimed*100:.1f}%)")
    
    # Subtypes
    subtypes = type_df['Claim Sub Type'].value_counts()
    if len(subtypes) > 0:
        print(f"      Subtypes:")
        for subtype, subcount in subtypes.head(3).items():
            print(f"         - {subtype}: {subcount:,} claims")

# ==================================================================================
# CRITICAL INSIGHTS #7: PROBLEM AREAS IDENTIFICATION
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #7: PROBLEM AREAS & ACTION ITEMS")
print("=" * 100)

print("\n🚨 TOP PRIORITY ISSUES:")

# 1. Highest loss insurers
top_loss_insurers = insurer_analysis.head(3)
print("\n1️⃣  TOP 3 INSURERS BY LOSS AMOUNT (Immediate Action Required):")
for idx, (insurer, row) in enumerate(top_loss_insurers.iterrows(), 1):
    print(f"   {idx}. {insurer}: {row['Loss_Amount']:,.2f} SAR lost")
    print(f"      → Action: Urgent meeting to review rejection patterns")

# 2. Complete rejections
rejected_df = df[df['Status'] == 'Rejected']
rejected_value = rejected_df['Net Amount'].sum()
print(f"\n2️⃣  COMPLETE REJECTIONS:")
print(f"   • Count: {len(rejected_df):,} claims")
print(f"   • Total Value: {rejected_value:,.2f} SAR")
print(f"   → Action: Appeal process initiation for eligible claims")

# 3. Partial approvals
partial_df = df[df['Status'] == 'Partial']
partial_claimed = partial_df['Net Amount'].sum()
partial_approved = partial_df['Approved Amount'].sum()
partial_loss = partial_claimed - partial_approved
print(f"\n3️⃣  PARTIAL APPROVALS (Hidden Losses):")
print(f"   • Count: {len(partial_df):,} claims")
print(f"   • Claimed: {partial_claimed:,.2f} SAR")
print(f"   • Approved: {partial_approved:,.2f} SAR")
print(f"   • Lost Amount: {partial_loss:,.2f} SAR")
print(f"   → Action: Review partial rejection reasons and appeal")

# 4. Pending claims
pending_df = df[df['Status'] == 'Pended']
pending_value = pending_df['Net Amount'].sum()
print(f"\n4️⃣  PENDING CLAIMS (At Risk):")
print(f"   • Count: {len(pending_df):,} claims")
print(f"   • Total Value: {pending_value:,.2f} SAR")
print(f"   → Action: Follow-up required to prevent timeout rejections")

# 5. Error status claims
error_df = df[df['Status'] == 'Error']
error_value = error_df['Net Amount'].sum()
print(f"\n5️⃣  ERROR STATUS CLAIMS:")
print(f"   • Count: {len(error_df):,} claims")
print(f"   • Total Value: {error_value:,.2f} SAR")
print(f"   → Action: Technical review and resubmission")

# ==================================================================================
# CRITICAL INSIGHTS #8: RECOVERY OPPORTUNITY ANALYSIS
# ==================================================================================
print("\n" + "=" * 100)
print("📊 CRITICAL INSIGHT #8: RECOVERY OPPORTUNITY ANALYSIS")
print("=" * 100)

# Calculate recoverable amounts
recoverable_statuses = ['Rejected', 'Partial', 'Error']
recoverable_df = df[df['Status'].isin(recoverable_statuses)]
recoverable_claimed = recoverable_df['Net Amount'].sum()
recoverable_approved = recoverable_df['Approved Amount'].sum()
total_recoverable = recoverable_claimed - recoverable_approved

print(f"\n💰 RECOVERY POTENTIAL:")
print(f"   ╔══════════════════════════════════════════════════════════╗")
print(f"   ║ Total Recoverable Amount:    {total_recoverable:>18,.2f} SAR ║")
print(f"   ║ Number of Claims:            {len(recoverable_df):>18,}     ║")
print(f"   ║ Average per Claim:           {total_recoverable/len(recoverable_df):>18,.2f} SAR ║")
print(f"   ╚══════════════════════════════════════════════════════════╝")

# Recovery priority by insurer
print("\n🎯 RECOVERY PRIORITY BY INSURER:")
recovery_by_insurer = recoverable_df.groupby('Insurer Name').agg({
    'Net Amount': ['count', 'sum'],
    'Approved Amount': 'sum'
})
recovery_by_insurer.columns = ['Count', 'Claimed', 'Approved']
recovery_by_insurer['Recoverable'] = recovery_by_insurer['Claimed'] - recovery_by_insurer['Approved']
recovery_by_insurer = recovery_by_insurer.sort_values('Recoverable', ascending=False)

for idx, (insurer, row) in enumerate(recovery_by_insurer.head(5).iterrows(), 1):
    print(f"\n   {idx}. {insurer}")
    print(f"      • Recoverable Amount: {row['Recoverable']:,.2f} SAR")
    print(f"      • Number of Claims: {int(row['Count']):,}")
    print(f"      • Priority Score: {'🔴 CRITICAL' if row['Recoverable'] > 5000000 else '🟡 HIGH'}")

# ==================================================================================
# SAVE COMPREHENSIVE INSIGHTS REPORT
# ==================================================================================
print("\n" + "=" * 100)
print("💾 SAVING COMPREHENSIVE INSIGHTS REPORT")
print("=" * 100)

# Prepare detailed insights report
insights_report = {
    'analysis_date': datetime.now().isoformat(),
    'period': {
        'start_date': str(df['Date'].min()),
        'end_date': str(df['Date'].max()),
        'total_days': int(df['Date'].nunique())
    },
    'financial_overview': {
        'total_claimed': float(total_claimed),
        'total_approved': float(total_approved),
        'total_rejected': float(total_rejected),
        'rejection_rate_pct': float(rejection_rate),
        'avg_claim_value': float(avg_claim),
        'avg_approved_value': float(avg_approved)
    },
    'status_breakdown': {
        status: {
            'count': int(len(df[df['Status'] == status])),
            'percentage': float(len(df[df['Status'] == status]) / len(df) * 100),
            'total_claimed': float(df[df['Status'] == status]['Net Amount'].sum()),
            'total_approved': float(df[df['Status'] == status]['Approved Amount'].sum())
        }
        for status in df['Status'].dropna().unique()
    },
    'top_loss_insurers': [
        {
            'name': insurer,
            'claims_count': int(row['Claims_Count']),
            'total_claimed': float(row['Total_Claimed']),
            'total_approved': float(row['Total_Approved']),
            'loss_amount': float(row['Loss_Amount']),
            'loss_rate_pct': float(row['Loss_Rate']),
            'approval_rate_pct': float(row['Approval_Rate'])
        }
        for insurer, row in insurer_analysis.head(10).iterrows()
    ],
    'recovery_opportunities': {
        'total_recoverable_amount': float(total_recoverable),
        'number_of_claims': int(len(recoverable_df)),
        'avg_per_claim': float(total_recoverable / len(recoverable_df)),
        'by_insurer': [
            {
                'insurer': insurer,
                'recoverable_amount': float(row['Recoverable']),
                'claim_count': int(row['Count'])
            }
            for insurer, row in recovery_by_insurer.head(10).iterrows()
        ]
    },
    'high_value_claims': {
        'threshold': float(high_value_threshold),
        'count': int(len(high_value_df)),
        'total_value': float(high_value_df['Net Amount'].sum()),
        'percentage_of_total': float(high_value_df['Net Amount'].sum() / df['Net Amount'].sum() * 100)
    },
    'critical_issues': {
        'complete_rejections': {
            'count': int(len(rejected_df)),
            'value': float(rejected_value)
        },
        'partial_approvals_loss': {
            'count': int(len(partial_df)),
            'loss_amount': float(partial_loss)
        },
        'pending_at_risk': {
            'count': int(len(pending_df)),
            'value': float(pending_value)
        },
        'error_status': {
            'count': int(len(error_df)),
            'value': float(error_value)
        }
    }
}

# Save the report
with open(f'{base_path}\\deep_insights_report.json', 'w', encoding='utf-8') as f:
    json.dump(insights_report, f, indent=2, ensure_ascii=False)

print(f"\n✅ Insights report saved: deep_insights_report.json")

# Create actionable Excel reports
print(f"\n📊 Creating actionable Excel reports...")

# 1. Top Priority Appeals List
priority_appeals = recoverable_df.nlargest(100, 'Net Amount')[
    ['Bundle ID', 'Transaction Identifier', 'Patient Identifier', 'Insurer Name', 
     'Status', 'Net Amount', 'Approved Amount', 'Submission Date']
].copy()
priority_appeals['Loss_Amount'] = priority_appeals['Net Amount'] - priority_appeals['Approved Amount']
priority_appeals = priority_appeals.sort_values('Loss_Amount', ascending=False)
priority_appeals.to_csv(f'{base_path}\\priority_appeals_list.csv', index=False)
print(f"   ✓ priority_appeals_list.csv (Top 100 claims for appeal)")

# 2. Insurer Performance Report
insurer_analysis.to_csv(f'{base_path}\\insurer_performance_report.csv')
print(f"   ✓ insurer_performance_report.csv")

# 3. Daily Financial Summary
daily_trends.to_csv(f'{base_path}\\daily_financial_summary.csv')
print(f"   ✓ daily_financial_summary.csv")

print("\n" + "=" * 100)
print("✅ DEEP INSIGHTS ANALYSIS COMPLETE!")
print("=" * 100)

print(f"\n📁 Generated Files:")
print(f"   1. deep_insights_report.json - Comprehensive insights in JSON format")
print(f"   2. priority_appeals_list.csv - Top 100 claims requiring immediate appeal")
print(f"   3. insurer_performance_report.csv - Detailed insurer analysis")
print(f"   4. daily_financial_summary.csv - Daily trends and patterns")

print(f"\n🎯 KEY TAKEAWAYS:")
print(f"   • Total Financial Loss: {total_rejected:,.2f} SAR ({rejection_rate:.1f}%)")
print(f"   • Recoverable Amount: {total_recoverable:,.2f} SAR from {len(recoverable_df):,} claims")
print(f"   • High-Value Claims: {len(high_value_df):,} claims worth {high_value_df['Net Amount'].sum():,.2f} SAR")
print(f"   • Critical Insurers: {len(insurer_analysis)} insurers analyzed")
print(f"\n💡 RECOMMENDED ACTIONS:")
print(f"   1. Initiate appeals for top 100 high-value rejections")
print(f"   2. Schedule urgent meetings with top 3 loss-generating insurers")
print(f"   3. Review and resubmit {len(error_df):,} error status claims")
print(f"   4. Follow-up on {len(pending_df):,} pending claims to prevent timeout")
print(f"   5. Analyze partial approval patterns for {len(partial_df):,} claims")

print("\n" + "=" * 100)
