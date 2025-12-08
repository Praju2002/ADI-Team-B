"""
Financial Health & Sustainability Dashboard
============================================
KPIs Implemented:
1. Non-Revenue Water (NRW) Rate - by zone per month
2. Sewer Revenue Coverage (SRC) Rate - by city per month  
3. OpEx Share of Budget (OSB) Rate - by city per year
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
import warnings

warnings.filterwarnings('ignore')

# ---------------------------#
# Page Setup
# ---------------------------#
st.set_page_config(
    page_title="Financial Health Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure browser resolves Streamlit runtime assets from root
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
st.title("Financial Health & Sustainability")

with st.spinner('Loading financial data...'):
    billing_df = load_table('billing')
    all_fin_service_df = load_table('all_fin_service')
    all_national_df = load_table('all_nationalacc')

# ---------------------------#
# Sidebar Filters
# ---------------------------#
st.sidebar.header("Filter Options")

# Get available countries
available_countries = get_clean_countries(billing_df)
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
for df in [billing_df, all_fin_service_df]:
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
def apply_filters(df, country, date_range):
    """Apply country and date filters to dataframe."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Country filter
    if country and 'country' in df.columns:
        df = df[df['country'] == country]
    
    # Date filter - dates should already be parsed by loader
    if date_range and len(date_range) == 2 and 'date' in df.columns:
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df = df[(df['date'] >= start) & (df['date'] <= end)]
    
    return df


billing_filtered = apply_filters(billing_df, selected_country, date_range)
fin_service_filtered = apply_filters(all_fin_service_df, selected_country, date_range)
national_filtered = apply_filters(all_national_df, selected_country, date_range)

# Track metrics for summary
summary_metrics = {}

# ===========================
# KPI 1: Non-Revenue Water (NRW) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  Non-Revenue Water (NRW) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "Total_billed = Sum of billed for each zone per month across all days, customers, and sources\n\n"
        "Total_paid = Sum of paid for each zone per month across all days, customers, and sources\n\n"
        "NRW Rate = (Total_billed - Total_paid) × 100 / Total_billed\n\n"
        "**Aggregation:** Zone × Month\n\n"
        "**Tooltip:** NRW Amount = Total_billed - Total_paid\n\n"
        "**File:** billing")

