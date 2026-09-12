"""Author deterministic fictional records. No extraction or lead detection."""
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).with_name('data') / 'demo'


def generate():
    entities, relationships, evidence, sources, events = [], [], [], [], []
    people = [('rahul', 'Rahul Kumar Sharma'), ('amit', 'Amit Verma'), ('vikram', 'Vikram Singh'),
              ('neha', 'Neha Kapoor'), ('arjun', 'Arjun Mehta'), ('sana', 'Sana Iqbal'),
              ('dev', 'Dev Malhotra'), ('priya', 'Priya Nair'), ('kabir', 'Kabir Joshi'), ('meera', 'Meera Das')]
    phones = ['P101', 'P204', 'P305', 'P306', 'P307', 'P308', 'P309', 'P310', 'P311', 'P312', 'P313', 'P314']
    accounts = ['A17', 'A31', 'A44', 'A52', 'A63', 'A74', 'A85', 'A96']
    for i, (eid, name) in enumerate(people):
        entities.append(dict(id=eid, label=name, display_label='Rahul Sharma' if eid=='rahul' else name,
                             type='Person', identifier='DEMO-PER-'+str(i+1).zfill(2), description='Fictional person listed in authorized demonstration records.', x=(i%5)*170, y=(i//5)*210, evidence_ids=[]))
    for i, eid in enumerate(phones):
        entities.append(dict(id=eid, label='Phone '+eid, display_label=eid, type='Phone',
                             identifier=f'+91 DEMO {1000+i:04d} (non-dialable)', description='Synthetic phone number. Association does not establish who made a call.', x=(i%6)*145, y=480+(i//6)*200, evidence_ids=[]))
    for i, eid in enumerate(accounts):
        entities.append(dict(id=eid, label='Account '+eid, display_label=eid, type='Account', identifier='DEMO-BANK-'+eid,
                             description='Synthetic bank account. Listed control is a record assertion, not independent verification.', x=(i%4)*240, y=940+(i//4)*200, evidence_ids=[]))
    for kind, items, y in [('Vehicle', [('V01','DEMO-VH-01'),('V02','DEMO-VH-02'),('V03','DEMO-VH-03')],1380),
                           ('Location',[('L01','Rivergate depot'),('L02','East market'),('L03','Canal junction'),('L04','North yard')],1580),
                           ('Organization',[('O01','Mira Logistics'),('O02','Northline Trading'),('O03','Cedar Services')],1780)]:
        for i,(eid,name) in enumerate(items):
            entities.append(dict(id=eid,label=name,display_label=name,type=kind,identifier=eid,
                                 description='Fictional '+kind.lower()+' record. No real-world allegation.',x=i*240,y=y,evidence_ids=[]))
    def src(sid,filename,kind,description):
        sources.append(dict(id=sid,filename=filename,type=kind,description=description,representation='canonical_synthetic_records',evidence_ids=[]))
    src('S01','subscriber-register.csv','Report','Synthetic phone association records')
    src('S02','cdr-baseline-08-08-to-08-14.csv','CDR','Seven complete baseline days; two calls each day')
    src('S03','cdr-event-2026-08-15.csv','CDR','Eleven calls on the selected activity day')
    src('S04','account-control-register.csv','Transaction','Synthetic account control assertions')
    src('S05','transactions-2026-08-15.csv','Transaction','Three transfers within ninety minutes')
    src('S06','event-x-report.txt','Report','Fictional report sentence and report timestamp')
    src('S07','vehicle-register.csv','Vehicle','Synthetic keeper and location observations')
    src('S08','context-register.txt','Report','Supporting fictional organization and location links')
    def ev(eid,sid,row,text,entity_ids,timestamp='2026-08-14T09:00:00+05:30',fields=None,paragraph=None):
        source=next(s for s in sources if s['id']==sid)
        item=dict(id=eid,source_id=sid,source_filename=source['filename'],source_type=source['type'],
                  locator=dict(row=row,page=1 if paragraph else None,paragraph=paragraph,fields=fields or ['record']),
                  timestamp=timestamp,exact_excerpt=text,verification_status='Synthetic source record · not independently verified',
                  entity_ids=entity_ids,relationship_ids=[])
        evidence.append(item);source['evidence_ids'].append(eid)
        for entity in entities:
            if entity['id'] in entity_ids: entity['evidence_ids'].append(eid)
        return eid
    def rel(rid,a,b,kind,eids):
        relationships.append(dict(id=rid,source=a,target=b,type=kind,status='recorded',evidence_ids=eids,event_ids=[]))
        for item in evidence:
            if item['id'] in eids:item['relationship_ids'].append(rid)
    def event(eid,kind,time,ids,eids,rids,amount=None,duration=None):
        events.append(dict(id=eid,type=kind,timestamp=time,entity_ids=ids,evidence_ids=eids,relationship_ids=rids,amount_inr=amount,duration_seconds=duration))
        for r in relationships:
            if r['id'] in rids:r['event_ids'].append(eid)
    # Backbone and branches. No fixture contains a precomputed path response.
    mappings=[('rahul','P101'),('amit','P204'),('neha','P305'),('arjun','P306'),('sana','P307'),('dev','P308'),('priya','P309'),('kabir','P310'),('meera','P311'),('vikram','P312')]
    for i,(person,phone) in enumerate(mappings):
        eid=f'E-SUB-{i+1:02d}';ev(eid,'S01',i+2,f'{person}: listed user of synthetic phone {phone}; independently verified identity unavailable.',[person,phone],fields=['person','phone'])
        if person=='amit':rel('R03',phone,person,'USED_BY',[eid])
        else:rel('R01' if person=='rahul' else f'R-SUB-{i+1:02d}',person,phone,'USES',[eid])
    controls=[('amit','A17'),('vikram','A31'),('vikram','A44'),('neha','A52'),('arjun','A63'),('sana','A74'),('dev','A85'),('priya','A96')]
    for i,(person,account) in enumerate(controls):
        eid=f'E-ACC-{i+1:02d}';ev(eid,'S04',i+2,f'Account {account}: listed controller {person}; this is a synthetic register assertion.',[person,account],fields=['account','listed_controller'])
        if account=='A31':rel('R06',account,person,'CONTROLLED_BY',[eid])
        else:rel('R04' if account=='A17' else f'R-ACC-{i+1:02d}',person,account,'CONTROLS',[eid])
    baseline_ids=[]
    for day in range(8,15):
        for i,target in enumerate(['P204','P313']):
            eid=f'E-BASE-{day:02d}-{i}';time=f'2026-08-{day:02d}T10:{i*10:02d}:00+05:30'
            baseline_ids.append(ev(eid,'S02',(day-8)*2+i+2,f'P101 → {target}; {time}; connected call; duration 60 seconds.', ['P101',target],time,['caller','callee','start','duration_seconds']))
            event('EV-'+eid,'call',time,['P101',target],[eid],[],duration=60)
    call_ids=[]
    targets=['P204','P204','P204','P305','P306','P307','P308','P309','P310','P311','P313']
    for i,target in enumerate(targets):
        time=(datetime.fromisoformat('2026-08-15T18:00:00+05:30')+timedelta(minutes=i*4)).isoformat()
        eid=f'E-CDR-{i+1:02d}';call_ids.append(ev(eid,'S03',i+2,f'P101 → {target}; {time}; connected call; duration {60+i*5} seconds. Call content unavailable.', ['P101',target],time,['caller','callee','start','duration_seconds']))
    for i,target in enumerate(dict.fromkeys(targets)):
        eids=[eid for eid,t in zip(call_ids,targets) if t==target]
        rel('R02' if target=='P204' else 'R-CALL-'+target,'P101',target,'CALLED',eids)
    for i,(eid,target) in enumerate(zip(call_ids,targets)):
        rid='R02' if target=='P204' else 'R-CALL-'+target
        event('EV-'+eid,'call',evidence[next(j for j,e in enumerate(evidence) if e['id']==eid)]['timestamp'],['P101',target],[eid],[rid],duration=60+i*5)
    for i,(a,b,amount,time,rid) in enumerate([('A17','A31',75000,'18:35','R05'),('A17','A44',60000,'19:10','R-TX-2'),('A44','A31',60000,'19:50','R-TX-3')]):
        timestamp=f'2026-08-15T{time}:00+05:30';eid=f'E-TX-{i+1:02d}'
        ev(eid,'S05',i+2,f'{a} → {b}; INR {amount:,}; {timestamp}; purpose unspecified.',[a,b],timestamp,['sender','receiver','amount_inr','timestamp'])
        rel(rid,a,b,'TRANSFERRED_TO',[eid]);event('EV-'+eid,'transfer',timestamp,[a,b],[eid],[rid],amount=amount)
    extras=[('R-V1','neha','V01','REGISTERED_KEEPER','S07'),('R-V2','kabir','V02','REGISTERED_KEEPER','S07'),('R-V3','meera','V03','REGISTERED_KEEPER','S07'),('R-V4','V01','L01','OBSERVED_AT','S07'),('R-C1','O01','L01','LISTED_AT','S08'),('R-C2','neha','O01','LISTED_CONTACT','S08'),('R-C3','arjun','O02','LISTED_CONTACT','S08'),('R-C4','O02','L02','LISTED_AT','S08'),('R-C5','O03','L03','LISTED_AT','S08'),('R-C6','P314','L04','LISTED_AT','S08')]
    for i,(rid,a,b,kind,sid) in enumerate(extras):
        eid=f'E-CTX-{i+1:02d}';ev(eid,sid,i+2,f'{a} → {b}; {kind}. Synthetic record only; occupants and real-world involvement are unknown.',[a,b],fields=['subject','relationship','object'])
        rel(rid,a,b,kind,[eid])
    ev('E-REPORT-01','S06',None,'Event X: a fictional delivery discrepancy was reported near Rivergate depot at 20:00 IST on 15 August 2026. This report does not establish an offence or identify responsible persons.',['L01'],'2026-08-15T20:00:00+05:30',['sentence'],paragraph=3)
    event('EV-REPORT-01','report','2026-08-15T20:00:00+05:30',['L01'],['E-REPORT-01'],[])
    focus=['rahul','P101','P204','amit','A17','A31','vikram','A44','P305','neha','P306','arjun','V01','L01','O01']
    # Deterministic focused display coordinates; graph traversal never reads these.
    positions={'rahul':(40,85),'P101':(215,85),'P204':(390,85),'amit':(565,85),
               'A17':(565,245),'A31':(390,245),'vikram':(215,245),'A44':(665,280),
               'P305':(20,450),'neha':(125,450),'P306':(230,450),'arjun':(335,450),
               'V01':(440,450),'L01':(545,450),'O01':(650,450)}
    for n in entities:
        if n['id'] in positions:n['x'],n['y']=positions[n['id']]
    # Context entries use a separate overview layout generated by the frontend grid;
    # that layout is presentation-only and does not calculate analytical results.
    case=dict(id='VEIL-DEMO-001',name='Reference Investigation',classification='Synthetic Demonstration',status='Active Review',timezone='Asia/Kolkata',description='Fictional investigation workspace · leads, not accusations.',event_label='Event X',event_timestamp='2026-08-15T20:00:00+05:30',source_default='rahul',target_default='vikram',focus_entity_ids=focus,max_depth=8)
    from .resolution_fixtures import extend
    extend(entities, relationships, evidence, sources, focus)
    return {'entities':dict(case=case,items=entities),'relationships':dict(items=relationships),'events':dict(items=events),'leads':dict(items=[]),'evidence':dict(items=evidence),'sources':dict(items=sources)}


if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    for name,content in generate().items():
        envelope=dict(schema_version=1,case_id='VEIL-DEMO-001',synthetic=True,data_version='golden-v1',**content)
        (ROOT/(name+'.json')).write_text(json.dumps(envelope,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

