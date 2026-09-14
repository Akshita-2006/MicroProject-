"""Describe staged releases without converting their unverified UTC labels."""
from pathlib import Path
import argparse
import json
import pandas as pd
from src.analysis.audit_dataset import longest

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, choices=[2024, 2025], required=True)
    year = parser.parse_args().year
    data = pd.read_parquet(ROOT/f'data/interim/delhi_pollutants_{year}_unverified.parquet')
    data['Station Name'] = data['Station Name'].str.strip()
    # Preserve the mirror labels, rather than assuming a timezone conversion is valid.
    grid = pd.date_range(f'{year}-01-01',f'{year}-12-31 23:45',freq='15min',tz='UTC')
    columns = [c for c in data if c.startswith(('PM2.5 (','PM10 (','NO2 (','SO2 (','Ozone (','CO (','AT (','RH (','WS (','WD ('))]
    stations, variables = [], []
    for (sid,name), group in data.groupby(['Station ID','Station Name']):
        group = group.sort_values('Timestamp')
        duplicate_count = int(group.Timestamp.duplicated().sum())
        unique = group.drop_duplicates('Timestamp').set_index('Timestamp')
        stations.append(dict(station_id=sid,station=name,rows=len(group),
                             first_label=str(group.Timestamp.min()),last_label=str(group.Timestamp.max()),
                             duplicate_timestamps=duplicate_count,expected_quarter_hours=len(grid),
                             timestamp_row_coverage_pct=100*unique.index.isin(grid).sum()/len(grid)))
        for column in columns:
            series = pd.to_numeric(unique[column],errors='coerce').reindex(grid)
            # Report negative values; do not silently discard or certify them.
            observed = int(series.count())
            variables.append(dict(station_id=sid,station=name,variable=column,
                                  observed=observed,calendar_missing_pct=100*series.isna().mean(),
                                  longest_missing_hours=longest(series.isna())/4,
                                  negative_count=int((series<0).sum()),minimum=series.min(),maximum=series.max(),
                                  hours_with_at_least_3_values=int((series.resample('h').count()>=3).sum())))
    out=ROOT/'reports/tables/recent_audit'
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(stations).to_csv(out/f'stations_{year}.csv',index=False)
    pd.DataFrame(variables).to_csv(out/f'variables_{year}.csv',index=False)
    summary=dict(year=year,rows=len(data),station_names=data['Station Name'].nunique(),
                 station_ids=data['Station ID'].nunique(),first_label=str(data.Timestamp.min()),
                 last_label=str(data.Timestamp.max()),timestamp_dtype=str(data.Timestamp.dtype),
                 duplicate_station_time_rows=int(data.duplicated(['Station ID','Timestamp']).sum()),
                 variables=columns,model_ready=False,
                 caution='UTC is the mirror label, not a verified source timezone; hourly counts are audit diagnostics only. Row presence is not pollutant availability. No AQI target is supplied by this release.')
    (out/f'summary_{year}.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(pd.DataFrame(variables).groupby('variable').calendar_missing_pct.mean().to_string())


if __name__ == '__main__':
    main()
