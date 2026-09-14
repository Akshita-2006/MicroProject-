# Execution checklist — 14 September 2026

The project is partly complete. See [current status](../reports/project_status.md) and [acceptance evidence](acceptance.md). Current model outputs remain seven-station 2023 retrospective results.

## Completed

- [x] Audit inherited prototype and 39 historical AQI stations; build seven-station 2017–2023 dataset and quality/EDA reports.
- [x] Execute historical baselines, RF/XGBoost comparisons, bounded tuning, five feature ablations and 24-hour direct forecasts.
- [x] Execute missing-history fallback, interval calibration, sustained episode detection, event/timing/warning evaluation and global feature importance.
- [x] Build historical replay dashboard and portable repository setup instructions.
- [x] Download/hash-verify/audit 2024–2025 mirror pollutant releases: 1,368,606 and 1,366,609 Delhi rows respectively.
- [x] Reassess training-era coverage: 31 candidates among 39 archived stations; display screening reasons in dashboard.
- [x] Record expanded train/selection/calibration/external-test periods before new-period model scores.
- [x] Capture and compare one official Alipur sample: 66 numeric values and 14 missing cells match interval-start clock labels.
- [x] Implement interval-end aggregation helper with explicit timezone and missing-quarter handling; keep it outside training pending source validation.
- [x] Pass 17 automated tests; verify station-audit dashboard with Streamlit AppTest.

## Partial or outstanding — in dependency order

- [ ] Restore official export/viewer access; the last session showed a blank CAPTCHA and API errors.
- [ ] Expand primary comparisons to additional stations/periods; establish station IDs, timezone, interval boundaries, quality filtering and reporting latency. One sample is not broad verification.
- [ ] Obtain recent AQI targets or validate their construction; acquire available 2026 observations.
- [ ] Integrate verified pollutant data and aligned recent weather; evaluate station-specific weather and actual as-of availability.
- [ ] Finalize an expanded model-ready dataset and defensible station roster; candidate status alone does not enable forecasts.
- [ ] Train/tune/compare expanded models and pollutant ablations using the recorded evaluation protocol; recalibrate uncertainty.
- [ ] Execute untouched-period 2025/2026 forecast, episode, warning and timing evaluation with sample sizes and censoring.
- [ ] Decide on sequence models, recursive forecasts and local explanations from validation evidence; record any justified deferral.
- [ ] Update dashboard forecast dates/stations only after new model artifacts are validated.
- [ ] Implement and validate current/as-of feeds if present-day early warning is required; current dashboard remains historical replay.
- [ ] Regenerate final reports/manifests, run final integration/browser checks and audit all original requirements before declaring completion.

Source acquisition/audit commands and evidence: [recent data audit](../reports/recent_data_audit.md). Reproducible primary comparison: `python -m src.data_acquisition.compare_official_sample`. Expanded experiment boundaries: [protocol](expanded_evaluation_protocol.json).
