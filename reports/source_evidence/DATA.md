# india-cpcb-aqi

The source data is fetched from the [Central Pollution Control Board (CPCB) Data Repository](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-data-repository) and [Central Pollution Control Board (CPCB) AQI Repository](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/aqi-repository)

## Data Dictionary

### 15-minute Interval Air Quality Data

| Variable | Type | Description |
|----------|------|-------------|
| Station ID | string | Unique identifier for each monitoring station (e.g., site_1406) |
| State | string | Name of the state or union territory where the station is located |
| City | string | Name of the city where the monitoring station is located |
| Station Name | string | Full name of the monitoring station |
| Timestamp | datetime | Timestamp of the air quality measurements in UTC (15-minute interval data, YYYY-MM-DD HH:MM:SS format) |
| PM2.5 (µg/m³) | float | Concentration of fine particulate matter (diameter ≤ 2.5 µm) in micrograms per cubic meter |
| PM10 (µg/m³) | float | Concentration of coarse particulate matter (diameter ≤ 10 µm) in micrograms per cubic meter |
| NO (µg/m³) | float | Concentration of nitric oxide in micrograms per cubic meter |
| NO2 (µg/m³) | float | Concentration of nitrogen dioxide in micrograms per cubic meter |
| NOx (ppb) | float | Concentration of nitrogen oxides (NO + NO2) in parts per billion |
| NH3 (µg/m³) | float | Concentration of ammonia in micrograms per cubic meter |
| SO2 (µg/m³) | float | Concentration of sulfur dioxide in micrograms per cubic meter |
| CO (mg/m³) | float | Concentration of carbon monoxide in milligrams per cubic meter |
| Ozone (µg/m³) | float | Concentration of ground-level ozone in micrograms per cubic meter |
| Benzene (µg/m³) | float | Concentration of benzene (volatile organic compound) in micrograms per cubic meter |
| Toluene (µg/m³) | float | Concentration of toluene (volatile organic compound) in micrograms per cubic meter |
| Xylene (µg/m³) | float | Concentration of xylene (volatile organic compound) in micrograms per cubic meter |
| O Xylene (µg/m³) | float | Concentration of ortho-xylene (volatile organic compound) in micrograms per cubic meter (typically null/not measured) |
| Eth-Benzene (µg/m³) | float | Concentration of ethylbenzene (volatile organic compound) in micrograms per cubic meter |
| MP-Xylene (µg/m³) | float | Concentration of meta/para-xylene (volatile organic compound) in micrograms per cubic meter |
| AT (°C) | float | Ambient air temperature in degrees Celsius |
| RH (%) | float | Relative humidity as a percentage |
| WS (m/s) | float | Wind speed in meters per second |
| WD (deg) | float | Wind direction in degrees (0-360) |
| RF (mm) | float | Rainfall in millimeters |
| TOT-RF (mm) | float | Total rainfall in millimeters |
| SR (W/mt2) | float | Solar radiation in watts per square meter |
| BP (mmHg) | float | Barometric pressure in millimeters of mercury |
| VWS (m/s) | float | Vertical wind speed in meters per second |


### Hourly AQI Data

| Variable | Type | Description |
|----------|------|-------------|
| Station ID | string | Unique identifier for each monitoring station (e.g., site_1406) |
| State | string | Name of the state or union territory where the station is located |
| City | string | Name of the city where the monitoring station is located |
| Station Name | string | Full name of the monitoring station |
| Date | datetime | Date of the AQI measurements (YYYY-MM-DD format) |
| 00:00:00 | integer | AQI value measured at midnight (00:00 hours) |
| 01:00:00 | integer | AQI value measured at 1:00 AM |
| 02:00:00 | integer | AQI value measured at 2:00 AM |
| 03:00:00 | integer | AQI value measured at 3:00 AM |
| 04:00:00 | integer | AQI value measured at 4:00 AM |
| 05:00:00 | integer | AQI value measured at 5:00 AM |
| 06:00:00 | integer | AQI value measured at 6:00 AM |
| 07:00:00 | integer | AQI value measured at 7:00 AM |
| 08:00:00 | integer | AQI value measured at 8:00 AM |
| 09:00:00 | integer | AQI value measured at 9:00 AM |
| 10:00:00 | integer | AQI value measured at 10:00 AM |
| 11:00:00 | integer | AQI value measured at 11:00 AM |
| 12:00:00 | integer | AQI value measured at 12:00 PM (noon) |
| 13:00:00 | integer | AQI value measured at 1:00 PM |
| 14:00:00 | integer | AQI value measured at 2:00 PM |
| 15:00:00 | integer | AQI value measured at 3:00 PM |
| 16:00:00 | integer | AQI value measured at 4:00 PM |
| 17:00:00 | integer | AQI value measured at 5:00 PM |
| 18:00:00 | integer | AQI value measured at 6:00 PM |
| 19:00:00 | integer | AQI value measured at 7:00 PM |
| 20:00:00 | integer | AQI value measured at 8:00 PM |
| 21:00:00 | integer | AQI value measured at 9:00 PM |
| 22:00:00 | integer | AQI value measured at 10:00 PM |
| 23:00:00 | integer | AQI value measured at 11:00 PM |