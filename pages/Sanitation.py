import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(page_title="Sanitation Service Dashboard", page_icon="🚽", layout="wide")

st.title("🚽 Sanitation Service Dashboard")

from utils.data_loader import load_all_data

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

# Use centralized loader from utils.data_loader (cached there)

# Load data once with caching
data_dict = load_all_data()
all_fin_service_df = data_dict.get('all_fin_service', pd.DataFrame())
all_national_df = data_dict.get('all_national', pd.DataFrame())
billing_df = data_dict.get('billing', pd.DataFrame())
production_df = data_dict.get('production', pd.DataFrame())
s_access_df = data_dict.get('s_access', pd.DataFrame())
s_service_df = data_dict.get('s_service', pd.DataFrame())
w_access_df = data_dict.get('w_access', pd.DataFrame())
w_service_df = data_dict.get('w_service', pd.DataFrame())

# --- External Filter ---
filter_col = 'country'

st.sidebar.header("🌍 Filter Options")

# Get unique countries
if not s_service_df.empty and filter_col in s_service_df.columns:
    available_countries = sorted(s_service_df[filter_col].unique())
elif not w_access_df.empty and filter_col in w_access_df.columns:
    available_countries = sorted(w_access_df[filter_col].unique())
else:
    available_countries = ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']

