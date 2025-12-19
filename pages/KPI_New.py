import streamlit as st
import pandas as pd
import calendar
import plotly.express as px

st.write("Summary")

def clean_date(df, date_col):
    df = df.copy()
    # # Auto convert date
    # df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # ---- Fix your year-to-datetime issue ----
    # --- Safe datetime conversion for mixed cases ---
    if df[date_col].dtype == "int64":
        # only year → make it YYYY-01-01
        df[date_col] = pd.to_datetime(df[date_col].astype(str), format="%Y", errors="coerce")

    else:
        # covers: strings like "2020-01-01 00:00:00", "2020-01", etc.
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # normalize all datetimes
    df[date_col] = df[date_col].dt.normalize()

    # # Auto convert numeric column
    # df[sum_col] = pd.to_numeric(df[sum_col], errors="coerce")
    return df

def group_and_sum(df, new_col_name, date_col, group_cols, granularity, sum_col):
    """
    Group a dataframe by a date granularity + other columns and sum a value column.

    Parameters:
    df (pd.DataFrame): Input dataframe.
    new_col_name (str): The name of the new summed column to create.
    date_col (str): Name of the date column.
    group_cols (list): Other columns to group by.
    granularity (str): 'day', 'month', or 'year'.
    sum_col (str): The column whose values will be summed.

    Returns:
    pd.DataFrame: Grouped + summed dataframe.
    """

    df = df.copy()

    # Ensure date column is datetime
    df[date_col] = pd.to_datetime(df[date_col])

    # Create grouped date column
    if granularity == "month":
        df["grouped_date"] = df[date_col].dt.to_period("M").dt.to_timestamp()
    elif granularity == "day":
        df["grouped_date"] = df[date_col].dt.date
    elif granularity == "year":
        df["grouped_date"] = df[date_col].dt.to_period("Y").dt.to_timestamp()
    else:
        raise ValueError("Granularity must be 'day', 'month', or 'year'.")

    # Group and sum
    grouped_df = (
        df.groupby(["grouped_date"] + group_cols)[sum_col]
          .sum()
          .reset_index()
          .rename(columns={sum_col: new_col_name})
    )

    return grouped_df


def simple_group_and_sum(df, group_cols, sum_cols):
    """
    Groups the dataframe by `group_cols` and sums only the columns in `sum_cols`.
    Drops all other columns except `group_cols`.
    
    Parameters:
        df (pd.DataFrame): Input dataframe
        group_cols (list): Columns to group by
        sum_cols (list): Columns to sum
    
    Returns:
        pd.DataFrame: Grouped and summed dataframe
    """
    df = df.copy()
    
    # Keep only group columns + columns to sum
    cols_to_keep = group_cols + sum_cols
    df = df[cols_to_keep]
    
    # Group and sum specified columns
    grouped_df = df.groupby(group_cols, as_index=False)[sum_cols].sum()
    
    return grouped_df

def kpi_rate_calc(df, kpi_name, col1, col2, flag=0):
    df = df.copy()
    tooltip = "Tool "+kpi_name
    kpi_name = kpi_name + " Rate"
    if flag==0:
        df[kpi_name] = ((df[col1] - df[col2]) * 100) / df[col1]
        df[tooltip] = (df[col1] - df[col2])
    elif flag==1:
        df[kpi_name] = (df[col1] * 100) / df[col2]
        df[tooltip] = df[col1]
    elif flag==2:
        df[kpi_name] = (df[col1]) / df[col2]
        df[tooltip] = df[col1]
    
    return df

def clean_country_city_zone_source(df):
    try:
        if 'country' in df.columns:
            df['country'] = df['country'].str.title()
        if 'city' in df.columns:
            df['city'] = df['city'].str.title()
        if 'zone' in df.columns:
            df['zone'] = df['zone'].str.title()
        if 'source' in df.columns:
            df['source'] = df['source'].str.title()
    except Exception as e:
        print(f"An error occurred: {e}")
        pass

