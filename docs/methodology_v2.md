# Corrected methodology and preregistered choices

## Data and provenance

AQI source: [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi), a CPCB-derived mirror. The local compressed wide file is preserved and hashed in `reports/tables/v2/data_manifest.json`; its bytes exactly match source commit `a58f47848e678c7cea58a69758343d08d0b49915`. Pinned source code, documentation, license and hash evidence are saved in `reports/source_evidence`. The source reports ODbL licensing; attribute the mirror and CPCB and preserve applicable database notices when redistributing. This is secondary-source data, not an independently authenticated CPCB export.

Station IDs in the inherited AQI file are defective. Normalized station names are the provisional keys. No city-wide representativeness claim is made. Selection requires at least 85% observed valid AQI on the full 2017–2021 hourly calendar and no conflicting duplicates. Later station commissioning is penalized by this fixed-period rule; exclusion does not establish that a station is intrinsically poor. All 39 candidates remain in the quality report. High AQI up to 500 is retained; only negative or above-scale AQI is invalidated, with raw values preserved. Repeated readings are flagged, not automatically removed.

All seven selected names and agencies were subsequently matched to the official [CPCB station list](https://airquality.cpcb.gov.in/ccr_docs/caaqms_list_All_India.pdf), downloaded from the government domain. The PDF, SHA-256 and exact row matches are preserved in `reports/source_evidence` and `official_station_name_matches.csv`. This confirms names, not numeric source IDs or measurement history. The current official historical repository is `https://airquality.cpcb.gov.in/ccr/#/repository/aqi`; its file listing is protected by CAPTCHA, so primary export verification is pending user completion of that step. An independently encountered non-government domain was not accepted as primary identity evidence.

[CPCB calculation guidance](https://cpcb.gov.in/displaypdf.php?id=bmF0aW9uYWwtYWlyLXF1YWxpdHktaW5kZXgvSG93X0FRSV9DYWxjdWxhdGVkLnBkZg%3D%3D) defines AQI from the largest pollutant sub-index, based on running concentration averages. We forecast the provided dimensionless AQI; we do not reconstruct it from a single instantaneous concentration. Thus hourly AQI persistence is not independent hourly exposure evidence. The mirror does not allow independent verification of every source sub-index.

## Pollutant investigation

The 2017 pollutant release was actually downloaded and inspected. It contains PM2.5, PM10, NO2, ozone, SO2 and CO, with substantial station-dependent missingness. Shadipur PM10 is entirely absent in this sample. This sample does not justify filling 2018–2023 pollutant features or claiming an evaluated pollutant model.

There is a material timezone concern: [the source parser](https://github.com/Vonter/india-cpcb-aqi/blob/main/parse.py) assigns UTC to timestamp strings with `replace_time_zone`, which is not evidence that the original strings were UTC. The [dictionary](https://github.com/Vonter/india-cpcb-aqi/blob/main/DATA.md) describes them as UTC. Original CPCB timestamp semantics must be verified before joining these observations with AQI. Consequently the primary experiment uses AQI history, not unverified pollutant joins. No pollutant predictive-utility experiment is claimed. The local sample and missingness report make the next investigation reproducible.

## Weather and issuance

The existing [Open-Meteo archive](https://open-meteo.com/en/docs/historical-weather-api) payload specifies the IST offset and records returned coordinates and units. One Delhi grid location is reused for all selected stations as a regional meteorological covariate. It is not on-site weather. Station-specific retrieval requires validated station coordinates and should be compared subsequently. AQI timestamps are provisionally treated as local IST; this assumption remains a limitation because the hourly source dictionary omits an explicit timezone statement.

Forecast issuance occurs after AQI and weather at t are available. No future weather is supplied. Retrospective reanalysis can contain revisions or information assimilation unavailable in real time; this study is an offline hindcast, not an operational availability test. A real service must ingest as-of observations and account for reporting latency.

## Experiments and leakage controls

Each station has a complete hourly grid. Features are computed separately and concatenated; no inter-station rolling or lag operations occur. No target imputation or future interpolation occurs. Complete cases of the full feature set define a common comparison sample for A–E, preventing ablation from changing evaluation dates. This restricts coverage and can bias evaluation toward well-observed periods; report counts.

Training: 2017–2021. Model/feature selection: January–June 2022. Interval calibration: July–December 2022. Retrospective test: 2023. Every boundary is purged so the target stays inside its assigned split. The test period was already examined by the inherited prototype; it cannot honestly be called a pristine external holdout.

Three predefined XGBoost parameter configurations cover learning rate, tree count/depth, child weight, row/column subsampling, gamma and L1/L2 regularization. Two expanding development folds validate on 2020 and 2021; every fourth eligible row is used during this limited-budget search. The mean fold MAE selects the tuning candidate. Five full-training ablations, the chosen tuning candidate, Random Forest and two baselines are compared on 2022 selection MAE separately by horizon. Test outcomes never select the model. This is a bounded search, not exhaustive optimization.

All models pool selected stations with station indicators. Persistence uses AQI(t). Seasonal naive uses the latest observed value at the target hour of day; at +24h it equals persistence. Models produce direct forecasts at each hour +1 through +24. Intermediate-hour configurations inherit the nearest required horizon's validation choice; their labels and fitted models are still hour-specific. No sparse-horizon interpolation is used.

ARIMA, recurrent networks and additional boosting libraries are deferred until these baselines establish value. No comparisons with unrun algorithms are reported. Direct versus recursive forecasting remains a documented extension, not a claimed experiment.

## Episode definition and evaluation

The research policy is AQI ≥301 for at least three consecutive observed/predicted hours. CPCB provides the category threshold, **not the three-hour persistence rule**. Three hours filters isolated spikes while retaining short warning lead times; it is a design choice, not a validated health threshold. Sensitivity is reported for 2, 3 and 6 hours without test-driven policy selection. Severe starts at 401. Continuous predictions are rounded only for display categories; threshold detection uses unrounded AQI ≥301.

All maximal qualifying runs are extracted. Missing hours break a run and do not prove recovery. Runs touching a window boundary or missing observation are censored; displayed durations are lower bounds when censored. Recovery is the first observed below-threshold hour, not a medical recovery prediction. Peak time is the first maximum within the available run.

Fixed-lead streams are evaluated at **target timestamps**. Events match one-to-one with positive temporal overlap, maximizing match count then overlap quality. Event precision, recall, F1, missed events and false alarms are distinct from hourly classification. Timing errors use matched events only; onset/duration/recovery errors omit corresponding censored endpoints. Event-level true negatives have no natural count.

A separate daily-issued, same-origin 24-hour warning evaluation reports the binary confusion matrix for whether any qualifying run occurs. Only windows with all 24 ground-truth values are scored. These daily windows measure warning presence, while fixed-lead streams measure event timing; neither is mislabeled as the other.

The same-origin trajectories are also evaluated for individual episode-segment matching and timing in `issued_episode_metrics.csv`. Each 24-hour window is independent; no concatenation across issuance times is permitted. This matches the dashboard forecasting setting. Multi-day episodes can appear as censored segments in successive windows, so these counts are not unique environmental events. Report the number of eligible timing matches alongside each timing mean; small uncensored duration samples cannot substantiate strong duration accuracy.

## Uncertainty and explanation

### Missing-history fallback extension

The original A–E ablations retain their common complete-case sample. A subsequent validation-only experiment compares native XGBoost missing-value handling, with and without missingness indicators, on incomplete histories. Both candidates use all eligible training origins with observed current AQI and target; no observation or target is imputed. The better incomplete-history validation MAE selects a fallback per required horizon, provided it beats persistence. The configuration is frozen before test evaluation. Intermediate hours inherit the nearest required horizon's configuration and are fitted directly.

The combined service keeps the original forecast on complete history and uses the fallback only for missing history. Current AQI must still be observed. Fallback interval calibration uses incomplete-history cases from the separate calibration period. Combined test and episode results are in `experiments/results/combined_system`, with each forecast tagged by route. Duplicate route keys are rejected. The wider population is explicitly distinguished from the original complete-case results; this is an availability improvement, not a claim of improved accuracy on identical cases. Missingness patterns may shift, and native missing handling does not verify the source measurements.

Absolute residuals from the separate calibration period define nominal 90% marginal intervals using a finite-sample quantile. Time dependence and seasonality violate simple exchangeability assumptions; report realized coverage rather than claiming guaranteed 90% reliability. These intervals are not event probabilities or simultaneous 24-hour bands. Calibration is pooled across stations, so per-station test coverage is essential.

Tree feature importances describe the fitted model's usage and can be biased by correlation. They are global, horizon-specific associations, not causal explanations or local SHAP values. Baselines have no tree importance. No invented confidence percentages or causal weather claims are displayed.


Official transmission-format evidence and unresolved interval-boundary/quality-flag semantics are recorded in [source access investigation](../reports/source_evidence/repository_access.md). The 2015 protocol does not establish the timezone of the mirrored public exports.
