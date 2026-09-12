from copy import deepcopy
from datetime import date
import pytest
from fastapi.testclient import TestClient
from backend.legacy import app, DATA
from backend.intelligence import find_path, select_edges, temporal_leads

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VEIL_DB',str(tmp_path/'test.sqlite3'))
    return TestClient(app)

def test_provenance_integrity(client):
    data=client.get('/api/case').json()
    ids={e['id'] for e in data['evidence']}; nodes={n['id'] for n in data['entities']}
    assert len(ids)==len(data['evidence'])
    for edge in data['edges']:
        assert edge['source'] in nodes and edge['target'] in nodes
        assert edge['evidence_ids'] and set(edge['evidence_ids'])<=ids
    for lead in data['leads']:
        assert lead['generated_by']=='computed_rule'
        for signal in lead['signals']: assert signal['evidence_ids'] and set(signal['evidence_ids'])<=ids

def test_path_is_computed_and_reacts_to_edge_removal():
    edges=select_edges(DATA)
    result=find_path(DATA,'p1','v1',edges)
    assert result['hops']==4 and result['nodes'][0]=='p1' and result['nodes'][-1]=='v1'
    assert find_path(DATA,'p1','v1',[e for e in edges if e['target']!='v1']) is None
    for a,b,edge in zip(result['nodes'],result['nodes'][1:],result['edges']): assert {a,b}=={edge['source'],edge['target']}

def test_inferred_default_and_filters(client):
    assert all(e['status']!='inferred' for e in client.get('/api/graph').json()['edges'])
    assert any(e['status']=='inferred' for e in client.get('/api/graph?include_inferred=true').json()['edges'])
    assert client.get('/api/path?source=alias&target=p1').json()['hops']>1
    assert client.get('/api/path?source=alias&target=p1&include_inferred=true').json()['hops']==1
    assert client.get('/api/path?source=p1&target=v1&relationship=call').status_code==404
    assert client.get('/api/graph?start=2026-08-16&end=2026-08-14').status_code==422
    assert client.get('/api/path?source=missing&target=p1').status_code==404
    assert client.get('/api/path?source=p1&target=p1').json()['hops']==0
    assert select_edges(DATA,start=date(2026,8,16))==[]

def test_temporal_rule_requires_calls_and_time_window():
    assert len(temporal_leads(DATA))==1
    changed=deepcopy(DATA)
    changed['edges']=[e for e in changed['edges'] if e['id']!='r005']
    assert temporal_leads(changed)==[]
    changed=deepcopy(DATA)
    next(e for e in changed['edges'] if e['type']=='transfer')['timestamp']='2026-08-16T23:00:00+05:30'
    assert temporal_leads(changed)==[]
    changed=deepcopy(DATA)
    next(e for e in changed['edges'] if e['type']=='transfer')['target']='a1'
    assert temporal_leads(changed)==[]

def test_review_persists_and_does_not_merge(client):
    body=dict(target_type='alias',target_id='alias-01',decision='accept_match',rationale='Candidate requires an independent identity check.')
    response=client.post('/api/reviews',json=body)
    assert response.status_code==201
    assert TestClient(app).get('/api/audit').json()[0]['rationale']==body['rationale']
    assert len(client.get('/api/case').json()['entities'])==10
    assert next(e for e in client.get('/api/case').json()['edges'] if e['id']=='r13')['status']=='inferred'
    assert client.post('/api/reviews',json={**body,'decision':'dismiss'}).status_code==422
    assert client.post('/api/reviews',json={**body,'rationale':'        '}).status_code==422
    assert client.post('/api/reviews',json={**body,'target_id':'unknown'}).status_code==404

def test_lead_review_and_exact_evidence(client):
    lead=client.get('/api/case').json()['leads'][0]
    assert client.post('/api/reviews',json=dict(target_type='lead',target_id=lead['id'],decision='follow_up',rationale='Check whether the payment relates to a delivery.')).status_code==201
    for eid in lead['evidence_ids']:
        record=client.get('/api/evidence/'+eid).json()
        assert record['id']==eid and record['locator'] and record['excerpt']
    assert client.get('/api/evidence/E999').status_code==404
