"""Download hourly historical weather data from Open-Meteo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_HOURLY = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "pressure_msl",
    "precipitation",
]


def build_url(latitude: float, longitude: float, start_date: str, end_date: str) -> str:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(DEFAULT_HOURLY),
        "timezone": "Asia/Kolkata",
    }
    return "https://archive-api.open-meteo.com/v1/archive?" + urlencode(params)


def download_json(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--latitude", type=float, default=28.6139)
    parser.add_argument("--longitude", type=float, default=77.2090)
    parser.add_argument("--output", default="data/raw/weather_open_meteo_delhi.json")
    args = parser.parse_args()

    url = build_url(args.latitude, args.longitude, args.start_date, args.end_date)
    download_json(url, Path(args.output))
    print(f"Saved weather data to {args.output}")


if __name__ == "__main__":
    main()
