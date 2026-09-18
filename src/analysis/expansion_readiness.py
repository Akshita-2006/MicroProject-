"""Prepare station-name links and recent weather without approving source joins."""
from pathlib import Path
import hashlib
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def station_key(name):
    # Keep agency tokens: Pusa DPCC and Pusa IMD are different stations.
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


def link_stations(historical, recent):
    historical = historical.copy()
    recent = recent.copy()
    historical['name_key'] = historical.station.map(station_key)
    recent['name_key'] = recent.station.map(station_key)
    if historical.name_key.duplicated().any():
        raise ValueError('Ambiguous historical station names')
    if recent.name_key.duplicated().any() or recent.station_id.duplicated().any():
        raise ValueError('Ambiguous recent station names or IDs')
    result = historical.merge(recent[['name_key', 'station', 'station_id']],
                              on='name_key', how='outer', suffixes=('_historical', '_recent'),
                              validate='one_to_one', indicator=True)
    result['name_match'] = result['_merge'].eq('both')
    result['identity_status'] = result.name_match.map({
        True: 'Name match only; official ID verification pending',
        False: 'No exact normalized name match; manual review required'})
    return result.drop(columns=['_merge', 'name_key'])


def check_weather(payload):
    if payload.get('timezone') != 'Asia/Kolkata' or payload.get('utc_offset_seconds') != 19800:
        raise ValueError('Weather must explicitly use IST')
    expected = {'temperature_2m': '°C', 'relative_humidity_2m': '%',
                'wind_speed_10m': 'km/h', 'wind_direction_10m': '°',
                'pressure_msl': 'hPa', 'precipitation': 'mm'}
    for column, unit in expected.items():
        if payload['hourly_units'].get(column) != unit:
            raise ValueError(f'Unexpected unit for {column}')
    frame = pd.DataFrame(payload['hourly']).rename(columns={'time': 'timestamp'})
    frame['timestamp'] = pd.to_datetime(frame.timestamp).dt.tz_localize('Asia/Kolkata')
    if frame.empty or frame.timestamp.duplicated().any():
        raise ValueError('Empty weather data or duplicate times')
    if not frame.timestamp.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError('Weather calendar is not continuous hourly data')
    if set(expected) - set(frame.columns):
        raise ValueError('Required weather variables missing')
    return frame


def main():
    out = ROOT/'reports/tables/station_expansion'
    out.mkdir(parents=True, exist_ok=True)
    historical = pd.read_csv(out/'candidates.csv')
    summary = {}
    for year in (2024, 2025):
        recent = pd.read_csv(ROOT/f'reports/tables/recent_audit/stations_{year}.csv')
        linked = link_stations(historical, recent)
        linked.to_csv(out/f'name_links_{year}.csv', index=False)
        summary[str(year)] = dict(recent_stations=len(recent), name_matches=int(linked.name_match.sum()),
                                 coverage_candidates_with_name_match=int((linked.name_match & linked.coverage_candidate.eq(True)).sum()))
    raw = ROOT/'data/raw/recent_audit/weather_delhi_2024_2026.json'
    payload = json.loads(raw.read_text(encoding='utf-8'))
    weather = check_weather(payload)
    target = ROOT/'data/interim/weather_delhi_2024_2026.parquet'
    weather.to_parquet(target, index=False)
    summary['weather'] = dict(hours=len(weather), first=str(weather.timestamp.min()),
                              last=str(weather.timestamp.max()), latitude=payload['latitude'],
                              longitude=payload['longitude'], timezone=payload['timezone'],
                              raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                              missing_values=weather.drop(columns='timestamp').isna().sum().to_dict(),
                              source='Open-Meteo historical archive; regional grid, not station-local weather',
                              use='Staged only; no join to unverified pollution timestamps')
    summary['forecast_expansion_ready'] = False
    summary['remaining'] = ['Official station ID checks', 'Verified pollution timezone',
                            'Recent AQI targets', 'Expanded training and evaluation']
    (out/'readiness_2026_09_16.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