if not billing_filtered.empty and 'billed' in billing_filtered.columns and 'paid' in billing_filtered.columns:
    df_nrw = billing_filtered.copy()
    
    # Date is already parsed - just verify we have it
    if 'date' not in df_nrw.columns or df_nrw['date'].isna().all():
        st.warning("Date column not available in billing data")
    else:
        # Create zone from country since zone/source columns don't exist in billing CSV
        if 'zone' not in df_nrw.columns:
            if 'city' in df_nrw.columns:
                df_nrw['zone'] = df_nrw['city']
            elif 'country' in df_nrw.columns:
                df_nrw['zone'] = df_nrw['country']
            else:
                df_nrw['zone'] = 'All Zones'
        
        # Aggregate by zone and month
        df_nrw['year_month'] = df_nrw['date'].dt.to_period('M').astype(str)
        
        # Ensure numeric columns
        df_nrw['billed'] = pd.to_numeric(df_nrw['billed'], errors='coerce')
        df_nrw['paid'] = pd.to_numeric(df_nrw['paid'], errors='coerce')
        
        nrw_agg = df_nrw.groupby(['zone', 'year_month']).agg({
            'billed': 'sum',
            'paid': 'sum'
        }).reset_index()
        
        # Calculate NRW Rate
        nrw_agg['nrw_amount'] = nrw_agg['billed'] - nrw_agg['paid']
        nrw_agg['nrw_rate'] = nrw_agg.apply(
            lambda row: safe_div(row['nrw_amount'], row['billed']) * 100,
            axis=1
        )
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        avg_nrw = nrw_agg['nrw_rate'].mean()
        total_nrw_amount = nrw_agg['nrw_amount'].sum()
        total_billed = nrw_agg['billed'].sum()

        # If billed amounts are zero or invalid, try volumetric NRW using production + w_service
        if total_billed == 0 or pd.isna(avg_nrw):
            prod_df = load_table('production')
            ws_df = load_table('w_service')
            best = compute_best_nrw(billing_df, prod_df, ws_df, selected_country)
            if best.get('mode') == 'volumetric':
                vol_nat = best['national']
                # Use volumetric metrics
                avg_nrw = vol_nat['nrw_pct_of_input'].mean()
                total_nrw_amount = vol_nat['nrw_m3'].sum()
                total_billed = vol_nat['system_input_m3'].sum()
                # mark in summary that these are volumetric units (m3)
                summary_metrics['nrw_mode'] = 'volumetric'
            else:
                summary_metrics['nrw_mode'] = 'financial'

        summary_metrics['avg_nrw'] = avg_nrw
        
        with col1:
                st.metric(
                    "Average NRW Rate",
                    f"{avg_nrw:.1f}%",
                    help="NRW = (system_input - consumption) / system_input × 100" if summary_metrics.get('nrw_mode') == 'volumetric' else "NRW Amount = billed - paid"
                )
        
        with col2:
            # Show a single total metric; units depend on mode
            if summary_metrics.get('nrw_mode') == 'volumetric':
                st.metric(
                    "Total NRW Volume",
                    f"{total_nrw_amount:,.0f} m3",
                    help="Total volumetric NRW (system_input - consumption)"
                )
            else:
                st.metric(
                    "Total NRW Amount",
                    f"${total_nrw_amount:,.0f}",
                    help="Total revenue lost to non-payment"
                )
        
        with col3:
            if summary_metrics.get('nrw_mode') == 'volumetric':
                st.metric(
                    "Total System Input",
                    f"{total_billed:,.0f} m3",
                    help="Total system input (production)"
                )
            else:
                st.metric(
                    "Total Billed",
                    f"${total_billed:,.0f}",
                    help="Total amount billed across all zones"
                )
        
        # Wide line chart. Use volumetric chart when volumetric mode is active,
        # otherwise default to billing-based chart.
        if summary_metrics.get('nrw_mode') == 'volumetric':
            # Ensure we have volumetric national balance table
            # Use a locals() check instead of a bare expression to avoid accidental output
            if 'vol_nat' not in locals():
                prod_df = load_table('production')
                ws_df = load_table('w_service')
                best = compute_best_nrw(billing_df, prod_df, ws_df, selected_country)
                vol_nat = best.get('national', pd.DataFrame())

            bal = vol_nat.copy()
            if not bal.empty:
                fig_nrw = make_subplots(specs=[[{"secondary_y": True}]])

                # Bar: NRW volume (m3) on secondary axis
                fig_nrw.add_trace(
                    go.Bar(
                        x=bal['year_month'],
                        y=bal['nrw_m3'],
                        name='NRW Volume (m3)',
                        marker_color='lightgray',
                        opacity=0.6,
                        hovertemplate='<b>%{x}</b><br>NRW Volume: %{y:,.0f} m3<extra></extra>'
                    ),
                    secondary_y=True
                )

                # Line: NRW % of input on primary axis
                fig_nrw.add_trace(
                    go.Scatter(
                        x=bal['year_month'],
                        y=bal['nrw_pct_of_input'],
                        name='NRW % of Input',
                        mode='lines+markers',
                        line=dict(color=OKABE_ITO[4], width=3),
                        marker=dict(size=8, symbol='circle', color=OKABE_ITO[4]),
                        hovertemplate='<b>%{x}</b><br>NRW %: %{y:.1f}%<extra></extra>'
                    ),
                    secondary_y=False
                )

                fig_nrw.update_xaxes(title_text="Month", rangeslider_visible=True, rangeslider_thickness=0.05)
                fig_nrw.update_yaxes(title_text="NRW Rate (%)", secondary_y=False)
                fig_nrw.update_yaxes(title_text="NRW Volume (m3)", secondary_y=True, showgrid=False)
                fig_nrw.update_layout(
                    title='Volumetric Non-Revenue Water by Month',
                    height=500,
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", align="left")
                )

                try:
                    set_smart_yaxis(fig_nrw, primary=bal['nrw_pct_of_input'], secondary=bal['nrw_m3'])
                except Exception:
                    pass

                try:
                    fig_nrw.update_layout(colorway=OKABE_ITO)
                except Exception:
                    pass

                st.plotly_chart(fig_nrw, use_container_width=True, key="nrw_rate_trend_volumetric")
            else:
                st.warning("Volumetric NRW data not available to plot.")
        else:
            # Billing-based chart (existing behavior)
            fig_nrw = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add thin overlay bar for NRW amount (on secondary axis)
            for zone in nrw_agg['zone'].unique():
                zone_data = nrw_agg[nrw_agg['zone'] == zone]
                fig_nrw.add_trace(
                    go.Bar(
                        x=zone_data['year_month'],
                        y=zone_data['nrw_amount'],
                        name=f'{zone} - NRW Amount',
                        marker_color='lightgray',
                        opacity=0.3,
                        showlegend=False,
                        hovertemplate='<b>%{x}</b><br>NRW Amount: $%{y:,.0f}<extra></extra>'
                    ),
                    secondary_y=True
                )
            
            # Add line with visible data points for NRW rate (on primary axis)
            for zone in nrw_agg['zone'].unique():
                zone_data = nrw_agg[nrw_agg['zone'] == zone]
                fig_nrw.add_trace(
                    go.Scatter(
                        x=zone_data['year_month'],
                        y=zone_data['nrw_rate'],
                        name=zone,
                        mode='lines+markers',
                        line=dict(color=OKABE_ITO[4], width=3),
                        marker=dict(size=8, symbol='circle', color=OKABE_ITO[4]),
                        hovertemplate='<b>%{x}</b><br>NRW Rate: %{y:.1f}%<extra></extra>'
                    ),
                    secondary_y=False
                )
            
            # Update layout
            fig_nrw.update_xaxes(title_text="Month", rangeslider_visible=True, rangeslider_thickness=0.05)
            fig_nrw.update_yaxes(title_text="NRW Rate (%)", secondary_y=False)
            fig_nrw.update_yaxes(title_text="NRW Amount ($)", secondary_y=True, showgrid=False)
            fig_nrw.update_layout(
                title='Non-Revenue Water Rate by Zone Over Time',
                height=500,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            # Adjust y-axes to avoid very-tight ranges that make small variations appear flat.
            try:
                set_smart_yaxis(fig_nrw, primary=nrw_agg['nrw_rate'], secondary=nrw_agg['nrw_amount'])
            except Exception:
                pass

            try:
                fig_nrw.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_nrw, use_container_width=True, key="nrw_rate_trend")
        
        # Tooltip explanation
        with st.expander("Understanding NRW Rate"):
            st.markdown("""
            **Non-Revenue Water (NRW) Rate** measures the percentage of billed water that is not paid for.
            
            - **Formula**: `NRW Rate = ((Billed - Paid) / Billed) × 100`
            - **NRW Amount**: `Billed - Paid` (shown in tooltip)
            - **Aggregation**: By zone per month
            """)
