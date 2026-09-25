# Calibrated AQI forecasting protocol

## Question

Can recent station-level pollutant history forecast a calibrated AQI value one to twenty-four hours ahead across Delhi?

## Target construction

The 2017--2025 pollutant panel is converted to a CPCB-breakpoint calculated AQI using only trailing pollutant averages. A calibration model maps calculated AQI, pollutant concentrations, calendar terms and station identity to archived official AQI. It is fitted through 2022 and checked only on official 2023 observations. The 2023 overlap is never used for calibration fitting.

The 2024--2025 target is therefore **calibrated AQI**, not an official CPCB hourly AQI release.

## Forecast split

| Role | Period | Permitted use |
| --- | --- | --- |
| Forecast training | 2017--2023 | Fit candidate models only |
| Validation | 2024 | Choose one forecast configuration and interval settings |
| Final test | 2025 | One final report only; never tune after inspection |

All lagged predictors must end at the forecast issue time. Rows whose target crosses a split boundary are excluded from the earlier split.

## Required reporting

Report MAE, RMSE, R2, AQI-category accuracy, warning precision/recall/F1, 90% interval coverage, station-level results and seasonal results. Compare against persistence and seasonal-naive baselines. State the official-overlap agreement separately from 2024--2025 forecast performance.
