import streamlit as st
import pandas as pd
import numpy as np

st.title("Water Service Dashboard")

# Filters
available_countries = ["Lesotho", "Malawi", "Uganda", "Cameroon"]
available_years = list(range(2020, 2026))

col_filters_left, col_filters_right = st.columns(2)
with col_filters_left:
    selected_country = st.selectbox("Country", options=available_countries, index=0)
with col_filters_right:
    selected_year = st.selectbox("Year", options=available_years, index=len(available_years) - 1)


def generate_monthly_dummy_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for country in available_countries:
        base_hours = {
            "Lesotho": 18.0,
            "Malawi": 16.0,
            "Uganda": 20.0,
            "Cameroon": 17.0,
        }[country]
        for year in available_years:
            for month in range(1, 13):
                seasonal = 1.0 + 0.1 * np.sin((month / 12) * 2 * np.pi)
                service_hours = np.clip(rng.normal(base_hours * seasonal, 1.2), 10, 24)

                tests_conducted_chlorine = int(rng.normal(220, 30))
                test_conducted_ecoli = int(rng.normal(200, 25))
                test_passed_chlorine = int(np.clip(tests_conducted_chlorine * rng.uniform(0.85, 0.98), 0, tests_conducted_chlorine))
                tests_passed_ecoli = int(np.clip(test_conducted_ecoli * rng.uniform(0.88, 0.99), 0, test_conducted_ecoli))

                total_consumption = float(np.clip(rng.normal(18_000, 3_000), 8_000, 30_000))
                metered_share = np.clip(rng.normal(0.65, 0.1), 0.2, 0.95)
                metered = float(total_consumption * metered_share)

                water_revenue = float(np.clip(rng.normal(120_000, 25_000), 40_000, 220_000))
                sewer_revenue = float(np.clip(rng.normal(55_000, 12_000), 15_000, 110_000))
                opex = float(np.clip(rng.normal(160_000, 30_000), 60_000, 280_000))

                rows.append({
                    "country": country,
                    "year": year,
                    "month": month,
                    "date": pd.Timestamp(year=year, month=month, day=1),
                    "service_hours": float(service_hours),
                    "tests_conducted_chlorine": tests_conducted_chlorine,
                    "test_conducted_ecoli": test_conducted_ecoli,
                    "test_passed_chlorine": test_passed_chlorine,
                    "tests_passed_ecoli": tests_passed_ecoli,
                    "metered": metered,
                    "total_consumption": total_consumption,
                    "water_revenue": water_revenue,
                    "sewer_revenue": sewer_revenue,
                    "opex": opex,
                })
    return pd.DataFrame(rows)


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


df = generate_monthly_dummy_data()

# Compute KPIs at row level for convenient plotting
df["quality_compliance_pct"] = (df["test_passed_chlorine"] + df["tests_passed_ecoli"]) / (
    df["tests_conducted_chlorine"] + df["test_conducted_ecoli"]
) * 100.0
df["metering_ratio_pct"] = (df["metered"] / df["total_consumption"]) * 100.0
df["operating_coverage_pct"] = ((df["sewer_revenue"] + df["water_revenue"]) / df["opex"]) * 100.0


# KPI cards for selected country/year (aggregated across months)
sel = df[(df["country"] == selected_country) & (df["year"] == selected_year)]
service_hours = sel["service_hours"].mean() if not sel.empty else 0.0
compliance_pct = sel["quality_compliance_pct"].mean() if not sel.empty else 0.0
metering_ratio_pct = sel["metering_ratio_pct"].mean() if not sel.empty else 0.0
operating_coverage_pct = sel["operating_coverage_pct"].mean() if not sel.empty else 0.0

st.subheader(f"{selected_country} — {selected_year}")
metric_cols = st.columns(4)
metric_cols[0].metric("Continuity of Supply (hrs/day)", f"{service_hours:,.1f}")
metric_cols[1].metric("Water Quality Compliance (%)", f"{compliance_pct:,.1f}")
metric_cols[2].metric("Metering Ratio (%)", f"{metering_ratio_pct:,.1f}")
metric_cols[3].metric("Operating Cost Coverage (%)", f"{operating_coverage_pct:,.1f}")


# Trend charts for selected country across 2020–2025
st.markdown("---")
st.subheader("Trends — Monthly")
sel_country = df[df["country"] == selected_country]

trend_cols = st.columns(2)
with trend_cols[0]:
    st.line_chart(sel_country.set_index("date")["service_hours"], height=220)
    st.caption("Continuity of Supply (hrs/day)")
with trend_cols[1]:
    st.line_chart(sel_country.set_index("date")["quality_compliance_pct"], height=220)
    st.caption("Drinking Water Quality Compliance (%)")

trend_cols2 = st.columns(2)
with trend_cols2[0]:
    st.line_chart(sel_country.set_index("date")["metering_ratio_pct"], height=220)
    st.caption("Metering Ratio (%)")
with trend_cols2[1]:
    st.line_chart(sel_country.set_index("date")["operating_coverage_pct"], height=220)
    st.caption("Operating Cost Coverage (%)")


# Country comparison for selected year (averages)
st.markdown("---")
st.subheader(f"Country Comparison — {selected_year}")
year_avg = (
    df[df["year"] == selected_year]
    .groupby("country", as_index=False)[
        [
            "service_hours",
            "quality_compliance_pct",
            "metering_ratio_pct",
            "operating_coverage_pct",
        ]
    ]
    .mean()
)

comp_cols = st.columns(2)
with comp_cols[0]:
    st.bar_chart(year_avg.set_index("country")["service_hours"], height=250)
    st.caption("Continuity of Supply (hrs/day)")
with comp_cols[1]:
    st.bar_chart(year_avg.set_index("country")["quality_compliance_pct"], height=250)
    st.caption("Water Quality Compliance (%)")

comp_cols2 = st.columns(2)
with comp_cols2[0]:
    st.bar_chart(year_avg.set_index("country")["metering_ratio_pct"], height=250)
    st.caption("Metering Ratio (%)")
with comp_cols2[1]:
    st.bar_chart(year_avg.set_index("country")["operating_coverage_pct"], height=250)
    st.caption("Operating Cost Coverage (%)")


with st.expander("Formulas"):
    st.markdown("- Continuity of Supply: service_hours (hrs/day)")
    st.markdown("- Drinking Water Quality Compliance: ((test_passed_chlorine + tests_passed_ecoli) / (tests_conducted_chlorine + test_conducted_ecoli)) * 100")
    st.markdown("- Metering Ratio: (metered / total_consumption) * 100")
    st.markdown("- Operating Cost Coverage: (sewer_revenue + water_revenue) / opex * 100")