selected_values = st.sidebar.multiselect(
    f"Select Country/Countries", 
    options=available_countries,
    default=available_countries
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Select countries to filter all sanitation service metrics.")

# --- Main Dashboard ---

# KPI 1: Sewer Coverage
st.markdown("### 🏘️ Access")
col1, col2 = st.columns(2)

with col1:
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate Sewer Coverage
        if 'sewer_connections' in df_filtered.columns and 'households' in df_filtered.columns:
            # Vectorized sewer coverage
            sewer_connections = pd.to_numeric(df_filtered.get('sewer_connections', pd.Series(dtype=float)), errors='coerce')
            households = pd.to_numeric(df_filtered.get('households', pd.Series(dtype=float)), errors='coerce')
            coverage = (sewer_connections / households) * 100
            coverage = coverage.replace([np.inf, -np.inf], pd.NA)
            df_filtered['Sewer_Coverage'] = coverage.round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_coverage = df_filtered["Sewer_Coverage"].replace(0, pd.NA).dropna()
            
            if len(valid_coverage) > 0:
                avg_coverage = valid_coverage.mean()
                st.metric(
                    label="Sewer Coverage",
                    value=f"{avg_coverage:.1f}%",
                    help="% of households with sewer connections - Category: Access"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='Sewer_Coverage', 
                        chart_label="Sewer Coverage",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid sewer coverage data available")
        else:
            st.warning("Sewer connection data not available")

with col2:
    # KPI 2: Wastewater Safely Treated
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate Wastewater Treatment Rate
        if 'ww_treated' in df_filtered.columns and 'ww_collected' in df_filtered.columns:
            # Vectorized wastewater treated percentage
            ww_treated = pd.to_numeric(df_filtered.get('ww_treated', pd.Series(dtype=float)), errors='coerce')
            ww_collected = pd.to_numeric(df_filtered.get('ww_collected', pd.Series(dtype=float)), errors='coerce')
            treated_pct = (ww_treated / ww_collected) * 100
            treated_pct = treated_pct.replace([np.inf, -np.inf], pd.NA)
            df_filtered['WW_Treated_Pct'] = treated_pct.round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_treated = df_filtered["WW_Treated_Pct"].replace(0, pd.NA).dropna()
            
            if len(valid_treated) > 0:
                avg_treated = valid_treated.mean()
                st.metric(
                    label="Wastewater Safely Treated",
                    value=f"{avg_treated:.1f}%",
                    help="% of collected wastewater that is treated - Category: Efficiency & Environmental"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='WW_Treated_Pct', 
                        chart_label="Wastewater Safely Treated",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid wastewater treatment data available")
        else:
            st.warning("Wastewater treatment data not available")

st.markdown("---")
st.markdown("### 🔧 Service Quality")

# KPI 3: Customer Complaint Resolution Rate
df = all_fin_service_df.copy()
if not df.empty and filter_col in df.columns:
    df_filtered = df[df[filter_col].isin(selected_values)]
    
    # Calculate Complaint Resolution Rate
    if 'resolved' in df_filtered.columns and 'complaints' in df_filtered.columns:
        # Vectorized complaint resolution
        resolved = pd.to_numeric(df_filtered.get('resolved', pd.Series(dtype=float)), errors='coerce')
        complaints = pd.to_numeric(df_filtered.get('complaints', pd.Series(dtype=float)), errors='coerce')
        complaint_rate = (resolved / complaints) * 100
        complaint_rate = complaint_rate.replace([np.inf, -np.inf], pd.NA)
        df_filtered['Complaint_Resolution_Rate'] = complaint_rate.round(2)
        
        # Drop NaN and zero values before calculating mean
        valid_resolution = df_filtered["Complaint_Resolution_Rate"].replace(0, pd.NA).dropna()
        
        if len(valid_resolution) > 0:
            avg_resolution = valid_resolution.mean()
            st.metric(
                label="Customer Complaint Resolution Rate",
                value=f"{avg_resolution:.1f}%",
                help="% of customer complaints resolved - Category: Service Quality"
            )
            
            # Chart
            x_col = 'date' if 'date' in df_filtered.columns else 'date_MMYY'
            if x_col in df_filtered.columns:
                plotly_chart_with_labels(
                    df_filtered, 
                    x_col=x_col, 
                    y_col='Complaint_Resolution_Rate', 
                    chart_label="Customer Complaint Resolution Rate",
                    unit="(%)",
                    color_col='country'
                )
        else:
            st.warning("No valid complaint resolution data available")
    else:
        st.warning("Complaint resolution data not available")

st.markdown("---")
st.markdown("### 💩 Fecal Sludge Management")
col3, col4 = st.columns(2)

with col3:
    # KPI 4a: Fecal Sludge Emptied
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate FS Emptied Rate
        if 'hh_emptied' in df_filtered.columns and 'households' in df_filtered.columns and 'sewer_connections' in df_filtered.columns:
            # Vectorized fecal sludge emptied percentage
            hh_emptied = pd.to_numeric(df_filtered.get('hh_emptied', pd.Series(dtype=float)), errors='coerce')
            households = pd.to_numeric(df_filtered.get('households', pd.Series(dtype=float)), errors='coerce')
            sewer_connections = pd.to_numeric(df_filtered.get('sewer_connections', pd.Series(dtype=float)), errors='coerce')
            non_sewered = households - sewer_connections
            fs_emptied_pct = (hh_emptied / non_sewered) * 100
            fs_emptied_pct = fs_emptied_pct.replace([np.inf, -np.inf], pd.NA)
            df_filtered['FS_Emptied_Pct'] = fs_emptied_pct.round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_emptied = df_filtered["FS_Emptied_Pct"].replace(0, pd.NA).dropna()
            
            if len(valid_emptied) > 0:
                avg_emptied = valid_emptied.mean()
                st.metric(
                    label="Fecal Sludge Emptied",
                    value=f"{avg_emptied:.1f}%",
                    help="% of non-sewered households with fecal sludge emptied - Category: Access & Environmental"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='FS_Emptied_Pct', 
                        chart_label="Fecal Sludge Emptied (% of non-sewered HHs)",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid fecal sludge emptying data available")
        else:
            st.warning("Fecal sludge emptying data not available")

with col4:
    # KPI 4b: Fecal Sludge Treated
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate FS Treated Rate
        # Note: We need estimated volume emptied - using hh_emptied as proxy
        if 'fs_treated' in df_filtered.columns and 'hh_emptied' in df_filtered.columns:
            # Assuming average volume per household (this should be adjusted based on actual data)
            avg_volume_per_hh = 2.0  # m3 - adjust as needed
            df_filtered['estimated_volume_emptied'] = pd.to_numeric(df_filtered.get('hh_emptied', pd.Series(dtype=float)), errors='coerce') * avg_volume_per_hh
            fs_treated = pd.to_numeric(df_filtered.get('fs_treated', pd.Series(dtype=float)), errors='coerce')
            estimated_vol = pd.to_numeric(df_filtered.get('estimated_volume_emptied', pd.Series(dtype=float)), errors='coerce')
            fs_treated_pct = (fs_treated / estimated_vol) * 100
            fs_treated_pct = fs_treated_pct.replace([np.inf, -np.inf], pd.NA)
            df_filtered['FS_Treated_Pct'] = fs_treated_pct.round(2)
            
            # Drop NaN and zero values before calculating mean
            valid_treated = df_filtered["FS_Treated_Pct"].replace(0, pd.NA).dropna()
            
            if len(valid_treated) > 0:
                avg_treated = valid_treated.mean()
                st.metric(
                    label="Fecal Sludge Treated",
                    value=f"{avg_treated:.1f}%",
                    help="% of emptied fecal sludge that is treated - Category: Access & Environmental"
                )
                
                # Chart
                x_col = 'date_MMYY' if 'date_MMYY' in df_filtered.columns else 'date'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='FS_Treated_Pct', 
                        chart_label="Fecal Sludge Treated (% of FS emptied)",
                        unit="(%)",
                        color_col='country'
                    )
            else:
                st.warning("No valid fecal sludge treatment data available")
        else:
            st.warning("Fecal sludge treatment data not available")

st.markdown("---")
st.markdown("""
### 📋 Sanitation Service Dashboard Summary
This dashboard provides detailed sanitation service performance metrics:

- **Access**: Sewer coverage showing household connections to sewer network
- **Efficiency & Environmental**: Wastewater treatment rates showing environmental protection
- **Service Quality**: Customer complaint resolution showing service responsiveness
- **Fecal Sludge Management**: Coverage and treatment of fecal sludge from non-sewered households

Use the sidebar to filter by country and explore detailed trends over time.
""")
