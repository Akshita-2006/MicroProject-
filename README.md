# Delhi Pollution Episode Forecasting and Early Warning

A Python project that predicts air pollution at Delhi monitoring stations for each of the next 24 hours. It estimates when a period of high pollution may start, reach its peak and end.

**Current state:** 30 eligible Delhi stations, historical observations from 2017–2023, saved trained models and a Streamlit replay dashboard. It is not a live monitoring feed or an official CPCB advisory. The dashboard also contains a voluntary precaution profile; it does not diagnose disease or predict a medical outcome.

## Current progress — 25 September 2026

| Area | Current state |
|---|---|
| Running forecasts | 30 evaluated stations; historical AQI/weather data from 2017–2023. AQI replay charts use 2023, while the shared date selector also supports the 2024–2025 concentration view. |
| Recent data | Delhi concentration releases for every year from 2017 through 2025 are stored and SHA-256 checked against their release metadata. |
| Official evidence | CPCB viewer and spreadsheet exports work again. Saved evidence includes 2025 pollutant samples for Alipur and Anand Vihar, a 2026 Alipur sample, and Anand Vihar’s January 2026 hourly AQI workbook. This is not a city-wide recent AQI dataset. |
| Station expansion | 31 coverage candidates were identified among 39 historical stations. Thirty have usable 2017–2023 archived records and were trained in the expanded pooled model. |
| Concentration forecasts | 2,361,483 hourly station records across 30 stations. Seven pollutant models trained on 2017-2023, checked in 2024 and tested once on 2025. |
| Dashboard and tests | The 2024 validation and 2025 test concentration forecasts, accuracy views, and concentration-history chart are connected to the dashboard. The project has 21 passing automated tests. |
| Remaining work | Obtain broad official 2024-2025 hourly AQI targets only if the AQI model must also extend through 2025; live data remains future scope. |

See [current project status](reports/project_status.md) for the complete evidence and [remaining checklist](docs/remaining_checklist.md) for next steps. The results below remain 2023 retrospective scores, not results from the newly acquired data.

## Quick start

Install Python 3.12 and Git. Clone this repository using its GitHub **Code** URL, then open a terminal in the cloned folder (the folder containing `README.md`). All commands below use paths relative to that folder; no particular username or checkout location is required.

You do not need to retrain models to view the dashboard if the saved artifacts are available. Installing dependencies alone does not download data or models; see **Required data and saved artifacts** below.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8502
```

### macOS / Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8502
```

No environment activation is required. Open **http://127.0.0.1:8502/** in your browser. Keep the terminal open while using the app. Press **Ctrl+C** to stop it. If this app is already running on that port, open its URL instead of starting another copy.

If PowerShell or VS Code displays a line containing `Activate.ps1` or shows `(.venv)` before the prompt, it has only selected the project’s Python environment. Do not run `Activate.ps1` yourself; continue with the dashboard command.

After installation, Windows users can also run:

```powershell
.\start_dashboard.ps1
```

The launcher prefers the repository's `.venv` interpreter, otherwise uses `python` from PATH, and starts the dashboard on port 8502. It resolves the project directory from the script's location.

`requirements-lock.txt` records the direct package versions used by this project; it is not a complete transitive dependency lock. `requirements.txt` contains unpinned package names. Prefer the recorded versions when loading the saved models.

## Streamlit Community Cloud deployment

Before deploying, commit the dashboard runtime bundle to GitHub. It contains only the files needed by `dashboard/app.py`: the two processed panels, the 2024 and 2025 recorded-concentration files, saved model directories, and saved result files. The repository ignore rules already permit these exact files while continuing to exclude raw archives and training-only data.

```powershell
git add dashboard src requirements.txt .gitignore data/processed/delhi_hourly_all_eligible.parquet data/processed/delhi_concentrations_hourly_2017_2025.parquet data/interim/delhi_pollutants_2024_unverified.parquet data/interim/delhi_pollutants_2025_unverified.parquet experiments/models experiments/results/all_eligible_30 experiments/results/concentrations_2017_2025
git commit -m "Add Streamlit deployment bundle"
git push origin main
```

