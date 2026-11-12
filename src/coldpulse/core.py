"""Offline analysis of synthetic sensor CSV. This is NOT an equipment controller."""
import csv
from pathlib import Path

def analyze(path, min_consecutive=1):
    """Validate offline telemetry and flag sustained threshold deviations.

    Rows must be in acquisition order per sensor. No automation or physical control.
    """
    import math
    if not isinstance(min_consecutive, int) or not 1 <= min_consecutive <= 1000:
        raise ValueError('min_consecutive must be between 1 and 1000')
    alerts=[]; total=0; runs={}
    with open(path, newline='', encoding='utf-8') as f:
        reader=csv.DictReader(f)
        required={'timestamp','sensor_id','temperature_c','lower_c','upper_c'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('CSV missing required headers')
        for row in reader:
            total+=1
            value=float(row['temperature_c']); low=float(row['lower_c']); high=float(row['upper_c'])
            if not all(math.isfinite(x) for x in (value, low, high)) or low>high:
                raise ValueError('Invalid or non-finite sensor reading/bounds')
            sensor=row['sensor_id']
            condition='below' if value<low else 'above' if value>high else None
            previous, length=runs.get(sensor,(None,0))
            length=length+1 if condition is not None and condition==previous else (1 if condition else 0)
            runs[sensor]=(condition,length)
            if condition and (min_consecutive==1 or length==min_consecutive):
                alerts.append({'timestamp':row['timestamp'],'sensor_id':sensor,'value_c':value,
                               'condition': condition,'consecutive_samples':length})
    return {'samples':total,'alerts':alerts,'min_consecutive':min_consecutive,
            'warning':'Demonstration only; not for controlling physical equipment.'}

def configure(sub):
    p=sub.add_parser('analyze',help='Analyze CSV readings')
    p.add_argument('path')
    p.add_argument('--min-consecutive', type=int, default=1, help='Alert only after N consecutive out-of-range readings per sensor')

def run(args):
    return analyze(args.path, args.min_consecutive)

def demo():
    return analyze(Path(__file__).resolve().parents[2]/'samples'/'telemetry.csv')
