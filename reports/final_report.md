# Delhi Air-Quality Forecasting: Final Report

## Objective

This project delivers a 30-station Delhi air-quality research dashboard. It
replays historical AQI forecasts through 2023 and forecasts pollutant
concentrations through 2025. The dashboard also identifies likely sustained
high-pollution episodes in the 24-hour AQI replay horizon.

The project is not a live monitoring platform, official CPCB AQI service, or
medical decision system.

## Data and evaluation design

The historical AQI system uses station-level AQI and regional Delhi weather
for 2017--2023. The AQI replay evaluation is retrospective because the 2023
period had already been examined in the inherited project.

The concentration system uses a continuous 2017--2025 Delhi panel covering
30 stations and seven pollutants: PM2.5, PM10, NO2, ozone, SO2, CO, and
benzene. The split is chronological: training from 2017--2023, validation in
2024, and one final test in 2025.

## Models compared

XGBoost was compared fairly against persistence, seasonal naive forecasting,
and Random Forest on identical historical AQI test origins. Persistence
repeats the latest value; seasonal naive uses the same hour on the previous
day. XGBoost was also evaluated with five predefined feature groups: AQI
history, history plus time, history plus weather, history plus time and
weather, and full engineered features.

The selected approach is tuned XGBoost using full features: AQI lags and
rolling statistics, calendar variables, regional weather variables, and
station indicators.

| Horizon | Persistence MAE | Seasonal-naive MAE | Random Forest MAE | XGBoost MAE | XGBoost RMSE | XGBoost R² | Test rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 hour | 26.89 | 63.22 | 25.66 | **25.42** | 41.87 | 0.896 | 104,083 |
| 6 hours | 67.26 | 63.08 | 49.55 | **48.09** | 66.58 | 0.739 | 102,340 |
| 12 hours | 77.72 | 63.19 | 53.98 | **52.22** | 71.96 | 0.698 | 101,441 |
| 24 hours | 63.02 | 63.02 | 56.63 | **55.22** | 75.47 | 0.672 | 100,849 |

The results show that selected XGBoost achieves the lowest MAE at every
reported horizon. Full comparison and feature-ablation values are retained in
`experiments/results/all_eligible_30/model_comparison.csv`.

## Concentration and calibrated-AQI results

For the seven pollutant models, the same chronological split was used. The
calibrated-AQI target was fitted to archived official AQI through 2022 and
checked against 198,558 unseen station-hours in 2023: MAE 25.45, RMSE 39.85,
and R² 0.903.

| Horizon | 2024 validation R² | 2025 test R² | 2025 MAE |
|---|---:|---:|---:|
| 1 hour | 0.954 | 0.956 | 16.95 |
| 6 hours | 0.816 | 0.845 | 35.47 |
| 12 hours | 0.775 | 0.816 | 38.56 |
| 24 hours | 0.745 | 0.782 | 41.96 |

The calibrated-AQI values for 2024--2025 are derived from pollutant
observations. They must not be labelled as official CPCB hourly AQI values.

## Dashboard and verification

The Streamlit dashboard provides station/date/hour selection, historical AQI
replay, episode and warning output, recorded pollutant views, concentration
forecasting, model evidence, station comparison, and a methodology page.

The final verification run completed successfully:

- 21 of 21 automated tests passed.
- The 2023 AQI replay, 2024 concentration view, and 2025 pollutant view
  loaded without application exceptions.
- A local dashboard smoke test returned HTTP 200.

## Conclusion

The project is complete as a reproducible retrospective air-quality
forecasting dashboard. XGBoost was selected on validation evidence and
outperformed the included persistence, seasonal-naive, and Random Forest
comparators on the reported historical test horizons. The concentration and
calibrated-AQI results are clearly separated from official AQI claims.
