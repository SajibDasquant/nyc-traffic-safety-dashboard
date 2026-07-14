"""One-off script: aggregates the raw NYC Motor Vehicle Collisions export
(2.27M rows, 567MB) into small summary tables under data/, since the raw
file is far too large for GitHub (100MB limit) or Streamlit Cloud memory.

Source: NYC Open Data - Motor Vehicle Collisions - Crashes
Run once whenever the source export is refreshed:

    python prep_data.py path/to/export.csv
"""
import sys

import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "export.csv"

COLS = [
    "CRASH DATE", "CRASH TIME", "BOROUGH", "LATITUDE", "LONGITUDE",
    "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED",
    "NUMBER OF PEDESTRIANS INJURED", "NUMBER OF PEDESTRIANS KILLED",
    "NUMBER OF CYCLIST INJURED", "NUMBER OF CYCLIST KILLED",
    "NUMBER OF MOTORIST INJURED", "NUMBER OF MOTORIST KILLED",
    "CONTRIBUTING FACTOR VEHICLE 1", "VEHICLE TYPE CODE 1",
    "ON STREET NAME",
]

print("Loading raw export (this can take a minute)...")
df = pd.read_csv(SRC, usecols=COLS, low_memory=False)
df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"])
df["YEAR"] = df["CRASH DATE"].dt.year
df["MONTH"] = df["CRASH DATE"].dt.to_period("M").astype(str)
df["HOUR"] = pd.to_datetime(df["CRASH TIME"], format="%H:%M", errors="coerce").dt.hour
df["DAY_OF_WEEK"] = df["CRASH DATE"].dt.day_name()
print(f"Loaded {len(df):,} rows, {df['CRASH DATE'].min().date()} to {df['CRASH DATE'].max().date()}")

# Drop the current partial month/year so trend charts don't show a fake dip
last_complete_month = df["MONTH"].max()
df_complete = df[df["MONTH"] < last_complete_month]

# ── Monthly citywide trend ───────────────────────────────────────────────
monthly = df_complete.groupby("MONTH").agg(
    crashes=("CRASH DATE", "count"),
    injured=("NUMBER OF PERSONS INJURED", "sum"),
    killed=("NUMBER OF PERSONS KILLED", "sum"),
).reset_index()
monthly.to_csv("data/monthly_citywide.csv", index=False)

# ── Yearly borough rollup ────────────────────────────────────────────────
yearly_borough = df_complete.dropna(subset=["BOROUGH"]).groupby(["YEAR", "BOROUGH"]).agg(
    crashes=("CRASH DATE", "count"),
    injured=("NUMBER OF PERSONS INJURED", "sum"),
    killed=("NUMBER OF PERSONS KILLED", "sum"),
    pedestrians_injured=("NUMBER OF PEDESTRIANS INJURED", "sum"),
    pedestrians_killed=("NUMBER OF PEDESTRIANS KILLED", "sum"),
    cyclists_injured=("NUMBER OF CYCLIST INJURED", "sum"),
    cyclists_killed=("NUMBER OF CYCLIST KILLED", "sum"),
    motorists_injured=("NUMBER OF MOTORIST INJURED", "sum"),
    motorists_killed=("NUMBER OF MOTORIST KILLED", "sum"),
).reset_index()
yearly_borough.to_csv("data/yearly_borough.csv", index=False)

# ── Contributing factors (top 15) ────────────────────────────────────────
factors = (
    df["CONTRIBUTING FACTOR VEHICLE 1"]
    .fillna("Unknown").replace("Unspecified", "Unknown")
    .value_counts().head(15).reset_index()
)
factors.columns = ["factor", "count"]
factors.to_csv("data/contributing_factors.csv", index=False)

# ── Vehicle types (top 15) ───────────────────────────────────────────────
vehicles = (
    df["VEHICLE TYPE CODE 1"]
    .fillna("Unknown").value_counts().head(15).reset_index()
)
vehicles.columns = ["vehicle_type", "count"]
vehicles.to_csv("data/vehicle_types.csv", index=False)

# ── Hour x day-of-week heatmap ───────────────────────────────────────────
hourly_dow = df.dropna(subset=["HOUR"]).groupby(["DAY_OF_WEEK", "HOUR"]).size().reset_index(name="crashes")
hourly_dow.to_csv("data/hourly_dow.csv", index=False)

# ── Sampled geocoded points for the map (most recent complete year) ─────
recent_year = df_complete["YEAR"].max()
geo = df_complete[
    (df_complete["YEAR"] == recent_year) & df_complete["LATITUDE"].notna() & df_complete["LONGITUDE"].notna()
    & (df_complete["LATITUDE"] != 0)
].copy()
sample_n = min(25_000, len(geo))
sample = geo.sample(n=sample_n, random_state=42)[
    ["CRASH DATE", "BOROUGH", "LATITUDE", "LONGITUDE", "ON STREET NAME",
     "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED", "CONTRIBUTING FACTOR VEHICLE 1"]
]
sample.columns = ["crash_date", "borough", "latitude", "longitude", "street", "injured", "killed", "factor"]
sample.to_csv("data/crash_sample.csv", index=False)

print(f"Wrote monthly_citywide.csv ({len(monthly)} rows)")
print(f"Wrote yearly_borough.csv ({len(yearly_borough)} rows)")
print(f"Wrote contributing_factors.csv ({len(factors)} rows)")
print(f"Wrote vehicle_types.csv ({len(vehicles)} rows)")
print(f"Wrote hourly_dow.csv ({len(hourly_dow)} rows)")
print(f"Wrote crash_sample.csv ({len(sample)} rows, year {recent_year})")
