from collections import Counter
from copy import deepcopy
from datetime import datetime
from statistics import median
import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app, repository
from backend.demo_paths import compute_path
from backend.demo_repository import DemoRepository
from backend.generate_demo import generate, ROOT


@pytest.fixture
def client(tmp_path,monkeypatch):
    from backend import main
    from backend.resolution import ResolutionStore
    monkeypatch.setattr(main,"resolution_store",ResolutionStore(tmp_path/"resolution.sqlite3"))
    from backend.intake_store import IntakeStore
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.sqlite3'))
    with TestClient(app) as client: yield client


def test_case_and_sources(client):
    response=client.get('/api/cases/demo')
    assert response.status_code==200
    data=response.json()
    assert data['synthetic'] is True
    assert data['case']['id']=='VEIL-DEMO-001'
    assert data['case']['classification']=='Synthetic Demonstration'
    assert data['case']['status']=='Active Review'
    assert data['counts']['entities']==42
    assert len(client.get('/api/cases/demo/sources').json()['sources'])==9


def test_graph_provenance_and_types(client):
    data=client.get('/api/cases/demo/graph').json()
    assert Counter(n['type'] for n in data['nodes'])=={'Person':12,'Phone':12,'Account':8,'Vehicle':3,'Location':4,'Organization':3}
    assert 30<=len(data['relationships'])<=45
    ids={n['id'] for n in data['nodes']}
    for r in data['relationships']:
        assert r['source'] in ids and r['target'] in ids
        assert r['evidence_ids'] and set(r['evidence_ids'])<=repository.evidence.keys()


def test_target_path_is_computed(client):
    result=client.get('/api/cases/demo/path?source=rahul&target=vikram').json()
    assert result['node_ids']==['rahul','P101','P204','amit','A17','A31','vikram']
    assert result['path_length']==6
    assert [r['type'] for r in result['relationships']]==['USES','CALLED','USED_BY','CONTROLS','TRANSFERRED_TO','CONTROLLED_BY']
    for step in result['steps']:
        assert step['evidence_ids']
        relationship=repository.relationships[step['relationship_id']]
        assert {step['from_id'],step['to_id']}=={relationship.source,relationship.target}
    changed=deepcopy(repository)
    del changed.relationships['R01']
    del changed.relationships['R-RES-02']
    assert compute_path(changed,'rahul','vikram',8) is None
    # Removing the direct transfer changes the computed route (no fixture path response).
    changed=deepcopy(repository)
    del changed.relationships['R05']
    assert 'A44' in compute_path(changed,'rahul','vikram',8).node_ids


@pytest.mark.parametrize('source,target,depth,status,code',[
    ('missing','vikram',8,404,'ENTITY_NOT_FOUND'),
    ('rahul','P314',8,404,'NO_PATH_WITHIN_DEPTH'),
    ('rahul','vikram',5,404,'NO_PATH_WITHIN_DEPTH'),
    ('rahul','vikram',9,422,'INVALID_REQUEST'),
    ('rahul','vikram',0,422,'INVALID_REQUEST'),
])
def test_invalid_or_bounded_path(client,source,target,depth,status,code):
    r=client.get('/api/cases/demo/path',params={'source':source,'target':target,'max_depth':depth})
    assert r.status_code==status
    assert r.json()['error']['code']==code


def test_zero_hop_and_reverse_and_ties(client):
    assert client.get('/api/cases/demo/path?source=rahul&target=rahul').json()['path_length']==0
    result=client.get('/api/cases/demo/path?source=vikram&target=rahul').json()
    assert result['steps'][0]['traversal']=='reverse'
    reordered=deepcopy(repository)
    reordered.relationships=dict(reversed(list(reordered.relationships.items())))
    assert compute_path(reordered,'rahul','vikram',8).node_ids==compute_path(repository,'rahul','vikram',8).node_ids


def test_evidence_and_lead(client):
    lead=client.get('/api/leads/17').json()['lead']
    assert lead['engine_version']=='temporal-leads-v1' and lead['review_priority']=='HIGH'
    assert len(lead['signals'])==4
    assert 'not a probability of criminal activity' in lead['disclaimer']
    assert client.get('/api/cases/demo/leads').json()['leads'][0]['lead_id']=='17'
    for evidence_id in lead['evidence_ids']:
        r=client.get('/api/evidence/'+evidence_id)
        assert r.status_code==200
        e=r.json()['evidence']
        assert e['source_filename'] and e['source_type'] and e['timestamp'] and e['exact_excerpt'] and e['verification_status']
        assert e['locator']['row'] or e['locator']['paragraph']
    for route in ['/api/leads/999','/api/evidence/absent']:
        assert client.get(route).status_code==404


def test_fixture_claims_are_supported_without_runtime_detection():
    calls=[e for e in repository.events.values() if e.type=='call']
    baseline=[e for e in calls if e.timestamp.day<15]
    current=[e for e in calls if e.timestamp.day==15]
    assert median(Counter(e.timestamp.date() for e in baseline).values())==2
    assert len(current)==11
    old_contacts={e.entity_ids[1] for e in baseline}
    assert len({e.entity_ids[1] for e in current}-old_contacts)==7
    transfers=[e for e in repository.events.values() if e.type=='transfer']
    assert sum(e.amount_inr for e in transfers)==195000
    assert len({n for e in transfers for n in e.entity_ids})==3
    assert (max(e.timestamp for e in transfers)-min(e.timestamp for e in transfers)).total_seconds()==75*60
    assert (repository.case.event_timestamp-max(e.timestamp for e in transfers)).total_seconds()==10*60
    # A44 is a branch, not a fabricated third account on the shortest path.
    alternate=['rahul','P101','P204','amit','A17','A44','A31','vikram']
    for a,b in zip(alternate,alternate[1:]):
        assert any({r.source,r.target}=={a,b} for r in repository.relationships.values())


def test_generator_and_validation(tmp_path):
    for name,data in generate().items():
        stored=json.loads((ROOT/(name+'.json')).read_text(encoding='utf-8'))
        assert stored['items']==data['items']
        (tmp_path/(name+'.json')).write_text(json.dumps(stored),encoding='utf-8')
    broken=json.loads((tmp_path/'relationships.json').read_text())
    broken['items'][0]['evidence_ids']=['absent']
    (tmp_path/'relationships.json').write_text(json.dumps(broken))
    with pytest.raises(ValueError,match='unresolved'):DemoRepository(tmp_path)


def test_legacy_review_and_detection_routes_remain_disabled(client):
    assert client.post('/api/reviews',json={}).status_code==404
    assert client.get('/api/audit').status_code==404
    assert len(client.get('/openapi.json').json()['paths'])==24

