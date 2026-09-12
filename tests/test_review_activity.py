from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from backend import main
from backend.review_store import ReviewStore,ReviewInput
from backend.resolution import ResolutionStore
from backend.intake_store import IntakeStore,SAMPLES

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'resolution_store',ResolutionStore(tmp_path/'resolution.sqlite3'))
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.sqlite3'))
    with TestClient(main.app) as c:yield c

def payload(c,**changes):
    lead=c.get('/api/leads/17').json()['lead']
    return {'reviewer':'Demo investigator','action':'NEEDS_MORE_EVIDENCE','reason':'Request original CDR verification','idempotency_key':'request-0001','lead_revision':lead['lead_revision'],**changes}

def test_review_persists_and_audit_old_new(client):
    body=payload(client)
    response=client.post('/api/leads/17/reviews',json=body);assert response.status_code==200,response.text
    review=response.json()
    assert client.get('/api/leads/17').json()['lead']['review_status']=='NEEDS_MORE_EVIDENCE'
    reopened=ReviewStore(main.review_store.path)
    assert reopened.history('VEIL-DEMO-001','17')[0].review_id==review['review_id']
    event=client.get('/api/cases/demo/audit?action=LEAD_REVIEW_SUBMITTED').json()[0]
    assert event['old_state']['review_status']=='UNREVIEWED'
    assert event['new_state']['review_status']=='NEEDS_MORE_EVIDENCE'
    assert event['actor']==body['reviewer'] and event['reason']==body['reason']
    second={**body,'action':'USEFUL_LEAD','idempotency_key':'request-0002','reason':''}
    assert client.post('/api/leads/17/reviews',json=second).status_code==200
    entries=client.get('/api/cases/demo/audit?action=LEAD_REVIEW_SUBMITTED').json()
    assert entries[0]==event and entries[1]['old_state']['review_status']=='NEEDS_MORE_EVIDENCE'
    assert client.get('/api/leads/17/reviews').json()[0]==review

def test_duplicate_retry_and_conflict(client):
    body=payload(client)
    first=client.post('/api/leads/17/reviews',json=body).json()
    assert client.post('/api/leads/17/reviews',json=body).json()==first
    assert len(client.get('/api/cases/demo/audit?action=LEAD_REVIEW_SUBMITTED').json())==1
    assert client.post('/api/leads/17/reviews',json={**body,'reason':'changed'}).status_code==409
    lead=main.current_lead('17');body2=ReviewInput(**{**body,'idempotency_key':'parallel-key'})
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:main.review_store.submit(lead,body2),range(2)))
    assert results[0].review_id==results[1].review_id

@pytest.mark.parametrize('changes',[{'reviewer':' '},{'action':'GUILTY'},{'idempotency_key':'x'},{'lead_revision':'x'},{'object_id':'rahul'}])
def test_review_validation(client,changes):
    body=payload(client,**changes)
    assert client.post('/api/leads/17/reviews',json=body).status_code==422
    assert not client.get('/api/cases/demo/audit?action=LEAD_REVIEW_SUBMITTED').json()

def test_revision_change_and_unknown_lead(client,monkeypatch):
    body=payload(client)
    assert client.post('/api/leads/17/reviews',json={**body,'lead_revision':'0'*64}).status_code==409
    assert client.post('/api/leads/unknown/reviews',json=body).status_code==404
    client.post('/api/leads/17/reviews',json=body)
    from copy import deepcopy
    changed=deepcopy(main.repository)
    changed.events['EV-E-TX-01'].amount_inr+=1
    monkeypatch.setattr(main,'repository',changed)
    newer=client.get('/api/leads/17').json()['lead']
    assert newer['lead_revision']!=body['lead_revision'] and newer['review_status']=='UNREVIEWED'
    assert len(client.get('/api/leads/17/reviews').json())==1

def test_generation_dedupe_and_evidence_open(client):
    client.get('/api/cases/demo/leads');client.get('/api/cases/demo/leads')
    assert len(client.get('/api/cases/demo/audit?action=LEAD_GENERATED').json())==1
    client.get('/api/evidence/E-TX-01')
    ev=client.get('/api/cases/demo/audit?action=EVIDENCE_OPENED').json()[0]
    assert ev['object_id']=='E-TX-01' and ev['evidence_ids']==['E-TX-01'] and ev['source_types']==['Transaction']
    client.get('/api/evidence/missing')
    assert len(client.get('/api/cases/demo/audit?action=EVIDENCE_OPENED').json())==1

def test_resolution_and_undo_audit(client):
    pid='MP-rahul-rk-sharma';body={'reviewer':'Analyst','reason':'Reviewed identifiers','action':'CONFIRM_MATCH'}
    decision=client.post('/api/resolution-proposals/'+pid+'/decisions',json=body).json()
    rows=client.get('/api/cases/demo/audit?action=ENTITY_RESOLUTION_DECISION').json()
    assert rows[0]['old_state']=={'status':'REVIEW'} and rows[0]['new_state']['status']=='CONFIRMED'
    assert client.post('/api/resolution-decisions/'+decision['decision_id']+'/undo',json={**body,'action':'UNDO_CONFIRMED_MATCH'}).status_code==200
    undo=client.get('/api/cases/demo/audit?action=RESOLUTION_DECISION_UNDONE').json()[0]
    assert undo['old_state']=={'status':'CONFIRMED'} and undo['new_state']['status']=='REVIEW'
    assert len(client.get('/api/cases/demo/audit?action=ENTITY_RESOLUTION_DECISION').json())==1

