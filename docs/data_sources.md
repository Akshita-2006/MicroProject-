# Data used by the project

## AQI

The current seven-station forecasts use 2017–2023 hourly AQI from [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi), a public archive of CPCB data. The local file matches the saved source version. The selected station names and agencies also match an official CPCB station list.

The archive has faulty station IDs, and the AQI timezone is assumed to be IST. Station names remain the working keys until IDs can be verified.

An official CPCB January 2026 hourly AQI workbook for Anand Vihar is stored under `data/raw/official_aqi/`. It covers one station and one month, so it cannot yet train or test an expanded system.

## Pollutant measurements

The 2017, 2024 and 2025 releases contain pollutant concentrations, not the hourly AQI target used by the current models. The Delhi subsets contain 1,368,606 rows for 2024 and 1,366,609 for 2025.

Official exports for Alipur and Anand Vihar were saved to compare with the mirror data. They support the visible 15-minute interval labels for those samples only. The source timezone, quality flags, reporting delay and broader station/date coverage still need checking. No AQI target is derived from pollutant concentrations.

## Weather

The project uses Open-Meteo historical weather for one Delhi location: temperature, humidity, wind speed and direction, pressure and rainfall. The existing modelling data covers 2017–2023. A second checked regional series covers 1 January 2024 through 9 September 2026.

This is regional weather, not weather measured at each pollution station. Historical weather may have been revised after the observation time, so it does not prove what a live service would have known at that time.

## Evidence and licensing

Source copies, hashes, official exports and attribution notices are in `reports/source_evidence/`. See the [recent data audit](../reports/recent_data_audit.md), [technical methodology](methodology_v2.md) and [remaining checklist](remaining_checklist.md) for the precise limits before newer data can be used.
