> Historical audit of the inherited prototype, preserved as a baseline. For the current implemented state and remaining work, read [project status](project_status.md).

# Current-state audit — 12 September 2026

The inherited project is a working Shadipur regression demonstration. Its raw inputs, acquisition utilities, initial EDA, model families, and Streamlit foundation are reusable. Existing result files are historical prototype outputs, not valid final comparisons.

## Findings before implementation

- AQI conversion retains missing station-days as absent rows. Shadipur has 59,568 rows across a 61,344-hour period. Row shifts consequently do not always represent hour lags or forecast horizons.
- The apparent 98.18% coverage excludes absent days. Coverage must use an explicit hourly calendar.
- Station ID repeats across different Delhi names; use normalized station name, retain the defective source ID only for provenance, and investigate upstream metadata.
- Feature generation uses only past rows, but does not enforce single-station, continuous-hour inputs.
- Persistence uses AQI at t−1 although AQI at t is in the dataset. Correct comparison assumes issuance after the observation at t becomes available.
- Splitting after feature-specific dropna produces different periods and evaluation samples between ablations.
- Training labels cross validation boundaries; purge by target timestamp, not just origin timestamp.
- Tuning results do not determine the deployed model. Test-based statements about the best feature set compromise claims of untouched evaluation.
- Weather timestamps are naive; payload timezone, offset, coordinates and units require explicit verification. Archive reanalysis is retrospective, not proof of operational feature availability.
- Event scores classify individual threshold exceedances. They are not sustained-event precision/recall.
- The episode helper returns only the first run, can bridge gaps, and treats missing values like recovery.
- Four sparse horizons cannot establish hourly onset, duration or recovery. An hourly forecast trajectory is required; interpolation cannot be presented as measured timing skill.
- Dashboard shows historical predictions at issue timestamps, no persisted inference models, no station selection, no uncertainty or actual warning cards.
- README runtime/status statements are stale. The final report overstates leakage safety and calls previously inspected test outcomes held-out final evidence.

## Execution decisions

Preserve legacy scripts and results for traceability. Add a versioned corrected pipeline with fixed calendar splits and station-isolated hourly features. Select stations using pre-test coverage only; inspect all stations without choosing by test performance. Freeze model selection on validation, reserve a separate calibration interval, and explicitly call the 2023 test a retrospective holdout because this source period was already inspected in the prototype. Use current-AQI persistence and daily seasonal naive baselines. Test event gaps, censoring and one-to-one matching independently of model accuracy.

The sample in the supplied request mislabels AQI 358 as Severe. CPCB's Very Poor category spans 301–400; Severe starts at 401. The implementation will use the correct categories.
