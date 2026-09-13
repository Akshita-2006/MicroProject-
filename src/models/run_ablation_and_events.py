"""Run feature ablation, tuned XGBoost, and event-warning evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from xgboost import XGBRegressor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.build_features import HORIZONS, add_features, add_target, feature_groups, split_chronologically


EVENT_THRESHOLD = 301


def evaluate_regression(y_true, y_pred) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate_events(y_true, y_pred) -> dict[str, float]:
    actual = y_true >= EVENT_THRESHOLD
    predicted = y_pred >= EVENT_THRESHOLD
    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[False, True]).ravel()
    return {
        "precision": float(precision_score(actual, predicted, zero_division=0)),
        "recall": float(recall_score(actual, predicted, zero_division=0)),
        "f1": float(f1_score(actual, predicted, zero_division=0)),
        "actual_event_rate": float(actual.mean()),
        "predicted_event_rate": float(predicted.mean()),
        "true_positive": int(tp),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_negative": int(tn),
    }


def xgb_model(max_depth=4, learning_rate=0.05, n_estimators=350):
    return XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )


def rf_model():
    return RandomForestRegressor(
        n_estimators=120,
        max_depth=18,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )


def run(input_path: Path, results_dir: Path) -> None:
    df = add_features(pd.read_csv(input_path, parse_dates=["timestamp"]))
    groups = feature_groups(df)
    regression_rows = []
    event_rows = []
    tuning_rows = []
    predictions = []

    for horizon in HORIZONS:
        horizon_df = add_target(df, horizon)

        for group_name, columns in groups.items():
            model_df = horizon_df.dropna(subset=columns + ["target", "aqi_lag_1"]).copy()
            train, valid, test = split_chronologically(model_df)

            models = {
                "persistence": None,
                "random_forest": rf_model(),
                "xgboost_default_tuned": xgb_model(),
            }

            for model_name, model in models.items():
                if model is None:
                    for split_name, split_df in [("validation", valid), ("test", test)]:
                        pred = split_df["aqi_lag_1"].to_numpy()
                        metrics = evaluate_regression(split_df["target"], pred)
                        regression_rows.append(
                            {
                                "feature_group": group_name,
                                "model": model_name,
                                "horizon": horizon,
                                "split": split_name,
                                **metrics,
                            }
                        )
                    continue

                model.fit(train[columns], train["target"])
                for split_name, split_df in [("validation", valid), ("test", test)]:
                    pred = model.predict(split_df[columns])
                    metrics = evaluate_regression(split_df["target"], pred)
                    regression_rows.append(
                        {
                            "feature_group": group_name,
                            "model": model_name,
                            "horizon": horizon,
                            "split": split_name,
                            **metrics,
                        }
                    )

                if group_name == "full_engineered" and model_name == "xgboost_default_tuned":
                    test_pred = model.predict(test[columns])
                    event_rows.append(
                        {
                            "model": model_name,
                            "horizon": horizon,
                            "split": "test",
                            "threshold": EVENT_THRESHOLD,
                            **evaluate_events(test["target"], test_pred),
                        }
                    )
                    pred_df = test[["timestamp", "aqi", "target"]].copy()
                    pred_df["horizon"] = horizon
                    pred_df["prediction"] = test_pred
                    pred_df["predicted_event"] = pred_df["prediction"] >= EVENT_THRESHOLD
                    pred_df["actual_event"] = pred_df["target"] >= EVENT_THRESHOLD
                    predictions.append(pred_df)

        tuned_candidates = [
            {"max_depth": 3, "learning_rate": 0.10, "n_estimators": 250},
            {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 350},
            {"max_depth": 5, "learning_rate": 0.05, "n_estimators": 450},
            {"max_depth": 6, "learning_rate": 0.03, "n_estimators": 500},
        ]
        columns = groups["full_engineered"]
        model_df = horizon_df.dropna(subset=columns + ["target", "aqi_lag_1"]).copy()
        train, valid, _test = split_chronologically(model_df)
        for params in tuned_candidates:
            model = xgb_model(**params)
            model.fit(train[columns], train["target"])
            pred = model.predict(valid[columns])
            tuning_rows.append({"horizon": horizon, **params, **evaluate_regression(valid["target"], pred)})

    results_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(regression_rows).to_csv(results_dir / "ablation_forecast_results.csv", index=False)
    pd.DataFrame(event_rows).to_csv(results_dir / "event_detection_results.csv", index=False)
    pd.DataFrame(tuning_rows).to_csv(results_dir / "xgboost_tuning_results.csv", index=False)
    if predictions:
        pd.concat(predictions).to_csv(results_dir / "xgboost_test_predictions.csv", index=False)

    print("Saved ablation, tuning, event, and prediction outputs.")
    print(pd.DataFrame(event_rows).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/shadipur_aqi_weather_hourly.csv")
    parser.add_argument("--results-dir", default="experiments/results")
    args = parser.parse_args()
    run(Path(args.input), Path(args.results_dir))


if __name__ == "__main__":
    main()