def add_city_column_if_missing(df, city_zone_mapping_df):
    if 'city' not in df.columns and 'zone' in df.columns:
        merged_df = df.merge(city_zone_mapping_df[['zone', 'city']], on='zone', how='left')
        df['city'] = merged_df['city']
        df['city'] = df['city'].fillna('Unknown City')
        # print("City column added to df.")
    else:
        pass
        # print("City column already exists, skipping city-zone merge for df.")
    # display(df[:1])


# --- Chart Function ---
# def plotly_chart_with_labels(df, x_col, y_col, chart_label, flag=0):
#     st.subheader(chart_label)
#     # Avg. y-axis by x-axis
#     df_avg = df.groupby(x_col, as_index=False)[y_col].mean().round(0)
#     # Plot chart (line + markers + text labels)
#     fig = px.line(
#         df_avg,
#         x=x_col,
#         y=y_col,
#         title=f"Avg. {y_col} by {x_col}",
#         markers=True
#     )
#     # Add text labels for each point
#     fig.update_traces(
#         text=df_avg[y_col],
#         textposition='top center',
#         mode='lines+markers+text'
#     )
#     # Layout
#     fig.update_layout(
#         title_x=0.5,
#         xaxis_title=x_col,
#         yaxis_title=f"Avg. {y_col}",
#         template="plotly_white"
#     )
#     st.plotly_chart(fig, use_container_width=True)

# def plotly_chart_with_labels(df, x_col, y_col, chart_label):

#     # ---- UNIQUE STATE PREFIX PER CHART ----
#     prefix = chart_label.replace(" ", "_").lower()

#     level_key   = f"{prefix}_drill_level"
#     year_key    = f"{prefix}_selected_year"
#     month_key   = f"{prefix}_selected_month"

#     ss = st.session_state
#     ss.setdefault(level_key, "year")
#     ss.setdefault(year_key, None)
#     ss.setdefault(month_key, None)

#     level = ss[level_key]

#     print(chart_label)
#     print(df[x_col].unique())

#     # ---- Detect granularity ----
#     has_month = df[x_col].dt.month.nunique() > 1
#     has_day   = df[x_col].dt.day.nunique() > 1

#     st.subheader(chart_label)

#     # ---- Breadcrumbs ----
#     crumbs = ["Year"]
#     if level in ["month", "day"]:
#         crumbs.append(str(ss[year_key]))
#     if level == "day":
#         crumbs.append(str(ss[month_key]))

#     st.markdown(" > ".join([f"**{c}**" for c in crumbs]))
#     st.write("Hover • Click to drill down")

#     # ---- LEVEL: YEAR ----
#     if level == "year":
#         df_plot = df.copy()
#         df_plot["Year"] = df_plot[x_col].dt.year
#         df_plot = df_plot.groupby("Year")[y_col].mean().reset_index().round(0)
#         xfield = "Year"

#     # ---- LEVEL: MONTH ----
#     # elif level == "month":
#     #     df_plot = df[df[x_col].dt.year == ss[year_key]].copy()
#     #     # df_plot["Month"] = df_plot[x_col].dt.month
#     # #     df_plot = df_plot.groupby("Month")[y_col].mean().reset_index().round(0)
#     # #     df_plot["Month"] = df_plot["Month"].astype(str)
#     # #     xfield = "Month"
#     #     df_plot["MonthNum"] = df_plot[x_col].dt.month
#     #     df_plot = df_plot.groupby("MonthNum")[y_col].mean().reset_index().round(0)

#     #     # Add month name (Jan, Feb,…)
#     #     df_plot["Month"] = df_plot["MonthNum"].dt.month_name().str[:3]   # Jan, Feb, Mar

#     #     # Sort by numeric month
#     #     df_plot = df_plot.sort_values("MonthNum")
#     #     xfield = "Month"

#     elif level == "month":
#         df_plot = df[df[x_col].dt.year == ss[year_key]].copy()

#         # Extract numeric month
#         df_plot["MonthNum"] = df_plot[x_col].dt.month

#         # Aggregate
#         df_plot = df_plot.groupby("MonthNum")[y_col].mean().reset_index().round(0)

