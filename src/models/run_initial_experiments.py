"""Run initial leakage-safe multi-horizon AQI forecasting experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


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

    for window in ROLL_WINDOWS:
        shifted = df["aqi"].shift(1)
        df[f"aqi_roll_mean_{window}"] = shifted.rolling(window).mean()
        df[f"aqi_roll_max_{window}"] = shifted.rolling(window).max()
        df[f"aqi_roll_std_{window}"] = shifted.rolling(window).std()

    wind_radians = np.deg2rad(df["wind_direction_10m"])
    df["wind_dir_sin"] = np.sin(wind_radians)
    df["wind_dir_cos"] = np.cos(wind_radians)
    return df


def split_chronologically(df: pd.DataFrame):
    train_end = int(len(df) * 0.70)
    valid_end = int(len(df) * 0.85)
    return df.iloc[:train_end], df.iloc[train_end:valid_end], df.iloc[valid_end:]


def evaluate(y_true, y_pred) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }


def fit_models(X_train, y_train):
    return {
        "random_forest": RandomForestRegressor(
            n_estimators=120,
            max_depth=18,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ).fit(X_train, y_train),
        "xgboost": XGBRegressor(
            n_estimators=350,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        ).fit(X_train, y_train),
    }


def run(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["timestamp"])
    df = add_features(df)
    feature_columns = [
        col
        for col in df.columns
        if col.startswith("aqi_lag_")
        or col.startswith("aqi_roll_")
        or col in WEATHER_COLUMNS
        or col in ["hour_sin", "hour_cos", "month_sin", "month_cos", "dayofweek", "wind_dir_sin", "wind_dir_cos"]
    ]

    rows = []
    for horizon in HORIZONS:
        horizon_df = df.copy()
        horizon_df["target"] = horizon_df["aqi"].shift(-horizon)
        model_df = horizon_df.dropna(subset=feature_columns + ["target", "aqi_lag_1"]).copy()
        train, valid, test = split_chronologically(model_df)

        y_valid = valid["target"]
        y_test = test["target"]
        persistence_valid = valid["aqi_lag_1"]
        persistence_test = test["aqi_lag_1"]

        for split_name, actual, pred in [
            ("validation", y_valid, persistence_valid),
            ("test", y_test, persistence_test),
        ]:
            metrics = evaluate(actual, pred)
            rows.append({"model": "persistence", "horizon": horizon, "split": split_name, **metrics})

        X_train = train[feature_columns]
        y_train = train["target"]
        models = fit_models(X_train, y_train)

        for model_name, model in models.items():
            for split_name, split_df in [("validation", valid), ("test", test)]:
                pred = model.predict(split_df[feature_columns])
                metrics = evaluate(split_df["target"], pred)
                rows.append({"model": model_name, "horizon": horizon, "split": split_name, **metrics})

    results = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/shadipur_aqi_weather_hourly.csv")
    parser.add_argument("--output", default="experiments/results/initial_forecast_results.csv")
    args = parser.parse_args()
    results = run(Path(args.input), Path(args.output))
    print(results.to_string(index=False))
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
