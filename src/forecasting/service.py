"""Saved-model inference using only station history through issuance."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from src.features.hourly import build
from src.episode_detection.timeline import extract, category

ROOT = Path(__file__).resolve().parents[2]


def forecast(history, issued, artifacts=None):
    root = Path(artifacts) if artifacts else ROOT
    selected = json.loads((root/'experiments/results/v2/selection.json').read_text())
    history = history[history.timestamp <= issued].sort_values('timestamp').tail(73)
    if len(history) < 73 or history.timestamp.iloc[-1] != issued:
        raise ValueError('73 consecutive hours ending at issuance are required')
    x,_ = build(history)
    row = x.tail(1).copy()
    if not np.isfinite(history.aqi.iloc[-1]):
        raise ValueError('Current AQI is missing; forecast unavailable')
    missing_history = row.isna().any(axis=None)
    fallback = None
    if missing_history and (root/'experiments/results/combined_system/complete.json').exists():
        fallback = json.loads((root/'experiments/results/missing_history_fallback/selection.json').read_text())
        row = pd.concat([row,row.isna().astype('float32').add_prefix('missing_')],axis=1)
    station = history.station_name.iloc[-1]
    station_features = [c for c in selected['1']['features'] if c.startswith('station_')]
    if 'station_'+station not in station_features:
        raise ValueError('Station is not represented in the trained model')
    records = []
    for h in range(1,25):
        cfg = fallback[str(h)] if fallback is not None else selected[str(h)]
        for feature in cfg['features']:
            if feature.startswith('station_'):
                row[feature] = float(feature == 'station_'+station)
        if fallback is None and row[cfg['features']].isna().any(axis=None):
            raise ValueError('Required observations are missing; forecast unavailable')
        kind = 'xgboost_missing_fallback' if fallback is not None else cfg['model']
        if kind == 'persistence':
            p = history.aqi.iloc[-1]
        elif kind == 'seasonal_naive':
            p = history.aqi.iloc[-1-(24-h)]
        else:
            folder = 'missing_history_fallback' if fallback is not None else 'v2'
            est = joblib.load(root/f'experiments/models/{folder}/h{h}.joblib')
            p = float(est.predict(row[cfg['features']])[0])
        p = float(np.clip(p,0,500))
        radius = cfg['interval_radius_90']
        records.append(dict(horizon=h,target_time=issued+pd.Timedelta(hours=h),prediction=p,
                            lower=max(0,p-radius),upper=min(500,p+radius),category=category(p),model=kind,
                            route='missing_history_fallback' if fallback is not None else 'complete_history'))
    return pd.DataFrame(records)


def warning(trajectory, current_aqi):
    events = extract(trajectory.set_index('target_time').prediction)
    if events:
        risk = 'SEVERE RISK' if max(e.peak_aqi for e in events) >= 401 else 'HIGH RISK'
    elif trajectory.prediction.max() >= 201:
        risk = 'MODERATE RISK'
    else:
        risk = 'LOW RISK'
    return dict(risk=risk,current_category=category(current_aqi),episodes=events)
