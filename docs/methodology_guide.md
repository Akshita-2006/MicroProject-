# How the forecasts work

## What this dashboard shows

This dashboard uses past records to show what a forecast would have looked like at a selected time in 2023. It predicts AQI for each of the next 24 hours at seven Delhi monitoring stations. AQI describes air pollution; higher values mean worse air quality.

It does not show today's conditions. The 2024 and 2025 pollutant files have been downloaded and checked for missing records, but they have not been used to train these models. A later coverage check found 31 possible stations for expansion; these are not 31 additional trained models.

## Where the data comes from

AQI comes from the public Vonter/india-cpcb-aqi archive, which collects CPCB data. The working dataset covers 2017–2023. The seven station names were checked against an official CPCB list. Some source IDs are faulty, and the AQI timezone is assumed to be Indian Standard Time (IST); that assumption still needs official confirmation.

Weather comes from Open-Meteo historical records for one Delhi location. All seven stations use the same regional weather, which cannot describe every station's local conditions.

One small 2025 Alipur pollutant sample matched the official CPCB table. That check does not verify every station, date or timezone. Further comparisons remain unfinished after official downloads failed and the viewer showed a blank CAPTCHA and API errors.

## Why only seven stations?

The original selection required at least 85% of hourly AQI readings during 2017–2021, with no conflicting readings at the same time. Seven stations passed. This rule can exclude useful stations whose records started later.

A later check used 2019–2021 and found 31 candidates. The Station comparison tab shows the reasons. Their data must still be verified and their forecasts evaluated before they can enter the selector.

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

An earlier version of this project had already examined 2023. A test on a later, previously unused period is still needed. There are no model results for 2024, 2025 or 2026 yet.

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

The main tasks are verifying source times and station IDs, preparing recent AQI and weather, testing pollutant inputs, training more stations and evaluating later years. A live service would also need current data and checks on reporting delays.

Full calculation details are in `docs/methodology_v2.md`. Current results are in `reports/project_status.md`, and remaining tasks are in `docs/remaining_checklist.md`.
