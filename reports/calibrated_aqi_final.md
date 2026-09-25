# Final local calibrated-AQI experiment

## Scope

This local experiment forecasts a **calibrated AQI** from a uniform 2017--2025 Delhi pollutant panel. It is not an official CPCB AQI forecast or a live advisory.

## Target and safeguards

- Published CPCB pollutant breakpoints and trailing windows produce calculated AQI.
- A calibration model is fitted only through 2022 against archived official AQI.
- Official 2023 AQI is held out for calibration agreement: MAE 25.45, RMSE 39.85, R2 0.903 (198,558 station-hours).
- AQI forecast models train on 2017--2023 calibrated AQI, use 2024 only for validation, and report 2025 once as the final test.
- No 2025 values were used to fit or choose the reported model settings.

## Forecast results

| Horizon | 2024 validation R2 | 2025 test R2 | 2025 MAE |
| --- | ---: | ---: | ---: |
| 1 hour | 0.954 | 0.956 | 16.95 |
| 6 hours | 0.816 | 0.845 | 35.47 |
| 12 hours | 0.775 | 0.816 | 38.56 |
| 24 hours | 0.745 | 0.782 | 41.96 |

## Limitation

The 2024--2025 target is calibrated from pollutant measurements because a broad official hourly AQI target archive was not available. The 2025 scores measure this documented calibrated-AQI system, not agreement with an official 2025 CPCB AQI release.
