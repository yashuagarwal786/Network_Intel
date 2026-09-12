from copy import deepcopy
from fastapi.testclient import TestClient
import pytest
from backend import main
from backend.resolution import normalize, candidates, proposals, ResolutionStore, project

RAHUL='MP-rahul-rk-sharma'
AMIT='MP-amit-a-verma'

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'resolution_store',ResolutionStore(tmp_path/'decisions.sqlite3'))
    from backend.intake_store import IntakeStore
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.sqlite3'))
    with TestClient(main.app) as c:yield c

def decide(c,pid,action):
    return c.post(f'/api/resolution-proposals/{pid}/decisions',json={'action':action,'reviewer':'Test investigator','reason':'Reviewed exact source assertions.'})

def test_normalization_and_blocking():
    assert normalize('  R.K.  SHARMA ')==normalize('R K Sharma')
    assert normalize('Ａ． Verma')=='a verma'
    pairs={frozenset((a.id,b.id)) for a,b in candidates(main.repository)}
    assert {frozenset(('rahul','rk-sharma')),frozenset(('amit','a-verma'))}<=pairs
    # Shared vehicles now create review candidates, but never automatic merges.
    assert frozenset(('kabir','rahul')) in pairs

def test_phone_vehicle_score_and_ambiguous_name():
    matches=proposals(main.repository);r=matches[RAHUL];a=matches[AMIT]
    assert r.recommendation==r.status=='REVIEW'
    assert r.feature_comparisons[1].value==1 and r.feature_comparisons[1].weight>.2
    assert r.feature_comparisons[2].value==1
    assert {'E-SUB-01','E-RES-01'}<=set(r.feature_comparisons[1].evidence_ids)
    assert r.score==round(sum(f.value*f.weight for f in r.feature_comparisons),4)
    assert a.recommendation=='REVIEW' and a.score<.2
    assert all(f.value==0 for f in a.feature_comparisons[1:])

def test_false_merge_negative(client):
    repo=deepcopy(main.repository)
    repo.entities['rk-sharma'].label='Rahul Kumar Sharma'
    repo.relationships={id:r for id,r in repo.relationships.items() if not id.startswith('R-RES-')}
    p=next(p for p in proposals(repo).values() if 'rk-sharma' in (p.left_entity_id,p.right_entity_id))
    assert p.score==.2 and p.recommendation=='REVIEW'
    before=client.get('/api/cases/demo/graph').json()
    for _ in range(2):client.get('/api/cases/demo/resolution-proposals')
    assert client.get('/api/cases/demo/graph').json()==before

def test_confirm_project_provenance_path_and_undo(client):
    before=client.get('/api/cases/demo/graph').json()
    original=client.get('/api/evidence/E-RES-01').json()
    assert len(before['nodes'])==42
    result=decide(client,RAHUL,'CONFIRM_MATCH');assert result.status_code==200
    confirmed=client.get('/api/cases/demo/graph').json()
    assert len(confirmed['nodes'])==41
    rahul=next(n for n in confirmed['nodes'] if n['id']=='rahul')
    assert rahul['aliases']==['R.K. Sharma']
    assert set(rahul['original_entity_ids'])=={'rahul','rk-sharma'}
    assert 'E-RES-01' in rahul['evidence_ids']
    rel=next(r for r in confirmed['relationships'] if r['id']=='R-RES-01')
    assert rel['source']=='rahul' and rel['original_source']=='rk-sharma'
    assert client.get('/api/evidence/E-RES-01').json()==original
    assert client.get('/api/cases/demo/path?source=rk-sharma&target=rahul').json()['path_length']==0
    assert client.get('/api/cases/demo/path?source=rahul&target=vikram').json()['path_length']==6
    assert any(n['id']=='a-verma' for n in confirmed['nodes'])
    undo=client.post('/api/resolution-decisions/'+result.json()['decision_id']+'/undo',json={'action':'UNDO_CONFIRMED_MATCH','reviewer':'Second reviewer','reason':'Reopen identity verification.'})
    assert undo.status_code==200
    assert client.get('/api/cases/demo/graph').json()==before
    assert client.get('/api/cases/demo/path?source=rk-sharma&target=rahul').json()['path_length']==2
    detail=client.get('/api/resolution-proposals/'+RAHUL).json()
    assert detail['proposal']['status']=='REVIEW' and len(detail['decisions'])==2
    assert detail['decisions'][1]['undoes_decision_id']==result.json()['decision_id']
    assert client.post('/api/resolution-decisions/'+result.json()['decision_id']+'/undo',json={'action':'UNDO_CONFIRMED_MATCH','reviewer':'Test','reason':'Repeated'}).status_code==409

def test_reject_defer_and_validation(client):
    before=client.get('/api/cases/demo/graph').json()
    assert decide(client,AMIT,'REJECT_MATCH').status_code==200
    assert client.get('/api/resolution-proposals/'+AMIT).json()['proposal']['status']=='REJECTED'
    assert decide(client,AMIT,'DEFER').status_code==200
    assert client.get('/api/cases/demo/graph').json()==before
    assert decide(client,RAHUL,'UNDO_CONFIRMED_MATCH').status_code==409
    assert decide(client,'missing','CONFIRM_MATCH').status_code==404
    assert client.post('/api/resolution-proposals/'+RAHUL+'/decisions',json={'action':'CONFIRM_MATCH','reviewer':' ','reason':'x'}).status_code==422
    assert decide(client,RAHUL,'CONFIRM_MATCH').status_code==200
    assert decide(client,RAHUL,'REJECT_MATCH').status_code==409

def test_idempotent_init_persistence_reset(client):
    decide(client,RAHUL,'CONFIRM_MATCH')
    path=main.resolution_store.path
    for _ in range(3):
        store=ResolutionStore(path)
        assert len(store.history(RAHUL))==1 and store.state(RAHUL)=='CONFIRMED'
    store.reset();assert store.state(RAHUL)=='REVIEW'
    projected,_=project(main.repository,main.matches,store)
    assert len(projected.entities)==42
