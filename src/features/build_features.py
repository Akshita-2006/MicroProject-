"""Shared leakage-safe feature engineering for hourly AQI forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd


HORIZONS = [1, 6, 12, 24]
LAGS = [1, 2, 3, 6, 12, 24, 48, 72]
ROLL_WINDOWS = [3, 6, 12, 24]
WEATHER_COLUMNS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "pressure_msl",
    "precipitation",
]
TIME_COLUMNS = [
    "dayofweek",
    "hour_sin",
    "hour_cos",
    "month_sin",
    "month_cos",
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp").copy()
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    for lag in LAGS:
        df[f"aqi_lag_{lag}"] = df["aqi"].shift(lag)

    shifted = df["aqi"].shift(1)
    for window in ROLL_WINDOWS:
        df[f"aqi_roll_mean_{window}"] = shifted.rolling(window).mean()
        df[f"aqi_roll_max_{window}"] = shifted.rolling(window).max()
        df[f"aqi_roll_std_{window}"] = shifted.rolling(window).std()

    wind_radians = np.deg2rad(df["wind_direction_10m"])
    df["wind_dir_sin"] = np.sin(wind_radians)
    df["wind_dir_cos"] = np.cos(wind_radians)
    return df


def feature_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    lag_cols = [col for col in df.columns if col.startswith("aqi_lag_")]
    rolling_cols = [col for col in df.columns if col.startswith("aqi_roll_")]
    weather_cols = WEATHER_COLUMNS + ["wind_dir_sin", "wind_dir_cos"]
    weather_cols = [col for col in weather_cols if col in df.columns]

    return {
        "pollutant_lags": lag_cols,
        "lags_time": lag_cols + TIME_COLUMNS,
        "lags_time_weather": lag_cols + TIME_COLUMNS + weather_cols,
        "full_engineered": lag_cols + rolling_cols + TIME_COLUMNS + weather_cols,
    }


def add_target(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    out = df.copy()
    out["target"] = out["aqi"].shift(-horizon)
    return out


def split_chronologically(df: pd.DataFrame):
    train_end = int(len(df) * 0.70)
    valid_end = int(len(df) * 0.85)
    return df.iloc[:train_end], df.iloc[train_end:valid_end], df.iloc[valid_end:]
