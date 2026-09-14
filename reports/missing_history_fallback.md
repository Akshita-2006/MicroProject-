# Missing-history fallback evaluation

The complete-history model remains unchanged. When a 73-hour calendar window contains missing past values, a separately trained XGBoost fallback uses native missing-value handling. Target values are not filled in, and no forecast is made when current AQI is missing. Validation chooses between native missing handling with and without missingness indicators, using incomplete-history MAE at each required horizon. The nearest required horizon supplies the configuration for intermediate hours. Calibration uses missing-history July–December 2022 cases separately for each forecast hour.

## What changed and why

The prior complete-case policy excluded many otherwise usable forecast origins. Training the fallback on all training origins with observed current/target AQI allows it to learn from incomplete history. Existing complete-history forecasts are preserved, so differences in their recorded accuracy cannot be attributed to this change. Test outcomes do not choose the fallback policy.

Validation-only comparison on incomplete histories:

| horizon | variant | n | mae | persistence_mae |
|---|---|---|---|---|
| 1.000 | native_missing | 16137.000 | 34.655 | 35.786 |
| 1.000 | native_missing_flags | 16137.000 | 34.644 | 35.786 |
| 6.000 | native_missing | 15660.000 | 64.649 | 84.976 |
| 6.000 | native_missing_flags | 15660.000 | 63.970 | 84.976 |
| 12.000 | native_missing | 15457.000 | 66.508 | 96.688 |
| 12.000 | native_missing_flags | 15457.000 | 66.317 | 96.688 |
| 24.000 | native_missing | 15395.000 | 66.822 | 79.659 |
| 24.000 | native_missing_flags | 15395.000 | 66.681 | 79.659 |

## Coverage and combined accuracy

Evaluable daily windows increased from 1,082 of 2,548 (42.5%) to 1,894 of 2,548 (74.3%). Produced windows increased from 1,289 to 2,410. Remaining omitted cases include missing current observations and missing future truth. Evaluable coverage is not identical to forecast availability.

Combined retrospective test regression (a broader population than the old complete-case table):

| station | horizon | fallback_n | interval_coverage | n | mae | rmse | r2 |
|---|---|---|---|---|---|---|---|
| ALL | 1.000 | 25980.000 | 0.890 | 56713.000 | 26.064 | 43.847 | 0.874 |
| ALL | 6.000 | 25490.000 | 0.862 | 55883.000 | 48.948 | 68.402 | 0.695 |
| ALL | 12.000 | 25234.000 | 0.857 | 55434.000 | 52.501 | 72.722 | 0.656 |
| ALL | 24.000 | 25030.000 | 0.855 | 55046.000 | 54.925 | 75.480 | 0.628 |

## Warnings and episode timing

Binary daily warning TP=646, FP=32, FN=241, TN=975; precision=0.953, recall=0.728, F1=0.826. These metrics concern whether any sustained episode occurs in a window.

Episode-segment matching and timing within each same-origin trajectory:

| metric | value |
|---|---|
| eligible_windows | 1894.000 |
| actual_episode_segments | 1383.000 |
| predicted_episode_segments | 1093.000 |
| matched_segments | 842.000 |
| precision | 0.770 |
| recall | 0.609 |
| f1 | 0.680 |
| onset_error_hours | 2.036 |
| onset_error_hours_n | 304.000 |
| peak_error_hours | 3.895 |
| peak_error_hours_n | 842.000 |
| duration_error_hours | 2.214 |
| duration_error_hours_n | 28.000 |
| recovery_error_hours | 3.201 |
| recovery_error_hours_n | 358.000 |
| scheduled_windows | 2548.000 |
| produced_windows | 2410.000 |
| abstained_windows | 138.000 |
| excluded_produced_windows | 516.000 |
| evaluated_fraction | 0.743 |

Timing means remain conditional on matched segments and censoring. More complete coverage does not establish accurate event duration, an external holdout, verified pollutant alignment, or real-time validity. The test era was previously inspected. No comparison between different evaluation populations should be described as a pure accuracy improvement.

Files: experiments/results/combined_system contains combined predictions, numeric results, fixed-lead event results, daily binary warnings and same-origin episode matches. The two source populations are checked for duplicate forecast keys before combining. Each returned forecast identifies its route.
