"""Single-station, regular-hour features available after observation at issue time."""
import numpy as np
import pandas as pd

LAGS = [1, 2, 3, 6, 12, 24, 48, 72]
WINDOWS = [3, 6, 12, 24, 48, 72]
WEATHER = ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'pressure_msl', 'precipitation']


def build(frame):
    df = frame.sort_values('timestamp').copy().reset_index(drop=True)
    if 'station_name' in df and df.station_name.nunique() != 1:
        raise ValueError('Build features separately for each station')
    if not df.timestamp.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError('Input must have a unique continuous hourly grid')
    x = {'aqi':df.aqi}
    for lag in LAGS:
        x[f'aqi_lag_{lag}'] = df.aqi.shift(lag)
    history = list(x)
    t = df.timestamp.dt
    for name, value, period in [('hour',t.hour,24), ('weekday',t.dayofweek,7), ('month',t.month-1,12)]:
        x[f'{name}_sin'] = np.sin(2*np.pi*value/period)
        x[f'{name}_cos'] = np.cos(2*np.pi*value/period)
    x['weekend'] = (t.dayofweek >= 5).astype(float)
    temporal = list(x)[len(history):]
    for col in WEATHER:
        x[col] = df[col]
    x['wind_sin'] = np.sin(np.deg2rad(df.wind_direction_10m))
    x['wind_cos'] = np.cos(np.deg2rad(df.wind_direction_10m))
    weather = list(x)[len(history)+len(temporal):]
    for window in WINDOWS:
        roll = df.aqi.rolling(window, min_periods=window)
        for stat in ['mean','max','min','std']:
            x[f'aqi_{stat}_{window}'] = getattr(roll,stat)()
        x[f'aqi_trend_{window}'] = (df.aqi-df.aqi.shift(window-1))/(window-1)
        x[f'exceedance_count_{window}'] = df.aqi.ge(301).astype(float).where(df.aqi.notna()).rolling(window).sum()
    for col in WEATHER:
        for lag in [1,6,24]:
            x[f'{col}_lag_{lag}'] = df[col].shift(lag)
        x[f'{col}_mean_24'] = df[col].rolling(24).mean()
    features = pd.DataFrame(x, index=df.index).astype('float32')
    groups = {'A_history':history, 'B_history_time':history+temporal,
              'C_history_weather':history+weather, 'D_history_time_weather':history+temporal+weather,
              'E_full':list(features)}
    return features, groups


def split_masks(timestamps, horizon):
    target_time = timestamps + pd.Timedelta(hours=horizon)
    return {
        'train':target_time < pd.Timestamp('2022-01-01'),
        'validation':(timestamps >= '2022-01-01') & (target_time < '2022-07-01'),
        'calibration':(timestamps >= '2022-07-01') & (target_time < '2023-01-01'),
        'test':(timestamps >= '2023-01-01') & (target_time < '2024-01-01'),
    }
