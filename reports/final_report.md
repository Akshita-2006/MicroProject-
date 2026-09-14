# Delhi Pollution Episode Forecasting — Engineering Report

## Current completion status — 14 September 2026

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


---

Generated from saved experiment results. The current status below includes the backup model; sections 1–15 describe the original seven-station model evaluation.

## 1. What was inherited

A Shadipur-only AQI/meteorology prototype, 2017–2023 raw files, initial EDA, persistence/RF/XGBoost regression, sparse-horizon threshold scores and a plot-oriented Streamlit page. The original 59,568-row station series omitted 1,776 hours from its calendar. Its reported accuracy cannot be directly compared to this corrected experiment because targets, baselines, station scope and splits changed.

## 2. What changed

Calendar-complete station series, correct current-AQI persistence, station-isolated features, fixed purged calendar splits, common ablation samples, models chosen on validation data, 24 direct hourly forecasts, sustained events with censoring, one-to-one event matching, daily warning confusion matrices, calibrated intervals, global feature importance, replay inference and a redesigned dashboard. Legacy outputs remain outside the v2 folder.

## 3. Dataset and source audit

All 39 Delhi station names were audited. The corrected panel contains 429,408 hourly rows over seven years for 7 selected stations. Raw input SHA-256 values and actual weather units/coordinates are recorded in the data manifest. The AQI mirror claims CPCB provenance; defective AQI IDs and uncertified timestamp semantics remain explicit limitations. Source AQI is not independently reconstructed. The local AQI bytes were verified against pinned source commit a58f47848e678c7cea58a69758343d08d0b49915. A direct CPCB metadata request initially failed certificate verification; a retry using default system certificate trust reached the server but returned HTTP 404; the request and error are saved in reports/source_evidence/primary_source_attempt.json. TLS checks were not disabled. Further investigation successfully retrieved the official government-domain station-list PDF and matched all seven selected station names and agencies. Authorized repository access showed recent file listings, but download actions did not yield files. The alternate Advanced Search table supplied one Alipur sample matching 66 numeric values and 14 missing cells at interval-start clock labels. Broader verification remains incomplete. The last recorded viewer session showed a blank CAPTCHA and API errors.

Shadipur missingness is 4.664% on the full calendar, rather than the prototype's 1.82% among retained rows. Impossible AQI outside 0–500 is flagged; high valid pollution is retained. Missingness by station/year/variable, duplicate conflicts, constant sequences and extreme values are in reports/tables/v2.

## 4. Selected stations

Selection was fixed by training-period coverage ≥85% and absence of conflicting timestamps, not test accuracy. Later-commissioned stations may fail this period-specific rule despite useful shorter records.

| station | observed | missing_pct | train_coverage | longest_missing_hours |
|---|---|---|---|---|
| Shadipur Delhi CPCB | 58483.000 | 4.664 | 0.940 | 1283.000 |
| DTU Delhi CPCB | 57125.000 | 6.878 | 0.923 | 720.000 |
| NSIT Dwarka Delhi CPCB | 56127.000 | 8.504 | 0.910 | 863.000 |
| ITO Delhi CPCB | 55230.000 | 9.967 | 0.890 | 720.000 |
| IHBAS Dilshad Garden Delhi CPCB | 55096.000 | 10.185 | 0.889 | 747.000 |
| Sirifort Delhi CPCB | 54611.000 | 10.976 | 0.882 | 719.000 |
| Mandir Marg Delhi DPCC | 53906.000 | 12.125 | 0.866 | 356.000 |

## 5. Pollutants and weather

The 2017 pollutant release was downloaded and inspected, including all six requested pollutants. Per-station diagnostics and correlations were generated. Shadipur PM10 is entirely absent in that sample. The upstream parser assigns UTC to timestamp strings without establishing their original timezone; joining this sample risks a 5.5-hour alignment error. The 2024 and 2025 releases have since been downloaded, hash-verified and audited (1,368,606 and 1,366,609 Delhi rows; 39 and 40 station IDs). One official Alipur comparison supports interval-start labels for that sample, but does not certify timezone. An interval-safe aggregation helper is implemented and tested but not connected to training. The primary model therefore excludes unverified pollutant observations. Predictive usefulness of these pollutants has **not** been evaluated.

