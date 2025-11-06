# NPHIES Data Analysis - Quick Start Guide

## 📦 What You Have

You now have **3 powerful analysis tools** in your folder:

### 1. **interactive_analyzer.py** ⭐ RECOMMENDED FOR BEGINNERS
- **Menu-driven interface** - Easy to use!
- No need to edit code
- Search claims by insurer or patient
- View summaries instantly
- Run full analysis with one click

### 2. **nphies_analyzer.py** - Console Analysis
- Detailed text-based analysis
- Comprehensive statistics
- Issue detection
- Recommendations
- Perfect for quick insights

### 3. **advanced_nphies_analyzer.py** - Visualizations
- Beautiful charts and graphs
- Dashboard visualizations
- Excel reports
- Requires: matplotlib, seaborn, openpyxl

---

## 🚀 Getting Started (3 Easy Steps)

### Step 1: Install Python Packages
Open PowerShell in this folder and run:
```powershell
pip install pandas numpy matplotlib seaborn openpyxl
```

Or simply double-click: **`run_analyzer.bat`** and choose option 3

### Step 2: Run Analysis

#### Option A: Interactive Menu (EASIEST) ⭐
```powershell
python interactive_analyzer.py
```

#### Option B: Quick Console Analysis
```powershell
python nphies_analyzer.py
```

#### Option C: Full Analysis with Charts
```powershell
python advanced_nphies_analyzer.py
```

### Step 3: View Results
Check the **`analysis_output`** folder for:
- 📊 Charts and graphs (PNG files)
- 📑 Excel reports
- 📄 Text reports

---

## 💡 Quick Tips

### What Each Script Does:

**Interactive Analyzer** (interactive_analyzer.py)
```
✓ Easy menu navigation
✓ Load data once, run multiple analyses
✓ Search specific insurers or patients
✓ No coding required
✓ Perfect for exploring data
```

**Basic Analyzer** (nphies_analyzer.py)
```
✓ Complete analysis in one run
✓ Detailed console output
✓ Issue detection
✓ Recommendations
✓ Text report export
```

**Advanced Analyzer** (advanced_nphies_analyzer.py)
```
✓ Beautiful visualizations
✓ Multiple chart types
✓ Excel multi-sheet reports
✓ Temporal heatmaps
✓ Professional dashboards
```

---

## 📊 What You'll Discover

### Claims Insights
- ✅ How many claims are approved vs rejected
- 💰 Total revenue submitted and approved
- 📉 Which insurers have high rejection rates
- 📅 Daily and hourly submission patterns
- ⚠️ Claims with errors or issues

### Payment Insights
- 💵 Total payments received
- 🏢 Top paying insurers
- ⚠️ Zero-amount payment bundles
- 📊 Payment trends over time

### Eligibility Insights
- ✓ Success vs error rates
- 👥 Patients with repeated errors
- 🏥 Insurers with most checks
- 🔍 Integration issues

### Pattern Detection
- 🔴 High rejection rates (alerts if >30%)
- ⚠️ Repeated patient errors
- 📧 Excessive communications
- 💔 Revenue leakage points

### Recommendations
- 💡 How to reduce rejections
- 📈 Revenue optimization tips
- 🔧 Process improvements
- 🎯 Focus areas for improvement

---

## 🎯 Common Use Cases

### "I want to see overall performance"
```powershell
python nphies_analyzer.py
```
Look at: Status distribution, financial summary, top insurers

### "Which insurer is rejecting most claims?"
```powershell
python interactive_analyzer.py
```
Choose: Menu option 14 (Search by Insurer)

### "Show me charts and graphs"
```powershell
python advanced_nphies_analyzer.py
```
Open PNG files in `analysis_output` folder

### "I need an Excel report for management"
```powershell
python advanced_nphies_analyzer.py
```
Open: `analysis_output/nphies_detailed_report.xlsx`

### "Find all claims for patient X"
```powershell
python interactive_analyzer.py
```
Choose: Menu option 15 (Search by Patient)

---

## 📁 Output Files Explained

### Text Reports
**`nphies_analysis_report.txt`**
- Summary statistics
- Status distributions
- Key metrics
- Quick reference

**`insights_report.txt`**
- Executive summary
- Issues identified
- Opportunities
- Action items

