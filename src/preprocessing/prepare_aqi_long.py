"""Convert wide CPCB-derived hourly AQI data into long hourly records."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


HOUR_COLUMNS = [f"{hour:02d}:00:00" for hour in range(24)]


def load_and_filter_delhi(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    missing = [col for col in HOUR_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected hour columns: {missing}")
    return df[df["City"].astype("string").str.lower() == "delhi"].copy()


def to_long_hourly(df: pd.DataFrame) -> pd.DataFrame:
    id_columns = ["Station ID", "State", "City", "Station Name", "Date"]
    long_df = df.melt(
        id_vars=id_columns,
        value_vars=HOUR_COLUMNS,
        var_name="hour",
        value_name="aqi",
    )
    long_df["timestamp"] = pd.to_datetime(
        long_df["Date"].astype("string") + " " + long_df["hour"].astype("string"),
        errors="coerce",
    )
    long_df = long_df.rename(
        columns={
            "Station ID": "station_id",
            "State": "state",
            "City": "city",
            "Station Name": "station_name",
        }
    )
    long_df["aqi"] = pd.to_numeric(long_df["aqi"], errors="coerce")
    return long_df[
        ["timestamp", "station_id", "state", "city", "station_name", "aqi"]
    ].sort_values(["station_id", "timestamp"])


def write_summary(df: pd.DataFrame, output_path: Path) -> None:
    summary = (
        df.groupby(["station_id", "station_name"], dropna=False)
        .agg(
            rows=("aqi", "size"),
            non_missing_aqi=("aqi", "count"),
            missing_aqi=("aqi", lambda values: int(values.isna().sum())),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
            mean_aqi=("aqi", "mean"),
        )
        .reset_index()
    )
    summary["coverage_fraction"] = summary["non_missing_aqi"] / summary["rows"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.sort_values(
        ["coverage_fraction", "non_missing_aqi"], ascending=[False, False]
    ).to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/cpcb-aqi.csv.gz")
    parser.add_argument("--output", default="data/interim/delhi_aqi_hourly_long.csv")
    parser.add_argument("--station-summary", default="reports/tables/delhi_station_summary.csv")
    args = parser.parse_args()

    delhi_wide = load_and_filter_delhi(Path(args.input))
    hourly = to_long_hourly(delhi_wide)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(output_path, index=False)
    write_summary(hourly, Path(args.station_summary))

    print(f"Delhi station-day rows: {len(delhi_wide):,}")
    print(f"Delhi hourly rows: {len(hourly):,}")
    print(f"Stations: {hourly['station_id'].nunique():,}")
    print(f"Timestamp range: {hourly['timestamp'].min()} to {hourly['timestamp'].max()}")
    print(f"Non-missing AQI: {hourly['aqi'].notna().sum():,}")
    print(f"Missing AQI: {hourly['aqi'].isna().sum():,}")
    print(f"Saved hourly data to {output_path}")
    print(f"Saved station summary to {args.station_summary}")


if __name__ == "__main__":
    main()
