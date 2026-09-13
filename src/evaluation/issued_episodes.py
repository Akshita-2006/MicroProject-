"""Evaluate same-origin 24h episode trajectories, without joining issue windows."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.episode_detection.timeline import evaluate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'experiments/results/v2'
ERRORS = ['onset_error_hours','peak_error_hours','duration_error_hours','recovery_error_hours']


def evaluate_windows(trajectories):
    windows, matches, exclusions = [], [], []
    for (station, issued), g in trajectories.groupby(['station_name','timestamp']):
        g = g.sort_values('target_time')
        expected = pd.date_range(issued+pd.Timedelta(hours=1), periods=24, freq='h')
        if len(g) != 24 or not pd.DatetimeIndex(g.target_time).equals(expected):
            exclusions.append(dict(station=station,issued=issued,reason='incomplete_or_irregular_forecast'))
            continue
        if g[['actual','prediction']].isna().any(axis=None):
            exclusions.append(dict(station=station,issued=issued,reason='missing_truth_or_prediction'))
            continue
        m, pairs = evaluate(g.set_index('target_time').actual,g.set_index('target_time').prediction)
        windows.append(dict(station=station,issued=issued,**m))
        for pair in pairs:
            # Only uncensored onsets can support an onset lead-time statement.
            valid_onset = np.isfinite(pair['onset_error_hours'])
            matches.append(dict(station=station,issued=issued,**pair,
                                actual_onset_lead_hours=(pair['actual_onset']-issued).total_seconds()/3600 if valid_onset else np.nan,
                                predicted_onset_lead_hours=(pair['predicted_onset']-issued).total_seconds()/3600 if valid_onset else np.nan))
    return pd.DataFrame(windows), pd.DataFrame(matches), pd.DataFrame(exclusions,columns=['station','issued','reason'])


def summarize(windows):
    rows=[]
    groups=list(windows.groupby('station'))+[('ALL',windows)]
    for station,g in groups:
        tp,actual,predicted=(int(g[c].sum()) for c in ['matched_events','actual_events','predicted_events'])
        row=dict(station=station,eligible_windows=len(g),actual_episode_segments=actual,predicted_episode_segments=predicted,
                 matched_segments=tp,precision=tp/predicted if predicted else 0,recall=tp/actual if actual else 0,
                 f1=2*tp/(predicted+actual) if predicted+actual else 0)
        for col in ERRORS:
            n=int(g[col+'_n'].sum())
            row[col]=(g[col].fillna(0)*g[col+'_n']).sum()/n if n else np.nan
            row[col+'_n']=n
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    source=pd.read_parquet(OUT/'daily_trajectories.parquet')
    windows,matches,excluded=evaluate_windows(source)
    windows.to_csv(OUT/'issued_episode_windows.csv',index=False)
    matches.to_csv(OUT/'issued_episode_matches.csv',index=False)
    excluded.to_csv(OUT/'issued_episode_exclusions.csv',index=False)
    summary=summarize(windows)
    # The backtest issued at midnight Jan 1–Dec 30 (364 days) for every selected
    # station. An absent trajectory is an abstention, not an eligible negative.
    expected_per_station = len(pd.date_range('2023-01-01','2023-12-30',freq='D'))
    station_counts=source.groupby('station_name').timestamp.nunique()
    summary['scheduled_windows']=[expected_per_station*len(station_counts) if s=='ALL' else expected_per_station for s in summary.station]
    summary['produced_windows']=[int(station_counts.sum()) if s=='ALL' else int(station_counts[s]) for s in summary.station]
    summary['abstained_windows']=summary.scheduled_windows-summary.produced_windows
    summary['excluded_produced_windows']=summary.produced_windows-summary.eligible_windows
    summary['evaluated_fraction']=summary.eligible_windows/summary.scheduled_windows
    summary.to_csv(OUT/'issued_episode_metrics.csv',index=False)
    print(summary[summary.station == 'ALL'].to_string(index=False))
    print('Excluded windows:',len(excluded))


if __name__ == '__main__':
    main()
