import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from pathlib import Path
from utils.floating_button import add_floating_chatbot_button

st.set_page_config(page_title="Water Service Dashboard", layout="wide")

# Modern pastel design
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
    
    h1 { 
        font-size: 2.8rem; 
        font-weight: 600; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    h3 { 
        font-size: 0.875rem; 
        font-weight: 600; 
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
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
    
    .stWarning { 
        border-radius: 8px; 
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
    }
    
    .stInfo { 
        border-radius: 8px; 
        border-left: 4px solid #3b82f6;
        background: #eff6ff;
    }
    
    [data-testid="column"] { padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)

st.title(" Water Services")

# --- Helper Functions ---
def plotly_chart_with_labels(df, x_col, y_col, chart_label, unit="", color_col=None):
    """Create a line chart with labels"""
    st.subheader(chart_label)
    
    if df.empty or y_col not in df.columns:
        st.warning(f"No data available for {chart_label}")
        return
    
    # Filter out invalid values before aggregation
    df_clean = df[[x_col, y_col, color_col] if color_col and color_col in df.columns else [x_col, y_col]].copy()
    df_clean = df_clean.dropna(subset=[y_col])
    
    # Average y-axis by x-axis and color
    if color_col and color_col in df.columns:
        df_avg = df_clean.groupby([x_col, color_col], as_index=False)[y_col].mean().round(2)
        fig = px.line(df_avg, x=x_col, y=y_col, color=color_col, 
                     title=f"{chart_label} by {x_col}",
                     markers=True)
    else:
        df_avg = df_clean.groupby(x_col, as_index=False)[y_col].mean().round(2)
        fig = px.line(df_avg, x=x_col, y=y_col, 
                     title=f"{chart_label} by {x_col}",
                     markers=True)
    
    # Layout
    fig.update_layout(
        title_x=0.5,
        xaxis_title=x_col,
        yaxis_title=f"{y_col} {unit}",
        template="plotly_white",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart_label}")

# --- Import centralized data loader ---
from utils.data_loader import load_table

# Load only the data needed for this page (lazy loading)
with st.spinner('Loading water data...'):
    all_fin_service_df = load_table('all_fin_service')
    w_service_df = load_table('w_service')
    w_access_df = load_table('w_access')

# --- External Filter ---
filter_col = 'country'

st.sidebar.header("Filter Options")

# Get unique countries
if not w_access_df.empty and filter_col in w_access_df.columns:
    available_countries = sorted(w_access_df[filter_col].unique())
else:
    available_countries = ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']

# Single-select dropdown (keep behavior consistent with other pages)
cleaned = []
for c in available_countries:
    try:
        if pd.isna(c):
            continue
    except Exception:
        pass
    s = str(c).strip()
    if s == "" or s.lower() in ("nan", "n/a", "<n/a>", "<na>", "na", "none"):
        continue
    cleaned.append(s)

available_countries = sorted(set(cleaned)) if cleaned else ['No countries found']

selected_country = st.sidebar.selectbox(
    "Select Country",
    options=available_countries,
    index=0,
    help="Select a country to filter the dashboard (single selection)"
)

st.sidebar.markdown("---")

# Date filtering with quick period selection
date_min = None
date_max = None
date_col = None

for df in [w_service_df, w_access_df, all_fin_service_df]:
    if not df.empty:
        # Check for date columns
        if 'date' in df.columns:
            date_col = 'date'
        elif 'date_MMYY' in df.columns:
            date_col = 'date_MMYY'
        
        if date_col and date_col in df.columns:
            try:
                df_date_min = pd.to_datetime(df[date_col], errors='coerce').min()
                df_date_max = pd.to_datetime(df[date_col], errors='coerce').max()
                if pd.notna(df_date_min) and pd.notna(df_date_max):
                    if date_min is None or df_date_min < date_min:
                        date_min = df_date_min
                    if date_max is None or df_date_max > date_max:
                        date_max = df_date_max
            except:
                pass

if date_min and date_max and pd.notna(date_min) and pd.notna(date_max):
    st.sidebar.markdown("### Time Period")
    period_option = st.sidebar.radio(
        "Select Period:",
        ["All Time", "Last 12 Months", "Last 6 Months", "Custom Range"],
        index=0,
        help="Choose a time period to analyze"
    )
    
    if period_option == "Last 12 Months":
        date_range = (date_max - pd.DateOffset(months=12), date_max)
    elif period_option == "Last 6 Months":
        date_range = (date_max - pd.DateOffset(months=6), date_max)
    elif period_option == "Custom Range":
        date_range = st.sidebar.date_input("Select Date Range:", value=(date_min, date_max))
    else:
        date_range = (date_min, date_max)
    
    # Apply date filtering to dataframes
    if date_range and len(date_range) == 2:
        start = pd.to_datetime(date_range[0]) if not isinstance(date_range[0], pd.Timestamp) else date_range[0]
        end = pd.to_datetime(date_range[1]) if not isinstance(date_range[1], pd.Timestamp) else date_range[1]
        
        if not w_service_df.empty:
            dc = 'date' if 'date' in w_service_df.columns else 'date_MMYY' if 'date_MMYY' in w_service_df.columns else None
            if dc:
                try:
                    w_service_df[dc] = pd.to_datetime(w_service_df[dc], errors='coerce')
                    w_service_df = w_service_df[(w_service_df[dc] >= start) & (w_service_df[dc] <= end)]
                except:
                    pass
        
        if not w_access_df.empty:
            dc = 'date' if 'date' in w_access_df.columns else 'date_MMYY' if 'date_MMYY' in w_access_df.columns else None
            if dc:
                try:
                    w_access_df[dc] = pd.to_datetime(w_access_df[dc], errors='coerce')
                    w_access_df = w_access_df[(w_access_df[dc] >= start) & (w_access_df[dc] <= end)]
                except:
                    pass
        
        if not all_fin_service_df.empty:
            dc = 'date' if 'date' in all_fin_service_df.columns else 'date_MMYY' if 'date_MMYY' in all_fin_service_df.columns else None
            if dc:
                try:
                    all_fin_service_df[dc] = pd.to_datetime(all_fin_service_df[dc], errors='coerce')
                    all_fin_service_df = all_fin_service_df[(all_fin_service_df[dc] >= start) & (all_fin_service_df[dc] <= end)]
                except:
                    pass

# --- Main Dashboard ---

# KPI 1: Continuity of Supply
st.markdown("### Service Quality")
col1 = st.columns(1)[0]


with col1:
    # KPI 2: Drinking Water Quality Compliance
    df = w_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate Water Quality Compliance
        required_cols = ['test_passed_chlorine', 'tests_passed_ecoli', 'tests_conducted_chlorine', 'test_conducted_ecoli']
        
        # Check for alternative column names
        if 'test_passed_chlorine' not in df_filtered.columns:
            if 'tests_passed_chlorine' in df_filtered.columns:
                df_filtered['test_passed_chlorine'] = df_filtered['tests_passed_chlorine']
        
        has_chlorine = 'test_passed_chlorine' in df_filtered.columns and 'tests_conducted_chlorine' in df_filtered.columns
        has_ecoli = 'tests_passed_ecoli' in df_filtered.columns and 'test_conducted_ecoli' in df_filtered.columns
        
        if has_chlorine or has_ecoli:
            # Fill missing values with 0
            for col in required_cols:
                if col not in df_filtered.columns:
                    df_filtered[col] = 0
                else:
                    df_filtered[col] = df_filtered[col].fillna(0)
            
            df_filtered['total_passed'] = df_filtered['test_passed_chlorine'] + df_filtered['tests_passed_ecoli']
            df_filtered['total_conducted'] = df_filtered['tests_conducted_chlorine'] + df_filtered['test_conducted_ecoli']
            
            df_filtered["Water_Quality_Compliance"] = df_filtered.apply(
                lambda row: (row["total_passed"] / row["total_conducted"]) * 100
                if pd.notna(row["total_conducted"]) and row["total_conducted"] != 0 else 0,
                axis=1
            ).round(2)
            
            # Drop NaN values before calculating mean
            valid_compliance = df_filtered["Water_Quality_Compliance"].replace(0, pd.NA).dropna()
            
            if len(valid_compliance) > 0:
                avg_compliance = valid_compliance.mean()
                st.metric(
                    label="Drinking Water Quality Compliance",
                    value=f"{avg_compliance:.1f}%",
                    help="% of water quality tests passed - Category: Service Quality"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='Water_Quality_Compliance', 
                        chart_label="Drinking Water Quality Compliance",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid water quality compliance data available")
        else:
            st.warning("Water quality testing data not available")

st.markdown("---")
st.markdown("### Efficiency & Financial Sustainability")
col3, col4 = st.columns(2)

with col3:
    # KPI 3: Metering Ratio
    df = w_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate Metering Ratio
        if 'metered' in df_filtered.columns and 'total_consumption' in df_filtered.columns:
            df_filtered["Metering_Ratio"] = df_filtered.apply(
                lambda row: (row["metered"] / row["total_consumption"]) * 100
                if pd.notna(row["total_consumption"]) and row["total_consumption"] != 0 else 0,
                axis=1
            ).round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_metering = df_filtered["Metering_Ratio"].replace(0, pd.NA).dropna()
            
            if len(valid_metering) > 0:
                avg_metering = valid_metering.mean()
                st.metric(
                    label="Metering Ratio",
                    value=f"{avg_metering:.1f}%",
                    help="% of water consumption that is metered - Category: Efficiency & Billing"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='Metering_Ratio', 
                        chart_label="Metering Ratio",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid metering data available")
        else:
            st.warning("Metering data not available")

with col4:
    # KPI 4: Operating Cost Coverage
    df = all_fin_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate Operating Cost Coverage
        required_cols = ['sewer_revenue', 'water_revenue', 'opex']
        
        # Check if we have the necessary columns
        has_revenue = 'sewer_revenue' in df_filtered.columns or 'water_revenue' in df_filtered.columns
        has_opex = 'opex' in df_filtered.columns
        
        if has_revenue and has_opex:
            # Fill missing values with 0
            for col in ['sewer_revenue', 'water_revenue']:
                if col not in df_filtered.columns:
                    df_filtered[col] = 0
                else:
                    df_filtered[col] = df_filtered[col].fillna(0)
            
            df_filtered['opex'] = df_filtered['opex'].fillna(0)
            df_filtered['total_revenue'] = df_filtered['sewer_revenue'] + df_filtered['water_revenue']
            
            df_filtered["Operating_Cost_Coverage"] = df_filtered.apply(
                lambda row: (row["total_revenue"] / row["opex"]) * 100
                if pd.notna(row["opex"]) and row["opex"] != 0 else 0,
                axis=1
            ).round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_coverage = df_filtered["Operating_Cost_Coverage"].replace(0, pd.NA).dropna()
            
            if len(valid_coverage) > 0:
                avg_coverage = valid_coverage.mean()
                st.metric(
                    label="Operating Cost Coverage",
                    value=f"{avg_coverage:.1f}%",
                    help="Revenue as % of Operating Expenses - Category: Financial Sustainability"
                )
                
                # Chart
                x_col = 'date' if 'date' in df_filtered.columns else 'date_MMYY'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='Operating_Cost_Coverage', 
                        chart_label="Operating Cost Coverage",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid operating cost coverage data available")
        else:
            st.warning("Financial data not fully available")


st.markdown("""
### Water Service Dashboard Summary
This dashboard provides detailed water service performance metrics:

- **Service Quality**: Continuity of supply and drinking water quality compliance
- **Efficiency & Billing**: Metering ratio showing extent of water consumption measurement
- **Financial Sustainability**: Operating cost coverage showing revenue vs operational expenses
- **Water Stress**: Production level as percentage of available water resources

Use the sidebar to filter by country and explore detailed trends over time.
""")

# Add floating chatbot button
add_floating_chatbot_button()
