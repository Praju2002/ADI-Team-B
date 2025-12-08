"""
Sanitation Operations Dashboard
================================
KPIs Implemented:
- Sewer Unresolved Complaints (SUC) Rate: UC = (complaints - resolved) / complaints × 100
- Sewer Blocks per Kilometre (SBK): blocks / sewer_length
- Sewer Revenue Coverage (SRC) Rate: (sewer_revenue / opex) × 100
- Sanitation Staffing per Sewer Connection (SSS) Rate
- Sanitation Access (SA) over time: stacked bar chart with safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct
- Households Unconnected to Sanitation (HUS) Rate: (households - sewer_connections) / households × 100
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plot_utils import set_smart_yaxis
from utils.colors import OKABE_ITO, CB_SEQUENTIAL
import warnings

warnings.filterwarnings('ignore')

# ---------------------------#
# Page Setup
# ---------------------------#
st.set_page_config(
    page_title="Sanitation Operations Dashboard",
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
    
    /* Fix tooltip overflow and positioning */
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
    
    /* Align help icon with title */
    [data-testid="column"]:has([data-testid="stTooltipIcon"]) {
        display: flex !important;
        align-items: flex-start !important;
        padding-top: 0.5rem !important;
    }
    
    [data-testid="column"]:has([data-testid="stTooltipIcon"]) > div {
        margin-top: 0 !important;
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
    
    /* Ensure chart containers don't overflow */
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
    /* Prevent global transition animations from affecting Plotly tooltip positioning */
    .plotly .hoverlayer, .plotly .hoverlayer * {
        transition: none !important;
        -webkit-transition: none !important;
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


# ---------------------------#
# Load Data
# ---------------------------#
st.title("Sanitation Operations")

with st.spinner('Loading sanitation data...'):
    all_fin_service_df = load_table('all_fin_service')
    s_service_df = load_table('s_service')
    s_access_df = load_table('s_access')

# ---------------------------#
# Sidebar Filters
# ---------------------------#
st.sidebar.header("Filter Options")

# Get available countries
available_countries = get_clean_countries(s_service_df)
if not available_countries:
    available_countries = get_clean_countries(all_fin_service_df)

selected_country = st.sidebar.selectbox(
    "Select Country",
    options=available_countries,
    index=0
)

st.sidebar.markdown("---")

# Date filtering
date_min, date_max = None, None
for df in [all_fin_service_df, s_service_df]:
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
        ["All Time", "Last 12 Months", "Last 6 Months", "Custom Range"],
        index=0
    )
    
    if period_option == "Last 12 Months":
        date_range = (date_max - pd.DateOffset(months=12), date_max)
    elif period_option == "Last 6 Months":
        date_range = (date_max - pd.DateOffset(months=6), date_max)
    elif period_option == "Custom Range":
        date_range = st.sidebar.date_input("Select Date Range:", value=(date_min.date(), date_max.date()))
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
    
    # Country filter
    if country and 'country' in df.columns:
        df = df[df['country'] == country]
    
    # Date filter
    if date_range and len(date_range) == 2 and date_col in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df = df[(df[date_col] >= start) & (df[date_col] <= end)]
    
    return df


fin_service_filtered = apply_filters(all_fin_service_df, selected_country, date_range)
s_service_filtered = apply_filters(s_service_df, selected_country, date_range)
s_access_filtered = apply_filters(s_access_df, selected_country, None, date_col='year')



# Track metrics for summary
summary_metrics = {}

# ===========================
# KPI: Sewer Unresolved Complaints (SUC) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Sewer Unresolved Complaints (SUC) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "UC Rate for each city per month = (complaints - resolved) / complaints × 100\n\n"
        "**Aggregation:** City × Month\n\n"
        "**Tooltip:** UC = complaints - resolved\n\n"
        "**File:** all_fin_service")

if not fin_service_filtered.empty and 'complaints' in fin_service_filtered.columns and 'resolved' in fin_service_filtered.columns:
    df_suc = fin_service_filtered.copy()
    if 'date' in df_suc.columns:
        df_suc['date'] = pd.to_datetime(df_suc['date'], errors='coerce')
    else:
        df_suc['date'] = pd.NaT
    
    # Create city column if not exists
    if 'city' not in df_suc.columns:
        df_suc['city'] = df_suc.get('country', 'Unknown')
    
    # Aggregate by city and month
    df_suc['year_month'] = df_suc['date'].dt.to_period('M').astype(str)
    
    suc_agg = df_suc.groupby(['city', 'year_month']).agg({
        'complaints': 'sum',
        'resolved': 'sum'
    }).reset_index()
    
    # Calculate SUC Rate
    suc_agg['unresolved_complaints'] = suc_agg['complaints'] - suc_agg['resolved']
    suc_agg['suc_rate'] = suc_agg.apply(
        lambda row: safe_div(row['unresolved_complaints'], row['complaints']) * 100,
        axis=1
    )
    
    # Filter valid values (keep zeros; drop only missing complaints)
    suc_agg = suc_agg[suc_agg['complaints'].notna()]
    
    if not suc_agg.empty:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        avg_suc = suc_agg['suc_rate'].mean()
        total_unresolved = suc_agg['unresolved_complaints'].sum()
        total_complaints = suc_agg['complaints'].sum()
        
        summary_metrics['avg_suc'] = avg_suc
        
        with col1:
            st.metric(
                "Average UC Rate",
                f"{avg_suc:.1f}%",
                help=f"UC = {total_unresolved:,.0f}"
            )
        
        with col2:
            st.metric(
                "Total Unresolved",
                f"{total_unresolved:,.0f}"
            )
        
        with col3:
            st.metric(
                "Total Complaints",
                f"{total_complaints:,.0f}"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Column + Line Combo Chart
            # Aggregate for single timeline (sum across cities)
            suc_timeline = suc_agg.groupby('year_month').agg({
                'complaints': 'sum',
                'unresolved_complaints': 'sum',
                'suc_rate': 'mean'
            }).reset_index()
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Column: Total complaints (categorical color from Okabe-Ito)
            fig.add_trace(
                go.Bar(
                    x=suc_timeline['year_month'],
                    y=suc_timeline['complaints'],
                    name='Total Complaints',
                    marker_color=OKABE_ITO[1],
                    text=suc_timeline['complaints'],
                    textposition='none',
                    hovertemplate='<b>%{x}</b><br>Total Complaints: %{y:,.0f}<br>Unresolved: %{customdata:,.0f}<extra></extra>',
                    customdata=suc_timeline['unresolved_complaints']
                ),
                secondary_y=False
            )
            
            # Line: UC Rate (Yellow/Light Orange)
            fig.add_trace(
                go.Scatter(
                    x=suc_timeline['year_month'],
                    y=suc_timeline['suc_rate'],
                    name='UC Rate (%)',
                    mode='lines+markers',
                    line=dict(color=OKABE_ITO[0], width=3),
                    marker=dict(size=8, color=OKABE_ITO[0]),
                    hovertemplate='<b>%{x}</b><br>UC Rate: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=True
            )
            
            # Target line
            # target line removed
            
            fig.update_layout(
                title='UC Rate Over Time (Column + Line Combo)',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            fig.update_xaxes(title_text="Period")
            fig.update_yaxes(title_text="Total Complaints", secondary_y=False)
            fig.update_yaxes(title_text="UC Rate (%)", secondary_y=True)
            # Adjust y-axes for better visibility when values have small spans
            try:
                set_smart_yaxis(fig, primary=suc_timeline['complaints'], secondary=suc_timeline['suc_rate'])
            except Exception:
                pass

            try:
                fig.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig, width='stretch', key="suc_rate_trend")
        
        with col2:
            # City comparison
            city_avg = suc_agg.groupby('city')['suc_rate'].mean().reset_index()
            city_avg = city_avg.sort_values('suc_rate', ascending=True)
            
            fig_bar = px.bar(
                city_avg, x='suc_rate', y='city', orientation='h',
                title='Average UC Rate by City',
                color='suc_rate',
                color_continuous_scale=CB_SEQUENTIAL
            )
            # target line removed
            fig_bar.update_layout(
                xaxis_title="UC Rate (%)",
                yaxis_title="City",
                height=400,
                showlegend=False
            )
            try:
                fig_bar.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_bar, width='stretch', key="suc_city_comparison")
        
        with st.expander("Understanding UC Rate"):
            st.markdown("""
            **Sewer Unresolved Complaints (UC) Rate** measures the percentage of customer complaints that remain unresolved.
            
            - **Formula**: `UC Rate = (complaints - resolved) / complaints × 100`
            - **Tooltip**: `UC = complaints - resolved` (absolute number of unresolved complaints)
            - **Source**: all_fin_service
            """)
    else:
        st.warning("No valid SUC data after filtering")
else:
    st.warning("Complaint data not available. Required columns: complaints, resolved")


# ===========================
# KPI: Sewer Blocks per Kilometre (SBK)
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Sewer Blocks per Kilometre (SBK)")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "SBK for each city per month = blocks / sewer_length\n\n"
        "**Aggregation:** City × Month\n\n"
        "**Tooltip:** Sewer Blocks = blocks\n\n"
        "**File:** all_fin_service")

if not fin_service_filtered.empty and 'blocks' in fin_service_filtered.columns and 'sewer_length' in fin_service_filtered.columns:
    df_sbk = fin_service_filtered.copy()
    if 'date' in df_sbk.columns:
        df_sbk['date'] = pd.to_datetime(df_sbk['date'], errors='coerce')
    else:
        df_sbk['date'] = pd.NaT
    
    # Create city column if not exists
    if 'city' not in df_sbk.columns:
        df_sbk['city'] = df_sbk.get('country', 'Unknown')
    
    # Aggregate by city and month
    df_sbk['year_month'] = df_sbk['date'].dt.to_period('M').astype(str)
    
    sbk_agg = df_sbk.groupby(['city', 'year_month']).agg({
        'blocks': 'sum',
        'sewer_length': 'mean'  # Length stays constant, use mean
    }).reset_index()
    
    # Calculate SBK
    sbk_agg['sbk'] = sbk_agg.apply(
        lambda row: safe_div(row['blocks'], row['sewer_length']),
        axis=1
    )
    
    # Filter valid values (keep zero-length rows if present; drop only missing sewer_length)
    sbk_agg = sbk_agg[sbk_agg['sewer_length'].notna()]
    
    if not sbk_agg.empty:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        avg_sbk = sbk_agg['sbk'].mean()
        total_blocks = sbk_agg['blocks'].sum()
        avg_length = sbk_agg['sewer_length'].mean()
        
        summary_metrics['avg_sbk'] = avg_sbk
        
        with col1:
            st.metric(
                "Average SBK",
                f"{avg_sbk:.2f}",
                help=f"blocks = {total_blocks:,.0f}"
            )
        
        with col2:
            st.metric(
                "Total Blocks",
                f"{total_blocks:,.0f}"
            )
        
        with col3:
            st.metric(
                "Avg Sewer Length",
                f"{avg_length:,.1f} km"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Wide line chart with rolling average
            sbk_timeline = sbk_agg.groupby('year_month').agg({
                'sbk': 'mean',
                'blocks': 'sum'
            }).reset_index()
            
            # Calculate rolling average (3-month)
            sbk_timeline['rolling_avg'] = sbk_timeline['sbk'].rolling(window=3, min_periods=1).mean()
            
            fig = go.Figure()
            
            # Line with points: SBK (Blue)
            fig.add_trace(
                go.Scatter(
                    x=sbk_timeline['year_month'],
                    y=sbk_timeline['sbk'],
                    name='SBK',
                    mode='lines+markers',
                    line=dict(color='#2E86AB', width=2),
                    marker=dict(size=8, color='#2E86AB'),
                    hovertemplate='<b>%{x}</b><br>SBK: %{y:.2f}<br>Blocks: %{customdata:,.0f}<extra></extra>',
                    customdata=sbk_timeline['blocks']
                )
            )
            
            # Rolling average line (Light Blue)
            fig.add_trace(
                go.Scatter(
                    x=sbk_timeline['year_month'],
                    y=sbk_timeline['rolling_avg'],
                    name='3-Month Avg',
                    mode='lines',
                    line=dict(color='#A9D6E5', width=3, dash='dash'),
                    hovertemplate='<b>%{x}</b><br>3-Month Avg: %{y:.2f}<extra></extra>'
                )
            )
            
            # Target line
            # target line removed
            
            fig.update_layout(
                title='Sewer Blocks per km (Line + Rolling Average)',
                xaxis_title='Period',
                yaxis_title='Blocks per km',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            
            try:
                set_smart_yaxis(fig, primary=sbk_timeline['sbk'])
            except Exception:
                pass

            try:
                fig.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig, width='stretch', key="sbk_trend")
        
        with col2:
            # City comparison
            city_avg = sbk_agg.groupby('city')['sbk'].mean().reset_index()
            city_avg = city_avg.sort_values('sbk', ascending=True)
            
            fig_bar = px.bar(
                city_avg, x='sbk', y='city', orientation='h',
                title='Average SBK by City',
                color='sbk',
                color_continuous_scale=CB_SEQUENTIAL
            )
            # target line removed
            fig_bar.update_layout(
                xaxis_title="Blocks per km",
                yaxis_title="City",
                height=400,
                showlegend=False
            )
            try:
                fig_bar.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_bar, width='stretch', key="sbk_city_comparison")
        
        with st.expander("Understanding SBK"):
            st.markdown("""
            **Sewer Blocks per Kilometre (SBK)** measures network maintenance efficiency.
            
            - **Formula**: `SBK = blocks / sewer_length`
            - **Tooltip**: `Sewer Blocks = blocks` (absolute number of blockages)
            - **Source**: all_fin_service
            """)
    else:
        st.warning("No valid SBK data after filtering")
else:
    st.warning("Block/sewer length data not available. Required columns: blocks, sewer_length")


# ===========================
# KPI: Sewer Revenue Coverage (SRC) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Sewer Revenue Coverage (SRC) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "SRC Rate for each city per month = (sewer_revenue / opex) × 100\n\n"
        "**Aggregation:** City × Month\n\n"
        "**Tooltip:** SRC Amount = sewer_revenue\n\n"
        "**File:** all_fin_service")

if not fin_service_filtered.empty and 'sewer_revenue' in fin_service_filtered.columns and 'opex' in fin_service_filtered.columns:
    df_src = fin_service_filtered.copy()
    if 'date' in df_src.columns:
        df_src['date'] = pd.to_datetime(df_src['date'], errors='coerce')
    else:
        df_src['date'] = pd.NaT
    
    # Create city column if not exists
    if 'city' not in df_src.columns:
        df_src['city'] = df_src.get('country', 'Unknown')
    
    # Aggregate by city and month
    df_src['year_month'] = df_src['date'].dt.to_period('M').astype(str)
    
    src_agg = df_src.groupby(['city', 'year_month']).agg({
        'sewer_revenue': 'sum',
        'opex': 'sum'
    }).reset_index()
    
    # Calculate SRC Rate
    src_agg['src_rate'] = src_agg.apply(
        lambda row: safe_div(row['sewer_revenue'], row['opex']) * 100,
        axis=1
    )
    
    # Filter valid values (keep zero opex rows; drop only missing values)
    src_agg = src_agg[src_agg['opex'].notna()]
    
    if not src_agg.empty:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        avg_src = src_agg['src_rate'].mean()
        total_revenue = src_agg['sewer_revenue'].sum()
        total_opex = src_agg['opex'].sum()
        
        summary_metrics['avg_src'] = avg_src
        
        with col1:
            st.metric(
                "Average SRC Rate",
                f"{avg_src:.1f}%",
                help=f"sewer_revenue = {total_revenue:,.0f}"
            )
        
        with col2:
            st.metric(
                "Total Sewer Revenue",
                f"{total_revenue:,.0f}"
            )
        
        with col3:
            st.metric(
                "Total OpEx",
                f"{total_opex:,.0f}"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Line chart with area fill
            src_timeline = src_agg.groupby('year_month').agg({
                'sewer_revenue': 'sum',
                'opex': 'sum',
                'src_rate': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            # Line: SRC Rate with area fill (Teal/Green gradient)
            fig.add_trace(
                go.Scatter(
                    x=src_timeline['year_month'],
                    y=src_timeline['src_rate'],
                    name='SRC Rate (%)',
                    mode='lines+markers',
                    line=dict(color='#0D7C66', width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(13, 124, 102, 0.2)',
                    hovertemplate='<b>%{x}</b><br>SRC Rate: %{y:.1f}%<br>Revenue: %{customdata[0]:,.0f}<br>OpEx: %{customdata[1]:,.0f}<extra></extra>',
                    customdata=src_timeline[['sewer_revenue', 'opex']].values
                )
            )
            
            # Target line
            # target line removed
            
            fig.update_layout(
                title='SRC Rate Over Time',
                xaxis_title='Period',
                yaxis_title='SRC Rate (%)',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                showlegend=True,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            
            try:
                set_smart_yaxis(fig, primary=src_timeline['src_rate'])
            except Exception:
                pass

            try:
                fig.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig, width='stretch', key="src_rate_trend")
        
        with col2:
            # City comparison
            city_avg = src_agg.groupby('city')['src_rate'].mean().reset_index()
            city_avg = city_avg.sort_values('src_rate', ascending=False)
            
            fig_bar = px.bar(
                city_avg, x='src_rate', y='city', orientation='h',
                title='Average SRC Rate by City',
                color='src_rate',
                color_continuous_scale=CB_SEQUENTIAL[::-1]
            )
            # target line removed
            fig_bar.update_layout(
                xaxis_title="SRC Rate (%)",
                yaxis_title="City",
                height=400,
                showlegend=False
            )
            try:
                fig_bar.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_bar, width='stretch', key="src_city_comparison")
        
        with st.expander("Understanding SRC Rate"):
            st.markdown("""
            **Sewer Revenue Coverage (SRC) Rate** measures financial sustainability of sewer operations.
            
            - **Formula**: `SRC Rate = (sewer_revenue / opex) × 100`
            - **Tooltip**: `SRC Amount = sewer_revenue` (total sewer revenue)
            - **Source**: all_fin_service
            """)
    else:
        st.warning("No valid SRC data after filtering")
else:
    st.warning("Revenue/opex data not available. Required columns: sewer_revenue, opex")


# ===========================
# REFERENCE: Sanitation Staffing per Sewer Connection (SSS) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Sanitation Staffing per Sewer Connection (SSS) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "city_sewer_connections per month = Sum of sewer_connections across all zones of a city\n\n"
        "SSS Rate for each city per month = (san_staff / city_sewer_connections) × 1000\n\n"
        "**Aggregation:** City × Month\n\n"
        "**Tooltip:** san_staff\n\n"
        "**Files:** s_service and all_fin_service")

if not fin_service_filtered.empty and not s_service_filtered.empty:
    df_fin = fin_service_filtered.copy()
    df_san = s_service_filtered.copy()
    
    if 'date' in df_fin.columns:
        df_fin['date'] = pd.to_datetime(df_fin['date'], errors='coerce')
    else:
        df_fin['date'] = pd.NaT
    if 'date' in df_san.columns:
        df_san['date'] = pd.to_datetime(df_san['date'], errors='coerce')
    else:
        df_san['date'] = pd.NaT
    
    # Create city column - use country for both since we don't have zone-to-city mapping
    # This aggregates all zones within a country
    if 'city' not in df_fin.columns:
        df_fin['city'] = df_fin.get('country', 'Unknown')
    else:
        # If city exists but we need country-level aggregation for matching with s_service
        df_fin['city'] = df_fin.get('country', 'Unknown')
    
    # Extract year_month
    df_fin['year_month'] = df_fin['date'].dt.to_period('M').astype(str)
    df_san['year_month'] = df_san['date'].dt.to_period('M').astype(str)
    
    # Aggregate sewer connections by country (sum across zones) per month
    # Note: Using country as "city" since we don't have zone-to-city mapping
    if 'sewer_connections' in df_san.columns:
        df_san['city'] = df_san.get('country', 'Unknown')
        
        conn_agg = df_san.groupby(['city', 'year_month']).agg({
            'sewer_connections': 'sum'
        }).reset_index()
        conn_agg.rename(columns={'sewer_connections': 'city_sewer_connections'}, inplace=True)
        
        # Get staffing data
        if 'san_staff' in df_fin.columns:
            staff_agg = df_fin.groupby(['city', 'year_month']).agg({
                'san_staff': 'sum'
            }).reset_index()
            
            # Merge
            sss_data = staff_agg.merge(conn_agg, on=['city', 'year_month'], how='inner')
            
            # Calculate SSS Rate (staff per 1000 connections)
            sss_data['sss_rate'] = sss_data.apply(
                lambda row: safe_div(row['san_staff'], row['city_sewer_connections']) * 1000,
                axis=1
            )
            
            # Filter valid (keep zero connections rows; drop only missing values)
            sss_data = sss_data[sss_data['city_sewer_connections'].notna()]
            
            if not sss_data.empty:
                col1, col2, col3 = st.columns(3)
                
                avg_sss = sss_data['sss_rate'].mean()
                total_staff = sss_data['san_staff'].sum()
                total_connections = sss_data['city_sewer_connections'].sum()
                
                summary_metrics['avg_sss'] = avg_sss
                
                with col1:
                    st.metric(
                        "Avg SSS Rate",
                        f"{avg_sss:.2f}",
                        help=f"san_staff = {total_staff:,.0f}"
                    )
                
                with col2:
                    st.metric(
                        "Total San Staff",
                        f"{total_staff:,.0f}"
                    )
                
                with col3:
                    st.metric(
                        "Total Connections",
                        f"{total_connections:,.0f}"
                    )
                
                # Charts
                # City dropdown selector
                cities = sorted(sss_data['city'].unique())
                
                if len(cities) > 1:
                    selected_city_sss = st.selectbox(
                        "Select City/Country for SSS Trend:",
                        options=['All'] + list(cities),
                        key="sss_city_selector"
                    )
                else:
                    selected_city_sss = cities[0] if cities else None
                
                if selected_city_sss and selected_city_sss != 'All':
                    sss_display = sss_data[sss_data['city'] == selected_city_sss]
                else:
                    # Aggregate all cities
                    sss_display = sss_data.groupby('year_month').agg({
                        'san_staff': 'sum',
                        'city_sewer_connections': 'sum',
                        'sss_rate': 'mean'
                    }).reset_index()
                
                # Line chart (Teal)
                fig = go.Figure()
                
                fig.add_trace(
                    go.Scatter(
                        x=sss_display['year_month'],
                        y=sss_display['sss_rate'],
                        name='SSS Rate',
                        mode='lines+markers',
                        line=dict(color='#00BFA5', width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>%{x}</b><br>SSS Rate: %{y:.2f}<br>Staff: %{customdata[0]:,.0f}<br>Connections: %{customdata[1]:,.0f}<extra></extra>',
                        customdata=sss_display[['san_staff', 'city_sewer_connections']].values if 'san_staff' in sss_display.columns else None
                    )
                )
                
                title_text = f'SSS Rate Over Time - {selected_city_sss}' if selected_city_sss != 'All' else 'SSS Rate Over Time - All Cities'
                
                fig.update_layout(
                    title=title_text,
                    xaxis_title='Period',
                    yaxis_title='Staff per 1000 connections',
                    template='plotly_white',
                    hovermode='x unified',
                    height=400,
                    showlegend=False,
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial",
                        align="left"
                    )
                )
                try:
                    set_smart_yaxis(fig, primary=sss_display['sss_rate'])
                except Exception:
                    pass

                try:
                    fig.update_layout(colorway=OKABE_ITO)
                except Exception:
                    pass

                st.plotly_chart(fig, use_container_width=True, key="sss_trend")
                
                # City comparison bar chart
                col1, col2 = st.columns(2)
                
                with col1:
                    city_avg = sss_data.groupby('city')['sss_rate'].mean().reset_index()
                    city_avg = city_avg.sort_values('sss_rate', ascending=True)
                    
                    fig_bar = px.bar(
                        city_avg, x='sss_rate', y='city', orientation='h',
                        title='Average SSS Rate by Country',
                        color='sss_rate',
                        color_continuous_scale=CB_SEQUENTIAL
                    )
                    fig_bar.update_layout(
                        xaxis_title="Staff per 1000 connections",
                        yaxis_title="Country",
                        height=300,
                        showlegend=False
                    )
                    try:
                        fig_bar.update_layout(colorway=OKABE_ITO)
                    except Exception:
                        pass

                    st.plotly_chart(fig_bar, use_container_width=True, key="sss_city_comparison")
                
                with st.expander("Understanding SSS Rate"):
                    st.markdown("""
                    **Sanitation Staffing per Sewer Connection (SSS) Rate** measures staffing adequacy.
                    
                    - **Formula**: `SSS Rate = (san_staff / country_sewer_connections) × 1000`
                    - **san_staff**: Number of sanitation staff (shown in tooltip)
                    - **country_sewer_connections**: Sum of sewer connections across all zones per country per month
                    - **Rate**: Staff per 1000 connections
                    - **Aggregation**: By country per month
                    
                    Note: Aggregated at country level since zone-to-city mapping is not available.
                    """)
            else:
                st.warning("No valid SSS data after merging")
        else:
            st.warning("san_staff column not found")
    else:
        st.warning("sewer_connections column not found in s_service")
else:
    st.warning("Financial or sanitation service data not available for SSS calculation")


# ===========================
# KPI: Sanitation Access (SA) over time
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Sanitation Access (SA) Over Time")
with col_help:
    st.markdown("", help="**Metric:** Sanitation Access (SA) over time (stacked bar chart)\n\n"
        "**Formula:** Direct columns for each zone per year:\n"
        "safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct\n\n"
        "**Aggregation:** Zone × Year\n\n"
        "**Tooltips:** safely_managed, basic, limited, unimproved, open_def (absolute numbers)\n\n"
        "**File:** s_access")

if not s_access_filtered.empty:
    df_access = s_access_filtered.copy()
    
    # Check for required columns
    access_cols = ['safely_managed_pct', 'basic_pct', 'limited_pct', 'unimproved_pct', 'open_def_pct']
    tooltip_cols = ['safely_managed', 'basic', 'limited', 'unimproved', 'open_def']
    
    available_cols = [c for c in access_cols if c in df_access.columns]
    
    if available_cols:
        # Get year column
        year_col = 'year' if 'year' in df_access.columns else 'date_YY' if 'date_YY' in df_access.columns else None
        
        if year_col:
            # Aggregate by zone and year
            zone_col = 'zone' if 'zone' in df_access.columns else 'country'
            
            agg_cols = {c: 'mean' for c in available_cols}
            for tc in tooltip_cols:
                if tc in df_access.columns:
                    agg_cols[tc] = 'sum'
            
            access_agg = df_access.groupby([zone_col, year_col]).agg(agg_cols).reset_index()
            
            # Create 100% stacked bar chart with specified colors
            # Define color mapping for sanitation access levels
            color_map = {
                'Safely Managed': '#2D5F2E',      # Dark Green
                'Basic': '#4A9B4A',                # Medium Green
                'Limited': '#90EE90',              # Light Green
                'Unimproved': '#D2B48C',           # Light Brown
                'Open Def': '#F5DEB3'              # Beige
            }
            
            # Prepare data for stacked bar
            fig = go.Figure()
            
            # Get unique years sorted
            years = sorted(access_agg[year_col].unique())
            
            # Add traces for each access type
            for col in available_cols:
                label = col.replace('_pct', '').replace('_', ' ').title()
                
                # Aggregate across zones for each year
                yearly_avg = access_agg.groupby(year_col)[col].mean().reindex(years)
                
                # Get tooltip data (absolute numbers)
                tooltip_col = tooltip_cols[available_cols.index(col)] if available_cols.index(col) < len(tooltip_cols) else None
                if tooltip_col and tooltip_col in access_agg.columns:
                    yearly_abs = access_agg.groupby(year_col)[tooltip_col].sum().reindex(years)
                    customdata = yearly_abs.values
                    hovertemplate = f'<b>{label}</b><br>Percentage: %{{y:.1f}}%<br>Population: %{{customdata:,.0f}}<extra></extra>'
                else:
                    customdata = None
                    hovertemplate = f'<b>{label}</b><br>Percentage: %{{y:.1f}}%<extra></extra>'
                
                fig.add_trace(
                    go.Bar(
                        x=years,
                        y=yearly_avg.values,
                        name=label,
                        marker_color=color_map.get(label, '#cccccc'),
                        customdata=customdata,
                        hovertemplate=hovertemplate
                    )
                )
            
            fig.update_layout(
                title='Sanitation Access Over Time (100% Stacked Bar)',
                xaxis_title='Year',
                yaxis_title='Percentage (%)',
                barmode='stack',
                template='plotly_white',
                height=500,
                legend_title='Access Level',
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            
            try:
                fig.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig, width='stretch', key="sanitation_access_stacked")
            
            # Zone selector for detail view
            if zone_col in access_agg.columns:
                zones = access_agg[zone_col].unique()
                selected_zone = st.selectbox("Select Zone for Details:", zones, key="zone_selector")
                
                zone_data = access_agg[access_agg[zone_col] == selected_zone]
                
                if not zone_data.empty:
                    # Show latest values
                    latest = zone_data.sort_values(year_col).iloc[-1]
                    
                    cols = st.columns(len(available_cols))
                    for i, col in enumerate(available_cols):
                        with cols[i]:
                            label = col.replace('_pct', '').replace('_', ' ').title()
                            value = latest[col] if col in latest else 0
                            tooltip_col = tooltip_cols[i] if i < len(tooltip_cols) else None
                            tooltip_val = latest.get(tooltip_col, 'N/A') if tooltip_col else 'N/A'
                            st.metric(
                                label,
                                f"{value:.1f}%",
                                help=f"{tooltip_col}: {tooltip_val}" if tooltip_col else None
                            )
            
            with st.expander("Understanding Sanitation Access"):
                st.markdown("""
                **Sanitation Access (SA)** shows the distribution of population across different sanitation service levels.
                
                - **Formula**: Direct columns (no calculation): safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct
                - **Tooltips**: safely_managed, basic, limited, unimproved, open_def (absolute numbers)
                - **Safely Managed**: Using improved facilities with safe disposal/treatment
                - **Basic**: Using improved facilities not shared
                - **Limited**: Using improved facilities shared
                - **Unimproved**: Using unimproved facilities
                - **Open Defecation**: No facilities
                - **Source**: s_access
                """)
        else:
            st.warning("No year column found in s_access data")
    else:
        st.warning("Access percentage columns not found in s_access data")
else:
    st.warning("Sanitation access data not available")


# ===========================
# KPI: Households Unconnected to Sanitation (HUS) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("### Households Unconnected to Sanitation (HUS) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "HUS Rate for each zone per month = (households - sewer_connections) / households × 100\n\n"
        "**Aggregation:** Zone × Month\n\n"
        "**Tooltip:** households - sewer_connections (unconnected households)\n\n"
        "**File:** s_service")

if not s_service_filtered.empty and 'households' in s_service_filtered.columns and 'sewer_connections' in s_service_filtered.columns:
    df_hus = s_service_filtered.copy()
    if 'date' in df_hus.columns:
        df_hus['date'] = pd.to_datetime(df_hus['date'], errors='coerce')
    else:
        df_hus['date'] = pd.NaT
    
    # Get zone column
    zone_col = 'zone' if 'zone' in df_hus.columns else 'country'
    
    # Create year_month
    df_hus['year_month'] = df_hus['date'].dt.to_period('M').astype(str)
    
    # Aggregate by zone and month
    hus_agg = df_hus.groupby([zone_col, 'year_month']).agg({
        'households': 'sum',
        'sewer_connections': 'sum'
    }).reset_index()
    
    # Calculate HUS Rate
    hus_agg['unconnected'] = hus_agg['households'] - hus_agg['sewer_connections']
    hus_agg['hus_rate'] = hus_agg.apply(
        lambda row: safe_div(row['unconnected'], row['households']) * 100,
        axis=1
    )
    
    # Filter valid (keep zero households rows; drop only missing values)
    hus_agg = hus_agg[hus_agg['households'].notna()]
    
    if not hus_agg.empty:
        col1, col2, col3 = st.columns(3)
        
        avg_hus = hus_agg['hus_rate'].mean()
        total_unconnected = hus_agg['unconnected'].sum()
        total_households = hus_agg['households'].sum()
        
        summary_metrics['avg_hus'] = avg_hus
        
        with col1:
            st.metric(
                "Average HUS Rate",
                f"{avg_hus:.1f}%",
                help=f"households - sewer_connections = {total_unconnected:,.0f}"
            )
        
        with col2:
            st.metric(
                "Total Unconnected",
                f"{total_unconnected:,.0f}",
                help="Total households without sewer connection"
            )
        
        with col3:
            st.metric(
                "Total Households",
                f"{total_households:,.0f}",
                help="Total households in service area"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Vertical column chart (Yellow/Orange)
            hus_timeline = hus_agg.groupby('year_month').agg({
                'unconnected': 'sum',
                'households': 'sum',
                'hus_rate': 'mean'
            }).reset_index()
            
            # Determine color based on rate (alert if high)
            colors = ['#FFA500' if rate > 50 else '#FFD700' for rate in hus_timeline['hus_rate']]
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Bar(
                    x=hus_timeline['year_month'],
                    y=hus_timeline['hus_rate'],
                    name='HUS Rate',
                    marker_color=colors,
                    text=hus_timeline['hus_rate'].round(1),
                    textposition='none',
                    hovertemplate='<b>%{x}</b><br>HUS Rate: %{y:.1f}%<br>Unconnected: %{customdata:,.0f}<extra></extra>',
                    customdata=hus_timeline['unconnected']
                )
            )
            
            # Target line
            # target line removed
            
            fig.update_layout(
                title='HUS Rate Over Time (Vertical Column Chart)',
                xaxis_title='Period',
                yaxis_title='HUS Rate (%)',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            try:
                set_smart_yaxis(fig, primary=hus_timeline['hus_rate'])
            except Exception:
                pass

            try:
                fig.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig, width='stretch', key="hus_trend")
        
        with col2:
            zone_avg = hus_agg.groupby(zone_col)['hus_rate'].mean().reset_index()
            zone_avg = zone_avg.sort_values('hus_rate', ascending=False)
            
            # Show horizontal bar chart with dynamic x-axis range and value labels
            fig_bar = px.bar(
                zone_avg, x='hus_rate', y=zone_col, orientation='h',
                title=f'Average HUS Rate by {zone_col.title()}',
                color='hus_rate',
                color_continuous_scale=['green', 'yellow', 'red'],
                text=zone_avg['hus_rate'].round(1)
            )

            # Compute a tight x-axis range around the data so differences in the 90s are visible
            try:
                min_r = float(zone_avg['hus_rate'].min())
                max_r = float(zone_avg['hus_rate'].max())
                span = max_r - min_r
                pad = max(0.5, span * 0.1)  # at least 0.5 percentage points padding
                x0 = max(0, min_r - pad)
                x1 = min(100, max_r + pad)
            except Exception:
                x0, x1 = 0, 100

            # target line removed
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(
                xaxis=dict(title="HUS Rate (%)", range=[x0, x1], tickformat='.1f'),
                yaxis_title=zone_col.title(),
                height=400,
                showlegend=False,
                margin=dict(l=120, r=40, t=60, b=40)
            )
            try:
                fig_bar.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_bar, width='stretch', key="hus_zone_comparison")
        
        with st.expander("Understanding HUS Rate"):
            st.markdown("""
            **Households Unconnected to Sanitation (HUS) Rate** measures sanitation coverage gap.
            
            - **Formula**: `HUS Rate = (households - sewer_connections) / households × 100`
            - **Tooltip**: `households - sewer_connections` (absolute number of unconnected households)
            - **Source**: s_service
            """)
    else:
        st.warning("No valid HUS data after filtering")
else:
    st.warning("Household/connection data not available. Required columns: households, sewer_connections")


# ===========================
# Summary Section
# ===========================
st.markdown("---")
st.markdown("### Sanitation Operations Summary")

summary_data = []

if 'avg_suc' in summary_metrics:
    avg = summary_metrics['avg_suc']
    summary_data.append({
        'KPI': 'Sewer Unresolved Complaints Rate',
        'Value': f"{avg:.1f}%",
        'Status': 'Good' if avg < 10 else 'Moderate' if avg < 20 else 'High'
    })

if 'avg_sbk' in summary_metrics:
    avg = summary_metrics['avg_sbk']
    summary_data.append({
        'KPI': 'Sewer Blocks per km',
        'Value': f"{avg:.2f}",
        'Status': 'Good' if avg < 2 else 'Moderate' if avg < 5 else 'High'
    })

if 'avg_src' in summary_metrics:
    avg = summary_metrics['avg_src']
    summary_data.append({
        'KPI': 'Sewer Revenue Coverage Rate',
        'Value': f"{avg:.1f}%",
        'Status': 'Good' if avg >= 100 else 'Below Target' if avg >= 80 else 'Low'
    })

if 'avg_sss' in summary_metrics:
    avg = summary_metrics['avg_sss']
    summary_data.append({
        'KPI': 'Sanitation Staff per 1000 Connections',
        'Value': f"{avg:.2f}",
        'Status': 'Monitor'
    })

if 'avg_hus' in summary_metrics:
    avg = summary_metrics['avg_hus']
    summary_data.append({
        'KPI': 'Households Unconnected Rate',
        'Value': f"{avg:.1f}%",
        'Status': 'Good' if avg < 50 else 'Moderate' if avg < 70 else 'High'
    })

if summary_data:
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, width='stretch', hide_index=True)
else:
    st.info("No summary data available. Please check data availability.")


st.markdown("---")
st.markdown("""
### Sanitation Operations Dashboard Summary

This dashboard tracks **Operational Performance** for sanitation services through key indicators:

1. **UC Rate**: Unresolved customer complaints rate = (complaints - resolved) / complaints × 100
2. **SBK**: Sewer blocks per kilometer = blocks / sewer_length
3. **SRC Rate**: Sewer revenue coverage = (sewer_revenue / opex) × 100
4. **Sanitation Access**: Population distribution by service level (safely_managed_pct, basic_pct, limited_pct, unimproved_pct, open_def_pct)
5. **HUS Rate**: Households unconnected to sanitation = (households - sewer_connections) / households × 100

**Data Sources**: all_fin_service, s_service, s_access

Use the sidebar filters to explore different countries and time periods.
""")
