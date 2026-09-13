#!/usr/bin/env python3
"""Parse CPCB air quality data (CSV for raw measurements, XLS for AQI) into year-wise Parquet files."""
import argparse
import io
import json
import logging
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import polars as pl
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

META_COLS = {"Station ID", "State", "City", "Station Name", "File Path", "Timestamp"}
BATCH_SIZE = 32
CSV_READ_OPTS = {"null_values": ["NA", "NaN"], "infer_schema_length": 1000}
SAMPLE_READ_OPTS = {**CSV_READ_OPTS, "infer_schema_length": 100, "n_rows": 100}


@dataclass
class FileInfo:
    """Metadata for a CSV or XLS file to process."""
    station_id: str
    station_name: str
    state: str
    city: str
    source: str
    from_zip: bool
    is_aqi: bool = False
    zip_path: Optional[Path] = None
    member_name: Optional[str] = None
    path: Optional[Path] = None


@dataclass(frozen=True)
class OutputConfig:
    """Configuration for output file naming."""
    year_prefix: str
    latest_filename: str


OUTPUT_CONFIGS = {
    True: OutputConfig("cpcb-aqi-", "latest.parquet"),  # AQI
    False: OutputConfig("cpcb-air-quality-", "latest-air-quality.parquet"),  # Raw
}


# ============================================================================
# Station Metadata
# ============================================================================

def load_stations_data(path: Path) -> Dict:
    """Load station metadata from JSON file."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_mappings(stations_data: Dict) -> tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Build city_state, station_city, and station_name mappings."""
    dropdown = stations_data.get("dropdown", {})
    cities = dropdown.get("cities", {})
    stations = dropdown.get("stations", {})

    city_state = {c["value"]: state for state, city_list in cities.items() for c in city_list}
    station_city = {}
    station_name = {}
    for city, station_list in stations.items():
        for s in station_list:
            sid = s["value"]
            station_city[sid] = city
            station_name[sid] = s.get("label", sid)

    return city_state, station_city, station_name


def get_station_metadata(
    station_id: str,
    city_state: Dict[str, str],
    station_city: Dict[str, str],
    station_name: Dict[str, str],
) -> tuple[str, str, str]:
    """Get metadata for a station."""
    city = station_city.get(station_id, "Unknown")
    state = city_state.get(city, "Unknown") if city != "Unknown" else "Unknown"
    name = station_name.get(station_id, station_id)
    return state, city, name


# ============================================================================
# File Parsing
# ============================================================================

def _find_timestamp_column(df: pl.DataFrame) -> Optional[str]:
    """Find timestamp column in DataFrame."""
    # Try common names first
    for col in ["Date", "date", "DATE", "Timestamp", "timestamp", "TIMESTAMP"]:
        if col in df.columns:
            return col
    # Try first datetime-like column
    for col in df.columns:
        if df[col].dtype in [pl.Date, pl.Datetime]:
            return col
    return None


def _normalize_timestamp(df: pl.DataFrame) -> pl.DataFrame:
    """Normalize timestamp column to UTC Datetime."""
    if df["Timestamp"].dtype == pl.Utf8:
        return (
            df.with_columns(
                pl.col("Timestamp")
                .str.strip_chars()
                .str.strptime(pl.Datetime, strict=False)
                .dt.replace_time_zone("UTC")
            )
            .drop_nulls(subset=["Timestamp"])
        )
    elif df["Timestamp"].dtype == pl.Date:
        return df.with_columns(pl.col("Timestamp").cast(pl.Datetime).dt.replace_time_zone("UTC"))
    return df


def _add_metadata(df: pl.DataFrame, file_info: FileInfo) -> pl.DataFrame:
    """Add metadata columns to DataFrame."""
    meta = {
        "Station ID": file_info.station_id,
        "State": file_info.state or "Unknown",
        "City": file_info.city or "Unknown",
        "Station Name": file_info.station_name or file_info.station_id,
        "File Path": file_info.source,
    }
    df = df.with_columns([pl.lit(v).alias(k) for k, v in meta.items()])
    # Reorder: metadata first, then timestamp, then other columns
    meta_cols = list(meta.keys()) + ["Timestamp"]
    other_cols = [c for c in df.columns if c not in meta_cols]
    return df.select(meta_cols + other_cols)


