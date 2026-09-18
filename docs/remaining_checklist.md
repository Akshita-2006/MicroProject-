# Execution checklist — 18 September 2026

The project is partly complete. The dashboard and saved models still show seven-station historical forecasts for 2023. Newer data is being prepared but has not been used to train or evaluate a model.

## Completed

- [x] Audit 39 historical AQI stations and create the seven-station 2017–2023 modelling dataset.
- [x] Run historical baselines, Random Forest and XGBoost comparisons, tuning, input comparisons and direct 24-hour forecasts.
- [x] Run missing-history fallback, prediction ranges, pollution-episode detection and episode/warning evaluation.
- [x] Build the historical replay dashboard and public-repository setup instructions.
- [x] Download, hash-check and audit 2024–2025 pollutant releases: 1,368,606 and 1,366,609 Delhi rows.
- [x] Identify 31 station-expansion candidates from 39 archived stations using 2019–2021 coverage.
- [x] Save the evaluation plan before calculating any new-period model scores.
- [x] Restore access to CPCB’s official viewer and spreadsheet exports after an approved CAPTCHA.
- [x] Save official evidence: 2025 Alipur and Anand Vihar pollutant-table exports, a 2026 Alipur export, and Anand Vihar’s January 2026 hourly AQI workbook.
- [x] Download and validate regional Delhi weather from 1 January 2024 through 9 September 2026: 23,592 continuous IST-labelled hours with no missing weather fields.
- [x] Match all 31 expansion candidates by normalized name to the 2024 and 2025 pollutant station lists, while preserving agency names so stations are not merged incorrectly.
- [x] Pass 20 automated tests and load the station-audit dashboard with Streamlit AppTest.

## Still required, in order

- [ ] Expand official comparisons across stations and dates. Current samples show displayed 15-minute `Date From` and `Date To` intervals, but do not establish timezone, quality filtering or reporting delay for every export.
- [ ] Build a broad recent AQI target dataset. The official January 2026 workbook covers Anand Vihar only; the 2024–2025 mirror releases are pollutant records, not hourly AQI targets.
- [ ] Verify pollutant units, timestamps and averaging before creating any AQI target from concentration records.
- [ ] Join only verified pollutant and weather inputs, then freeze a documented expanded station roster and model-ready dataset.
- [ ] Train, tune, compare and recalibrate expanded models using the recorded evaluation plan.
- [ ] Evaluate 2025 and later available 2026 periods without changing the model based on those test results.
- [ ] Add newer dates and stations to the dashboard only after the relevant models and evaluations are complete.
- [ ] Build and test a current-data feed if live warning is required. The current dashboard remains historical replay.
- [ ] Regenerate results and reports, run final tests and complete the requirement-by-requirement acceptance review.

Evidence: [project status](../reports/project_status.md), [recent data audit](../reports/recent_data_audit.md), [station and weather readiness](../reports/tables/station_expansion/readiness_2026_09_16.json), and [official source access log](../reports/source_evidence/repository_access.md). The expanded split boundaries are in [expanded_evaluation_protocol.json](expanded_evaluation_protocol.json).
