import pandas as pd

# Load insights report
xlsx = pd.ExcelFile('output/insights_and_recommendations_20250507_090420.xlsx')
print('Sheets in Insights report:', xlsx.sheet_names)

# Print content of each sheet
for sheet in xlsx.sheet_names:
    print(f'\nSheet: {sheet}')
    df = pd.read_excel('output/insights_and_recommendations_20250507_090420.xlsx', sheet_name=sheet)
    print(df.head(3).to_string())
    print(f'[Total rows: {len(df)}]')
