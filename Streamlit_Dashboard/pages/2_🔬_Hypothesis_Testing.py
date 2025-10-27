"""
Hypothesis Testing Page
Statistical verification of the budget allocation hypothesis
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Hypothesis Testing",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Hypothesis Testing & Verification")

st.markdown("""
**Research Hypothesis:**
> Budget allocated and staff cost consume a huge fixed portion, reducing funds available for the rest.
""")

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
    # Calculate overall statistics
    total_budget = data['budget_allocated'].sum()
    total_staff = data['staff_cost'].sum()
    staff_percentage = (total_staff / total_budget * 100) if total_budget > 0 else 0
    
    # Hypothesis verification
    threshold_huge = 40
    threshold_very_huge = 60
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Budget (5 years)", f"${total_budget/1e9:.1f}B")
    with col2:
        st.metric("Staff Costs", f"${total_staff/1e9:.1f}B")
    with col3:
        st.metric("Staff Percentage", f"{staff_percentage:.1f}%")
    
    st.divider()
    
    # Verdict
    st.header("🎯 Hypothesis Verdict")
    
    if staff_percentage >= threshold_very_huge:
        st.error(f"**STRONGLY CONFIRMED**: Staff costs consume {staff_percentage:.1f}% - exceeding {threshold_very_huge}% threshold")
        verdict_color = "red"
    elif staff_percentage >= threshold_huge:
        st.warning(f"**CONFIRMED**: Staff costs consume {staff_percentage:.1f}% - exceeding {threshold_huge}% threshold")
        verdict_color = "orange"
    else:
        st.success(f"**NOT CONFIRMED**: Staff costs consume {staff_percentage:.1f}% - below {threshold_huge}% threshold")
        verdict_color = "green"
    
    st.divider()
    
    # Hypothesis Gauge
    st.header("📊 Hypothesis Verification Gauge")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create gauge chart
    theta = np.linspace(0, np.pi, 100)
    r1 = 1
    
    # Background
    ax.plot(r1 * np.cos(theta), r1 * np.sin(theta), 'k-', linewidth=3)
    
    # Staff cost arc
    staff_theta = np.linspace(0, np.pi * staff_percentage / 100, 50)
    ax.fill_between(r1 * np.cos(staff_theta), 0, r1 * np.sin(staff_theta), 
                   color='red', alpha=0.7, label=f'Staff Costs ({staff_percentage:.1f}%)')
    
    # Other costs arc
    other_theta = np.linspace(np.pi * staff_percentage / 100, np.pi, 50)
    ax.fill_between(r1 * np.cos(other_theta), 0, r1 * np.sin(other_theta), 
                   color='green', alpha=0.7, label=f'Other Costs ({100-staff_percentage:.1f}%)')
    
    # Add threshold lines
    threshold_40_theta = np.pi * 40 / 100
    threshold_60_theta = np.pi * 60 / 100
    
    # Markers
    ax.plot([0, r1 * np.cos(threshold_40_theta)], [0, r1 * np.sin(threshold_40_theta)], 
           'orange', linestyle='--', linewidth=2, alpha=0.7, label='Huge Threshold (40%)')
    ax.plot([0, r1 * np.cos(threshold_60_theta)], [0, r1 * np.sin(threshold_60_theta)], 
           'red', linestyle='--', linewidth=2, alpha=0.7, label='Very Huge Threshold (60%)')
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect('equal')
    ax.set_title('Hypothesis Verification Gauge', fontsize=16, fontweight='bold')
    ax.legend(loc='upper right')
    ax.axis('off')
    
    st.pyplot(fig)
    plt.close()
    
    st.divider()
    
    # Statistical Analysis
    st.header("📊 Statistical Analysis")
    
    yearly_stats = []
    for year in sorted(data['date'].unique()):
        year_data = data[data['date'] == year]
        year_budget = year_data['budget_allocated'].sum()
        year_staff = year_data['staff_cost'].sum()
        year_pct = (year_staff / year_budget * 100) if year_budget > 0 else 0
        
        yearly_stats.append({
            'year': year,
            'staff_percentage': year_pct,
            'budget': year_budget,
            'staff_cost': year_staff
        })
    
    df_stats = pd.DataFrame(yearly_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Yearly Staff Cost Percentage")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df_stats['year'], df_stats['staff_percentage'], 
                     color=['red' if pct >= 40 else 'orange' if pct >= 30 else 'green' 
                           for pct in df_stats['staff_percentage']], alpha=0.7)
        
        ax.axhline(y=40, color='orange', linestyle='--', linewidth=2, label='Huge Threshold')
        ax.axhline(y=60, color='red', linestyle='--', linewidth=2, label='Very Huge Threshold')
        
        ax.set_xlabel('Year')
        ax.set_ylabel('Staff Cost Percentage (%)')
        ax.set_title('Staff Cost Percentage by Year', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=11)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("Budget Efficiency Analysis")
        
        df_stats['remaining_pct'] = 100 - df_stats['staff_percentage']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df_stats['year'], df_stats['remaining_pct'], 
               marker='o', linewidth=3, markersize=10, color='green', label='Remaining Budget %')
        ax.set_xlabel('Year')
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Budget Available for Other Purposes', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 100])
        ax.grid(True, alpha=0.3)
        
        for i, row in df_stats.iterrows():
            ax.text(row['year'], row['remaining_pct'], 
                   f"{row['remaining_pct']:.1f}%", 
                   ha='center', va='bottom', fontsize=10)
        
        st.pyplot(fig)
        plt.close()
    
    st.divider()
    
    # Summary
    st.header("📋 Summary Table")
    df_stats['total_budget_b'] = df_stats['budget'] / 1e9
    df_stats['staff_cost_b'] = df_stats['staff_cost'] / 1e9
    df_stats['available_b'] = (df_stats['budget'] - df_stats['staff_cost']) / 1e9
    
    display_df = df_stats[['year', 'total_budget_b', 'staff_cost_b', 'available_b', 
                          'staff_percentage']].copy()
    display_df.columns = ['Year', 'Total Budget (B)', 'Staff Cost (B)', 
                         'Available Budget (B)', 'Staff %']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Recommendations
    st.header("💡 Recommendations")
    
    if staff_percentage >= 60:
        st.error("**URGENT ACTION REQUIRED**")
        st.markdown("""
        - **Staff costs exceeding 60% is critical**
        - Immediate review of staffing levels and compensation structures
        - Consider staff efficiency improvements
        - Reduce staff costs to free up budget for critical services
        """)
    elif staff_percentage >= 40:
        st.warning("**MONITOR CLOSELY**")
        st.markdown(f"""
        - Staff costs at **{staff_percentage:.1f}%** exceed the 40% threshold
        - Monitor staff cost trends to prevent further escalation
        - Review budget allocation priorities
        - Consider efficiency improvements to optimize staff productivity
        - Explore options to reduce staff costs while maintaining service quality
        """)
    else:
        st.success("**WITHIN ACCEPTABLE RANGES**")
        st.markdown(f"""
        - Staff costs at **{staff_percentage:.1f}%** are within reasonable limits
        - Continue monitoring for cost escalation
        - Maintain current staffing efficiency
        """)
    
else:
    st.error("Could not load budget data.")