#         # Convert month number → Jan, Feb, Mar...
#         df_plot["Month"] = df_plot["MonthNum"].apply(
#             lambda m: calendar.month_abbr[m]
#         )

#         # Ensure months sorted correctly
#         df_plot = df_plot.sort_values("MonthNum")

#         xfield = "Month"

#     # ---- LEVEL: DAY ----
#     elif level == "day":
#         df_plot = df[
#             (df[x_col].dt.year == ss[year_key]) &
#             (df[x_col].dt.month == int(ss[month_key]))
#         ].copy()
#         df_plot["Day"] = df_plot[x_col].dt.day
#         df_plot = df_plot.groupby("Day")[y_col].mean().reset_index().round(0)
#         xfield = "Day"

#     # ---- PLOT ----
#     fig = px.line(
#         df_plot, x=xfield, y=y_col, markers=True, title=chart_label
#     )
#     fig.update_traces(
#         mode="lines+markers+text",
#         text=df_plot[y_col],
#         textposition="top center"
#     )
#     fig.update_layout(
#         transition_duration=400,
#         hovermode="closest",
#         template="plotly_white",
#         title_x=0.5
#     )

#     # unique widget key
#     plot_key = f"plot_{prefix}_{level}"

#     event = st.plotly_chart(
#         fig,
#         use_container_width=True,
#         on_select="rerun",
#         key=plot_key
#     )

#     # ---- DRILL DOWN ----
#     if event.selection and len(event.selection.points) > 0:
#         sel = event.selection.points[0]["x"]

#         if level == "year" and has_month:
#             ss[year_key] = int(sel)
#             ss[level_key] = "month"
#             st.rerun()

#         elif level == "month" and has_day:
#             ss[month_key] = sel
#             ss[level_key] = "day"
#             st.rerun()

#     # ---- BACK BUTTON ----
#     cols = st.columns([1, 1, 5])
#     if level in ["month", "day"]:
#         if cols[0].button("⬅ Back", key=f"back_{prefix}_{level}"):

#             if level == "day":
#                 ss[level_key] = "month"
#                 ss[month_key] = None
#             else:
#                 ss[level_key] = "year"
#                 ss[year_key] = None

#             st.rerun()


