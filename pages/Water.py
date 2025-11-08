import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(page_title="Water Service Dashboard", page_icon="💧", layout="wide")

st.title("💧 Water Service Dashboard")

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
if not w_access_df.empty and filter_col in w_access_df.columns:
    available_countries = sorted(w_access_df[filter_col].unique())
else:
    available_countries = ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']

selected_values = st.sidebar.multiselect(
    f"Select Country/Countries", 
    options=available_countries,
    default=available_countries
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Select countries to filter all water service metrics.")

# --- Main Dashboard ---

# KPI 1: Continuity of Supply
st.markdown("### 🚰 Service Quality")
col1, col2 = st.columns(2)

with col1:
    df = production_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
        # Calculate average - handle NaN values
        if 'service_hours' in df_filtered.columns:
            # Drop NaN values before calculating mean
            valid_data = df_filtered['service_hours'].dropna()
            
            if len(valid_data) > 0:
                avg_value = valid_data.mean()
                st.metric(
                    label="Continuity of Supply",
                    value=f"{avg_value:.1f} hrs/day",
                    help="Average hours of water service per day - Category: Service Quality"
                )
                
                # Chart
                x_col = 'date' if 'date' in df_filtered.columns else 'date_YY'
                if x_col in df_filtered.columns:
                    plotly_chart_with_labels(
                        df_filtered, 
                        x_col=x_col, 
                        y_col='service_hours', 
                        chart_label="Continuity of Supply",
                        unit="(hours/day)",
                        color_col='country'
                    )
            else:
                st.warning("No valid service hours data available for selected countries")
        else:
            st.warning("Service hours data not available in production data")
    else:
        st.warning("Production data not available or missing country column")

with col2:
    # KPI 2: Drinking Water Quality Compliance
    df = w_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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
st.markdown("### 📊 Efficiency & Financial Sustainability")
col3, col4 = st.columns(2)

with col3:
    # KPI 3: Metering Ratio
    df = w_service_df.copy()
    if not df.empty and filter_col in df.columns:
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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
        df_filtered = df[df[filter_col].isin(selected_values)]
        
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

st.markdown("---")
st.markdown("""
### 📋 Water Service Dashboard Summary
This dashboard provides detailed water service performance metrics:

- **Service Quality**: Continuity of supply and drinking water quality compliance
- **Efficiency & Billing**: Metering ratio showing extent of water consumption measurement
- **Financial Sustainability**: Operating cost coverage showing revenue vs operational expenses

Use the sidebar to filter by country and explore detailed trends over time.
""")
