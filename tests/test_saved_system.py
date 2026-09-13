"""Integration checks use already trained artifacts; skip before a training run."""
from pathlib import Path
import unittest
import pandas as pd
import numpy as np
from src.forecasting.service import forecast

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless((ROOT/'experiments/results/v2/run_manifest.json').exists(),'Training artifacts not yet available')
class SavedSystem(unittest.TestCase):
    def test_replay_matches_backtest_and_ignores_future(self):
        data = pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet')
        stored = pd.read_parquet(ROOT/'experiments/results/v2/daily_trajectories.parquet')
        station = 'Shadipur Delhi CPCB'
        stored = stored[stored.station_name == station]
        issued = stored.timestamp.min()
        expected = stored[stored.timestamp == issued].sort_values('horizon')
        g = data[data.station_name == station].copy()
        p = forecast(g,issued)
        np.testing.assert_allclose(p.prediction,expected.prediction,rtol=1e-6)
        g.loc[g.timestamp > issued,'aqi'] = 0
        p2 = forecast(g,issued)
        np.testing.assert_allclose(p.prediction,p2.prediction,rtol=0,atol=0)
        self.assertTrue(p.target_time.diff().iloc[1:].eq(pd.Timedelta(hours=1)).all())

    def test_missing_input_abstention(self):
        data = pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet')
        g = data[data.station_name == 'Shadipur Delhi CPCB'].copy()
        issued = pd.Timestamp('2023-11-01 12:00')
        g.loc[g.timestamp == issued,'aqi'] = np.nan
        with self.assertRaises(ValueError):
            forecast(g,issued)


if __name__ == '__main__':
    unittest.main()
