"""Build a station-level hourly AQI plus weather modelling dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_dataset(aqi_path: Path, weather_path: Path, station_name: str) -> pd.DataFrame:
    aqi = pd.read_csv(aqi_path, parse_dates=["timestamp"])
    station = aqi[aqi["station_name"].astype("string").str.strip() == station_name].copy()
    if station.empty:
        raise ValueError(f"No rows found for station: {station_name}")

    weather = pd.read_csv(weather_path, parse_dates=["timestamp"])
    merged = station.merge(weather, on="timestamp", how="left")
    merged = merged.sort_values("timestamp")
    return merged


def write_quality_summary(df: pd.DataFrame, output_path: Path) -> None:
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_fraction"] = missing["missing_count"] / len(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    missing.to_csv(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aqi", default="data/interim/delhi_aqi_hourly_long.csv")
    parser.add_argument("--weather", default="data/interim/weather_open_meteo_delhi_hourly.csv")
    parser.add_argument("--station", default="Shadipur Delhi CPCB")
    parser.add_argument("--output", default="data/processed/shadipur_aqi_weather_hourly.csv")
    parser.add_argument("--quality-output", default="reports/tables/shadipur_model_dataset_missingness.csv")
    args = parser.parse_args()

    dataset = build_dataset(Path(args.aqi), Path(args.weather), args.station)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    write_quality_summary(dataset, Path(args.quality_output))

    print(f"Station: {args.station}")
    print(f"Rows: {len(dataset):,}")
    print(f"Timestamp range: {dataset['timestamp'].min()} to {dataset['timestamp'].max()}")
    print(f"Non-missing AQI: {dataset['aqi'].notna().sum():,}")
    print(f"Missing AQI: {dataset['aqi'].isna().sum():,}")
    print(f"Saved model dataset to {output_path}")
    print(f"Saved missingness summary to {args.quality_output}")


if __name__ == "__main__":
    main()
