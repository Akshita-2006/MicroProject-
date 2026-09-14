"""Reproduce the bounded comparison against captured official Alipur table rows."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = ROOT/'reports/source_evidence'
    source = pd.read_csv(out/'alipur_official_2025_sample.csv')
    evidence_path = out/'alipur_official_2025_comparison.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
    mirror = pd.read_parquet(ROOT/'data/interim/delhi_pollutants_2025_unverified.parquet')
    mirror = mirror[mirror['Station Name'].str.strip().eq(evidence['station'])].copy()
    mirror.index = mirror.Timestamp.dt.tz_localize(None)
    if mirror.index.duplicated().any():
        raise ValueError('Ambiguous duplicate source timestamps')
    clock = pd.to_datetime(source['Date From'],format='%d-%m-%Y %H:%M')
    columns = list(source.columns[2:])
    expected = source[columns].to_numpy(dtype=float)
    comparisons = []
    for name, shift in [('same_clock_interval_start',0),('interval_end',15),
                        ('UTC_to_IST_hypothesis',-330),('IST_to_UTC_hypothesis',330)]:
        labels = pd.DatetimeIndex(clock + pd.Timedelta(minutes=shift))
        present = labels.isin(mirror.index)
        actual = mirror.reindex(labels)[columns].to_numpy(dtype=float)
        numeric = np.isfinite(expected) & np.isfinite(actual)
        comparisons.append(dict(hypothesis=name,shift_minutes=shift,
            matched_timestamp_rows=int(present.sum()),comparable_numeric_cells=int(numeric.sum()),
            equal_numeric_cells=int(np.isclose(expected,actual,atol=1e-8,rtol=0)[numeric].sum()),
            matching_missing_cells=int((np.isnan(expected)&np.isnan(actual)&present[:,None]).sum())))
    evidence['comparisons'] = comparisons
    evidence['reproduce'] = 'python -m src.data_acquisition.compare_official_sample'
    evidence_path.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print(json.dumps(comparisons,indent=2))


if __name__ == '__main__':
    main()
