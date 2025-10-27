# pages/1_KPI_Overview.py

import streamlit as st
import plotly.express as px
from utils.data_loader import df_districts, df_timeseries, render_sidebar_filters, KPI_TO_PAGE

# Load and filter data using the utility function
filtered_districts, filtered_timeseries = render_sidebar_filters(df_districts)

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

# ---
## 🎯 Core Performance Indicators

# Function to create a KPI card with a button
def kpi_card(col, title, value, delta_value, progress, kpi_key, delta_color="normal"):
    """Renders a Streamlit metric and a button to navigate to the detail page."""
    with col:
        st.metric(
            title,
            value,
            delta_value,
            delta_color=delta_color
        )
        # Use st.page_link to navigate to the dedicated detail page
        st.page_link(
            KPI_TO_PAGE.get(kpi_key),
            label="📊 View Details", 
            use_container_width=True,
            help=f"Navigate to {title} analysis page"
        )
        st.progress(progress)


# Row 1: Access & Coverage
st.subheader("🎯 Core Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

kpi_card(col1, "💧 Water Coverage", f"{kpis['water_coverage']:.1f}%", 
         f"{(kpis['water_coverage'] - 65):+.1f}%", kpis['water_coverage']/100, "WATER_COVERAGE")

# Sanitation and Service Hours (no detail pages yet, so no page_link)
col2.metric("🚽 Sanitation Coverage", f"{kpis['sanitation_coverage']:.1f}%", f"{(kpis['sanitation_coverage'] - 45):+.1f}%")
col2.progress(kpis['sanitation_coverage']/100)

col3.metric("⏰ Service Hours", f"{kpis['service_hours']:.1f} hrs", f"{(kpis['service_hours'] - 12):+.1f} hrs")

col4.metric("😊 Customer Satisfaction", f"{kpis['customer_satisfaction']:.1f}%", f"{(kpis['customer_satisfaction'] - 75):+.1f}%")
col4.progress(kpis['customer_satisfaction']/100)

# ---

# Row 2: Efficiency & Financials
col1, col2, col3, col4 = st.columns(4)

kpi_card(col1, "🚰 Non-Revenue Water", f"{kpis['nrw_pct']:.1f}%", 
         f"{(kpis['nrw_pct'] - 42):+.1f}%", (100 - kpis['nrw_pct'])/100, "NRW", delta_color="inverse")

kpi_card(col2, "💰 Cost Recovery", f"{kpis['occr_pct']:.1f}%", 
         f"{(kpis['occr_pct'] - 95):+.1f}%", kpis['occr_pct']/150, "COST_RECOVERY")

kpi_card(col3, "🔬 Water Quality", f"{kpis['water_quality']:.1f}%", 
         f"{(kpis['water_quality'] - 88):+.1f}%", kpis['water_quality']/100, "WATER_QUALITY")

# Collection Efficiency (no detail page yet)
col4.metric("💵 Collection Efficiency", f"{kpis['collection_efficiency']:.1f}%", f"{(kpis['collection_efficiency'] - 85):+.1f}%")
col4.progress(kpis['collection_efficiency']/100)

# ---
## 💡 Executive Insights

st.subheader("💡 Executive Insights")

col1, col2, col3 = st.columns(3)

with col1:
    if not filtered_districts.empty:
        best_performer = filtered_districts.loc[filtered_districts['water_coverage'].idxmax()]
        st.success(f"**🏆 Best Performer**: {best_performer['district']} "
                    f"({best_performer['water_coverage']:.1f}% coverage)")

with col2:
    if not filtered_districts.empty:
        concern_area = filtered_districts.loc[filtered_districts['nrw_pct'].idxmax()]
        st.warning(f"**⚠️ Needs Attention**: {concern_area['district']} "
                    f"({concern_area['nrw_pct']:.1f}% NRW)")

with col3:
    if not filtered_districts.empty:
        financial_leader = filtered_districts.loc[filtered_districts['occr_pct'].idxmax()]
        st.info(f"**💰 Financial Leader**: {financial_leader['district']} "
                f"({financial_leader['occr_pct']:.1f}% cost recovery)")

# ---
## 📈 Regional Performance Overview

st.subheader("📈 Regional Performance Overview")

fig_performance = px.bar(
    filtered_districts,
    x='district',
    y=['water_coverage', 'nrw_pct', 'occr_pct'],
    title="Key Metrics Comparison Across Districts",
    barmode='group'
)
st.plotly_chart(fig_performance, use_container_width=True)