def plotly_chart_with_labels(df, x_col, y_col, chart_label, tooltip_cols=None):
    tooltip_cols = tooltip_cols or []

    # ---- UNIQUE STATE PREFIX ----
    prefix = chart_label.replace(" ", "_").lower()
    level_key   = f"{prefix}_drill_level"
    year_key    = f"{prefix}_selected_year"
    month_key   = f"{prefix}_selected_month"

    ss = st.session_state
    ss.setdefault(level_key, "year")
    ss.setdefault(year_key, None)
    ss.setdefault(month_key, None)

    level = ss[level_key]

    st.subheader(chart_label)

    # ---- Detect available granularity ----
    has_month = df[x_col].dt.month.nunique() > 1
    has_day   = df[x_col].dt.day.nunique() > 1

    # ---- Breadcrumbs ----
    crumbs = ["Year"]
    if level in ["month", "day"]:
        crumbs.append(str(ss[year_key]))
    if level == "day":
        crumbs.append(calendar.month_abbr[int(ss[month_key])])
    st.markdown(" > ".join([f"**{c}**" for c in crumbs]))
    st.write("Hover • Click to drill down")

    # ================================
    #   LEVEL 1: YEAR
    # ================================
    if level == "year":

        df_plot = df.copy()
        df_plot["Year"] = df_plot[x_col].dt.year

        df_plot = df_plot.groupby("Year")[y_col].mean().reset_index().round(1)

        # ---- FORCE categorical axis ----
        df_plot["Year"] = df_plot["Year"].astype(str)
        xfield = "Year"

    # ================================
    #   LEVEL 2: MONTH
    # ================================
    elif level == "month":
        df_plot = df[df[x_col].dt.year == ss[year_key]].copy()

        df_plot["MonthNum"] = df_plot[x_col].dt.month
        df_plot = df_plot.groupby("MonthNum")[y_col].mean().reset_index().round(1)

        df_plot["Month"] = df_plot["MonthNum"].apply(lambda m: calendar.month_abbr[m])
        df_plot["Month"] = df_plot["Month"].astype(str)

        df_plot = df_plot.sort_values("MonthNum")
        xfield = "Month"

    # ================================
    #   LEVEL 3: DAY
    # ================================
    elif level == "day":
        df_plot = df[
            (df[x_col].dt.year == ss[year_key]) &
            (df[x_col].dt.month == int(ss[month_key]))
        ].copy()

        df_plot["Day"] = df_plot[x_col].dt.day
        df_plot = df_plot.groupby("Day")[y_col].mean().reset_index().round(1)

        df_plot["Day"] = df_plot["Day"].astype(str)
        xfield = "Day"

    # ================================
    #   BUILD PLOT
    # ================================
    fig = px.line(
        df_plot,
        x=xfield,
        y=y_col,
        markers=True,
        title=chart_label
    )

    # -----------------------------
    # CUSTOM TOOLTIP SUPPORT
    # -----------------------------
    if tooltip_cols:
        df_plot["_tooltipdata"] = df[tooltip_cols].iloc[:len(df_plot)].values
        custom_len = len(tooltip_cols)
    else:
        df_plot["_tooltipdata"] = None
        custom_len = 0

    fig.update_traces(
        customdata=df_plot["_tooltipdata"],
        hovertemplate=(
            f"{xfield}: %{{x}}<br>"
            f"{y_col}: %{{y}}<br>"
            +
            "".join([
                f"{col}: %{{customdata[{i}]}}<br>"
                for i, col in enumerate(tooltip_cols)
            ])
            +
            "<extra></extra>"
        )
    )

    fig.update_traces(
        mode="lines+markers+text",
        text=df_plot[y_col],
        textposition="top center"
    )

    # CRITICAL: Force categorical x-axis so NO 2020.5 etc.
    fig.update_xaxes(type="category")

    fig.update_layout(
        transition_duration=400,
        hovermode="closest",
        template="plotly_white",
        title_x=0.5,
    )

    # Unique key for each chart
    plot_key = f"plot_{prefix}_{level}"

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        key=plot_key
    )

    # ================================
    #   DRILL DOWN LOGIC
    # ================================
    if event.selection and len(event.selection.points) > 0:
        sel = event.selection.points[0]["x"]

        # YEAR → MONTH
        if level == "year" and has_month:
            ss[year_key] = int(sel)
            ss[level_key] = "month"
            st.rerun()

        # MONTH → DAY
        elif level == "month" and has_day:
            ss[month_key] = list(calendar.month_abbr).index(sel)
            ss[level_key] = "day"
            st.rerun()

    # ================================
    #   BACK BUTTON
    # ================================
    cols = st.columns([1, 1, 5])
    if level in ["month", "day"]:

        if cols[0].button("⬅ Back", key=f"back_{prefix}_{level}"):

            if level == "day":
                ss[level_key] = "month"
                ss[month_key] = None
            else:
                ss[level_key] = "year"
                ss[year_key] = None

            st.rerun()


def metric_card(df, col_name, label=None):
    """
    Displays a Streamlit metric card showing the average of a column.

    Parameters:
        df (pd.DataFrame): Input dataframe
        col_name (str): Column to average
        label (str): Optional label to show on the card (default = col_name)
    """
    # Use custom label or fallback to column name
    label = label if label else col_name

    # Compute average (ignores NaN automatically)
    avg_value = df[col_name].mean()

    # Round to 1 decimals
    avg_value = round(avg_value, 1)

    # Show metric card
    st.metric(label=label, value=f"{avg_value}")




all_fin_service_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='all_fin_service'), 'date_MMYY')
all_national_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='all_national'), 'date_YY')
billing_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='agg_billing'), 'date_YYMM')
production_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='production'), 'date_YYMMDD')
s_access_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='s_access'), 'date_YY')
s_service_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='s_service'), 'date_MMYY')
w_access_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='w_access'), 'date_YY')
w_service_df = clean_date(pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='w_service'), 'date_MMYY')
city_zone_mapping_df = pd.read_excel('Raw_Data\Master_Data.xlsx', sheet_name='city_zone_mapping')
master_list_df = [all_fin_service_df, all_national_df, billing_df,
                  production_df, s_access_df, s_service_df,
                  w_access_df, w_service_df, city_zone_mapping_df]

