"""Author deterministic validation variants, then evaluate against external labels."""
from copy import deepcopy
from collections import Counter
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
from .demo_repository import DemoRepository
from .demo_schemas import Event, Evidence
from .lead_engine import run_engine, traceable

ROOT=Path(__file__).resolve().parents[1]/'demo-data'/'temporal-validation'

def add_call(repo,id,phone,target,stamp,sid,row,relationship=None,context='Synthetic routine contact'):
    eid='E-'+id
    source=repo.sources[sid]
    template=next(e for e in repo.evidence.values() if e.source_id==sid)
    repo.evidence[eid]=template.model_copy(deep=True,update={'id':eid,'timestamp':stamp,'exact_excerpt':f'{context}: {phone} -> {target}; {stamp.isoformat()}; connected call, 60 seconds.','entity_ids':[phone,target],'relationship_ids':[relationship] if relationship else [],'locator':template.locator.model_copy(update={'row':row})})
    source.evidence_ids.append(eid)
    for n in [phone,target]:repo.entities[n].evidence_ids.append(eid)
    event_id='EV-'+id
    repo.events[event_id]=Event(id=event_id,type='call',timestamp=stamp,entity_ids=[phone,target],evidence_ids=[eid],relationship_ids=[relationship] if relationship else [],duration_seconds=60)
    if relationship:
        repo.relationships[relationship].evidence_ids.append(eid);repo.relationships[relationship].event_ids.append(event_id)

def make_dataset(name):
    repo=DemoRepository()
    if name=='alternate_seed_22':
        for e in repo.events.values():e.timestamp+=timedelta(days=7)
        for e in repo.evidence.values():
            old=e.timestamp;e.timestamp+=timedelta(days=7)
            e.exact_excerpt=e.exact_excerpt.replace(old.isoformat(),e.timestamp.isoformat())
        repo.case.event_timestamp+=timedelta(days=7)
        for sid in ['S02','S03','S05']:
            repo.sources[sid].filename='validation-22-'+repo.sources[sid].filename.replace('08-08-to-08-14','08-15-to-08-21').replace('2026-08-15','2026-08-22')
            repo.sources[sid].description='Deterministic alternate-seed source records; see rows for actual counts and amounts.'
            for e in repo.evidence.values():
                if e.source_id==sid:e.source_filename=repo.sources[sid].filename
        for e in repo.evidence.values():e.exact_excerpt=e.exact_excerpt.replace('15 August 2026','22 August 2026')
        start=repo.case.event_timestamp.replace(hour=10,minute=0,second=0)-timedelta(days=7)
        row=16
        for i,count in enumerate([3,2,3,4,3,2,4]):
            for j in range(count-2):
                add_call(repo,f'ALT-BASE-{i}-{j}','P101','P305',start+timedelta(days=i,minutes=20+j),'S02',row);row+=1
        for i in range(3):add_call(repo,f'ALT-DAY-{i}','P101','P204',repo.case.event_timestamp.replace(hour=18,minute=44+i*4),'S03',13+i,'R02')
        tx=sorted((e for e in repo.events.values() if e.type=='transfer'),key=lambda e:e.timestamp)
        for i,(e,amount) in enumerate(zip(tx,[40000,30000,20000])):
            e.amount_inr=Decimal(amount)
            if i==2:e.timestamp+=timedelta(minutes=5)
            for eid in e.evidence_ids:
                source=repo.evidence[eid];source.timestamp=e.timestamp;source.exact_excerpt=f'{e.entity_ids[0]} -> {e.entity_ids[1]}; INR {amount}; {e.timestamp.isoformat()}; synthetic alternate-seed transfer.'
    # Explicit benign communication outlier: routine service checks, no financial overlap.
    start=repo.case.event_timestamp.replace(hour=10,minute=0,second=0)-timedelta(days=7)
    for i in range(7):
        for j in range(2):add_call(repo,f'BENIGN-BASE-{i}-{j}','P314','P313',start+timedelta(days=i,minutes=j),'S02',100+i*2+j)
    for i in range(12):add_call(repo,f'BENIGN-DAY-{i}','P314','P313',repo.case.event_timestamp.replace(hour=12,minute=i),'S03',100+i,context='Labelled benign synthetic service-status check')
    if name=='benign_only':
        removed_events={e.id for e in repo.events.values() if e.type=='transfer'}
        removed_evidence={id for e in repo.events.values() if e.id in removed_events for id in e.evidence_ids}
        repo.events={id:e for id,e in repo.events.items() if id not in removed_events}
        repo.evidence={id:e for id,e in repo.evidence.items() if id not in removed_evidence}
        for r in repo.relationships.values():
            r.event_ids=[id for id in r.event_ids if id not in removed_events];r.evidence_ids=[id for id in r.evidence_ids if id not in removed_evidence]
        repo.relationships={id:r for id,r in repo.relationships.items() if r.evidence_ids}
        for e in repo.evidence.values():e.relationship_ids=[id for id in e.relationship_ids if id in repo.relationships]
        for owner in list(repo.entities.values())+list(repo.sources.values()):owner.evidence_ids=[id for id in owner.evidence_ids if id not in removed_evidence]
        repo.sources={id:s for id,s in repo.sources.items() if s.evidence_ids}
    return repo

