# Streamlit Dashboard - Malawi Budget Analysis

## 🚀 Quick Start

From the project root directory:
```bash
./run_streamlit.sh
```

Or manually:
```bash
cd Streamlit_Dashboard
streamlit run app.py
```

## 📁 Structure

```
Streamlit_Dashboard/
├── app.py                              # Main entry point
├── pages/
│   ├── 1_📈_Detailed_Analysis.py      # Detailed analysis page
│   ├── 2_🔬_Hypothesis_Testing.py     # Hypothesis testing page
│   └── 3_📋_Data_Explorer.py          # Data explorer page
└── README.md                           # This file
```

## 📄 Pages Overview

### 1. Home / Overview (app.py)
- Quick dashboard overview
- Key metrics
- Budget allocation pie chart
- Yearly trend visualization

### 2. Detailed Analysis
- **Path**: Streamlit_Dashboard/pages/1_📈_Detailed_Analysis.py
- Category breakdown charts
- Budget by category visualization
- Percentage distribution
- Year-by-year comparison

### 3. Hypothesis Testing
- **Path**: Streamlit_Dashboard/pages/2_🔬_Hypothesis_Testing.py
- Statistical hypothesis verification
- Hypothesis gauge chart
- Trend analysis
- Recommendations

### 4. Data Explorer
- **Path**: Streamlit_Dashboard/pages/3_📋_Data_Explorer.py
- Interactive data filtering
- Data download functionality
- Statistical summaries
- Data quality checks

## 🎯 Features

- **Multi-page navigation** - Easy access to different analysis views
- **Interactive filtering** - Filter by year and city
- **Real-time updates** - Charts update dynamically
- **Data download** - Export filtered data as CSV
- **Color-coded verdicts** - Visual hypothesis verification
- **Responsive design** - Works on different screen sizes

## 💡 Usage Tips

1. **Start at the Home page** to see the overview
2. **Use sidebar filters** to focus on specific data
3. **Navigate between pages** using the sidebar
4. **Download data** from the Data Explorer page
5. **Check recommendations** in Hypothesis Testing page

## 🔧 Technical Details

- **Framework**: Streamlit
- **Data Source**: CSV files in `../Data/`
- **Visualization**: Matplotlib
- **Cache**: Streamlit's `@st.cache_data` for performance
- **Layout**: Wide layout for better charts

## 📊 Data Requirements

The dashboard expects CSV files in the `Data/` directory with the following structure:
- `budget_allocated` - Total budget
- `staff_cost` - Staff costs
- `san_allocation` - SAN allocation
- `wat_allocation` - WAT allocation
- `staff_training_budget` - Training budget
- `date` - Year
- `city` - City name
