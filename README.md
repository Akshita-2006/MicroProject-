# Delhi Air Quality Forecasting Project

## Purpose

This research project forecasts station-level calibrated AQI and pollutant concentrations for Delhi. It supports early identification of high-pollution periods and presents pollutant-specific hazards in plain language. It is not a live service, a medical tool, or an official CPCB advisory.

## Data and target

A uniform 2017–2025 Delhi pollutant panel covers 30 stations and seven pollutants: PM2.5, PM10, nitrogen dioxide, ozone, sulphur dioxide, carbon monoxide, and benzene.

Calculated AQI is created from pollutant concentrations using CPCB breakpoints and trailing averaging windows. A calibration model was fitted through 2022 against archived official AQI and checked on untouched official 2023 observations. The 2024–2025 target is calibrated AQI, not official CPCB hourly AQI.

## Evaluation design

| Stage | Period | Use |
| --- | --- | --- |
| AQI calibration fit | 2017–2022 | Map calculated AQI to archived official AQI |
| AQI calibration check | 2023 | Independent official-AQI agreement |
| Forecast training | 2017–2023 | Fit AQI and pollutant forecasts |
| Forecast validation | 2024 | Validate fixed forecast design |
| Final forecast test | 2025 | Report final results |

## Results

Official-AQI calibration check in 2023: R² 0.903, MAE 25.45 AQI points, RMSE 39.85 AQI points.

| AQI horizon | 2025 R² | 2025 MAE |
| --- | ---: | ---: |
| 1 hour | 0.956 | 16.95 |
| 6 hours | 0.845 | 35.47 |
| 12 hours | 0.816 | 38.56 |
| 24 hours | 0.782 | 41.96 |

Average 2025 pollutant-forecast R² values are 0.758, 0.566, 0.585 and 0.576 at 1, 6, 12 and 24 hours respectively. Pollutant values remain in their physical units; they are not percentages.

## Dashboard

Run `start_dashboard.ps1` from the project folder, then open `http://127.0.0.1:8502/`.

Select a station, date, and hour. The dashboard shows calculated AQI, category, recorded pollutants, pollutant hazards, concentration history, pollutant forecasts, and model evidence.

## Project documents

- `reports/calibrated_aqi_final.md` — final result summary and limitation.
- `docs/calibrated_aqi_protocol.md` — fixed evaluation protocol.
- `docs/data_sources.md` — dataset provenance.

## Limitation

The 2025 AQI forecast results evaluate calibrated AQI derived from the pollutant panel. They are not a direct comparison with a broad official CPCB 2025 hourly AQI archive.