def parse_file(content: bytes | Path, file_info: FileInfo) -> Optional[pl.DataFrame]:
    """Parse file content (CSV or XLS) into a DataFrame with metadata."""
    try:
        if file_info.is_aqi:
            df = pl.read_excel(
                io.BytesIO(content) if isinstance(content, bytes) else content,
                engine="openpyxl",
                null_values=["NA", "NaN", ""],
                infer_schema_length=1000,
            )
            # Find and rename timestamp column
            date_col = _find_timestamp_column(df)
            if date_col is None:
                logger.warning("No timestamp column found in %s", file_info.source)
                return None
            if date_col != "Timestamp":
                df = df.rename({date_col: "Timestamp"})
        else:
            df = pl.read_csv(
                io.BytesIO(content) if isinstance(content, bytes) else content,
                **CSV_READ_OPTS
            )
            if "Timestamp" not in df.columns:
                logger.warning("No 'Timestamp' column in %s", file_info.source)
                return None
    except Exception as e:
        logger.error("Failed to read %s from %s: %s", "XLS" if file_info.is_aqi else "CSV", file_info.source, e)
        return None

    # Normalize timestamp and add metadata
    df = _normalize_timestamp(df)
    if df.height == 0:
        return None

    return _add_metadata(df, file_info)


# ============================================================================
# File Discovery
# ============================================================================

@contextmanager
def zip_file_manager():
    """Context manager for caching zip files."""
    cache: Dict[Path, zipfile.ZipFile] = {}
    try:
        yield cache
    finally:
        for zf in cache.values():
            zf.close()
        cache.clear()


def iter_station_files(
    raw_dir: Path,
    city_state: Dict[str, str],
    station_city: Dict[str, str],
    station_name: Dict[str, str],
    is_aqi: bool = False,
) -> Iterable[FileInfo]:
    """Yield FileInfo for each CSV or XLS file in the raw directory."""
    extension = ".xls" if is_aqi else ".csv"
    suffix = "_aqi" if is_aqi else ""

    # Process zip archives
    for zip_path in raw_dir.glob(f"*{suffix}.zip"):
        station_id = zip_path.stem.replace("_aqi", "")
        state, city, sname = get_station_metadata(station_id, city_state, station_city, station_name)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member_name in zf.namelist():
                    if member_name.lower().endswith(extension):
                        yield FileInfo(
                            station_id=station_id,
                            station_name=sname,
                            state=state,
                            city=city,
                            source=f"{zip_path.name}:{member_name}",
                            from_zip=True,
                            is_aqi=is_aqi,
                            zip_path=zip_path,
                            member_name=member_name,
                        )
        except zipfile.BadZipFile:
            logger.error("Skipping corrupted zip file: %s", zip_path)

    # Process legacy directory layout
    for station_dir in raw_dir.iterdir():
        if not station_dir.is_dir():
            continue
        station_id = station_dir.name
        state, city, sname = get_station_metadata(station_id, city_state, station_city, station_name)
        for file_path in station_dir.glob(f"*{extension}"):
            yield FileInfo(
                station_id=station_id,
                station_name=sname,
                state=state,
                city=city,
                source=str(file_path),
                from_zip=False,
                is_aqi=is_aqi,
                path=file_path,
            )


def read_file_content(file_info: FileInfo, zip_cache: Dict[Path, zipfile.ZipFile]) -> Optional[bytes]:
    """Read file content from zip or disk."""
    try:
        if file_info.from_zip:
            if file_info.zip_path not in zip_cache:
                zip_cache[file_info.zip_path] = zipfile.ZipFile(file_info.zip_path, "r")
            return zip_cache[file_info.zip_path].read(file_info.member_name)
        return file_info.path.read_bytes()
    except Exception as e:
        logger.error("Failed to read %s: %s", file_info.source, e)
        return None


# ============================================================================
# Schema Analysis
# ============================================================================

def infer_schema(content: bytes | Path, is_aqi: bool = False) -> Optional[Dict[str, pl.DataType]]:
    """Infer schema from a CSV or XLS sample."""
    try:
        if is_aqi:
            df = pl.read_excel(
                io.BytesIO(content) if isinstance(content, bytes) else content,
                engine="openpyxl",
                null_values=["NA", "NaN", ""],
                infer_schema_length=100,
                n_rows=100,
            )
        else:
            df = pl.read_csv(io.BytesIO(content) if isinstance(content, bytes) else content, **SAMPLE_READ_OPTS)
        return dict(df.schema)
    except Exception:
        return None


def compute_dtype_coercions(dtype_stats: Dict[str, set[pl.DataType]]) -> Dict[str, pl.DataType]:
    """Compute dtype coercions for String/numeric conflicts."""
    numeric_types = {pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64}
    return {
        name: pl.Float64
        for name, dtypes in dtype_stats.items()
        if len(dtypes) > 1 and pl.Utf8 in dtypes and any(dt in numeric_types for dt in dtypes)
    }


