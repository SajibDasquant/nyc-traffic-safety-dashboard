import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="NYC Traffic Safety Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SEVERITY_COLORS = {"Fatal": "#d62728", "Injury": "#ff7f0e", "No Injury": "#2ca02c"}


@st.cache_data
def load_data():
    monthly = pd.read_csv("data/monthly_citywide.csv")
    yearly_borough = pd.read_csv("data/yearly_borough.csv")
    factors = pd.read_csv("data/contributing_factors.csv")
    vehicles = pd.read_csv("data/vehicle_types.csv")
    hourly_dow = pd.read_csv("data/hourly_dow.csv")
    sample = pd.read_csv("data/crash_sample.csv")
    return monthly, yearly_borough, factors, vehicles, hourly_dow, sample


monthly, yearly_borough, factors, vehicles, hourly_dow, sample = load_data()

sample["crash_date"] = pd.to_datetime(sample["crash_date"])


def severity_of(row):
    if row["killed"] > 0:
        return "Fatal"
    if row["injured"] > 0:
        return "Injury"
    return "No Injury"


sample["severity"] = sample.apply(severity_of, axis=1)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")

boroughs = ["All"] + sorted(yearly_borough["BOROUGH"].unique().tolist())
sel_borough = st.sidebar.selectbox("Borough", boroughs)

years = sorted(yearly_borough["YEAR"].unique().tolist())
sel_years = st.sidebar.select_slider("Year Range", options=years, value=(years[0], years[-1]))

yb = yearly_borough[(yearly_borough["YEAR"] >= sel_years[0]) & (yearly_borough["YEAR"] <= sel_years[1])]
if sel_borough != "All":
    yb = yb[yb["BOROUGH"] == sel_borough]

sample_filt = sample.copy()
if sel_borough != "All":
    sample_filt = sample_filt[sample_filt["borough"] == sel_borough]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚦 NYC Traffic Safety Analytics")
st.caption(
    f"NYC Motor Vehicle Collisions · {monthly['MONTH'].min()} to {monthly['MONTH'].max()} "
    f"· {int(yb['crashes'].sum()):,} crashes in current filter"
)
st.caption(f"Note: {years[0]} and {years[-1]} are partial calendar years in the source data.")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_crashes = int(yb["crashes"].sum())
total_injured = int(yb["injured"].sum())
total_killed = int(yb["killed"].sum())
ped_killed = int(yb["pedestrians_killed"].sum())
cyclist_killed = int(yb["cyclists_killed"].sum())
fatality_rate = (total_killed / total_crashes * 1000) if total_crashes else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Crashes", f"{total_crashes:,}")
c2.metric("Persons Injured", f"{total_injured:,}")
c3.metric("Persons Killed", f"{total_killed:,}", delta_color="inverse")
c4.metric("Fatalities per 1,000 Crashes", f"{fatality_rate:.2f}")

c5, c6 = st.columns(2)
c5.metric("Pedestrian Fatalities", f"{ped_killed:,}", delta_color="inverse")
c6.metric("Cyclist Fatalities", f"{cyclist_killed:,}", delta_color="inverse")

st.divider()

# ── Citywide Trend ────────────────────────────────────────────────────────────
st.subheader("Citywide Monthly Trend")
fig_trend = px.line(
    monthly, x="MONTH", y=["crashes", "injured", "killed"],
    labels={"MONTH": "Month", "value": "Count", "variable": "Metric"},
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_trend.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title="")
st.plotly_chart(fig_trend, width="stretch")

st.divider()

# ── Borough + Severity Breakdown ─────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Crashes by Borough & Year")
    fig_borough = px.bar(
        yb, x="YEAR", y="crashes", color="BOROUGH", barmode="group",
        labels={"crashes": "Crashes", "YEAR": "Year", "BOROUGH": "Borough"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_borough.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_borough, width="stretch")

with col_b:
    st.subheader("Injury Severity Mix (Sampled Year)")
    sev_counts = sample_filt["severity"].value_counts().reindex(["Fatal", "Injury", "No Injury"]).fillna(0)
    fig_sev = px.pie(
        values=sev_counts.values, names=sev_counts.index,
        color=sev_counts.index, color_discrete_map=SEVERITY_COLORS, hole=0.4,
    )
    fig_sev.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_sev, width="stretch")

# ── Factors + Vehicles ────────────────────────────────────────────────────────
st.divider()
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Top Contributing Factors")
    fig_factors = px.bar(
        factors.sort_values("count"), x="count", y="factor", orientation="h",
        labels={"count": "Crashes", "factor": ""},
        color="count", color_continuous_scale="Reds",
    )
    fig_factors.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_factors, width="stretch")

with col_d:
    st.subheader("Top Vehicle Types Involved")
    fig_vehicles = px.bar(
        vehicles.sort_values("count"), x="count", y="vehicle_type", orientation="h",
        labels={"count": "Crashes", "vehicle_type": ""},
        color="count", color_continuous_scale="Blues",
    )
    fig_vehicles.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_vehicles, width="stretch")

# ── Time Patterns ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Crashes by Hour & Day of Week")
heat = hourly_dow.pivot(index="DAY_OF_WEEK", columns="HOUR", values="crashes").reindex(DOW_ORDER)
fig_heat = px.imshow(
    heat, labels=dict(x="Hour of Day", y="", color="Crashes"),
    color_continuous_scale="YlOrRd", aspect="auto",
)
fig_heat.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_heat, width="stretch")

# ── Map ───────────────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"Crash Locations — Sampled Recent Year ({len(sample_filt):,} points)")
fig_map = px.scatter_map(
    sample_filt, lat="latitude", lon="longitude", color="severity",
    hover_data={"borough": True, "street": True, "injured": True, "killed": True,
                "latitude": False, "longitude": False, "severity": False},
    color_discrete_map=SEVERITY_COLORS, zoom=9.5, height=520,
)
fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), map_style="open-street-map")
st.plotly_chart(fig_map, width="stretch")

# ── Fatal Crash Table ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Fatal Crashes (Sampled Year)")
fatal = sample_filt[sample_filt["severity"] == "Fatal"].sort_values("crash_date", ascending=False)[
    ["crash_date", "borough", "street", "injured", "killed", "factor"]
]
if len(fatal):
    st.dataframe(fatal.reset_index(drop=True), width="stretch")
else:
    st.info("No fatal crashes in the current filter.")
