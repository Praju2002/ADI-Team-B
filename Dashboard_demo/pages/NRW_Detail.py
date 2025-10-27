# pages/3_NRW_Detail.py

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import df_districts, df_timeseries, render_sidebar_filters

# Load and filter data
filtered_districts, _ = render_sidebar_filters(df_districts)
selected_districts = st.session_state.get('selected_districts', [])

st.header("🚰 Non-Revenue Water Analysis")

# ---
## Non-Revenue Water Detailed Analysis

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
    fig_nrw.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Good Practice Target")
    st.plotly_chart(fig_nrw, use_container_width=True)

with col2:
    # NRW components simulation
    nrw_components = []
    for district in selected_districts:
        # Check if district is in filtered data before accessing
        if district in filtered_districts['district'].values:
            nrw = filtered_districts[filtered_districts['district'] == district]['nrw_pct'].values[0]
            nrw_components.append({
                'district': district,
                'Physical Losses': nrw * 0.6,
                'Commercial Losses': nrw * 0.3,
                'Unauthorized Consumption': nrw * 0.1
            })
    
    if nrw_components:
        df_components = pd.DataFrame(nrw_components)
        df_melted = df_components.melt(id_vars=['district'], var_name='Component', value_name='Percentage')
        
        fig_components = px.bar(
            df_melted,
            x='district', y='Percentage',
            color='Component',
            title="NRW Components Breakdown (Simulated)",
            barmode='stack'
        )
        st.plotly_chart(fig_components, use_container_width=True)
    else:
        st.info("Select districts to see the NRW components breakdown.")

# ---
## 🎯 NRW Reduction Opportunities

st.subheader("🎯 NRW Reduction Opportunities")

opportunity_data = []
for index, row in filtered_districts.iterrows():
    nrw = row['nrw_pct']
    if nrw > 40:
        opportunity = "High - Urgent Action Needed"
    elif nrw > 30:
        opportunity = "Medium - Improvement Needed" 
    else:
        opportunity = "Low - Good Performance"
        
    opportunity_data.append({
        'district': row['district'],
        'NRW (%)': f"{nrw:.1f}",
        'Opportunity Level': opportunity,
        'Reduction Potential to 25%': max(0, nrw - 25)
    })

df_opportunities = pd.DataFrame(opportunity_data)
st.dataframe(df_opportunities, use_container_width=True, hide_index=True)