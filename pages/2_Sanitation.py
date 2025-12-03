import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from pathlib import Path
from utils.floating_button import add_floating_chatbot_button

st.set_page_config(page_title="Sanitation Service Dashboard", layout="wide")

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

st.title(" Sanitation Services")

# Ensure browser resolves Streamlit runtime assets from root when pages are navigated
st.markdown("<base href='/' />", unsafe_allow_html=True)

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
with st.spinner('Loading sanitation data...'):
    all_fin_service_df = load_table('all_fin_service')
    s_service_df = load_table('s_service')

# --- External Filter ---
filter_col = 'country'

st.sidebar.header("Filter Options")

# Build cleaned country list and exclude placeholders like NaN, 'n/a', '<n/a>'
raw_countries = []
if not s_service_df.empty and filter_col in s_service_df.columns:
    raw_countries = list(s_service_df[filter_col].unique())
elif not all_fin_service_df.empty and filter_col in all_fin_service_df.columns:
    raw_countries = list(all_fin_service_df[filter_col].unique())
else:
    raw_countries = ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']

cleaned = []
for c in raw_countries:
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

# Single-select dropdown (first country selected by default)
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

for df in [s_service_df, all_fin_service_df]:
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
        
        if not s_service_df.empty:
            dc = 'date' if 'date' in s_service_df.columns else 'date_MMYY' if 'date_MMYY' in s_service_df.columns else None
            if dc:
                try:
                    s_service_df[dc] = pd.to_datetime(s_service_df[dc], errors='coerce')
                    s_service_df = s_service_df[(s_service_df[dc] >= start) & (s_service_df[dc] <= end)]
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

# KPI 1: Sewer Coverage
st.markdown("###  Access")
col1, col2 = st.columns(2)

with col1:
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate Sewer Coverage
        if 'sewer_connections' in df_filtered.columns and 'households' in df_filtered.columns:
            df_filtered["Sewer_Coverage"] = df_filtered.apply(
                lambda row: (row["sewer_connections"] / row["households"]) * 100
                if pd.notna(row["households"]) and row["households"] != 0 else 0,
                axis=1
            ).round(2)
            
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
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate Wastewater Treatment Rate
        if 'ww_treated' in df_filtered.columns and 'ww_collected' in df_filtered.columns:
            df_filtered["WW_Treated_Pct"] = df_filtered.apply(
                lambda row: (row["ww_treated"] / row["ww_collected"]) * 100
                if pd.notna(row["ww_collected"]) and row["ww_collected"] != 0 else 0,
                axis=1
            ).round(2)
            
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
st.markdown("###  Service Quality")

# KPI 3: Customer Complaint Resolution Rate
df = all_fin_service_df.copy()
if not df.empty and filter_col in df.columns:
    df_filtered = df.copy()
    if selected_country and selected_country != 'No countries found':
        df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
    
    # Calculate Complaint Resolution Rate
    if 'resolved' in df_filtered.columns and 'complaints' in df_filtered.columns:
        df_filtered["Complaint_Resolution_Rate"] = df_filtered.apply(
            lambda row: (row["resolved"] / row["complaints"]) * 100
            if pd.notna(row["complaints"]) and row["complaints"] != 0 else 0,
            axis=1
        ).round(2)
        
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

# ===========================
# NETWORK EFFICIENCY
# ===========================
st.markdown("###  Network Maintenance & Efficiency")
st.caption("Data Availability: Cameroon, Lesotho, Malawi, Uganda")

