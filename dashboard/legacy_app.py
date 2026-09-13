"""Streamlit dashboard for the Delhi AQI early-warning prototype."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "shadipur_aqi_weather_hourly.csv"
RESULTS_PATH = ROOT / "experiments" / "results" / "initial_forecast_results.csv"
EVENT_RESULTS_PATH = ROOT / "experiments" / "results" / "event_detection_results.csv"
PREDICTIONS_PATH = ROOT / "experiments" / "results" / "xgboost_test_predictions.csv"


st.set_page_config(page_title="Delhi AQI Early Warning", layout="wide")
st.title("Delhi AQI Episode Early-Warning Prototype")

if not DATA_PATH.exists():
    st.error("Processed dataset not found. Run preprocessing first.")
    st.stop()

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
station_name = df["station_name"].dropna().iloc[0]

st.caption(
    "Research prototype only. This dashboard is not an official CPCB alert or medical advisory."
)

metric_cols = st.columns(4)
metric_cols[0].metric("Station", station_name)
metric_cols[1].metric("Hourly rows", f"{len(df):,}")
metric_cols[2].metric("Non-missing AQI", f"{df['aqi'].notna().sum():,}")
metric_cols[3].metric("Date range", f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}")

recent_days = st.slider("Recent history window", min_value=7, max_value=120, value=30, step=1)
recent = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(days=recent_days)]
fig = px.line(recent, x="timestamp", y="aqi", title=f"Recent AQI History - Last {recent_days} Days")
fig.add_hline(y=301, line_dash="dash", annotation_text="Very Poor threshold")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Forecast Model Results")
    if RESULTS_PATH.exists():
        results = pd.read_csv(RESULTS_PATH)
        st.dataframe(results, use_container_width=True, hide_index=True)
    else:
        st.info("Initial forecast results are not available yet.")

with right:
    st.subheader("Event Warning Results")
    if EVENT_RESULTS_PATH.exists():
        event_results = pd.read_csv(EVENT_RESULTS_PATH)
        st.dataframe(event_results, use_container_width=True, hide_index=True)
    else:
        st.info("Event detection results will appear after the ablation script runs.")

st.subheader("Predicted Episode View")
if PREDICTIONS_PATH.exists():
    predictions = pd.read_csv(PREDICTIONS_PATH, parse_dates=["timestamp"])
    horizon = st.selectbox("Forecast horizon", sorted(predictions["horizon"].unique()))
    horizon_predictions = predictions[predictions["horizon"] == horizon].tail(240)
    fig_pred = px.line(
        horizon_predictions,
        x="timestamp",
        y=["target", "prediction"],
        title=f"Actual vs Predicted AQI - {horizon}h Horizon",
    )
    fig_pred.add_hline(y=301, line_dash="dash", annotation_text="Very Poor threshold")
    st.plotly_chart(fig_pred, use_container_width=True)
else:
    st.info("Prediction timeline will appear after event experiments complete.")
