"""Stage a public mirror release for audit, without certifying or joining it."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, choices=[2024, 2025], required=True)
    args = parser.parse_args()
    metadata_url = f'https://api.github.com/repos/Vonter/india-cpcb-aqi/releases/tags/{args.year}'
    with urllib.request.urlopen(metadata_url, timeout=60) as response:
        release = json.load(response)
    asset = next(a for a in release['assets'] if a['name'] == f'cpcb-air-quality-{args.year}.parquet')
    raw = ROOT/'data/raw/recent_audit'
    raw.mkdir(parents=True, exist_ok=True)
    path = raw/asset['name']
    expected = asset.get('digest', '').removeprefix('sha256:')
    if len(expected) != 64:
        raise ValueError('Release does not supply an expected SHA-256')
    if not path.exists():
        partial = path.with_suffix('.part')
        with urllib.request.urlopen(asset['browser_download_url'], timeout=120) as response, partial.open('wb') as output:
            total = 0
            while chunk := response.read(8 * 1024 * 1024):
                output.write(chunk)
                total += len(chunk)
                if total % (64 * 1024 * 1024) == 0:
                    print(f'{args.year}: downloaded {total // (1024*1024)} MiB', flush=True)
        if partial.stat().st_size != asset['size']:
            raise ValueError('Download length mismatch; partial preserved')
        with partial.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != expected:
            raise ValueError('Release hash mismatch; partial preserved')
        partial.rename(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != expected:
        raise ValueError('Existing file hash mismatch')
    target = ROOT/f'data/interim/delhi_pollutants_{args.year}_unverified.parquet'
    count = 0
    parquet = pq.ParquetFile(path)
    with pq.ParquetWriter(target, parquet.schema_arrow) as writer:
        for batch in parquet.iter_batches(batch_size=100_000):
            table = pa.Table.from_batches([batch])
            selected = table.filter(pc.equal(pc.utf8_lower(pc.utf8_trim_whitespace(table['City'])), 'delhi'))
            if selected.num_rows:
                writer.write_table(selected)
                count += selected.num_rows
    evidence = dict(year=args.year, source=asset['browser_download_url'], release_api=metadata_url,
                    sha256=digest, expected_sha256=expected, size=path.stat().st_size,
                    delhi_rows=count, columns=parquet.schema_arrow.names,
                    status='UNVERIFIED_TIMESTAMP_SEMANTICS: audit only, not model-ready')
    out = ROOT/'reports/source_evidence'/f'recent_release_{args.year}.json'
    out.write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    main()