Weather uses the existing Open-Meteo Delhi grid: temperature °C, humidity %, wind km/h and degrees, pressure hPa and precipitation mm. The payload states Asia/Kolkata and offset 19,800 seconds. One regional grid is shared across stations; station-specific meteorology is not claimed. Retrospective reanalysis is not an as-of operational weather feed.

## 6. Features and ablation

AQI at issuance and lags 1/2/3/6/12/24/48/72h; rolling mean/min/max/std and endpoint trends over 3/6/12/24/48/72h; exceedance counts; cyclic hour/weekday/month and weekend; weather at issuance, lags and rolling means; station indicators. No future weather is used. Five ablations use the same complete-case samples.

Validation MAE by feature group (lower is better):

| feature_group | 1 | 6 | 12 | 24 |
|---|---|---|---|---|
| A_history | 35.415 | 74.141 | 70.511 | 72.766 |
| B_history_time | 34.375 | 63.405 | 67.390 | 71.474 |
| C_history_weather | 35.207 | 69.520 | 66.835 | 70.673 |
| D_history_time_weather | 34.216 | 61.549 | 64.906 | 68.531 |
| E_full | 33.902 | 59.559 | 64.277 | 68.326 |

A: AQI history; B: history + time; C: history + weather; D: both; E: full engineering. Differences measure predictive association under this split, not causality. No pollutant interaction was added without verified pollutant data.

## 7. Models and hyperparameters

Persistence, daily seasonal naive, Random Forest and XGBoost were executed. 24 HPO fold evaluations compare three predefined XGBoost configurations in two expanding folds per required horizon. Search uses every fourth eligible development row, then ablations and selection models fit the full training sample. Random Forest uses 60 trees, depth 14, leaf minimum 8 and half-sample bootstrap. XGBoost selections and exact parameters are in selection.json; all ten requested tuning dimensions vary across the bounded candidate set. No exhaustive optimization is claimed.

LSTM/GRU, additional boosters and ARIMA were not run. Direct versus recursive remains an extension. Each additional trajectory hour is fitted directly using a nearby required horizon's validation-selected configuration.

## 8. Experiment protocol

Training 2017–2021; selection January–June 2022; calibration July–December 2022; retrospective test 2023. Labels crossing boundaries are purged. Selection uses MAE only and is written before test scoring. Test results are descriptive. The inherited experiment already examined the 2023 era, so a test on a previously unused period is still needed. No shuffling, target interpolation, test tuning or test-based feature choice occurs in v2.

## 9. Selected results by horizon

| horizon | model | validation_MAE | test_MAE | test_RMSE | test_R2 | interval_coverage | test_n |
|---|---|---|---|---|---|---|---|
| 1.000 | xgboost_tuned | 33.813 | 25.938 | 44.112 | 0.873 | 0.894 | 30733.000 |
| 6.000 | xgboost | 59.559 | 48.230 | 67.662 | 0.703 | 0.863 | 30393.000 |
| 12.000 | xgboost | 64.277 | 51.980 | 71.705 | 0.669 | 0.864 | 30200.000 |
| 24.000 | xgboost | 68.326 | 54.632 | 74.389 | 0.644 | 0.865 | 30016.000 |

These are the validation-selected models' test results, not the best observed test configuration. The 90% intervals are marginal, not guaranteed under temporal dependence.

## 10. Full model comparison

