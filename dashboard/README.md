# Dashboard

The dashboard runs from `dashboard/app.py`. It shows saved AQI replay forecasts for 30 eligible Delhi stations at selected times in 2023, plus recorded 2024–2025 pollutant concentrations.

Follow the installation commands in the [main README](../README.md). From the repository root, use the Python environment where you installed the dependencies:

```sh
python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8502
```

Open http://127.0.0.1:8502/ and keep the terminal running. Choose a station, date and hour in the sidebar. The Pollutants tab uses the same date; changing its date updates the sidebar as well.

| Tab | Contents |
|---|---|
| Forecast & episode | Next 24 hours, prediction ranges and sustained pollution periods |
| Pollutants | Recorded 2024-2025 concentrations; plain-language pollutant effects and green/yellow/red station-relative comparison; 2024 validation and 2025 1/6/12/24-hour concentration forecasts with their correctly labelled accuracy, and an optional non-diagnostic precaution profile |
| AQI history / Concentration history | Past AQI readings for a 2023 selection; for a 2024–2025 selection, recorded history for the chosen pollutant at the same station |
| Model evidence | Forecast errors, warning results and model inputs |
| Station comparison | Readings at the same time and checks for adding more stations |
| Methodology | Plain-language explanation from `docs/methodology_guide.md` |

For a 2024 or 2025 date, the main tab changes to a concentration-forecast grid: seven pollutants by +1, +6, +12 and +24 hours. Recorded concentrations are also available in the Pollutants tab. Their colours compare a reading to the same station's 2025 records: green is lower than the median, yellow is from the median to the 90th percentile, and red is at or above the 90th percentile. These colours are not health limits. The concentration forecasts were trained on 2017-2023, checked on 2024 and tested once on 2025. R² is labelled as a model-quality score, not a pollution percentage or medical score. The dashboard is not a live service.

`legacy_app.py` is the earlier dashboard, kept for reference. Use `app.py` for the current project.
