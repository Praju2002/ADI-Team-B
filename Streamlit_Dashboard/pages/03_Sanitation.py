import streamlit as st
import pandas as pd
import numpy as np

st.title("Sanitation Service Dashboard")

countries = ["Lesotho", "Malawi", "Uganda", "Cameroon"]
years = list(range(2020, 2026))

left, right = st.columns(2)
with left:
    country = st.selectbox("Country", countries)
with right:
    year = st.selectbox("Year", years, index=len(years) - 1)


def generate_sanitation_data(seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for c in countries:
        sewer_base = {"Lesotho": 35, "Malawi": 28, "Uganda": 40, "Cameroon": 32}[c]
        for y in years:
            for m in range(1, 13):
                date = pd.Timestamp(year=y, month=m, day=1)
                households = int(np.clip(rng.normal(120_000, 10_000), 60_000, 200_000))
                sewer_connections = int(np.clip(households * np.clip(rng.normal(sewer_base / 100.0, 0.05), 0.05, 0.8), 1, households))

                ww_collected = float(np.clip(rng.normal(85_000, 12_000), 30_000, 160_000))
                treat_eff = np.clip(rng.normal(0.7, 0.12), 0.2, 0.98)
                ww_treated = float(ww_collected * treat_eff)

                complaints = int(np.clip(rng.normal(1_000, 250), 100, 5_000))
                resolve_eff = np.clip(rng.normal(0.88, 0.07), 0.4, 0.99)
                resolved = int(complaints * resolve_eff)

                hh_emptied = int(np.clip(rng.normal(3_000, 600), 500, 12_000))
                fs_treated = float(np.clip(rng.normal(hh_emptied * 0.6, hh_emptied * 0.15), 100.0, hh_emptied * 1.2))

                rows.append({
                    "country": c,
                    "year": y,
                    "month": m,
                    "date": date,
                    "households": households,
                    "sewer_connections": sewer_connections,
                    "ww_collected": ww_collected,
                    "ww_treated": ww_treated,
                    "complaints": complaints,
                    "resolved": resolved,
                    "hh_emptied": hh_emptied,
                    "fs_treated": fs_treated,
                })
    df = pd.DataFrame(rows)
    df["sewer_coverage_pct"] = (df["sewer_connections"] / df["households"]) * 100.0
    df["ww_treated_pct"] = (df["ww_treated"] / df["ww_collected"]) * 100.0
    df["complaint_resolution_pct"] = (df["resolved"] / df["complaints"]) * 100.0
    non_sewered = (df["households"] - df["sewer_connections"]).clip(lower=1)
    df["fs_emptied_pct"] = (df["hh_emptied"] / non_sewered) * 100.0
    estimated_volume_emptied = df["hh_emptied"] * 1.0  # 1 unit per HH as placeholder
    df["fs_treated_pct"] = (df["fs_treated"] / estimated_volume_emptied.replace(0, np.nan)) * 100.0
    df["fs_treated_pct"] = df["fs_treated_pct"].fillna(0.0).clip(0, 200)
    return df


df = generate_sanitation_data()
sel = df[(df["country"] == country) & (df["year"] == year)]

# KPI cards (averaged over months)
sewer_cov = sel["sewer_coverage_pct"].mean()
ww_treated = sel["ww_treated_pct"].mean()
complaint_res = sel["complaint_resolution_pct"].mean()
fs_emptied = sel["fs_emptied_pct"].mean()
fs_treated = sel["fs_treated_pct"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Sewer Coverage (%)", f"{sewer_cov:,.1f}")
c2.metric("Wastewater Safely Treated (%)", f"{ww_treated:,.1f}")
c3.metric("Complaint Resolution Rate (%)", f"{complaint_res:,.1f}")
c4, c5 = st.columns(2)
c4.metric("Fecal Sludge Emptied (%) of non-sewered", f"{fs_emptied:,.1f}")
c5.metric("Fecal Sludge Treated (%) of emptied est.", f"{fs_treated:,.1f}")

st.markdown("---")
st.subheader("Trends — Monthly")
country_df = df[df["country"] == country]

t1, t2 = st.columns(2)
with t1:
    st.line_chart(country_df.set_index("date")["sewer_coverage_pct"], height=220)
    st.caption("Sewer Coverage (%)")
with t2:
    st.area_chart(country_df.set_index("date")["ww_treated_pct"], height=220)
    st.caption("Wastewater Safely Treated (%)")

t3, t4 = st.columns(2)
with t3:
    st.line_chart(country_df.set_index("date")["complaint_resolution_pct"], height=220)
    st.caption("Complaint Resolution Rate (%)")
with t4:
    st.bar_chart(country_df.set_index("date")[["fs_emptied_pct", "fs_treated_pct"]], height=220)
    st.caption("Fecal Sludge: Emptied vs Treated (%)")

st.markdown("---")
st.subheader(f"Country Comparison — {year}")
avg = (
    df[df["year"] == year]
    .groupby("country", as_index=False)[[
        "sewer_coverage_pct",
        "ww_treated_pct",
        "complaint_resolution_pct",
        "fs_emptied_pct",
        "fs_treated_pct",
    ]].mean()
)

b1, b2 = st.columns(2)
with b1:
    st.bar_chart(avg.set_index("country")["sewer_coverage_pct"], height=250)
    st.caption("Sewer Coverage (%)")
with b2:
    st.bar_chart(avg.set_index("country")["ww_treated_pct"], height=250)
    st.caption("Wastewater Safely Treated (%)")

b3, b4 = st.columns(2)
with b3:
    st.bar_chart(avg.set_index("country")["complaint_resolution_pct"], height=250)
    st.caption("Complaint Resolution Rate (%)")
with b4:
    st.bar_chart(avg.set_index("country")[["fs_emptied_pct", "fs_treated_pct"]], height=250)
    st.caption("Fecal Sludge Emptied vs Treated (%)")

with st.expander("Formulas"):
    st.markdown("- Sewer Coverage: (sewer_connections / households) * 100")
    st.markdown("- Wastewater Safely Treated: (ww_treated / ww_collected) * 100")
    st.markdown("- Complaint Resolution Rate: (resolved / complaints) * 100")
    st.markdown("- FS Emptied: (hh_emptied / (households - sewer_connections)) * 100")
    st.markdown("- FS Treated: (fs_treated / estimated_volume_emptied) * 100")


