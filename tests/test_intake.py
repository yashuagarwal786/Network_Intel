import hashlib
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from backend import main
from backend.intake_models import UploadSource,Manifest
from backend.intake_parser import parse,extract
from backend.intake_store import IntakeStore,SAMPLES
from backend.resolution import ResolutionStore

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.sqlite3'))
    monkeypatch.setattr(main,'resolution_store',ResolutionStore(tmp_path/'resolution.sqlite3'))
    with TestClient(main.app) as c:yield c

def upload(c,name,kind,content=None):
    return c.post('/api/cases/demo/sources/upload',json={'filename':name,'source_type':kind,'content':content if content is not None else (SAMPLES/name).read_text(encoding='utf-8')})

def test_cdr_invalid_row_and_checksum_locator(client):
    response=upload(client,'cdr.csv','CDR');assert response.status_code==200
    manifest=response.json();text=(SAMPLES/'cdr.csv').read_text(encoding='utf-8')
    assert manifest['checksum']==hashlib.sha256(text.encode()).hexdigest()
    assert 'Row 4' in manifest['validation_errors'][0]
    summary=client.post('/api/cases/demo/process').json();assert summary['valid_records']==2 and summary['rejected_records']==1
    rows=client.get('/api/cases/demo/source-records').json()['records'];assert [r['row'] for r in rows]==[2,3,4]
    for r in rows:
        assert text[r['span_start']:r['span_end']]==r['raw_excerpt']
        assert client.get('/api/source-records/'+r['record_id']).json()==r
        evidence=client.get('/api/evidence/E-'+r['record_id']).json()['evidence']
        assert evidence['exact_excerpt']==r['raw_excerpt'] and evidence['parser_version']=='controlled-intake-v1'
    data=client.get('/api/cases/demo/extracted-claims').json()
    assert len(data['claims'])==2
    assert not any(m['record_id']==rows[2]['record_id'] for m in data['mentions'])

@pytest.mark.parametrize('name,kind,relation',[('transactions.csv','Transaction','TRANSFERRED_TO'),('vehicles.csv','Vehicle','REGISTERED_KEEPER')])
def test_structured_sources(client,name,kind,relation):
    assert upload(client,name,kind).status_code==200
    result=client.post('/api/cases/demo/process').json();assert result['valid_records']==2
    data=client.get('/api/cases/demo/extracted-claims').json();assert any(c['relationship_type']==relation for c in data['claims'])
    assert all(m['verification_status']=='UNVERIFIED' and m['evidence_id'] for m in data['mentions'])

def test_report_extraction_negation_uncertainty_and_unsupported(client):
    upload(client,'report.txt','Report');client.post('/api/cases/demo/process')
    data=client.get('/api/cases/demo/extracted-claims').json();kinds={m['kind'] for m in data['mentions']}
    assert {'Person','Organization','Location','Phone','Vehicle','Date','Money','CaseIdentifier'}<=kinds
    assert any(m['raw_value']=='INR 75000.00' for m in data['mentions'])
    assert any(m['raw_value']=='12 August 2026' for m in data['mentions'])
    meeting=[c for c in data['claims'] if c['relationship_type']=='MET']
    assert {c['disposition'] for c in meeting}=={'NEGATED','UNCERTAIN'}
    graph=client.get('/api/cases/demo/graph').json();assert not any(r['type']=='MET' for r in graph['relationships'])
    for c in meeting:
        e=client.get('/api/evidence/'+c['evidence_ids'][0]).json()['evidence']
        assert 'Rahul Sharma' in e['exact_excerpt'];assert not e['relationship_ids']
    assert any(c['disposition']=='UNSUPPORTED' and 'secretly directs' in client.get('/api/source-records/'+c['record_id']).json()['raw_excerpt'] for c in data['claims'])

