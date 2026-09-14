# Validation record — current summary (14 September 2026)

Latest full suite: **17 tests passed**. Streamlit AppTest passed after the station-audit dashboard change. The later interval helper has three dedicated tests and remains outside the current inference pipeline. No new-period model validation has been performed. Historical entries below record earlier checks and their smaller test counts; they are not the current total. See [project status](project_status.md).

---

# Validation record — 12 September 2026

- Twelve automated temporal/inference tests passed: future feature perturbation, boundary purge, gap rejection, missing-data censoring, spike rejection, one-to-one matching, saved-model/backtest equivalence and missing-current-input abstention; same-origin known timing errors, missing-truth exclusion and prevention of artificial cross-window episodes; plus fallback replay/future-invariance and disjoint forecast-route checks (some tests cover multiple assertions).
- Streamlit AppTest loaded the complete Shadipur forecast and episode without exceptions; switching to DTU also raised no application exception.
- Actual browser rendering was inspected. A dark/light theme conflict was found and corrected with project-local Streamlit theme configuration. Narrow-panel metric sizes were reduced to improve readability.
- All 24 saved hourly models produced a real forecast trajectory; inference at the same stored issue time matched the backtest numerically. Mutating future AQI values did not change the issued forecast.
- The training log records completed tuning, ablations, model comparison and all hourly fits. Generated outputs include station-level numeric/event/timing/warning metrics and uncertainty coverage.
- Local AQI SHA-256 matches the pinned public source file. This verifies byte provenance, not CPCB sensor validity or source timestamp semantics.

Known scientific limits are listed in the engineering report and methodology. Automated correctness tests do not establish real-world predictive reliability.

## 13 September follow-up

- Re-ran all twelve automated tests: passed in 3.424 seconds.
- Regenerated the engineering and missing-history reports from completed experiment outputs.
- Verified the running dashboard in the browser: forecast cards, episode timeline and uncertainty plot loaded without the previous missing-route cache exception. Cache keys now include relevant data, inference code and selection/completion artifact revisions.
- Recorded current code hashes separately in `experiments/results/combined_system/current_code_hashes.json`; the earlier training snapshot is preserved.


## 14 September station expansion audit

All fourteen tests passed, including new checks that future observations do not influence station screening and conflicting training records exclude candidates. Streamlit AppTest loaded without exceptions and confirmed the station expansion audit section is present. The audit identified 31 coverage candidates out of 39 archived stations; this does not certify new models or primary-source identity.


## 14 September interval verification

Seventeen tests passed in 5.131 seconds. New tests verify interval-end causality, incomplete-hour handling and invalid-source rejection. The primary Alipur comparison is reproducible with `python -m src.data_acquisition.compare_official_sample`: all 66 observed numeric cells and 14 missing cells match at the same Date From clock labels. This one sample does not certify timezone, all stations, other years or publication latency. The new aggregation helper remains outside training until source checks pass.

## Documentation and dashboard audit — 14 September 2026

Reviewed the current dashboard, README, methodology, data-source notes, status reports and report generators against code and saved artifacts. Corrected the obsolete dashboard placeholder and CAPTCHA-permission wording. Added a plain-language methodology page, explained model scores and simplified dashboard captions. Technical methods and original source evidence remain available.

Checks in this pass:

- Confirmed seven stations and 2017–2023 dates in the loaded model dataset.
- Confirmed 31 coverage candidates among 39 stations and the staged 2024/2025 row counts.
- Confirmed the README's four forecast-error rows against combined saved results.
- All 17 existing tests passed in 3.453 seconds, with no skips.
- Streamlit AppTest loaded five tabs and the new methodology text without application exceptions.

This verifies the checked code paths and consistency with local results. It does not independently verify all source readings, complete recent-data training or establish live forecast accuracy.
