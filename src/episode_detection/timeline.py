"""Hourly episode extraction with explicit missing-data and boundary censoring."""
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd


def category(value):
    if not np.isfinite(value) or value < 0 or value > 500:
        return 'Unknown'
    # Predictions are continuous; round to the nearest integer AQI before categorizing.
    value = np.floor(value + .5)
    return next(label for upper,label in [(50,'Good'),(100,'Satisfactory'),(200,'Moderate'),(300,'Poor'),(400,'Very Poor'),(500,'Severe')] if value <= upper)


@dataclass
class Episode:
    onset: pd.Timestamp
    end: pd.Timestamp
    recovery: pd.Timestamp | None
    peak_time: pd.Timestamp
    peak_aqi: float
    severity: str
    duration_hours: int
    left_censored: bool
    right_censored: bool

    def record(self):
        return asdict(self)


def extract(series, persistence=3, threshold=301):
    if persistence < 1:
        raise ValueError('Persistence must be positive')
    if not isinstance(series.index, pd.DatetimeIndex) or series.index.has_duplicates:
        raise ValueError('Unique DatetimeIndex required')
    if series.empty:
        return []
    series = series.sort_index().reindex(pd.date_range(series.index.min(), series.index.max(), freq='h'))
    values = series.to_numpy(dtype=float)
    high = np.isfinite(values) & (values >= threshold)
    episodes = []
    i = 0
    while i < len(values):
        if not high[i]:
            i += 1
            continue
        start = i
        while i < len(values) and high[i]:
            i += 1
        if i-start < persistence:
            continue
        right = i == len(values) or not np.isfinite(values[i])
        peak = start + int(np.argmax(values[start:i]))
        episodes.append(Episode(series.index[start], series.index[i-1], None if right else series.index[i],
                                series.index[peak],float(values[peak]),category(values[peak]),i-start,
                                start == 0 or not np.isfinite(values[start-1]), right))
    return episodes


def evaluate(actual, predicted, persistence=3):
    """One-to-one maximum-cardinality overlap matching; no event-level TN exists."""
    from scipy.optimize import linear_sum_assignment
    a, p = extract(actual,persistence), extract(predicted,persistence)
    weights = np.zeros((len(a),len(p)))
    for i,x in enumerate(a):
        for j,y in enumerate(p):
            overlap = max(0.,(min(x.end,y.end)-max(x.onset,y.onset)).total_seconds()/3600+1)
            if overlap:
                union = (max(x.end,y.end)-min(x.onset,y.onset)).total_seconds()/3600+1
                weights[i,j] = 1 + overlap/union/(max(len(a),len(p))+1)
    matches = []
    if weights.size:
        ii,jj = linear_sum_assignment(weights, maximize=True)
        for i,j in zip(ii,jj):
            if weights[i,j] > 0:
                x,y = a[i],p[j]
                hours = lambda b,c:abs((b-c).total_seconds())/3600
                matches.append(dict(actual_onset=x.onset,predicted_onset=y.onset,
                                    onset_error_hours=hours(x.onset,y.onset) if not(x.left_censored or y.left_censored) else np.nan,
                                    peak_error_hours=hours(x.peak_time,y.peak_time),
                                    duration_error_hours=abs(x.duration_hours-y.duration_hours) if not(x.left_censored or y.left_censored or x.right_censored or y.right_censored) else np.nan,
                                    recovery_error_hours=hours(x.recovery,y.recovery) if x.recovery is not None and y.recovery is not None else np.nan))
    tp = len(matches)
    precision = tp/len(p) if p else 0.
    recall = tp/len(a) if a else 0.
    metrics = dict(actual_events=len(a),predicted_events=len(p),matched_events=tp, false_alarms=len(p)-tp,
                   missed_events=len(a)-tp,event_precision=precision,event_recall=recall,
                   event_f1=2*precision*recall/(precision+recall) if precision+recall else 0.)
    for col in ['onset_error_hours','peak_error_hours','duration_error_hours','recovery_error_hours']:
        v = [m[col] for m in matches if np.isfinite(m[col])]
        metrics[col] = float(np.mean(v)) if v else None
        metrics[col+'_n'] = len(v)
    return metrics, matches
