import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Malawi Water Sector Performance Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== GENERATE REALISTIC MALAWI DATA =====
def generate_malawi_water_data():
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

# Load data
df_districts, df_timeseries = generate_malawi_water_data()

# ===== SESSION STATE MANAGEMENT =====
if 'current_page' not in st.session_state:
    st.session_state.current_page = "KPI_OVERVIEW"

if 'selected_kpi' not in st.session_state:
    st.session_state.selected_kpi = None

# ===== FILTERS =====
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/d/d1/Flag_of_Malawi.svg", width=80)
st.sidebar.title("Malawi Water Board")

# Navigation
if st.session_state.current_page != "KPI_OVERVIEW":
    if st.sidebar.button("⬅️ Back to KPI Overview"):
        st.session_state.current_page = "KPI_OVERVIEW"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

regions = df_districts['region'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "Select Regions:",
    options=regions,
    default=regions
)

districts = df_districts['district'].unique().tolist()
selected_districts = st.sidebar.multiselect(
    "Select Districts:",
    options=districts,
    default=districts
)

# Filter data
filtered_districts = df_districts[
    df_districts['region'].isin(selected_regions) & 
    df_districts['district'].isin(selected_districts)
]

filtered_timeseries = df_timeseries[
    df_timeseries['district'].isin(selected_districts)
]