for df in master_list_df:
    clean_country_city_zone_source(df)
for df in master_list_df:
    add_city_column_if_missing(df, city_zone_mapping_df)

# --- External Filter ---
filter_col = 'country'  # You define this in code

selected_values = st.sidebar.selectbox(
    "Select Country",
    options=all_national_df[filter_col].unique(),
    index=0,
    help="Select a country to filter the dashboard (single selection)"
)
selected_values = [selected_values]  # Convert to list for filtering

# KPI 1

kpi1_billing_df = simple_group_and_sum(
    df=billing_df, group_cols=["zone", "date_YYMM", "country"],
    sum_cols=["billed", "paid", "consumption_m3"])
kpi1_billing_df.rename(columns={'billed': 'total_billed'}, inplace=True)
kpi1_billing_df.rename(columns={'paid': 'total_paid'}, inplace=True)
kpi1_billing_df = kpi_rate_calc(kpi1_billing_df, "NRW", "total_billed", "total_paid")

kpi2a4a5_all_fin_service_df = simple_group_and_sum(
    df=all_fin_service_df, group_cols=["city", "date_MMYY", "country"],
    sum_cols=["sewer_revenue", "opex", "complaints", "resolved", "blocks", "sewer_length"])

kpi2a4a5_all_fin_service_df.rename(columns={'sewer_revenue': 'total_sewer_revenue'}, inplace=True)
kpi2a4a5_all_fin_service_df.rename(columns={'opex': 'total_opex'}, inplace=True)
kpi2a4a5_all_fin_service_df = kpi_rate_calc(kpi2a4a5_all_fin_service_df, "SRC", "total_sewer_revenue", "total_opex", flag=1)

# kpi4a5_all_fin_service_df = simple_group_and_sum(
#     df=all_fin_service_df, group_cols=["city", "date_MMYY", "country"],
#     sum_cols=[])

kpi2a4a5_all_fin_service_df.rename(columns={'complaints': 'total_complaints'}, inplace=True)
kpi2a4a5_all_fin_service_df.rename(columns={'resolved': 'total_resolved'}, inplace=True)
kpi2a4a5_all_fin_service_df = kpi_rate_calc(kpi2a4a5_all_fin_service_df, "SUC", "total_complaints", "total_resolved", flag=0)

kpi2a4a5_all_fin_service_df.rename(columns={'blocks': 'total_blocks'}, inplace=True)
kpi2a4a5_all_fin_service_df.rename(columns={'sewer_length': 'total_sewer_length'}, inplace=True)
kpi2a4a5_all_fin_service_df = kpi_rate_calc(kpi2a4a5_all_fin_service_df, "SBK", "total_blocks", "total_sewer_length", flag=2)


# KPI 3


kpi3_all_fin_service_df = group_and_sum(
    df=all_fin_service_df,new_col_name="total_opex", date_col="date_MMYY",
    group_cols=["country", "city"], granularity="year", sum_col="opex")

kpi3_all_national_df = simple_group_and_sum(
    df=all_national_df, group_cols=["country", "city", "date_YY"],
    sum_cols=["budget_allocated"])
kpi3_all_national_df.rename(columns={'budget_allocated': 'total_budget_allocated'}, inplace=True)

kpi3_all_fin_service_df.rename(columns={'grouped_date': 'date_YY'}, inplace=True)

kpi3_df = pd.merge(kpi3_all_fin_service_df, kpi3_all_national_df,
                                 how="left",
                                 on=["country", "city", "date_YY"])

kpi3_df = kpi_rate_calc(kpi3_df, "OSB", "total_budget_allocated", "total_opex", flag=0)

