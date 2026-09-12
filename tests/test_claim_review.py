from fastapi.testclient import TestClient
from backend import main
from backend.intake_models import UploadSource
from backend.intake_store import IntakeStore

def test_claim_review_and_graph_filtering(tmp_path, monkeypatch):
    store = IntakeStore(tmp_path / 'intake_claim_test.sqlite3')
    monkeypatch.setattr(main, 'intake_store', store)

    # Upload and process a small source with report
    store.upload(UploadSource(
        filename='report.txt',
        source_type='Report',
        content='Rahul Sharma visited North yard on 14 August 2026.\nVikram Singh uses phone +910000000204.\n'
    ))
    store.process()

    candidate = next(c for c in store.read()['claims'] if c['disposition'] == 'GRAPH_CANDIDATE')
    claim_id = candidate['claim_id']
    assert candidate['verification_status'] in ['EXTRACTED_UNVERIFIED', 'UNVERIFIED']

    with TestClient(main.app) as client:
        # 1. Review claim to INVESTIGATOR_VERIFIED
        res = client.post(f'/api/claims/{claim_id}/review', json={
            'status': 'INVESTIGATOR_VERIFIED',
            'reviewer': 'Inspector Roy',
            'reason': 'Corroborated by field surveillance log.'
        })
        assert res.status_code == 200
        data = res.json()
        assert data['verification_status'] == 'INVESTIGATOR_VERIFIED'
        assert data['reviewed_by'] == 'Inspector Roy'
        assert data['review_reason'] == 'Corroborated by field surveillance log.'

        # Augment should include this relationship with INVESTIGATOR_VERIFIED
        aug = store.augment(main.repository)
        assert claim_id in aug.relationships
        assert aug.relationships[claim_id].verification_status == 'INVESTIGATOR_VERIFIED'

        # 2. Reject the claim
        res2 = client.post(f'/api/claims/{claim_id}/review', json={
            'status': 'INVESTIGATOR_REJECTED',
            'reviewer': 'Inspector Roy',
            'reason': 'False positive entity pairing.'
        })
        assert res2.status_code == 200
        assert res2.json()['verification_status'] == 'INVESTIGATOR_REJECTED'

        # Augment MUST exclude rejected claims from the graph
        aug2 = store.augment(main.repository)
        assert claim_id not in aug2.relationships

        # 3. Invalid claim ID returns 404
        res_err = client.post('/api/claims/nonexistent/review', json={
            'status': 'INVESTIGATOR_VERIFIED',
            'reviewer': 'Inspector Roy',
            'reason': 'Test'
        })
        assert res_err.status_code == 404
