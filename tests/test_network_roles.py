from fastapi.testclient import TestClient
from backend.main import app
from backend.demo_repository import DemoRepository
from backend.intelligence import compute_network_roles

def test_compute_network_roles_identifies_bridge():
    repo = DemoRepository()
    roles = compute_network_roles(repo)
    assert len(roles) == len(repo.entities)
    
    # Check that Amit Verma is identified as a bridge node
    amit_role = next((r for r in roles if r['entity_id'] == 'amit'), None)
    assert amit_role is not None
    assert amit_role['category'] == 'BRIDGE'
    assert amit_role['betweenness'] > 0.10
    assert 'betweenness centrality' in amit_role['reason'].lower()

def test_network_roles_api():
    client = TestClient(app)
    response = client.get('/api/cases/demo/network-roles')
    assert response.status_code == 200
    data = response.json()
    assert 'case_id' in data
    assert 'roles' in data
    assert len(data['roles']) >= 40
    
    first = data['roles'][0]
    for key in ['entity_id', 'entity_label', 'degree', 'betweenness', 'role', 'category', 'reason', 'disclaimer']:
        assert key in first
