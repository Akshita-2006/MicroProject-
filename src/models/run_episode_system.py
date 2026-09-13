"""Corrected pooled Delhi experiments. Selection never reads test scores.

All features are station-local; station indicators permit pooled training.
Calendar splits: train 2017–2021, select Jan–Jun 2022, calibrate Jul–Dec
2022, retrospective test 2023. Legacy prototype already inspected this test era.
"""
from pathlib import Path
import json
import time
import platform
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, confusion_matrix
from xgboost import XGBRegressor
from src.features.hourly import build, split_masks
from src.episode_detection.timeline import evaluate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'experiments/results/v2'
MODELS = ROOT/'experiments/models/v2'
KEY_HORIZONS = [1,6,12,24]
BASE = dict(n_estimators=180,max_depth=4,learning_rate=.06,min_child_weight=5,
            subsample=.8,colsample_bytree=.8,gamma=0,reg_alpha=0,reg_lambda=5)
CANDIDATES = [BASE,
    dict(n_estimators=250,max_depth=6,learning_rate=.04,min_child_weight=10,subsample=.85,colsample_bytree=.9,gamma=.1,reg_alpha=.1,reg_lambda=10),
    dict(n_estimators=140,max_depth=3,learning_rate=.1,min_child_weight=3,subsample=.7,colsample_bytree=.75,gamma=.5,reg_alpha=1,reg_lambda=3)]


def model(kind, params=None):
    if kind == 'random_forest':
        return RandomForestRegressor(n_estimators=60,max_depth=14,min_samples_leaf=8,max_samples=.5,n_jobs=4,random_state=42)
    return XGBRegressor(**(params or BASE),objective='reg:squarederror',tree_method='hist',n_jobs=4,random_state=42)


def scores(y,p):
    return dict(n=len(y),mae=float(mean_absolute_error(y,p)),rmse=float(mean_squared_error(y,p)**.5),r2=float(r2_score(y,p)))


def load():
    panel = pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet').sort_values(['station_name','timestamp']).reset_index(drop=True)
    xs = []
    for _,g in panel.groupby('station_name',sort=True):
        x, groups = build(g)
        xs.append(x)
    x = pd.concat(xs,ignore_index=True)
    indicators = pd.get_dummies(panel.station_name,prefix='station',dtype='float32')
    x = pd.concat([x,indicators],axis=1)
    groups = {k:v+list(indicators) for k,v in groups.items()}
    return panel,x,groups


