"""Generate EDA tables and figures for the Shadipur AQI-weather dataset."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("reports/matplotlib_cache").resolve()))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def save_plot(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def run(input_path: Path, figure_dir: Path, table_dir: Path) -> None:
    df = pd.read_csv(input_path, parse_dates=["timestamp"])
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    summary = df.describe(include="all").transpose()
    summary.to_csv(table_dir / "eda_summary_statistics.csv")

    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_fraction"] = missing["missing_count"] / len(df)
    missing.to_csv(table_dir / "eda_missingness.csv")

    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["year"] = df["timestamp"].dt.year
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["season"] = df["month"].map(
        {
            12: "winter",
            1: "winter",
            2: "winter",
            3: "summer",
            4: "summer",
            5: "summer",
            6: "monsoon",
            7: "monsoon",
            8: "monsoon",
            9: "post_monsoon",
            10: "post_monsoon",
            11: "post_monsoon",
        }
    )

    grouped_tables = {
        "aqi_by_hour.csv": df.groupby("hour")["aqi"].agg(["count", "mean", "median", "max"]),
        "aqi_by_month.csv": df.groupby("month")["aqi"].agg(["count", "mean", "median", "max"]),
        "aqi_by_year.csv": df.groupby("year")["aqi"].agg(["count", "mean", "median", "max"]),
        "aqi_by_season.csv": df.groupby("season")["aqi"].agg(["count", "mean", "median", "max"]),
    }
    for name, table in grouped_tables.items():
        table.to_csv(table_dir / name)

    corr_cols = [
        "aqi",
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "wind_direction_10m",
        "pressure_msl",
        "precipitation",
    ]
    df[corr_cols].corr(numeric_only=True).to_csv(table_dir / "weather_aqi_correlations.csv")

    plt.figure(figsize=(10, 4))
    df.set_index("timestamp")["aqi"].resample("D").mean().plot()
    plt.title("Daily Mean AQI - Shadipur Delhi CPCB")
    plt.ylabel("AQI")
    save_plot(figure_dir / "daily_mean_aqi.png")

    plt.figure(figsize=(8, 4))
    df.groupby("hour")["aqi"].mean().plot(marker="o")
    plt.title("Mean AQI by Hour of Day")
    plt.ylabel("Mean AQI")
    plt.xlabel("Hour")
    save_plot(figure_dir / "aqi_by_hour.png")

    plt.figure(figsize=(8, 4))
    df.groupby("month")["aqi"].mean().plot(kind="bar")
    plt.title("Mean AQI by Month")
    plt.ylabel("Mean AQI")
    plt.xlabel("Month")
    save_plot(figure_dir / "aqi_by_month.png")

    plt.figure(figsize=(8, 4))
    df["aqi"].hist(bins=60)
    plt.title("AQI Distribution")
    plt.xlabel("AQI")
    plt.ylabel("Frequency")
    save_plot(figure_dir / "aqi_distribution.png")

    print(f"Saved EDA figures to {figure_dir}")
    print(f"Saved EDA tables to {table_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/shadipur_aqi_weather_hourly.csv")
    parser.add_argument("--figure-dir", default="reports/figures")
    parser.add_argument("--table-dir", default="reports/tables")
    args = parser.parse_args()
    run(Path(args.input), Path(args.figure_dir), Path(args.table_dir))


if __name__ == "__main__":
    main()
