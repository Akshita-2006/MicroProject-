# Acceptance evidence

| Requirement | Evidence / status |
|---|---|
| Investigate multiple Delhi stations; select defensible set | 39 audited, seven selected by training coverage; station_quality.csv |
| Document historical data and weather | Pinned byte-verified source, local raw hashes, source license and weather payload metadata |
| Quality report, hourly dataset and EDA | reports/tables/v2; delhi_hourly_v2.parquet; monthly patterns and correlations |
| Leakage-safe features and audit | src/features/hourly.py; current_state_audit.md; temporal tests |
| Baselines and ML | Current persistence, seasonal naive, RF and XGBoost executed |
| Missing-history availability | Validation-selected native-missing fallback fitted for all 24 hours, separately calibrated and evaluated; 94.6% daily forecast availability, 74.3% evaluable windows. No target imputation. |
| Hyperparameter optimization | Three configurations, two expanding folds per horizon; tuning.csv; bounded rather than exhaustive |
| Feature ablation | Five controlled groups with common samples; model_comparison.csv |
| 1/6/12/24h evaluation | selected_horizon_results.csv; station results and complete model table |
| Episode definition and detection | Three-hour policy, threshold 301, gap-aware extraction; sensitivity at 2/3/6h |
| Onset, severity, peak, duration, recovery | 24 direct hourly forecasts; extract() and dashboard cards; censored endpoints explicit |
| Event precision/recall/F1 and timing | Fixed-lead event_metrics.csv and pooled_event_metrics.csv; same-origin issued_episode_metrics.csv and match/exclusion records. Uncensored duration sample is small. |
| Warning performance | Daily same-origin 24h binary warning confusion matrices; warning_metrics.csv |
| Explainability and uncertainty | Horizon-specific global tree importance and calibrated marginal intervals; no local SHAP or event probabilities claimed |
| Selection without test tuning | Selection uses January–June 2022; test era was already examined by inherited prototype |
| Dashboard | Station/date/hour replay, episodes, forecast bands, historical trends, model evidence, station comparison, methodology |
| Reproducibility and report | run_pipeline.py, saved models, locked dependency versions, README and 17-part engineering report |
| Verified pollutant integration | **Not met:** sample investigated, upstream timestamp semantics unresolved; excluded rather than joined speculatively |
| Primary-source station identity/timezone validation | **Partial:** all seven station names/agencies matched to the government-domain CPCB PDF; source IDs and timestamp semantics remain unresolved. Current repository route is reachable but requires CAPTCHA verification. |
| Truly untouched external and operational validation | **Not met:** later independent data and as-of feeds needed |

The implemented deliverable is an expanded, evaluated offline research prototype. The three unmet scientific requirements above must remain visible; they cannot be resolved by claiming that software tests passed.
