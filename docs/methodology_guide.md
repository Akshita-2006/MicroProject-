# How the forecasts work

## What this dashboard shows

This dashboard uses past records to show what a forecast would have looked like at a selected time in 2023. It predicts AQI for each of the next 24 hours at 30 Delhi monitoring stations. AQI describes air pollution; higher values mean worse air quality.

It does not show today's conditions. The shared date selector also supports recorded pollutant concentrations for 2024–2025. Seven concentration models were trained on 2017–2023, checked in 2024, and evaluated once on 2025. Their predictions are separate from the AQI replay model.

## Where the data comes from

AQI comes from the public Vonter/india-cpcb-aqi archive, which collects CPCB data. The working dataset covers 2017–2023. Thirty station records passed the completed historical quality and evaluation process. Some source IDs are faulty, and the AQI timezone is assumed to be Indian Standard Time (IST); that assumption still needs official confirmation.

Weather comes from Open-Meteo historical records for one Delhi location. All stations use the same regional weather, which cannot describe every station's local conditions.

Official CPCB access now works again. Saved exports include 2025 Alipur and Anand Vihar pollutant samples, a 2026 Alipur sample and Anand Vihar’s January 2026 hourly AQI workbook. These are useful checks, but they do not verify every station, date, timezone or quality rule. The January AQI workbook covers only one station and month.

## Why 30 stations?

The original selection required at least 85% of hourly AQI readings during 2017–2021, with no conflicting readings at the same time. A later historical-panel build and evaluation produced 30 eligible stations. The station selector contains those 30 evaluated stations.

A separate 2019–2021 coverage screen identified 31 candidates. The Station comparison tab retains that audit for transparency; passing a coverage screen alone does not establish an evaluated forecast.

## How a forecast is made

The model uses AQI and weather available up to the selected time: recent readings, averages and changes over previous hours, the time of day and the station. It does not use future observations to make a forecast.

The project compares two simple methods—keeping the current AQI and using the latest reading from the target hour of day—with Random Forest and XGBoost machine-learning models. Separate models predict each of the next 24 hours.

If some past values are missing, a separately trained backup model can be used. If the current AQI is missing, no forecast is shown.

## How the models were checked

| Period | Purpose |
|---|---|
| 2017–2021 | Train the models |
| January–June 2022 | Choose models and input combinations |
| July–December 2022 | Set prediction ranges |
| 2023 | Compare forecasts with recorded observations |

The AQI replay model has no broad 2024–2025 hourly AQI target panel, so its chart and AQI metrics remain limited to 2023. The separate concentration models have a later untouched 2025 test period. There are no 2026 model results.

## What counts as a pollution episode?

The project marks an episode when AQI stays at **301 or higher for at least three consecutive hours**. The threshold comes from the CPCB Very Poor category; the three-hour rule is a project choice, not an official warning rule. AQI of 401 or higher is Severe.

For each predicted episode, the dashboard shows its start, highest AQI, duration and when AQI falls below 301. Here, recovery means that drop in AQI, not a health outcome. Missing hours interrupt an episode. If it extends beyond the 24-hour forecast, its full duration and end time are unknown.

## How to read the results

- **MAE:** average forecast error in AQI points. Lower is better. An MAE of 26 means predictions were about 26 points away from observations on average.
- **RMSE:** an error measure that gives more weight to large mistakes. Lower is better.
- **R²:** compares model errors with predicting the average observed AQI. Higher is better; it is not a percentage accuracy.
- **Precision:** how many predicted warnings were correct.
- **Recall:** how many actual episodes the system detected.
- **F1:** a score combining precision and recall.

A daily warning asks whether any episode occurs in the next 24 hours. Episode matching also checks whether individual predicted episodes overlap actual ones. These are different tests, so their scores differ.

Timing errors use only matched episodes with enough observations. Only 28 matches had fully known starts and ends for the combined duration result. That is too small a sample for a strong duration-accuracy claim.

## The shaded range and feature chart

The shaded range was set to aim for 90% coverage of individual hourly observations. In the 2023 evaluation, coverage was about 89% at one hour and 85.5% at 24 hours. It is not a guarantee or a 90% chance of an episode.

The feature chart shows which inputs the main model uses most across its predictions. It does not explain the cause of pollution or the exact reason for one forecast.

## What still needs work

The remaining task for later AQI testing is a broad, verified 2024–2025 hourly AQI target panel. A live service would also need current data and checks on reporting delays. The completed concentration-model work is recorded in the project status and checklist.

Full calculation details are in `docs/methodology_v2.md`. Current results are in `reports/project_status.md`, and remaining tasks are in `docs/remaining_checklist.md`.
