# 🚀 Streamlit Setup & Usage Guide

## ✅ Quick Start

### Method 1: Using the Launcher Script (Easiest)
```bash
./run_streamlit.sh
```

### Method 2: Manual Launch
```bash
# Activate virtual environment
source malawi_analysis_env/bin/activate

# Run Streamlit
streamlit run app.py
```

## 📍 What Happens Next

1. **Streamlit starts automatically**
   - The app launches on `http://localhost:8501`
   - Your browser will open automatically (if configured)
   - If not, copy the URL from the terminal

2. **Access the dashboard**
   - Open your browser
   - Navigate to: `http://localhost:8501`

## 🎨 Dashboard Features

### Interactive Elements:
- **📊 Filter by Year** - Select specific years to analyze
- **🏙️ Filter by City** - Focus on specific cities
- **📈 Real-time Updates** - Charts update as you change filters
- **🎯 Hypothesis Verification** - Color-coded verdict (Red/Orange/Green)

### Dashboard Sections:

1. **Overview Metrics** (Top Row)
   - Total Budget
   - Staff Costs
   - Remaining Budget
   - Hypothesis Verdict

2. **Visualizations**
   - Budget Allocation Pie Chart
   - Yearly Trend Line Chart
   - Category Breakdown Bar Chart
   - Impact Analysis Horizontal Bars

3. **Data Tables**
   - Detailed budget breakdown
   - Percentage calculations
   - Year-by-year comparison

4. **Recommendations**
   - Actionable insights
   - Color-coded warnings
   - Strategic suggestions

## 🛠️ Troubleshooting

### Issue: "Port already in use"
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: "Module not found"
**Solution:**
```bash
source malawi_analysis_env/bin/activate
pip install -r requirements.txt
```

### Issue: "No data showing"
**Solution:**
- Ensure CSV file exists in the directory
- Check file name matches: `all_nationalacc_malawi - all_nationalacc_malawi.csv`

### Issue: Browser doesn't open
**Solution:**
- Check terminal for the URL (usually `http://localhost:8501`)
- Manually copy and paste into browser

### Issue: Virtual environment issues
**Solution:**
```bash
# Delete and recreate
rm -rf malawi_analysis_env
python3 -m venv malawi_analysis_env
source malawi_analysis_env/bin/activate
pip install -r requirements.txt
```

## 🎯 Using the Dashboard

### To Analyze Specific Years:
1. Open sidebar (click ☰ icon top left)
2. Select years from "Select Years" dropdown
3. Charts update automatically

### To Focus on Specific Cities:
1. Open sidebar
2. Select cities from "Select Cities" dropdown
3. View filtered results

### To Understand the Hypothesis:
- **Red Badge** = Hypothesis CONFIRMED (staff costs >40%)
- **Orange Badge** = Hypothesis CONFIRMED (staff costs >40%)
- **Green Badge** = Hypothesis NOT CONFIRMED (staff costs <40%)

### To See Recommendations:
- Scroll down to "Recommendations" section
- Color-coded alerts based on results:
  - 🔴 Red = Critical action needed
  - 🟠 Orange = Monitor closely
  - 🟢 Green = Within acceptable ranges

## 💻 Stopping the Server

Press `Ctrl + C` in the terminal where Streamlit is running

## 🔄 Updating the Dashboard

### To modify the app:
1. Edit `app.py`
2. Save the file
3. Streamlit auto-refreshes (watch the browser)

### Key files:
- `app.py` - Main Streamlit application
- `requirements.txt` - Dependencies
- `run_streamlit.sh` - Launcher script

## 📊 Current Analysis Results

Based on your CSV data:
- **Hypothesis Status:** CONFIRMED ✅
- **Staff Costs:** 40.3% of total budget
- **Total Budget:** $1,286.7B (5 years)
- **Staff Costs:** $518.4B
- **Available for Other:** $768.3B

## 🎓 Tips for Best Results

1. **Start with all data selected** to see overall picture
2. **Filter by specific years** to identify trends
3. **Look at the yearly trend chart** to spot patterns
4. **Check recommendations** for actionable insights
5. **Compare different time periods** to analyze changes

## 🚀 Advanced Usage

### Custom Port:
```bash
streamlit run app.py --server.port 8502
```

### Run in Background:
```bash
nohup streamlit run app.py &
```

### View Logs:
```bash
tail -f nohup.out
```

### Stop Background Process:
```bash
pkill -f streamlit
```

## 📞 Support

If you encounter issues:
1. Check that all files are present
2. Verify CSV file exists
3. Ensure virtual environment is activated
4. Check Python version (3.8+)
5. Review error messages in terminal

---

**Enjoy your interactive budget analysis dashboard!** 🎉

The dashboard provides real-time insights into Malawi's budget allocation and automatically verifies your hypothesis about staff costs consuming a huge portion of the budget.
