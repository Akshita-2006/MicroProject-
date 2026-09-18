import unittest
import pandas as pd
from src.analysis.expansion_readiness import link_stations, check_weather


class ExpansionReadiness(unittest.TestCase):
    def test_agencies_are_not_merged(self):
        historical = pd.DataFrame({'station': ['Pusa Delhi DPCC', 'Pusa Delhi IMD']})
        recent = pd.DataFrame({'station': ['Pusa, Delhi - DPCC'], 'station_id': ['site_a']})
        linked = link_stations(historical, recent)
        self.assertEqual(int(linked.name_match.sum()), 1)
        self.assertFalse(linked.loc[linked.station_historical.eq('Pusa Delhi IMD'), 'name_match'].iloc[0])

    def test_ambiguous_ids_rejected(self):
        historical = pd.DataFrame({'station': ['Pusa Delhi DPCC']})
        recent = pd.DataFrame({'station': ['Pusa Delhi DPCC', 'Pusa Delhi IMD'], 'station_id': ['same', 'same']})
        with self.assertRaises(ValueError):
            link_stations(historical, recent)

    def test_weather_clock_and_gaps(self):
        units = {'temperature_2m': '°C', 'relative_humidity_2m': '%', 'wind_speed_10m': 'km/h',
                 'wind_direction_10m': '°', 'pressure_msl': 'hPa', 'precipitation': 'mm'}
        payload = {'timezone': 'Asia/Kolkata', 'utc_offset_seconds': 19800, 'hourly_units': units,
                   'hourly': {'time': ['2024-01-01T00:00', '2024-01-01T01:00'], **{k: [1, None] for k in units}}}
        result = check_weather(payload)
        self.assertEqual(str(result.timestamp.dt.tz), 'Asia/Kolkata')
        self.assertTrue(pd.isna(result.temperature_2m.iloc[1]))
        payload['hourly']['time'][1] = '2024-01-01T02:00'
        with self.assertRaises(ValueError):
            check_weather(payload)
        payload['timezone'] = 'UTC'
        with self.assertRaises(ValueError):
            check_weather(payload)