### Visual Reports
**`claims_dashboard.png`**
- 6-panel overview
- Status, types, insurers
- Financial summary
- Daily trends

**`insurer_analysis.png`**
- Approval rates per insurer
- Rejection rates
- Average amounts
- Performance comparison

**`payment_analysis.png`**
- Payment distributions
- Top payers
- Temporal trends
- Zero vs non-zero

**`temporal_heatmap.png`**
- Submission patterns
- Peak hours/days
- Workload distribution

### Excel Report
**`nphies_detailed_report.xlsx`**
- Sheet 1: Claim Status Summary
- Sheet 2: Insurer Performance
- Sheet 3: Payment Summary
- Sheet 4: Eligibility Status
- Ready for pivot tables and charts

---

## ⚙️ Customization

All scripts can be customized! Edit these sections:

### Change Folder Path
```python
# At bottom of each script, change:
folder_path = r"c:\Your\New\Path"
```

### Filter by Date
```python
# Add after loading data:
df = df[df['Submission Date'] >= '2025-04-01']
df = df[df['Submission Date'] <= '2025-04-30']
```

### Focus on Specific Insurer
```python
# Add filter:
df = df[df['Insurer Name'] == 'GlobeMed Saudi']
```

### Change Alert Thresholds
```python
# In issue detection section:
if rejection_rate > 20:  # Change from 30 to 20
    # More sensitive alerts
```

---

## 🐛 Troubleshooting

### "No module named pandas"
```powershell
# Solution:
pip install pandas numpy matplotlib seaborn openpyxl
```

### "File not found"
- Check CSV files are in the same folder
- Verify file names contain: Claim_, PaymentReconciliation_, etc.

### "Permission denied"
- Close Excel if report file is open
- Run PowerShell as Administrator

### Charts not showing
- Install required packages: `pip install matplotlib seaborn`
- Check `analysis_output` folder for PNG files

### Script runs but no output
- Check console for error messages
- Verify CSV files have data
- Check date format matches script expectations

---

## 📞 Need Help?

### Quick Checks:
1. ✓ Are CSV files in the folder?
2. ✓ Are packages installed? (`pip list` to check)
3. ✓ Is Python 3.7+ installed? (`python --version`)
4. ✓ Any error messages in console?

### Common Fixes:
- **Restart PowerShell** after installing packages
- **Close all Excel files** before running
- **Check file permissions** on folder
- **Run as Administrator** if needed

---

## 🎓 Learning More

### Understand the Metrics:

**Approval Rate** = (Approved Claims / Total Claims) × 100
- Good: >70%
- Warning: 50-70%
- Critical: <50%

**Revenue Loss** = Submitted Amount - Approved Amount
- Track this monthly
- Identify top loss categories
- Appeal high-value rejections

**Rejection Rate** = (Rejected Claims / Total Claims) × 100
- Target: <20%
- Investigate if >30%
- Review submission quality

---

## 🚀 Next Steps

1. **Run your first analysis**
   ```powershell
   python interactive_analyzer.py
   ```

2. **Review the outputs**
   - Check console output
   - Open analysis_output folder
   - Review charts and reports

3. **Identify issues**
   - Note high rejection rates
   - Check insurers with problems
   - Review error patterns

4. **Take action**
   - Follow recommendations
   - Implement fixes
   - Monitor improvements

5. **Run regular analyses**
   - Weekly for operations
   - Monthly for management
   - Quarterly for strategy

---

## ✅ Success Checklist

- [ ] Python and packages installed
- [ ] CSV files in correct folder
- [ ] Ran at least one script
- [ ] Found output files
- [ ] Reviewed key metrics
- [ ] Identified at least one improvement area
- [ ] Shared insights with team

---

## 🎯 Pro Tips

1. **Run analyses regularly** - Track improvements over time
2. **Compare periods** - Month-over-month, quarter-over-quarter
3. **Share visualizations** - Charts are great for presentations
4. **Focus on actionable insights** - Don't just collect data
5. **Automate** - Schedule scripts to run automatically
6. **Customize** - Adapt scripts to your specific needs
7. **Document findings** - Keep track of what you learn

---

**Happy Analyzing! 📊**

For Al-Hayat National Hospital - Unaizah - Al-Qassim
NPHIES Data Analysis Suite v1.0
