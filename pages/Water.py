import streamlit as st
import pandas as pd
import plotly.express as px

st.write("Water Service Dashboard")

# --- Chart Function ---
def plotly_chart_with_labels(df, x_col, y_col, chart_label, flag=0):
    st.subheader(chart_label)

    # Average y-axis by x-axis
    df_avg = df.groupby(x_col, as_index=False)[y_col].mean().round(0)

    # Plot chart
    fig = px.scatter(df_avg, x=x_col, y=y_col, text=y_col, title=f"Average {y_col} by {x_col}")
    fig.update_traces(textposition='top center')

    # Layout
    fig.update_layout(
        title_x=0.5,
        xaxis_title=x_col,
        yaxis_title=f"Average {y_col}",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

all_fin_service_df = pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_fin_service')
all_national_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='all_national')
# billing_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='billing')
production_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='production')
s_access_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='s_access')
s_service_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='s_service')
w_access_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='w_access')
w_service_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='w_service')


# --- External Filter ---
filter_col = 'country'  # You define this in code

st.sidebar.header("Filter Country")
selected_values = st.sidebar.multiselect(
    f"Select {filter_col}(s)", 
    options=w_access_df[filter_col].unique(),
    default=w_access_df[filter_col].unique()
    )


# KPI 1
df = w_access_df
df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
plotly_chart_with_labels(df_filtered, x_col='date_YY', y_col='safely_managed_pct', chart_label="Population with Safely Managed Water")
