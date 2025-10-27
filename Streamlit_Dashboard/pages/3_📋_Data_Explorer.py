"""
Data Explorer Page
Interactive data exploration and filtering
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Data Explorer",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Data Explorer")

@st.cache_data
def load_data():
    """Load budget data from CSV"""
    csv_path = Path("../Data/budget_data.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = df.fillna(0)
        return df
    return None

data = load_data()

if data is not None and not data.empty:
    # Filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        st.subheader("Year Selection")
        years = sorted(data['date'].unique())
        selected_years = st.multiselect(
            "Select Years",
            options=years,
            default=years
        )
        
        st.subheader("City Selection")
        cities = data['city'].unique()
        selected_cities = st.multiselect(
            "Select Cities",
            options=cities,
            default=cities
        )
        
        st.subheader("Column Filters")
        columns_to_show = st.multiselect(
            "Select Columns to Display",
            options=data.columns.tolist(),
            default=data.columns.tolist()
        )
    
    # Filter data
    filtered_data = data[
        (data['date'].isin(selected_years)) & 
        (data['city'].isin(selected_cities))
    ][columns_to_show].copy()
    
    if not filtered_data.empty:
        # Display filtered data
        st.header("📊 Filtered Data")
        
        # Add calculated columns
        filtered_data['staff_percentage'] = (
            filtered_data['staff_cost'] / filtered_data['budget_allocated'] * 100
        ).round(2)
        
        # Format display
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_budget_data.csv',
            mime='text/csv'
        )
        
        st.divider()
        
        # Statistics
        st.header("📈 Data Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_budget = filtered_data['budget_allocated'].sum()
        total_staff = filtered_data['staff_cost'].sum()
        total_san = filtered_data['san_allocation'].sum()
        total_wat = filtered_data['wat_allocation'].sum()
        
        with col1:
            st.metric("Total Budget", f"${total_budget/1e9:.2f}B")
        with col2:
            st.metric("Total Staff Cost", f"${total_staff/1e9:.2f}B")
        with col3:
            st.metric("Total SAN", f"${total_san/1e9:.2f}B")
        with col4:
            st.metric("Total WAT", f"${total_wat/1e9:.2f}B")
        
        st.divider()
        
        # Field-specific statistics
        st.header("🔢 Field Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Budget Allocation Statistics")
            budget_stats = filtered_data['budget_allocated'].describe()
            st.write(budget_stats)
            
            # Convert to billions for display
            budget_stats_display = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
                'Amount (Billions)': [
                    budget_stats['mean']/1e9,
                    budget_stats['std']/1e9,
                    budget_stats['min']/1e9,
                    budget_stats['25%']/1e9,
                    budget_stats['50%']/1e9,
                    budget_stats['75%']/1e9,
                    budget_stats['max']/1e9
                ]
            })
            st.dataframe(budget_stats_display, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("Staff Cost Statistics")
            staff_stats = filtered_data['staff_cost'].describe()
            st.write(staff_stats)
            
            # Convert to billions for display
            staff_stats_display = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
                'Amount (Billions)': [
                    staff_stats['mean']/1e9,
                    staff_stats['std']/1e9,
                    staff_stats['min']/1e9,
                    staff_stats['25%']/1e9,
                    staff_stats['50%']/1e9,
                    staff_stats['75%']/1e9,
                    staff_stats['max']/1e9
                ]
            })
            st.dataframe(staff_stats_display, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Data quality check
        st.header("🔍 Data Quality Check")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(filtered_data))
        with col2:
            null_count = filtered_data.isnull().sum().sum()
            st.metric("Null Values", null_count)
        with col3:
            st.metric("Data Completeness", f"{(1 - null_count/(len(filtered_data)*len(filtered_data.columns)))*100:.1f}%")
        
        st.divider()
        
        # Summary by category
        st.header("📊 Summary by Year")
        
        summary = filtered_data.groupby('date').agg({
            'budget_allocated': 'sum',
            'staff_cost': 'sum',
            'san_allocation': 'sum',
            'wat_allocation': 'sum',
            'staff_training_budget': 'sum'
        }).reset_index()
        
        summary['staff_pct'] = (summary['staff_cost'] / summary['budget_allocated'] * 100).round(2)
        
        st.dataframe(summary, use_container_width=True, hide_index=True)
        
    else:
        st.warning("No data matches the selected filters.")
else:
    st.error("Could not load budget data.")
