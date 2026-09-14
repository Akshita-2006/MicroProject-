import unittest
import pandas as pd
from src.analysis.reassess_stations import assess


class StationExpansion(unittest.TestCase):
    def test_later_archive_start_and_future_independence(self):
        history = pd.DataFrame({'station_name':' Example ',
                                'timestamp':pd.date_range('2019-01-01','2021-12-31 23:00',freq='h'),
                                'aqi':100})
        baseline = assess(history)
        self.assertTrue(baseline.coverage_candidate.iloc[0])
        self.assertEqual(baseline.station.iloc[0], 'Example')
        self.assertEqual(baseline.active_archive_coverage_pct.iloc[0],100)
        future = pd.DataFrame({'station_name':['Example']*2,'timestamp':['2025-01-01']*2,'aqi':[10,500]})
        pd.testing.assert_frame_equal(baseline,assess(pd.concat([history,future])))

    def test_conflicting_training_record_rejects_candidate(self):
        history = pd.DataFrame({'station_name':'Example',
                                'timestamp':pd.date_range('2019-01-01','2021-12-31 23:00',freq='h'),
                                'aqi':100})
        conflict = history.iloc[[0]].assign(aqi=200)
        result = assess(pd.concat([history,conflict]))
        self.assertFalse(result.coverage_candidate.iloc[0])
        self.assertEqual(result.training_conflicts.iloc[0],1)
