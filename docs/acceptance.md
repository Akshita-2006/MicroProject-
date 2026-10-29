# Acceptance evidence — current review baseline (29 October 2026)

**Current decision: implementation evidence is established for the scoped
research dashboard; final submission acceptance is pending the required final
review checks.** The dashboard is a 30-station retrospective Delhi air-quality
research system. It is not a live monitoring service, an official CPCB AQI
release, or medical advice.

Two results must remain distinct throughout the review:

- **Archived-AQI replay:** official/archived AQI and regional weather for 30
  stations through 2023. Its reported evaluation stops in 2023.
- **Concentration and calibrated-AQI experiments:** a 2017--2025 concentration
  panel, seven pollutant models with 2024 validation and untouched 2025 test,
  plus a separate pollutant-derived calibrated-AQI experiment. Neither creates
  an official 2024--2025 CPCB hourly AQI target panel.

| Requirement | Status | Evidence and remaining scope |
|---|---|---|
| Multi-station historical AQI system | Implemented | 30 eligible Delhi stations, hourly 2017--2023 AQI/weather panel, direct 1--24 hour replay models and station selector. The station screen was fixed before the held-out historical evaluation. |
| Historical AQI baselines and model comparison | Implemented | Persistence, seasonal naive, Random Forest, XGBoost, validation-only tuning and A--E feature ablations are saved in `experiments/results/all_eligible_30/model_comparison.csv`. The 2023 period was previously inspected in the inherited work, so it is retrospective rather than a fully external test. |
| AQI episodes, warning output and uncertainty | Implemented with limits | Episode matching, warning metrics, hourly trajectories and nominal 90% marginal intervals are implemented. Timing is conditional on matched/censoring-eligible events; intervals are not event probabilities or simultaneous trajectory guarantees. |
| Historical AQI evaluation period | Partial | The model has evaluated archived targets through 2023 only. A broad, validated official 2024--2025 hourly AQI target panel is still required for later official-AQI testing. |
| Continuous concentration data | Implemented | SHA-256-checked annual releases form a 2017--2025 hourly Delhi panel with 2,361,483 station-hour records across 30 stations. Units, gaps and source provenance remain documented. |
| Concentration forecasting | Implemented | PM2.5, PM10, NO2, ozone, SO2, CO and benzene models train on 2017--2023, validate on 2024 and test once on 2025. Metrics are in `experiments/results/concentrations_2017_2025/metrics.csv`. This is model performance for measured concentrations, not official AQI performance. |
| Calibrated-AQI experiment | Implemented with explicit limitation | The calculated/calibrated target uses pollutants. Calibration agreement with archived official 2023 AQI is MAE 25.45, RMSE 39.85 and R² 0.903 over 198,558 station-hours. Its 2024--2025 target is not an official CPCB AQI observation. |
| Official recent-source evidence | Partial | CPCB viewer/export evidence and bounded pollutant samples are saved. The Alipur comparison verifies one sample only; it does not establish universal timezone, station-ID, reporting-latency or export semantics. |
| Weather | Partial | Regional Delhi weather is available and evaluated in the historical system. It is not station-local and does not prove operational as-of availability. |
| Dashboard | Implemented for scoped replay | The dashboard supports 30-station historical AQI replay through 2023 and recorded/forecast concentration views for 2024--2025. It labels forecast versus observation and validation versus test periods. |
| Automated and UI checks | Implemented; rerun required for release | The latest recorded full suite passed 21 tests, with Streamlit AppTest/smoke checks recorded in `reports/validation.md`. The final dated rerun is a submission gate, not a scientific-validity guarantee. |
| Documentation consistency | In progress | Current scope is stated in `README.md` and `reports/project_status.md`. This matrix and the addendum in `reports/final_report.md` supersede their older seven-station snapshots. |
| Final submission acceptance | Pending final review | Complete the required items in `docs/remaining_checklist.md`: evidence freeze, dated tests/UI check, source/data release checks, required comparison tables and final claim/slide review. |

## Acceptance conditions that remain out of scope

The following are valuable extensions, not conditions for accepting the scoped
retrospective dashboard: a verified live CPCB feed, station-specific
meteorology, operational publication-delay handling, a recursive-model
comparison, local explanation methods, or health-outcome inference. A broad
official 2024--2025 AQI panel becomes required only if the project claims
official-AQI evaluation beyond 2023.

For the executable final-review tasks and comparison plan, see the
[remaining checklist](remaining_checklist.md). For the authoritative current
implementation summary, see [project status](../reports/project_status.md).
