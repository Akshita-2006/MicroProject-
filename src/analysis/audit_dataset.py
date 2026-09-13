"""Reproducible calendar-based quality audit; station choice uses 2017–2021 only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def longest(mask):
    s = pd.Series(np.asarray(mask, dtype=bool))
    return int(s.groupby((s != s.shift()).cumsum()).sum().max()) if len(s) else 0


def main():
    out = ROOT / 'reports/tables/v2'
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / 'data/interim/delhi_aqi_hourly_long.csv', parse_dates=['timestamp'])
    df['station_name'] = df.station_name.str.strip()
    grid = pd.date_range('2017-01-01', '2023-12-31 23:00', freq='h')
    rows, years, clean = [], [], []
    for name, g in df.groupby('station_name'):
        dup = int(g.duplicated('timestamp').sum())
        conflict = int((g.groupby('timestamp').aqi.nunique() > 1).sum())
        s = g.groupby('timestamp').aqi.first().reindex(grid)
        bad = (s < 0) | (s > 500)
        s = s.mask(bad)
        train = s.loc[:'2021-12-31 23:00']
        constant = s.notna() & s.eq(s.shift())
        rows.append(dict(station=name, source_rows=len(g), expected_hours=len(grid),
                         observed=int(s.count()), missing_pct=float(s.isna().mean()*100),
                         first_observation=str(s.first_valid_index()), last_observation=str(s.last_valid_index()),
                         missing_hours_absent_rows=len(grid)-g.timestamp.nunique(), duplicates=dup,
                         conflicting_timestamps=conflict, invalid_range=int(bad.sum()),
                         longest_missing_hours=longest(s.isna()), longest_equal_transitions=longest(constant),
                         severe_hours=int((s >= 401).sum()), train_coverage=float(train.notna().mean()),
                         source_ids=';'.join(g.station_id.dropna().unique()), available_variables='aqi'))
        for year, v in s.groupby(s.index.year):
            years.append(dict(station=name, year=year, hours=len(v), observed=int(v.count()), missing_pct=v.isna().mean()*100))
        clean.append(pd.DataFrame({'timestamp':grid, 'station_name':name, 'aqi':s.values}))
    quality = pd.DataFrame(rows).sort_values('train_coverage', ascending=False)
    # Fixed data-quality policy: at least 85% of full training calendar; no conflicts.
    quality['selected'] = (quality.train_coverage >= .85) & (quality.conflicting_timestamps == 0)
    quality.to_csv(out/'station_quality.csv', index=False)
    pd.DataFrame(years).to_csv(out/'station_year_quality.csv', index=False)
    selected = quality.loc[quality.selected, 'station'].tolist()
    panel = pd.concat([g for g in clean if g.station_name.iloc[0] in selected], ignore_index=True)
    weather_path = ROOT/'data/raw/weather_open_meteo_delhi_2017_2023.json'
    weather = json.loads(weather_path.read_text())
    metadata = {k:v for k,v in weather.items() if k != 'hourly'}
    if weather.get('utc_offset_seconds') != 19800:
        raise ValueError('Weather timezone does not match assumed IST AQI timestamps')
    w = pd.DataFrame(weather['hourly']).rename(columns={'time':'timestamp'})
    w.timestamp = pd.to_datetime(w.timestamp)
    assert not w.timestamp.duplicated().any()
    panel = panel.merge(w, on='timestamp', how='left', validate='many_to_one')
    panel.to_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet', index=False)
    panel.groupby('station_name')[w.columns.drop('timestamp').tolist()+['aqi']].agg(lambda x:x.isna().mean()*100).to_csv(out/'variable_missingness.csv')
    panel[panel.timestamp < '2022-01-01'].groupby(['station_name', panel.timestamp.dt.month]).aqi.agg(['count','mean','median','max']).to_csv(out/'training_monthly_eda.csv')
    panel[panel.timestamp < '2022-01-01'].select_dtypes('number').corr().to_csv(out/'training_correlations.csv')
    metadata['aqi_timezone_assumption'] = 'Asia/Kolkata; hourly AQI dictionary does not explicitly certify timezone'
    metadata['selected_stations'] = selected
    metadata['sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'data/raw/cpcb-aqi.csv.gz', weather_path]}
    (out/'data_manifest.json').write_text(json.dumps(metadata, indent=2))
    print(quality[['station','train_coverage','missing_pct','selected']].to_string(index=False))


if __name__ == '__main__':
    main()
