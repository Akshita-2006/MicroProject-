"""Create a transparent calculated-AQI target from the uniform pollutant panel.

This is a research target, not an official CPCB AQI release.  It uses rolling
averages and published CPCB concentration breakpoints, then takes the highest
available pollutant sub-index for each station-hour.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'data/processed/delhi_concentrations_hourly_2017_2025.parquet'
OUTPUT=ROOT/'data/processed/delhi_calculated_aqi_hourly_2017_2025.parquet'

SPECS={
 'PM2.5 (µg/m³)':(24,[(0,30,0,50),(30,60,50,100),(60,90,100,200),(90,120,200,300),(120,250,300,400),(250,500,400,500)]),
 'PM10 (µg/m³)':(24,[(0,50,0,50),(50,100,50,100),(100,250,100,200),(250,350,200,300),(350,430,300,400),(430,600,400,500)]),
 'NO2 (µg/m³)':(24,[(0,40,0,50),(40,80,50,100),(80,180,100,200),(180,280,200,300),(280,400,300,400),(400,1000,400,500)]),
 'Ozone (µg/m³)':(8,[(0,50,0,50),(50,100,50,100),(100,168,100,200),(168,208,200,300),(208,748,300,400),(748,1000,400,500)]),
 'SO2 (µg/m³)':(24,[(0,40,0,50),(40,80,50,100),(80,380,100,200),(380,800,200,300),(800,1600,300,400),(1600,3000,400,500)]),
 'CO (mg/m³)':(8,[(0,1,0,50),(1,2,50,100),(2,10,100,200),(10,17,200,300),(17,34,300,400),(34,50,400,500)])}

def subindex(value, bands):
    answer=np.full(len(value),np.nan)
    for lo,hi,ilo,ihi in bands:
        mask=value.ge(lo)&value.le(hi)&np.isnan(answer)
        answer[mask]=((ihi-ilo)/(hi-lo)*(value[mask]-lo)+ilo).clip(0,500)
    return answer

def main():
    data=pd.read_parquet(INPUT).sort_values(['station_name','timestamp'])
    indices=[]
    for column,(hours,bands) in SPECS.items():
        averaged=data.groupby('station_name')[column].transform(lambda x:x.rolling(hours,min_periods=hours).mean())
        indices.append(pd.Series(subindex(averaged,bands),index=data.index,name=column))
    index_frame=pd.concat(indices,axis=1)
    frame=data[['station_name','timestamp']].copy()
    frame['calculated_aqi']=index_frame.max(axis=1,skipna=True)
    frame['dominant_pollutant']=index_frame.fillna(-np.inf).idxmax(axis=1).where(frame.calculated_aqi.notna())
    frame.to_parquet(OUTPUT,index=False)
    frame.groupby(frame.timestamp.dt.year).calculated_aqi.agg(['count','mean']).to_csv(ROOT/'reports/tables/calculated_aqi_coverage_2017_2025.csv')
    print(f'Saved {len(frame):,} calculated AQI rows to {OUTPUT}')
if __name__=='__main__': main()
