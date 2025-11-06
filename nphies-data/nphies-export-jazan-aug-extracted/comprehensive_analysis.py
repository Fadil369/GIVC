import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Load the merged data
print("=" * 80)
print("COMPREHENSIVE NPHIES DATA ANALYSIS - JAZAN AUGUST")
print("=" * 80)
print("\nLoading data...")

base_path = r"C:\Users\rcmrejection3\OneDrive\Desktop\nphies-export-jazan-aug-extracted\nphies-export-jazan-aug"
df = pd.read_csv(f"{base_path}\\merged_all_data.csv", low_memory=False)

print(f"✓ Loaded {len(df):,} records")
print(f"✓ Columns: {len(df.columns)}")
print(f"✓ Date Range: {df.shape}")

# ============================================================================
# 1. DATA STRUCTURE & QUALITY ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("1. DATA STRUCTURE & QUALITY ANALYSIS")
print("=" * 80)

print("\n📊 Dataset Overview:")
print(f"   • Total Records: {len(df):,}")
print(f"   • Total Columns: {len(df.columns)}")
print(f"   • Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

print("\n📋 Column Information:")
print(df.dtypes.value_counts())

print("\n🔍 Missing Data Analysis:")
missing_data = df.isnull().sum()
missing_pct = (missing_data / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing_Count': missing_data,
    'Missing_Percentage': missing_pct
}).sort_values('Missing_Percentage', ascending=False)
print(missing_df[missing_df['Missing_Count'] > 0].head(20))

# ============================================================================
# 2. RECORD TYPE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("2. RECORD TYPE ANALYSIS")
print("=" * 80)

if 'resourceType' in df.columns:
    resource_counts = df['resourceType'].value_counts()
    print("\n📦 Resource Type Distribution:")
    for resource, count in resource_counts.items():
        pct = (count / len(df) * 100)
        print(f"   • {resource}: {count:,} ({pct:.1f}%)")
else:
    print("⚠ 'resourceType' column not found")

# ============================================================================
# 3. TEMPORAL ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("3. TEMPORAL ANALYSIS")
print("=" * 80)

# Find date columns
date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'created' in col.lower()]
print(f"\n📅 Date Columns Found: {len(date_columns)}")
for col in date_columns[:10]:
    print(f"   • {col}")

