import streamlit as st
import pandas as pd

st.title("Water Service Dashboard")

# Filters
available_countries = ["Lesotho", "Malawi", "Uganda", "Cameroon"]
available_years = list(range(2020, 2026))

col_filters_left, col_filters_right = st.columns(2)
with col_filters_left:
    selected_country = st.selectbox("Country", options=available_countries, index=0)
with col_filters_right:
    selected_year = st.selectbox("Year", options=available_years, index=len(available_years) - 1)


def generate_dummy_data() -> dict:
    countries = available_countries
    years = available_years

    # production_[country].csv mock
    production_rows = []
    for country in countries:
        for year in years:
            service_hours = 12 + hash((country, year)) % 13  # 12 to 24 hours
            production_rows.append({
                "country": country,
                "year": year,
                "service_hours": float(service_hours),
            })
    production_df = pd.DataFrame(production_rows)

    # w_service_[country].csv mock (water service quality/efficiency)
    w_service_rows = []
    for country in countries:
        for year in years:
            tests_conducted_chlorine = 200 + (hash((country, year, "cl")) % 100)
            test_conducted_ecoli = 180 + (hash((country, year, "ec")) % 80)
            test_passed_chlorine = int(tests_conducted_chlorine * 0.9)
            tests_passed_ecoli = int(test_conducted_ecoli * 0.92)
            metered = 8_000 + (hash((country, year, "m")) % 5_000)
            total_consumption = metered + 2_000 + (hash((country, year, "tc")) % 5_000)
            w_service_rows.append({
                "country": country,
                "year": year,
                "tests_conducted_chlorine": tests_conducted_chlorine,
                "test_conducted_ecoli": test_conducted_ecoli,
                "test_passed_chlorine": test_passed_chlorine,
                "tests_passed_ecoli": tests_passed_ecoli,
                "metered": float(metered),
                "total_consumption": float(total_consumption),
            })
    w_service_df = pd.DataFrame(w_service_rows)

    # all_fin_service_[country].csv mock (financials)
    fin_rows = []
    for country in countries:
        for year in years:
            water_revenue = 1_000_000 + (hash((country, year, "wr")) % 500_000)
            sewer_revenue = 400_000 + (hash((country, year, "sr")) % 250_000)
            opex = 1_200_000 + (hash((country, year, "ox")) % 400_000)
            fin_rows.append({
                "country": country,
                "year": year,
                "water_revenue": float(water_revenue),
                "sewer_revenue": float(sewer_revenue),
                "opex": float(opex),
            })
    fin_df = pd.DataFrame(fin_rows)

    return {
        "production": production_df,
        "w_service": w_service_df,
        "fin": fin_df,
    }


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


data = generate_dummy_data()

production_sel = data["production"].query("country == @selected_country and year == @selected_year")
w_service_sel = data["w_service"].query("country == @selected_country and year == @selected_year")
fin_sel = data["fin"].query("country == @selected_country and year == @selected_year")

# Continuity of Supply (Service Quality)
service_hours = float(production_sel["service_hours"].iloc[0]) if not production_sel.empty else 0.0

# Drinking Water Quality Compliance (Service Quality)
cl_pass = int(w_service_sel["test_passed_chlorine"].iloc[0]) if not w_service_sel.empty else 0
ec_pass = int(w_service_sel["tests_passed_ecoli"].iloc[0]) if not w_service_sel.empty else 0
cl_tests = int(w_service_sel["tests_conducted_chlorine"].iloc[0]) if not w_service_sel.empty else 0
ec_tests = int(w_service_sel["test_conducted_ecoli"].iloc[0]) if not w_service_sel.empty else 0
compliance_pct = safe_ratio(cl_pass + ec_pass, cl_tests + ec_tests) * 100

# Metering Ratio (Efficiency & Billing)
metered = float(w_service_sel["metered"].iloc[0]) if not w_service_sel.empty else 0.0
total_consumption = float(w_service_sel["total_consumption"].iloc[0]) if not w_service_sel.empty else 0.0
metering_ratio_pct = safe_ratio(metered, total_consumption) * 100

# Operating Cost Coverage (Financial Sustainability)
sewer_revenue = float(fin_sel["sewer_revenue"].iloc[0]) if not fin_sel.empty else 0.0
water_revenue = float(fin_sel["water_revenue"].iloc[0]) if not fin_sel.empty else 0.0
opex = float(fin_sel["opex"].iloc[0]) if not fin_sel.empty else 0.0
operating_coverage_pct = safe_ratio(sewer_revenue + water_revenue, opex) * 100

st.subheader(f"{selected_country} — {selected_year}")
metric_cols = st.columns(4)
metric_cols[0].metric("Continuity of Supply (hrs/day)", f"{service_hours:,.1f}")
metric_cols[1].metric("Water Quality Compliance (%)", f"{compliance_pct:,.1f}")
metric_cols[2].metric("Metering Ratio (%)", f"{metering_ratio_pct:,.1f}")
metric_cols[3].metric("Operating Cost Coverage (%)", f"{operating_coverage_pct:,.1f}")

with st.expander("Data references (dummy placeholders)"):
    st.write("production_[country].csv ➜ service_hours")
    st.write("w_service_[country].csv ➜ tests, metering, consumption")
    st.write("all_fin_service_[country].csv ➜ water_revenue, sewer_revenue, opex")


