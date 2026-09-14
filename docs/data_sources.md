# Data used by the project

## AQI

The current forecasts use 2017–2023 hourly AQI from [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi), a public archive of CPCB data. The local file matches the saved source version. Seven station names and agencies also match an official CPCB list.

These checks do not verify every reading. The archive contains faulty station IDs, and the AQI timezone is assumed to be IST. Station names are used until the IDs can be verified. Source copies, file hashes and attribution notices are in `reports/source_evidence/`.

## Pollutant measurements

The 2017, 2024 and 2025 releases were downloaded from the same archive. They contain pollutant concentrations, which differ from the AQI number predicted by the current models.

The Delhi subsets contain 1,368,606 rows for 2024 and 1,366,609 for 2025. These include missing values; a row does not necessarily contain a valid measurement. One ten-row Alipur sample matched the official 2025 table. Timezone, broader source checks and recent AQI targets remain unresolved, so these files are not used by the forecasting models.

See the [recent data audit](../reports/recent_data_audit.md) for evidence, quality checks and commands. No verified 2026 dataset is available in this project.

## Weather

The current dataset uses Open-Meteo historical weather for one Delhi location: temperature, humidity, wind speed and direction, pressure and rainfall. The saved response specifies IST and the units.

All seven stations use this regional weather. It is not a measurement at each pollution station. Historical weather can also be revised after the event, so it does not prove what data would have been available to a live service at that time.

## Source notices and further checks

Keep the archive's attribution and database notices with redistributed data. Copies are in `reports/source_evidence/`. OpenAQ and Kaggle were considered during the initial investigation but do not supply the current forecast inputs.

The [technical methodology](methodology_v2.md) records assumptions and references. The [remaining checklist](remaining_checklist.md) lists checks needed before recent data can be used.
