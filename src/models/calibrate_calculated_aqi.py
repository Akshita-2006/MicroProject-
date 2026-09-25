"""Calibrate calculated pollutant AQI to archived official AQI without using 2023 labels in fitting."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

ROOT=Path(__file__).resolve().parents[2]
POLLUTANTS=['PM2.5 (µg/m³)','PM10 (µg/m³)','NO2 (µg/m³)','Ozone (µg/m³)','SO2 (µg/m³)','CO (mg/m³)']

def main():
    calculated=pd.read_parquet(ROOT/'data/processed/delhi_calculated_aqi_hourly_2017_2025.parquet')
    concentration=pd.read_parquet(ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet',columns=['station_name','timestamp']+POLLUTANTS)
    official=pd.read_parquet(ROOT/'data/processed/delhi_hourly_all_eligible.parquet',columns=['station_name','timestamp','aqi'])
    data=calculated.merge(concentration,on=['station_name','timestamp']).merge(official,on=['station_name','timestamp']).dropna(subset=['aqi','calculated_aqi']).reset_index(drop=True)
    data['hour_sin']=np.sin(2*np.pi*data.timestamp.dt.hour/24); data['hour_cos']=np.cos(2*np.pi*data.timestamp.dt.hour/24)
    data['month_sin']=np.sin(2*np.pi*(data.timestamp.dt.month-1)/12); data['month_cos']=np.cos(2*np.pi*(data.timestamp.dt.month-1)/12)
    data=pd.concat([data,pd.get_dummies(data.station_name,prefix='station',dtype='float32')],axis=1)
    features=[c for c in data if c not in ['station_name','timestamp','aqi','dominant_pollutant']]
    train=data.timestamp<'2023-01-01'; test=data.timestamp>='2023-01-01'
    fit=np.flatnonzero(train & data[features].notna().all(axis=1))[::8]
    model=XGBRegressor(n_estimators=350,max_depth=7,learning_rate=.05,subsample=.8,colsample_bytree=.85,objective='reg:squarederror',tree_method='hist',n_jobs=4,random_state=42)
    model.fit(data.loc[fit,features],data.loc[fit,'aqi'])
    ix=np.flatnonzero(test & data[features].notna().all(axis=1)); pred=model.predict(data.loc[ix,features])
    result={'test_period':'2023 only; not used for fitting','n':int(len(ix)),'mae':float(mean_absolute_error(data.loc[ix,'aqi'],pred)),'rmse':float(mean_squared_error(data.loc[ix,'aqi'],pred)**.5),'r2':float(r2_score(data.loc[ix,'aqi'],pred))}
    out=ROOT/'experiments/results/calculated_aqi_calibration'; out.mkdir(parents=True,exist_ok=True)
    (out/'official_overlap_2023.json').write_text(json.dumps(result,indent=2)); joblib.dump({'model':model,'features':features},out/'calibrator.joblib'); print(result)
if __name__=='__main__': main()