kpi6a7_w_service_df = simple_group_and_sum(
    df=w_service_df, group_cols=["zone", "date_MMYY", "country"],
    sum_cols=["tests_passed_ecoli", "test_conducted_ecoli", "tests_ecoli",
              "test_passed_chlorine", "tests_conducted_chlorine", "tests_chlorine"])

kpi6a7_w_service_df.rename(columns={'tests_passed_ecoli': 'total_tests_passed_ecoli'}, inplace=True)
kpi6a7_w_service_df.rename(columns={'test_conducted_ecoli': 'total_test_conducted_ecoli'}, inplace=True)
kpi6a7_w_service_df.rename(columns={'tests_ecoli': 'total_tests_ecoli'}, inplace=True)

kpi6a7_w_service_df.rename(columns={'test_passed_chlorine': 'total_tests_passed_chlorine'}, inplace=True)
kpi6a7_w_service_df.rename(columns={'tests_conducted_chlorine': 'total_tests_conducted_chlorine'}, inplace=True)
kpi6a7_w_service_df.rename(columns={'tests_chlorine': 'total_tests_chlorine'}, inplace=True)

kpi6a7_w_service_df = kpi_rate_calc(kpi6a7_w_service_df, "ETF", "total_test_conducted_ecoli", "total_tests_passed_ecoli", flag=0)
kpi6a7_w_service_df = kpi_rate_calc(kpi6a7_w_service_df, "ETS", "total_tests_ecoli", "total_test_conducted_ecoli", flag=0)

kpi6a7_w_service_df = kpi_rate_calc(kpi6a7_w_service_df, "CTF", "total_tests_conducted_chlorine", "total_tests_passed_chlorine", flag=0)
kpi6a7_w_service_df = kpi_rate_calc(kpi6a7_w_service_df, "CTS", "total_tests_chlorine", "total_tests_conducted_chlorine", flag=0)


kpi8_w_access_df = simple_group_and_sum(
    df=w_access_df, group_cols=["city", "date_YY", "country"],
    sum_cols=["popn_total", "households", "municipal_coverage"])
kpi8_w_access_df.rename(columns={'popn_total': 'total_popn_total'}, inplace=True)
kpi8_w_access_df.rename(columns={'households': 'total_households'}, inplace=True)
kpi8_w_access_df.rename(columns={'municipal_coverage': 'total_municipal_coverage'}, inplace=True)
kpi8_w_access_df["PPH"]=kpi8_w_access_df["total_popn_total"]/kpi8_w_access_df["total_households"]
kpi8_w_access_df["MHC"]=kpi8_w_access_df["total_municipal_coverage"]/kpi8_w_access_df["PPH"]

# If date_MMYY is a string, ensure it's converted to datetime
kpi8_all_fin_service_df = all_fin_service_df.copy()
kpi8_all_fin_service_df['date_MMYY'] = pd.to_datetime(kpi8_all_fin_service_df['date_MMYY'])
# Extract year
kpi8_all_fin_service_df['year'] = kpi8_all_fin_service_df['date_MMYY'].dt.year
# If date_YY is a string or datetime, convert and extract year
kpi8_w_access_df['date_YY'] = pd.to_datetime(kpi8_w_access_df['date_YY'], format='%Y')
kpi8_w_access_df['year'] = kpi8_w_access_df['date_YY'].dt.year
kpi8_df = kpi8_all_fin_service_df.merge(
    kpi8_w_access_df[['year', 'MHC', 'city', 'country']],
    on=['year', 'city', 'country'],
    how='left'
)
# kpi8_df['WSH'] = kpi8_df['w_staff'] / kpi8_df['MHC']
kpi8_df = kpi_rate_calc(kpi8_df, "WSH", "w_staff", "MHC", flag=1)

kpi9_s_service_df = simple_group_and_sum(
    df=s_service_df, group_cols=["city", "date_MMYY", "country"],
    sum_cols=["sewer_connections"])
kpi9_s_service_df.rename(columns={'sewer_connections': 'total_sewer_connections'}, inplace=True)
kpi9_all_fin_service_df = all_fin_service_df.copy()

