# pages/2_Water_Coverage_Detail.py

import streamlit as st
import plotly.express as px
from utils.data_loader import df_districts, df_timeseries, render_sidebar_filters

# Load and filter data using the utility function
filtered_districts, filtered_timeseries = render_sidebar_filters(df_districts)
selected_districts = st.session_state.get('selected_districts', [])

st.header("💧 Water Coverage Analysis")

# ---
## Detailed Water Coverage Analysis

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

# ---
## 📈 Coverage Trends Over Time

if len(selected_districts) > 0:
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
else:
    st.warning("Please select at least one district in the sidebar to view trends.")