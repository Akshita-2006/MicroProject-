# Delhi Pollution Episode Forecasting and Early Warning

A Python research project that forecasts station-level AQI at 1, 6, 12 and 24 hours, builds a complete 24-hour forecast trajectory, and detects sustained pollution episodes with onset, peak, severity, duration and recovery estimates.

**Current state:** seven Delhi stations, historical observations from 2017–2023, saved trained models and a Streamlit replay dashboard. It is not a live monitoring feed or an official CPCB advisory. Newer data and broader station coverage remain work in progress.

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

After installation, Windows users can also run:

```powershell
.\start_dashboard.ps1
```

The launcher prefers the repository's `.venv` interpreter, otherwise uses `python` from PATH, and starts the dashboard on port 8502. It resolves the project directory from the script's location.

`requirements-lock.txt` records the direct package versions used by this project; it is not a complete transitive dependency lock. `requirements.txt` contains unpinned package names. Prefer the recorded versions when loading the saved models.

## Using the dashboard

1. Select a monitoring station in the sidebar.
2. Choose a replay date and issue hour in IST. The current date picker covers 1 January–30 December 2023; it does not issue today's forecast.
3. Open **Forecast & episode** for the observed AQI, four forecast horizons, uncertainty bands, episode details and forecast download.
4. Open **Historical trends**, **Model evidence**, **Station comparison** or **Methodology** for the supporting analysis.

For a starting example, use Shadipur, 1 November 2023, 12:00 IST. Forecasts use history through the selected issue time. Incomplete past history uses the separately validated fallback when available; missing current AQI causes abstention. Recovery beyond the forecast window is shown as unobserved, not invented.

## What is implemented

- Audit of 39 stations, with seven selected using training-period coverage and conflicting-record checks.
- Hourly calendars, missingness and continuity reports, duplicate/range checks and exploratory analysis.
- Station-local AQI lags, rolling statistics, time features and regional weather inputs.
- Persistence and seasonal-naive baselines, Random Forest and XGBoost comparisons, five feature ablations and bounded time-aware hyperparameter tuning.
- Direct models for all 24 future hours; separately trained missing-history fallback models.
- Sustained episode detection: AQI at least 301 for three consecutive hours. Three hours is a research policy, not an official CPCB persistence rule.
- Episode matching, warning confusion matrices, timing errors, sample counts and censoring.
- Nominal 90% marginal prediction intervals and global tree feature importance.
- Saved-model inference, reproducible evaluation/report commands and twelve automated tests.

Current stations: Shadipur, DTU, NSIT Dwarka, ITO, IHBAS Dilshad Garden, Sirifort and Mandir Marg.

## Current results

Combined complete-history and missing-history system, pooled 2023 retrospective evaluation:

| Horizon | MAE (AQI points) | RMSE | R² |
|---|---:|---:|---:|
| 1 hour | 26.06 | 43.85 | 0.874 |
| 6 hours | 48.95 | 68.40 | 0.695 |
| 12 hours | 52.50 | 72.72 | 0.656 |
| 24 hours | 54.92 | 75.48 | 0.628 |

Daily any-episode warning precision/recall/F1: **95.3% / 72.8% / 82.6%**. Stricter individual episode-segment precision/recall/F1: **77.0% / 60.9% / 68.0%**.

Average onset/peak/recovery errors on matched, evaluable segments are approximately 2.0/3.9/3.2 hours. Duration error is 2.2 hours, but only 28 uncensored cases support that estimate.

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
│   └── processed/                    # Model-ready seven-station hourly panel
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
│   ├── final_report.md               # Engineering report
│   ├── missing_history_fallback.md   # Combined-system results and limitations
│   ├── current_state_audit.md        # Audit of inherited prototype
│   ├── validation.md                 # Test and dashboard verification record
│   ├── tables/v2/                    # Quality tables and data manifest
│   ├── figures/                      # Generated figures
│   └── source_evidence/              # Source hashes, licenses and official documents
├── docs/
│   ├── methodology_v2.md             # Data, splits, methods and limitations
│   ├── acceptance.md                 # Requirement-by-requirement status
│   └── remaining_checklist.md        # Outstanding work, including newer data/stations
├── tests/                            # Temporal, episode, replay and fallback tests
└── notebooks/                        # Notebook notes/supporting exploration
```

This tree shows the main maintained paths; earlier scripts and result files are retained for audit history. Use `run_pipeline.py` and `dashboard/app.py` for the current system. Results outside the named current experiment directories may belong to the earlier prototype.

## Data provenance and limitations

AQI comes from [Vonter/india-cpcb-aqi](https://github.com/Vonter/india-cpcb-aqi), which identifies CPCB as its source. The local archive was byte-verified against commit `a58f47848e678c7cea58a69758343d08d0b49915`. Evidence and source notices are in `reports/source_evidence/`; raw hashes are in `reports/tables/v2/data_manifest.json`. Attribution: CPCB and Vonter/india-cpcb-aqi; database ODbL, with individual contents potentially copyright CPCB. Preserve applicable source notices and database terms when redistributing.

Weather comes from the [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api), using one regional Delhi grid and IST timestamps.

The mirror's station IDs are faulty; names are used provisionally. Seven station names/agencies were matched to an official CPCB station list, but timestamp timezone and export semantics remain unresolved. AQI alignment currently assumes IST. Pollutants have not been joined because their timestamp semantics are ambiguous. Historical weather does not establish operational input availability.

The old station rule requires at least 85% coverage over the full 2017–2021 calendar, which disadvantages later-starting records. The latest official repository inspection lists 2026 Anand Vihar files, but these are not yet integrated. See the [remaining checklist](docs/remaining_checklist.md).

AQI 301–400 is Very Poor and 401–500 is Severe. The model has global feature importance, not local causal explanations. No LSTM/GRU, local SHAP, pollutant-utility or recursive-forecast experiment is claimed.

## Troubleshooting

| Problem | What to do |
|---|---|
| `ModuleNotFoundError` | Use the same interpreter for package installation and running commands; ordinary `python` may point to another installation. |
| Port 8502 is already in use | Open the existing server if it is this app, or launch with another port such as `--server.port 8503`. |
| Browser cannot connect | Check that the Streamlit terminal is still running and use its printed URL. |
| Missing data/model or incomplete-run message | Restore the required saved artifacts, or rebuild after supplying the raw inputs. |
| Forecast unavailable for a date | Check current AQI availability; abstention is expected for missing current inputs. |
| PowerShell blocks the launcher script | Use the direct Python/Streamlit command above; the launcher is optional. |
| Model loading fails after changing packages | Use the recorded versions and matching run artifacts; otherwise retrain and reevaluate in the new environment. |

## Reports to read

- [Engineering report](reports/final_report.md)
- [Current combined results](reports/missing_history_fallback.md)
- [Methodology](docs/methodology_v2.md)
- [Acceptance status](docs/acceptance.md)
- [Remaining work](docs/remaining_checklist.md)
- [Validation record](reports/validation.md)
