"""Create the all-eligible-station historical AQI/weather panel.

This is deliberately limited to the already audited 2017--2023 AQI archive.
It does not treat the 2024--2025 concentration mirror as a model feature until
the source's interval and unit semantics have passed the provenance gate.
"""
from pathlib import Path
import argparse
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aqi', default=ROOT/'data/interim/delhi_aqi_hourly_long.csv', type=Path)
    parser.add_argument('--weather', default=ROOT/'data/interim/weather_open_meteo_delhi_hourly.csv', type=Path)
    parser.add_argument('--candidates', default=ROOT/'reports/tables/station_expansion/candidates.csv', type=Path)
    parser.add_argument('--output', default=ROOT/'data/processed/delhi_hourly_all_eligible.parquet', type=Path)
    args = parser.parse_args()
    eligible = set(pd.read_csv(args.candidates).query('coverage_candidate').station)
    aqi = pd.read_csv(args.aqi, parse_dates=['timestamp'])
    aqi = aqi[aqi.station_name.isin(eligible)].copy()
    aqi = aqi[(aqi.timestamp >= '2017-01-01') & (aqi.timestamp < '2024-01-01')]
    # One row per station/hour, retaining missing AQI as an unavailable reading.
    if aqi.duplicated(['station_name', 'timestamp']).any():
        raise ValueError('Duplicate AQI records require source resolution before training')
    weather = pd.read_csv(args.weather, parse_dates=['timestamp'])
    expected = pd.date_range('2017-01-01', '2023-12-31 23:00', freq='h')
    panels = []
    for station, group in aqi.groupby('station_name', sort=True):
        panel = group.set_index('timestamp')[['station_name', 'aqi']].reindex(expected)
        panel['station_name'] = station
        panel.index.name = 'timestamp'
        panels.append(panel.reset_index())
    panel = pd.concat(panels, ignore_index=True).merge(weather, on='timestamp', how='left')
    required_weather = ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m',
                        'wind_direction_10m', 'pressure_msl', 'precipitation']
    if panel[required_weather].isna().any().any():
        raise ValueError('Weather must cover every station-hour')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(args.output, index=False)
    summary = panel.groupby('station_name').aqi.agg(hours='size', observed='count').reset_index()
    summary['coverage_pct'] = 100 * summary.observed / summary.hours
    summary.to_csv(ROOT/'reports/tables/all_eligible_station_panel_coverage.csv', index=False)
    print(f'Saved {len(panel):,} rows for {panel.station_name.nunique()} eligible stations to {args.output}')


if __name__ == '__main__':
    main()