# ===== KPI OVERVIEW PAGE =====
def render_kpi_overview():
    st.title("💧 Malawi Water Sector Performance Dashboard")
    st.markdown("### Key Performance Indicators Overview - Real-time Sector Monitoring")
    
    # Calculate KPIs
    kpis = {
        'water_coverage': filtered_districts['water_coverage'].mean(),
        'sanitation_coverage': filtered_districts['sanitation_coverage'].mean(),
        'nrw_pct': filtered_districts['nrw_pct'].mean(),
        'occr_pct': filtered_districts['occr_pct'].mean(),
        'service_hours': filtered_districts['service_hours'].mean(),
        'water_quality': filtered_districts['water_quality_compliance'].mean(),
        'collection_efficiency': filtered_districts['collection_efficiency'].mean(),
        'customer_satisfaction': filtered_districts['customer_satisfaction'].mean()
    }
    
    # KPI CARDS WITH DETAILS BUTTONS
    st.subheader("🎯 Core Performance Indicators")
    
    # Row 1: Access & Coverage
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💧 Water Coverage",
            f"{kpis['water_coverage']:.1f}%",
            f"{(kpis['water_coverage'] - 65):+.1f}%"
        )
        if st.button("📊 View Details", key="water_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "WATER_COVERAGE"
            st.rerun()
        st.progress(kpis['water_coverage']/100)
    
    with col2:
        st.metric(
            "🚽 Sanitation Coverage", 
            f"{kpis['sanitation_coverage']:.1f}%",
            f"{(kpis['sanitation_coverage'] - 45):+.1f}%"
        )
        if st.button("📊 View Details", key="sanitation_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "SANITATION_COVERAGE"
            st.rerun()
        st.progress(kpis['sanitation_coverage']/100)
    
    with col3:
        st.metric(
            "⏰ Service Hours",
            f"{kpis['service_hours']:.1f} hrs",
            f"{(kpis['service_hours'] - 12):+.1f} hrs"
        )
        if st.button("📊 View Details", key="service_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "SERVICE_HOURS"
            st.rerun()
    
    with col4:
        st.metric(
            "😊 Customer Satisfaction",
            f"{kpis['customer_satisfaction']:.1f}%",
            f"{(kpis['customer_satisfaction'] - 75):+.1f}%"
        )
        if st.button("📊 View Details", key="satisfaction_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "CUSTOMER_SATISFACTION"
            st.rerun()
        st.progress(kpis['customer_satisfaction']/100)
    
    # Row 2: Efficiency & Financials
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🚰 Non-Revenue Water",
            f"{kpis['nrw_pct']:.1f}%",
            f"{(kpis['nrw_pct'] - 42):+.1f}%",
            delta_color="inverse"
        )
        if st.button("📊 View Details", key="nrw_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "NRW"
            st.rerun()
        st.progress((100 - kpis['nrw_pct'])/100)
    
    with col2:
        st.metric(
            "💰 Cost Recovery",
            f"{kpis['occr_pct']:.1f}%",
            f"{(kpis['occr_pct'] - 95):+.1f}%"
        )
        if st.button("📊 View Details", key="occr_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "COST_RECOVERY"
            st.rerun()
        st.progress(kpis['occr_pct']/150)
    
    with col3:
        st.metric(
            "🔬 Water Quality",
            f"{kpis['water_quality']:.1f}%",
            f"{(kpis['water_quality'] - 88):+.1f}%"
        )
        if st.button("📊 View Details", key="quality_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "WATER_QUALITY"
            st.rerun()
        st.progress(kpis['water_quality']/100)
    
    with col4:
        st.metric(
            "💵 Collection Efficiency",
            f"{kpis['collection_efficiency']:.1f}%",
            f"{(kpis['collection_efficiency'] - 85):+.1f}%"
        )
        if st.button("📊 View Details", key="collection_details", use_container_width=True):
            st.session_state.current_page = "DETAIL_PAGE"
            st.session_state.selected_kpi = "COLLECTION_EFFICIENCY"
            st.rerun()
        st.progress(kpis['collection_efficiency']/100)
    
    # QUICK INSIGHTS
    st.subheader("💡 Executive Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_performer = filtered_districts.loc[filtered_districts['water_coverage'].idxmax()]
        st.success(f"**🏆 Best Performer**: {best_performer['district']} "
                  f"({best_performer['water_coverage']}% coverage)")
    
    with col2:
        concern_area = filtered_districts.loc[filtered_districts['nrw_pct'].idxmax()]
        st.warning(f"**⚠️ Needs Attention**: {concern_area['district']} "
                  f"({concern_area['nrw_pct']}% NRW)")
    
    with col3:
        financial_leader = filtered_districts.loc[filtered_districts['occr_pct'].idxmax()]
        st.info(f"**💰 Financial Leader**: {financial_leader['district']} "
               f"({financial_leader['occr_pct']}% cost recovery)")
    
    # PERFORMANCE OVERVIEW CHART
    st.subheader("📈 Regional Performance Overview")
    
    fig_performance = px.bar(
        filtered_districts,
        x='district',
        y=['water_coverage', 'nrw_pct', 'occr_pct'],
        title="Key Metrics Comparison Across Districts",
        barmode='group'
    )
    st.plotly_chart(fig_performance, use_container_width=True)

# ===== DETAIL PAGES =====
def render_detail_page():
    kpi = st.session_state.selected_kpi
    
    # KPI Title Mapping
    kpi_titles = {
        "WATER_COVERAGE": "💧 Water Coverage Analysis",
        "SANITATION_COVERAGE": "🚽 Sanitation Coverage Analysis", 
        "SERVICE_HOURS": "⏰ Service Hours & Reliability",
        "CUSTOMER_SATISFACTION": "😊 Customer Satisfaction Analysis",
        "NRW": "🚰 Non-Revenue Water Analysis",
        "COST_RECOVERY": "💰 Cost Recovery & Financial Sustainability",
        "WATER_QUALITY": "🔬 Water Quality Compliance",
        "COLLECTION_EFFICIENCY": "💵 Revenue Collection Efficiency"
    }
    
    st.header(kpi_titles.get(kpi, "Detailed Analysis"))
    
    if kpi == "WATER_COVERAGE":
        render_water_coverage_details()
    elif kpi == "NRW":
        render_nrw_details()
    elif kpi == "COST_RECOVERY":
        render_cost_recovery_details()
    elif kpi == "WATER_QUALITY":
        render_water_quality_details()
    # Add other KPI detail pages as needed

def render_water_coverage_details():
    st.markdown("### Detailed Water Coverage Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Coverage by district
        fig_coverage = px.bar(
            filtered_districts.sort_values('water_coverage', ascending=False),
            x='district', y='water_coverage',
            title="Water Coverage by District (%)",
            color='water_coverage',
            color_continuous_scale='Blues'
        )
        fig_coverage.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="SDG Target")
        st.plotly_chart(fig_coverage, use_container_width=True)
    
    with col2:
        # Regional comparison
        regional_avg = filtered_districts.groupby('region')['water_coverage'].mean().reset_index()
        fig_regional = px.pie(
            regional_avg,
            values='water_coverage',
            names='region',
            title="Water Coverage Distribution by Region"
        )
        st.plotly_chart(fig_regional, use_container_width=True)
    
    # Time trend
    st.subheader("📈 Coverage Trends Over Time")
    
    if len(selected_districts) <= 4:
        fig_trend = px.line(
            filtered_timeseries,
            x='date', y='water_coverage',
            color='district',
            title="Water Coverage Trend Over Time",
            labels={'water_coverage': 'Coverage (%)'}
        )
        fig_trend.add_hline(y=80, line_dash="dash", line_color="green")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Select 1-4 districts to view trend analysis")

def render_nrw_details():
    st.markdown("### Non-Revenue Water Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # NRW by district
        fig_nrw = px.bar(
            filtered_districts.sort_values('nrw_pct'),
            x='district', y='nrw_pct',
            title="Non-Revenue Water by District (%)",
            color='nrw_pct',
            color_continuous_scale='RdYlGn_r'
        )
        fig_nrw.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Good Practice")
        st.plotly_chart(fig_nrw, use_container_width=True)
    
    with col2:
        # NRW components simulation
        nrw_components = []
        for district in selected_districts:
            nrw = filtered_districts[filtered_districts['district'] == district]['nrw_pct'].values[0]
            nrw_components.append({
                'district': district,
                'Physical Losses': nrw * 0.6,
                'Commercial Losses': nrw * 0.3,
                'Unauthorized Consumption': nrw * 0.1
            })
        
        df_components = pd.DataFrame(nrw_components)
        df_melted = df_components.melt(id_vars=['district'], var_name='Component', value_name='Percentage')
        
        fig_components = px.bar(
            df_melted,
            x='district', y='Percentage',
            color='Component',
            title="NRW Components Breakdown",
            barmode='stack'
        )
        st.plotly_chart(fig_components, use_container_width=True)
    
    # NRW Reduction Opportunities
    st.subheader("🎯 NRW Reduction Opportunities")
    
    opportunity_data = []
    for district in selected_districts:
        nrw = filtered_districts[filtered_districts['district'] == district]['nrw_pct'].values[0]
        if nrw > 40:
            opportunity = "High - Urgent Action Needed"
        elif nrw > 30:
            opportunity = "Medium - Improvement Needed" 
        else:
            opportunity = "Low - Good Performance"
            
        opportunity_data.append({
            'district': district,
            'nrw_pct': nrw,
            'opportunity_level': opportunity,
            'reduction_potential': max(0, nrw - 25)
        })
    
    df_opportunities = pd.DataFrame(opportunity_data)
    st.dataframe(df_opportunities, use_container_width=True)

def render_cost_recovery_details():
    st.markdown("### Cost Recovery & Financial Sustainability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost recovery by district
        fig_occr = px.bar(
            filtered_districts.sort_values('occr_pct'),
            x='district', y='occr_pct',
            title="O&M Cost Coverage Ratio (%)",
            color='occr_pct',
            color_continuous_scale='RdYlGn'
        )
        fig_occr.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Break-even")
        fig_occr.add_hline(y=120, line_dash="dash", line_color="green", annotation_text="Sustainable")
        st.plotly_chart(fig_occr, use_container_width=True)
    
    with col2:
        # Financial health matrix
        fig_matrix = px.scatter(
            filtered_districts,
            x='occr_pct',
            y='collection_efficiency',
            size='water_coverage',
            color='region',
            hover_name='district',
            title="Financial Health Matrix",
            labels={'occr_pct': 'Cost Recovery (%)', 'collection_efficiency': 'Collection Efficiency (%)'}
        )
        fig_matrix.add_hline(y=95, line_dash="dash", line_color="green")
        fig_matrix.add_vline(x=100, line_dash="dash", line_color="orange")
        st.plotly_chart(fig_matrix, use_container_width=True)

def render_water_quality_details():
    st.markdown("### Water Quality Compliance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality compliance by district
        fig_quality = px.bar(
            filtered_districts.sort_values('water_quality_compliance', ascending=False),
            x='district', y='water_quality_compliance',
            title="Water Quality Compliance (%)",
            color='water_quality_compliance',
            color_continuous_scale='RdYlGn'
        )
        fig_quality.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="National Standard")
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Quality vs Service correlation
        fig_correlation = px.scatter(
            filtered_districts,
            x='service_hours',
            y='water_quality_compliance',
            size='customer_satisfaction',
            color='region',
            hover_name='district',
            title="Service Hours vs Water Quality",
            labels={'service_hours': 'Daily Service Hours', 'water_quality_compliance': 'Quality Compliance (%)'}
        )
        st.plotly_chart(fig_correlation, use_container_width=True)

# ===== MAIN APP LOGIC =====
if st.session_state.current_page == "KPI_OVERVIEW":
    render_kpi_overview()
elif st.session_state.current_page == "DETAIL_PAGE":
    render_detail_page()

# ===== FOOTER =====
st.markdown("---")
st.caption("🇲🇼 Malawi Water Sector Performance Dashboard | "
          "📊 Monitoring SDG 6 Progress | "
          "🔢 Simulated Data for Demonstration")