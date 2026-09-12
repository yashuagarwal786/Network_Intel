"""Export real API responses for an offline judge fallback; never used as UI fallbacks."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://127.0.0.1:8000');p.add_argument('--output',default='artifacts/sample-api');args=p.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    routes={'case':'/api/cases/demo','sources':'/api/cases/demo/processing-summary','graph':'/api/cases/demo/graph','path':'/api/cases/demo/path?source=rahul&target=vikram','lead-17':'/api/leads/17','evidence':'/api/evidence/E-TX-01','resolution':'/api/cases/demo/resolution-proposals','reviews':'/api/leads/17/reviews','audit':'/api/cases/demo/audit','timeline':'/api/cases/demo/timeline'}
    for name,route in routes.items():
        with urlopen(args.base_url+route,timeout=15) as response:data=json.load(response)
        (output/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Exported {len(routes)} actual API responses to {output.resolve()}')
