"""Verify the local AQI bytes against a pinned public source; save source evidence."""
from pathlib import Path
import hashlib
import json
import requests

ROOT = Path(__file__).resolve().parents[2]


def main():
    api='https://api.github.com/repos/Vonter/india-cpcb-aqi'
    r=requests.get(api+'/commits/main',timeout=30)
    r.raise_for_status()
    sha=r.json()['sha']
    raw=f'https://raw.githubusercontent.com/Vonter/india-cpcb-aqi/{sha}/'
    out=ROOT/'reports/source_evidence'
    out.mkdir(parents=True,exist_ok=True)
    source=requests.get(raw+'data/cpcb-aqi.csv.gz',timeout=90)
    source.raise_for_status()
    local=ROOT/'data/raw/cpcb-aqi.csv.gz'
    digest=lambda b:hashlib.sha256(b).hexdigest()
    evidence=dict(repository=api,commit=sha,download_url=raw+'data/cpcb-aqi.csv.gz',
                  remote_sha256=digest(source.content),local_sha256=digest(local.read_bytes()))
    evidence['byte_match']=evidence['remote_sha256']==evidence['local_sha256']
    for name in ['README.md','DATA.md','parse.py','fetch.py','LICENSE']:
        response=requests.get(raw+name,timeout=30)
        response.raise_for_status()
        (out/name).write_bytes(response.content)
    (out/'provenance.json').write_text(json.dumps(evidence,indent=2))
    if not evidence['byte_match']:
        raise ValueError('Local AQI file differs from the source snapshot; review before replacing anything')
    print(json.dumps(evidence,indent=2))


if __name__ == '__main__':
    main()