| setup | 1h mae | 6h mae | 12h mae | 24h mae | 1h rmse | 6h rmse | 12h rmse | 24h rmse | 1h r2 | 6h r2 | 12h r2 | 24h r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| persistence/A_history | 26.625 | 62.233 | 71.678 | 61.164 | 49.320 | 91.814 | 102.063 | 89.744 | 0.841 | 0.454 | 0.330 | 0.483 |
| random_forest/E_full | 26.103 | 48.909 | 52.916 | 55.366 | 44.560 | 68.487 | 72.822 | 75.128 | 0.870 | 0.696 | 0.659 | 0.637 |
| seasonal_naive/A_history | 61.224 | 61.184 | 61.247 | 61.164 | 89.969 | 89.853 | 89.939 | 89.744 | 0.472 | 0.477 | 0.479 | 0.483 |
| xgboost/A_history | 27.255 | 58.373 | 56.577 | 56.691 | 46.085 | 78.437 | 77.476 | 77.190 | 0.861 | 0.601 | 0.614 | 0.617 |
| xgboost/B_history_time | 26.650 | 51.622 | 53.664 | 55.343 | 45.184 | 71.929 | 74.190 | 75.574 | 0.867 | 0.665 | 0.646 | 0.633 |
| xgboost/C_history_weather | 26.867 | 54.915 | 54.513 | 55.091 | 45.534 | 75.218 | 74.578 | 74.962 | 0.865 | 0.633 | 0.642 | 0.639 |
| xgboost/D_history_time_weather | 26.538 | 50.563 | 52.905 | 54.616 | 44.826 | 70.421 | 72.801 | 74.450 | 0.869 | 0.679 | 0.659 | 0.644 |
| xgboost/E_full | 26.164 | 48.230 | 51.980 | 54.632 | 44.439 | 67.662 | 71.705 | 74.389 | 0.871 | 0.703 | 0.669 | 0.644 |
| xgboost_tuned/E_full | 25.938 | 47.385 | 51.829 | 54.406 | 44.112 | 66.833 | 71.540 | 74.241 | 0.873 | 0.711 | 0.671 | 0.646 |

## 11. Sustained-event results

Research definition: AQI ≥301 for three consecutive hours; CPCB defines the threshold category, not this persistence requirement. Unknown values break runs and censor endpoints. Onset, peak, severity, duration and recovery are extracted from the hourly forecast. Recovery means first below-threshold hour. Boundary durations are lower bounds.

Pooled event counts sum station-level one-to-one matches from fixed-lead streams. Timing MAEs are conditional on matched events and available uncensored endpoints:

| horizon | persistence | actual_events | predicted_events | matched | precision | recall | f1 | onset_error_hours | peak_error_hours | duration_error_hours | recovery_error_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.000 | 3.000 | 660.000 | 597.000 | 526.000 | 0.881 | 0.797 | 0.837 | 2.198 | 3.217 | 2.677 | 1.317 |
| 6.000 | 3.000 | 680.000 | 529.000 | 393.000 | 0.743 | 0.578 | 0.650 | 6.752 | 7.433 | 10.107 | 5.968 |
| 12.000 | 3.000 | 689.000 | 513.000 | 372.000 | 0.725 | 0.540 | 0.619 | 6.591 | 7.051 | 11.780 | 6.830 |
| 24.000 | 3.000 | 686.000 | 523.000 | 365.000 | 0.698 | 0.532 | 0.604 | 6.569 | 6.414 | 12.048 | 6.945 |

Sensitivity at 2/3/6h persistence is saved in pooled_event_metrics.csv; no test-driven policy choice was made. Predictions are evaluated only where a forecast and truth exist; availability must be considered alongside accuracy.

## 12. Warning performance

Daily midnight issuance, one 24-hour trajectory per eligible station-day, binary outcome: at least one sustained episode. Only fully observed truth windows qualify. TP=392, FP=15, FN=127, TN=548; pooled precision=0.963, recall=0.755, F1=0.847.