def test_object_assessments_are_explicit_not_graph_mutations(client):
    body=payload(client,action='VERIFIED_RELATIONSHIP',object_id='R01')
    before=client.get('/api/cases/demo/graph').json()
    assert client.post('/api/leads/17/reviews',json=body).status_code==200
    assert client.get('/api/cases/demo/graph').json()==before
    assert client.post('/api/leads/17/reviews',json={**body,'object_id':'bad','idempotency_key':'object-invalid'}).status_code==422
    pid='MP-rahul-rk-sharma'
    assert client.post('/api/resolution-proposals/'+pid+'/decisions',json={'action':'CONFIRM_MATCH','reviewer':'Analyst','reason':'Reviewed'}).status_code==200
    body=payload(client,action='INCORRECT_ENTITY_MERGE',object_id=pid,idempotency_key='merge-report')
    assert client.post('/api/leads/17/reviews',json=body).status_code==200
    assert client.get('/api/resolution-proposals/'+pid).json()['proposal']['status']=='CONFIRMED'

def test_intake_audit_and_timeline_claims(client):
    reset=client.post('/api/cases/demo/intake/reset',json={'reload_samples':True});assert reset.status_code==200
    assert len(client.get('/api/cases/demo/audit?action=SOURCE_UPLOADED').json())==4
    client.post('/api/cases/demo/process')
    assert len(client.get('/api/cases/demo/audit?action=SOURCE_PROCESSED').json())==4
    timeline=client.get('/api/cases/demo/timeline').json()
    claims=[e for e in timeline if e['category']=='EXTRACTED_CLAIM']
    assert any('NEGATED' in e['title'] and e['timestamp'] is None for e in claims)
    assert any(e['event_type']=='vehicle_observation' and e['timestamp'] for e in claims)
    for item in claims:
        assert item['evidence_ids']
        assert client.get('/api/evidence/'+item['evidence_ids'][0]).status_code==200
    client.post('/api/cases/demo/intake/reset',json={'reload_samples':False})
    assert len(client.get('/api/cases/demo/audit?action=SOURCE_PROCESSED').json())==4

def test_timeline_order_filters_and_case_isolation(client):
    client.post('/api/leads/17/reviews',json=payload(client))
    main.review_store.append('ANOTHER-CASE','Other','HUMAN','HIDDEN','lead','17')
    items=client.get('/api/cases/demo/timeline').json();dated=[datetime.fromisoformat(e['timestamp']) for e in items if e['timestamp']]
    assert dated==sorted(dated)
    assert {'OBSERVED_SOURCE_EVENT','ANALYTICAL_SIGNAL','HUMAN_SYSTEM_ACTION'}<={e['category'] for e in items}
    assert all(e['case_id']=='VEIL-DEMO-001' for e in items)
    assert all(e['case_id']=='VEIL-DEMO-001' for e in client.get('/api/cases/demo/audit').json())
    filtered=client.get('/api/cases/demo/timeline',params={'event_type':'transfer','source_type':'Transaction','entity_id':'A17','start':'2026-08-15T00:00:00+05:30','end':'2026-08-15T23:59:59+05:30'}).json()
    assert filtered and all(e['event_type']=='transfer' and 'A17' in e['entity_ids'] and 'Transaction' in e['source_types'] for e in filtered)
    assert client.get('/api/cases/demo/timeline?entity_id=foreign').status_code==404
    assert client.get('/api/cases/demo/audit?actor=Demo&action=LEAD_REVIEW_SUBMITTED').json()
    assert client.get('/api/cases/demo/timeline?start=2026-08-15T00:00:00').status_code==422
    assert client.get('/api/cases/demo/timeline?start=2026-09-01T00:00:00Z&end=2026-08-01T00:00:00Z').status_code==422

def test_outbox_recovery_and_idempotent_initialization(client,tmp_path):
    from backend.intake_models import UploadSource
    # Simulate a committed source operation before its audit mirror runs.
    main.intake_store.upload(UploadSource(filename='cdr.csv',source_type='CDR',content=(SAMPLES/'cdr.csv').read_text(encoding='utf-8')))
    main.intake_store.process()
    assert not main.review_store.audit('VEIL-DEMO-001')
    first=client.get('/api/cases/demo/audit').json()
    assert {e['action'] for e in first}=={'SOURCE_UPLOADED','SOURCE_PROCESSED'}
    assert client.get('/api/cases/demo/audit').json()==first
    assert ReviewStore(main.review_store.path).audit('VEIL-DEMO-001')==main.review_store.audit('VEIL-DEMO-001')
    import sqlite3
    old=tmp_path/'legacy.sqlite3'
    with sqlite3.connect(old) as db:db.execute('CREATE TABLE reviews(id INTEGER PRIMARY KEY, decision TEXT)')
    with pytest.raises(ValueError,match='incompatible legacy'):ReviewStore(old)
    with sqlite3.connect(old) as db:assert [r[1] for r in db.execute('PRAGMA table_info(reviews)')]==['id','decision']
