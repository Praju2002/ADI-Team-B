# 🚀 Quick Start Guide

## TL;DR - Get Started in 3 Commands

```bash
# 1. Activate virtual environment
source malawi_analysis_env/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Run the dashboard
./run_streamlit.sh
```

That's it! The dashboard will open at `http://localhost:8501`

---

## 📁 Current Structure

```
ADI-Team-B/
├── Data/
│   └── budget_data.csv           # Your data here
├── Streamlit_Dashboard/
│   ├── app.py                    # Home page
│   └── pages/
│       ├── 1_📈_Detailed_Analysis.py
│       ├── 2_🔬_Hypothesis_Testing.py
│       └── 3_📋_Data_Explorer.py
└── run_streamlit.sh              # Quick launcher
```

---

## 🎯 What You Get

### Multi-Page Dashboard:
1. **Overview** - Home page with key metrics
2. **📈 Detailed Analysis** - Charts and breakdowns
3. **🔬 Hypothesis Testing** - Statistical verification
4. **📋 Data Explorer** - Interactive data exploration

### Features:
- ✅ Filter by year and city
- ✅ Real-time chart updates
- ✅ Download data as CSV
- ✅ Color-coded hypothesis verdicts
- ✅ Interactive visualizations
- ✅ Multi-page navigation

---

## 📊 Expected Results

**Your Hypothesis:** Staff costs consume a huge portion of budget

**Result:** CONFIRMED ✅
- Staff costs: 40.3% of total budget
- Exceeds 40% threshold for "huge portion"

---

## 🔧 Troubleshooting

### "Port already in use"
```bash
streamlit run Streamlit_Dashboard/app.py --server.port 8502
```

### "Module not found"
```bash
source malawi_analysis_env/bin/activate
pip install -r requirements.txt
```

### "No data showing"
- Check that `Data/budget_data.csv` exists
- Verify file name matches exactly
- Check file permissions

---

## 📚 Documentation

- **STREAMLIT_GUIDE.md** - Complete user guide
- **PROJECT_STRUCTURE.md** - Detailed structure
- **README.md** - Project overview
- **Streamlit_Dashboard/README.md** - Dashboard docs

---

## 🎓 Next Steps

1. Run the dashboard: `./run_streamlit.sh`
2. Explore different pages from sidebar
3. Filter data using sidebar controls
4. Check hypothesis results
5. Download filtered data if needed

---

**Ready to explore your budget data!** 📊
