import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(page_title="Sanitation Service Dashboard", page_icon="🚽", layout="wide")

st.title("🚽 Sanitation Service Dashboard")

# --- Helper Functions ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_csv():
    """Load data from individual CSV files"""
    data = {}
    countries = ['cameroon', 'lesotho', 'malawi', 'uganda']
    base_path = Path('Raw_Data')
    
    # Initialize empty dataframes
    all_fin_service_list = []
    all_national_list = []
    billing_list = []
    production_list = []
    s_access_list = []
    s_service_list = []
    w_access_list = []
    w_service_list = []
    
    for country in countries:
        country_path = base_path / country
        try:
            # Load each file type
            if (country_path / f'all_fin_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f'all_fin_service_{country}.csv')
                df['country'] = country.capitalize()
                all_fin_service_list.append(df)
            
            if (country_path / f'all_nationalacc_{country}.csv').exists():
                df = pd.read_csv(country_path / f'all_nationalacc_{country}.csv')
                df['country'] = country.capitalize()
                all_national_list.append(df)
            
            if (country_path / f'billing_{country}.csv').exists():
                df = pd.read_csv(country_path / f'billing_{country}.csv')
                df['country'] = country.capitalize()
                billing_list.append(df)
            
            if (country_path / f'production_{country}.csv').exists():
                df = pd.read_csv(country_path / f'production_{country}.csv')
                df['country'] = country.capitalize()
                production_list.append(df)
            
            if (country_path / f's_access_{country}.csv').exists():
                df = pd.read_csv(country_path / f's_access_{country}.csv')
                df['country'] = country.capitalize()
                s_access_list.append(df)
            
            if (country_path / f's_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f's_service_{country}.csv')
                df['country'] = country.capitalize()
                s_service_list.append(df)
            
            if (country_path / f'w_access_{country}.csv').exists():
                df = pd.read_csv(country_path / f'w_access_{country}.csv')
                df['country'] = country.capitalize()
                w_access_list.append(df)
            
            if (country_path / f'w_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f'w_service_{country}.csv')
                df['country'] = country.capitalize()
                w_service_list.append(df)
        except Exception as e:
            st.warning(f"Error loading data for {country}: {e}")
    
    # Concatenate all dataframes
    data['all_fin_service'] = pd.concat(all_fin_service_list, ignore_index=True) if all_fin_service_list else pd.DataFrame()
    data['all_national'] = pd.concat(all_national_list, ignore_index=True) if all_national_list else pd.DataFrame()
    data['billing'] = pd.concat(billing_list, ignore_index=True) if billing_list else pd.DataFrame()
    data['production'] = pd.concat(production_list, ignore_index=True) if production_list else pd.DataFrame()
    data['s_access'] = pd.concat(s_access_list, ignore_index=True) if s_access_list else pd.DataFrame()
    data['s_service'] = pd.concat(s_service_list, ignore_index=True) if s_service_list else pd.DataFrame()
    data['w_access'] = pd.concat(w_access_list, ignore_index=True) if w_access_list else pd.DataFrame()
    data['w_service'] = pd.concat(w_service_list, ignore_index=True) if w_service_list else pd.DataFrame()
    
    return data

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

# --- Load Data with Caching ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """Load all data with caching"""
    try:
        # Try loading from Excel first
        if os.path.exists('Raw_Data/Master_Data.xlsx'):
            with st.spinner('Loading data from Excel...'):
                return {
                    'all_fin_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_fin_service'),
                    'all_national': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_national'),
                    'billing': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='billing'),
                    'production': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='production'),
                    's_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_access'),
                    's_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_service'),
                    'w_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_access'),
                    'w_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_service')
                }
        else:
            raise FileNotFoundError("Excel file not found, loading from CSV files")
    except:
        # Load from CSV files
        with st.spinner('Loading data from CSV files...'):
            return load_data_from_csv()

# Load data once with caching
data_dict = load_all_data()
all_fin_service_df = data_dict['all_fin_service']
all_national_df = data_dict['all_national']
billing_df = data_dict['billing']
production_df = data_dict['production']
s_access_df = data_dict['s_access']
s_service_df = data_dict['s_service']
w_access_df = data_dict['w_access']
w_service_df = data_dict['w_service']

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
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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
st.markdown("### 🔧 Service Quality")

# KPI 3: Customer Complaint Resolution Rate
df = all_fin_service_df.copy()
if not df.empty and filter_col in df.columns:
    df_filtered = df[df[filter_col].isin(selected_values)]
    
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
st.markdown("### 💩 Fecal Sludge Management")
col3, col4 = st.columns(2)

with col3:
    # KPI 4a: Fecal Sludge Emptied
    df = s_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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
### 📋 Sanitation Service Dashboard Summary
This dashboard provides detailed sanitation service performance metrics:

- **Access**: Sewer coverage showing household connections to sewer network
- **Efficiency & Environmental**: Wastewater treatment rates showing environmental protection
- **Service Quality**: Customer complaint resolution showing service responsiveness
- **Fecal Sludge Management**: Coverage and treatment of fecal sludge from non-sewered households

Use the sidebar to filter by country and explore detailed trends over time.
""")