| station | eligible_windows | true_negative | false_positive | false_negative | true_positive | precision | recall | f1 |
|---|---|---|---|---|---|---|---|---|
| DTU Delhi CPCB | 184.000 | 119.000 | 3.000 | 23.000 | 39.000 | 0.929 | 0.629 | 0.750 |
| IHBAS Dilshad Garden Delhi CPCB | 136.000 | 89.000 | 3.000 | 14.000 | 30.000 | 0.909 | 0.682 | 0.779 |
| ITO Delhi CPCB | 158.000 | 82.000 | 3.000 | 22.000 | 51.000 | 0.944 | 0.699 | 0.803 |
| Mandir Marg Delhi DPCC | 85.000 | 50.000 | 0.000 | 9.000 | 26.000 | 1.000 | 0.743 | 0.852 |
| NSIT Dwarka Delhi CPCB | 174.000 | 68.000 | 1.000 | 19.000 | 86.000 | 0.989 | 0.819 | 0.896 |
| Shadipur Delhi CPCB | 271.000 | 106.000 | 4.000 | 34.000 | 127.000 | 0.969 | 0.789 | 0.870 |
| Sirifort Delhi CPCB | 74.000 | 34.000 | 1.000 | 6.000 | 33.000 | 0.971 | 0.846 | 0.904 |

These warning-window metrics differ from fixed-lead event metrics. Event counts do not have a meaningful true-negative total.

### Same-origin episode timing — the dashboard's forecast setting

Each daily 24-hour trajectory is now evaluated independently for episode matching and timing. Adjacent issue windows are never stitched into an apparent continuous forecast. Counts refer to episode segments inside forecast windows, not unique multi-day environmental events.

| metric | value |
|---|---|
| eligible_windows | 1082.000 |
| actual_episode_segments | 819.000 |
| predicted_episode_segments | 658.000 |
| matched_segments | 509.000 |
| precision | 0.774 |
| recall | 0.621 |
| f1 | 0.689 |
| onset_error_hours | 2.312 |
| onset_error_hours_n | 186.000 |
| peak_error_hours | 4.104 |
| peak_error_hours_n | 509.000 |
| duration_error_hours | 1.933 |
| duration_error_hours_n | 15.000 |
| recovery_error_hours | 3.535 |
| recovery_error_hours_n | 215.000 |
| scheduled_windows | 2548.000 |
| produced_windows | 1289.000 |
| abstained_windows | 1259.000 |
| excluded_produced_windows | 207.000 |
| evaluated_fraction | 0.425 |

The binary warning F1 above only asks whether any episode occurs. Same-origin episode F1 additionally penalizes unmatched and extra episode segments, and is therefore a different, stricter outcome. Timing errors apply only to matched segments; onset and duration/recovery counts exclude the corresponding censored endpoints. Only 15 completely bounded matches support the duration-error mean in this run, which is insufficient for a strong duration-accuracy claim. Peak timing describes the maximum within the available window. Detailed windows, matches and exclusions are saved in issued_episode_*.csv.

## 13. Explainability and uncertainty

Top global features per required horizon:

| horizon | feature | importance |
|---|---|---|
| 1.000 | aqi | 0.733 |
| 1.000 | aqi_mean_3 | 0.072 |
| 1.000 | aqi_min_3 | 0.015 |
| 1.000 | aqi_mean_24 | 0.008 |
| 1.000 | aqi_max_3 | 0.006 |
| 6.000 | aqi_mean_24 | 0.471 |
| 6.000 | aqi_mean_48 | 0.085 |
| 6.000 | aqi | 0.063 |
| 6.000 | aqi_mean_72 | 0.033 |
| 6.000 | month_cos | 0.023 |
| 12.000 | aqi_mean_24 | 0.252 |
| 12.000 | aqi_lag_12 | 0.229 |
| 12.000 | aqi_mean_12 | 0.097 |
| 12.000 | aqi_mean_48 | 0.049 |
| 12.000 | exceedance_count_24 | 0.047 |
| 24.000 | aqi | 0.271 |
| 24.000 | aqi_mean_3 | 0.240 |
| 24.000 | aqi_min_3 | 0.087 |
| 24.000 | aqi_mean_24 | 0.062 |
| 24.000 | aqi_lag_24 | 0.058 |

Importances are tree usage, potentially biased by correlated features, and are neither local SHAP values nor causal effects. Separate July–December 2022 residual quantiles produce nominal 90% bands; per-station realized coverage is reported in model_comparison.csv. No confidence percentage is assigned to an episode.

## 14. Dashboard and reproducibility

