"""Read CPCB's public station metadata endpoint without bypassing TLS or access controls."""
from pathlib import Path
import base64
import json
import requests

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=ROOT/'reports/source_evidence'
    out.mkdir(parents=True,exist_ok=True)
    url='https://airquality.cpcb.gov.in/dataRepository/all_india_stationlist'
    record={'url':url,'purpose':'Verify station identities directly with CPCB'}
    try:
        r=requests.post(url,data='e30=',headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},timeout=30)
        record['http_status']=r.status_code
        r.raise_for_status()
        payload=json.loads(base64.b64decode(r.text))
        (out/'cpcb_stations.json').write_text(json.dumps(payload,indent=2))
        record['status']='retrieved'
    except Exception as error:
        record.update(status='unavailable',reason=str(error))
    (out/'primary_source_attempt.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