Then open [Streamlit Community Cloud](https://share.streamlit.io/), select the repository and `main` branch, set the entrypoint to `dashboard/app.py`, and click **Deploy**. Community Cloud redeploys after later pushes to that branch.

## Using the dashboard

1. Select a monitoring station in the sidebar.
2. Choose a date and issue hour in IST. The same selection is used by every tab. The AQI replay chart has evaluated target data through 2023. For 2024–2025, the main page changes to a concentration-forecast view with all seven pollutants across +1, +6, +12 and +24 hours.
3. For a 2023 selection, open **Forecast & episode** for the observed AQI, four forecast horizons, uncertainty bands, episode details and forecast download. For a 2024–2025 selection, open **Concentration forecast** for the seven-pollutant, four-horizon forecast grid.
4. Open **Pollutants** to view the corresponding selected date. Changing the date there also changes the sidebar date. Each recorded pollutant has a green, yellow, or red comparison against that station's 2025 readings, plus plain-language hazard information. In both 2024 and 2025, the tab shows 1/6/12/24-hour concentration forecasts; it labels 2024 validation accuracy separately from untouched 2025 test accuracy.
5. Open **AQI history** for a 2023 selection, or **Concentration history** for a 2024–2025 selection. The latter lets you choose one pollutant and see its recorded history for the selected station and period.

For a starting example, use Shadipur, 1 November 2023, 12:00 IST. Forecasts use history through the selected issue time. Incomplete past history uses the separately validated fallback when available; no forecast is made if the current AQI is missing. If AQI is not predicted to fall below 301 within 24 hours, its end time is shown as unknown.

## What is implemented

- Audit of 39 stations, with 30 eligible stations used in the expanded historical training set.
- Hourly calendars, missingness and continuity reports, duplicate/range checks and exploratory analysis.
- Station-local AQI lags, rolling statistics, time features and regional weather inputs.
- Persistence and seasonal-naive baselines, Random Forest and XGBoost comparisons, five input combinations and a limited search for model settings using earlier periods for training and later periods for validation.
- Direct models for all 24 future hours; separately trained missing-history fallback models.
- Sustained episode detection: AQI at least 301 for three consecutive hours. Three hours is a research policy, not an official CPCB persistence rule.
- Comparison of predicted and observed episodes, correct and missed warnings, timing errors and counts of cases with known start/end times.
- Prediction ranges targeting 90% coverage of individual hourly readings, plus a chart of the inputs the model uses most.
- Saved-model inference, reproducible evaluation/report commands and 21 automated tests.

The dashboard selector includes 30 eligible Delhi stations. Its concentration tab uses station names matched to the 2024-2025 public source releases.

## Current results

Results averaged across the 30-station expanded XGBoost models in 2023. MAE is average error in AQI points; RMSE gives more weight to large errors. Lower is better for both. R² measures fit, not percentage accuracy:

| Horizon | MAE (AQI points) | RMSE | R² |
|---|---:|---:|---:|
| 1 hour | 25.32 | 41.02 | 0.894 |
| 6 hours | 48.20 | 66.25 | 0.730 |
| 12 hours | 52.47 | 71.81 | 0.687 |
| 24 hours | 55.52 | 75.39 | 0.659 |

Precision is the share of predicted warnings that were correct; recall is the share of actual episodes detected. F1 combines the two. Daily warning precision/recall/F1: **95.3% / 72.8% / 82.6%**. Stricter individual episode-segment precision/recall/F1: **77.0% / 60.9% / 68.0%**.

Average onset/peak/recovery errors on matched, evaluable segments are approximately 2.0/3.9/3.2 hours. Duration error is 2.2 hours, but only 28 cases with fully known starts and ends support that estimate.

Forecast availability is **94.6%** of 2,548 scheduled daily windows; **74.3%** are evaluable for episodes after requiring future observations. Availability is not accuracy. Nominal 90% interval coverage is about 89.0% at 1 hour and 85.5% at 24 hours.

Training uses 2017–2021, model selection January–June 2022, and interval calibration July–December 2022. The inherited prototype already examined the 2023 era, so these are retrospective results, not an untouched external test. No 2025/2026 model results are claimed.

## Commands for tests, reports and training

From the project root, select the virtual environment created above (PowerShell):

```powershell
$projectPython = '.\.venv\Scripts\python.exe'
```

On macOS/Linux, replace `& $projectPython` in the commands below with `.venv/bin/python`.

Run the automated tests:

```powershell
& $projectPython -m unittest discover -s tests -v
```

Tests cover temporal boundaries, missing-data handling, episode matching, saved-model replay and disjoint forecast routes. Some artifact-dependent tests skip if trained artifacts are missing; inspect the output rather than treating skips as full validation.

Regenerate reports from saved results without training:

```powershell
& $projectPython run_pipeline.py --report-only
```

This recalculates primary same-origin episode evaluation and regenerates the fallback report when combined outputs exist, then writes the engineering report. It requires existing experiment outputs; it does not rebuild combined predictions.

Run the full current pipeline:

```powershell
& $projectPython run_pipeline.py
```

This prepares AQI/weather, audits the dataset, runs tests, trains/evaluates the primary models, evaluates episodes, selects and trains the missing-history fallback, combines results, reruns tests and generates reports. It can take substantial time and rewrites generated artifacts in the current result/model directories. Preserve a copy of an experiment before rebuilding if you need its exact outputs. The pipeline still targets 2017–2023; rerunning it does not add recent data or new stations automatically.

## Required data and saved artifacts

For the existing full dashboard, retain:

- `data/processed/delhi_hourly_v2.parquet`
- `experiments/models/v2/h1.joblib` through `h24.joblib`
- `experiments/results/v2/`, including selection and run manifests and evaluation tables
- `experiments/models/missing_history_fallback/` and `experiments/results/missing_history_fallback/`
- `experiments/results/combined_system/`, including `complete.json`

The fallback is enabled by completed combined-system artifacts. Keep model selections, models and evaluation outputs from the same run together.

For rebuilding, the pipeline expects `data/raw/cpcb-aqi.csv.gz` and `data/raw/weather_open_meteo_delhi_2017_2023.json`. It does not automatically retrieve the raw AQI archive. If the pollutant diagnostic sample is absent, it downloads the 2017 public release (approximately 107 MB); that sample is for investigation, not current model features.

Weather acquisition command, if needed:

```powershell
& $projectPython -m src.data_acquisition.download_weather_open_meteo --start-date 2017-01-01 --end-date 2023-12-31 --output data/raw/weather_open_meteo_delhi_2017_2023.json
```

Retain the hashed original weather for exact data reproduction: reanalysis revisions may change a new download.

## Project structure

```text
MicroProject/
├── README.md                         # Setup, usage, results and project guide
├── requirements.txt                  # Unpinned direct dependencies
├── requirements-lock.txt             # Recorded direct dependency versions
├── run_pipeline.py                   # Current training/evaluation/report entry point
├── start_dashboard.ps1               # Windows dashboard launcher
├── .streamlit/config.toml            # Dashboard theme and local-server settings
├── configs/                          # Supporting configuration files
├── dashboard/
│   ├── app.py                        # Current Streamlit dashboard
│   └── legacy_app.py                 # Preserved earlier dashboard
├── data/
│   ├── raw/                          # Original compressed AQI, weather and pollutant sample
│   ├── interim/                      # Reshaped hourly data and source diagnostics
│   └── processed/                    # Model-ready historical station panels
├── src/
│   ├── data_acquisition/             # Downloads, provenance and station-source checks
│   ├── preprocessing/                # AQI/weather conversion; earlier preprocessing retained
│   ├── analysis/                     # Quality audit, EDA and report generators
│   ├── features/hourly.py            # Current leakage-aware feature construction
│   ├── models/
│   │   ├── run_episode_system.py      # Primary model comparisons, tuning and 24-hour fits
│   │   ├── validate_missing_history.py # Validation-only fallback comparison
│   │   └── train_missing_fallback.py  # Fallback training, calibration and evaluation
│   ├── forecasting/service.py        # Saved-model inference and warning generation
│   ├── episode_detection/timeline.py # Gap-aware episode extraction and matching
│   └── evaluation/
│       ├── issued_episodes.py        # Same-origin episode/window evaluation
│       └── combine_fallback.py       # Combine disjoint primary/fallback predictions
├── experiments/
│   ├── models/                       # v2/ and missing_history_fallback/ saved models
│   ├── results/
│   │   ├── v2/                       # Primary complete-history results and selections
│   │   ├── missing_history_validation/ # Fallback candidate validation evidence
│   │   ├── missing_history_fallback/  # Fallback predictions and selections
│   │   └── combined_system/          # Current combined metrics and predictions
│   └── logs/                         # Recorded experiment execution logs
├── reports/
│   ├── project_status.md             # Current results and remaining work
│   ├── final_report.md               # Engineering report
│   ├── missing_history_fallback.md   # Combined-system results and limitations
│   ├── current_state_audit.md        # Audit of inherited prototype
│   ├── validation.md                 # Test and dashboard verification record
│   ├── tables/v2/                    # Quality tables and data manifest
│   ├── figures/                      # Generated figures
│   └── source_evidence/              # Source hashes, licenses and official documents
├── docs/
│   ├── methodology_guide.md          # Plain-language dashboard explanation
│   ├── methodology_v2.md             # Technical details and assumptions
│   ├── acceptance.md                 # Requirement-by-requirement status
│   └── remaining_checklist.md        # Outstanding work, including newer data/stations
├── tests/                            # Temporal, episode, replay and fallback tests
└── notebooks/                        # Notebook notes/supporting exploration
```

This tree shows the main maintained paths; earlier scripts and result files are retained for audit history. Use `run_pipeline.py` and `dashboard/app.py` for the current system. Results outside the named current experiment directories may belong to the earlier prototype.

## Data provenance and limitations

AQI comes from [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi), which identifies CPCB as its source. The local archive was byte-verified against commit `a58f47848e678c7cea58a69758343d08d0b49915`. Evidence and source notices are in `reports/source_evidence/`; raw hashes are in `reports/tables/v2/data_manifest.json`. Attribution: CPCB and Vonter/india-cpcb-aqi; database ODbL, with individual contents potentially copyright CPCB. Preserve applicable source notices and database terms when redistributing.

Weather comes from the [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api), using one regional Delhi grid and IST timestamps.

The mirror's station IDs are faulty; names are used provisionally. Seven station names/agencies were matched to an official CPCB station list, but AQI timezone and broader export semantics remain unresolved. A bounded Alipur pollutant comparison supports interval-start labels for that sample; see the [primary comparison](reports/source_evidence/alipur_official_2025_comparison.json). AQI alignment currently assumes IST. Pollutants have not been joined because their timestamp semantics are ambiguous. Historical weather does not establish operational input availability.

The old station rule requires at least 85% coverage over the full 2017–2021 calendar, which disadvantages later-starting records. An official January 2026 Anand Vihar hourly AQI workbook is now stored as source evidence, but it covers one station and month and is not integrated. See the [remaining checklist](docs/remaining_checklist.md).

AQI 301–400 is Very Poor and 401–500 is Severe. The model has global feature importance, not local causal explanations. No LSTM/GRU, local SHAP, pollutant-utility or recursive-forecast experiment is claimed.

## Troubleshooting

| Problem | What to do |
|---|---|
| `ModuleNotFoundError` | Use the same interpreter for package installation and running commands; ordinary `python` may point to another installation. |
| Port 8502 is already in use | Open the existing server if it is this app, or launch with another port such as `--server.port 8503`. |
| Browser cannot connect | Check that the Streamlit terminal is still running and use its printed URL. |
| Missing data/model or incomplete-run message | Restore the required saved artifacts, or rebuild after supplying the raw inputs. |
| Forecast unavailable for a date | Check current AQI availability; no forecast can be made without current readings. |
| PowerShell blocks the launcher script | Use the direct Python/Streamlit command above; the launcher is optional. |
| Model loading fails after changing packages | Use the recorded versions and matching run artifacts; otherwise retrain and reevaluate in the new environment. |

## Reports to read

- [Current project status](reports/project_status.md)
- [Engineering report](reports/final_report.md)
- [Recent data audit](reports/recent_data_audit.md)
- [Current combined results](reports/missing_history_fallback.md)
- [How the forecasts work](docs/methodology_guide.md)
- [Technical methodology](docs/methodology_v2.md)
- [Acceptance status](docs/acceptance.md)
- [Remaining work](docs/remaining_checklist.md)
- [Validation record](reports/validation.md)
- [Documentation audit](reports/documentation_audit.md)

### Station expansion audit

Run `python -m src.analysis.reassess_stations` using your project environment to generate the 39-station coverage screen. It identifies 31 candidates using 2019–2021 observations only; 30 have usable archived records and evaluated expanded forecast models. The dashboard Station comparison tab shows the screening reasons. New-period evaluation boundaries are recorded in `docs/expanded_evaluation_protocol.json`; training on recent data remains gated on source verification.

Recent concentration acquisition and quality findings are documented in [recent data audit](reports/recent_data_audit.md). The 2017-2025 concentration model uses the documented chronological split: train 2017-2023, select in 2024 and test once in 2025. The AQI forecast date range and reported AQI scores remain retrospective until official 2024-2025 AQI targets are acquired.

