#!/usr/bin/env python3
"""Fetch CPCB air quality data (raw measurements or AQI) from Indian air quality stations."""
import argparse
import base64
import json
import logging
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
from urllib.parse import quote

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALL_STATIONS_URL = "https://airquality.cpcb.gov.in/dataRepository/all_india_stationlist"
FILE_PATH_URL = "https://airquality.cpcb.gov.in/dataRepository/file_Path"
DOWNLOAD_BASE_URL = "https://airquality.cpcb.gov.in/dataRepository/download_file"


@dataclass(frozen=True)
class DataTypeConfig:
    """Configuration for a data type (raw or AQI)."""
    frequency: str
    api_type: str
    file_ext: str
    zip_suffix: str


DATA_TYPE_CONFIGS = {
    "raw": DataTypeConfig("15min", "raw", ".csv", ""),
    "aqi": DataTypeConfig("daily", "stationLevel", ".xls", "_aqi"),
}


class CPCBClient:
    """Client for interacting with CPCB data repository APIs."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:145.0) Gecko/20100101 Firefox/145.0",
            "Accept": "q=0.8;application/json;q=0.9",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        })

    def fetch_stations_list(self, out_path: Path = Path("stations.json")) -> Dict[str, Any]:
        """Fetch station list from CPCB API and save to JSON."""
        logger.info("Fetching station list from CPCB API...")
        try:
            resp = self.session.post(ALL_STATIONS_URL, data="e30=", timeout=30)
            resp.raise_for_status()
            decoded = base64.b64decode(resp.text).decode("utf-8")
            data = json.loads(decoded)
            out_path.write_text(decoded, encoding="utf-8")
            logger.info("Station list saved to %s", out_path)
            return data
        except Exception as e:
            logger.error("Error fetching station list: %s", e)
            raise

    @staticmethod
    def _build_payload(
        station_id: str,
        station_name: str,
        config: DataTypeConfig,
        state: str = "",
        city: str = "",
        year: str = "",
    ) -> str:
        """Build base64-encoded payload for file_Path endpoint."""
        payload = {
            "station_id": station_id,
            "station_name": station_name,
            "state": state,
            "city": city,
            "frequency": config.frequency,
            "dataType": config.api_type,
        }
        if year:
            payload["year"] = year
        return base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()

    def fetch_station_file_list(
        self,
        station_id: str,
        station_name: str,
        config: DataTypeConfig,
        state: str = "",
        city: str = "",
        year: str = "",
    ) -> List[Dict[str, Any]]:
        """Fetch file list for a station."""
        payload = self._build_payload(station_id, station_name, config, state, city, year)
        time.sleep(1)  # Be polite

        try:
            resp = self.session.post(FILE_PATH_URL, data=payload, timeout=30)
            resp.raise_for_status()
            data = json.loads(base64.b64decode(resp.text).decode("utf-8"))

            if data.get("status") != "success":
                logger.warning("file_Path returned non-success for %s: %s", station_id, data.get("status"))
                return []

            entries = data.get("data", [])
            if not isinstance(entries, list):
                logger.warning("Unexpected data structure for %s: %r", station_id, entries)
                return []
            return entries
        except Exception as e:
            logger.error("Error calling file_Path for %s: %s", station_id, e)
            return []

    @staticmethod
    def _get_zip_path(station_id: str, config: DataTypeConfig) -> Path:
        """Get path to station zip archive."""
        raw_dir = Path("raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        return raw_dir / f"{station_id}{config.zip_suffix}.zip"

    @staticmethod
    def _get_existing_years(zip_path: Path, config: DataTypeConfig) -> Set[str]:
        """Get set of years already in zip archive."""
        if not zip_path.exists():
            return set()

        years = set()
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    if name.lower().endswith(config.file_ext):
                        stem = Path(name).stem
                        if stem.isdigit():
                            years.add(stem)
        except zipfile.BadZipFile:
            logger.error("Corrupted zip file: %s", zip_path)
        return years

    def _download_file(self, filepath: str, max_retries: int = 3) -> bytes | None:
        """Download file content with retries."""
        url = f"{DOWNLOAD_BASE_URL}?file_name={quote(filepath)}"

        for attempt in range(max_retries):
            try:
                logger.info("Downloading %s (attempt %d/%d)", filepath, attempt + 1, max_retries)
                with self.session.get(url, stream=True, timeout=60) as resp:
                    resp.raise_for_status()
                    return b"".join(resp.iter_content(chunk_size=8192))
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error("All download attempts failed for %s", filepath)
                    return None
                logger.warning("Download attempt %d/%d failed for %s: %s", attempt + 1, max_retries, filepath, e)
                time.sleep(2**attempt)
        return None

    def download_entries_to_zip(
        self,
        entries: Iterable[Dict[str, Any]],
        station_id: str,
        config: DataTypeConfig,
    ) -> tuple[int, int]:
        """Download files for a station into a zip archive."""
        zip_path = self._get_zip_path(station_id, config)
        existing_years = self._get_existing_years(zip_path, config)
        attempted = downloaded = 0

        with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            for entry in entries:
                filepath = entry.get("filepath")
                year = str(entry.get("year", "unknown"))

                if not filepath:
                    logger.warning("Missing filepath in entry for %s: %r", station_id, entry)
                    continue

                attempted += 1
                if year in existing_years:
                    logger.info("Skipping year %s for %s (already downloaded)", year, station_id)
                    continue

                content = self._download_file(filepath)
                if content is None:
                    continue

                zf.writestr(f"{year}{config.file_ext}", content)
                logger.info("Stored year %s for %s in %s", year, station_id, zip_path)
                downloaded += 1
                existing_years.add(year)

        return attempted, downloaded


def iter_all_stations(stations_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Flatten stations structure into a list of station dicts."""
    dropdown = stations_data.get("dropdown", {})
    stations_by_city = dropdown.get("stations", {})
    cities_by_state = dropdown.get("cities", {})

    # Build city->state mapping
    city_state = {c["value"]: state for state, city_list in cities_by_state.items() for c in city_list}

    # Build station list
    stations = []
    for city, station_list in stations_by_city.items():
        state = city_state.get(city, "")
        stations.extend({
            "station_id": s["value"],
            "station_name": s["label"],
            "city": city,
            "state": state,
        } for s in station_list)

    return stations


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CPCB air quality data")
    parser.add_argument("--year", type=str, help="Year to fetch (e.g., '2024'). Default: all years")
    parser.add_argument(
        "--data-type",
        type=str,
        choices=["raw", "aqi"],
        default="raw",
        help="Data type: 'raw' (15-min) or 'aqi' (daily). Default: raw",
    )
    args = parser.parse_args()

    client = CPCBClient()
    try:
        stations_data = client.fetch_stations_list()
    except Exception:
        logger.error("Aborting due to station list fetch failure")
        sys.exit(1)

    stations = iter_all_stations(stations_data)
    config = DATA_TYPE_CONFIGS[args.data_type]
    data_label = "AQI" if args.data_type == "aqi" else "raw measurement"

    logger.info(
        "Processing %d stations (year: %s, type: %s)",
        len(stations),
        args.year or "all",
        data_label,
    )

    total_attempted = total_downloaded = 0
    start_time = time.time()

    for idx, station in enumerate(stations, start=1):
        station_id = station["station_id"]
        logger.info(
            "[%d/%d] %s (%s) - %s, %s",
            idx,
            len(stations),
            station_id,
            station["station_name"],
            station.get("city", ""),
            station.get("state", ""),
        )

        entries = client.fetch_station_file_list(
            station_id,
            station["station_name"],
            config,
            state=station.get("state", ""),
            city=station.get("city", ""),
        )

        if not entries:
            logger.info("No entries found for %s", station_id)
            continue

        # Filter by year if specified
        if args.year:
            entries = [e for e in entries if str(e.get("year", "")) == str(args.year)]
            if not entries:
                logger.info("No entries for %s in year %s", station_id, args.year)
                continue

        logger.info("Found %d entries for %s", len(entries), station_id)
        attempted, downloaded = client.download_entries_to_zip(entries, station_id, config)
        total_attempted += attempted
        total_downloaded += downloaded

        # Progress summary every 20 stations
        if idx % 20 == 0:
            elapsed = time.time() - start_time
            rate = total_attempted / elapsed if elapsed > 0 else 0.0
            logger.info(
                "Progress: %d/%d stations, %d/%d files (%.2f files/sec)",
                idx,
                len(stations),
                total_downloaded,
                total_attempted,
                rate,
            )

    elapsed = time.time() - start_time
    logger.info("Done. Downloaded %d/%d files in %.1f seconds", total_downloaded, total_attempted, elapsed)


if __name__ == "__main__":
    main()