Station selector, historical issue date/hour, observed category, four horizon cards, complete hourly forecast with bands, episode cards including censored recovery, history, model evidence, same-time station comparison, methodology and forecast CSV download. Model inference truncates history at issuance and abstains on missing required inputs. The app does not display 2023 data as live 2026 conditions.

Run `python run_pipeline.py`; open `python -m streamlit run dashboard/app.py`. Raw data is preserved. Models and outputs live in experiments/models/v2 and experiments/results/v2. Data quality and this report can be regenerated separately.

## 15. Failures and limitations

Forecast availability under the conservative full-feature input requirement:

| station | test_hours | full_feature_hours | feature_availability_pct |
|---|---|---|---|
| DTU Delhi CPCB | 8760.000 | 5219.000 | 59.578 |
| IHBAS Dilshad Garden Delhi CPCB | 8760.000 | 4070.000 | 46.461 |
| ITO Delhi CPCB | 8760.000 | 4558.000 | 52.032 |
| Mandir Marg Delhi DPCC | 8760.000 | 2965.000 | 33.847 |
| NSIT Dwarka Delhi CPCB | 8760.000 | 4789.000 | 54.669 |
| Shadipur Delhi CPCB | 8760.000 | 7010.000 | 80.023 |
| Sirifort Delhi CPCB | 8760.000 | 2358.000 | 26.918 |

Missingness makes this a conditional evaluation; omitted windows may be more difficult. Monthly MAE, bias and severe-event counts are in monthly_failure_analysis.csv. Long-horizon regression shrinks extremes and may miss severe episodes. Event matching by any overlap can credit loosely aligned events, so timing errors must accompany F1. Peaks and durations are truncated by forecast windows; three-hour persistence is a research policy. Station identity, timezone and mirror provenance require further primary-source validation. Pollutant integration, station-local weather and real-time delivery are not complete.

## 16. Acceptance status and remaining weaknesses

### Missing-history fallback — subsequent validation and combined evaluation



The complete-history model remains unchanged. When a 73-hour calendar window contains missing past values, a separately trained XGBoost fallback uses native missing-value handling. Target values are not filled in, and no forecast is made when current AQI is missing. Validation chooses between native missing handling with and without missingness indicators, using incomplete-history MAE at each required horizon. The nearest required horizon supplies the configuration for intermediate hours. Calibration uses missing-history July–December 2022 cases separately for each forecast hour.

#### What changed and why

The prior complete-case policy excluded many otherwise usable forecast origins. Training the fallback on all training origins with observed current/target AQI allows it to learn from incomplete history. Existing complete-history forecasts are preserved, so differences in their recorded accuracy cannot be attributed to this change. Test outcomes do not choose the fallback policy.

Validation-only comparison on incomplete histories:

| horizon | variant | n | mae | persistence_mae |
|---|---|---|---|---|
| 1.000 | native_missing | 16137.000 | 34.655 | 35.786 |
| 1.000 | native_missing_flags | 16137.000 | 34.644 | 35.786 |
| 6.000 | native_missing | 15660.000 | 64.649 | 84.976 |
| 6.000 | native_missing_flags | 15660.000 | 63.970 | 84.976 |
| 12.000 | native_missing | 15457.000 | 66.508 | 96.688 |
| 12.000 | native_missing_flags | 15457.000 | 66.317 | 96.688 |
| 24.000 | native_missing | 15395.000 | 66.822 | 79.659 |
| 24.000 | native_missing_flags | 15395.000 | 66.681 | 79.659 |

#### Coverage and combined accuracy

Evaluable daily windows increased from 1,082 of 2,548 (42.5%) to 1,894 of 2,548 (74.3%). Produced windows increased from 1,289 to 2,410. Remaining omitted cases include missing current observations and missing future truth. Evaluable coverage is not identical to forecast availability.

Combined retrospective test regression (a broader population than the old complete-case table):

