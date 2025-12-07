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
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .kpi-good { border-left: 4px solid #27ae60; }
    .kpi-warning { border-left: 4px solid #f39c12; }
    .kpi-critical { border-left: 4px solid #e74c3c; }
    
    /* Fix tooltip overflow */
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
    
    /* Fix Plotly chart tooltip overflow */
    /* Allow hover layer events so text and box render together correctly */
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
    
    /* Prevent global transition animations from affecting Plotly tooltip positioning */
    .plotly .hoverlayer, .plotly .hoverlayer * {
        transition: none !important;
        -webkit-transition: none !important;
    }
    /* Ensure chart containers don't overflow */
    [data-testid="stPlotlyChart"] {
        overflow: visible !important;
        position: relative !important;
    }
    
    [data-testid="stPlotlyChart"] > div {
        overflow: visible !important;
    }
    
    /* Fix Plotly tooltip positioning */
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
            return "", "#27ae60"
        elif value >= target * 0.8:
            return "", "#f39c12"
        else:
            return "", "#e74c3c"
    else:
        if value <= target:
            return "", "#27ae60"
        elif value <= target * 1.2:
            return "", "#f39c12"
        else:
            return "", "#e74c3c"


def make_sparkline(x, y, color="#667eea", height=80):
    """Return a tiny Plotly sparkline figure for a 1-row display under a KPI."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(x), y=list(y), mode='lines', line=dict(color=color, width=2), hovertemplate='%{y:.1f}<extra></extra>'))
    fig.update_layout(
        margin=dict(l=2, r=2, t=2, b=2),
        height=height,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def monthly_nrw_series(billing_df, months=12):
    """Return (months, nrw_rate_series) for national NRW based on billing (percentage)."""
    if billing_df is None or billing_df.empty or 'date' not in billing_df.columns:
        return [], []
    df = billing_df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isna().all() or 'billed' not in df.columns or 'paid' not in df.columns:
        return [], []
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['billed'] = pd.to_numeric(df['billed'], errors='coerce').fillna(0)
    df['paid'] = pd.to_numeric(df['paid'], errors='coerce').fillna(0)
    agg = df.groupby('year_month', as_index=False).agg({'billed': 'sum', 'paid': 'sum'})
    agg['nrw_rate'] = agg.apply(lambda r: safe_div(r['billed'] - r['paid'], r['billed']) * 100 if r['billed'] > 0 else float('nan'), axis=1)
    agg = agg.sort_values('year_month').tail(months)
    return agg['year_month'].tolist(), agg['nrw_rate'].fillna(0).tolist()


def monthly_src_series(fin_service_df, months=12):
    """Return (months, src_rate_series) for national SRC using sewer_revenue/opex aggregated monthly."""
    if fin_service_df is None or fin_service_df.empty or 'date' not in fin_service_df.columns:
        return [], []
    df = fin_service_df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isna().all() or 'sewer_revenue' not in df.columns or 'opex' not in df.columns:
        return [], []
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['sewer_revenue'] = pd.to_numeric(df['sewer_revenue'], errors='coerce').fillna(0)
    df['opex'] = pd.to_numeric(df['opex'], errors='coerce').fillna(0)
    agg = df.groupby('year_month', as_index=False).agg({'sewer_revenue': 'sum', 'opex': 'sum'})
    agg['src_rate'] = agg.apply(lambda r: safe_div(r['sewer_revenue'], r['opex']) * 100 if r['opex'] > 0 else float('nan'), axis=1)
    agg = agg.sort_values('year_month').tail(months)
    return agg['year_month'].tolist(), agg['src_rate'].fillna(0).tolist()


def yearly_osb_series(fin_service_df, national_df):
    """Return (years, osb_rate_series) per year using total opex and national budget per year."""
    if (fin_service_df is None or fin_service_df.empty) or (national_df is None or national_df.empty):
        return [], []
    df_fin = fin_service_df.copy()
    if 'date' in df_fin.columns:
        df_fin['date'] = pd.to_datetime(df_fin['date'], errors='coerce')
        df_fin['year'] = df_fin['date'].dt.year
    else:
        df_fin['year'] = None
    if 'opex' not in df_fin.columns:
        return [], []
    df_fin['opex'] = pd.to_numeric(df_fin['opex'], errors='coerce').fillna(0)
    opex_agg = df_fin.groupby('year', as_index=False)['opex'].sum()

    df_nat = national_df.copy()
    if 'date' in df_nat.columns:
        df_nat['date'] = pd.to_datetime(df_nat['date'], errors='coerce')
        df_nat['year'] = df_nat['date'].dt.year
    else:
        df_nat['year'] = df_nat.get('year')
    if 'budget_allocated' not in df_nat.columns:
        return [], []
    df_nat['budget_allocated'] = pd.to_numeric(df_nat['budget_allocated'], errors='coerce').fillna(0)
    budget_agg = df_nat.groupby('year', as_index=False)['budget_allocated'].sum()

    merged = opex_agg.merge(budget_agg, on='year', how='inner').sort_values('year')
    if merged.empty:
        return [], []
    merged['osb_rate'] = merged.apply(lambda r: safe_div(r['opex'], r['budget_allocated']) * 100 if r['budget_allocated'] > 0 else float('nan'), axis=1)
    return merged['year'].astype(str).tolist(), merged['osb_rate'].fillna(0).tolist()


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

# Add cache clear button
if st.sidebar.button("Clear Cache & Reload Data"):
    st.cache_data.clear()
    st.rerun()

# Get available countries
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


# Apply filters to all dataframes
billing_filtered = apply_filters(billing_df, selected_country, date_range)
fin_service_filtered = apply_filters(all_fin_service_df, selected_country, date_range)
# National data has yearly dates - don't filter by monthly date range to avoid losing data
national_filtered = apply_filters(all_national_df, selected_country, None)  # Only filter by country
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

# KPI 2: SRC Rate
if not fin_service_filtered.empty and 'sewer_revenue' in fin_service_filtered.columns and 'opex' in fin_service_filtered.columns:
    total_sewer_revenue = fin_service_filtered['sewer_revenue'].sum()
    total_opex = fin_service_filtered['opex'].sum()
    kpi_results['src_rate'] = safe_div(total_sewer_revenue, total_opex) * 100

# KPI 3: OSB Rate (requires annual data)
if not fin_service_filtered.empty and not national_filtered.empty:
    if 'opex' in fin_service_filtered.columns and 'budget_allocated' in national_filtered.columns:
        # Ensure numeric types
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

# Overview metrics row
st.markdown("### Key Performance Indicators Overview")

# Financial Health Section
st.markdown("#### Financial Health & Sustainability")

col1, col2, col3 = st.columns(3)

with col1:
    if 'nrw_rate' in kpi_results:
        value = kpi_results['nrw_rate']
        status, color = get_status_color(value, 25, higher_is_better=False)
        st.metric(
            "1. NRW Rate",
            f"{value:.1f}%",
            delta=f"Target: <25% {status}",
            delta_color="normal" if value < 25 else "inverse",
            help="**Formula:**\n\n"
                "Total_billed = Sum of billed for each zone per month across all days, customers, and sources\n\n"
                "Total_paid = Sum of paid for each zone per month across all days, customers, and sources\n\n"
                "NRW Rate = (Total_billed - Total_paid) × 100 / Total_billed\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** NRW Amount = Total_billed - Total_paid\n\n"
                "**File:** billing"
        )
    else:
        st.metric("1. NRW Rate", "N/A", help="Data not available")

with col2:
    if 'src_rate' in kpi_results:
        value = kpi_results['src_rate']
        status, color = get_status_color(value, 100, higher_is_better=True)
        st.metric(
            "2. SRC Rate",
            f"{value:.1f}%",
            delta=f"Target: ≥100% {status}",
            delta_color="normal" if value >= 100 else "inverse",
            help="**Formula:**\n\n"
                "SRC Rate for each city per month = (sewer_revenue / opex) × 100\n\n"
                "**Aggregation:** City × Month\n\n"
                "**Tooltip:** SRC Amount = sewer_revenue\n\n"
                "**File:** all_fin_service"
        )
    else:
        st.metric("2. SRC Rate", "N/A", help="Data not available")

with col3:
    if 'osb_rate' in kpi_results:
        value = kpi_results['osb_rate']
        status, color = get_status_color(value, 100, higher_is_better=False)
        st.metric(
            "3. OSB Rate",
            f"{value:.1f}%",
            delta=f"Target: ≤100% {status}",
            delta_color="normal" if value <= 100 else "inverse",
            help="**Formula:**\n\n"
                "Total_opex = For all months of every year, sum of opex across each city\n\n"
                "Budget_allocated = As provided for every year from all_national\n\n"
                "OSB Rate for each city per year = (Total_opex / Budget_allocated) × 100\n\n"
                "**Aggregation:** City × Year\n\n"
                "**Tooltip:** Total_opex\n\n"
                "**Files:** all_fin_service and all_national"
        )
    else:
        st.metric("3. OSB Rate", "N/A", help="Data not available")

st.markdown("---")

# Operational Performance Section
st.markdown("#### Operational Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'suc_rate' in kpi_results:
        value = kpi_results['suc_rate']
        status, color = get_status_color(value, 10, higher_is_better=False)
        st.metric(
            "4. SUC Rate",
            f"{value:.1f}%",
            delta=f"Target: <10% {status}",
            delta_color="normal" if value < 10 else "inverse",
            help="**Formula:**\n\n"
                "UC Rate for each city per month = (complaints - resolved) / complaints × 100\n\n"
                "**Aggregation:** City × Month\n\n"
                "**Tooltip:** UC = complaints - resolved\n\n"
                "**File:** all_fin_service"
        )
    else:
        st.metric("4. SUC Rate", "N/A", 
            help="**Formula:**\n\n"
                "UC Rate for each city per month = (complaints - resolved) / complaints × 100\n\n"
                "**Aggregation:** City × Month\n\n"
                "**Tooltip:** UC = complaints - resolved\n\n"
                "**File:** all_fin_service")

with col2:
    if 'sbk' in kpi_results:
        value = kpi_results['sbk']
        status, color = get_status_color(value, 2, higher_is_better=False)
        st.metric(
            "5. SBK",
            f"{value:.2f}",
            delta=f"Target: <2 {status}",
            delta_color="normal" if value < 2 else "inverse",
            help="**Formula:**\n\n"
                "SBK for each city per month = blocks / sewer_length\n\n"
                "**Aggregation:** City × Month\n\n"
                "**Tooltip:** Sewer Blocks = blocks\n\n"
                "**File:** all_fin_service"
        )
    else:
        st.metric("5. SBK", "N/A",
            help="**Formula:**\n\n"
                "SBK for each city per month = blocks / sewer_length\n\n"
                "**Aggregation:** City × Month\n\n"
                "**Tooltip:** Sewer Blocks = blocks\n\n"
                "**File:** all_fin_service")

with col3:
    if 'etp_rate' in kpi_results:
        value = kpi_results['etp_rate']
        status, color = get_status_color(value, 95, higher_is_better=True)
        st.metric(
            "6. ETP Rate",
            f"{value:.1f}%",
            delta=f"Target: ≥95% {status}",
            delta_color="normal" if value >= 95 else "inverse",
            help="**Formula:**\n\n"
                "E.Coli Tests Passed for each zone per month = (tests_passed_ecoli / test_conducted_ecoli) × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** tests_passed_ecoli\n\n"
                "**File:** w_service"
        )
    else:
        st.metric("6. ETP Rate", "N/A",
            help="**Formula:**\n\n"
                "E.Coli Tests Passed for each zone per month = (tests_passed_ecoli / test_conducted_ecoli) × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** tests_passed_ecoli\n\n"
                "**File:** w_service")

with col4:
    if 'ctp_rate' in kpi_results:
        value = kpi_results['ctp_rate']
        status, color = get_status_color(value, 95, higher_is_better=True)
        st.metric(
            "7. CTP Rate",
            f"{value:.1f}%",
            delta=f"Target: ≥95% {status}",
            delta_color="normal" if value >= 95 else "inverse",
            help="**Formula:**\n\n"
                "Chlorine Tests Passed for each zone per month = (tests_passed_chlorine / tests_conducted_chlorine) × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** tests_passed_chlorine\n\n"
                "**File:** w_service"
        )
    else:
        st.metric("7. CTP Rate", "N/A",
            help="**Formula:**\n\n"
                "Chlorine Tests Passed for each zone per month = (tests_passed_chlorine / tests_conducted_chlorine) × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** tests_passed_chlorine\n\n"
                "**File:** w_service")

col1, col2, col3 = st.columns(3)

with col1:
    if 'ncw_rate' in kpi_results:
        value = kpi_results['ncw_rate']
        status, color = get_status_color(value, 30, higher_is_better=False)
        st.metric(
            "10. NCW Rate",
            f"{value:.1f}%",
            delta=f"Target: <30% {status}",
            delta_color="normal" if value < 30 else "inverse",
            help="**Formula:**\n\n"
                "Total_production = Sum of all production across all sources on all days of a month\n\n"
                "Grand_Total_Consumption = Sum of all total_consumption across all zones in a month\n\n"
                "NCW Rate of each country per month = (Total_production - Grand_Total_Consumption) × 100 / Total_production\n\n"
                "**Tooltip:** Total_production - Grand_Total_Consumption\n\n"
                "**Files:** production and w_service"
        )
    else:
        st.metric("10. NCW Rate", "N/A",
            help="**Formula:**\n\n"
                "Total_production = Sum of all production across all sources on all days of a month\n\n"
                "Grand_Total_Consumption = Sum of all total_consumption across all zones in a month\n\n"
                "NCW Rate of each country per month = (Total_production - Grand_Total_Consumption) × 100 / Total_production\n\n"
                "**Tooltip:** Total_production - Grand_Total_Consumption\n\n"
                "**Files:** production and w_service")

with col2:
    if 'nmw_rate' in kpi_results:
        value = kpi_results['nmw_rate']
        status, color = get_status_color(value, 20, higher_is_better=False)
        st.metric(
            "11. NMW Rate",
            f"{value:.1f}%",
            delta=f"Target: <20% {status}",
            delta_color="normal" if value < 20 else "inverse",
            help="**Formula:**\n\n"
                "NMW Rate for each zone per month = (total_consumption - metered) × 100 / total_consumption\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** total_consumption - metered\n\n"
                "**File:** w_service"
        )
    else:
        st.metric("11. NMW Rate", "N/A",
            help="**Formula:**\n\n"
                "NMW Rate for each zone per month = (total_consumption - metered) × 100 / total_consumption\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** total_consumption - metered\n\n"
                "**File:** w_service")

with col3:
    st.metric("8. WSH Rate", "See Water Page", 
        help="**Formula:**\n\n"
            "Sum the following for all Zones of a city per year: popn_total, households, municipal_coverage (w_access)\n\n"
            "Population per household (PPH) for each city per year = sum(popn_total) / sum(households)\n\n"
            "Municipal_households_covered (MHC) for each city per year = sum(municipal_coverage) / PPH\n\n"
            "WSH Rate for each city per month = (w_staff / MHC of that year) × 1000\n\n"
            "**Aggregation:** City × Month\n\n"
            "**Tooltip:** w_staff\n\n"
            "**Files:** w_access and all_fin_service")
    st.metric("9. SSS Rate", "See Sanitation Page", 
        help="**Formula:**\n\n"
            "city_sewer_connections per month = Sum of sewer_connections across all zones of a city\n\n"
            "SSS Rate for each city per month = (san_staff / city_sewer_connections) × 1000\n\n"
            "**Aggregation:** City × Month\n\n"
            "**Tooltip:** san_staff\n\n"
            "**Files:** s_service and all_fin_service")

st.markdown("---")

# Service Coverage Section
st.markdown("#### Service Coverage & Equity")

col1, col2, col3 = st.columns(3)

with col1:
    if 'puw_rate' in kpi_results:
        value = kpi_results['puw_rate']
        status, color = get_status_color(value, 50, higher_is_better=False)
        st.metric(
            "14. PUW Rate",
            f"{value:.1f}%",
            delta=f"Target: <50% {status}",
            delta_color="normal" if value < 50 else "inverse",
            help="**Formula:**\n\n"
                "PUW Rate for each zone per year = (popn_total - municipal_coverage) / households × 100\n\n"
                "**Aggregation:** Zone × Year\n\n"
                "**Tooltip:** popn_total - municipal_coverage (unconnected population)\n\n"
                "**File:** w_access"
        )
    else:
        st.metric("14. PUW Rate", "N/A",
            help="**Formula:**\n\n"
                "PUW Rate for each zone per year = (popn_total - municipal_coverage) / households × 100\n\n"
                "**Aggregation:** Zone × Year\n\n"
                "**Tooltip:** popn_total - municipal_coverage (unconnected population)\n\n"
                "**File:** w_access")

with col2:
    if 'hus_rate' in kpi_results:
        value = kpi_results['hus_rate']
        status, color = get_status_color(value, 50, higher_is_better=False)
        st.metric(
            "15. HUS Rate",
            f"{value:.1f}%",
            delta=f"Target: <50% {status}",
            delta_color="normal" if value < 50 else "inverse",
            help="**Formula:**\n\n"
                "HUS Rate for each zone per month = (households - sewer_connections) / households × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** households - sewer_connections (unconnected households)\n\n"
                "**File:** s_service"
        )
    else:
        st.metric("15. HUS Rate", "N/A",
            help="**Formula:**\n\n"
                "HUS Rate for each zone per month = (households - sewer_connections) / households × 100\n\n"
                "**Aggregation:** Zone × Month\n\n"
                "**Tooltip:** households - sewer_connections (unconnected households)\n\n"
                "**File:** s_service")

with col3:
    st.metric("12 & 13. Access Charts", "See Detail Pages", 
        help="**KPI 12: Water Access (WA) over time** - Stacked bar chart showing safely_managed_pct, basic_pct, limited_pct, unimproved_pct, surface_water_pct by zone per year (File: w_access)\n\n"
            "**KPI 13: Sanitation Access (SA) over time** - Stacked bar chart showing safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct by zone per year (File: s_access)")

st.markdown("---")

# KPI Summary Table
st.markdown("### KPI Summary Table")

summary_data = [
    {"#": "1", "KPI": "Non-Revenue Water (NRW) Rate", "Formula": "(billed-paid)/billed × 100", "Target": "< 25%", "Value": f"{kpi_results.get('nrw_rate', 'N/A'):.1f}%" if 'nrw_rate' in kpi_results else "N/A", "Category": "Financial"},
    {"#": "2", "KPI": "Sewer Revenue Coverage (SRC) Rate", "Formula": "sewer_revenue/opex × 100", "Target": "≥ 100%", "Value": f"{kpi_results.get('src_rate', 'N/A'):.1f}%" if 'src_rate' in kpi_results else "N/A", "Category": "Financial"},
    {"#": "3", "KPI": "OpEx Share of Budget (OSB) Rate", "Formula": "total_opex/budget_allocated × 100", "Target": "≤ 100%", "Value": f"{kpi_results.get('osb_rate', 'N/A'):.1f}%" if 'osb_rate' in kpi_results else "N/A", "Category": "Financial"},
    {"#": "4", "KPI": "Sewer Unresolved Complaints (SUC) Rate", "Formula": "(complaints-resolved)/complaints × 100", "Target": "< 10%", "Value": f"{kpi_results.get('suc_rate', 'N/A'):.1f}%" if 'suc_rate' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "5", "KPI": "Sewer Blocks per km (SBK)", "Formula": "blocks/sewer_length", "Target": "< 2", "Value": f"{kpi_results.get('sbk', 'N/A'):.2f}" if 'sbk' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "6", "KPI": "E.Coli Tests Passed (ETP) Rate", "Formula": "tests_passed_ecoli/test_conducted_ecoli × 100", "Target": "≥ 95%", "Value": f"{kpi_results.get('etp_rate', 'N/A'):.1f}%" if 'etp_rate' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "7", "KPI": "Chlorine Tests Passed (CTP) Rate", "Formula": "tests_passed_chlorine/tests_conducted_chlorine × 100", "Target": "≥ 95%", "Value": f"{kpi_results.get('ctp_rate', 'N/A'):.1f}%" if 'ctp_rate' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "8", "KPI": "Water Staffing per Household (WSH) Rate", "Formula": "w_staff/MHC × 100", "Target": "Varies", "Value": "See Detail Page", "Category": "Operational"},
    {"#": "9", "KPI": "Sanitation Staffing per Connection (SSS) Rate", "Formula": "san_staff/city_sewer_connections × 100", "Target": "Varies", "Value": "See Detail Page", "Category": "Operational"},
    {"#": "10", "KPI": "Non Consumed Water (NCW) Rate", "Formula": "(production-consumption)/production × 100", "Target": "< 30%", "Value": f"{kpi_results.get('ncw_rate', 'N/A'):.1f}%" if 'ncw_rate' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "11", "KPI": "Non Metered Water (NMW) Rate", "Formula": "(total_consumption-metered)/total_consumption × 100", "Target": "< 20%", "Value": f"{kpi_results.get('nmw_rate', 'N/A'):.1f}%" if 'nmw_rate' in kpi_results else "N/A", "Category": "Operational"},
    {"#": "12", "KPI": "Water Access Over Time", "Formula": "Direct columns (stacked bar)", "Target": "Monitor", "Value": "See Water Page", "Category": "Coverage"},
    {"#": "13", "KPI": "Sanitation Access Over Time", "Formula": "Direct columns (stacked bar)", "Target": "Monitor", "Value": "See Sanitation Page", "Category": "Coverage"},
    {"#": "14", "KPI": "Population Unconnected to Water (PUW) Rate", "Formula": "(popn_total-municipal_coverage)/households × 100", "Target": "< 50%", "Value": f"{kpi_results.get('puw_rate', 'N/A'):.1f}%" if 'puw_rate' in kpi_results else "N/A", "Category": "Coverage"},
    {"#": "15", "KPI": "Households Unconnected to Sanitation (HUS) Rate", "Formula": "(households-sewer_connections)/households × 100", "Target": "< 50%", "Value": f"{kpi_results.get('hus_rate', 'N/A'):.1f}%" if 'hus_rate' in kpi_results else "N/A", "Category": "Coverage"},
]

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, width='stretch', hide_index=True)

st.markdown("---")

# Navigation Guide
st.markdown("### Navigation Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Finance Page**
    - KPI 1: NRW Rate
    - KPI 2: SRC Rate
    - KPI 3: OSB Rate

    Detailed charts, trends, and zone/city breakdowns for financial sustainability metrics.
    """)

with col2:
    st.markdown("""
    **Sanitation Page**
    - KPI 4: SUC Rate
    - KPI 5: SBK
    - KPI 9: SSS Rate
    - KPI 13: Sanitation Access
    - KPI 15: HUS Rate

    Operational performance and service coverage for sanitation.
    """)

with col3:
    st.markdown("""
    **Water Page**
    - KPI 6: ETP Rate
    - KPI 7: CTP Rate
    - KPI 8: WSH Rate
    - KPI 10: NCW Rate
    - KPI 11: NMW Rate
    - KPI 12: Water Access
    - KPI 14: PUW Rate

    Water quality, efficiency, and coverage metrics.
    """)

st.markdown("---")

# Data Source Reference
with st.expander("📁 Data Sources Reference"):
    st.markdown("""
    | File | Granularity | Key Columns |
    |------|-------------|-------------|
    | **billing** | Zone, Customer, Day | billed, paid, consumption_m3 |
    | **all_fin_service** | City, Month | sewer_revenue, opex, complaints, resolved, blocks, sewer_length, san_staff, w_staff |
    | **all_national** | City, Year | budget_allocated |
    | **production** | Source, Day | production_m3, service_hours |
    | **w_service** | Zone, Month | total_consumption, metered, tests_passed_ecoli, test_conducted_ecoli, tests_passed_chlorine, tests_conducted_chlorine |
    | **w_access** | Zone, Year | safely_managed_pct, basic_pct, limited_pct, unimproved_pct, surface_water_pct, popn_total, households, municipal_coverage |
    | **s_service** | Zone, Month | households, sewer_connections |
    | **s_access** | Zone, Year | safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct |
    """)

st.markdown("---")
st.caption("Water & Sanitation Dashboard | Data Analytics for Infrastructure Development")
