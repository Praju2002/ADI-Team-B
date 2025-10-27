"""
Detailed Analysis Page
Comprehensive charts and breakdown of budget allocation
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Detailed Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Detailed Budget Analysis")

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
        st.header("🔧 Filters")
        years = sorted(data['date'].unique())
        selected_years = st.multiselect("Select Years", options=years, default=years)
        cities = data['city'].unique()
        selected_cities = st.multiselect("Select Cities", options=cities, default=cities)
    
    filtered_data = data[
        (data['date'].isin(selected_years)) & 
        (data['city'].isin(selected_cities))
    ].copy()
    
    # Calculate statistics
    total_budget = filtered_data['budget_allocated'].sum()
    total_staff = filtered_data['staff_cost'].sum()
    total_san = filtered_data['san_allocation'].sum()
    total_wat = filtered_data['wat_allocation'].sum()
    total_training = filtered_data['staff_training_budget'].sum()
    
    # Category Breakdown
    st.header("📋 Category Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget by Category")
        
        categories = ['Staff Costs', 'SAN Allocation', 'WAT Allocation', 'Staff Training']
        amounts = [total_staff, total_san, total_wat, total_training]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(categories, [a/1e9 for a in amounts], 
                     color=['#ff6b6b', '#45b7d1', '#96ceb4', '#f9ca24'], alpha=0.8)
        ax.set_ylabel('Amount (Billions)')
        ax.set_title('Budget Allocation by Category', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${amount/1e9:.1f}B', ha='center', va='bottom', fontsize=10)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("Percentage Distribution")
        
        percentages = [
            (total_staff / total_budget * 100) if total_budget > 0 else 0,
            (total_san / total_budget * 100) if total_budget > 0 else 0,
            (total_wat / total_budget * 100) if total_budget > 0 else 0,
            (total_training / total_budget * 100) if total_budget > 0 else 0
        ]
        labels = ['Staff', 'SAN', 'WAT', 'Training']
        colors = ['#ff6b6b', '#45b7d1', '#96ceb4', '#f9ca24']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(percentages, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Budget Distribution by Category (%)', fontsize=14, fontweight='bold')
        
        st.pyplot(fig)
        plt.close()
    
    st.divider()
    
    # Yearly Comparison
    st.header("📅 Year-by-Year Comparison")
    
    yearly_data = []
    for year in sorted(filtered_data['date'].unique()):
        year_data = filtered_data[filtered_data['date'] == year]
        yearly_data.append({
            'year': year,
            'total_budget': year_data['budget_allocated'].sum(),
            'staff_costs': year_data['staff_cost'].sum(),
            'san_allocation': year_data['san_allocation'].sum(),
            'wat_allocation': year_data['wat_allocation'].sum()
        })
    
    df_yearly = pd.DataFrame(yearly_data)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df_yearly['year']))
    width = 0.25
    
    bars1 = ax.bar(x - 1.5*width, df_yearly['total_budget']/1e9, width, label='Total Budget', color='lightblue')
    bars2 = ax.bar(x - 0.5*width, df_yearly['staff_costs']/1e9, width, label='Staff Costs', color='red')
    bars3 = ax.bar(x + 0.5*width, df_yearly['san_allocation']/1e9, width, label='SAN', color='#45b7d1')
    bars4 = ax.bar(x + 1.5*width, df_yearly['wat_allocation']/1e9, width, label='WAT', color='#96ceb4')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Amount (Billions)')
    ax.set_title('Budget Categories Over Time', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_yearly['year'])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    plt.close()
    
    # Data table
    st.header("📊 Detailed Data Table")
    st.dataframe(df_yearly, use_container_width=True, hide_index=True)
    
else:
    st.error("Could not load budget data.")
