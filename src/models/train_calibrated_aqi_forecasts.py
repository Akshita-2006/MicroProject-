"""Chronological calibrated-AQI forecasts; 2025 is never used for fitting or selection."""
from pathlib import Path
import json, joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

ROOT=Path(__file__).resolve().parents[2]
POLLUTANTS=['PM2.5 (µg/m³)','PM10 (µg/m³)','NO2 (µg/m³)','Ozone (µg/m³)','SO2 (µg/m³)','CO (mg/m³)']
HORIZONS=[1,6,12,24]

def metric(y,p): return {'n':int(len(y)),'mae':float(mean_absolute_error(y,p)),'rmse':float(mean_squared_error(y,p)**.5),'r2':float(r2_score(y,p))}

def main():
    calculated=pd.read_parquet(ROOT/'data/processed/delhi_calculated_aqi_hourly_2017_2025.parquet')
    pollutants=pd.read_parquet(ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet',columns=['station_name','timestamp']+POLLUTANTS)
    data=calculated.merge(pollutants,on=['station_name','timestamp']).sort_values(['station_name','timestamp']).reset_index(drop=True)
    saved=joblib.load(ROOT/'experiments/results/calculated_aqi_calibration/calibrator.joblib')
    data['hour_sin']=np.sin(2*np.pi*data.timestamp.dt.hour/24); data['hour_cos']=np.cos(2*np.pi*data.timestamp.dt.hour/24)
    data['month_sin']=np.sin(2*np.pi*(data.timestamp.dt.month-1)/12); data['month_cos']=np.cos(2*np.pi*(data.timestamp.dt.month-1)/12)
    data=pd.concat([data,pd.get_dummies(data.station_name,prefix='station',dtype='float32')],axis=1)
    for c in saved['features']:
        if c not in data: data[c]=0.
    usable=data[saved['features']].notna().all(axis=1)
    data['calibrated_aqi']=np.nan; data.loc[usable,'calibrated_aqi']=np.clip(saved['model'].predict(data.loc[usable,saved['features']]),0,500)
    for lag in [1,2,3,6,12,24,48,72]: data[f'aqi_lag_{lag}']=data.groupby('station_name').calibrated_aqi.shift(lag)
    features=['calibrated_aqi']+[f'aqi_lag_{x}' for x in [1,2,3,6,12,24,48,72]]+POLLUTANTS+['hour_sin','hour_cos','month_sin','month_cos']+[c for c in data if c.startswith('station_') and c!='station_name']
    out=ROOT/'experiments/results/calibrated_aqi_forecast'; models=ROOT/'experiments/models/calibrated_aqi_forecast'; out.mkdir(parents=True,exist_ok=True); models.mkdir(parents=True,exist_ok=True)
    rows=[]
    for h in HORIZONS:
        y=data.groupby('station_name').calibrated_aqi.shift(-h)
        base=data[features].notna().all(axis=1)&y.notna()
        train=base&(data.timestamp<'2024-01-01'); validation=base&(data.timestamp>='2024-01-01')&(data.timestamp<'2025-01-01'); test=base&(data.timestamp>='2025-01-01')
        fit=np.flatnonzero(train)[::8]
        model=XGBRegressor(n_estimators=300,max_depth=6,learning_rate=.05,subsample=.8,colsample_bytree=.85,objective='reg:squarederror',tree_method='hist',n_jobs=4,random_state=42)
        model.fit(data.loc[fit,features],y.iloc[fit])
        for name,mask in [('validation_2024',validation),('test_2025',test)]:
            ix=np.flatnonzero(mask); rows.append({'horizon':h,'split':name,**metric(y.iloc[ix],model.predict(data.loc[ix,features]))})
        joblib.dump({'model':model,'features':features,'horizon':h},models/f'h{h}.joblib'); print('completed',h,flush=True)
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    (out/'manifest.json').write_text(json.dumps({'target':'calibrated AQI','train':'2017-2023','validation':'2024','test':'2025','calibration':'fit through 2022; official overlap tested on 2023'},indent=2))
if __name__=='__main__': main()
