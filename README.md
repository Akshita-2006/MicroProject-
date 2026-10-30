# Delhi Air-Quality Forecasting Dashboard

A 30-station Delhi air-quality research dashboard. It provides historical AQI
replay forecasts through 2023 and pollutant-concentration forecasts through
2025. It is not a live monitoring system, an official CPCB advisory, or
medical advice.

## Run the dashboard

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\start_dashboard.ps1
```

Open `http://127.0.0.1:8502` in a browser. Select a station, date, and hour.
Choose a 2023 date for AQI replay or a 2024--2025 date for concentration
forecasting.

## What the project contains

- Historical AQI replay for 30 Delhi stations, using 2017--2023 AQI and
  regional weather data.
- Direct 1--24 hour AQI forecasts, episode warnings, prediction ranges, and
  station comparison.
- Seven pollutant concentration models: PM2.5, PM10, NO2, ozone, SO2, CO, and
  benzene. They train on 2017--2023, validate on 2024, and test once on 2025.
- A calibrated-AQI experiment derived from pollutant observations. It is kept
  separate from official CPCB AQI.

## XGBoost model comparison

XGBoost was compared on the same 2023 retrospective test origins against:

- **Persistence:** repeats the latest observed AQI.
- **Seasonal naive:** uses the AQI from the same hour on the previous day.
- **Random Forest:** a second tree-based machine-learning model.
- **Feature ablations:** AQI history only; history plus time; history plus
  weather; history plus time and weather; and the full engineered feature set.

The selected model is tuned XGBoost with the full feature set. Lower MAE and
RMSE are better; higher R² is better.

| Horizon | Persistence MAE | Seasonal-naive MAE | Random Forest MAE | XGBoost MAE | XGBoost RMSE | XGBoost R² | Test rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 hour | 26.89 | 63.22 | 25.66 | **25.42** | 41.87 | 0.896 | 104,083 |
| 6 hours | 67.26 | 63.08 | 49.55 | **48.09** | 66.58 | 0.739 | 102,340 |
| 12 hours | 77.72 | 63.19 | 53.98 | **52.22** | 71.96 | 0.698 | 101,441 |
| 24 hours | 63.02 | 63.02 | 56.63 | **55.22** | 75.47 | 0.672 | 100,849 |

The full machine-readable comparison is in
`experiments/results/all_eligible_30/model_comparison.csv`.

## Concentration and calibrated-AQI results

The calibrated-AQI target was fitted against archived official AQI through
2022, then checked on unseen 2023 official observations: **MAE 25.45, RMSE
39.85, R² 0.903** across 198,558 station-hours. This does not make the
2024--2025 calibrated values official CPCB AQI observations.

| Forecast horizon | 2024 validation R² | 2025 test R² | 2025 MAE |
|---|---:|---:|---:|
| 1 hour | 0.954 | 0.956 | 16.95 |
| 6 hours | 0.816 | 0.845 | 35.47 |
| 12 hours | 0.775 | 0.816 | 38.56 |
| 24 hours | 0.745 | 0.782 | 41.96 |

## Verification

The repository has **21 passing automated tests**. They cover temporal
boundaries, future-data isolation, gap handling, episode matching, station
screening, saved-model replay, and pollutant interval contracts.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Project layout

```text
dashboard/        Streamlit application
src/              Data preparation, forecasting, evaluation, and analysis code
tests/            Automated tests
data/             Local datasets (not all source data is stored in Git)
experiments/      Saved model artifacts and evaluation outputs
reports/          Final report and validation record
docs/             Dashboard methodology shown inside the application
```

For the formal results and scope, read [the final report](reports/final_report.md).
For test evidence, read [the validation record](reports/validation.md).
