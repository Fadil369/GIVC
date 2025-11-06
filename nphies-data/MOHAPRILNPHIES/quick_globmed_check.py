import pandas as pd

df = pd.read_csv('Claim_0555a8fb-8ec7-460f-b92f-06ba0bd3fb2d_part1_2025-04-06_2025-04-27.csv')
globmed = df[df['Receiver Name'].str.contains('GlobMed', case=False, na=False)]

print(f"Total GlobMed claims: {len(globmed)}")
print(f"\nStatus breakdown:")
print(globmed['Status'].value_counts())
print(f"\nTotal billed: SAR {globmed['Net Amount'].sum():,.2f}")
print(f"Total approved: SAR {globmed['Approved Amount'].sum():,.2f}")
