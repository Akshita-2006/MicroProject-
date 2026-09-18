# india-cpcb-aqi

Dataset of 15-minutely air quality and hourly AQI measurements in India. Sourced from the [Central Pollution Control Board (CPCB) Data Repository](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-data-repository) and [Central Pollution Control Board (CPCB) AQI Repository](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/aqi-repository).

Explore a subset of the 15-minutely, station-level air quality measurements dataset [here](https://hyparam.github.io/demos/hyparquet/?key=https%3A%2F%2Fraw.githubusercontent.com%2FVonter%2Findia-cpcb-aqi%2Fmain%2Fdata%2Flatest-air-quality.parquet).

Explore the hourly, station-level AQI measurements dataset [here](https://hyparam.github.io/demos/hyparquet/?key=https%3A%2F%2Fraw.githubusercontent.com%2FVonter%2Findia-cpcb-aqi%2Fmain%2Fdata%2Fcpcb-aqi.parquet).

## Data

* The data for 15-minute interval, station-level air quality measurements is available as Parquet and compressed CSV files on the [Releases](https://github.com/Vonter/india-cpcb-aqi/releases) page.
* The upstream `cpcb-aqi.csv.gz` and `cpcb-aqi.parquet` files are published on the [Releases](https://github.com/Vonter/india-cpcb-aqi/releases) page. They are not stored in this evidence folder.

For more details, refer to the [DATA.md](DATA.md).

## Visualizations

#### AQI at IGI Airport, Delhi

![](viz/igi.png)

## Scripts

- [fetch.py](fetch.py) Fetches the CSV files containing 15-minutely air quality data and hourly AQI data
- [parse.py](parse.py): Parses the CSV files to generate the Parquet and compressed CSV dataset

## License

This india-cpcb-aqi dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. 
Some individual contents of the database are under copyright by CPCB.

You are free:

* **To share**: To copy, distribute and use the database.
* **To create**: To produce works from the database.
* **To adapt**: To modify, transform and build upon the database.

As long as you:

* **Attribute**: You must attribute any public use of the database, or works produced from the database, in the manner specified in the ODbL. For any use or redistribution of the database, or works produced from it, you must make clear to others the license of the database and keep intact any notices on the original database.
* **Share-Alike**: If you publicly use any adapted version of this database, or works produced from an adapted database, you must also offer that adapted database under the ODbL.
* **Keep open**: If you redistribute the database, or an adapted version of it, then you may use technological measures that restrict the work (such as DRM) as long as you also redistribute a version without such measures.

## Generating

Ensure that `python` and the required dependencies in `requirements.txt` are installed.

```
# Fetch the CSV files
python fetch.py

# Parse the CSV files
python parse.py
```

## TODO

- Interactive visualization website

## Credits

- [CPCB](https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/aqi-repository)
