import streamlit as st
import pandas as pd
import numpy as np

st.title("Summary Dashboard — High-Level Overview")

countries = ["Lesotho", "Malawi", "Uganda", "Cameroon"]
years = list(range(2020, 2026))

left, right = st.columns(2)
with left:
    country = st.selectbox("Country", countries)
with right:
    year = st.selectbox("Year", years, index=len(years) - 1)


def generate_overview_data(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for c in countries:
        water_base = {"Lesotho": 72, "Malawi": 60, "Uganda": 78, "Cameroon": 66}[c]
        sanitation_base = {"Lesotho": 58, "Malawi": 50, "Uganda": 62, "Cameroon": 55}[c]
        for y in years:
            for m in range(1, 13):
                date = pd.Timestamp(year=y, month=m, day=1)
                safely_managed_water = float(np.clip(rng.normal(water_base, 4), 40, 95))
                safely_managed_san = float(np.clip(rng.normal(sanitation_base, 5), 30, 90))

                w_supplied = float(np.clip(rng.normal(22_000, 3_000), 8_000, 35_000))
                total_consumption = float(np.clip(rng.normal(18_000, 2_500), 6_000, 32_000))

                water_billed = float(np.clip(rng.normal(95_000, 15_000), 30_000, 180_000))
                sewer_billed = float(np.clip(rng.normal(42_000, 8_000), 10_000, 90_000))
                water_revenue = float(np.clip(rng.normal(90_000, 15_000), 25_000, 170_000))
                sewer_revenue = float(np.clip(rng.normal(40_000, 7_000), 9_000, 85_000))

                rows.append({
                    "country": c,
                    "year": y,
                    "month": m,
                    "date": date,
                    "safely_managed_water_pct": safely_managed_water,
                    "safely_managed_sanitation_pct": safely_managed_san,
                    "w_supplied": w_supplied,
                    "total_consumption": total_consumption,
                    "water_billed": water_billed,
                    "sewer_billed": sewer_billed,
                    "water_revenue": water_revenue,
                    "sewer_revenue": sewer_revenue,
                })
    df = pd.DataFrame(rows)
    df["nrw_pct"] = (df["w_supplied"] - df["total_consumption"]) / df["w_supplied"] * 100.0
    df["collection_efficiency_pct"] = (df["sewer_revenue"] + df["water_revenue"]) / (
        df["sewer_billed"] + df["water_billed"]
    ) * 100.0
    return df


df = generate_overview_data()
sel = df[(df["country"] == country) & (df["year"] == year)]

# KPI cards (averaged over months)
wm = sel["safely_managed_water_pct"].mean()
sm = sel["safely_managed_sanitation_pct"].mean()
nrw = sel["nrw_pct"].mean()
rc = sel["collection_efficiency_pct"].mean()

cards = st.columns(4)
cards[0].metric("Safely Managed Water (%)", f"{wm:,.1f}")
cards[1].metric("Safely Managed Sanitation (%)", f"{sm:,.1f}")
cards[2].metric("NRW (%)", f"{nrw:,.1f}")
cards[3].metric("Revenue Collection Eff. (%)", f"{rc:,.1f}")

st.markdown("---")
st.subheader("Trends — Monthly")
country_df = df[df["country"] == country]

tc1, tc2 = st.columns(2)
with tc1:
    st.area_chart(country_df.set_index("date")["safely_managed_water_pct"], height=220, use_container_width=True)
    st.caption("Safely Managed Water (% of population)")
with tc2:
    st.area_chart(country_df.set_index("date")["safely_managed_sanitation_pct"], height=220, use_container_width=True)
    st.caption("Safely Managed Sanitation (% of population)")

tc3, tc4 = st.columns(2)
with tc3:
    st.line_chart(country_df.set_index("date")["nrw_pct"], height=220, use_container_width=True)
    st.caption("Non-Revenue Water (% of water supplied)")
with tc4:
    st.line_chart(country_df.set_index("date")["collection_efficiency_pct"], height=220, use_container_width=True)
    st.caption("Revenue Collection Efficiency (%)")

st.markdown("---")
st.subheader(f"Country Comparison — {year}")
avg = (
    df[df["year"] == year]
    .groupby("country", as_index=False)[[
        "safely_managed_water_pct",
        "safely_managed_sanitation_pct",
        "nrw_pct",
        "collection_efficiency_pct",
    ]].mean()
)

cc1, cc2 = st.columns(2)
with cc1:
    st.bar_chart(avg.set_index("country")["safely_managed_water_pct"], height=250)
    st.caption("Safely Managed Water (%)")
with cc2:
    st.bar_chart(avg.set_index("country")["safely_managed_sanitation_pct"], height=250)
    st.caption("Safely Managed Sanitation (%)")

cc3, cc4 = st.columns(2)
with cc3:
    st.bar_chart(avg.set_index("country")["nrw_pct"], height=250)
    st.caption("NRW (%) — lower is better")
with cc4:
    st.bar_chart(avg.set_index("country")["collection_efficiency_pct"], height=250)
    st.caption("Revenue Collection Efficiency (%)")

with st.expander("Formulas"):
    st.markdown("- Safely Managed Water: safely_managed_pct")
    st.markdown("- Safely Managed Sanitation: safely_managed_pct")
    st.markdown("- NRW: ((w_supplied - total_consumption) / w_supplied) * 100")
    st.markdown("- Revenue Collection Efficiency: (sewer_revenue + water_revenue) / (sewer_billed + water_billed) * 100")