kpi9_df = kpi9_all_fin_service_df.merge(
    kpi9_s_service_df[["city", "date_MMYY", "country", 'total_sewer_connections']],
    on=['date_MMYY', 'city', 'country'],
    how='left'
)

# kpi9_df['Sewer_Connections'] = kpi9_df['sewer_connections'] / kpi9_df['total_sewer_connections']
kpi9_df = kpi_rate_calc(kpi9_df, "SSC", "san_staff", "total_sewer_connections", flag=1)

kpi10_production_df = group_and_sum(
    df=production_df,new_col_name="total_production", date_col="date_YYMMDD",
    group_cols=["country"], granularity="month", sum_col="production_m3")
kpi10_production_df.rename(columns={'grouped_date': 'date_MMYY'}, inplace=True)

kpi10_w_service_df = simple_group_and_sum(
    df=w_service_df, group_cols=["date_MMYY", "country"],
    sum_cols=["total_consumption"])
kpi10_w_service_df.rename(columns={'total_consumption': 'grand_total_consumption'}, inplace=True)

kpi10_df = kpi10_w_service_df.merge(
    kpi10_production_df[["date_MMYY", "country", 'total_production']],
    on=['date_MMYY', 'country'],
    how='left'
)

kpi10_df = kpi_rate_calc(kpi10_df, "NCW", "total_production", "grand_total_consumption", flag=0)

kpi11_w_service_df = simple_group_and_sum(
    df=w_service_df, group_cols=["date_MMYY", "zone", "country"],
    sum_cols=["total_consumption", "metered"])
kpi11_w_service_df.rename(columns={'total_consumption': 'grand_total_consumption'}, inplace=True)
kpi11_w_service_df.rename(columns={'metered': 'total_metered'}, inplace=True)
kpi11_w_service_df = kpi_rate_calc(kpi11_w_service_df, "NMW", "grand_total_consumption", "total_metered", flag=0)

kpi12_w_service_df = simple_group_and_sum(
    df=w_access_df, group_cols=["date_YY", "zone", "country"],
    sum_cols=["popn_total", "municipal_coverage"])
kpi12_w_service_df.rename(columns={'popn_total': 'grand_popn_total'}, inplace=True)
kpi12_w_service_df.rename(columns={'municipal_coverage': 'total_municipal_coverage'}, inplace=True)
kpi12_w_service_df = kpi_rate_calc(kpi12_w_service_df, "PUW", "grand_popn_total", "total_municipal_coverage", flag=0)

kpi13_s_service_df = simple_group_and_sum(
    df=s_service_df, group_cols=["date_MMYY", "zone", "country"],
    sum_cols=["households", "sewer_connections"])
kpi13_s_service_df.rename(columns={'households': 'total_households'}, inplace=True)
kpi13_s_service_df.rename(columns={'sewer_connections': 'total_sewer_connections'}, inplace=True)
kpi13_s_service_df = kpi_rate_calc(kpi13_s_service_df, "HUS", "total_households", "total_sewer_connections", flag=0)


# with st.container():


#     df = kpi1_billing_df
#     df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
#     plotly_chart_with_labels(df_filtered, x_col='date_YYMM', y_col='NRW Rate', chart_label="Non-Revenue Water (NRW) Rate", tooltip_cols=["Tool NRW"])
    
    
#     df = kpi2a4a5_all_fin_service_df
#     df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
#     plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='SRC Rate', chart_label="Sewer Revenue Coverage (SRC) Rate", tooltip_cols=["Tool SRC"])
    

#     df = kpi3_df
#     df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
#     plotly_chart_with_labels(df_filtered, x_col='date_YY', y_col='OSB Rate', chart_label="Opex Share of Budget (OSB) Rate", tooltip_cols=["Tool OSB"])


tab1, tab2, tab3 = st.tabs(["Financial Health", "Operational Performance", "Service Coverage"])