def test_official_process_idempotence_projection_and_reset(client):
    base=client.get('/api/cases/demo/graph').json()
    assert client.post('/api/cases/demo/intake/reset',json={'reload_samples':True}).status_code==200
    first=client.post('/api/cases/demo/process').json()
    assert first['records_processed']==15 and first['relationship_candidates']==9
    graph=client.get('/api/cases/demo/graph').json();assert len(graph['relationships'])==len(base['relationships'])+9
    assert len(graph['nodes'])>len(base['nodes'])
    extracted=[r for r in graph['relationships'] if r['id'].startswith('C-')]
    for r in extracted:
        assert r['verification_status']=='UNVERIFIED'
        for e in r['evidence_ids']:assert client.get('/api/evidence/'+e).status_code==200
    original=deepcopy(main.intake_store.read())
    assert client.post('/api/cases/demo/process').json()==first
    assert main.intake_store.read()==original
    assert client.get('/api/cases/demo/graph').json()==graph
    assert upload(client,'duplicate.csv','CDR',(SAMPLES/'cdr.csv').read_text()).json()['source_file_id']==next(m['source_file_id'] for m in first['manifests'] if m['source_type']=='CDR')
    assert len(main.intake_store.read()['files'])==4
    assert IntakeStore(main.intake_store.path).read()==original
    assert client.get('/api/cases/demo/path?source=rahul&target=vikram').json()['path_length']==6
    edge=extracted[0]
    assert client.get('/api/cases/demo/path',params={'source':edge['source'],'target':edge['target']}).json()['path_length']>=1
    assert client.get('/api/resolution-proposals/MP-rahul-rk-sharma').json()['proposal']['recommendation']=='REVIEW'
    client.post('/api/cases/demo/intake/reset',json={'reload_samples':False})
    assert client.get('/api/cases/demo/graph').json()==base

@pytest.mark.parametrize('name,kind,content',[('../bad.csv','CDR','x'),('C:\\bad.csv','CDR','x'),('CON.csv','CDR','x'),('bad.exe','Report','x'),('bad.pdf','Report','x'),('bad.txt','CDR','x'),('bad.csv','CDR','\x00'),('bad.txt','Report','x'*65537),('bad.txt','Report','₹'*30000)],ids=['traversal','absolute','reserved','exe','pdf','wrong-type','binary','large-ascii','large-utf8'])
def test_unsafe_uploads(client,name,kind,content):
    assert upload(client,name,kind,content).status_code==422
    assert not main.intake_store.read()['files']

def test_upload_bounds_types_invalid_header_and_not_found(client):
    assert client.post('/api/cases/demo/sources/upload',content=b'x'*400001,headers={'Content-Type':'application/json'}).status_code==413
    assert client.post('/api/cases/demo/sources/upload',content=b'foo',headers={'Content-Type':'text/plain'}).status_code==415
    bad=upload(client,'bad.csv','CDR','unexpected,header\n1,2\n').json();assert bad['processing_status']=='INVALID'
    assert client.post('/api/cases/demo/process').json()['records_processed']==0
    assert client.get('/api/source-records/missing').status_code==404

def test_multiline_csv_locator_and_duplicate_row(client):
    content=(SAMPLES/'cdr.csv').read_text().splitlines()[0]+'\r\nCALL-ONE,+910000000101,+910000000204,2026-08-12T18:00:00+05:30,60,"Rivergate\n depot"\r\nCALL-TWO,+910000000101,+910000000204,2026-08-12T18:00:00+05:30,60,East market\r\nCALL-TWO,+910000000101,+910000000204,2026-08-12T18:00:00+05:30,60,East market\r\n'
    upload(client,'multiline.csv','CDR',content);client.post('/api/cases/demo/process')
    rows=client.get('/api/cases/demo/source-records').json()['records']
    assert [r['row'] for r in rows]==[2,4,5]
    for r in rows:assert content[r['span_start']:r['span_end']]==r['raw_excerpt']
    assert rows[-1]['validation_errors']==['duplicate source record identifier']

def test_unsupported_typed_template_and_identifier_extraction(client):
    upload(client,'typed.txt','Report','Mira Logistics is located at Rahul Sharma.\nReference TX-900, account DEMO-A909, date 2026-08-12, amount INR 10.00.\n')
    client.post('/api/cases/demo/process')
    data=client.get('/api/cases/demo/extracted-claims').json()
    assert all(c['disposition']=='UNSUPPORTED' for c in data['claims'])
    assert {'TransactionIdentifier','Account','Date','Money'}<={m['kind'] for m in data['mentions']}

def test_resolution_remains_reversible_with_processed_sources(client):
    client.post('/api/cases/demo/intake/reset',json={'reload_samples':True});client.post('/api/cases/demo/process')
    before=client.get('/api/cases/demo/graph').json()
    body={'action':'CONFIRM_MATCH','reviewer':'Test','reason':'Synthetic source review'}
    decision=client.post('/api/resolution-proposals/MP-rahul-rk-sharma/decisions',json=body)
    assert decision.status_code==200
    assert len(client.get('/api/cases/demo/graph').json()['nodes'])==len(before['nodes'])-1
    body['action']='UNDO_CONFIRMED_MATCH'
    assert client.post('/api/resolution-decisions/'+decision.json()['decision_id']+'/undo',json=body).status_code==200
    assert client.get('/api/cases/demo/graph').json()==before
    assert client.get('/api/leads/17').status_code==200
