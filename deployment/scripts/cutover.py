#!/usr/bin/env python3
"""Read-only snapshot reconciliation, stop gate on duplicate/missing/changed keys."""
import json,pathlib,sys
FIELDS={'vin','site_id','partner_id','location_id','state','version'}
def load(path):
    values=json.loads(pathlib.Path(path).read_text())
    if not isinstance(values,list) or not values:raise ValueError('Snapshot must be nonempty list')
    result={}
    for row in values:
        if not isinstance(row,dict) or set(row)!=FIELDS or not isinstance(row['vin'],str) or not isinstance(row['version'],int):raise ValueError('Snapshot shape invalid')
        if row['vin'] in result:raise ValueError('Duplicate vehicle key')
        result[row['vin']]=row
    return result
def compare(source,target):
    differences=[]
    for key in sorted(set(source)|set(target)):
        if source.get(key)!=target.get(key):differences.append(dict(vin=key,source=source.get(key),target=target.get(key)))
    return differences
if __name__=='__main__':
    try:
        if len(sys.argv)!=3:raise ValueError('cutover.py source.json target.json')
        diff=compare(load(sys.argv[1]),load(sys.argv[2]));print(json.dumps(dict(go='NO_GO' if diff else 'GO_LAB',differences=diff,simulation=True),indent=2));sys.exit(2 if diff else 0)
    except (OSError,ValueError) as e:print(json.dumps(dict(go='NO_GO',error=str(e),simulation=True)));sys.exit(2)
