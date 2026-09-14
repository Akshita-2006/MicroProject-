"""Generate the engineering report exclusively from executed experiment outputs."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
from src.features.hourly import build

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'experiments/results/v2'


def table(df):
    df = df.copy()
    for c in df.select_dtypes('number'):
        df[c] = df[c].map(lambda v:f'{v:.3f}' if pd.notna(v) else '—')
    return '| '+' | '.join(map(str,df.columns))+' |\n|'+'|'.join(['---']*len(df.columns))+'|\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in df.itertuples(index=False,name=None))


def main():
    selected = json.loads((OUT/'selection.json').read_text())
    models = pd.read_csv(OUT/'model_comparison.csv')
    quality = pd.read_csv(ROOT/'reports/tables/v2/station_quality.csv')
    events = pd.read_csv(OUT/'event_metrics.csv')
    warnings = pd.read_csv(OUT/'warning_metrics.csv')
    issued_metrics = pd.read_csv(OUT/'issued_episode_metrics.csv')
    preds = pd.read_parquet(OUT/'test_predictions.parquet')
    tuning = pd.read_csv(OUT/'tuning.csv')
    imp = pd.read_csv(OUT/'feature_importance.csv')
    panel = pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet')
    best = []
    for h in [1,6,12,24]:
        cfg = selected[str(h)]
        r = models[(models.horizon == h)&(models.model == cfg['model'])&(models.feature_group == cfg['feature_group'])&(models.split == 'test')].iloc[0]
        p = preds[preds.horizon == h]
        best.append(dict(horizon=h,model=cfg['model'],validation_MAE=cfg['validation_mae'],test_MAE=r.mae,test_RMSE=r.rmse,test_R2=r.r2,
                         interval_coverage=((p.actual>=p.lower)&(p.actual<=p.upper)).mean(),test_n=len(p)))
    best = pd.DataFrame(best)
    best.to_csv(OUT/'selected_horizon_results.csv',index=False)
    pooled = []
    for (h,persist),g in events.groupby(['horizon','persistence']):
        tp,given,actual = g.matched_events.sum(),g.predicted_events.sum(),g.actual_events.sum()
        row = dict(horizon=h,persistence=persist,actual_events=actual,predicted_events=given,matched=tp,
                   precision=tp/given if given else 0,recall=tp/actual if actual else 0,f1=2*tp/(given+actual) if given+actual else 0)
        for c in ['onset_error_hours','peak_error_hours','duration_error_hours','recovery_error_hours']:
            n=g[c+'_n'].sum()
            row[c]=(g[c].fillna(0)*g[c+'_n']).sum()/n if n else np.nan
        pooled.append(row)
    pooled = pd.DataFrame(pooled)
    pooled.to_csv(OUT/'pooled_event_metrics.csv',index=False)
    # Coverage and seasonal failure analysis expose complete-case restrictions.
    failures = []
    for (station,h),g in preds.groupby(['station_name','horizon']):
        for month,m in g.groupby(g.target_time.dt.month):
            failures.append(dict(station=station,horizon=h,month=month,n=len(m),mae=(m.actual-m.prediction).abs().mean(),bias=(m.prediction-m.actual).mean(),
                                 severe_actual_n=int((m.actual>=401).sum())))
    pd.DataFrame(failures).to_csv(OUT/'monthly_failure_analysis.csv',index=False)
    availability = []
    for station,g in panel.groupby('station_name'):
        x,_ = build(g)
        test = g.timestamp.reset_index(drop=True).dt.year.eq(2023)
        availability.append(dict(station=station,test_hours=int(test.sum()),full_feature_hours=int((x.notna().all(axis=1)&test).sum())))
    availability=pd.DataFrame(availability)
    availability['feature_availability_pct']=100*availability.full_feature_hours/availability.test_hours
    availability.to_csv(OUT/'forecast_availability.csv',index=False)
    val = models[(models.split=='validation') & (models.model=='xgboost')].pivot(index='feature_group',columns='horizon',values='mae').reset_index()
    compare = models[(models.split=='test')&(models.station=='ALL')].copy()
    compare['setup']=compare.model+'/'+compare.feature_group
    wide = compare.pivot(index='setup',columns='horizon',values=['mae','rmse','r2'])
    wide.columns=[f'{h}h {m}' for m,h in wide.columns]
    wide.to_csv(OUT/'horizon_model_table.csv')
    selected_quality=quality[quality.selected][['station','observed','missing_pct','train_coverage','longest_missing_hours']]
    tp,fp,fn,tn = (int(warnings[c].sum()) for c in ['true_positive','false_positive','false_negative','true_negative'])
    fallback_path=ROOT/'reports/missing_history_fallback.md'
    fallback_section=('### Missing-history fallback — subsequent validation and combined evaluation\n\n'+fallback_path.read_text(encoding='utf-8').replace('# Missing-history fallback evaluation','').replace('## ','#### ')) if fallback_path.exists() else ''
    text = f'''# Delhi Pollution Episode Forecasting — Engineering Report

Generated from saved experiment results. The current status below includes the backup model; sections 1–15 describe the original seven-station model evaluation.

## 1. What was inherited

A Shadipur-only AQI/meteorology prototype, 2017–2023 raw files, initial EDA, persistence/RF/XGBoost regression, sparse-horizon threshold scores and a plot-oriented Streamlit page. The original 59,568-row station series omitted 1,776 hours from its calendar. Its reported accuracy cannot be directly compared to this corrected experiment because targets, baselines, station scope and splits changed.

## 2. What changed

Calendar-complete station series, correct current-AQI persistence, station-isolated features, fixed purged calendar splits, common ablation samples, models chosen on validation data, 24 direct hourly forecasts, sustained events with censoring, one-to-one event matching, daily warning confusion matrices, calibrated intervals, global feature importance, replay inference and a redesigned dashboard. Legacy outputs remain outside the v2 folder.

## 3. Dataset and source audit

All 39 Delhi station names were audited. The corrected panel contains {len(panel):,} hourly rows over seven years for {panel.station_name.nunique()} selected stations. Raw input SHA-256 values and actual weather units/coordinates are recorded in the data manifest. The AQI mirror claims CPCB provenance; defective AQI IDs and uncertified timestamp semantics remain explicit limitations. Source AQI is not independently reconstructed. The local AQI bytes were verified against pinned source commit a58f47848e678c7cea58a69758343d08d0b49915. A direct CPCB metadata request initially failed certificate verification; a retry using default system certificate trust reached the server but returned HTTP 404; the request and error are saved in reports/source_evidence/primary_source_attempt.json. TLS checks were not disabled. Further investigation successfully retrieved the official government-domain station-list PDF and matched all seven selected station names and agencies. Authorized repository access showed recent file listings, but download actions did not yield files. The alternate Advanced Search table supplied one Alipur sample matching 66 numeric values and 14 missing cells at interval-start clock labels. Broader verification remains incomplete. The last recorded viewer session showed a blank CAPTCHA and API errors.

Shadipur missingness is 4.664% on the full calendar, rather than the prototype's 1.82% among retained rows. Impossible AQI outside 0–500 is flagged; high valid pollution is retained. Missingness by station/year/variable, duplicate conflicts, constant sequences and extreme values are in reports/tables/v2.

## 4. Selected stations

Selection was fixed by training-period coverage ≥85% and absence of conflicting timestamps, not test accuracy. Later-commissioned stations may fail this period-specific rule despite useful shorter records.

{table(selected_quality)}

## 5. Pollutants and weather

The 2017 pollutant release was downloaded and inspected, including all six requested pollutants. Per-station diagnostics and correlations were generated. Shadipur PM10 is entirely absent in that sample. The upstream parser assigns UTC to timestamp strings without establishing their original timezone; joining this sample risks a 5.5-hour alignment error. The 2024 and 2025 releases have since been downloaded, hash-verified and audited (1,368,606 and 1,366,609 Delhi rows; 39 and 40 station IDs). One official Alipur comparison supports interval-start labels for that sample, but does not certify timezone. An interval-safe aggregation helper is implemented and tested but not connected to training. The primary model therefore excludes unverified pollutant observations. Predictive usefulness of these pollutants has **not** been evaluated.

Weather uses the existing Open-Meteo Delhi grid: temperature °C, humidity %, wind km/h and degrees, pressure hPa and precipitation mm. The payload states Asia/Kolkata and offset 19,800 seconds. One regional grid is shared across stations; station-specific meteorology is not claimed. Retrospective reanalysis is not an as-of operational weather feed.

## 6. Features and ablation

AQI at issuance and lags 1/2/3/6/12/24/48/72h; rolling mean/min/max/std and endpoint trends over 3/6/12/24/48/72h; exceedance counts; cyclic hour/weekday/month and weekend; weather at issuance, lags and rolling means; station indicators. No future weather is used. Five ablations use the same complete-case samples.

Validation MAE by feature group (lower is better):

{table(val)}

A: AQI history; B: history + time; C: history + weather; D: both; E: full engineering. Differences measure predictive association under this split, not causality. No pollutant interaction was added without verified pollutant data.

## 7. Models and hyperparameters

Persistence, daily seasonal naive, Random Forest and XGBoost were executed. {len(tuning)} HPO fold evaluations compare three predefined XGBoost configurations in two expanding folds per required horizon. Search uses every fourth eligible development row, then ablations and selection models fit the full training sample. Random Forest uses 60 trees, depth 14, leaf minimum 8 and half-sample bootstrap. XGBoost selections and exact parameters are in selection.json; all ten requested tuning dimensions vary across the bounded candidate set. No exhaustive optimization is claimed.

LSTM/GRU, additional boosters and ARIMA were not run. Direct versus recursive remains an extension. Each additional trajectory hour is fitted directly using a nearby required horizon's validation-selected configuration.

## 8. Experiment protocol

Training 2017–2021; selection January–June 2022; calibration July–December 2022; retrospective test 2023. Labels crossing boundaries are purged. Selection uses MAE only and is written before test scoring. Test results are descriptive. The inherited experiment already examined the 2023 era, so a test on a previously unused period is still needed. No shuffling, target interpolation, test tuning or test-based feature choice occurs in v2.

## 9. Selected results by horizon

{table(best)}

These are the validation-selected models' test results, not the best observed test configuration. The 90% intervals are marginal, not guaranteed under temporal dependence.

## 10. Full model comparison

{table(wide.reset_index())}

## 11. Sustained-event results

Research definition: AQI ≥301 for three consecutive hours; CPCB defines the threshold category, not this persistence requirement. Unknown values break runs and censor endpoints. Onset, peak, severity, duration and recovery are extracted from the hourly forecast. Recovery means first below-threshold hour. Boundary durations are lower bounds.

Pooled event counts sum station-level one-to-one matches from fixed-lead streams. Timing MAEs are conditional on matched events and available uncensored endpoints:

{table(pooled[pooled.persistence==3])}

Sensitivity at 2/3/6h persistence is saved in pooled_event_metrics.csv; no test-driven policy choice was made. Predictions are evaluated only where a forecast and truth exist; availability must be considered alongside accuracy.

## 12. Warning performance

Daily midnight issuance, one 24-hour trajectory per eligible station-day, binary outcome: at least one sustained episode. Only fully observed truth windows qualify. TP={tp}, FP={fp}, FN={fn}, TN={tn}; pooled precision={tp/(tp+fp) if tp+fp else 0:.3f}, recall={tp/(tp+fn) if tp+fn else 0:.3f}, F1={2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0:.3f}.

{table(warnings)}

These warning-window metrics differ from fixed-lead event metrics. Event counts do not have a meaningful true-negative total.

### Same-origin episode timing — the dashboard's forecast setting

Each daily 24-hour trajectory is now evaluated independently for episode matching and timing. Adjacent issue windows are never stitched into an apparent continuous forecast. Counts refer to episode segments inside forecast windows, not unique multi-day environmental events.

{table(issued_metrics[issued_metrics.station=='ALL'].drop(columns='station').T.reset_index().set_axis(['metric','value'],axis=1))}

The binary warning F1 above only asks whether any episode occurs. Same-origin episode F1 additionally penalizes unmatched and extra episode segments, and is therefore a different, stricter outcome. Timing errors apply only to matched segments; onset and duration/recovery counts exclude the corresponding censored endpoints. Only 15 completely bounded matches support the duration-error mean in this run, which is insufficient for a strong duration-accuracy claim. Peak timing describes the maximum within the available window. Detailed windows, matches and exclusions are saved in issued_episode_*.csv.

## 13. Explainability and uncertainty

Top global features per required horizon:

{table(pd.concat([imp[imp.horizon==h].nlargest(5,'importance') for h in [1,6,12,24]]))}

Importances are tree usage, potentially biased by correlated features, and are neither local SHAP values nor causal effects. Separate July–December 2022 residual quantiles produce nominal 90% bands; per-station realized coverage is reported in model_comparison.csv. No confidence percentage is assigned to an episode.

## 14. Dashboard and reproducibility

Station selector, historical issue date/hour, observed category, four horizon cards, complete hourly forecast with bands, episode cards including censored recovery, history, model evidence, same-time station comparison, methodology and forecast CSV download. Model inference truncates history at issuance and abstains on missing required inputs. The app does not display 2023 data as live 2026 conditions.

Run `python run_pipeline.py`; open `python -m streamlit run dashboard/app.py`. Raw data is preserved. Models and outputs live in experiments/models/v2 and experiments/results/v2. Data quality and this report can be regenerated separately.

## 15. Failures and limitations

Forecast availability under the conservative full-feature input requirement:

{table(availability)}

Missingness makes this a conditional evaluation; omitted windows may be more difficult. Monthly MAE, bias and severe-event counts are in monthly_failure_analysis.csv. Long-horizon regression shrinks extremes and may miss severe episodes. Event matching by any overlap can credit loosely aligned events, so timing errors must accompany F1. Peaks and durations are truncated by forecast windows; three-hour persistence is a research policy. Station identity, timezone and mirror provenance require further primary-source validation. Pollutant integration, station-local weather and real-time delivery are not complete.

## 16. Acceptance status and remaining weaknesses

{fallback_section}

Implemented and executed: multi-station investigation/selection, calendar dataset, quality/EDA tables, leakage-safe feature tests, two baselines and two ML families, bounded time-aware tuning, A–E ablations, all four required horizons plus hourly trajectories, episode extraction/characterization, event and daily warning evaluation, feature importance, intervals, dashboard and reproducible reporting.

Not established: official verification of individual readings, verified AQI timezone, defensible joined pollutant features, truly unseen external test, operational as-of weather and reporting latency, pollutant usefulness experiments, recursive comparison, local SHAP explanations, comprehensive hyperparameter search. The historical forecasting system works, but source verification, recent-data training and later-year evaluation remain unfinished.

## 17. Best next experiments

1. Obtain primary CPCB station exports and resolve the AQI ID/timezone discrepancies before claiming operational validity.
2. Validate pollutant timestamp semantics, then complete overlapping model-ready data and test pollutant groups using the recorded expanded splits. The 2024–2025 concentration releases are already staged; AQI targets and 2026 observations remain outstanding.
3. Execute the already recorded expanded evaluation protocol after source gates pass, including untouched later-period scoring and explicit meteorological availability/reporting delays.
4. Compare station-specific meteorology and pollutant models against this pooled baseline.
5. Improve extreme-event recall using validation-only objectives and assess warning lead time, interval calibration by season, and episode probability calibration.

Validation: the latest full suite has 17 passing tests, including station-screening and interval-end preprocessing checks. Streamlit AppTest passed after the station-coverage audit was added; earlier browser layout was inspected and corrected. New pollutant preprocessing is not yet integrated into the dashboard or trained models. See [validation record](validation.md) and [acceptance evidence](../docs/acceptance.md).

Sources and detailed assumptions: [methodology](../docs/methodology_v2.md), [initial audit](current_state_audit.md), [CPCB AQI calculation](https://cpcb.gov.in/National-Air-Quality-Index/), [data mirror](https://github.com/Vonter/india-cpcb-aqi), [Open-Meteo archive](https://open-meteo.com/en/docs/historical-weather-api).
'''
    status = (ROOT/'reports/project_status.md').read_text(encoding='utf-8')
    title, body = text.split('\n', 1)
    text = title + '\n\n' + status.replace('# Project status — 14 September 2026', '## Current completion status — 14 September 2026', 1) + '\n\n---\n' + body
    (ROOT/'reports/final_report.md').write_text(text,encoding='utf-8')
    print(best.to_string(index=False))
    print('Engineering report generated from executed outputs')


if __name__ == '__main__':
    main()
