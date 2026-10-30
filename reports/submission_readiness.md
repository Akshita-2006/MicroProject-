# Submission readiness record — 30 October 2026

## Decision

**Ready to submit as the scoped retrospective research dashboard.** The
submission claim is limited to a 30-station archived-AQI replay through 2023,
2017--2025 pollutant concentration forecasting, and a separately labelled
calibrated-AQI experiment. It is not a live service, medical advice, or an
official 2024--2025 CPCB hourly-AQI product.

The remaining external-source limitations are documented as limitations, not
open local defects. A broad official 2024--2025 hourly AQI target panel is
needed only for a future claim of official-AQI evaluation after 2023.

## Release identity

| Item | Value |
|---|---|
| Frozen model/data baseline revision | `2d7058ca0dd53e82817c1c98953b6e2f49f58f3b` |
| Python runtime | 3.13.5 |
| Dependency lock | `requirements-lock.txt` |
| AQI replay stations | 30 |
| Historical AQI period | 2017--2023 |
| Concentration split | train 2017--2023; validation 2024; test 2025 |

## Verification performed

| Check | Result |
|---|---|
| Automated suite | **21/21 tests passed** in 12.318 seconds using `python -m unittest discover -s tests -v`. |
| Dashboard application test | Streamlit AppTest completed with no application exceptions. |
| 2023 dashboard route | Historical AQI replay loaded successfully. |
| 2024 dashboard route | Concentration forecast view loaded successfully. |
| 2025 dashboard route | Pollutant-record view loaded successfully. |
| Local server smoke test | Streamlit returned HTTP 200 from `127.0.0.1:8503`; process was stopped after the check. |
| Documentation scope | `README.md`, `docs/acceptance.md`, `docs/remaining_checklist.md`, `reports/project_status.md`, and the current addendum in `reports/final_report.md` use the scoped claim above. |

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| `data/processed/delhi_hourly_all_eligible.parquet` | `D259ACD3F63F214A68F9CB5D4F6DAC7807862BE9B88E9D4DDD7ECBF2826E53F7` |
| `data/processed/delhi_concentrations_hourly_2017_2025.parquet` | `E641D28BC7E49E13B260331C2FD0E64CF240A840AA99DA773C4109B0F4F3ADB3` |
| `experiments/results/all_eligible_30/model_comparison.csv` | `7B1165F18A138A10F9121C5099B4EBFF057AF37E53E7887296E0323E0805055D` |
| `experiments/results/concentrations_2017_2025/metrics.csv` | `49EECE6EB7FCF201B5D26C75A341D6EFD1FECD36D72B10BF0FADB592CE7201CD` |
| `experiments/results/all_eligible_30/run_manifest.json` | `36CDAAD8D50701D42CF71CB7ECC9B52B362D87E7C04F11495FDC55209EC5B05F` |
| `experiments/results/concentrations_2017_2025/manifest.json` | `DBF8FA9FB73F68BBEB04F9E5B538093944E8FCCADF344DB702C40E375A40EF0C` |

## Required presentation language

- Report archived-AQI replay metrics separately from concentration and
  calibrated-AQI metrics.
- Label 2023 AQI evaluation as retrospective because the inherited prototype
  had already inspected that era.
- Label 2024 as concentration-model validation and 2025 as its untouched final
  test.
- Do not call the pollutant-derived 2024--2025 calibrated-AQI target an
  official CPCB AQI observation.
- Keep source timezone, station-ID, publication-latency and broad
  official-export verification limitations visible in the report.

The detailed final-review comparison plan is in
[`docs/remaining_checklist.md`](../docs/remaining_checklist.md).
