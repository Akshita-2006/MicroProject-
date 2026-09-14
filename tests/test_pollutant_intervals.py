import unittest
import pandas as pd
from src.preprocessing.pollutant_intervals import hourly_from_start_labels


class PollutantIntervals(unittest.TestCase):
    def sample(self):
        return pd.DataFrame({'Station ID':'a','Station Name':'Example',
            'Timestamp':pd.date_range('2025-01-01',periods=8,freq='15min',tz='UTC'),
            'PM':[10.,20.,30.,40.,100.,200.,300.,400.]})

    def test_end_boundary_and_future_independence(self):
        frame=self.sample()
        original=hourly_from_start_labels(frame,['PM'],source_clock_timezone='Asia/Kolkata')
        self.assertEqual(original.PM.iloc[0],25)
        self.assertEqual(original.interval_end.iloc[0],pd.Timestamp('2025-01-01 01:00',tz='Asia/Kolkata'))
        frame.loc[4:,'PM']=9999
        changed=hourly_from_start_labels(frame,['PM'],source_clock_timezone='Asia/Kolkata')
        self.assertEqual(changed.PM.iloc[0],original.PM.iloc[0])

    def test_missing_quarters_and_publication_delay(self):
        frame=self.sample().drop(index=[0,1])
        result=hourly_from_start_labels(frame,['PM'],source_clock_timezone='Asia/Kolkata',publication_delay_minutes=30)
        self.assertTrue(pd.isna(result.PM.iloc[0]))
        self.assertEqual(result['PM__quarters'].iloc[0],2)
        self.assertEqual(result.available_at.iloc[0]-result.interval_end.iloc[0],pd.Timedelta(minutes=30))

    def test_ambiguous_input_rejected(self):
        frame=self.sample()
        with self.assertRaises(ValueError):
            hourly_from_start_labels(frame,['PM'],source_clock_timezone=None)
        with self.assertRaises(ValueError):
            hourly_from_start_labels(pd.concat([frame,frame.iloc[[0]]]),['PM'],source_clock_timezone='Asia/Kolkata')