def predict(est, x, meta, horizon, kind):
    if kind == 'persistence':
        return meta.aqi.to_numpy()
    if kind == 'seasonal_naive':
        # The last observed value at the target's hour of day.
        return meta.seasonal.to_numpy()
    return np.clip(est.predict(x),0,500)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    MODELS.mkdir(parents=True,exist_ok=True)
    panel,x,groups = load()
    valid_x = x.notna().all(axis=1)
    tuning, comparisons, selected, predictions = [],[],{},[]
    importances = []
    for h in KEY_HORIZONS:
        print(f'Horizon {h}: time-aware tuning and ablation',flush=True)
        y = panel.groupby('station_name').aqi.shift(-h)
        seasonal = panel.groupby('station_name').aqi.shift(24-h) if h < 24 else panel.aqi
        usable = valid_x & y.notna() & seasonal.notna()
        masks = {k:v & usable for k,v in split_masks(panel.timestamp,h).items()}
        # Two expanding, purged development folds; deterministic sample limits HPO cost.
        candidate_errors = []
        for ci,params in enumerate(CANDIDATES):
            errors = []
            for year in [2020,2021]:
                start,end = pd.Timestamp(year,1,1),pd.Timestamp(year+1,1,1)
                fit = usable & ((panel.timestamp+pd.Timedelta(hours=h)) < start)
                val = usable & (panel.timestamp >= start) & ((panel.timestamp+pd.Timedelta(hours=h)) < end)
                ix = np.flatnonzero(fit)[::4]
                vx = np.flatnonzero(val)[::4]
                est = model('xgboost',params).fit(x.iloc[ix],y.iloc[ix])
                m = scores(y.iloc[vx],np.clip(est.predict(x.iloc[vx]),0,500))
                errors.append(m['mae'])
                tuning.append(dict(horizon=h,candidate=ci,fold_year=year,training_n=len(ix),parameters=json.dumps(params),**m))
            candidate_errors.append(np.mean(errors))
        params = CANDIDATES[int(np.argmin(candidate_errors))]
        configs = [('persistence','A_history',None),('seasonal_naive','A_history',None)]
        configs += [('xgboost',g,BASE) for g in groups]
        configs += [('xgboost_tuned','E_full',params),('random_forest','E_full',None)]
        candidates = []
        for kind,group,par in configs:
            cols = groups[group]
            est = None if kind in ['persistence','seasonal_naive'] else model(kind,par).fit(x.loc[masks['train'],cols],y[masks['train']])
            meta = panel.loc[masks['validation']].assign(seasonal=seasonal[masks['validation']])
            p = predict(est,x.loc[masks['validation'],cols],meta,h,kind)
            m = scores(y[masks['validation']],p)
            comparisons.append(dict(horizon=h,model=kind,feature_group=group,split='validation',station='ALL',**m))
            candidates.append((m['mae'],kind,group,par,est))
            print(f'  {kind}/{group}: validation MAE {m["mae"]:.2f}',flush=True)
        best = min(candidates,key=lambda c:c[0])
        _,kind,group,par,est = best
        selected[str(h)] = dict(model=kind,feature_group=group,parameters=par,validation_mae=best[0],features=groups[group])
        # Freeze selection on disk BEFORE producing any test metrics.
        (OUT/'selection.json').write_text(json.dumps(selected,indent=2))
        joblib.dump(est,MODELS/f'h{h}.joblib')
        cols = groups[group]
        calmeta = panel.loc[masks['calibration']].assign(seasonal=seasonal[masks['calibration']])
        cp = predict(est,x.loc[masks['calibration'],cols],calmeta,h,kind)
        residuals = np.abs(y[masks['calibration']].to_numpy()-cp)
        quantile = min(1,np.ceil((len(residuals)+1)*.9)/len(residuals))
        radius = float(np.quantile(residuals,quantile,method='higher'))
        selected[str(h)]['interval_radius_90'] = radius
        for _,ck,cg,cpar,ce in candidates:
            meta = panel.loc[masks['test']].assign(seasonal=seasonal[masks['test']])
            pp = predict(ce,x.loc[masks['test'],groups[cg]],meta,h,ck)
            # Test comparisons are descriptive only; the selected entry is already frozen.
            comparisons.append(dict(horizon=h,model=ck,feature_group=cg,split='test',station='ALL',**scores(y[masks['test']],pp)))
        testmeta = panel.loc[masks['test'],['timestamp','station_name','aqi']].assign(seasonal=seasonal[masks['test']])
        pp = predict(est,x.loc[masks['test'],cols],testmeta,h,kind)
        result = testmeta.drop(columns='seasonal').copy()
        result['target_time'] = result.timestamp+pd.Timedelta(hours=h)
        result['horizon'] = h
        result['actual'] = y[masks['test']].to_numpy()
        result['prediction'] = pp
        result['lower'] = np.maximum(0,pp-radius)
        result['upper'] = np.minimum(500,pp+radius)
        predictions.append(result)
        for station,g in result.groupby('station_name'):
            comparisons.append(dict(horizon=h,model=kind,feature_group=group,split='test_selected',station=station,
                                    interval_coverage=float(((g.actual >= g.lower)&(g.actual <= g.upper)).mean()),**scores(g.actual,g.prediction)))
        if est is not None and hasattr(est,'feature_importances_'):
            importances += [dict(horizon=h,feature=c,importance=float(v)) for c,v in zip(cols,est.feature_importances_)]
        pd.DataFrame(comparisons).to_csv(OUT/'model_comparison.csv',index=False)
        pd.DataFrame(tuning).to_csv(OUT/'tuning.csv',index=False)
        pd.DataFrame(importances).to_csv(OUT/'feature_importance.csv',index=False)
        pd.concat(predictions).to_parquet(OUT/'test_predictions.parquet',index=False)
        (OUT/'selection.json').write_text(json.dumps(selected,indent=2))
    # Forecast EVERY future hour. Intermediate horizons inherit nearest key-horizon
    # configuration selected on validation; no interpolation, no future weather.
    print('Training direct hourly trajectory models',flush=True)
    trajectory = []
    for h in range(1,25):
        anchor = min(KEY_HORIZONS,key=lambda a:abs(a-h))
        cfg = selected[str(anchor)]
        cols = cfg['features']
        y = panel.groupby('station_name').aqi.shift(-h)
        usable = valid_x & y.notna()
        masks = {k:v & usable for k,v in split_masks(panel.timestamp,h).items()}
        if h in KEY_HORIZONS:
            est = joblib.load(MODELS/f'h{h}.joblib')
        elif cfg['model'] in ['persistence','seasonal_naive']:
            est = None
        else:
            est = model(cfg['model'],cfg['parameters']).fit(x.loc[masks['train'],cols],y[masks['train']])
        joblib.dump(est,MODELS/f'h{h}.joblib')
        cfg = dict(cfg,anchor_horizon=anchor)
        # Each hour's interval is separately calibrated, including intermediate hours.
        seasonal = panel.groupby('station_name').aqi.shift(24-h) if h < 24 else panel.aqi
        cm = masks['calibration'] & seasonal.notna()
        cp = predict(est,x.loc[cm,cols],panel.loc[cm].assign(seasonal=seasonal[cm]),h,cfg['model'])
        residual = np.abs(y[cm].to_numpy()-cp)
        cfg['interval_radius_90'] = float(np.quantile(residual,min(1,np.ceil((len(residual)+1)*.9)/len(residual)),method='higher'))
        selected[str(h)] = cfg
        # Nonoverlapping daily-issued 24h windows keep event evaluation interpretable.
        tm = (panel.timestamp >= '2023-01-01') & (panel.timestamp < '2023-12-31') & panel.timestamp.dt.hour.eq(0) & valid_x & seasonal.notna()
        p = predict(est,x.loc[tm,cols],panel.loc[tm].assign(seasonal=seasonal[tm]),h,cfg['model'])
        g = panel.loc[tm,['timestamp','station_name','aqi']].copy()
        g['horizon'],g['target_time'],g['prediction'],g['actual'] = h,g.timestamp+pd.Timedelta(hours=h),p,y[tm].to_numpy()
        g['lower'],g['upper'] = np.maximum(0,p-cfg['interval_radius_90']),np.minimum(500,p+cfg['interval_radius_90'])
        trajectory.append(g)
        print(f'  hourly model +{h} saved',flush=True)
    (OUT/'selection.json').write_text(json.dumps(selected,indent=2))
    pd.concat(trajectory).to_parquet(OUT/'daily_trajectories.parquet',index=False)
    evaluate_outputs()
    (OUT/'run_manifest.json').write_text(json.dumps({'python':platform.python_version(),'completed_at_unix':time.time(),
        'seed':42,'hpo_stride':4,'rf_parameters':model('random_forest').get_params(),'test_previously_inspected':True},indent=2))


