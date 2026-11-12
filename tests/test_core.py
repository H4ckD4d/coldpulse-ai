import tempfile, unittest
from pathlib import Path
from coldpulse.core import analyze
class CoreTests(unittest.TestCase):
    def test_alerts_on_out_of_range(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv';p.write_text('timestamp,sensor_id,temperature_c,lower_c,upper_c\nt0,demo,6,0,5\n')
            self.assertEqual(analyze(p)['alerts'][0]['condition'],'above')
    def test_valid_reading_has_no_alerts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv';p.write_text('timestamp,sensor_id,temperature_c,lower_c,upper_c\nt0,demo,3,0,5\n')
            self.assertEqual(analyze(p)['alerts'],[])

    def test_sustained_alert_and_reset(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv'
            p.write_text('timestamp,sensor_id,temperature_c,lower_c,upper_c\n'
                't0,s1,8,0,5\nt1,s2,1,0,5\nt2,s1,9,0,5\n'
                't3,s1,4,0,5\nt4,s1,8,0,5\n')
            result=analyze(p, min_consecutive=2)
            self.assertEqual(len(result['alerts']),1)
            self.assertEqual(result['alerts'][0]['timestamp'],'t2')
    def test_rejects_nan_or_invalid_consecutive(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv';p.write_text('timestamp,sensor_id,temperature_c,lower_c,upper_c\nt0,s1,nan,0,5\n')
            with self.assertRaises(ValueError):
                analyze(p)
            with self.assertRaises(ValueError):
                analyze(p, min_consecutive=0)
