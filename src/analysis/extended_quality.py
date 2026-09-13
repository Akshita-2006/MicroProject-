"""Additional source diagnostics; findings never tune test-time model choices."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.analysis.audit_dataset import longest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'reports/tables/v2'


def main():
    panel = pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet')
    rows = []
    for station,g in panel.groupby('station_name'):
        for col in g.select_dtypes('number'):
            s = g[col]
            impossible = pd.Series(False,index=s.index)
            if col == 'relative_humidity_2m': impossible = (s<0)|(s>100)
            if col in ['wind_speed_10m','precipitation']: impossible = s<0
            if col == 'wind_direction_10m': impossible = (s<0)|(s>360)
            rows.append(dict(station=station,variable=col,missing_pct=s.isna().mean()*100,
                             longest_missing_hours=longest(s.isna()),minimum=s.min(),maximum=s.max(),
                             impossible_values=int(impossible.sum()),longest_equal_transitions=longest(s.notna()&s.eq(s.shift()))))
    pd.DataFrame(rows).to_csv(OUT/'variable_quality.csv',index=False)
    panel[panel.timestamp < '2022-01-01'].pivot(index='timestamp',columns='station_name',values='aqi').corr().to_csv(OUT/'station_correlations.csv')
    p = pd.read_parquet(ROOT/'data/interim/delhi_pollutants_2017.parquet')
    pollutants = [c for c in p if c.startswith(('PM2.5 (','PM10 (','NO2 (','Ozone (','SO2 (','CO ('))]
    summaries = []
    for station,g in p.groupby('Station Name'):
        for col in pollutants:
            values = pd.to_numeric(g[col],errors='coerce')
            summaries.append(dict(station=station,variable=col,rows=len(g),observed=int(values.count()),
                                  missing_pct=values.isna().mean()*100,negative_values=int((values<0).sum()),
                                  minimum=values.min(),maximum=values.max(),
                                  first_timestamp=str(g.Timestamp.min()),last_timestamp=str(g.Timestamp.max()),
                                  duplicate_timestamps=int(g.Timestamp.duplicated().sum()),source_id=';'.join(g['Station ID'].unique())))
    pd.DataFrame(summaries).to_csv(OUT/'pollutant_station_quality_2017.csv',index=False)
    p[p['Station Name'].str.contains('Shadipur')][pollutants].corr().to_csv(OUT/'shadipur_pollutant_correlations_2017.csv')
    # Cross-source names are normalized only for diagnostics, never to join measurements.
    mapping = p[['Station Name','Station ID']].drop_duplicates().copy()
    mapping['normalized_name'] = mapping['Station Name'].str.replace(',','',regex=False).str.replace(' - ',' ',regex=False).str.strip()
    mapping.to_csv(OUT/'pollutant_station_identity.csv',index=False)
    print('Extended data-quality and pollutant diagnostics saved')


if __name__ == '__main__':
    main()
