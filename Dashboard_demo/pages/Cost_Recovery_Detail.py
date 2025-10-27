# pages/4_Cost_Recovery_Detail.py

import streamlit as st
import plotly.express as px
from utils.data_loader import df_districts, df_timeseries, render_sidebar_filters

# Load and filter data
filtered_districts, _ = render_sidebar_filters(df_districts)

st.header("💰 Cost Recovery & Financial Sustainability")

# ---
## Financial Health Overview

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
    fig_occr.add_hline(y=120, line_dash="dash", line_color="green", annotation_text="Sustainable Target")
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