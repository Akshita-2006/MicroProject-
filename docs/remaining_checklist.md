# Execution checklist - 25 September 2026

## Completed

- [x] Build, train and evaluate the 30-station historical AQI replay system for 2017-2023.
- [x] Add the 2024-2025 recorded-pollutant dashboard view and source release link.
- [x] Download, hash-check and filter the 2018 and 2019 annual concentration releases to Delhi.
- [x] Retain the existing 2017, 2024 and 2025 Delhi concentration releases.
- [x] Stage regional Delhi weather through 2026 and retain CPCB export evidence.
- [x] Add a voluntary, non-diagnostic precaution profile and pass 21 automated tests.

## Required for the 2017-2025 concentration model

- [x] Download, SHA-256 verify and filter the 2020, 2021, 2022 and 2023 annual concentration releases.
- [x] Assemble one continuous station/pollutant panel for 2017-2025.
- [x] Preserve station mapping and source units; measured missing values remain missing.
- [x] Train concentration models on 2017-2023, select settings on 2024 and evaluate once on untouched 2025.
- [x] Add evaluated concentration forecasts and their accuracy to the dashboard and reports.
- [x] Connect the sidebar and pollutant date controls, and add station-relative colour cards with plain-language pollutant effects.

## Required only to extend AQI testing through 2025

- [ ] Obtain a broad, official 2024-2025 hourly AQI target panel. The annual concentration release cannot substitute for this target.
- [ ] Retrain or evaluate the AQI model on the approved 2017-2025 target split after that panel passes validation.

## Future scope

- [ ] Live CPCB feed and real-time warning operation.

Source catalog: [annual CPCB-derived releases](https://github.com/Vonter/india-cpcb-aqi/releases). Release hashes are stored in `reports/source_evidence/recent_release_<year>.json`.
