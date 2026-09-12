import sys, json, tempfile, urllib.request, time
from pathlib import Path
from copy import deepcopy
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
out={}
for label,base in [('public','https://veil-network-intel.vercel.app'),('isolated_local','http://127.0.0.1:8002')]:
    out[label]={}
    for endpoint in ['/api/cases/demo','/api/cases/demo/ner-status','/api/cases/demo/processing-summary','/api/cases/demo/anomalies']:
        start=time.perf_counter()
        try:
            with urllib.request.urlopen(base+endpoint,timeout=45) as r: data=json.load(r)
            if endpoint.endswith('anomalies'):data={k:data[k] for k in ['status','sample_size','generated_at']}
            out[label][endpoint]={'data':data,'single_request_seconds':round(time.perf_counter()-start,3)}
        except Exception as e:out[label][endpoint]={'error':str(e)}
from backend.demo_repository import DemoRepository
from backend.demo_paths import compute_path
from backend.resolution import proposals
from backend.lead_engine import run_engine
from backend.intake_store import IntakeStore
from backend.intake_models import UploadSource
from backend import ner_service
r=DemoRepository();p=compute_path(r,r.case.source_default,r.case.target_default,8)
out['baseline']={'entities':len(r.entities),'relationships':len(r.relationships),'events':len(r.events),'leads':len(run_engine(r).leads),'path':p.node_ids,'relationship_ids':p.relationship_ids,'resolution_proposals':list(proposals(r))}
noevents=deepcopy(r);noevents.events={}
out['without_events_leads']=len(run_engine(noevents).leads)
cut=deepcopy(r)
first=p.relationships[0];cut.relationships={k:v for k,v in cut.relationships.items() if {v.source,v.target}!={first.source,first.target}}
newpath=compute_path(cut,cut.case.source_default,cut.case.target_default,8)
out['cut_first_path_edge']=None if newpath is None else newpath.node_ids
with tempfile.TemporaryDirectory(prefix='ni-audit-',ignore_cleanup_errors=True) as tmp:
    store=IntakeStore(Path(tmp)/'in.sqlite3')
    for filename,content in [('alias-a.txt','Rahul Sharma uses phone +910000009999.\n'),('alias-b.txt','R.K. Sharma uses phone +910000009999.\n')]:
        store.upload(UploadSource(filename=filename,source_type='Report',content=content))
    summary=store.process();aug=store.augment(r)
    initial=set(proposals(r));updated=set(proposals(aug))
    out['fresh_alias_probe']={'records':summary.records_processed,'mentions':summary.entity_mentions,'added_persons':[n.label for k,n in aug.entities.items() if k not in r.entities and n.type=='Person'],'baseline_proposals':len(initial),'recomputed_proposals':len(updated),'new_proposals':sorted(updated-initial),'api_behavior':'main.matches computed once at startup over baseline, not updated by process_sources'}
with tempfile.TemporaryDirectory(prefix='ni-audit-',ignore_cleanup_errors=True) as tmp:
    store=IntakeStore(Path(tmp)/'in.sqlite3')
    text='Rahul Sharma uses phone +910000009991.\nRahul Sharma can be reached on +910000009992.\nRahul Sharma did not meet Vikram Singh on 12 August 2026.\nRahul Sharma met Vikram Singh on 12 September 2026.\n'
    store.upload(UploadSource(filename='grammar.txt',source_type='Report',content=text));store.process();state=store.read()
    out['grammar_probe']=[{'raw':next(r['raw_excerpt'] for r in state['records'] if r['record_id']==c['record_id']),'relationship':c['relationship_type'],'disposition':c['disposition']} for c in state['claims']]
with tempfile.TemporaryDirectory(prefix='ni-audit-',ignore_cleanup_errors=True) as tmp:
    store=IntakeStore(Path(tmp)/'in.sqlite3')
    text='call_id,caller_phone,receiver_phone,started_at,duration_seconds,tower_location\nCALL-AUDIT,+910000009991,+910000009992,2026-08-15T10:00:00+05:30,10,Mumbai\n'
    store.upload(UploadSource(filename='outside-dictionary.csv',source_type='CDR',content=text));summ=store.process()
    out['ordinary_location_probe']={'valid':summ.valid_records,'rejected':summ.rejected_records,'errors':[r['validation_errors'] for r in store.read()['records']]}
out['local_ner_available']=ner_service.is_available()
Path(__file__).with_name('probe-results.json').write_text(json.dumps(out,indent=2,default=str),encoding='utf-8')
print(json.dumps(out,indent=2,default=str))

