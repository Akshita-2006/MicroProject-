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

## Final review and submission gate

The items below are the review checklist for the current deliverable.  They do
not silently expand the claim from a retrospective research dashboard to a
live or official CPCB service.  Mark an item complete only when its evidence
file, command and date are recorded in the final report.

### 1. Resolve the evidence story (required)

- [ ] Update or archive the stale seven-station/incomplete statements in
  `docs/acceptance.md` and the historical-status portions of
  `reports/final_report.md`.  They conflict with the current 30-station,
  2017-2025 concentration results described in `README.md` and
  `reports/project_status.md`.
- [ ] State one final scope sentence consistently in the README, dashboard,
  presentation and report: 30-station historical AQI replay through 2023;
  recorded and forecast pollutant concentrations through 2025; neither a live
  feed, an official AQI release nor medical advice.
- [ ] Freeze a submission manifest: Git commit/hash, Python/package versions,
  model/result hashes, data release hashes, station roster, split dates and
  the exact commands used to regenerate results.
- [ ] Run the full automated suite in the locked project environment and save
  the dated result (currently expected: 21 tests).  Repeat the Streamlit
  AppTest/smoke check and manually inspect one 2023 AQI replay and one each
  of the 2024 and 2025 concentration views.
- [ ] Check every number quoted in the abstract, slides and dashboard against
  the saved CSV/Parquet artifacts; give every table its sample size, period,
  station population and units.

### 2. Required comparison tables (required)

- [ ] **AQI model comparison:** for each 1/6/12/24-hour horizon, show
  persistence, seasonal-naive, Random Forest, untuned XGBoost and selected
  XGBoost on the same 2023 origins.  Report MAE, RMSE, R², sample size and
  improvement over the strongest baseline.  Use
  `experiments/results/all_eligible_30/model_comparison.csv`; do not describe
  the already-inspected 2023 period as a fully external test.
- [ ] **Feature-value comparison:** retain the existing A--E ablation table
  (history; +time; +weather; +time+weather; full engineering) and report it
  as validation-only model selection.  It supports predictive utility, not
  causal statements.
- [ ] **Concentration performance table:** show the seven pollutants by
  1/6/12/24-hour horizon, separately for 2024 validation and untouched 2025
  test.  Include MAE, RMSE, R², units and `n` from
  `experiments/results/concentrations_2017_2025/metrics.csv`.  Do not average
  errors across pollutants with different units; if a compact summary is
  needed, use R² or a unitless normalized error and label the method.
- [ ] **Calibrated-AQI agreement table:** keep calibrated AQI distinct from
  official AQI.  Report the archived-2023 agreement (and any approved
  official-sample check) with MAE/RMSE/R² and category agreement.  Never call
  a pollutant-derived 2024--2025 target an official CPCB AQI observation.
- [ ] **Station comparison:** report the distribution across all 30 stations
  (median, IQR, best/worst and station-level `n`) rather than only pooled
  values.  Investigate, but do not hide, low-coverage or high-error stations.
- [ ] **Horizon comparison:** plot or tabulate degradation from 1 to 24 hours
  for AQI and for every pollutant; avoid comparing raw MAE between differently
  scaled pollutants.

### 3. Required robustness and safety slices (required)

- [ ] Break AQI and concentration errors down by season/month, AQI category
  (where official/archived AQI exists), concentration quantile and pollution
  episode/non-episode.  Report both metrics and sample counts; sparse cells
  should be labelled rather than interpreted.
- [ ] Report signed bias/mean error alongside MAE, especially for high AQI or
  high-concentration conditions, so systematic under-warning is visible.
- [ ] For AQI warning/episode output, present precision, recall, F1, false
  alarms, missed events, lead time, peak timing/value error and duration error.
  Timing and duration must state their matching/censoring rule and denominator.
- [ ] Report interval coverage **and width** overall and by horizon, station
  and season.  The nominal 90% bands are marginal prediction intervals, not
  episode probabilities or simultaneous 24-hour guarantees.
- [ ] Compare complete-history and missing-history fallback routes only within
  their own populations.  Give route counts, abstentions and performance; do
  not present increased availability as an accuracy gain on identical cases.
- [ ] Recheck leakage and chronology: target-boundary purge, issue-time
  truncation, station-isolated lags, fixed station screen and no 2025 test
  data used for feature/model selection.

### 4. Source and data-quality release checks (required)

- [ ] Verify release hashes, expected row/station/date counts, duplicate keys,
  units, missingness, outliers and the hourly calendar for the frozen inputs.
- [ ] Keep the CPCB sample comparison bounded: the Alipur result verifies the
  saved sample only.  Document unresolved AQI timezone, publication-latency,
  station-ID and broad-export semantics rather than extrapolating it.
- [ ] Verify dashboard labels: IST timestamps, pollutant units, AQI category
  boundaries (Very Poor 301--400; Severe 401--500), forecast versus observed
  status, 2024-validation versus 2025-test labels, source links and the
  non-diagnostic precaution wording.
- [ ] Test empty/missing inputs, unsupported dates, a station with low
  coverage and CSV-download output.  The application should abstain or show a
  clear limitation, never fabricate a forecast.

### 5. Comparisons worth doing only if time permits (optional; do not block submission)

- [ ] Add per-pollutant persistence and seasonal-naive baselines for the
  concentration models, evaluated on the exact same 2024/2025 rows.  This is
  the most valuable missing comparator for a claim that concentration ML adds
  forecasting value.
- [ ] Compare the pooled regional-weather model with station-specific weather
  only after station observations and as-of availability are verified.
- [ ] After pollutant timestamp semantics pass validation, run a frozen-split
  ablation of AQI history/weather versus +pollutant features.  Report the
  incremental result; do not assume pollutant usefulness.
- [ ] Compare direct multi-horizon forecasts with a recursive strategy on the
  same split.  Treat it as a separate experiment, not a retrofit to the
  selected model.
- [ ] Add a simple uncertainty benchmark (for example residual-quantile versus
  another validation-selected interval method) only if coverage and sharpness
  can be evaluated on held-out data.
- [ ] Add local explanation methods (such as SHAP) only as descriptive
  diagnostics; they are not evidence of causal pollution or weather effects.

### 6. Final presentation checklist (required)

- [ ] Prepare one concise results table for AQI and one for concentrations;
  move exhaustive station/pollutant tables to an appendix or downloadable CSV.
- [ ] Include a single architecture/data-flow graphic, the chronological split,
  the strongest baseline comparison, a station-performance distribution and a
  representative observed-versus-forecast/episode example.
- [ ] End with the limitations and next-step slide: recent official AQI panel,
  primary-source semantics, station-local/as-of weather and live-operation
  validation are future work.
- [ ] Have a reviewer reproduce the startup command and navigate the demo
  without author assistance.  Record defects and their resolution before
  declaring the project complete.

## Future extensions, outside the current dashboard scope

- [ ] Add a verified live or near-real-time CPCB feed, including publication-delay and quality checks.
- [ ] Add station-specific weather observations instead of one regional Delhi weather series.
- [ ] Add a verified 2026 annual concentration release after the year is complete and published.
- [ ] Assess health-outcome or hospital-admission data only with the required approvals and privacy safeguards; do not infer individual medical outcomes from pollution records alone.

## Future scope

- [ ] Live CPCB feed and real-time warning operation.

Source catalog: [annual CPCB-derived releases](https://github.com/Vonter/india-cpcb-aqi/releases). Release hashes are stored in `reports/source_evidence/recent_release_<year>.json`.
