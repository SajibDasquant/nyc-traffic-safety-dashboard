# NYC Traffic Safety Analytics

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
![Fiverr](https://img.shields.io/badge/Hire%20me-Fiverr-1DBF73?logo=fiverr)

An interactive dashboard analyzing 2.27 million NYC motor vehicle collision records (2012-2026) — built with Streamlit and Plotly on official NYC Open Data.

---

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nyc-traffic-safety-dashboard-e9wpkafq8xdlehblttqybz.streamlit.app/)

---

## Project Story

**What is it?** An interactive dashboard covering every police-reported NYC vehicle collision from 2012–2026 — crash trends, injuries, fatalities, and hotspots.

**Why this data?** It's official NYC Open Data from MV-104AN police reports, the same foundation behind Vision Zero, NYC's initiative to eliminate traffic deaths.

**How was it built?** The raw file was 2.27M rows / 567MB — too large for a web app. Python and Pandas aggregate it into summary tables, and the app itself is built in Streamlit with Plotly for the charts and map.

**What does it show?** Citywide/borough trends, pedestrian and cyclist fatalities, top contributing factors, crash patterns by hour and day, and a severity-mapped crash view.

---

## Metrics tracked

| Metric | Description |
|---|---|
| Total Crashes | Crash count for the selected borough/year range |
| Persons Injured / Killed | Citywide injury and fatality totals |
| Fatalities per 1,000 Crashes | Normalized severity indicator |
| Pedestrian / Cyclist Fatalities | Vulnerable road user impact |

---

## Charts included

- Citywide monthly trend (crashes, injuries, fatalities)
- Crashes by borough and year
- Injury severity mix (fatal / injury / no injury)
- Top contributing factors and vehicle types involved
- Hour-of-day x day-of-week crash heatmap
- Geographic crash map (sampled recent year, color-coded by severity)
- Fatal crash detail table

---

## Data pipeline

The raw NYC Open Data export is 2.27M rows / 567MB — too large for GitHub (100MB limit) or Streamlit Cloud memory. `prep_data.py` aggregates it into small summary tables under `data/`:

| File | Contents |
|---|---|
| `monthly_citywide.csv` | Citywide crashes/injuries/fatalities by month |
| `yearly_borough.csv` | Yearly totals by borough, incl. pedestrian/cyclist/motorist breakdown |
| `contributing_factors.csv` | Top 15 contributing factors |
| `vehicle_types.csv` | Top 15 vehicle types involved |
| `hourly_dow.csv` | Crash counts by hour x day-of-week |
| `crash_sample.csv` | 25,000-point stratified sample (most recent complete year) with lat/lon, for the map |

---

## Quickstart

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Opens in your browser at `http://localhost:8501`

---

## Use your own data

1. Download a fresh export from [NYC Open Data - Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95).
2. Run:
   ```bash
   python prep_data.py your_export.csv
   ```

---

## Project structure

```
nyc-traffic-safety-dashboard/
├── dashboard.py       # Streamlit app
├── prep_data.py        # Raw export → aggregated data/*.csv
├── data/
│   ├── monthly_citywide.csv
│   ├── yearly_borough.csv
│   ├── contributing_factors.csv
│   ├── vehicle_types.csv
│   ├── hourly_dow.csv
│   └── crash_sample.csv
└── requirements.txt
```

---

## Hire me on Fiverr

Need a civic, safety, or operations analytics dashboard built with your data? [Order on Fiverr →](https://www.fiverr.com/SajibDasquant)
