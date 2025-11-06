import pandas as pd

df = pd.read_csv('Claim_0555a8fb-8ec7-460f-b92f-06ba0bd3fb2d_part1_2025-04-06_2025-04-27.csv')

print(f"Total claims: {len(df)}")
print(f"\n{'Receiver Name':<60} {'Count':<10}")
print("=" * 75)

receiver_counts = df['Receiver Name'].value_counts()
for receiver, count in receiver_counts.head(20).items():
    print(f"{receiver:<60} {count:<10,}")

print(f"\n\nInsurer names:")
print(df['Insurer Name'].value_counts().head(20))