with tab1:

    col1, col2, col3 = st.columns(3)

    with col1:
        df = kpi1_billing_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "NRW Rate", label="Avg. NRW %")

    with col2:
        df = kpi2a4a5_all_fin_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "SRC Rate", label="Avg. SRC %")
        
    with col3:
        df = kpi3_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "OSB Rate", label="Avg. OSB %")


    df = kpi1_billing_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_YYMM', y_col='NRW Rate', chart_label="Non-Revenue Water (NRW) Rate", tooltip_cols=["Tool NRW"])
    
    
    df = kpi2a4a5_all_fin_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='SRC Rate', chart_label="Sewer Revenue Coverage (SRC) Rate", tooltip_cols=["Tool SRC"])
    

    df = kpi3_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_YY', y_col='OSB Rate', chart_label="Opex Share of Budget (OSB) Rate", tooltip_cols=["Tool OSB"])



with tab2:

    col1, col2, col3 = st.columns(3)

    with col1:
        df = kpi2a4a5_all_fin_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "SUC Rate", label="Avg. SUC %")

    with col2:
        df = kpi10_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "NCW Rate", label="Avg. NCW %")

    with col3:
        df = kpi11_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "NMW Rate", label="Avg. NMW %")

    col1, col2, col3 = st.columns(3)

    with col1:
        df = kpi2a4a5_all_fin_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "SBK Rate", label="Avg. SBK")

    with col2:
        df = kpi8_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "WSH Rate", label="Avg. WSH")

    with col3:
        df = kpi9_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "SSC Rate", label="Avg. SSC")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        df = kpi6a7_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "ETF Rate", label="Avg. ETF %")

    with col2:
        df = kpi6a7_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "ETS Rate", label="Avg. ETS %")
    with col3:
        df = kpi6a7_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "CTF Rate", label="Avg. CTF %")

    with col4:
        df = kpi6a7_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "CTS Rate", label="Avg. CTS %")


    df = kpi2a4a5_all_fin_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='SUC Rate', chart_label="Sewer Unresolved Complaints (SUC) Rate", tooltip_cols=["Tool SRC"])
    
    df = kpi2a4a5_all_fin_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='SBK Rate', chart_label="Sewer Blocks per Kilometre (SBK)", tooltip_cols=["Tool SRC"])

    df = kpi6a7_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='ETF Rate', chart_label="E. coli Test Failure (ETF) Rate", tooltip_cols=["Tool ETF"])

    df = kpi6a7_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='ETS Rate', chart_label="E. coli Test Skipped (ETS) Rate", tooltip_cols=["Tool ETS"])
    
    df = kpi6a7_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='CTF Rate', chart_label="Chlorine Test Failure (CTF) Rate", tooltip_cols=["Tool CTF"])

    df = kpi6a7_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='CTS Rate', chart_label="Chlorine Test Skipped (CTS) Rate", tooltip_cols=["Tool CTS"])

    df = kpi8_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='WSH Rate', chart_label="Water Staffing per hundred Households (WSH)", tooltip_cols=["Tool WSH"])

    df = kpi9_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='SSC Rate', chart_label="Sanitation Staffing per hundred sewer Connections (SSC)", tooltip_cols=["Tool SSC"])

    df = kpi10_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='NCW Rate', chart_label="Non Consumed Water (NCW) Rate", tooltip_cols=["Tool NCW"])

    df = kpi11_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='NMW Rate', chart_label="Non Metered Water (NMW) Rate", tooltip_cols=["Tool NMW"])

with tab3:

    col1, col2 = st.columns(2)

    with col1:
        df = kpi12_w_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "PUW Rate", label="Avg. PUW %")

    with col2:
        df = kpi13_s_service_df
        df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
        metric_card(df_filtered, "HUS Rate", label="Avg. HUS %")

    df = kpi12_w_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_YY', y_col='PUW Rate', chart_label="Population Unconnected to Water (PUW) Rate", tooltip_cols=["Tool PUW"])

    df = kpi13_s_service_df
    df_filtered = df[df[filter_col].isin(selected_values)] # Apply filter
    plotly_chart_with_labels(df_filtered, x_col='date_MMYY', y_col='HUS Rate', chart_label="Households Unconnected to Sanitation (HUS) Rate", tooltip_cols=["Tool HUS"])

