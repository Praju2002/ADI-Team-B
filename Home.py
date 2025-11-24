import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path
import time
from utils.data_loader import load_table, get_country_list

st.set_page_config(page_title="Summary Dashboard", page_icon="📊", layout="wide")

st.title("📊 Summary Dashboard - High-Level Overview")

# --- Helper Functions ---
# (Removed load_data_from_csv - now using centralized loader)

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
        height=400  # Fixed height for consistency
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart_label}")


def _get_processed_mtime():
    """Return processed.timestamp epoch float if exists, else 0."""
    marker = Path('Raw_Data/processed/processed.timestamp')
    try:
        if marker.exists():
            try:
                return float(marker.read_text())
            except Exception:
                return marker.stat().st_mtime
    except Exception:
        return 0
    return 0


@st.cache_data(ttl=3600)
def get_aggregated_from_parquet(table_name: str, x_col: str, y_col: str, color_col: str | None, countries_tuple: tuple, processed_mtime: float):
    """Load a table directly from Raw_Data/processed/<table_name>.parquet, apply country filter and aggregate.

    Cache key includes processed_mtime and countries_tuple so cache invalidates when processed data changes.
    """
    processed_dir = Path('Raw_Data/processed')
    p = processed_dir / f"{table_name}.parquet"
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(p)
    except Exception:
        return pd.DataFrame()

    if countries_tuple and 'country' in df.columns:
        df = df[df['country'].isin(countries_tuple)]

    if y_col not in df.columns:
        return pd.DataFrame()

    if color_col and color_col in df.columns:
        df_avg = df.groupby([x_col, color_col], as_index=False)[y_col].mean().round(2)
    else:
        df_avg = df.groupby(x_col, as_index=False)[y_col].mean().round(2)

    return df_avg

def create_metric_card(df, metric_col, title, unit="%", calculation_func=None):
    """Create a metric card with current value and trend"""
    if df.empty or metric_col not in df.columns:
        return None, None
    
    if calculation_func:
        value = calculation_func(df)
    else:
        value = df[metric_col].mean()
    
    return value, unit

# --- Load Data with Lazy Loading ---
# Only load tables as needed instead of all upfront
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = True
    with st.spinner('Initializing data loader...'):
        # This is fast - just sets up the lazy loader
        pass

# Load only the tables needed for this page
@st.cache_data(ttl=3600)
def get_home_page_data():
    """Load only the tables needed for Home page - lazy loading"""
    return {
        'w_access': load_table('w_access'),
        's_access': load_table('s_access'),
        'w_service': load_table('w_service'),
        'all_fin_service': load_table('all_fin_service'),
        'billing': load_table('billing')
    }

# Load data with lazy loading
data_dict = get_home_page_data()
all_fin_service_df = data_dict['all_fin_service']
billing_df = data_dict['billing']
w_access_df = data_dict['w_access']
s_access_df = data_dict['s_access']
w_service_df = data_dict['w_service']

# --- External Filter ---
filter_col = 'country'

st.sidebar.header("🌍 Filter Options")

# Get unique countries using cached function
available_countries = get_country_list('w_access')

selected_values = st.sidebar.multiselect(
    f"Select Country/Countries", 
    options=available_countries,
    default=available_countries
)

# Date filter if available
if 'date' in w_access_df.columns:
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input("Select Date Range", [])

st.sidebar.markdown("---")
st.sidebar.info("💡 Select countries to filter all metrics on this page.")

# --- Main Dashboard ---

# KPI 1: Population with Safely Managed Water
st.markdown("### 💧 Access Indicators")
col1, col2 = st.columns(2)

with col1:
    df = w_access_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate average - handle NaN values
        if 'safely_managed_pct' in df_filtered.columns:
            valid_data = df_filtered['safely_managed_pct'].dropna()
            
            if len(valid_data) > 0:
                avg_value = valid_data.mean()
                st.metric(
                    label="Population with Safely Managed Water",
                    value=f"{avg_value:.1f}%",
                    help="% of population with safely managed water - Category: Access"
                )
                
                # Chart
                if 'date_YY' in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col='date_YY', 
                        y_col='safely_managed_pct', 
                        chart_label="Population with Safely Managed Water",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid data available for safely managed water")

with col2:
    # KPI 2: Population with Safely Managed Sanitation
    df = s_access_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate average - handle NaN values
        if 'safely_managed_pct' in df_filtered.columns:
            valid_data = df_filtered['safely_managed_pct'].dropna()
            
            if len(valid_data) > 0:
                avg_value = valid_data.mean()
                st.metric(
                    label="Population with Safely Managed Sanitation",
                    value=f"{avg_value:.1f}%",
                    help="% of population with safely managed sanitation - Category: Access"
                )
                
                # Chart
                if 'date_YY' in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col='date_YY', 
                        y_col='safely_managed_pct', 
                        chart_label="Population with Safely Managed Sanitation",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid data available for safely managed sanitation")

st.markdown("---")
st.markdown("### 📈 Efficiency & Financial Sustainability")
col3, col4 = st.columns(2)