def gather_schema_stats(files: List[FileInfo], zip_cache: Dict[Path, zipfile.ZipFile]) -> Dict[str, set[pl.DataType]]:
    """Gather dtype statistics from CSV/XLS samples."""
    dtype_stats: Dict[str, set[pl.DataType]] = {}
    for file_info in tqdm(files, desc="Analyzing schemas", unit="file"):
        content = read_file_content(file_info, zip_cache)
        if content is None:
            continue
        schema = infer_schema(content, is_aqi=file_info.is_aqi)
        if schema:
            for name, dtype in schema.items():
                if name not in META_COLS:
                    dtype_stats.setdefault(name, set()).add(dtype)
    return dtype_stats


def apply_dtype_coercions(df: pl.DataFrame, coercions: Dict[str, pl.DataType]) -> pl.DataFrame:
    """Apply dtype coercions to resolve conflicts."""
    if not coercions:
        return df
    casts = [
        pl.col(name).cast(target_dtype, strict=False)
        for name, target_dtype in coercions.items()
        if name in df.columns and df.schema[name] != target_dtype
    ]
    return df.with_columns(casts) if casts else df


# ============================================================================
# Batch Processing
# ============================================================================

def process_files(
    files: List[FileInfo],
    dtype_coercions: Dict[str, pl.DataType],
    temp_path: Path,
    zip_cache: Dict[Path, zipfile.ZipFile],
) -> tuple[List[Path], Dict[int, List[Path]]]:
    """Process files into batches and map batches to years."""
    batch_files: List[Path] = []
    current_batch: List[pl.DataFrame] = []
    batch_counter = 0

    for file_info in tqdm(files, desc="Processing files", unit="file"):
        content = read_file_content(file_info, zip_cache)
        if content is None:
            continue

        df = parse_file(content, file_info)
        if df is None:
            continue

        df = apply_dtype_coercions(df, dtype_coercions)
        current_batch.append(df)

        if len(current_batch) >= BATCH_SIZE:
            batch_file = temp_path / f"batch_{batch_counter:06d}.parquet"
            pl.concat(current_batch, how="vertical", rechunk=False).write_parquet(batch_file, compression="snappy")
            batch_files.append(batch_file)
            current_batch.clear()
            batch_counter += 1

    # Write final batch
    if current_batch:
        batch_file = temp_path / f"batch_{batch_counter:06d}.parquet"
        pl.concat(current_batch, how="vertical", rechunk=False).write_parquet(batch_file, compression="snappy")
        batch_files.append(batch_file)

    # Map batches to years
    logger.info("Mapping batches to years...")
    year_to_batches: Dict[int, List[Path]] = {}
    for batch_file in tqdm(batch_files, desc="Analyzing batch years", unit="batch"):
        try:
            years = pl.scan_parquet(str(batch_file)).select(pl.col("Timestamp").dt.year().alias("Year")).collect()["Year"].unique().to_list()
            for year in years:
                year_to_batches.setdefault(year, []).append(batch_file)
        except Exception as e:
            logger.warning("Failed to extract years from %s: %s", batch_file, e)

    return batch_files, year_to_batches


# ============================================================================
# Output Generation
# ============================================================================

def build_lazy_pipeline(parquet_files: List[Path], filter_year: Optional[int] = None) -> pl.LazyFrame:
    """Build lazy evaluation pipeline for combining parquet files."""
    lazy = pl.concat([pl.scan_parquet(str(f)) for f in parquet_files])

    if filter_year is not None:
        lazy = lazy.filter(pl.col("Timestamp").dt.year() == filter_year)

    # Get data columns (non-metadata)
    sample = pl.scan_parquet(str(parquet_files[0])).head(1).collect()
    data_cols = [c for c in sample.columns if c not in META_COLS]

    # Filter rows with at least one data value
    if data_cols:
        lazy = lazy.filter(pl.any_horizontal([pl.col(c).is_not_null() for c in data_cols]))

    return lazy.sort(["State", "City", "Station Name", "Timestamp"])


def collect_with_fallback(lazy: pl.LazyFrame) -> pl.DataFrame:
    """Collect lazy frame with streaming engine, fallback to regular collect."""
    try:
        return lazy.collect(engine="streaming").rechunk()
    except (TypeError, ValueError):
        return lazy.collect().rechunk()


