"""Download a bounded source sample and inspect Delhi pollutant availability."""
from pathlib import Path
import json
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    url = 'https://github.com/Vonter/india-cpcb-aqi/releases/download/2017/cpcb-air-quality-2017.parquet'
    path = ROOT/'data/raw/cpcb-air-quality-2017.parquet'
    if not path.exists():
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        path.write_bytes(response.content)
    data = pd.read_parquet(path)
    delhi = data[data.City.str.strip().str.lower().eq('delhi')].copy()
    delhi.to_parquet(ROOT/'data/interim/delhi_pollutants_2017.parquet', index=False)
    report = {'source':url, 'rows':len(delhi), 'columns':list(delhi.columns),
              'missing_pct':(delhi.isna().mean()*100).to_dict(),
              'stations':delhi['Station Name'].unique().tolist()}
    (ROOT/'reports/tables/v2/pollutant_investigation.json').write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str))


if __name__ == '__main__':
    main()
