# Malawi Budget Analysis - Interactive Dashboard

## 📊 Project Overview

This project provides both **Python analysis scripts** and an **interactive Streamlit dashboard** to analyze Malawi's national accounts budget data and verify the hypothesis:
> **"Budget allocated and staff cost consume a huge fixed portion, reducing funds available for the rest"**

## 🎯 Hypothesis Testing

The analysis determines if staff costs consume a significant portion of the national budget by:
- Analyzing budget data from CSV files
- Calculating staff cost percentages
- Comparing against thresholds (40% = huge, 60% = very huge)
- Providing statistical verification with comprehensive visualizations

## 🚀 Quick Start

### Option 1: Streamlit Dashboard (Recommended - Interactive UI)

```bash
# Simple setup and run
./run_streamlit.sh
```

Or manually:
```bash
# Activate virtual environment
source malawi_analysis_env/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### Option 2: Python Script Analysis

```bash
# Activate virtual environment
source malawi_analysis_env/bin/activate

# Run the analysis
python malawi_csv_analysis.py
```

## 📁 Project Structure

```
ADI-Team-B/
├── Data/
│   └── budget_data.csv                       # Budget data (CSV)
├── Notebooks/                                # Jupyter notebooks
├── Output/                                   # Analysis outputs
├── Streamlit_Dashboard/
│   ├── app.py                                # Main Streamlit app
│   ├── pages/
│   │   ├── 1_📈_Detailed_Analysis.py        # Detailed analysis page
│   │   ├── 2_🔬_Hypothesis_Testing.py        # Hypothesis testing page
│   │   └── 3_📋_Data_Explorer.py            # Data explorer page
│   └── README.md                             # Dashboard documentation
├── requirements.txt                           # Python dependencies
├── run_streamlit.sh                          # Streamlit launcher script
├── .gitignore                                # Git ignore file
├── STREAMLIT_GUIDE.md                        # User guide
└── README.md                                 # This file
```

## 🎨 Streamlit Dashboard Features

### Interactive Elements:
- 📊 **Real-time filtering** by year and city
- 📈 **Dynamic visualizations** that update with filters
- 🎯 **Hypothesis verification** with color-coded verdicts
- 📋 **Detailed data tables** with all budget information
- 💡 **Smart recommendations** based on analysis results

### Dashboard Sections:
1. **Overview Metrics** - Quick summary cards
2. **Budget Allocation** - Pie charts showing staff vs other costs
3. **Yearly Trends** - Line charts tracking staff cost percentage over time
4. **Category Breakdown** - Bar charts for different budget categories
5. **Impact Analysis** - Visual comparison of budget impact
6. **Detailed Data Table** - Complete dataset with calculations
7. **Recommendations** - Actionable insights based on findings
8. **Hypothesis Summary** - Final verdict and evidence

## 🔧 Dependencies

- **streamlit** - Interactive web dashboard
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Plotting and visualization
- **seaborn** - Statistical data visualization
- **openpyxl** - Excel file support

## 📊 Analysis Results

Based on 2020-2024 data from Malawi:
- **Total Budget:** 1,286.7 Billion (5 years)
- **Staff Costs:** 518.4 Billion (40.3%)
- **Remaining Budget:** 768.3 Billion (59.7%)

### Hypothesis Verdict: **CONFIRMED** ✅
Staff costs consume 40.3% of the budget - exceeding the 40% threshold for "huge portion"

## 📈 Key Insights

### Year-by-Year Staff Cost Percentage:
- 2020: 50.0% (Very high)
- 2021: 31.2% (Improved)
- 2022: 28.8% (Best year)
- 2023: 53.7% (Concerning spike)
- 2024: 45.9% (Still high)

### Trends:
- Staff costs fluctuate significantly year-over-year
- 2023 saw a dramatic spike to 53.7%
- Average staff cost: 40.3% of total budget
- Only 59.7% of budget available for other critical areas

## 💡 Recommendations

### For High Staff Cost Situations (>40%):
1. **Monitor staff cost trends closely**
2. **Review budget allocation priorities**
3. **Consider efficiency improvements**
4. **Optimize staffing levels**
5. **Explore cost-saving measures**

### For Critical Situations (>60%):
1. **URGENT: Staff cost optimization required**
2. **Review staffing levels and compensation structures**
3. **Implement staff efficiency improvements**
4. **Reduce staff costs to free up budget for critical services**

## 🛠️ Troubleshooting

### Common Issues

1. **Streamlit not found:**
   ```bash
   pip install streamlit
   ```

2. **Port already in use:**
   ```bash
   streamlit run app.py --server.port 8502
   ```

3. **Import errors:**
   ```bash
   source malawi_analysis_env/bin/activate
   pip install -r requirements.txt
   ```

4. **Permission errors:**
   ```bash
   chmod +x run_streamlit.sh
   ```

## 📋 Usage Examples

### Using the Streamlit Dashboard:

1. **Launch the app:**
   ```bash
   ./run_streamlit.sh
   ```

2. **Filter data:**
   - Select years in the sidebar
   - Choose specific cities
   - Watch visualizations update automatically

3. **Explore insights:**
   - View hypothesis verification
   - Check recommendations
   - Download data tables
   - Analyze trends

### Using Python Scripts:

```bash
# Run comprehensive analysis
python malawi_csv_analysis.py

# This creates: malawi_csv_budget_analysis.png
```

## 🎯 Hypothesis Verification Logic

| Staff Cost % | Verdict | Description |
|---------------|---------|-------------|
| ≥60% | **STRONGLY CONFIRMED** | Very huge portion - staff costs dominate budget |
| ≥40% | **CONFIRMED** | Huge portion - significant staff cost impact |
| <40% | **NOT CONFIRMED** | Staff costs within reasonable limits |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.

---

**Note**: This analysis tool works with CSV budget data. The Streamlit dashboard provides an interactive interface for exploring the data and verifying the hypothesis about staff costs consuming a large portion of the national budget.