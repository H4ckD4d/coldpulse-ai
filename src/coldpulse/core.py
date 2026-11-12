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
    s=sub.add_parser('summary',help='Per-sensor offline statistics')
    s.add_argument('path')

def run(args):
    return summarize(args.path) if args.command=='summary' else analyze(args.path, args.min_consecutive)

def demo():
    return analyze(Path(__file__).resolve().parents[2]/'samples'/'telemetry.csv')


def summarize(path):
    """Offline descriptive sensor statistics. Never controls equipment."""
    import math
    summary={}
    with open(path,newline='',encoding='utf-8') as stream:
        reader=csv.DictReader(stream)
        if not {'sensor_id','temperature_c'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV missing required headers')
        for row in reader:
            sensor=row['sensor_id']
            if not sensor: raise ValueError('Missing sensor ID')
            value=float(row['temperature_c'])
            if not math.isfinite(value): raise ValueError('Non-finite value')
            item=summary.setdefault(sensor,{'count':0,'sum':0.0,'min':value,'max':value})
            item['count']+=1;item['sum']+=value
            item['min']=min(item['min'],value);item['max']=max(item['max'],value)
    return {'sensors':{k:{'samples':v['count'],'mean_c':round(v['sum']/v['count'],3),
                          'min_c':v['min'],'max_c':v['max']} for k,v in sorted(summary.items())},
            'warning':'Offline statistics only; not for controlling physical equipment.'}
