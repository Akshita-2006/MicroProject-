"""Build one hourly Delhi concentration panel from verified annual releases."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
YEARS = range(2017, 2026)
TARGETS = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'Ozone (µg/m³)',
           'SO2 (µg/m³)', 'CO (mg/m³)', 'Benzene (µg/m³)']

def normalize(value):
    import re
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\b(delhi|cpcb|dpcc|imd|iitm)\b', '', str(value).lower()))

def main():
    roster = pd.read_parquet(ROOT/'data/processed/delhi_hourly_all_eligible.parquet', columns=['station_name']).station_name.drop_duplicates()
    mapping = {normalize(name): name for name in roster}
    outputs = []
    for year in YEARS:
        path = ROOT/f'data/interim/delhi_pollutants_{year}_source_release.parquet'
        if not path.exists():
            if year in (2024, 2025):
                path = ROOT/f'data/interim/delhi_pollutants_{year}_unverified.parquet'
            elif year == 2017:
                path = ROOT/'data/interim/delhi_pollutants_2017.parquet'
            else:
                raise FileNotFoundError(path)
        data = pd.read_parquet(path, columns=['Station Name', 'Timestamp'] + TARGETS)
        data['station_name'] = data['Station Name'].map(lambda x: mapping.get(normalize(x)))
        data = data[data.station_name.notna()].copy()
        data['timestamp'] = pd.to_datetime(data['Timestamp']).dt.tz_localize(None)
        data = data.drop(columns=['Station Name', 'Timestamp'])
        for col in TARGETS:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        # Hourly mean of the source's 15-minute records. The source clock is preserved as supplied.
        data = data.groupby(['station_name', pd.Grouper(key='timestamp', freq='h')], as_index=False)[TARGETS].mean()
        outputs.append(data)
        print(f'{year}: {len(data):,} hourly station records', flush=True)
    panel = pd.concat(outputs, ignore_index=True).sort_values(['station_name', 'timestamp'])
    output = ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet'
    panel.to_parquet(output, index=False)
    coverage = panel.groupby('station_name')[TARGETS].count().reset_index()
    coverage.to_csv(ROOT/'reports/tables/concentration_panel_coverage_2017_2025.csv', index=False)
    print(f'Saved {len(panel):,} rows for {panel.station_name.nunique()} stations to {output}')

if __name__ == '__main__':
    main()
