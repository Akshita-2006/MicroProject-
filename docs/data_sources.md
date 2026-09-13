# Data Sources Investigation

## Air-Quality Data

### CPCB

The project synopsis identifies CPCB monitoring-station data as the primary intended source. CPCB is authoritative for Indian air-quality categories and station monitoring.

Implementation note: direct CPCB access may involve repository pages, downloads, or access constraints. If direct extraction is difficult, a CPCB-derived dataset with transparent provenance can be used, but its license and limitations must be documented.

### CPCB-Derived Dataset Candidate

Candidate: `Vonter/india-cpcb-aqi` on GitHub.

Observed properties from repository documentation:

- Source: CPCB Data Repository and CPCB AQI Repository.
- Data forms: 15-minute station-level pollutant measurements and hourly station-level AQI measurements.
- Available formats: Parquet and compressed CSV releases.
- License: Open Database License with attribution/share-alike conditions; some individual database contents are copyright CPCB.
- Usefulness: likely the best reproducible route if releases can be downloaded.

Risk: must inspect the actual downloaded files before selecting Delhi stations, date range, and variables.

### OpenAQ

OpenAQ API v3 provides locations, sensors, measurements, and hourly measurements.

Important limitation:

- API access requires an `X-API-Key`.
- New Delhi location data exists in OpenAQ, but direct API acquisition requires a user-provided key or another allowed download route.

OpenAQ remains useful for provenance and fallback access where key/download is available.

### Kaggle

Kaggle has Delhi PM2.5 datasets sourced from OpenAQ. This is not the preferred primary route because it is a secondary dataset, may require Kaggle credentials, and may include only PM2.5. It can be used only if better sources are blocked and limitations are documented.

## Weather Data

### Open-Meteo Historical Weather API

Open-Meteo provides historical hourly weather variables and supports Delhi coordinates.

Candidate variables:

- temperature_2m
- relative_humidity_2m
- wind_speed_10m
- wind_direction_10m
- pressure_msl
- precipitation

Usefulness:

- reproducible API;
- no manual web export required in normal use;
- hourly alignment matches the project design.

Risk:

- weather is grid/reanalysis-style data rather than station-specific pollution-site meteorology.
