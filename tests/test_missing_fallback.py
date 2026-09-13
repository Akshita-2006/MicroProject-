from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from src.forecasting.service import forecast

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless((ROOT/'experiments/results/combined_system/complete.json').exists(),'Combined evaluation not ready')
class MissingFallback(unittest.TestCase):
    def test_fallback_replay_matches_saved_trajectory(self):
        trajectory=pd.read_parquet(ROOT/'experiments/results/missing_history_fallback/daily_trajectories.parquet')
        station=trajectory.station_name.iloc[0]
        issued=trajectory[trajectory.station_name==station].timestamp.min()
        expected=trajectory[(trajectory.station_name==station)&(trajectory.timestamp==issued)].sort_values('horizon')
        panel=pd.read_parquet(ROOT/'data/processed/delhi_hourly_v2.parquet')
        history=panel[panel.station_name==station].copy()
        got=forecast(history,issued)
        self.assertTrue(got.route.eq('missing_history_fallback').all())
        np.testing.assert_allclose(got.prediction,expected.prediction,rtol=1e-6)
        np.testing.assert_allclose(got.lower,expected.lower,rtol=1e-6)
        history.loc[history.timestamp>issued,'aqi']=500
        future_changed=forecast(history,issued)
        np.testing.assert_array_equal(got.prediction,future_changed.prediction)

    def test_no_overlap_between_forecast_routes(self):
        combined=pd.read_parquet(ROOT/'experiments/results/combined_system/test_predictions.parquet')
        self.assertFalse(combined.duplicated(['station_name','timestamp','horizon']).any())
        self.assertEqual(set(combined.route),{'complete_history','missing_history_fallback'})
