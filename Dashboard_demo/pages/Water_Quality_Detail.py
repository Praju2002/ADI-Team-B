# pages/5_Water_Quality_Detail.py

import streamlit as st
import plotly.express as px
from utils.data_loader import df_districts, df_timeseries, render_sidebar_filters

# Load and filter data
filtered_districts, _ = render_sidebar_filters(df_districts)

st.header("🔬 Water Quality Compliance Analysis")

# ---
## Water Quality Performance

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