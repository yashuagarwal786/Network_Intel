from fastapi.testclient import TestClient
from backend import main
from backend.intake_store import IntakeStore
from backend.resolution import ResolutionStore


def client_for(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.sqlite3'))
    monkeypatch.setattr(main,'resolution_store',ResolutionStore(tmp_path/'resolution.sqlite3'))
    return TestClient(main.app)


def test_report_entities_relations_and_exact_provenance(tmp_path,monkeypatch):
    client=client_for(tmp_path,monkeypatch)
    content='Priya Nair visited Mumbai on 12 August 2026.\nPriya Nair uses phone +919876543210.\n'
    assert client.post('/api/cases/demo/sources/upload',json={'filename':'field-notes.txt','source_type':'Report','content':content}).status_code==200
    assert client.post('/api/cases/demo/process').status_code==200
    data=client.get('/api/cases/demo/extracted-claims').json()
    assert {'VISITED','USED_PHONE'}<={c['relationship_type'] for c in data['claims'] if c['disposition']=='GRAPH_CANDIDATE'}
    for item in [*data['mentions'],*data['claims']]:
        assert item['source_id'] and item['evidence_text'] and item['extraction_method']
        assert content[item['span_start']:item['span_end']]==item['evidence_text']
        assert item['confidence'] is None
    graph=client.get('/api/cases/demo/graph').json()
    extracted=[r for r in graph['relationships'] if r['id'].startswith('C-')]
    assert extracted and all(r['extraction_provenance'] for r in extracted)


def test_uploaded_csv_accepts_non_fixture_names_and_locations(tmp_path,monkeypatch):
    client=client_for(tmp_path,monkeypatch)
    csv='record_id,vehicle_number,relationship_type,person_name,observed_at,location,source_type\nVR-X1,DEMO-VH-901,OBSERVED_WITH,Imran Sheikh,2026-08-12T10:00:00+05:30,Kochi Dock 7,synthetic_observation\n'
    response=client.post('/api/cases/demo/sources/upload',json={'filename':'new-vehicle.csv','source_type':'Vehicle','content':csv})
    assert response.status_code==200
    summary=client.post('/api/cases/demo/process').json()
    assert summary['valid_records']==1 and summary['rejected_records']==0
    mentions=client.get('/api/cases/demo/extracted-claims').json()['mentions']
    assert {'Imran Sheikh','Kochi Dock 7'}<={m['raw_value'] for m in mentions}
