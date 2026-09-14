# Project status — 14 September 2026

**Overall: partially complete; further source verification is blocked by CPCB access failures.** The working deliverable is a seven-station historical AQI forecasting and episode-warning prototype. Recent pollutant data has been acquired and audited, but it is not integrated into the saved models. No 2024–2026 model performance is claimed.

## Completed and verified

| Work | Evidence and scope |
|---|---|
| Historical modelling dataset | Seven stations, 2017–2023 AQI and regional weather; quality audit of 39 stations. |
| Forecasting and experiments | Persistence, seasonal naive, Random Forest and XGBoost; bounded time-aware tuning, five feature ablations, 1/6/12/24h evaluation and 24 hourly trajectory models. |
| Pollution episode detection | Sustained-event detection, severity/onset/peak/duration/recovery, unknown boundaries caused by missing readings, one-to-one matching and daily warning evaluation. |
| Missing-history fallback | Backup model for gaps in past readings. Forecasts were produced for 94.6% of scheduled daily windows; 74.3% had enough future readings to score episodes. These are coverage figures, not accuracy. |
| Uncertainty and explanation | Prediction ranges for individual hours and a chart of model inputs. These do not explain pollution causes or give episode probabilities. |
| Recent data acquisition | 2024: 1,368,606 Delhi rows, 39 station IDs. 2025: 1,366,609 rows, 40 IDs. Both public mirror release hashes verified; data quality tables generated. |
| Expansion coverage screen | 31 candidates among 39 archived AQI stations using 2019–2021 data only. Candidate status does not mean a trained or validated model. |
| Evaluation design | Expanded split recorded before new-period model scores: train through 2023; selection/calibration in separate halves of 2024; external tests planned for 2025 and available 2026. |
| Dashboard and documentation | Historical replay, forecast/episode plots, model evidence, station comparison with expansion reasons, portable public-repository setup instructions. |
| Automated validation | Latest full suite: 17 tests passed. Streamlit application check passed after the station-audit view was added; the later interval helper is not connected to the dashboard. |

## Partial work — not yet accepted as complete

- **Source verification:** local AQI archive matched to the pinned mirror; seven station names/agencies matched to an official CPCB PDF. Defective AQI IDs and timezone assumptions remain unresolved.
- **Official pollutant comparison:** ten Alipur rows from 1 January 2025 matched 66 numeric and 14 missing cells. Mirror clock labels match official interval starts. This proves only that sample, not all stations, years, timezone or reporting latency.
- **Pollutant time aggregation:** implemented and tested with explicit caller-specified timezone, interval-end labels, missing-quarter counts and optional publication delay. It remains outside training pending broader source checks. The three-of-four completeness default is a research choice.
- **Recent data:** 2024–2025 pollutant releases are staged for audit, not model-ready. They contain 15-minute concentrations, not the AQI target used by current models. No verified 2026 observations have been acquired.
- **Station coverage:** seven evaluated stations remain forecastable. The 31 candidates are shown in the audit, not added to the forecast selector.

## Current model results — unchanged 2023 retrospective evaluation

| Horizon | MAE (AQI points) | RMSE | R² |
|---|---:|---:|---:|
| 1h | 26.06 | 43.85 | 0.874 |
| 6h | 48.95 | 68.40 | 0.695 |
| 12h | 52.50 | 72.72 | 0.656 |
| 24h | 54.92 | 75.48 | 0.628 |

Daily any-episode warning precision/recall/F1: 95.3% / 72.8% / 82.6%. Individual episode-segment precision/recall/F1: 77.0% / 60.9% / 68.0%. Mean onset/peak/recovery errors on matched evaluable segments: 2.0 / 3.9 / 3.2 hours. Duration error is 2.2 hours on only 28 uncensored cases; that evidence is weak.

These combined results cover a broader population than the primary complete-history results in the engineering report. Do not compare different populations as a pure accuracy gain. The inherited prototype already inspected 2023; a truly untouched later test remains outstanding.

## Remaining work, in execution order

1. Restore usable official source access and expand station/period comparisons. Establish timezone, station identity, interval boundary and quality/latency semantics.
2. Obtain recent AQI targets or validate their derivation from concentrations; acquire available 2026 observations. Do not treat 2026 as a complete year.
3. Complete source-audited pollutant/weather integration, including recent and station-specific weather assessment, and freeze the expanded model-ready dataset and station roster.
4. Execute expanded baseline/model comparisons, feature ablations, time-aware tuning and recalibration using the recorded split. Test pollutant usefulness rather than assuming it.
5. Evaluate untouched 2025/2026 periods: station/horizon errors, interval coverage, episode/warning scores, timing, censoring and failure cases. Document any deviation from the recorded evaluation design before scoring.
6. Update forecastable stations/dates from newly validated artifacts; implement and validate as-of feeds if present-day early warning is required. Current dashboard is replay only.
7. Assess optional extensions (sequence/recursive models, local explanations) on validation evidence; document any decision not to implement them. They are not completed experiments.
8. Regenerate final results, manifests and reports; rerun relevant tests/browser checks; complete the original requirement-by-requirement acceptance audit.

## Current blocker

CPCB monthly/yearly download actions did not produce files. Its alternate Advanced Search table worked for the saved Alipur sample, but a later session reset showed a blank CAPTCHA even after refresh and reported API errors. A working official export or restored viewer is needed for broader verification.

## Evidence

- [Engineering report](final_report.md) and [combined results](missing_history_fallback.md)
- [Recent data audit](recent_data_audit.md)
- [Primary sample comparison](source_evidence/alipur_official_2025_comparison.json)
- [Validation record](validation.md)
- [Acceptance matrix](../docs/acceptance.md)
- [Execution checklist](../docs/remaining_checklist.md)
- [Expanded evaluation protocol](../docs/expanded_evaluation_protocol.json)
