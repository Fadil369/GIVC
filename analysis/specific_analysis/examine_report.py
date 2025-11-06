import pandas as pd

# Load Excel report
xlsx = pd.ExcelFile('output/claim_analysis_20250507_090413.xlsx')
print('Sheets in Excel report:', xlsx.sheet_names)

# Print content of each sheet
for sheet in xlsx.sheet_names:
    print(f'\nSheet: {sheet}')
    df = pd.read_excel('output/claim_analysis_20250507_090413.xlsx', sheet_name=sheet)
    print(df.head(3).to_string())
    print(f'[Total rows: {len(df)}]')
