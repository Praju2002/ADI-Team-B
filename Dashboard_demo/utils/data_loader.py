# utils/data_loader.py

import streamlit as st
import pandas as pd
import numpy as np

# Set page config (can be here or in main/home file)
st.set_page_config(
    page_title="Malawi Water Sector Performance Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== GENERATE REALISTIC MALAWI DATA (REUSED) =====
@st.cache_data
def generate_malawi_water_data():
    """Generates and caches realistic, simulated Malawi water sector data."""
    regions = ['Northern Region', 'Central Region', 'Southern Region']
    districts = [
        'Blantyre', 'Lilongwe', 'Mzuzu', 'Zomba', 'Kasungu', 'Mangochi', 
        'Salima', 'Karonga', 'Mzimba', 'Balaka', 'Mulanje', 'Thyolo'
    ]
    
    np.random.seed(42)
    district_data = []
    
    for district in districts:
        if district in ['Mzuzu', 'Karonga', 'Mzimba']:
            region = 'Northern Region'
        elif district in ['Lilongwe', 'Kasungu', 'Salima']:
            region = 'Central Region'
        else:
            region = 'Southern Region'
            
        district_data.append({
            'region': region,
            'district': district,
            'water_coverage': np.random.randint(55, 85),
            'sanitation_coverage': np.random.randint(25, 65),
            'nrw_pct': np.random.randint(35, 70),
            'occr_pct': np.random.randint(45, 110),
            'service_hours': np.random.randint(6, 18),
            'collection_efficiency': np.random.randint(65, 95),
            'water_quality_compliance': np.random.randint(70, 98),
            'staff_productivity': np.random.randint(4, 15),
            'metering_ratio': np.random.randint(50, 90),
            'pro_poor_connections': np.random.randint(15, 40),
            'customer_satisfaction': np.random.randint(60, 90),
            'utility_size': np.random.choice(['Small', 'Medium', 'Large'], p=[0.4, 0.4, 0.2])
        })
    
    df_districts = pd.DataFrame(district_data)
    
    # Time series data
    dates = pd.date_range(start='2021-01-01', end='2024-03-01', freq='M')
    time_series_data = []
    
    for date in dates:
        for district in districts:
            base_data = df_districts[df_districts['district'] == district].iloc[0]
            progress_factor = (date.year - 2021) * 0.1
            
            time_series_data.append({
                'date': date,
                'district': district,
                'region': base_data['region'],
                'water_coverage': min(95, base_data['water_coverage'] + progress_factor * 10 + np.random.randint(-2, 3)),
                'nrw_pct': max(20, base_data['nrw_pct'] - progress_factor * 8 + np.random.randint(-3, 4)),
                'occr_pct': min(120, base_data['occr_pct'] + progress_factor * 12 + np.random.randint(-5, 6)),
                'water_quality_compliance': min(100, base_data['water_quality_compliance'] + progress_factor * 5 + np.random.randint(-2, 3)),
                'production_volume': np.random.randint(50000, 300000),
                'revenue_collected': np.random.randint(2000000, 8000000),
            })
    
    df_timeseries = pd.DataFrame(time_series_data)
    return df_districts, df_timeseries

# Load data once
df_districts, df_timeseries = generate_malawi_water_data()

# Dictionary to map KPI to its detail page file name
KPI_TO_PAGE = {
    "WATER_COVERAGE": "pages/Water_Coverage_Detail.py",
    "NRW": "pages/NRW_Detail.py",
    "COST_RECOVERY": "pages/Cost_Recovery_Detail.py",
    "WATER_QUALITY": "pages/Water_Quality_Detail.py",
    # Add other KPIs as needed
}

def render_sidebar_filters(df_districts):
    """Renders the standard sidebar filters and applies them to the dataframes."""
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/d/d1/Flag_of_Malawi.svg", width=80)
    st.sidebar.title("Malawi Water Board")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")

    # Region Filter
    regions = df_districts['region'].unique().tolist()
    selected_regions = st.sidebar.multiselect(
        "Select Regions:",
        options=regions,
        default=regions
    )

    # District Filter
    districts = df_districts['district'].unique().tolist()
    selected_districts = st.sidebar.multiselect(
        "Select Districts:",
        options=districts,
        default=districts
    )
    
    st.session_state['selected_regions'] = selected_regions
    st.session_state['selected_districts'] = selected_districts
    
    # Filter data
    filtered_districts = df_districts[
        df_districts['region'].isin(selected_regions) & 
        df_districts['district'].isin(selected_districts)
    ]
    
    filtered_timeseries = df_timeseries[
        df_timeseries['district'].isin(selected_districts)
    ]
    
    return filtered_districts, filtered_timeseries