"""
Malawi Budget Analysis - Multi-page Streamlit Dashboard
Main entry point for the interactive dashboard
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Malawi Budget Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #ff6b6b;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Malawi Budget Analysis Dashboard")
st.markdown("**Hypothesis Verification:** Staff costs consume a huge portion of the budget")

# Load data
@st.cache_data
def load_data():
    """Load budget data from CSV"""
    import pandas as pd
    from pathlib import Path
    
    csv_path = Path("../Data/budget_data.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = df.fillna(0)
        return df
    return None

# Load data
data = load_data()

if data is not None and not data.empty:
    # Sidebar
    with st.sidebar:
        st.header("🔧 Filters")
        
        years = sorted(data['date'].unique())
        selected_years = st.multiselect(
            "Select Years",
            options=years,
            default=years
        )
        
        cities = data['city'].unique()
        selected_cities = st.multiselect(
            "Select Cities",
            options=cities,
            default=cities
        )
    
    # Filter data
    filtered_data = data[
        (data['date'].isin(selected_years)) & 
        (data['city'].isin(selected_cities))
    ].copy()
    
    if not filtered_data.empty:
        # Calculate statistics
        total_budget = filtered_data['budget_allocated'].sum()
        total_staff = filtered_data['staff_cost'].sum()
        staff_percentage = (total_staff / total_budget * 100) if total_budget > 0 else 0
        remaining_budget = total_budget - total_staff
        
        # Main metrics
        st.header("📈 Overview Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Budget",
                value=f"${total_budget/1e9:.1f}B",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Staff Costs",
                value=f"${total_staff/1e9:.1f}B",
                delta=f"{staff_percentage:.1f}% of total"
            )
        
        with col3:
            st.metric(
                label="Remaining Budget",
                value=f"${remaining_budget/1e9:.1f}B",
                delta=f"{100-staff_percentage:.1f}% of total"
            )
        
        with col4:
            # Hypothesis verdict
            if staff_percentage >= 60:
                verdict = "🔴 STRONGLY CONFIRMED"
                color = "red"
            elif staff_percentage >= 40:
                verdict = "🟠 CONFIRMED"
                color = "orange"
            else:
                verdict = "🟢 NOT CONFIRMED"
                color = "green"
            
            st.markdown(f'<p style="color: {color}; font-size: 20px; font-weight: bold;">{verdict}</p>', 
                       unsafe_allow_html=True)
            st.metric("Staff %", f"{staff_percentage:.1f}%")
        
        st.divider()
        
        # Navigation
        st.markdown("### 📚 Navigate to Different Pages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **📊 Overview** (Current page)
            - **📈 Detailed Analysis** (Streamlit Dashboard → pages → detailed_analysis.py)
            - **🔬 Hypothesis Testing** (Streamlit Dashboard → pages → hypothesis_testing.py)
            - **📋 Data Explorer** (Streamlit Dashboard → pages → data_explorer.py)
            """)
        
        with col2:
            st.info("""
            **Use the sidebar to filter:**
            - Select specific years
            - Choose cities to analyze
            - Watch real-time updates
            """)
        
        st.divider()
        
        # Quick chart
        st.header("📊 Quick Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Budget Allocation")
            
            # Pie chart
            import matplotlib.pyplot as plt
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            
            categories = ['Staff Costs', 'Other Costs']
            sizes = [total_staff, remaining_budget]
            colors = ['#ff6b6b', '#4ecdc4']
            
            wedges, texts, autotexts = ax1.pie(sizes, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax1.set_title('Budget Allocation Breakdown', fontsize=14, fontweight='bold')
            
            st.pyplot(fig1)
            plt.close()
        
        with col2:
            st.subheader("Yearly Trend")
            
            # Line chart
            yearly_stats = filtered_data.groupby('date').agg({
                'budget_allocated': 'sum',
                'staff_cost': 'sum'
            }).reset_index()
            yearly_stats['staff_percentage'] = (yearly_stats['staff_cost'] / yearly_stats['budget_allocated'] * 100)
            
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.plot(yearly_stats['date'], yearly_stats['staff_percentage'], 
                    marker='o', linewidth=3, markersize=10, color='#ff6b6b', label='Staff %')
            ax2.axhline(y=40, color='orange', linestyle='--', alpha=0.7, label='Huge Threshold (40%)')
            ax2.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='Very Huge Threshold (60%)')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Staff Cost Percentage (%)')
            ax2.set_title('Staff Cost Trend Over Time', fontsize=14, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            st.pyplot(fig2)
            plt.close()
    
    else:
        st.warning("No data available for selected filters. Please adjust your selection.")
else:
    st.error("❌ Could not load budget data. Please ensure the CSV file exists in Data/budget_data.csv")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Malawi Budget Analysis Dashboard | Powered by Streamlit</p>
    <p>Navigate to different pages from the sidebar or use the navigation links above</p>
</div>
""", unsafe_allow_html=True)
