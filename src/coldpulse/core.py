"""Offline analysis of synthetic sensor CSV. This is NOT an equipment controller."""
import csv
from pathlib import Path

def analyze(path):
    alerts=[];total=0
    with open(path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        required={'timestamp','sensor_id','temperature_c','lower_c','upper_c'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('CSV missing required headers')
        for row in reader:
            total+=1
            value=float(row['temperature_c']); low=float(row['lower_c']);high=float(row['upper_c'])
            if low>high:
                raise ValueError('Invalid bounds')
            if not low<=value<=high:
                alerts.append({'timestamp':row['timestamp'],'sensor_id':row['sensor_id'],'value_c':value,
                               'condition': 'below' if value<low else 'above'})
    return {'samples':total,'alerts':alerts,'warning':'Demonstration only; not for controlling physical equipment.'}

def configure(sub):
    p=sub.add_parser('analyze',help='Analyze CSV readings')
    p.add_argument('path')

def run(args):
    return analyze(args.path)

def demo():
    return analyze(Path(__file__).resolve().parents[2]/'samples'/'telemetry.csv')