df_service = all_fin_service_df.copy()
if not df_service.empty and filter_col in df_service.columns:
    df_filtered = df_service.copy()
    if selected_country and selected_country != 'No countries found':
        df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
    
    if 'blocks' in df_filtered.columns and 'sewer_length' in df_filtered.columns:
        # Filter valid data (non-zero, non-null)
        valid_network = df_filtered[
            (df_filtered['blocks'].notna()) &
            (df_filtered['blocks'] > 0) &
            (df_filtered['sewer_length'].notna()) &
            (df_filtered['sewer_length'] > 0)
        ].copy()
        
        if len(valid_network) > 0:
            # Calculate blockages per km (Indicator #29)
            valid_network['blockages_per_km'] = valid_network['blocks'] / valid_network['sewer_length']
            
            avg_blockages = valid_network['blockages_per_km'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                delta_color = "normal" if avg_blockages < 2 else "inverse"
                st.metric(
                    "Blockages per km",
                    f"{avg_blockages:.2f}",
                    delta=f"Target: <2",
                    delta_color=delta_color,
                    help="Indicator #29: Network maintenance efficiency"
                )
            
            with col2:
                total_blocks = valid_network['blocks'].sum()
                st.metric("Total Blockages", f"{total_blocks:,.0f}")
            
            with col3:
                total_length = valid_network['sewer_length'].sum()
                st.metric("Total Sewer Length", f"{total_length:,.1f} km")
            
            # Blockages trend
            if 'date' in valid_network.columns and len(valid_network) > 1:
                blockage_trend = valid_network.groupby('date').agg({
                    'blocks': 'sum',
                    'sewer_length': 'sum'
                }).reset_index()
                
                # Filter out zero length records
                blockage_trend = blockage_trend[blockage_trend['sewer_length'] > 0].copy()
                
                if len(blockage_trend) > 0:
                    blockage_trend['blockages_per_km'] = blockage_trend['blocks'] / blockage_trend['sewer_length']
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=blockage_trend['date'],
                        y=blockage_trend['blockages_per_km'],
                        mode='lines+markers',
                        line=dict(color='#e74c3c', width=2),
                        marker=dict(size=8)
                    ))
                    
                    # Add target line
                    fig.add_hline(y=2, line_dash="dash", line_color="green", annotation_text="Target: 2 blocks/km")
                    
                    fig.update_layout(
                        title="Blockages per km Over Time (Indicator #29)",
                        xaxis_title="Date",
                        yaxis_title="Blockages per km",
                        height=350,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True, key="blockages_trend")
        else:
            st.info("📄 Blockage data not available for selected filters (requires non-zero values)")
    else:
        st.info("📄 Blockages or sewer length columns not found in data")
else:
    st.info("📄 Finance data required for network efficiency calculation")

st.markdown("---")
st.markdown("### Fecal Sludge Management")
col3, col4 = st.columns(2)

with col3:
    # KPI 4a: Fecal Sludge Emptied
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate FS Emptied Rate
        if 'hh_emptied' in df_filtered.columns and 'households' in df_filtered.columns and 'sewer_connections' in df_filtered.columns:
            df_filtered["FS_Emptied_Pct"] = df_filtered.apply(
                lambda row: (row["hh_emptied"] / (row["households"] - row["sewer_connections"])) * 100
                if pd.notna(row["households"]) and pd.notna(row["sewer_connections"]) 
                and (row["households"] - row["sewer_connections"]) > 0 else 0,
                axis=1
            ).round(2)
            
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
        df_filtered = df.copy()
        if selected_country and selected_country != 'No countries found':
            df_filtered = df_filtered[df_filtered[filter_col] == selected_country]
        
        # Calculate FS Treated Rate
        # Note: We need estimated volume emptied - using hh_emptied as proxy
        if 'fs_treated' in df_filtered.columns and 'hh_emptied' in df_filtered.columns:
            # Assuming average volume per household (this should be adjusted based on actual data)
            avg_volume_per_hh = 2.0  # m3 - adjust as needed
            df_filtered['estimated_volume_emptied'] = df_filtered['hh_emptied'] * avg_volume_per_hh
            
            df_filtered["FS_Treated_Pct"] = df_filtered.apply(
                lambda row: (row["fs_treated"] / row["estimated_volume_emptied"]) * 100
                if pd.notna(row["estimated_volume_emptied"]) and row["estimated_volume_emptied"] > 0 else 0,
                axis=1
            ).round(2)
            
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
### Sanitation Service Dashboard Summary
This dashboard provides detailed sanitation service performance metrics:

- **Access**: Sewer coverage showing household connections to sewer network
- **Efficiency & Environmental**: Wastewater treatment rates showing environmental protection
- **Service Quality**: Customer complaint resolution showing service responsiveness
- **Fecal Sludge Management**: Coverage and treatment of fecal sludge from non-sewered households

Use the sidebar to filter by country and explore detailed trends over time.
""")

# Add floating chatbot button
add_floating_chatbot_button()
