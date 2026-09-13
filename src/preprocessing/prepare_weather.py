"""Convert Open-Meteo archive JSON into hourly CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def prepare_weather(input_path: Path) -> pd.DataFrame:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    hourly = payload["hourly"]
    df = pd.DataFrame(hourly)
    df = df.rename(columns={"time": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.sort_values("timestamp")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/weather_open_meteo_delhi_2017_2023.json")
    parser.add_argument("--output", default="data/interim/weather_open_meteo_delhi_hourly.csv")
    args = parser.parse_args()

    weather = prepare_weather(Path(args.input))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    weather.to_csv(output_path, index=False)

    print(f"Weather hourly rows: {len(weather):,}")
    print(f"Timestamp range: {weather['timestamp'].min()} to {weather['timestamp'].max()}")
    print(f"Saved weather data to {output_path}")


if __name__ == "__main__":
    main()
