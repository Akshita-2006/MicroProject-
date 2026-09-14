"""Interval-safe aggregation for explicitly interpreted mirror clock labels.

This helper does not certify the source timezone or live publication latency.
Callers must resolve those semantics before using its output in model training.
"""
import pandas as pd


def hourly_from_start_labels(frame, value_columns, *, source_clock_timezone,
                             minimum_quarters=3, publication_delay_minutes=0):
    """Convert 15-minute interval-start wall clocks into end-labelled hourly means.

    The mirror's attached timezone is discarded deliberately: source_clock_timezone
    describes the source wall clock, rather than a conversion of the mirror label.
    Every output hour uses only intervals ending on or before that hour.
    Missing quarters remain missing; no forward filling or target construction.
    """
    if not source_clock_timezone:
        raise ValueError('An explicit source clock timezone is required')
    if minimum_quarters not in (1, 2, 3, 4):
        raise ValueError('minimum_quarters must be between 1 and 4')
    if publication_delay_minutes < 0:
        raise ValueError('Publication delay cannot be negative')
    data = frame.copy()
    starts = pd.to_datetime(data['Timestamp'])
    if starts.dt.tz is not None:
        starts = starts.dt.tz_localize(None)
    if starts.isna().any():
        raise ValueError('Missing or invalid interval timestamps')
    if ((starts.dt.minute % 15 != 0) | (starts.dt.second != 0) |
            (starts.dt.microsecond != 0) | (starts.dt.nanosecond != 0)).any():
        raise ValueError('Input timestamps must lie on a 15-minute grid')
    data['_start'] = starts.dt.tz_localize(source_clock_timezone, ambiguous='raise', nonexistent='raise')
    if data['Station ID'].isna().any():
        raise ValueError('Missing station IDs')
    if data.duplicated(['Station ID','_start']).any():
        raise ValueError('Duplicate station/interval rows must be resolved by source audit')
    outputs = []
    for station, group in data.groupby('Station ID'):
        if group['Station Name'].nunique(dropna=False) != 1:
            raise ValueError('A station ID has inconsistent names')
        values = group[value_columns].apply(pd.to_numeric, errors='coerce')
        values.index = pd.DatetimeIndex(group['_start'] + pd.Timedelta(minutes=15))
        aggregated = values.resample('h', closed='right', label='right').mean()
        counts = values.resample('h', closed='right', label='right').count()
        aggregated = aggregated.where(counts >= minimum_quarters)
        aggregated.index.name = 'interval_end'
        aggregated = aggregated.reset_index()
        for column in value_columns:
            aggregated[column + '__quarters'] = counts[column].to_numpy()
        aggregated['available_at'] = aggregated.interval_end + pd.Timedelta(minutes=publication_delay_minutes)
        aggregated['Station ID'] = station
        aggregated['Station Name'] = group['Station Name'].iloc[0]
        outputs.append(aggregated)
    return pd.concat(outputs, ignore_index=True) if outputs else pd.DataFrame()
