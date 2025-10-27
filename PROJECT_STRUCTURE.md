# 📁 Malawi Budget Analysis - Project Structure

## Directory Layout

```
ADI-Team-B/
│
├── 📂 Data/
│   └── budget_data.csv                        # Budget dataset (CSV format)
│
├── 📂 Notebooks/
│   └── (Jupyter notebooks for data exploration)
│
├── 📂 Output/
│   └── (Analysis output files and visualizations)
│
├── 📂 Streamlit_Dashboard/
│   ├── app.py                                 # Main Streamlit application
│   ├── pages/
│   │   ├── 1_📈_Detailed_Analysis.py        # Detailed Analysis Page
│   │   ├── 2_🔬_Hypothesis_Testing.py        # Hypothesis Testing Page
│   │   └── 3_📋_Data_Explorer.py             # Data Explorer Page
│   └── README.md                              # Dashboard documentation
│
├── 📂 malawi_analysis_env/                   # Python virtual environment
│
├── 📄 .gitignore                              # Git ignore patterns
├── 📄 requirements.txt                        # Python dependencies
├── 📄 run_streamlit.sh                        # Streamlit launcher script
├── 📄 STREAMLIT_GUIDE.md                      # User guide
├── 📄 README.md                               # Project documentation
└── 📄 PROJECT_STRUCTURE.md                    # This file
```

## 🎯 Component Descriptions

### Data/
**Purpose**: Store raw data files
- Contains CSV files with budget data
- Data follows standardized format
- Used by all analysis components

### Notebooks/
**Purpose**: Data exploration and prototyping
- Jupyter notebooks for experimentation
- Data exploration and analysis
- Prototype development

### Output/
**Purpose**: Generated files and results
- Visualizations exported here
- Analysis reports
- Processed datasets

### Streamlit_Dashboard/
**Purpose**: Interactive multi-page web application

#### app.py
- Main entry point
- Home page with overview
- Navigation to sub-pages

#### pages/
**Multi-page structure using Streamlit's pages feature**

1. **1_📈_Detailed_Analysis.py**
   - Category breakdown visualization
   - Budget allocation charts
   - Yearly comparisons
   
2. **2_🔬_Hypothesis_Testing.py**
   - Statistical hypothesis verification
   - Hypothesis gauge charts
   - Trend analysis
   - Recommendations

3. **3_📋_Data_Explorer.py**
   - Interactive data filtering
   - Data download functionality
   - Statistical summaries
   - Data quality metrics

## 🚀 Running the Application

### Quick Start
```bash
./run_streamlit.sh
```

### Manual Start
```bash
cd Streamlit_Dashboard
streamlit run app.py
```

## 📋 Key Files

### .gitignore
- Excludes virtual environment
- Ignores cache files
- Excludes output files
- Python build artifacts

### requirements.txt
Dependencies:
- `streamlit` - Web framework
- `pandas` - Data processing
- `numpy` - Numerical operations
- `matplotlib` - Plotting
- `seaborn` - Statistical viz
- `openpyxl` - Excel support

### run_streamlit.sh
Automated setup script that:
- Creates virtual environment
- Installs dependencies
- Launches Streamlit app

## 🎨 Multi-Page Navigation

### How It Works
1. **Main Page** (`app.py`) loads first
2. **Pages** are automatically detected from `pages/` folder
3. **Navigation** appears in sidebar
4. **Number prefix** determines order (1_, 2_, 3_)
5. **Emoji icons** for visual identification

### Page Routing
- Home: `/` (app.py)
- Detailed Analysis: `/Detailed_Analysis`
- Hypothesis Testing: `/Hypothesis_Testing`
- Data Explorer: `/Data_Explorer`

## 🔧 Configuration

### Streamlit Configuration
Configurable via `.streamlit/config.toml`:
- Theme settings
- Server configuration
- Layout preferences

### Data Configuration
- CSV files in `Data/` directory
- Standard column names expected
- Numeric values for budget calculations

## 📊 Data Flow

```
Data/budget_data.csv
    ↓
Streamlit Dashboard (loads data)
    ↓
User selects filters
    ↓
Data filtering
    ↓
Visualization generation
    ↓
Display on dashboard
```

## 🎯 Best Practices

1. **Data Organization**: Keep data in `Data/` folder
2. **Code Organization**: Separate pages for different views
3. **Naming Convention**: Number prefix for page order
4. **Documentation**: README in each major folder
5. **Git**: Use `.gitignore` for excluded files

## 📈 Future Enhancements

Potential additions:
- Authentication page
- Export functionality
- Real-time data updates
- Additional visualization types
- Comparison views across years
- Predictive analysis

## 🤝 Contributing

When adding new pages:
1. Create file in `Streamlit_Dashboard/pages/`
2. Use number prefix (e.g., `4_Page_Name.py`)
3. Update documentation
4. Test thoroughly
5. Commit with descriptive message

## 📞 Support

For issues or questions:
1. Check STREAMLIT_GUIDE.md
2. Review README.md
3. Inspect error messages
4. Verify data files exist

---

**Last Updated**: October 2024
