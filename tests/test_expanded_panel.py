import unittest
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class ExpandedPanel(unittest.TestCase):
    def test_all_eligible_panel_has_regular_station_grids(self):
        path = ROOT / 'data/processed/delhi_hourly_all_eligible.parquet'
        self.assertTrue(path.exists())
        data = pd.read_parquet(path)
        self.assertGreaterEqual(data.station_name.nunique(), 25)
        self.assertEqual(len(data), data.station_name.nunique() * 24 * (365 * 7 + 1))
        for _, group in data.groupby('station_name'):
            self.assertTrue(group.timestamp.sort_values().diff().iloc[1:].eq(pd.Timedelta(hours=1)).all())


if __name__ == '__main__':
    unittest.main()
