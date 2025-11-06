"""Professional NPHIES analysis script.
Generates additional KPI metrics to support issue identification and remediation planning.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)

claims_path = BASE_DIR / "Claim_0555a8fb-8ec7-460f-b92f-06ba0bd3fb2d_part1_2025-04-06_2025-04-27.csv"
payment_path = BASE_DIR / "PaymentReconciliation_da2e2188-9f0d-4d7a-8676-897b8a0177b2_part1_2025-04-01_2025-04-30.csv"
elig_path = BASE_DIR / "EligibilityRequest_0f6b6f4e-5474-453f-85e8-70633eb7e89c_part1_2025-04-01_2025-05-01.csv"

claims = pd.read_csv(claims_path)
payments = pd.read_csv(payment_path)
elig = pd.read_csv(elig_path)

claims['Net Amount'] = pd.to_numeric(claims['Net Amount'], errors='coerce')
claims['Approved Amount'] = pd.to_numeric(claims['Approved Amount'], errors='coerce')
payments['Net Amount'] = pd.to_numeric(payments['Net Amount'], errors='coerce')
payments['Number Of Claims'] = pd.to_numeric(payments['Number Of Claims'], errors='coerce')

summary_lines = []
append = summary_lines.append

append("CLAIMS OVERVIEW")
append("-" * 80)
total_claims = len(claims)
status_counts = claims['Status'].value_counts()
approved = status_counts.get('Approved', 0)
problematic = status_counts.get('Rejected', 0) + status_counts.get('Error', 0) + status_counts.get('Cancelled', 0)
append(f"Total claims: {total_claims:,}")
append(f"Approved claims: {approved:,} ({approved / total_claims * 100:.1f}%)")
append(f"Rejected/Error/Cancelled: {problematic:,} ({problematic / total_claims * 100:.1f}%)")
append("")

append("Top rejection drivers (count)")
rejection_df = claims[claims['Status'].isin(['Rejected', 'Error', 'Cancelled'])]
rej_counts = (rejection_df.groupby(['Insurer Name'])['Bundle ID']
              .count().sort_values(ascending=False).head(5))
for insurer, cnt in rej_counts.items():
    append(f"  {insurer}: {cnt} problem claims")
append("")

append("Financial leakage from partial approvals")
partial_df = claims[claims['Status'] == 'Partial']
partial_gap = (partial_df['Net Amount'] - partial_df['Approved Amount']).sum()
append(f"Partial approvals: {len(partial_df):,} records")
append(f"Shortfall retained by payers: SAR {partial_gap:,.2f}")
append("")

append("High-value rejected/error claims (Net Amount > 10k)")
high_value_df = rejection_df[rejection_df['Net Amount'] > 10000]
high_value_loss = high_value_df['Net Amount'].sum()
append(f"Count: {len(high_value_df):,}")
append(f"Total at risk: SAR {high_value_loss:,.2f}")
append("")

append("PAYMENT RECONCILIATION")
append("-" * 80)
zero_payment = payments[payments['Net Amount'] == 0]
append(f"Payment bundles: {len(payments):,}")
append(f"Zero-value bundles: {len(zero_payment):,} ({len(zero_payment) / len(payments) * 100:.1f}%)")
append(f"Total paid amount: SAR {payments['Net Amount'].sum():,.2f}")
append("")

append("ELIGIBILITY")
append("-" * 80)
elig_error = elig[elig['Status'] == 'Error']
append(f"Eligibility requests: {len(elig):,}")
append(f"Failures: {len(elig_error):,} ({len(elig_error) / len(elig) * 100:.1f}%)")

repeat_error = elig_error['Patient Identifier'].value_counts().head(5)
append("Top patients hitting repeated errors:")
for pid, cnt in repeat_error.items():
    append(f"  Patient {pid}: {cnt} errors")

report_path = OUTPUT_DIR / "professional_summary.txt"
report_path.write_text("\n".join(summary_lines), encoding="utf-8")

print("Professional analysis written to:", report_path)
