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
