"""Utilities for turning forecast sequences into pollution episodes."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Episode:
    onset_time: pd.Timestamp
    recovery_time: pd.Timestamp | None
    peak_time: pd.Timestamp
    peak_value: float
    duration_hours: int
    severity: str


def classify_aqi_like(value: float) -> str:
    """Classify an AQI-like value using CPCB category bands."""
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Satisfactory"
    if value <= 200:
        return "Moderate"
    if value <= 300:
        return "Poor"
    if value <= 400:
        return "Very Poor"
    return "Severe"


def detect_sustained_episode(
    forecast: pd.Series,
    threshold: float,
    minimum_persistence_hours: int = 2,
) -> Episode | None:
    """Detect the first sustained above-threshold interval in an hourly forecast series."""
    above = forecast >= threshold
    if not above.any():
        return None

    run_start = None
    run_values: list[tuple[pd.Timestamp, float]] = []

    for timestamp, is_above in above.items():
        if is_above:
            if run_start is None:
                run_start = timestamp
                run_values = []
            run_values.append((timestamp, float(forecast.loc[timestamp])))
            continue

        if run_start is not None and len(run_values) >= minimum_persistence_hours:
            return _build_episode(run_values, recovery_time=timestamp)
        run_start = None
        run_values = []

    if run_start is not None and len(run_values) >= minimum_persistence_hours:
        return _build_episode(run_values, recovery_time=None)
    return None


def _build_episode(
    run_values: list[tuple[pd.Timestamp, float]],
    recovery_time: pd.Timestamp | None,
) -> Episode:
    peak_time, peak_value = max(run_values, key=lambda item: item[1])
    return Episode(
        onset_time=run_values[0][0],
        recovery_time=recovery_time,
        peak_time=peak_time,
        peak_value=peak_value,
        duration_hours=len(run_values),
        severity=classify_aqi_like(peak_value),
    )
