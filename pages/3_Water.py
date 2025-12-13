"""
Water Operations Dashboard
===========================
KPIs Implemented:
1. Non-Revenue Water (NRW) Rate - by country per month
2. E.Coli Tests Passed (ETP) Rate - by zone per month
3. Chlorine Tests Passed (CTP) Rate - by zone per month
4. Water Access over time (stacked bar chart) - by zone per year
5. Population Unconnected to Water (PUW) Rate - by zone per year
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.plot_utils import set_smart_yaxis
from utils.colors import OKABE_ITO, CB_SEQUENTIAL
from utils.nrw import compute_best_nrw
from utils.floating_button import add_floating_chatbot_button
import warnings

warnings.filterwarnings('ignore')

# ---------------------------#
# Page Setup
# ---------------------------#
st.set_page_config(
    page_title="Water Operations Dashboard",
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
st.title("Water Operations")

with st.spinner('Loading water data...'):
    w_service_df = load_table('w_service')
    w_access_df = load_table('w_access')
    billing_df = load_table('billing')

# ---------------------------#
# Sidebar Filters
# ---------------------------#
st.sidebar.header("Filter Options")

# Get available countries
available_countries = get_clean_countries(w_service_df)
if not available_countries:
    available_countries = get_clean_countries(w_access_df)

selected_country = st.sidebar.selectbox(
    "Select Country",
    options=available_countries,
    index=0
)

st.sidebar.markdown("---")

# Date filtering
date_min, date_max = None, None
for df in [w_service_df, billing_df]:
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
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df = df[(df[date_col] >= start) & (df[date_col] <= end)]
    
    return df


w_service_filtered = apply_filters(w_service_df, selected_country, date_range)
w_access_filtered = apply_filters(w_access_df, selected_country, None, date_col='year')
billing_filtered = apply_filters(billing_df, selected_country, date_range)

# Track metrics for summary
summary_metrics = {}


# ===========================
# KPI 2: E.Coli Tests Passed (ETP) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  E.Coli Tests Passed (ETP) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "E.Coli Tests Passed for each zone per month = (tests_passed_ecoli / test_conducted_ecoli) × 100\n\n"
        "**Aggregation:** Zone × Month\n\n"
        "**Tooltip:** tests_passed_ecoli\n\n"
        "**File:** w_service")

# Check column names (may have variations)
ecoli_passed_col = None
ecoli_conducted_col = None
for col in w_service_filtered.columns:
    if 'passed' in col.lower() and 'ecoli' in col.lower():
        ecoli_passed_col = col
    if 'conducted' in col.lower() and 'ecoli' in col.lower():
        ecoli_conducted_col = col

if not w_service_filtered.empty and ecoli_passed_col and ecoli_conducted_col:
    df_etp = w_service_filtered.copy()
    if 'date' in df_etp.columns:
        df_etp['date'] = pd.to_datetime(df_etp['date'], errors='coerce')
    else:
        df_etp['date'] = pd.NaT
    
    # Get zone column
    zone_col = 'zone' if 'zone' in df_etp.columns else 'country'
    
    # Create year_month
    df_etp['year_month'] = df_etp['date'].dt.to_period('M').astype(str)
    
    # Aggregate by zone and month
    etp_agg = df_etp.groupby([zone_col, 'year_month']).agg({
        ecoli_passed_col: 'sum',
        ecoli_conducted_col: 'sum'
    }).reset_index()
    
    # Calculate ETP Rate
    etp_agg['etp_rate'] = etp_agg.apply(
        lambda row: safe_div(row[ecoli_passed_col], row[ecoli_conducted_col]) * 100,
        axis=1
    )
    
    # Filter valid (keep zero values, drop only missing denominators)
    etp_agg = etp_agg[etp_agg[ecoli_conducted_col].notna()]
    
    if not etp_agg.empty:
        col1, col2, col3 = st.columns(3)
        
        avg_etp = etp_agg['etp_rate'].mean()
        total_passed = etp_agg[ecoli_passed_col].sum()
        total_conducted = etp_agg[ecoli_conducted_col].sum()
        
        summary_metrics['avg_etp'] = avg_etp
        
        with col1:
            st.metric(
                "Average ETP Rate",
                f"{avg_etp:.1f}%",
                help=f"tests_passed_ecoli = {total_passed:,.0f}"
            )
        
        with col2:
            st.metric(
                "Tests Passed",
                f"{total_passed:,.0f}",
                help="Total E.Coli tests passed"
            )
        
        with col3:
            st.metric(
                "Tests Conducted",
                f"{total_conducted:,.0f}",
                help="Total E.Coli tests conducted"
            )
        
        # Charts
        # Column + Line combo chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add columns for tests conducted (light blue)
        fig.add_trace(
            go.Bar(
                x=etp_agg['year_month'],
                y=etp_agg[ecoli_conducted_col],
                name='Tests Conducted',
                marker_color='lightblue',
                opacity=0.6,
                yaxis='y2'
            ),
            secondary_y=True
        )
        
        # Add line for ETP Rate (green)
        for zone in etp_agg[zone_col].unique()[:5]:  # Limit to 5 zones for clarity
            zone_data = etp_agg[etp_agg[zone_col] == zone]
            fig.add_trace(
                go.Scatter(
                    x=zone_data['year_month'],
                    y=zone_data['etp_rate'],
                    name=f'{zone} - ETP Rate',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(size=6),
                    customdata=zone_data[[ecoli_passed_col]],
                    hovertemplate='<b>%{fullData.name}</b><br>ETP Rate: %{y:.1f}%<br>Tests Passed: %{customdata[0]:,.0f}<extra></extra>'
                ),
                secondary_y=False
            )
        
        # Add target line at 95%
        # target line removed
        
        # Update layout
        fig.update_xaxes(title_text="Period")
        fig.update_yaxes(title_text="ETP Rate (%)", secondary_y=False, range=[0, 105])
        fig.update_yaxes(title_text="Tests Conducted", secondary_y=True)
        
        fig.update_layout(
            title='E.Coli Test Pass Rate Over Time',
            template='plotly_white',
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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

        st.plotly_chart(fig, use_container_width=True, key="etp_trend")
        
        with st.expander("Understanding ETP Rate"):
            st.markdown("""
            **E.Coli Tests Passed (ETP) Rate** measures water quality compliance for E.Coli contamination.
            
            - **Formula**: `ETP Rate = (tests_passed_ecoli / test_conducted_ecoli) × 100`
            - **Tooltip**: tests_passed_ecoli (shown in metric tooltip)
            - **Aggregation**: By zone per month
            """)
    else:
        st.warning("No valid ETP data after filtering")
else:
    st.warning(f"E.Coli test data not available. Looking for: tests_passed_ecoli, test_conducted_ecoli")


# ===========================
# KPI 3: Chlorine Tests Passed (CTP) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  Chlorine Tests Passed (CTP) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "Chlorine Tests Passed for each zone per month = (tests_passed_chlorine / tests_conducted_chlorine) × 100\n\n"
        "**Aggregation:** Zone × Month\n\n"
        "**Tooltip:** tests_passed_chlorine\n\n"
        "**File:** w_service")

# Check column names
chlorine_passed_col = None
chlorine_conducted_col = None
for col in w_service_filtered.columns:
    if 'passed' in col.lower() and 'chlorine' in col.lower():
        chlorine_passed_col = col
    if 'conducted' in col.lower() and 'chlorine' in col.lower():
        chlorine_conducted_col = col

if not w_service_filtered.empty and chlorine_passed_col and chlorine_conducted_col:
    df_ctp = w_service_filtered.copy()
    if 'date' in df_ctp.columns:
        df_ctp['date'] = pd.to_datetime(df_ctp['date'], errors='coerce')
    else:
        df_ctp['date'] = pd.NaT
    
    zone_col = 'zone' if 'zone' in df_ctp.columns else 'country'
    df_ctp['year_month'] = df_ctp['date'].dt.to_period('M').astype(str)
    
    ctp_agg = df_ctp.groupby([zone_col, 'year_month']).agg({
        chlorine_passed_col: 'sum',
        chlorine_conducted_col: 'sum'
    }).reset_index()
    
    ctp_agg['ctp_rate'] = ctp_agg.apply(
        lambda row: safe_div(row[chlorine_passed_col], row[chlorine_conducted_col]) * 100,
        axis=1
    )
    
    ctp_agg = ctp_agg[ctp_agg[chlorine_conducted_col].notna()]
    
    if not ctp_agg.empty:
        col1, col2, col3 = st.columns(3)
        
        avg_ctp = ctp_agg['ctp_rate'].mean()
        total_passed = ctp_agg[chlorine_passed_col].sum()
        total_conducted = ctp_agg[chlorine_conducted_col].sum()
        
        summary_metrics['avg_ctp'] = avg_ctp
        
        with col1:
            st.metric(
                "Average CTP Rate",
                f"{avg_ctp:.1f}%",
                help=f"tests_passed_chlorine = {total_passed:,.0f}"
            )
        
        with col2:
            st.metric("Tests Passed", f"{total_passed:,.0f}")
        
        with col3:
            st.metric("Tests Conducted", f"{total_conducted:,.0f}")
        
        # Column + Line combo chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add columns for tests conducted (light blue)
        fig.add_trace(
            go.Bar(
                x=ctp_agg['year_month'],
                y=ctp_agg[chlorine_conducted_col],
                name='Tests Conducted',
                marker_color='lightblue',
                opacity=0.6,
                yaxis='y2'
            ),
            secondary_y=True
        )
        
        # Add line for CTP Rate (green)
        for zone in ctp_agg[zone_col].unique()[:5]:  # Limit to 5 zones for clarity
            zone_data = ctp_agg[ctp_agg[zone_col] == zone]
            fig.add_trace(
                go.Scatter(
                    x=zone_data['year_month'],
                    y=zone_data['ctp_rate'],
                    name=f'{zone} - CTP Rate',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(size=6),
                    customdata=zone_data[[chlorine_passed_col]],
                    hovertemplate='<b>%{fullData.name}</b><br>CTP Rate: %{y:.1f}%<br>Tests Passed: %{customdata[0]:,.0f}<extra></extra>'
                ),
                secondary_y=False
            )
        
        # Add target line at 95%
        # target line removed
        
        # Update layout
        fig.update_xaxes(title_text="Period")
        fig.update_yaxes(title_text="CTP Rate (%)", secondary_y=False, range=[0, 105])
        fig.update_yaxes(title_text="Tests Conducted", secondary_y=True)
        
        fig.update_layout(
            title='Chlorine Test Pass Rate Over Time',
            template='plotly_white',
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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

        st.plotly_chart(fig, use_container_width=True, key="ctp_trend")
        
        with st.expander("Understanding CTP Rate"):
            st.markdown("""
            **Chlorine Tests Passed (CTP) Rate** measures water quality compliance for chlorine residual.
            
            - **Formula**: `CTP Rate = (tests_passed_chlorine / tests_conducted_chlorine) × 100`
            - **Tooltip**: tests_passed_chlorine (shown in metric tooltip)
            - **Aggregation**: By zone per month
            """)
    else:
        st.warning("No valid CTP data after filtering")
else:
    st.warning("Chlorine test data not available")


# ===========================
# KPI 4: Water Access over time (Stacked Bar Chart)
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  Water Access Over Time")
with col_help:
    st.markdown("", help="**Metric:** Water Access (WA) over time (stacked bar chart)\n\n"
        "**Formula:** Direct columns for each zone per year:\n"
        "safely_managed_pct, basic_pct, limited_pct, unimproved_pct, surface_water_pct\n\n"
        "**Aggregation:** Zone × Year\n\n"
        "**Tooltips:** safely_managed, basic, limited, unimproved, surface_water (absolute numbers)\n\n"
        "**File:** w_access")

if not w_access_filtered.empty:
    df_access = w_access_filtered.copy()
    
    access_cols = ['safely_managed_pct', 'basic_pct', 'limited_pct', 'unimproved_pct', 'surface_water_pct']
    tooltip_cols = ['safely_managed', 'basic', 'limited', 'unimproved', 'surface_water']
    
    available_cols = [c for c in access_cols if c in df_access.columns]
    
    if available_cols:
        year_col = 'year' if 'year' in df_access.columns else 'date_YY' if 'date_YY' in df_access.columns else None
        
        if year_col:
            zone_col = 'zone' if 'zone' in df_access.columns else 'country'
            
            agg_cols = {c: 'mean' for c in available_cols}
            for tc in tooltip_cols:
                if tc in df_access.columns:
                    agg_cols[tc] = 'sum'
            
            access_agg = df_access.groupby([zone_col, year_col]).agg(agg_cols).reset_index()
            
            access_melt = access_agg.melt(
                id_vars=[zone_col, year_col],
                value_vars=available_cols,
                var_name='Access Type',
                value_name='Percentage'
            )
            
            access_melt['Access Type'] = access_melt['Access Type'].str.replace('_pct', '').str.replace('_', ' ').str.title()
            
            fig = px.bar(
                access_melt, x=year_col, y='Percentage', color='Access Type',
                title=f'Water Access by {zone_col.title()} Over Time',
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Percentage (%)",
                height=500,
                legend_title="Access Level",
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

            st.plotly_chart(fig, width='stretch', key="water_access_stacked")
            
            if zone_col in access_agg.columns:
                zones = access_agg[zone_col].unique()
                selected_zone = st.selectbox("Select Zone for Details:", zones, key="water_zone_selector")
                
                zone_data = access_agg[access_agg[zone_col] == selected_zone]
                
                if not zone_data.empty:
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
                                help=f"{tooltip_col} = {tooltip_val}" if tooltip_col else None
                            )
            
            with st.expander("Understanding Water Access"):
                st.markdown("""
                **Water Access** shows population distribution across service levels.
                
                - **Safely Managed**: Improved source, accessible on premises, available when needed, free of contamination
                - **Basic**: Improved source within 30 min round trip
                - **Limited**: Improved source over 30 min round trip
                - **Unimproved**: Unprotected well/spring
                - **Surface Water**: River, dam, lake, pond, stream, canal, irrigation channel
                
                **Tooltips**: safely_managed, basic, limited, unimproved, surface_water (absolute numbers)
                """)
        else:
            st.warning("No year column found")
    else:
        st.warning("Access percentage columns not found")
else:
    st.warning("Water access data not available")


# ===========================
# KPI 5: Population Unconnected to Water (PUW) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  Population Unconnected to Water (PUW) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "PUW Rate for each zone per year = (popn_total - municipal_coverage) / popn_total × 100\n\n"
        "**Aggregation:** Zone × Year\n\n"
        "**Tooltip:** popn_total - municipal_coverage (unconnected population)\n\n"
        "**File:** w_access")

if not w_access_filtered.empty and 'popn_total' in w_access_filtered.columns and 'municipal_coverage' in w_access_filtered.columns and 'popn_total' in w_access_filtered.columns:
    df_puw = w_access_filtered.copy()
    
    year_col = 'year' if 'year' in df_puw.columns else 'date_YY' if 'date_YY' in df_puw.columns else None
    zone_col = 'zone' if 'zone' in df_puw.columns else 'country'
    
    if year_col:
        puw_agg = df_puw.groupby([zone_col, year_col]).agg({
            'popn_total': 'sum',
            'municipal_coverage': 'sum',
            'popn_total': 'sum'
        }).reset_index()
        
        puw_agg['unconnected_pop'] = puw_agg['popn_total'] - puw_agg['municipal_coverage']
        puw_agg['puw_rate'] = puw_agg.apply(
            lambda row: safe_div(row['unconnected_pop'], row['popn_total']) * 100,
            axis=1
        )
        
        puw_agg = puw_agg[puw_agg['popn_total'].notna()]
        
        if not puw_agg.empty:
            col1, col2, col3 = st.columns(3)
            
            avg_puw = puw_agg['puw_rate'].mean()
            total_unconnected = puw_agg['unconnected_pop'].sum()
            total_pop = puw_agg['popn_total'].sum()
            
            summary_metrics['avg_puw'] = avg_puw
            
            with col1:
                st.metric(
                    "Average PUW Rate",
                    f"{avg_puw:.1f}%",
                    help=f"popn_total - municipal_coverage = {total_unconnected:,.0f}"
                )
            
            with col2:
                st.metric("Total Population", f"{total_pop:,.0f}")
            
            with col3:
                municipal = puw_agg['municipal_coverage'].sum()
                st.metric("Municipal Coverage", f"{municipal:,.0f}")
            
            # Horizontal bar chart sorted descending by PUW Rate
            # Calculate average per zone
            zone_avg = puw_agg.groupby(zone_col).agg({
                'puw_rate': 'mean',
                'unconnected_pop': 'sum'
            }).reset_index()
            zone_avg = zone_avg.sort_values('puw_rate', ascending=False)
            
            # Create horizontal bar chart with orange color
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                x=zone_avg['puw_rate'],
                y=zone_avg[zone_col],
                orientation='h',
                marker_color='orange',
                text=zone_avg['puw_rate'].round(1),
                texttemplate='%{text}%',
                textposition='outside',
                customdata=zone_avg[['unconnected_pop']],
                hovertemplate='<b>%{y}</b><br>PUW Rate: %{x:.1f}%<br>Unconnected Population: %{customdata[0]:,.0f}<extra></extra>'
            ))
            
            # Add target line at 50%
            # target line removed
            
            fig_bar.update_layout(
                title=f'Population Unconnected to Water (PUW) Rate by {zone_col.title()}',
                xaxis_title="PUW Rate (%)",
                yaxis_title=zone_col.title(),
                template='plotly_white',
                height=max(400, len(zone_avg) * 40),
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            
            try:
                fig_bar.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_bar, use_container_width=True, key="puw_zone_comparison")
            
            with st.expander("Understanding PUW Rate"):
                st.markdown("""
                **Population Unconnected to Water (PUW) Rate** measures water access gap.
                
                - **Formula**: `PUW Rate = (popn_total - municipal_coverage) / popn_total × 100`
                - **Tooltip**: popn_total - municipal_coverage (shown in metric tooltip)
                - **Aggregation**: By zone per year
                """)
        else:
            st.warning("No valid PUW data after filtering")
    else:
        st.warning("No year column found")
else:
    st.warning("Population/coverage data not available. Required: popn_total, municipal_coverage, households")



# Add floating chatbot button
add_floating_chatbot_button()
