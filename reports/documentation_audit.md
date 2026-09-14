# Documentation and dashboard audit — 14 September 2026

## Findings and changes

| Finding | Change |
|---|---|
| Dashboard guide said the app would be added later | Replaced with current launch instructions and tab descriptions |
| Methodology said CAPTCHA approval was pending | Corrected to the recorded download and viewer failures |
| Methodology used unexplained technical terms | Added a shorter guide for the dashboard; retained calculation details separately |
| Dashboard captions used terms such as abstention and censored endpoints | Explained missing readings and unknown episode start/end times in everyday language |
| Readers could confuse downloaded data with trained forecasts | Stated clearly that 2024–2025 files and extra station candidates are not used by current forecasts |
| Results used unexplained scores | Defined MAE, RMSE, R², precision, recall and F1 |
| Data-source notes still described the chosen archive as a candidate | Replaced with the actual inputs, checks and remaining limitations |
| Report wording included repeated claims about what was not invented or claimed | Replaced with direct descriptions and specific limitations; updated generators too |

## Verification

The loaded dataset has seven stations covering 2017–2023. The station screening has 31 candidates among 39 stations. The staged files contain 1,368,606 Delhi rows for 2024 and 1,366,609 for 2025. The README's forecast-error figures match the saved combined results.

All 17 existing tests passed with no skips. Streamlit AppTest loaded all five tabs and the new methodology without application exceptions. See [validation record](validation.md).

## Scope and remaining work

This pass reviewed the current public documentation and dashboard, checked key claims against code and saved results, and ran the existing checks. Historical evidence files remain records of their original dates. Technical references still use specialist terms where needed for reproducibility.

The project is not fully scientifically verified: source IDs and timezones, recent AQI targets, expanded training and later-year evaluation remain unfinished. See the [remaining checklist](../docs/remaining_checklist.md).