def write_dataset(repo,target):
    target.mkdir(parents=True,exist_ok=True)
    for name in ['entities','relationships','events','evidence','sources']:
        content={'schema_version':1,'case_id':repo.case.id,'synthetic':True,'data_version':'golden-v1','items':[x.model_dump(mode='json') for x in getattr(repo,name).values()]}
        if name=='entities':content['case']=repo.case.model_dump(mode='json')
        (target/(name+'.json')).write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def evaluate():
    truth=json.loads((ROOT/'ground-truth.json').read_text(encoding='utf-8'));results=[]
    for spec in truth['datasets']:
        repo=DemoRepository(ROOT/spec['dataset']);output=run_engine(repo);expected=spec['expected_signals']
        found=sum(any(s.signal_type==item['type'] and item['entity'] in s.involved_entity_ids and all(s.observed_value.get(k)==v for k,v in item.get('observed',{}).items()) for s in output.signals) for item in expected)
        actual=Counter((next(s.involved_entity_ids[0] for s in l.signals if s.signal_type=='COMMUNICATION_BURST'),l.review_priority) for l in output.leads)
        wanted=Counter((x['phone'],x['priority']) for x in spec['expected_leads'])
        refs=sorted({id for s in output.signals for id in s.supporting_evidence_ids}|{id for l in output.leads for id in l.evidence_ids})
        results.append({'dataset':spec['dataset'],'planted_signals_found':found,'planted_signals_expected':len(expected),'planted_signal_recall':found/len(expected) if expected else None,'false_leads':sum((actual-wanted).values()),'missing_expected_leads':sum((wanted-actual).values()),'evidence_references_checked':len(refs),'evidence_trace_coverage':sum(traceable(repo,[id]) for id in refs)/len(refs) if refs else 1.0,'expected_priority_result':actual==wanted,'deterministic_repeatability':output.model_dump_json()==run_engine(repo).model_dump_json(),'benign_non_leads_preserved':all(not any(n['entity'] in l.involved_entity_ids for l in output.leads) for n in spec['expected_non_leads'])})
    return {'scope':'Labelled synthetic validation only; not real-world accuracy. Fixed rules, not calibrated probabilities.','engine_version':output.engine_version,'results':results}

if __name__=='__main__':
    for name in ['primary_with_benign','alternate_seed_22','benign_only']:write_dataset(make_dataset(name),ROOT/name)
    result=evaluate();out=Path(__file__).resolve().parents[1]/'artifacts'/'cycle4'/'evaluation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
