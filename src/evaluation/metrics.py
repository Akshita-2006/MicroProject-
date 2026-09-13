"""Forecast and event evaluation metrics."""

from __future__ import annotations

import numpy as np


def mae(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def persistence_forecast(values, horizon: int):
    """Return aligned y_true and naive predictions for a fixed forecast horizon."""
    values = np.asarray(values, dtype=float)
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    return values[horizon:], values[:-horizon]