else:
    st.warning("Billing data not available for NRW calculation. Required columns: billed, paid")


# ===========================
# KPI 2: Sewer Revenue Coverage (SRC) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  Sewer Revenue Coverage (SRC) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "SRC Rate for each city per month = (sewer_revenue / opex) × 100\n\n"
        "**Aggregation:** City × Month\n\n"
        "**Tooltip:** SRC Amount = sewer_revenue\n\n"
        "**File:** all_fin_service")

if not fin_service_filtered.empty and 'sewer_revenue' in fin_service_filtered.columns and 'opex' in fin_service_filtered.columns:
    df_src = fin_service_filtered.copy()
    
    # Date is already parsed
    if 'date' not in df_src.columns or df_src['date'].isna().all():
        st.warning("Date column not available in financial service data")
    else:
        # City column exists in all_fin_service CSV
        if 'city' not in df_src.columns:
            df_src['city'] = df_src.get('country', 'Unknown')
        
        # Aggregate by city and month
        df_src['year_month'] = df_src['date'].dt.to_period('M').astype(str)
        
        # Ensure numeric BEFORE aggregation
        df_src['sewer_revenue'] = pd.to_numeric(df_src['sewer_revenue'], errors='coerce')
        df_src['opex'] = pd.to_numeric(df_src['opex'], errors='coerce')
        
        src_agg = df_src.groupby(['city', 'year_month']).agg({
            'sewer_revenue': 'sum',
            'opex': 'sum'
        }).reset_index()
        
        # Compute SRC Rate (keep zero values, drop NaN)
        src_agg['src_rate'] = src_agg.apply(
            lambda row: safe_div(row['sewer_revenue'], row['opex']) * 100,
            axis=1
        )
        # Keep zero values but drop NaN
        src_agg = src_agg[src_agg['src_rate'].notna()]
        
        if not src_agg.empty:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            avg_src = src_agg['src_rate'].mean()
            total_sewer_revenue = src_agg['sewer_revenue'].sum()
            total_opex = src_agg['opex'].sum()
            
            summary_metrics['avg_src'] = avg_src
            
            with col1:
                st.metric(
                    "Average SRC Rate",
                    f"{avg_src:.1f}%",
                    help="SRC Amount = sewer_revenue"
                )
            
            with col2:
                st.metric(
                    "Total Sewer Revenue",
                    f"${total_sewer_revenue:,.0f}",
                    help="Total sewer revenue collected"
                )
            
            with col3:
                st.metric(
                    "Total OpEx",
                    f"${total_opex:,.0f}",
                    help="Total operating expenses"
                )
            
            # Column + Line combo chart (revenue + coverage %)
            fig_src = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add columns for sewer revenue (on primary axis) - Teal color
            for city in src_agg['city'].unique():
                city_data = src_agg[src_agg['city'] == city]
                fig_src.add_trace(
                    go.Bar(
                        x=city_data['year_month'],
                        y=city_data['sewer_revenue'],
                        name=f'{city} - Revenue',
                        marker_color=OKABE_ITO[2],
                        opacity=0.85,
                        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
                    ),
                    secondary_y=False
                )
            
            # Add line for SRC rate (on secondary axis) - Green color
            for city in src_agg['city'].unique():
                city_data = src_agg[src_agg['city'] == city]
                fig_src.add_trace(
                    go.Scatter(
                        x=city_data['year_month'],
                        y=city_data['src_rate'],
                        name=f'{city} - Coverage %',
                        mode='lines+markers',
                        line=dict(color=OKABE_ITO[0], width=3),
                        marker=dict(size=8, color=OKABE_ITO[0]),
                        yaxis='y2',
                        hovertemplate='<b>%{x}</b><br>SRC Rate: %{y:.1f}%<extra></extra>'
                    ),
                    secondary_y=True
                )
            
            # Add target line at 100%
            # target line removed
            
            # Update layout
            fig_src.update_xaxes(title_text="Month", rangeslider_visible=True, rangeslider_thickness=0.05)
            fig_src.update_yaxes(title_text="Sewer Revenue ($)", secondary_y=False)
            fig_src.update_yaxes(title_text="SRC Rate (%)", secondary_y=True)
            fig_src.update_layout(
                title='Sewer Revenue Coverage by City',
                height=500,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial",
                    align="left"
                )
            )
            # Adjust y-axes so small-rate series are visible and revenue axis has sensible padding
            try:
                set_smart_yaxis(fig_src, primary=src_agg['sewer_revenue'], secondary=src_agg['src_rate'])
            except Exception:
                pass

            try:
                fig_src.update_layout(colorway=OKABE_ITO)
            except Exception:
                pass

            st.plotly_chart(fig_src, use_container_width=True, key="src_rate_trend")
            
            # Tooltip explanation
            with st.expander("Understanding SRC Rate"):
                st.markdown("""
                **Sewer Revenue Coverage (SRC) Rate** measures whether sewer revenue covers operating costs.
                
                - **Formula**: `SRC Rate = (Sewer Revenue / OpEx) × 100`
                - **SRC Amount**: `sewer_revenue` (shown in tooltip)
                - **Aggregation**: By city per month
                
                Reference: [MDPI Water Journal](https://www.mdpi.com/2073-4441/10/1/27)
                """)
        else:
            st.warning("No valid SRC data after filtering")