# Try to parse common date columns
for date_col in ['created', 'billablePeriod.start', 'created.at', 'date']:
    if date_col in df.columns:
        try:
            df[f'{date_col}_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
            valid_dates = df[f'{date_col}_parsed'].notna().sum()
            if valid_dates > 0:
                print(f"\n✓ Parsed '{date_col}': {valid_dates:,} valid dates")
                print(f"   Range: {df[f'{date_col}_parsed'].min()} to {df[f'{date_col}_parsed'].max()}")
        except:
            pass

# ============================================================================
# 4. CLAIM STATUS ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("4. CLAIM STATUS ANALYSIS")
print("=" * 80)

status_columns = [col for col in df.columns if 'status' in col.lower()]
print(f"\n🔖 Status Columns Found: {len(status_columns)}")

for col in status_columns[:5]:
    if df[col].notna().sum() > 0:
        print(f"\n{col}:")
        status_counts = df[col].value_counts().head(10)
        for status, count in status_counts.items():
            pct = (count / len(df) * 100)
            print(f"   • {status}: {count:,} ({pct:.1f}%)")

# ============================================================================
# 5. FINANCIAL ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("5. FINANCIAL ANALYSIS")
print("=" * 80)

# Find amount/value columns
financial_columns = [col for col in df.columns if 
                    any(term in col.lower() for term in ['amount', 'value', 'total', 'net', 'payment', 'price'])]

print(f"\n💰 Financial Columns Found: {len(financial_columns)}")

for col in financial_columns[:15]:
    if df[col].notna().sum() > 0:
        try:
            # Try to convert to numeric
            numeric_data = pd.to_numeric(df[col], errors='coerce')
            if numeric_data.notna().sum() > 100:  # Only if we have enough valid data
                print(f"\n{col}:")
                print(f"   • Count: {numeric_data.notna().sum():,}")
                print(f"   • Total: {numeric_data.sum():,.2f} SAR")
                print(f"   • Mean: {numeric_data.mean():,.2f} SAR")
                print(f"   • Median: {numeric_data.median():,.2f} SAR")
                print(f"   • Min: {numeric_data.min():,.2f} SAR")
                print(f"   • Max: {numeric_data.max():,.2f} SAR")
        except:
            pass

# ============================================================================
# 6. PAYER/INSURER ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("6. PAYER/INSURER ANALYSIS")
print("=" * 80)

payer_columns = [col for col in df.columns if 
                any(term in col.lower() for term in ['payer', 'insurer', 'insurance', 'organization'])]

print(f"\n🏢 Payer/Insurer Columns Found: {len(payer_columns)}")

for col in payer_columns[:10]:
    if df[col].notna().sum() > 0:
        unique_count = df[col].nunique()
        if unique_count < 50:  # Only show if reasonable number
            print(f"\n{col}: ({unique_count} unique)")
            top_values = df[col].value_counts().head(10)
            for value, count in top_values.items():
                pct = (count / len(df) * 100)
                print(f"   • {value}: {count:,} ({pct:.1f}%)")

# ============================================================================
# 7. DIAGNOSIS & PROCEDURE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("7. DIAGNOSIS & PROCEDURE ANALYSIS")
print("=" * 80)

diagnosis_columns = [col for col in df.columns if 
                    any(term in col.lower() for term in ['diagnosis', 'icd', 'condition'])]
procedure_columns = [col for col in df.columns if 
                    any(term in col.lower() for term in ['procedure', 'service', 'item'])]

print(f"\n🏥 Medical Coding Columns:")
print(f"   • Diagnosis-related: {len(diagnosis_columns)}")
print(f"   • Procedure-related: {len(procedure_columns)}")

# ============================================================================
# 8. ERROR & REJECTION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("8. ERROR & REJECTION ANALYSIS")
print("=" * 80)

error_columns = [col for col in df.columns if 
                any(term in col.lower() for term in ['error', 'reject', 'denied', 'issue', 'outcome'])]

print(f"\n❌ Error/Rejection Columns Found: {len(error_columns)}")

for col in error_columns[:10]:
    if df[col].notna().sum() > 0:
        print(f"\n{col}:")
        top_values = df[col].value_counts().head(10)
        for value, count in top_values.items():
            pct = (count / len(df) * 100)
            print(f"   • {value}: {count:,} ({pct:.1f}%)")

# ============================================================================
# 9. PATTERN DETECTION
# ============================================================================
print("\n" + "=" * 80)
print("9. PATTERN DETECTION & INSIGHTS")
print("=" * 80)

# Detect high-frequency values
print("\n🔍 High-Frequency Patterns:")
for col in df.columns[:30]:  # Check first 30 columns
    if df[col].notna().sum() > 0:
        unique_ratio = df[col].nunique() / len(df)
        if 0.01 < unique_ratio < 0.5:  # Good range for pattern detection
            top_value = df[col].value_counts().iloc[0]
            top_value_pct = (top_value / len(df) * 100)
            if top_value_pct > 10:  # At least 10% frequency
                print(f"   • {col}: '{df[col].value_counts().index[0]}' appears {top_value_pct:.1f}%")

# ============================================================================
# 10. DATA QUALITY ISSUES
# ============================================================================
print("\n" + "=" * 80)
print("10. DATA QUALITY ISSUES")
print("=" * 80)

print("\n⚠ Quality Checks:")

# Check for duplicates
duplicate_count = df.duplicated().sum()
print(f"   • Duplicate Rows: {duplicate_count:,} ({duplicate_count/len(df)*100:.2f}%)")

# Check for empty strings
empty_string_counts = (df == '').sum().sum()
print(f"   • Empty String Values: {empty_string_counts:,}")

# Check for zero values in numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
zero_counts = (df[numeric_cols] == 0).sum().sum()
print(f"   • Zero Values in Numeric Columns: {zero_counts:,}")

# ============================================================================
# 11. COLUMN CATEGORIZATION
# ============================================================================
print("\n" + "=" * 80)
print("11. COLUMN CATEGORIZATION")
print("=" * 80)

categories = {
    'Identification': [col for col in df.columns if any(term in col.lower() for term in ['id', 'identifier', 'reference'])],
    'Financial': financial_columns,
    'Status': status_columns,
    'Temporal': date_columns,
    'Medical': diagnosis_columns + procedure_columns,
    'Organization': payer_columns,
    'Error': error_columns
}

print("\n📂 Column Categories:")
for category, cols in categories.items():
    if cols:
        print(f"   • {category}: {len(cols)} columns")

# ============================================================================
# 12. SAMPLE RECORDS
# ============================================================================
print("\n" + "=" * 80)
print("12. SAMPLE RECORDS")
print("=" * 80)

print("\n📄 First Record Summary:")
first_record = df.iloc[0]
non_null_fields = first_record[first_record.notna()]
print(f"   • Non-null fields: {len(non_null_fields)}/{len(df.columns)}")
print(f"\nSample fields:")
for i, (field, value) in enumerate(non_null_fields.head(15).items()):
    print(f"   • {field}: {str(value)[:100]}")

# ============================================================================
# SAVE DETAILED REPORT
# ============================================================================
print("\n" + "=" * 80)
print("SAVING DETAILED ANALYSIS REPORT")
print("=" * 80)

# Prepare comprehensive report
report = {
    'analysis_date': datetime.now().isoformat(),
    'dataset_info': {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024 / 1024),
        'duplicate_rows': int(duplicate_count)
    },
    'columns': {
        'all_columns': list(df.columns),
        'categorized': {k: v for k, v in categories.items() if v}
    },
    'data_quality': {
        'missing_data': missing_df[missing_df['Missing_Count'] > 0].to_dict(),
        'empty_strings': int(empty_string_counts),
        'zero_values': int(zero_counts)
    }
}

# Save report
with open(f'{base_path}\\comprehensive_analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print(f"\n✓ Detailed report saved: comprehensive_analysis_report.json")

# Export summary CSV
summary_data = []
for col in df.columns:
    summary_data.append({
        'Column': col,
        'Data_Type': str(df[col].dtype),
        'Non_Null_Count': df[col].notna().sum(),
        'Null_Count': df[col].isna().sum(),
        'Null_Percentage': f"{(df[col].isna().sum() / len(df) * 100):.2f}%",
        'Unique_Values': df[col].nunique(),
        'Sample_Value': str(df[col].iloc[0]) if df[col].notna().any() else 'N/A'
    })

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(f'{base_path}\\column_summary.csv', index=False)
print(f"✓ Column summary saved: column_summary.csv")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\nGenerated Files:")
print(f"   1. comprehensive_analysis_report.json")
print(f"   2. column_summary.csv")
print(f"\nNext Steps:")
print(f"   • Review the detailed reports")
print(f"   • Identify specific areas for deeper analysis")
print(f"   • Generate targeted visualizations")
