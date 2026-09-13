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
