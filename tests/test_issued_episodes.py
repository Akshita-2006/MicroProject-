import unittest
import pandas as pd
import numpy as np
from src.evaluation.issued_episodes import evaluate_windows, summarize


class IssuedEpisodes(unittest.TestCase):
    def window(self,issued,actual,prediction):
        return pd.DataFrame(dict(station_name='test',timestamp=pd.Timestamp(issued),
                                 target_time=pd.date_range(pd.Timestamp(issued)+pd.Timedelta(hours=1),periods=24,freq='h'),
                                 actual=actual,prediction=prediction))

    def test_timing_has_known_error_and_correct_denominator(self):
        actual=[100]*4+[350]*5+[100]*15
        pred=[100]*6+[350]*5+[100]*13
        w,m,e=evaluate_windows(self.window('2023-01-01',actual,pred))
        row=summarize(w).query("station == 'ALL'").iloc[0]
        self.assertEqual(row.onset_error_hours,2)
        self.assertEqual(row.recovery_error_hours,2)
        self.assertEqual(row.duration_error_hours,0)
        self.assertEqual(row.onset_error_hours_n,1)
        self.assertEqual(m.actual_onset_lead_hours.iloc[0],5)
        self.assertEqual(len(e),0)

    def test_adjacent_windows_do_not_create_spurious_event(self):
        first=[100]*22+[350]*2
        second=[350]*2+[100]*22
        data=pd.concat([self.window('2023-01-01',first,first),self.window('2023-01-02',second,second)])
        w,m,e=evaluate_windows(data)
        self.assertEqual(w.actual_events.sum(),0)
        self.assertEqual(len(m),0)

    def test_missing_truth_excluded(self):
        actual=[350]*24
        actual[10]=np.nan
        w,m,e=evaluate_windows(self.window('2023-01-01',actual,[350]*24))
        self.assertTrue(w.empty)
        self.assertEqual(e.reason.iloc[0],'missing_truth_or_prediction')
