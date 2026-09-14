"""Audit expansion candidates using training-era observations only.

Candidate status is a data-coverage screen, not certification or model validation.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/tables/station_expansion'


def assess(frame):
    frame = frame.copy()
    frame['station_name'] = frame.station_name.str.strip()
    frame['timestamp'] = pd.to_datetime(frame.timestamp)
    frame = frame[(frame.timestamp >= '2017-01-01') & (frame.timestamp < '2022-01-01')]
    recent = pd.date_range('2019-01-01', '2021-12-31 23:00', freq='h')
    rows = []
    for station, group in frame.groupby('station_name'):
        values = pd.to_numeric(group.aqi, errors='coerce')
        group = group.assign(aqi=values.where(values.between(0, 500)))
        conflicts = int((group.groupby('timestamp').aqi.nunique() > 1).sum())
        series = group.groupby('timestamp').aqi.first().sort_index()
        valid = series.dropna()
        first = valid.index.min() if len(valid) else pd.NaT
        # No presumed commissioning date: this is the first observation in this archive.
        active = pd.date_range(first, '2021-12-31 23:00', freq='h') if len(valid) else []
        annual = [series.reindex(recent[recent.year == y]).notna().mean() for y in (2019, 2020, 2021)]
        coverage = float(series.reindex(recent).notna().mean())
        observed = int(series.reindex(recent).count())
        reasons = []
        if conflicts:
            reasons.append('Conflicting training timestamps')
        if observed < 2 * 365 * 24:
            reasons.append('Fewer than two years of observed hours in 2019–2021')
        if coverage < .85:
            reasons.append('2019–2021 coverage below 85%')
        if min(annual) < .70:
            reasons.append('At least one recent training year below 70% coverage')
        rows.append(dict(station=station, first_archive_observation=str(first),
                         active_archive_coverage_pct=100 * series.reindex(active).notna().mean() if len(active) else 0,
                         recent_coverage_pct=100 * coverage,
                         minimum_annual_coverage_pct=100 * min(annual),
                         recent_observed_hours=observed, training_conflicts=conflicts,
                         coverage_candidate=not reasons,
                         reason='; '.join(reasons) or 'Passes coverage screen; source verification and training required'))
    return pd.DataFrame(rows).sort_values('recent_coverage_pct', ascending=False)


def main():
    data = pd.read_csv(ROOT / 'data/interim/delhi_aqi_hourly_long.csv',
                       usecols=['station_name', 'timestamp', 'aqi'])
    report = assess(data)
    previous = pd.read_csv(ROOT / 'reports/tables/v2/station_quality.csv')
    report = report.merge(previous[['station', 'selected']].rename(columns={'selected': 'currently_modelled'}),
                          on='station', how='left', validate='one_to_one')
    OUT.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUT / 'candidates.csv', index=False)
    protocol = dict(observation_cutoff='2021-12-31 23:00', recent_window='2019–2021',
                    minimum_recent_coverage=.85, minimum_each_year_coverage=.70,
                    minimum_observed_hours=17520, conflicting_timestamps_allowed=0,
                    status='coverage-screen-only; does not change deployed station selection',
                    first_observation_note='Archive start is not a certified commissioning date',
                    later_data_used=False)
    (OUT / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    print(report[['station', 'recent_coverage_pct', 'coverage_candidate', 'currently_modelled']].to_string(index=False))


if __name__ == '__main__':
    main()
