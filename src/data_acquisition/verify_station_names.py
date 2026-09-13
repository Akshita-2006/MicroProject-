"""Match selected names against the downloaded government-domain CPCB station list."""
from pathlib import Path
import re
import hashlib
import json
import pandas as pd
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]


def normalized(value):
    return re.sub(r'\s+',' ',value.replace(',','').replace(' - ',' ')).strip()


def main():
    pdf=ROOT/'reports/source_evidence/cpcb_station_list.pdf'
    reader=PdfReader(pdf)
    rows=[]
    quality=pd.read_csv(ROOT/'reports/tables/v2/station_quality.csv')
    # Relevant Delhi table is on pages 1 and 2; verify exact normalized name matches.
    lines=[(i+1,line) for i in [0,1] for line in reader.pages[i].extract_text().splitlines()]
    for station in quality.loc[quality.selected,'station']:
        hits=[(page,line) for page,line in lines if normalized(re.sub(r'^\d+\s+','',line)) == station]
        rows.append(dict(station=station,matched=len(hits)==1,pdf_page=hits[0][0] if hits else None,
                         source_row=hits[0][1] if hits else None))
    result=pd.DataFrame(rows)
    result.to_csv(ROOT/'reports/tables/v2/official_station_name_matches.csv',index=False)
    evidence=dict(url='https://airquality.cpcb.gov.in/ccr_docs/caaqms_list_All_India.pdf',
                  sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),matched_stations=int(result.matched.sum()),
                  limitation='Confirms station names and agencies in this list; contains no source IDs, coordinates, timezone, or per-record verification.')
    (ROOT/'reports/source_evidence/official_station_name_verification.json').write_text(json.dumps(evidence,indent=2))
    print(result.to_string(index=False))


if __name__=='__main__':
    main()
