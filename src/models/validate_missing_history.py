"""Validation-only missing-history experiment; no test predictions or selection."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from src.models.run_episode_system import load,model,BASE,scores
from src.features.hourly import split_masks

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/results/missing_history_validation'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    panel,x,groups=load()
    complete=x.notna().all(axis=1)
    station_features=[c for c in x if c.startswith('station_')]
    missing=x.drop(columns=station_features).isna().astype('float32').add_prefix('missing_')
    augmented=pd.concat([x,missing],axis=1)
    results=[]
    for h in [1,6,12,24]:
        y=panel.groupby('station_name').aqi.shift(-h)
        eligible=panel.aqi.notna() & y.notna()
        masks={k:v & eligible for k,v in split_masks(panel.timestamp,h).items() if k in ['train','validation']}
        current=panel.loc[masks['validation'],'aqi']
        print('Horizon',h,'train',int(masks['train'].sum()),'validation',int(masks['validation'].sum()),flush=True)
        for variant,features,fit_mask in [('complete_history',x,masks['train'] & complete),
                                           ('native_missing',x,masks['train']),
                                           ('native_missing_flags',augmented,masks['train'])]:
            est=model('xgboost',BASE).fit(features.loc[fit_mask],y[fit_mask])
            for subset,mask in [('complete',masks['validation'] & complete),('incomplete',masks['validation'] & ~complete),('all',masks['validation'])]:
                if variant=='complete_history' and subset!='complete':
                    continue
                prediction=np.clip(est.predict(features.loc[mask]),0,500)
                results.append(dict(horizon=h,variant=variant,subset=subset,training_n=int(fit_mask.sum()),
                                    persistence_mae=float((y[mask]-panel.loc[mask,'aqi']).abs().mean()),**scores(y[mask],prediction)))
            print(' ',variant,'fit completed',flush=True)
        pd.DataFrame(results).to_csv(OUT/'validation_results.csv',index=False)
    (OUT/'protocol.json').write_text(json.dumps(dict(
        training='2017-2021, purged by target timestamp',validation='2022-01-01 through 2022-06-30, purged',
        test_scored=False,target_imputation=False,current_aqi_required=True,parameters=BASE,
        decision='Evidence for a subsequent deployment decision; existing system unchanged'),indent=2))
    print(pd.DataFrame(results).to_string(index=False),flush=True)


if __name__=='__main__':
    main()
