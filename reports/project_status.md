# Project status - 25 September 2026

**Overall: expanded historical AQI system and 2017-2025 concentration-model evaluation complete.**

The dashboard provides 30-station AQI replay forecasts for 2023 and a separate recorded-concentration view for 2024-2025. It is not a live service or an official advisory.

## Completed

| Area | Current evidence |
|---|---|
| AQI forecasts | 30 eligible Delhi stations, 2017-2023 AQI/weather panel and direct 1-24 hour XGBoost models. |
| 2023 accuracy | Average MAE: 25.32 (1h), 48.20 (6h), 52.47 (12h), and 55.52 (24h) AQI points. |
| Dashboard | Shared station/date/time controls, AQI replay, episode timeline, accuracy tab, historical trends, source-linked pollutant records, station-relative colour cards with plain-language effects, and optional precaution profile. |
| Pollutant source releases | Continuous 2017-2025 annual releases are stored; newly acquired 2018-2023 files were SHA-256 checked. |
| Recent weather | Regional Delhi weather is staged through 9 September 2026. |
| Concentration evaluation | 2017-2023 training, 2024 validation and untouched 2025 testing completed for PM2.5, PM10, NO2, ozone, SO2, CO and benzene. |

## Current data plan

The continuous **2017-2025** pollutant panel contains 2,361,483 station-hour records across 30 stations. Models were fitted on 2017-2023, checked on 2024 and tested once on untouched 2025 data.

The AQI forecast cannot use that same 2017-2025 split yet because the public annual releases contain pollutant concentrations, not hourly AQI targets for 2024-2025. The existing AQI model therefore remains evaluated through 2023. No AQI value is calculated from raw concentration records.

## Remaining work

1. Acquire a broad official 2024-2025 hourly AQI target panel if the AQI model itself must also be tested through 2025.

## Sources

- [Public annual release catalog](https://github.com/Vonter/india-cpcb-aqi/releases)
- [CPCB source-access evidence](source_evidence/repository_access.md)
- [2018 release evidence](source_evidence/recent_release_2018.json)
- [2019 release evidence](source_evidence/recent_release_2019.json)
