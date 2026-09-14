# Recent pollutant data audit — 14 September 2026

The 2024 and 2025 public CPCB-derived mirror Parquet releases were downloaded and their SHA-256 hashes matched the digests published by GitHub. This verifies file identity, not CPCB observation validity. The all-India archives are preserved under `data/raw/recent_audit`; Delhi subsets are explicitly named `_unverified.parquet` under `data/interim`.

| Year | Delhi rows | Station IDs | Duplicate station/time rows |
|---|---:|---:|---:|
| 2024 | 1,368,606 | 39 | 0 |
| 2025 | 1,366,609 | 40 | 0 |

Timestamps are labelled UTC by the mirror. The earlier parser audit showed timezone assignment rather than established conversion; no IST conversion or issue-time join has been performed. These are 15-minute records, not hourly AQI targets. The release does not include the AQI target used by the current models. Deriving an AQI target would require verified units, averaging periods, completeness criteria and source comparison.

Coverage is measured per variable over the complete labelled year, including missing rows and null values. A populated timestamp does not imply a valid pollutant reading. Negative values and longest missing periods are reported, not automatically removed. Hourly groups with at least three observations are an audit diagnostic, not an endorsed aggregation rule.

Detailed tables: `reports/tables/recent_audit/stations_2024.csv`, `stations_2025.csv`, `variables_2024.csv` and `variables_2025.csv`. Provenance: `reports/source_evidence/recent_release_2024.json` and `recent_release_2025.json`.

The 2025 dataset includes 40 station identities; 35 have at least 85% observed PM2.5 values on the full year calendar. This external-period coverage statistic has not been used to select a model or tune hyperparameters.

Separately, the training-era expansion audit identifies 31 coverage candidates out of 39 historical AQI stations. Seven remain in the saved forecasting system. Additional candidates require source verification and executed model evaluation before being made forecastable.

Official repository downloads did not yield a file. The alternate Advanced Search table subsequently supplied an Alipur sample: ten rows matched all 66 numeric and 14 missing cells at interval-start clock labels. This bounded comparison does not certify timezone or other stations/periods. After a session reset, the CAPTCHA image remained blank after refresh and the page reported API errors; that session could not continue. Source export verification, recent AQI acquisition or validated target construction, 2026 acquisition, pollutant integration and expanded model evaluation remain incomplete.

## Reproduce the audit

Using your project Python environment from the repository root:

```sh
python -m src.data_acquisition.stage_recent_release --year 2024
python -m src.data_acquisition.stage_recent_release --year 2025
python -m src.analysis.audit_recent_pollutants --year 2024
python -m src.analysis.audit_recent_pollutants --year 2025
python -m src.analysis.reassess_stations
```

The two all-India downloads total about 1.54 GB. Source checks fail on a hash mismatch. These commands do not retrain or modify the current model selections.

## Subsequent source verification and preprocessing

The [saved comparison](source_evidence/alipur_official_2025_comparison.json) is reproducible with `python -m src.data_acquisition.compare_official_sample`. Interval-end aggregation is implemented and tested in `src/preprocessing/pollutant_intervals.py`, but is not yet connected to model training. See [current project status](project_status.md) for the complete remaining scope.