def evaluate_outputs(results_dir=OUT):
    OUT = Path(results_dir)
    points = pd.read_parquet(OUT/'test_predictions.parquet')
    rows,matches = [],[]
    for (station,h),g in points.groupby(['station_name','horizon']):
        a = g.set_index('target_time').actual
        p = g.set_index('target_time').prediction
        for persistence in [2,3,6]:
            m, pairs = evaluate(a,p,persistence)
            rows.append(dict(station=station,horizon=h,persistence=persistence,**m))
            matches += [dict(station=station,horizon=h,persistence=persistence,**pair) for pair in pairs]
    pd.DataFrame(rows).to_csv(OUT/'event_metrics.csv',index=False)
    pd.DataFrame(matches).to_csv(OUT/'event_matches.csv',index=False)
    warning_rows = []
    from src.episode_detection.timeline import extract
    trajectories = pd.read_parquet(OUT/'daily_trajectories.parquet')
    for station,g in trajectories.groupby('station_name'):
        truth,pred = [],[]
        for issued,w in g.groupby('timestamp'):
            w = w.sort_values('target_time')
            if len(w) != 24 or w.actual.isna().any():
                continue
            truth.append(bool(extract(w.set_index('target_time').actual)))
            pred.append(bool(extract(w.set_index('target_time').prediction)))
        tn,fp,fn,tp = confusion_matrix(truth,pred,labels=[False,True]).ravel()
        warning_rows.append(dict(station=station,eligible_windows=len(truth),true_negative=tn,false_positive=fp,false_negative=fn,true_positive=tp,
                                 precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn) if tp+fn else 0,
                                 f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0))
    pd.DataFrame(warning_rows).to_csv(OUT/'warning_metrics.csv',index=False)
    print('Saved regression, event, timing and daily warning evaluations',flush=True)


if __name__ == '__main__':
    main()
