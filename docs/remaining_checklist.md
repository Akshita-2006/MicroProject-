# Remaining work — 13 September 2026

## Data recency and station coverage
- [ ] Acquire and audit 2024–2025 AQI/pollutant data and available 2026 observations. Do not treat 2026 as a complete year.
- [ ] Verify official export timestamps, timezone, interval boundaries, station IDs and quality flags against the inherited mirror.
- [ ] Reassess all available Delhi stations using coverage within their operating periods and recent common windows, with explicit minimum history requirements.
- [ ] Include major locations where data support reliable models; show unavailable/excluded stations with reasons. The old 85% rule over the entire 2017–2021 calendar is not a current network-coverage policy.
- [ ] Evaluate PM2.5, PM10, NO2, O3, SO2 and CO for availability and predictive benefit after source validation.
- [ ] Update weather through the same period and evaluate station-specific weather alignment; distinguish retrospective weather from inputs actually available at issue time.

## Experiments and scientific validation
- [ ] Freeze the new train/selection/calibration/untouched-test periods before examining new-period model scores. Preserve original retrospective results.
- [ ] Refit baselines and candidate models on the expanded verified data, repeat feature ablations and time-aware tuning, and evaluate each station/horizon.
- [ ] Recalibrate intervals and measure coverage on the new test period, separately for complete and incomplete histories.
- [ ] Re-evaluate same-origin episode detection, warning errors and onset/peak/duration/recovery timing. Report censoring and sample sizes; short trajectories cannot establish full multi-day episode duration.
- [ ] Decide from evidence whether sequence models, recursive forecasts or local explanations add enough value; do not present these unexecuted options as completed experiments.

## Product and delivery
- [ ] Update dashboard dates and station inventory from validated artifacts, with source freshness, history limits and station exclusion reasons.
- [ ] If current early warning is required, implement an authorized live/as-of data feed and validate latency, missing inputs and forecast issuance. Current dashboard is historical replay.
- [ ] Regenerate the report, quality tables, dependency/code/data manifests and acceptance checklist after expanded experiments.
- [ ] Run inference/leakage tests and browser checks for the expanded system, then audit all original requirements before declaring completion.

## Completed foundation
- [x] Audit of 39 stations; seven-station retrospective AQI/weather dataset and data-quality reports.
- [x] 1/6/12/24-hour regression evaluation, 24-hour trajectories, baselines, RF/XGBoost comparisons, bounded tuning and feature ablations.
- [x] Gap-aware sustained episode detection, timing metrics, warning evaluation, calibrated marginal intervals and global feature importance.
- [x] Validation-selected missing-history fallback; 94.6% scheduled daily forecast availability in the evaluated 2023 sample. This is availability, not prediction accuracy.
- [x] Saved inference pipeline, twelve passing automated tests, dashboard and reproducible engineering reports.
- [x] User-approved CPCB CAPTCHA submitted successfully on 13 September 2026. Repository UI lists Anand Vihar hourly AQI files for January–August 2026; downloaded file contents are not yet verified.
