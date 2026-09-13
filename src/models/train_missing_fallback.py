"""Fit a validation-selected missing-history fallback, preserving complete-case models."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from src.models.run_episode_system import load,model,BASE,scores,KEY_HORIZONS
from src.features.hourly import split_masks

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/results/missing_history_fallback'
MODELS=ROOT/'experiments/models/missing_history_fallback'


def main():
    validation=pd.read_csv(ROOT/'experiments/results/missing_history_validation/validation_results.csv')
    choices={}
    for h in KEY_HORIZONS:
        rows=validation[(validation.horizon==h)&(validation.subset=='incomplete')]
        if len(rows)!=2:
            raise ValueError('Both validation-only candidates must finish at each horizon')
        best=rows.loc[rows.mae.idxmin()]
        if best.mae >= best.persistence_mae:
            raise ValueError('Missing-history ML does not beat persistence on validation')
        choices[str(h)]=dict(variant=best.variant,validation_incomplete_mae=float(best.mae),parameters=BASE)
    OUT.mkdir(parents=True,exist_ok=True)
    MODELS.mkdir(parents=True,exist_ok=True)
    # Freeze fallback choice before any calibration/test evaluation.
    (OUT/'selection.json').write_text(json.dumps(choices,indent=2))
    panel,x,_=load()
    complete=x.notna().all(axis=1)
    station_cols=[c for c in x if c.startswith('station_')]
    flagged=pd.concat([x,x.drop(columns=station_cols).isna().astype('float32').add_prefix('missing_')],axis=1)
    rows,predictions,trajectories=[],[],[]
    for h in range(1,25):
        anchor=min(KEY_HORIZONS,key=lambda a:abs(a-h))
        cfg=dict(choices[str(anchor)])
        features=flagged if cfg['variant']=='native_missing_flags' else x
        y=panel.groupby('station_name').aqi.shift(-h)
        eligible=panel.aqi.notna() & y.notna()
        masks={k:v & eligible for k,v in split_masks(panel.timestamp,h).items()}
        est=model('xgboost',BASE).fit(features.loc[masks['train']],y[masks['train']])
        joblib.dump(est,MODELS/f'h{h}.joblib')
        # Calibrate specifically on missing-history cases, the fallback's population.
        cm=masks['calibration'] & ~complete
        cp=np.clip(est.predict(features.loc[cm]),0,500)
        residual=np.abs(y[cm].to_numpy()-cp)
        radius=float(np.quantile(residual,min(1,np.ceil((len(residual)+1)*.9)/len(residual)),method='higher'))
        cfg.update(features=list(features),interval_radius_90=radius,calibration_n=len(residual),anchor_horizon=anchor)
        choices[str(h)]=cfg
        daily=(panel.timestamp >= '2023-01-01') & (panel.timestamp < '2023-12-31') & panel.timestamp.dt.hour.eq(0) & panel.aqi.notna() & ~complete
        dp=np.clip(est.predict(features.loc[daily]),0,500)
        dg=panel.loc[daily,['timestamp','station_name','aqi']].copy()
        dg['horizon'],dg['target_time'],dg['actual'],dg['prediction']=h,dg.timestamp+pd.Timedelta(hours=h),y[daily].to_numpy(),dp
        dg['lower'],dg['upper']=np.maximum(0,dp-radius),np.minimum(500,dp+radius)
        trajectories.append(dg)
        if h in KEY_HORIZONS:
            tm=masks['test'] & ~complete
            pp=np.clip(est.predict(features.loc[tm]),0,500)
            g=panel.loc[tm,['timestamp','station_name','aqi']].copy()
            g['horizon'],g['target_time'],g['actual'],g['prediction']=h,g.timestamp+pd.Timedelta(hours=h),y[tm].to_numpy(),pp
            g['lower'],g['upper']=np.maximum(0,pp-radius),np.minimum(500,pp+radius)
            predictions.append(g)
            rows.append(dict(horizon=h,variant=cfg['variant'],population='incomplete_history',
                             coverage=float(((g.actual>=g.lower)&(g.actual<=g.upper)).mean()),**scores(g.actual,g.prediction)))
            pd.DataFrame(rows).to_csv(OUT/'test_results.csv',index=False)
            pd.concat(predictions).to_parquet(OUT/'test_predictions.parquet',index=False)
        (OUT/'selection.json').write_text(json.dumps(choices,indent=2))
        print(f'Fallback +{h} saved',flush=True)
    pd.concat(trajectories).to_parquet(OUT/'daily_trajectories.parquet',index=False)
    (OUT/'complete.json').write_text(json.dumps(dict(hourly_models=24,policy='Fallback only when complete-history features are unavailable; current AQI required.',test_previously_inspected=True),indent=2))


if __name__=='__main__':
    main()