else:
    st.warning("Financial service data not available for SRC calculation. Required columns: sewer_revenue, opex")


# ===========================
# KPI 3: OpEx Share of Budget (OSB) Rate
# ===========================
st.markdown("---")
col_title, col_help = st.columns([0.95, 0.05])
with col_title:
    st.markdown("###  OpEx Share of Budget (OSB) Rate")
with col_help:
    st.markdown("", help="**Formula:**\n\n"
        "Total_opex = For all months of every year, sum of opex across each city\n\n"
        "Budget_allocated = As provided for every year from all_national\n\n"
        "OSB Rate for each city per year = (Total_opex / Budget_allocated) × 100\n\n"
        "**Aggregation:** City × Year\n\n"
        "**Tooltip:** Total_opex\n\n"
        "**Files:** all_fin_service and all_national")

if not fin_service_filtered.empty and not national_filtered.empty:
    df_fin = fin_service_filtered.copy()
    df_nat = national_filtered.copy()
    
    # Dates are already parsed - just extract year
    if 'date' in df_fin.columns and not df_fin['date'].isna().all():
        df_fin['year'] = df_fin['date'].dt.year
    else:
        df_fin['year'] = None
    
    if 'date' in df_nat.columns and not df_nat['date'].isna().all():
        df_nat['year'] = df_nat['date'].dt.year
    else:
        df_nat['year'] = None
    
    # Create city column if not exists
    if 'city' not in df_fin.columns:
        df_fin['city'] = df_fin.get('country', 'Unknown')
    if 'city' not in df_nat.columns:
        df_nat['city'] = df_nat.get('country', 'Unknown')
    
    # Check if we have valid year data
    if df_fin['year'].isna().all() and df_nat['year'].isna().all():
        st.warning("Year data not available for OSB calculation")
    # Aggregate opex by city (across years) to show city-level OSB
    elif 'opex' in df_fin.columns:
        # Ensure opex numeric
        df_fin['opex'] = pd.to_numeric(df_fin['opex'], errors='coerce')
        # Aggregate opex across all available years by city
        opex_agg = df_fin.groupby(['city'], as_index=False).agg({'opex': 'sum'}).rename(columns={'opex': 'total_opex'})

        # Get budget allocation by city across years (sum budgets to match opex aggregation)
        if 'budget_allocated' in df_nat.columns:
            df_nat['budget_allocated'] = pd.to_numeric(df_nat['budget_allocated'], errors='coerce')
            budget_agg = df_nat.groupby(['city'], as_index=False).agg({'budget_allocated': 'sum'})

            # Merge city-level totals
            osb_data = opex_agg.merge(budget_agg, on=['city'], how='inner')

            # Calculate OSB Rate at city level
            osb_data['total_opex'] = pd.to_numeric(osb_data['total_opex'], errors='coerce')
            osb_data['budget_allocated'] = pd.to_numeric(osb_data['budget_allocated'], errors='coerce')
            osb_data['osb_rate'] = osb_data.apply(
                lambda row: safe_div(row['total_opex'], row['budget_allocated']) * 100 if row['budget_allocated'] > 0 else float('nan'),
                axis=1
            )
            osb_data = osb_data[osb_data['osb_rate'].notna()]
            
            if not osb_data.empty:
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                avg_osb = osb_data['osb_rate'].mean()
                total_opex_sum = osb_data['total_opex'].sum()
                total_budget = osb_data['budget_allocated'].sum()
                
                summary_metrics['avg_osb'] = avg_osb
                
                with col1:
                    st.metric(
                        "Average OSB Rate",
                        f"{avg_osb:.1f}%",
                        help="Total_opex shown in tooltip"
                    )
                
                with col2:
                    st.metric(
                        "Total OpEx",
                        f"${total_opex_sum:,.0f}",
                        help="Sum of all operating expenses"
                    )
                
                with col3:
                    st.metric(
                        "Total Budget Allocated",
                        f"${total_budget:,.0f}",
                        help="Total budget allocated across all years"
                    )
                
                # Horizontal bar chart with gradient color showing budget utilization
                # Create city labels and sort by OSB rate (city-level view)
                osb_display = osb_data.copy()
                osb_display['city_label'] = osb_display['city']
                osb_display = osb_display.sort_values('osb_rate', ascending=True)
                
                # Create gradient blue colors based on OSB rate
                # Light blue for low utilization, dark blue for high utilization
                colors = []
                for rate in osb_display['osb_rate']:
                    if rate <= 50:
                        colors.append('#cce5ff')  # Light blue
                    elif rate <= 75:
                        colors.append('#66b3ff')  # Medium blue
                    elif rate <= 100:
                        colors.append('#0080ff')  # Blue
                    else:
                        colors.append('#0056b3')  # Dark blue
                
                fig_osb = go.Figure()
                
                fig_osb.add_trace(go.Bar(
                    y=osb_display['city_label'],
                    x=osb_display['osb_rate'],
                    orientation='h',
                    marker=dict(
                        color=colors,
                        line=dict(color='#003d7a', width=1)
                    ),
                    text=osb_display['osb_rate'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>OSB Rate: %{x:.1f}%<br>Total OpEx: $%{customdata[0]:,.0f}<br>Total Budget: $%{customdata[1]:,.0f}<extra></extra>',
                    customdata=osb_display[['total_opex', 'budget_allocated']].values
                ))
                
                # Add vertical line at 100% budget limit
                # budget limit line removed
                
                fig_osb.update_layout(
                    title='OpEx Share of Budget by City',
                    xaxis_title="OSB Rate (%)",
                    yaxis_title="City (Year)",
                    height=max(400, len(osb_display) * 40),
                    showlegend=False,
                    xaxis=dict(
                        range=[0, max(osb_display['osb_rate'].max() * 1.1, 110)],
                        rangeslider=dict(visible=True, thickness=0.05)
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial",
                        align="left"
                    ),
                    dragmode='zoom'
                )
                # For horizontal bar chart the numeric axis is `x`, helper focuses on y-axis.
                # Keep existing x-range behavior; render chart.
                try:
                    fig_osb.update_layout(colorway=OKABE_ITO)
                except Exception:
                    pass

                st.plotly_chart(fig_osb, use_container_width=True, key="osb_rate_chart")
                
                # Tooltip explanation
                with st.expander("Understanding OSB Rate"):
                    st.markdown("""
                    **OpEx Share of Budget (OSB) Rate** measures how much of the allocated budget is consumed by operating expenses.
                    
                    - **Formula**: `OSB Rate = (Total OpEx / Budget Allocated) × 100`
                    - **Total_opex**: Sum of opex across all months for each city (shown in tooltip)
                    - **Aggregation**: By city per year
                    """)
            else:
                st.warning("No valid OSB data after filtering")
        else:
            st.warning("Budget allocation data not available in national accounts")
    else:
        st.warning("OpEx data not available in financial services")
else:
    st.warning("Financial or national data not available for OSB calculation")


# ===========================
# Summary Section
# ===========================
st.markdown("---")
st.markdown("### Financial Health Summary")

summary_data = []

# NRW Summary
if 'avg_nrw' in summary_metrics:
    avg_nrw = summary_metrics['avg_nrw']
    summary_data.append({
        'KPI': 'Non-Revenue Water Rate',
        'Value': f"{avg_nrw:.1f}%",
        'Status': 'Good' if avg_nrw < 25 else 'High' if avg_nrw < 40 else 'Critical'
    })

# SRC Summary
if 'avg_src' in summary_metrics:
    avg_src = summary_metrics['avg_src']
    summary_data.append({
        'KPI': 'Sewer Revenue Coverage Rate',
        'Value': f"{avg_src:.1f}%",
        'Status': 'Sustainable' if avg_src >= 100 else 'Below Cost Recovery' if avg_src >= 80 else 'Critical'
    })

# OSB Summary
if 'avg_osb' in summary_metrics:
    avg_osb = summary_metrics['avg_osb']
    summary_data.append({
        'KPI': 'OpEx Share of Budget Rate',
        'Value': f"{avg_osb:.1f}%",
        'Status': 'Within Budget' if avg_osb <= 100 else 'Over Budget' if avg_osb <= 120 else 'Critical'
    })

if summary_data:
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, width='stretch', hide_index=True)
else:
    st.info("No summary data available. Please check data availability.")


st.markdown("---")
st.markdown("""
### Financial Health Dashboard Summary

This dashboard tracks **Financial Health & Sustainability** through three key performance indicators:

1. **NRW Rate**: Measures revenue leakage from unpaid bills
2. **SRC Rate**: Assesses whether sewer revenue covers operating costs
3. **OSB Rate**: Monitors operating expense efficiency against budget

Use the sidebar filters to explore different countries and time periods.
""")
