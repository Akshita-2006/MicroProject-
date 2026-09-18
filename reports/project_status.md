# Project status — 18 September 2026

**Overall: partly complete.** The working deliverable remains a seven-station historical AQI forecasting and episode-warning prototype evaluated on 2023. Recent source access and staging have improved, but no 2024–2026 forecast model has been trained or scored.

## Completed work

| Work | Evidence and scope |
|---|---|
| Historical modelling dataset | Seven stations, 2017–2023 AQI and regional weather; quality audit of 39 stations. |
| Forecasting system | Persistence, seasonal-naive, Random Forest and XGBoost; limited time-aware tuning, five input comparisons, 1/6/12/24-hour evaluation and 24 direct forecast models. |
| Pollution episodes | Sustained-event detection, onset/peak/duration/recovery, missing-data boundaries, one-to-one matching and daily warning evaluation. |
| Missing-history fallback | Backup model for missing past readings; forecasts produced for 94.6% of scheduled daily windows. |
| Recent pollutant audit | 2024: 1,368,606 Delhi rows across 39 station IDs. 2025: 1,366,609 rows across 40 IDs. Release hashes and quality tables are saved. |
| Station readiness | 31 candidates among 39 historical stations. All 31 have normalized-name matches in both recent pollutant station lists. This is not official ID confirmation or model validation. |
| Recent weather | 23,592 continuous, IST-labelled regional weather hours from 1 January 2024 through 9 September 2026; no missing requested weather fields. |
| Official exports | CPCB viewer access and spreadsheet export work. Evidence includes two 2025 pollutant samples, a 2026 Alipur sample and Anand Vihar’s January 2026 hourly AQI workbook. |
| Automated checks | 20 tests passed, including recent station-name-link and weather checks. Streamlit AppTest passed for the station-audit dashboard. |

## What the new evidence proves—and does not prove

- The official viewer/export route is usable again. The January 2026 Anand Vihar workbook proves an official hourly AQI file can be obtained.
- The current official AQI acquisition is still one station and one month. It is not sufficient for city-wide model expansion, 2025 evaluation or 2026 evaluation.
- The 2024–2025 mirror files are 15-minute pollutant records, not hourly AQI targets. They remain outside training.
- The official samples preserve `Date From` and `Date To` values, but do not establish source timezone, quality-flag rules, reporting delay or all-station equivalence.
- Seven stations remain forecastable in the dashboard. The other 31 candidates require a verified target dataset, trained models and evaluation before they are added.

## Current model results — unchanged 2023 evaluation

| Horizon | MAE (AQI points) | RMSE | R² |
|---|---:|---:|---:|
| 1h | 26.06 | 43.85 | 0.874 |
| 6h | 48.95 | 68.40 | 0.695 |
| 12h | 52.50 | 72.72 | 0.656 |
| 24h | 54.92 | 75.48 | 0.628 |

Daily warning precision/recall/F1 is 95.3% / 72.8% / 82.6%. These results are retrospective, and an earlier prototype had already inspected the 2023 period. They are not 2025 or 2026 results.

## Remaining work

1. Collect and audit official AQI exports across the needed stations and dates.
2. Verify station IDs, timestamp timezone, interval meaning, quality handling and reporting delay.
3. Create a documented recent AQI target panel, then join only verified pollutant and weather inputs.
4. Freeze the expanded station list and dataset, then train, select and calibrate models on the recorded split.
5. Evaluate untouched 2025 and later available 2026 data. Do not tune after inspecting those results.
6. Update dashboard dates and station options only after the new model artefacts pass evaluation.

## Evidence

- [Engineering report](final_report.md)
- [Recent data audit](recent_data_audit.md)
- [Official source access log](source_evidence/repository_access.md)
- [Recent station/weather readiness](tables/station_expansion/readiness_2026_09_16.json)
- [Acceptance matrix](../docs/acceptance.md)
- [Execution checklist](../docs/remaining_checklist.md)
