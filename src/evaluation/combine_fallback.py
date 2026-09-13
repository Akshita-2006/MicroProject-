"""Evaluate the combined policy on disjoint complete/incomplete-history cases."""
from pathlib import Path
import json
import pandas as pd
from src.models.run_episode_system import evaluate_outputs,scores
from src.evaluation.issued_episodes import evaluate_windows,summarize

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/results/combined_system'


def main():
    fallback=ROOT/'experiments/results/missing_history_fallback'
    if not (fallback/'complete.json').exists():
        raise ValueError('All fallback models must be complete before combined evaluation')
    OUT.mkdir(parents=True,exist_ok=True)
    for filename in ['test_predictions.parquet','daily_trajectories.parquet']:
        a=pd.read_parquet(ROOT/'experiments/results/v2'/filename).assign(route='complete_history')
        b=pd.read_parquet(fallback/filename).assign(route='missing_history_fallback')
        data=pd.concat([a,b],ignore_index=True)
        if data.duplicated(['station_name','timestamp','horizon']).any():
            raise ValueError('Primary and fallback forecast populations must be disjoint')
        data.sort_values(['station_name','timestamp','horizon']).to_parquet(OUT/filename,index=False)
    points=pd.read_parquet(OUT/'test_predictions.parquet')
    rows=[]
    for h,by_h in points.groupby('horizon'):
        for station,g in list(by_h.groupby('station_name'))+[('ALL',by_h)]:
            rows.append(dict(station=station,horizon=h,fallback_n=int(g.route.eq('missing_history_fallback').sum()),
                             interval_coverage=float(((g.actual>=g.lower)&(g.actual<=g.upper)).mean()),**scores(g.actual,g.prediction)))
    pd.DataFrame(rows).to_csv(OUT/'regression_metrics.csv',index=False)
    evaluate_outputs(OUT)
    trajectories=pd.read_parquet(OUT/'daily_trajectories.parquet')
    windows,matches,excluded=evaluate_windows(trajectories)
    windows.to_csv(OUT/'issued_episode_windows.csv',index=False)
    matches.to_csv(OUT/'issued_episode_matches.csv',index=False)
    excluded.to_csv(OUT/'issued_episode_exclusions.csv',index=False)
    summary=summarize(windows)
    counts=trajectories.groupby('station_name').timestamp.nunique()
    summary['scheduled_windows']=[364*len(counts) if s=='ALL' else 364 for s in summary.station]
    summary['produced_windows']=[int(counts.sum()) if s=='ALL' else int(counts[s]) for s in summary.station]
    summary['abstained_windows']=summary.scheduled_windows-summary.produced_windows
    summary['excluded_produced_windows']=summary.produced_windows-summary.eligible_windows
    summary['evaluated_fraction']=summary.eligible_windows/summary.scheduled_windows
    summary.to_csv(OUT/'issued_episode_metrics.csv',index=False)
    manifest=dict(policy='Keep v2 predictions on complete history; validation-selected native-missing fallback otherwise; abstain without current AQI.',
                  test_previously_inspected=True,primary='v2',fallback='missing_history_fallback')
    (OUT/'complete.json').write_text(json.dumps(manifest,indent=2))
    print(pd.DataFrame(rows).query("station == 'ALL'").to_string(index=False))
    print(summary.query("station == 'ALL'").to_string(index=False))


if __name__=='__main__':
    main()
