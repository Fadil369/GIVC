import pandas as pd
import glob

# Get all CSV files
csv_files = glob.glob("*.csv")
print(f"Found {len(csv_files)} CSV files:")
for file in csv_files:
    print(f"  - {file}")

# Read and combine all CSV files
all_dataframes = []
for file in csv_files:
    df = pd.read_csv(file)
    df['source_file'] = file  # Add source file column
    all_dataframes.append(df)

# Concatenate all dataframes
merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)

# Save to new file
output_file = "merged_all_data.csv"
merged_df.to_csv(output_file, index=False)

print(f"\nMerged {len(all_dataframes)} files into '{output_file}'")
print(f"Total rows: {len(merged_df)}")
print(f"Total columns: {len(merged_df.columns)}")