with col3:
    # KPI 3: Non-Revenue Water (NRW)
    df = w_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate NRW
        if 'NRW' not in df_filtered.columns and 'w_supplied' in df_filtered.columns and 'total_consumption' in df_filtered.columns:
            # Vectorized NRW (computed here only if not precomputed in data loader)
            df_filtered['w_supplied'] = pd.to_numeric(df_filtered['w_supplied'], errors='coerce')
            df_filtered['total_consumption'] = pd.to_numeric(df_filtered['total_consumption'], errors='coerce')
            df_filtered['NRW'] = ((df_filtered['w_supplied'] - df_filtered['total_consumption']) / df_filtered['w_supplied']) * 100
            df_filtered.loc[~df_filtered['w_supplied'].notna() | (df_filtered['w_supplied'] == 0), 'NRW'] = pd.NA
            df_filtered['NRW'] = df_filtered['NRW'].round(2)

        # Drop NaN and zero-like values before calculating mean
        valid_nrw = df_filtered['NRW'].replace(0, pd.NA).dropna() if 'NRW' in df_filtered.columns else pd.Series(dtype='float64')

        if len(valid_nrw) > 0:
            avg_nrw = valid_nrw.mean()
            st.metric(
                label="Non-Revenue Water (NRW)",
                value=f"{avg_nrw:.1f}%",
                help="% of water supplied not generating revenue - Category: Efficiency"
            )

            # Chart
            x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
            if x_col in df_filtered.columns:
                plotly_chart_with_labels(
                    df_filtered, 
                    x_col=x_col, 
                    y_col='NRW', 
                    chart_label="Non-Revenue Water (NRW)",
                    unit="(%)",
                    color_col='country'
                )
        else:
            st.warning("No valid NRW data available")

with col4:
    # KPI 4: Revenue Collection Efficiency
    df_fin = all_fin_service_df.copy()
    df_bill = billing_df.copy()
    
    if not df_fin.empty and filter_col in df_fin.columns:
        df_filtered_fin = df_fin[df_fin[filter_col].isin(selected_values)]
        
        # Calculate Revenue Collection Efficiency
        required_cols = ['sewer_revenue', 'water_revenue', 'sewer_billed', 'water_billed']
        
        # Check if we have billing data
        if 'sewer_billed' not in df_filtered_fin.columns and not df_bill.empty:
            # Merge with billing data
            if 'date' in df_filtered_fin.columns and 'date' in df_bill.columns:
                df_filtered_fin = df_filtered_fin.merge(
                    df_bill[['date', 'country', 'billed']].rename(columns={'billed': 'water_billed'}),
                    on=['date', 'country'],
                    how='left'
                )
        
        # Calculate efficiency
        has_revenue = 'sewer_revenue' in df_filtered_fin.columns or 'water_revenue' in df_filtered_fin.columns
        has_billed = 'sewer_billed' in df_filtered_fin.columns or 'water_billed' in df_filtered_fin.columns

        if has_revenue and has_billed:
            # Ensure numeric and fill missing with 0 where appropriate
            for col in ['sewer_revenue', 'water_revenue', 'sewer_billed', 'water_billed']:
                if col not in df_filtered_fin.columns:
                    df_filtered_fin[col] = 0
                else:
                    df_filtered_fin[col] = pd.to_numeric(df_filtered_fin[col], errors='coerce').fillna(0)

            df_filtered_fin['total_revenue'] = df_filtered_fin['sewer_revenue'] + df_filtered_fin['water_revenue']
            df_filtered_fin['total_billed'] = df_filtered_fin['sewer_billed'] + df_filtered_fin['water_billed']

            # Vectorized efficiency (if not precomputed)
            if 'Revenue_Collection_Efficiency' not in df_filtered_fin.columns:
                df_filtered_fin.loc[(df_filtered_fin['total_billed'].notna()) & (df_filtered_fin['total_billed'] != 0), 'Revenue_Collection_Efficiency'] = (
                    df_filtered_fin['total_revenue'] / df_filtered_fin['total_billed']
                ) * 100
                df_filtered_fin['Revenue_Collection_Efficiency'] = df_filtered_fin['Revenue_Collection_Efficiency'].round(2)

            # Drop NaN and zero-like values before calculating mean
            valid_efficiency = df_filtered_fin['Revenue_Collection_Efficiency'].replace(0, pd.NA).dropna()

            if len(valid_efficiency) > 0:
                avg_efficiency = valid_efficiency.mean()
                st.metric(
                    label="Revenue Collection Efficiency",
                    value=f"{avg_efficiency:.1f}%",
                    help="% of billed revenue actually collected - Category: Financial Sustainability"
                )
                
                # Chart
                x_col = 'date' if 'date' in df_filtered_fin.columns else 'date_MMYY'
                if x_col in df_filtered_fin.columns:
                    plotly_chart_with_labels(
                        df_filtered_fin, 
                        x_col=x_col, 
                        y_col='Revenue_Collection_Efficiency', 
                        chart_label="Revenue Collection Efficiency",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid revenue collection efficiency data available")
        else:
            st.warning("Revenue and billing data not fully available")

st.markdown("---")
st.markdown("""
### 📋 Dashboard Summary
This dashboard provides a high-level overview of water and sanitation services across selected countries:

- **Access Indicators**: Population coverage with safely managed water and sanitation
- **Efficiency**: Non-Revenue Water showing system losses
- **Financial Sustainability**: Revenue collection efficiency showing billing vs collection performance

Use the sidebar to filter by country and explore detailed trends over time.
""")
