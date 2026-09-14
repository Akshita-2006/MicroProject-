# Acceptance evidence — 14 September 2026

**Overall: incomplete.** Read the [current status](../reports/project_status.md) for completed work, limitations and the unchanged model results. “Implemented” below describes the existing retrospective system, not acceptance of the expanded recent-data system.

| Requirement | Status | Evidence / remaining scope |
|---|---|---|
| Multi-station investigation | Implemented; expansion partial | 39 stations audited; seven evaluated models; 31 training-era coverage candidates. New candidates require source checks and model evaluation. |
| Historical AQI/weather dataset and EDA | Implemented | 2017–2023 panel, quality/continuity/missingness tables and regional weather metadata. |
| Recent pollutant acquisition and audit | Implemented for 2024–2025 mirror | 2,735,215 Delhi rows; release hashes verified; station/variable quality reports. Not model-ready and no verified 2026 acquisition. |
| Primary source identity and timestamps | Partial | Seven names/agencies matched to official PDF; one Alipur sample matches 66 values/14 missing cells at interval starts. IDs, timezone and broader applicability remain unresolved. |
| Interval-safe pollutant preprocessing | Implemented, not integrated | Explicit-timezone helper with interval-end aggregation and three focused tests. No production join or target derivation yet. |
| Leakage-safe AQI features | Implemented | Station-local hourly features, purged splits and temporal tests. |
| Baselines and ML | Implemented on historical panel | Persistence, seasonal naive, RF/XGBoost, five ablations and bounded tuning. Expanded-data experiments not run. |
| Multi-horizon forecasts and missing-history fallback | Implemented | 24 direct hourly models and fallback; 1/6/12/24h evaluation; 94.6% scheduled daily availability. |
| Episodes and early-warning evaluation | Implemented with limits | Same-origin matching, confusion matrices, timing/censoring; duration evidence is only 28 uncensored combined cases. |
| Uncertainty/explainability | Partial scope | Marginal intervals/global importance executed; long-horizon coverage below nominal. No local SHAP or event probabilities. |
| Untouched later-period validation | Not executed | Protocol recorded; no new-period model scores. |
| Pollutant predictive usefulness | Not executed | Concentrations audited but not joined, trained or ablated. |
| Updated/station-specific weather | Outstanding | Current inputs use one regional historical grid; recent weather and as-of availability not validated. |
| Dashboard | Implemented historical replay | Seven forecast stations; expansion audit and reasons visible; newer forecast dates/stations not enabled. |
| Live operational delivery | Not implemented | No validated current data feed, publication latency or as-of forecasting service. |
| Reproducibility/documentation | Implemented with limits | Portable README, current pipeline, saved artifacts and audit commands. Direct dependency versions recorded, not a full transitive lock. |
| Tests | Latest suite passed | 17 tests; Streamlit check after station-audit update passed. Tests do not establish scientific validity. |
| Final acceptance | Not achieved | Source verification, recent target/data integration, expanded training/external validation and final artifact checks remain. |

Current blocker: official download failures and a blank CAPTCHA/API error after the successful bounded table comparison. See [source access evidence](../reports/source_evidence/repository_access.md).
