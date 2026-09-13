import unittest
import numpy as np
import pandas as pd
from src.features.hourly import build, split_masks, WEATHER
from src.episode_detection.timeline import extract, evaluate, category


class TemporalContracts(unittest.TestCase):
    def series(self, values):
        return pd.Series(values,index=pd.date_range('2023-01-01',periods=len(values),freq='h'))

    def test_gaps_are_not_recovery(self):
        e = extract(self.series([310,320,330,np.nan,340,350,360,200]))
        self.assertEqual(len(e),2)
        self.assertIsNone(e[0].recovery)
        self.assertTrue(e[1].left_censored)
        self.assertEqual(e[1].duration_hours,3)

    def test_spike_and_censoring(self):
        self.assertEqual(extract(self.series([100,400,100])),[])
        e = extract(self.series([100,310,420,350]))[0]
        self.assertTrue(e.right_censored)
        self.assertEqual(e.severity,'Severe')
        self.assertEqual(category(358),'Very Poor')

    def test_no_multiple_credit(self):
        actual = self.series([100,320,320,320,100,320,320,320,100])
        pred = self.series([100,320,320,320,320,320,320,320,100])
        scores,_ = evaluate(actual,pred)
        self.assertEqual(scores['matched_events'],1)
        self.assertEqual(scores['missed_events'],1)

    def test_future_perturbation(self):
        df = pd.DataFrame({'timestamp':pd.date_range('2021-12-28',periods=150,freq='h'),'aqi':np.arange(150.),'wind_direction_10m':90.})
        for w in WEATHER:
            df[w] = 1.
        x,_ = build(df)
        df.loc[101:,'aqi'] = 999.
        z,_ = build(df)
        pd.testing.assert_frame_equal(x.iloc[:101],z.iloc[:101])
        with self.assertRaises(ValueError):
            build(df.drop(index=2))

    def test_boundary_purge(self):
        t = pd.Series(pd.date_range('2021-12-31',periods=48,freq='h'))
        masks = split_masks(t,24)
        self.assertEqual(int(masks['train'].sum()),0)


if __name__ == '__main__':
    unittest.main()
