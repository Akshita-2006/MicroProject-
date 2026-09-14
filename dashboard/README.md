# Dashboard

The dashboard runs from `dashboard/app.py`. It shows saved forecasts for seven Delhi stations at selected times in 2023.

Follow the installation commands in the [main README](../README.md). From the repository root, use the Python environment where you installed the dependencies:

```sh
python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8502
```

Open http://127.0.0.1:8502/ and keep the terminal running. Choose a station, date and hour in the sidebar.

| Tab | Contents |
|---|---|
| Forecast & episode | Next 24 hours, prediction ranges and sustained pollution periods |
| Historical trends | Past AQI readings for the selected station |
| Model evidence | Forecast errors, warning results and model inputs |
| Station comparison | Readings at the same time and checks for adding more stations |
| Methodology | Plain-language explanation from `docs/methodology_guide.md` |

The 2024–2025 downloads and extra station candidates are not connected to the saved forecasts yet. The dashboard is a historical demonstration, not a live service.

`legacy_app.py` is the earlier dashboard, kept for reference. Use `app.py` for the current project.
