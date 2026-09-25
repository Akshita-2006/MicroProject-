"""Chronological multi-pollutant concentration forecasts for the 2017-2025 panel."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet'
OUT = ROOT/'experiments/results/concentrations_2017_2025'
MODELS = ROOT/'experiments/models/concentrations_2017_2025'
TARGETS = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'Ozone (µg/m³)', 'SO2 (µg/m³)', 'CO (mg/m³)', 'Benzene (µg/m³)']
HORIZONS = [1, 6, 12, 24]

def features(data, target):
    frame = data[['station_name', 'timestamp', target]].copy().sort_values(['station_name', 'timestamp'])
    name = target.replace(' (µg/m³)', '').replace(' (mg/m³)', '').replace('.', '').replace(' ', '_')
    for lag in [1,2,3,6,12,24,48,72]: frame[f'{name}_lag_{lag}'] = frame.groupby('station_name')[target].shift(lag)
    frame['hour_sin'] = np.sin(2*np.pi*frame.timestamp.dt.hour/24)
    frame['hour_cos'] = np.cos(2*np.pi*frame.timestamp.dt.hour/24)
    frame['month_sin'] = np.sin(2*np.pi*(frame.timestamp.dt.month-1)/12)
    frame['month_cos'] = np.cos(2*np.pi*(frame.timestamp.dt.month-1)/12)
    return pd.concat([frame, pd.get_dummies(frame.station_name, prefix='station', dtype='float32')], axis=1)

def metrics(y, p):
    return dict(n=int(len(y)), mae=float(mean_absolute_error(y,p)), rmse=float(mean_squared_error(y,p)**.5), r2=float(r2_score(y,p)))

def main():
    OUT.mkdir(parents=True, exist_ok=True); MODELS.mkdir(parents=True, exist_ok=True)
    data = pd.read_parquet(DATA)
    rows=[]
    for target in TARGETS:
        x=features(data,target); feature_cols=[c for c in x if c not in ['station_name','timestamp',target]]
        for horizon in HORIZONS:
            y=x.groupby('station_name')[target].shift(-horizon)
            usable=x[feature_cols].notna().all(axis=1) & y.notna()
            train=usable & (x.timestamp<'2024-01-01')
            validation=usable & (x.timestamp>='2024-01-01') & (x.timestamp<'2025-01-01')
            test=usable & (x.timestamp>='2025-01-01')
            train_ix=np.flatnonzero(train)[::6]
            model=XGBRegressor(n_estimators=180,max_depth=5,learning_rate=.06,subsample=.8,colsample_bytree=.8,
                               objective='reg:squarederror',tree_method='hist',n_jobs=4,random_state=42)
            model.fit(x.loc[train_ix,feature_cols],y.iloc[train_ix])
            for split,mask in [('validation_2024',validation),('test_2025',test)]:
                ix=np.flatnonzero(mask)
                if len(ix): rows.append(dict(pollutant=target,horizon=horizon,split=split,**metrics(y.iloc[ix],model.predict(x.loc[ix,feature_cols]))))
            safe=''.join(c if c.isalnum() else '_' for c in target)
            joblib.dump(dict(model=model,features=feature_cols,pollutant=target,horizon=horizon), MODELS/f'{safe}_h{horizon}.joblib')
            print(f'{target} +{horizon} complete',flush=True)
    pd.DataFrame(rows).to_csv(OUT/'metrics.csv',index=False)
    (OUT/'manifest.json').write_text(json.dumps({'data':str(DATA),'split':'train 2017-2023, validation 2024, test 2025','pollutants':TARGETS,'horizons':HORIZONS},indent=2))

if __name__=='__main__': main()
