# NPHIES Data Analysis Suite

Comprehensive analysis tools for Saudi Arabian Health Insurance (NPHIES) data including Claims, Payments, Eligibility, Prior Authorization, and Communication Requests.

## 📁 Files Included

### 1. **nphies_analyzer.py** - Basic Console Analysis
- Comprehensive text-based analysis
- Detailed statistics and metrics
- Issue detection and recommendations
- Pattern identification
- Export summary reports

### 2. **advanced_nphies_analyzer.py** - Advanced Visualization Suite
- Beautiful charts and graphs
- Insurer performance dashboards
- Temporal heatmaps
- Excel reports with multiple sheets
- Visual insights

## 🚀 Quick Start

### Prerequisites
```powershell
# Install required packages
pip install pandas numpy matplotlib seaborn openpyxl
```

### Running the Analysis

#### Option 1: Basic Console Analysis
```powershell
cd "c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
python nphies_analyzer.py
```

#### Option 2: Advanced Analysis with Visualizations
```powershell
cd "c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
python advanced_nphies_analyzer.py
```

## 📊 What You'll Get

### From Basic Analyzer (`nphies_analyzer.py`)

**Console Output:**
- ✅ Claims status distribution
- 💰 Financial analysis (submitted vs approved)
- 🏥 Insurer performance metrics
- ❌ Rejection and error analysis
- 📅 Temporal trends
- 🔗 Relational deep-dive analysis
- ⚠️ Issue detection
- 💡 Actionable recommendations

**Output Files:**
- `analysis_output/nphies_analysis_report.txt` - Comprehensive text report

### From Advanced Analyzer (`advanced_nphies_analyzer.py`)

**Visualizations:**
1. `claims_dashboard.png` - 6-panel comprehensive claims dashboard
   - Status pie chart
   - Claim type distribution
   - Top insurers
   - Financial overview
   - Encounter class breakdown
   - Daily trend line

2. `insurer_analysis.png` - 4-panel insurer performance
   - Approval rates by insurer
   - Total amounts by insurer
   - Rejection rates
   - Average claim amounts

3. `payment_analysis.png` - 4-panel payment insights
   - Payment distribution histogram
   - Top payers
   - Daily payment trends
   - Zero vs non-zero payments

4. `temporal_heatmap.png` - Submission patterns by day and hour

**Data Reports:**
- `nphies_detailed_report.xlsx` - Excel workbook with multiple sheets:
  - Claim_Status: Status breakdown
  - Insurer_Summary: Detailed insurer metrics
  - Payment_Summary: Payer analysis
  - Eligibility_Status: Eligibility check results

- `insights_report.txt` - Executive summary with:
  - Key metrics
  - Issues identified
  - Opportunities for improvement

## 📈 Analysis Features

### 1. Claims Analysis
- Status distribution (Approved, Rejected, Partial, Error, Cancelled)
- Financial metrics (total submitted, approved, loss amount)
- Approval rates by insurer
- Claim type breakdown (institutional, professional, pharmacy, oral)
- Encounter class analysis (IMP, AMB, etc.)
- Temporal patterns

### 2. Payment Reconciliation
- Total payment amounts
- Zero payment detection
- Payer performance
- Claims per payment bundle
- Daily payment trends

### 3. Eligibility Analysis
- Error rate detection
- Repeated failure patterns
- Patient-level analysis
- Insurer query patterns

### 4. Prior Authorization
- Authorization request volumes
- Claim type distribution
- Insurer patterns
- Temporal trends

### 5. Communication Analysis
- Communication frequency
- Transactions with multiple communications
- Sender patterns
- Excessive communication detection

### 6. Relational Insights
- Claims vs Payments correlation
- Prior Auth vs Claims matching
- Eligibility vs Claims relationships
- Communication patterns

### 7. Issue Detection
- High rejection rates (>30%)
- Excessive zero payments (>20%)
- Eligibility errors (>50%)
- Repeated patient errors
- Excessive communications per transaction

### 8. Recommendations
- Revenue optimization strategies
- Process improvement suggestions
- Technical issue identification
- Best practices

## 🎯 Use Cases

### For Healthcare Administrators
- Monitor overall claim performance
- Identify revenue leakage
- Track insurer relationships
- Optimize submission processes

### For Finance Teams
- Analyze payment patterns
- Calculate revenue losses
- Track approval rates
- Identify collection issues

### For Operations Teams
- Detect system issues
- Monitor eligibility checking
- Optimize workflow
- Reduce rejection rates

### For IT Teams
- Identify integration problems
- Monitor error patterns
- Track communication volumes
- System performance analysis

## 📋 Sample Output

```
CLAIMS ANALYSIS
================================================================================

📊 CLAIM STATUS DISTRIBUTION:
--------------------------------------------------------------------------------
  Approved            :   3245 (45.50%)
  Rejected            :   1823 (25.55%)
  Partial             :    892 (12.50%)
  Cancelled           :    687 ( 9.63%)
  Error               :    485 ( 6.80%)

💰 FINANCIAL ANALYSIS:
--------------------------------------------------------------------------------
  Total Amount Submitted: SAR 12,456,789.50
  Total Amount Approved:  SAR  9,234,567.25
  Approval Rate: 74.13%
  Loss Amount: SAR 3,222,222.25

🏥 TOP INSURERS BY VOLUME:
--------------------------------------------------------------------------------
  GlobeMed Saudi
    Claims: 2345 | Approval Rate: 48.5% | Total: SAR 4,567,890.00
```

## 🔧 Customization

### Modify Analysis Parameters

Edit the scripts to customize:

```python
# Change date formats
df['Submission Date'] = pd.to_datetime(df['Submission Date'], format='%d-%m-%Y %H:%M:%S')

# Filter by date range
df = df[df['Submission Date'] >= '2025-04-01']

# Focus on specific insurers
df = df[df['Insurer Name'].isin(['GlobeMed Saudi', 'Bupa Arabia'])]

# Change thresholds
if rejection_rate > 30:  # Change from 30 to your threshold
    # Alert logic
```

## 🐛 Troubleshooting

### Issue: Module not found
```powershell
# Solution: Install required packages
pip install pandas numpy matplotlib seaborn openpyxl
```

### Issue: File not found
```python
# Solution: Check folder path in script
folder_path = r"c:\Users\rcmrejection3\OneDrive\Desktop\MOHAPRILNPHIES"
```

### Issue: Date parsing errors
```python
# Solution: Check date format in CSV files
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
```

## 📞 Support

For issues or questions:
1. Check the console output for specific error messages
2. Verify CSV file formats match expected structure
3. Ensure all required Python packages are installed
4. Check file paths are correct for your system

## 🔄 Updates

### Version 1.0
- Initial release
- Basic and advanced analyzers
- Comprehensive visualizations
- Excel and text reports

## 📄 License

This tool is provided as-is for healthcare data analysis purposes.

## 🙏 Credits

Built for Al-Hayat National Hospital - Unaizah - Al-Qassim
NPHIES Data Analysis Suite
