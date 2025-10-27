# Home.py

import streamlit as st

# Import the data and utilities
from utils.data_loader import generate_malawi_water_data

# Ensure data is loaded
df_districts, df_timeseries = generate_malawi_water_data()

# Main page content
st.title("🇲🇼 Welcome to the Malawi Water Sector Performance Dashboard")
st.markdown("---")
st.header("An Overview of Key Water and Sanitation Indicators")
st.markdown("""
This application provides a comprehensive, district-level view of the water sector's performance in Malawi, 
focusing on key operational and financial metrics.

**Navigate using the sidebar to explore:**

* **KPI Overview:** See high-level metrics and compare regional performance. (Click '1 KPI Overview' on the left).
* **Detailed Analysis:** Dive deep into specific indicators like Water Coverage, Non-Revenue Water (NRW), and Cost Recovery.

*Note: This dashboard uses simulated data for demonstration purposes.*
""")

st.info("Start by selecting a page from the sidebar to the left.")

# Footer
st.markdown("---")
st.caption("🇲🇼 Malawi Water Sector Performance Dashboard | 📊 Monitoring SDG 6 Progress | 🔢 Simulated Data for Demonstration")