import csv
import glob
from collections import OrderedDict

# Get all CSV files
csv_files = glob.glob("*.csv")
print(f"Found {len(csv_files)} CSV files:")
for file in csv_files:
    print(f"  - {file}")

# Collect all unique headers
all_headers = OrderedDict()
file_data = {}

# First pass: collect headers and data
for file in csv_files:
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Add source_file column
        headers.append('source_file')
        
        # Update all_headers
        for header in headers:
            all_headers[header] = None
        
        # Store data
        rows = []
        for row in reader:
            row.append(file)  # Add source file name
            rows.append(row)
        
        file_data[file] = {'headers': headers, 'rows': rows}

# Create final header list
final_headers = list(all_headers.keys())

# Write merged file
output_file = "merged_all_data.csv"
total_rows = 0

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(final_headers)
    
    for file in csv_files:
        headers = file_data[file]['headers']
        rows = file_data[file]['rows']
        
        for row in rows:
            # Create a row with all columns, filling missing ones with empty strings
            full_row = []
            for header in final_headers:
                if header in headers:
                    idx = headers.index(header)
                    if idx < len(row):
                        full_row.append(row[idx])
                    else:
                        full_row.append('')
                else:
                    full_row.append('')
            writer.writerow(full_row)
            total_rows += 1

print(f"\nMerged {len(csv_files)} files into '{output_file}'")
print(f"Total rows: {total_rows}")
print(f"Total columns: {len(final_headers)}")