| station | horizon | fallback_n | interval_coverage | n | mae | rmse | r2 |
|---|---|---|---|---|---|---|---|
| ALL | 1.000 | 25980.000 | 0.890 | 56713.000 | 26.064 | 43.847 | 0.874 |
| ALL | 6.000 | 25490.000 | 0.862 | 55883.000 | 48.948 | 68.402 | 0.695 |
| ALL | 12.000 | 25234.000 | 0.857 | 55434.000 | 52.501 | 72.722 | 0.656 |
| ALL | 24.000 | 25030.000 | 0.855 | 55046.000 | 54.925 | 75.480 | 0.628 |

#### Warnings and episode timing

Binary daily warning TP=646, FP=32, FN=241, TN=975; precision=0.953, recall=0.728, F1=0.826. These metrics concern whether any sustained episode occurs in a window.

Episode-segment matching and timing within each same-origin trajectory:

| metric | value |
|---|---|
| eligible_windows | 1894.000 |
| actual_episode_segments | 1383.000 |
| predicted_episode_segments | 1093.000 |
| matched_segments | 842.000 |
| precision | 0.770 |
| recall | 0.609 |
| f1 | 0.680 |
| onset_error_hours | 2.036 |
| onset_error_hours_n | 304.000 |
| peak_error_hours | 3.895 |
| peak_error_hours_n | 842.000 |
| duration_error_hours | 2.214 |
| duration_error_hours_n | 28.000 |
| recovery_error_hours | 3.201 |
| recovery_error_hours_n | 358.000 |
| scheduled_windows | 2548.000 |
| produced_windows | 2410.000 |
| abstained_windows | 138.000 |
| excluded_produced_windows | 516.000 |
| evaluated_fraction | 0.743 |

Timing means remain conditional on matched segments and censoring. More complete coverage does not establish accurate event duration, an external holdout, verified pollutant alignment, or real-time validity. The test era was previously inspected. No comparison between different evaluation populations should be described as a pure accuracy improvement.

Files: experiments/results/combined_system contains combined predictions, numeric results, fixed-lead event results, daily binary warnings and same-origin episode matches. The two source populations are checked for duplicate forecast keys before combining. Each returned forecast identifies its route.


Implemented and executed: multi-station investigation/selection, calendar dataset, quality/EDA tables, leakage-safe feature tests, two baselines and two ML families, bounded time-aware tuning, A–E ablations, all four required horizons plus hourly trajectories, episode extraction/characterization, event and daily warning evaluation, feature importance, intervals, dashboard and reproducible reporting.

Not established: official verification of individual readings, verified AQI timezone, defensible joined pollutant features, truly unseen external test, operational as-of weather and reporting latency, pollutant usefulness experiments, recursive comparison, local SHAP explanations, comprehensive hyperparameter search. The historical forecasting system works, but source verification, recent-data training and later-year evaluation remain unfinished.

## 17. Best next experiments

1. Obtain primary CPCB station exports and resolve the AQI ID/timezone discrepancies before claiming operational validity.
2. Validate pollutant timestamp semantics, then complete overlapping model-ready data and test pollutant groups using the recorded expanded splits. The 2024–2025 concentration releases are already staged; AQI targets and 2026 observations remain outstanding.
3. Execute the already recorded expanded evaluation protocol after source gates pass, including untouched later-period scoring and explicit meteorological availability/reporting delays.
4. Compare station-specific meteorology and pollutant models against this pooled baseline.
5. Improve extreme-event recall using validation-only objectives and assess warning lead time, interval calibration by season, and episode probability calibration.

Validation: the latest full suite has 17 passing tests, including station-screening and interval-end preprocessing checks. Streamlit AppTest passed after the station-coverage audit was added; earlier browser layout was inspected and corrected. New pollutant preprocessing is not yet integrated into the dashboard or trained models. See [validation record](validation.md) and [acceptance evidence](../docs/acceptance.md).

Sources and detailed assumptions: [methodology](../docs/methodology_v2.md), [initial audit](current_state_audit.md), [CPCB AQI calculation](https://cpcb.gov.in/National-Air-Quality-Index/), [data mirror](https://github.com/Vonter/india-cpcb-aqi), [Open-Meteo archive](https://open-meteo.com/en/docs/historical-weather-api).