def process_year(year: int, batch_files: List[Path], out_dir: Path, is_aqi: bool = False) -> Optional[Path]:
    """Process and save data for a single year (Parquet and CSV.zip)."""
    config = OUTPUT_CONFIGS[is_aqi]
    year_file = out_dir / f"{config.year_prefix}{year}.parquet"
    csv_zip_file = out_dir / f"{config.year_prefix}{year}.csv.zip"

    if year_file.exists() and csv_zip_file.exists():
        logger.info("Skipping year %d - files already exist", year)
        return year_file

    logger.info("Processing year %d (%d batches)...", year, len(batch_files))
    lazy = build_lazy_pipeline(batch_files, filter_year=year)
    df = collect_with_fallback(lazy)
    logger.info("Year %d: %d rows", year, df.height)

    # Save Parquet
    df.drop("File Path").write_parquet(year_file, compression="snappy")
    logger.info("Saved %s", year_file)

    # Save CSV.zip
    export_df = df.drop("File Path")
    csv_buffer = io.BytesIO()
    export_df.write_csv(csv_buffer, include_header=True)
    with zipfile.ZipFile(csv_zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{config.year_prefix}{year}.csv", csv_buffer.getvalue())
    csv_buffer.close()
    logger.info("Saved %s", csv_zip_file)

    return year_file


def generate_latest_parquet(out_dir: Path, is_aqi: bool = False) -> None:
    """Generate latest.parquet with data from the last week of the most recent year."""
    config = OUTPUT_CONFIGS[is_aqi]
    existing_years = []

    for parquet_file in out_dir.glob(f"{config.year_prefix}*.parquet"):
        try:
            year_str = parquet_file.stem.replace(config.year_prefix, "")
            if year_str.isdigit():
                existing_years.append(int(year_str))
        except (ValueError, AttributeError):
            continue

    if not existing_years:
        logger.warning("No year files found to generate %s", config.latest_filename)
        return

    latest_year = max(existing_years)
    latest_file = out_dir / f"{config.year_prefix}{latest_year}.parquet"

    if not latest_file.exists():
        logger.warning("Latest year file %s does not exist, skipping %s generation", latest_file, config.latest_filename)
        return

    logger.info("Generating %s from year %d (last week)...", config.latest_filename, latest_year)

    try:
        df = pl.read_parquet(latest_file)
        if df.height == 0:
            logger.warning("No data in %s, skipping %s generation", latest_file, config.latest_filename)
            return

        cutoff_date = df["Timestamp"].max() - timedelta(days=7)
        latest_df = df.filter(pl.col("Timestamp") >= cutoff_date)

        logger.info(
            "Latest week: %d rows from %s to %s",
            latest_df.height,
            latest_df["Timestamp"].min(),
            latest_df["Timestamp"].max(),
        )

        latest_path = out_dir / config.latest_filename
        latest_df.write_parquet(latest_path, compression="snappy")
        logger.info("Saved %s", latest_path)
    except Exception as e:
        logger.error("Error generating %s: %s", config.latest_filename, e)


# ============================================================================
# Main Workflow
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Parse CPCB air quality data files into year-wise Parquet files")
    parser.add_argument(
        "--data-type",
        type=str,
        choices=["raw", "aqi"],
        default="raw",
        help="Type of data to parse: 'raw' (15-min) or 'aqi' (daily). Default: raw",
    )
    args = parser.parse_args()

    is_aqi = args.data_type == "aqi"
    data_type_label = "AQI" if is_aqi else "raw measurement"
    logger.info("Starting %s parsing process...", data_type_label)

    raw_dir = Path("raw")
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    if not raw_dir.exists():
        logger.error("Directory %s does not exist!", raw_dir)
        return

    # Load station metadata
    try:
        stations_data = load_stations_data(Path("stations.json"))
        city_state, station_city, station_name = build_mappings(stations_data)
        logger.info("Loaded %d cities and %d stations", len(city_state), len(station_city))
    except Exception as e:
        logger.error("Error loading stations metadata: %s", e)
        logger.info("Proceeding without metadata mapping...")
        city_state, station_city, station_name = {}, {}, {}

    # Discover files
    files = list(iter_station_files(raw_dir, city_state, station_city, station_name, is_aqi=is_aqi))
    file_type = "XLS" if is_aqi else "CSV"
    logger.info("Found %d %s files to process", len(files), file_type)

    if not files:
        logger.error("No %s files found to process!", file_type)
        return

    # Analyze schemas
    with zip_file_manager() as zip_cache:
        dtype_stats = gather_schema_stats(files, zip_cache)

    dtype_coercions = compute_dtype_coercions(dtype_stats)
    if dtype_coercions:
        logger.info("Will coerce %d columns to Float64", len(dtype_coercions))

    # Process files
    with tempfile.TemporaryDirectory(prefix="cpcb_parse_") as temp_dir:
        temp_path = Path(temp_dir)
        with zip_file_manager() as zip_cache:
            batch_files, year_to_batches = process_files(files, dtype_coercions, temp_path, zip_cache)

        if batch_files and year_to_batches:
            years = sorted(year_to_batches.keys())
            logger.info("Processing %d years: %s", len(years), years)
            for year in years:
                process_year(year, year_to_batches[year], out_dir, is_aqi=is_aqi)
        else:
            logger.warning("No new data was processed, but will check for existing files...")

    # Generate latest.parquet
    generate_latest_parquet(out_dir, is_aqi=is_aqi)
    logger.info("Processing complete!")


if __name__ == "__main__":
    main()
