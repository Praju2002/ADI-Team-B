"""
Water & Sanitation Dashboard - Home/Summary Page
=================================================
Provides overview of all 15 KPIs across:
- Financial Health & Sustainability (KPIs 1-3)
- Operational Performance (KPIs 4-11)
- Service Coverage & Equity (KPIs 12-15)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.nrw import compute_best_nrw
import warnings

warnings.filterwarnings('ignore')

# ---------------------------#
# Page Setup
# ---------------------------#
st.set_page_config(
    page_title="WASH Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<base href='/' />", unsafe_allow_html=True)

# ---------------------------#
# Modern Pastel Design
# ---------------------------#
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    * { 
        font-family: 'Poppins', 'Inter', -apple-system, sans-serif;
        transition: all 0.2s ease;
    }
    
    .main { 
        padding: 2rem 3rem; 
        background: linear-gradient(135deg, #fdfbfb 0%, #f7f4f9 100%);
        min-height: 100vh;
    }
    
    h1, h2 { 
        font-size: 2.8rem; 
        font-weight: 600; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    h3 { 
        font-size: 0.875rem; 
        font-weight: 600; 
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 2.5rem;
    }
    
    [data-testid="stMetricValue"] { 
        font-size: 2rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] { 
        color: #9ca3af; 
        font-size: 0.75rem; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 0.08em;
    }
    
    [data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(12px);
        padding: 1.8rem; 
        border-radius: 18px; 
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%);
        border-right: 1px solid rgba(167, 139, 250, 0.2);
        
    }
             @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"] { 
             background: linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%);
            border-right: 1px solid rgba(167, 139, 250, 0.3);
        }
        
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 { 
            color: #e0e7ff;
        }
        
        .stSelectbox label, .stRadio label { 
            color: #cbd5e1;
        }
        
        .stSelectbox > div > div { 
            background: #1e293b;
            border: 1px solid #475569;
        }
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 { 
        color: #334155; 
        font-size: 0.75rem; 
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stSelectbox label, .stRadio label { 
        color: #475569; 
        font-weight: 500; 
        font-size: 0.875rem;
    }
    
    .stSelectbox > div > div { 
        background: #ffffff;
        border: 1px solid #cbd5e0; 
        border-radius: 8px;
    }
    
    [data-testid="stPlotlyChart"] { 
        background: #ffffff;
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: none;
    }
    
    hr { 
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    [data-testid="column"] { padding: 0.5rem; }
    
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 1.75rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .kpi-card-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }
    
    .kpi-good { border-left: 4px solid #27ae60; }
    .kpi-warning { border-left: 4px solid #f39c12; }
    .kpi-critical { border-left: 4px solid #e74c3c; }
    
    [data-testid="stTooltipIcon"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        vertical-align: middle !important;
    }
    
    .stTooltipContent {
        max-width: 400px !important;
        min-width: 250px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        padding: 12px !important;
        line-height: 1.5 !important;
    }
    
    .plotly .hoverlayer {
        pointer-events: auto !important;
    }

    .plotly .hoverlayer .hovertext {
        max-width: 300px !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        pointer-events: auto !important;
    }
    
    .plotly .hoverlayer, .plotly .hoverlayer * {
        transition: none !important;
        -webkit-transition: none !important;
    }
    
    [data-testid="stPlotlyChart"] {
        overflow: visible !important;
        position: relative !important;
    }
    
    [data-testid="stPlotlyChart"] > div {
        overflow: visible !important;
    }
    
    .svg-container {
        overflow: visible !important;
    }
    
    .plotly .hoverlayer .legend {
        pointer-events: all !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------#
# Import Data Loader
# ---------------------------#
from utils.data_loader import load_table

# ---------------------------#
# Helper Functions
# ---------------------------#
def safe_div(a, b, default=0):
    """Safe division to handle zero/NaN."""
    try:
        if pd.isna(a) or pd.isna(b) or b == 0:
            return default
        return a / b
    except Exception:
        return default


def get_clean_countries(df, col='country'):
    """Get cleaned list of countries from dataframe."""
    if df.empty or col not in df.columns:
        return ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']
    
    cleaned = []
    for c in df[col].unique():
        try:
            if pd.isna(c):
                continue
        except Exception:
            pass
        s = str(c).strip()
        if s == "" or s.lower() in ("nan", "n/a", "<n/a>", "<na>", "na", "none"):
            continue
        cleaned.append(s)
    
    return sorted(set(cleaned)) if cleaned else ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']


def get_status_color(value, target, higher_is_better=True):
    """Get status color based on value vs target."""
    if higher_is_better:
        if value >= target:
            return "Good", "#27ae60"
        elif value >= target * 0.8:
            return "Moderate", "#f39c12"
        else:
            return "Low", "#e74c3c"
    else:
        if value <= target:
            return "Good", "#27ae60"
        elif value <= target * 1.2:
            return "Moderate", "#f39c12"
        else:
            return "High", "#e74c3c"


# ---------------------------#
# Load Data
# ---------------------------#
st.title("Water & Sanitation Dashboard")
st.caption("Comprehensive KPI Monitoring for WASH Services")

with st.spinner('Loading dashboard data...'):
    billing_df = load_table('billing')
    all_fin_service_df = load_table('all_fin_service')
    all_national_df = load_table('all_national')
    w_service_df = load_table('w_service')
    w_access_df = load_table('w_access')
    s_service_df = load_table('s_service')
    s_access_df = load_table('s_access')
    production_df = load_table('production')

# ---------------------------#
# Sidebar Filters
# ---------------------------#
st.sidebar.header("Filter Options")

all_dfs = [billing_df, all_fin_service_df, w_service_df, w_access_df, s_service_df, s_access_df]
available_countries = []
for df in all_dfs:
    available_countries.extend(get_clean_countries(df))
available_countries = sorted(set(available_countries))

if not available_countries:
    available_countries = ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']

selected_country = st.sidebar.selectbox(
    "Select Country",
    options=available_countries,
    index=0,
    help="Select a country to filter the dashboard"
)

st.sidebar.markdown("---")
date_min, date_max = None, None
for df in all_dfs:
    if not df.empty and 'date' in df.columns:
        try:
            df_min = pd.to_datetime(df['date'], errors='coerce').min()
            df_max = pd.to_datetime(df['date'], errors='coerce').max()
            if pd.notna(df_min) and (date_min is None or df_min < date_min):
                date_min = df_min
            if pd.notna(df_max) and (date_max is None or df_max > date_max):
                date_max = df_max
        except Exception:
            pass

if date_min and date_max:
    st.sidebar.markdown("### Time Period")
    period_option = st.sidebar.radio(
        "Select Period:",
        ["All Time", "Last 12 Months", "Last 6 Months"],
        index=0
    )
    
    if period_option == "Last 12 Months":
        date_range = (date_max - pd.DateOffset(months=12), date_max)
    elif period_option == "Last 6 Months":
        date_range = (date_max - pd.DateOffset(months=6), date_max)
    else:
        date_range = (date_min, date_max)
else:
    date_range = None

# ---------------------------#
# Apply Filters
# ---------------------------#
def apply_filters(df, country, date_range, date_col='date'):
    """Apply country and date filters to dataframe."""
    if df.empty:
        return df
    
    df = df.copy()
    
    if country and 'country' in df.columns:
        df = df[df['country'] == country]
    
    if date_range and len(date_range) == 2 and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df = df[(df[date_col] >= start) & (df[date_col] <= end)]
    
    return df

billing_filtered = apply_filters(billing_df, selected_country, date_range)
fin_service_filtered = apply_filters(all_fin_service_df, selected_country, date_range)
national_filtered = apply_filters(all_national_df, selected_country, None)
w_service_filtered = apply_filters(w_service_df, selected_country, date_range)
w_access_filtered = apply_filters(w_access_df, selected_country, None, date_col='year')
s_service_filtered = apply_filters(s_service_df, selected_country, date_range)
s_access_filtered = apply_filters(s_access_df, selected_country, None, date_col='year')
production_filtered = apply_filters(production_df, selected_country, date_range)

# ---------------------------#
# Calculate All KPIs
# ---------------------------#
kpi_results = {}

# KPI 1: NRW Rate
if not billing_filtered.empty and 'billed' in billing_filtered.columns and 'paid' in billing_filtered.columns:
    total_billed = billing_filtered['billed'].sum()
    total_paid = billing_filtered['paid'].sum()
    kpi_results['nrw_rate'] = safe_div(total_billed - total_paid, total_billed) * 100
    kpi_results['nrw_mode'] = 'financial'
    
    # If billed amounts are zero or invalid, try volumetric NRW using production + w_service
    if total_billed == 0 or pd.isna(kpi_results['nrw_rate']):
        prod_df = load_table('production')
        ws_df = load_table('w_service')
        best = compute_best_nrw(billing_filtered, prod_df, ws_df, selected_country)
        if best.get('mode') == 'volumetric':
            vol_nat = best['national']
            # Use volumetric metrics
            kpi_results['nrw_rate'] = vol_nat['nrw_pct_of_input'].mean()
            kpi_results['nrw_mode'] = 'volumetric'
            kpi_results['vol_nat'] = vol_nat  # Store for later use in trend chart

# KPI 2: SRC Rate
if not fin_service_filtered.empty and 'sewer_revenue' in fin_service_filtered.columns and 'opex' in fin_service_filtered.columns:
    total_sewer_revenue = fin_service_filtered['sewer_revenue'].sum()
    total_opex = fin_service_filtered['opex'].sum()
    kpi_results['src_rate'] = safe_div(total_sewer_revenue, total_opex) * 100

# KPI 3: OSB Rate
if not fin_service_filtered.empty and not national_filtered.empty:
    if 'opex' in fin_service_filtered.columns and 'budget_allocated' in national_filtered.columns:
        fin_opex = pd.to_numeric(fin_service_filtered['opex'], errors='coerce')
        nat_budget = pd.to_numeric(national_filtered['budget_allocated'], errors='coerce')
        
        total_opex = fin_opex.sum()
        total_budget = nat_budget.sum()
        
        if total_budget > 0 and not pd.isna(total_opex) and not pd.isna(total_budget):
            kpi_results['osb_rate'] = safe_div(total_opex, total_budget) * 100

# KPI 4: SUC Rate
if not fin_service_filtered.empty and 'complaints' in fin_service_filtered.columns and 'resolved' in fin_service_filtered.columns:
    total_complaints = fin_service_filtered['complaints'].sum()
    total_resolved = fin_service_filtered['resolved'].sum()
    if total_complaints > 0:
        kpi_results['suc_rate'] = safe_div(total_complaints - total_resolved, total_complaints) * 100

# KPI 5: SBK
if not fin_service_filtered.empty and 'blocks' in fin_service_filtered.columns and 'sewer_length' in fin_service_filtered.columns:
    total_blocks = fin_service_filtered['blocks'].sum()
    avg_length = fin_service_filtered['sewer_length'].mean()
    if avg_length > 0:
        kpi_results['sbk'] = safe_div(total_blocks, avg_length)

# KPI 6: ETP Rate
ecoli_passed = None
ecoli_conducted = None
for col in w_service_filtered.columns:
    if 'passed' in col.lower() and 'ecoli' in col.lower():
        ecoli_passed = col
    if 'conducted' in col.lower() and 'ecoli' in col.lower():
        ecoli_conducted = col

if ecoli_passed and ecoli_conducted:
    total_passed = w_service_filtered[ecoli_passed].sum()
    total_conducted = w_service_filtered[ecoli_conducted].sum()
    if total_conducted > 0:
        kpi_results['etp_rate'] = safe_div(total_passed, total_conducted) * 100

# KPI 7: CTP Rate
chlorine_passed = None
chlorine_conducted = None
for col in w_service_filtered.columns:
    if 'passed' in col.lower() and 'chlorine' in col.lower():
        chlorine_passed = col
    if 'conducted' in col.lower() and 'chlorine' in col.lower():
        chlorine_conducted = col

if chlorine_passed and chlorine_conducted:
    total_passed = w_service_filtered[chlorine_passed].sum()
    total_conducted = w_service_filtered[chlorine_conducted].sum()
    if total_conducted > 0:
        kpi_results['ctp_rate'] = safe_div(total_passed, total_conducted) * 100

# KPI 10: NCW Rate
if not production_filtered.empty and not w_service_filtered.empty:
    prod_col = 'production_m3' if 'production_m3' in production_filtered.columns else 'production' if 'production' in production_filtered.columns else None
    if prod_col and 'total_consumption' in w_service_filtered.columns:
        total_prod = production_filtered[prod_col].sum()
        total_cons = w_service_filtered['total_consumption'].sum()
        if total_prod > 0:
            kpi_results['ncw_rate'] = safe_div(total_prod - total_cons, total_prod) * 100

# KPI 11: NMW Rate
if not w_service_filtered.empty and 'total_consumption' in w_service_filtered.columns and 'metered' in w_service_filtered.columns:
    total_cons = w_service_filtered['total_consumption'].sum()
    total_metered = w_service_filtered['metered'].sum()
    if total_cons > 0:
        kpi_results['nmw_rate'] = safe_div(total_cons - total_metered, total_cons) * 100

# KPI 14: PUW Rate
if not w_access_filtered.empty and all(col in w_access_filtered.columns for col in ['popn_total', 'municipal_coverage', 'households']):
    total_pop = w_access_filtered['popn_total'].sum()
    total_coverage = w_access_filtered['municipal_coverage'].sum()
    total_hh = w_access_filtered['households'].sum()
    if total_hh > 0:
        kpi_results['puw_rate'] = safe_div(total_pop - total_coverage, total_hh) * 100

# KPI 15: HUS Rate
if not s_service_filtered.empty and 'households' in s_service_filtered.columns and 'sewer_connections' in s_service_filtered.columns:
    total_hh = s_service_filtered['households'].sum()
    total_conn = s_service_filtered['sewer_connections'].sum()
    if total_hh > 0:
        kpi_results['hus_rate'] = safe_div(total_hh - total_conn, total_hh) * 100

# ---------------------------#
# Display Dashboard
# ---------------------------#
st.markdown("---")

# Financial Health Section - Card Style
st.markdown('<div class="kpi-card"><div class="kpi-card-title">Financial Health & Sustainability</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if 'nrw_rate' in kpi_results:
        value = kpi_results['nrw_rate']
        nrw_mode = kpi_results.get('nrw_mode', 'financial')
        if nrw_mode == 'volumetric':
            help_text = "**Formula (Volumetric):**\n\nNRW = (system_input - consumption) / system_input × 100\n\n**Aggregation:** Zone × Month\n\n**Note:** Using volumetric calculation due to unavailable billing data\n\n**Files:** production, w_service"
        else:
            help_text = "**Formula:**\n\nTotal_billed = Sum of billed for each zone per month across all days, customers, and sources\n\nTotal_paid = Sum of paid for each zone per month across all days, customers, and sources\n\nNRW Rate = (Total_billed - Total_paid) × 100 / Total_billed\n\n**Aggregation:** Zone × Month\n\n**Tooltip:** NRW Amount = Total_billed - Total_paid\n\n**File:** billing"
        st.metric(
            "1. NRW Rate",
            f"{value:.1f}%",
            help=help_text
        )
    else:
        st.metric("1. NRW Rate", "N/A", help="Data not available")

with col2:
    if 'src_rate' in kpi_results:
        value = kpi_results['src_rate']
        st.metric(
            "2. SRC Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nSRC Rate for each city per month = (sewer_revenue / opex) × 100\n\n**Aggregation:** City × Month\n\n**Tooltip:** SRC Amount = sewer_revenue\n\n**File:** all_fin_service"
        )
    else:
        st.metric("2. SRC Rate", "N/A", help="Data not available")

with col3:
    if 'osb_rate' in kpi_results:
        value = kpi_results['osb_rate']
        st.metric(
            "3. OSB Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nTotal_opex = For all months of every year, sum of opex across each city\n\nBudget_allocated = As provided for every year from all_national\n\nOSB Rate for each city per year = (Total_opex / Budget_allocated) × 100\n\n**Aggregation:** City × Year\n\n**Tooltip:** Total_opex\n\n**Files:** all_fin_service and all_national"
        )
    else:
        st.metric("3. OSB Rate", "N/A", help="Data not available")

# Trend visualization for Financial Health
if 'nrw_rate' in kpi_results:
    st.markdown("##### Trends")
    
    nrw_mode = kpi_results.get('nrw_mode', 'financial')
    
    if nrw_mode == 'volumetric' and 'vol_nat' in kpi_results:
        # Use volumetric data
        monthly = kpi_results['vol_nat'].copy()
        if not monthly.empty:
            monthly = monthly.sort_values('year_month').tail(12)
    elif not billing_filtered.empty:
        # Prepare trend data from billing
        df = billing_filtered.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        df['billed'] = pd.to_numeric(df['billed'], errors='coerce').fillna(0)
        df['paid'] = pd.to_numeric(df['paid'], errors='coerce').fillna(0)
        
        monthly = df.groupby('month').agg({'billed': 'sum', 'paid': 'sum'}).reset_index()
        monthly['nrw_rate'] = monthly.apply(lambda r: safe_div(r['billed'] - r['paid'], r['billed']) * 100, axis=1)
        monthly = monthly.sort_values('month').tail(12)
    else:
        monthly = pd.DataFrame()
    
    if not monthly.empty:
        fig = go.Figure()
        
        if nrw_mode == 'volumetric':
            # Plot volumetric NRW rate
            fig.add_trace(go.Scatter(
                x=monthly['year_month'],
                y=monthly['nrw_pct_of_input'],
                mode='lines+markers',
                name='NRW Rate (%)',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
            ))
        else:
            # Plot financial NRW rate
            fig.add_trace(go.Scatter(
                x=monthly['month'],
                y=monthly['nrw_rate'],
                mode='lines+markers',
                name='NRW Rate',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title='',
            yaxis_title='NRW Rate (%)',
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Operational Performance Section - Card Style
st.markdown('<div class="kpi-card"><div class="kpi-card-title">Operational Performance</div></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'suc_rate' in kpi_results:
        value = kpi_results['suc_rate']
        st.metric(
            "4. SUC Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nUC Rate for each city per month = (complaints - resolved) / complaints × 100\n\n**Aggregation:** City × Month\n\n**Tooltip:** UC = complaints - resolved\n\n**File:** all_fin_service"
        )
    else:
        st.metric("4. SUC Rate", "N/A", help="Data not available")

with col2:
    if 'sbk' in kpi_results:
        value = kpi_results['sbk']
        st.metric(
            "5. SBK",
            f"{value:.2f}",
            help="**Formula:**\n\nSBK for each city per month = blocks / sewer_length\n\n**Aggregation:** City × Month\n\n**Tooltip:** Sewer Blocks = blocks\n\n**File:** all_fin_service"
        )
    else:
        st.metric("5. SBK", "N/A", help="Data not available")

with col3:
    if 'etp_rate' in kpi_results:
        value = kpi_results['etp_rate']
        st.metric(
            "6. ETP Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nE.Coli Tests Passed for each zone per month = (tests_passed_ecoli / test_conducted_ecoli) × 100\n\n**Aggregation:** Zone × Month\n\n**Tooltip:** tests_passed_ecoli\n\n**File:** w_service"
        )
    else:
        st.metric("6. ETP Rate", "N/A", help="Data not available")

with col4:
    if 'ctp_rate' in kpi_results:
        value = kpi_results['ctp_rate']
        st.metric(
            "7. CTP Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nChlorine Tests Passed for each zone per month = (tests_passed_chlorine / tests_conducted_chlorine) × 100\n\n**Aggregation:** Zone × Month\n\n**Tooltip:** tests_passed_chlorine\n\n**File:** w_service"
        )
    else:
        st.metric("7. CTP Rate", "N/A", help="Data not available")

col1, col2 = st.columns(2)

with col1:
    if 'ncw_rate' in kpi_results:
        value = kpi_results['ncw_rate']
        st.metric(
            "10. NCW Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nTotal_production = Sum of all production across all sources on all days of a month\n\nGrand_Total_Consumption = Sum of all total_consumption across all zones in a month\n\nNCW Rate of each country per month = (Total_production - Grand_Total_Consumption) × 100 / Total_production\n\n**Tooltip:** Total_production - Grand_Total_Consumption\n\n**Files:** production and w_service"
        )
    else:
        st.metric("10. NCW Rate", "N/A", help="Data not available")

with col2:
    if 'nmw_rate' in kpi_results:
        value = kpi_results['nmw_rate']
        st.metric(
            "11. NMW Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nNMW Rate for each zone per month = (total_consumption - metered) × 100 / total_consumption\n\n**Aggregation:** Zone × Month\n\n**Tooltip:** total_consumption - metered\n\n**File:** w_service"
        )
    else:
        st.metric("11. NMW Rate", "N/A", help="Data not available")

# Comparison chart for water quality tests
if 'etp_rate' in kpi_results and 'ctp_rate' in kpi_results:
    st.markdown("##### Water Quality Test Performance")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['E.Coli Tests', 'Chlorine Tests'],
        y=[kpi_results.get('etp_rate', 0), kpi_results.get('ctp_rate', 0)],
        marker_color=['#667eea', '#764ba2'],
        text=[f"{kpi_results.get('etp_rate', 0):.1f}%", f"{kpi_results.get('ctp_rate', 0):.1f}%"],
        textposition='outside'
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title='',
        yaxis_title='Pass Rate (%)',
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', range=[0, 100])
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Service Coverage Section - Card Style
st.markdown('<div class="kpi-card"><div class="kpi-card-title">Service Coverage & Equity</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if 'puw_rate' in kpi_results:
        value = kpi_results['puw_rate']
        st.metric(
            "14. PUW Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nPUW Rate for each zone per year = (popn_total - municipal_coverage) / households × 100\n\n**Aggregation:** Zone × Year\n\n**Tooltip:** popn_total - municipal_coverage (unconnected population)\n\n**File:** w_access"
        )
    else:
        st.metric("14. PUW Rate", "N/A", help="Data not available")

with col2:
    if 'hus_rate' in kpi_results:
        value = kpi_results['hus_rate']
        st.metric(
            "15. HUS Rate",
            f"{value:.1f}%",
            help="**Formula:**\n\nHUS Rate for each zone per month = (households - sewer_connections) / households × 100\n\n**Aggregation:** Zone × Month\n\n**Tooltip:** households - sewer_connections (unconnected households)\n\n**File:** s_service"
        )
    else:
        st.metric("15. HUS Rate", "N/A", help="Data not available")

# Coverage comparison chart
if 'puw_rate' in kpi_results and 'hus_rate' in kpi_results:
    st.markdown("##### Service Coverage Gaps")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Water Access Gap', 'Sanitation Access Gap'],
        y=[kpi_results.get('puw_rate', 0), kpi_results.get('hus_rate', 0)],
        marker_color=['#667eea', '#764ba2'],
        text=[f"{kpi_results.get('puw_rate', 0):.1f}%", f"{kpi_results.get('hus_rate', 0):.1f}%"],
        textposition='outside'
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title='',
        yaxis_title='Gap Rate (%)',
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")