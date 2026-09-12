import json
from fastapi.testclient import TestClient
from backend.demo_repository import DemoRepository
from backend.evidence_explainer import explain,packet_for_lead,packet_for_path
from backend.lead_engine import run_engine
from backend.demo_paths import compute_path
from backend.main import app


class FakeResponse:
    def __init__(self,content):self.content=content
    def raise_for_status(self):return None
    def json(self):return {'choices':[{'message':{'content':json.dumps(self.content)}}]}


class FakeClient:
    def __init__(self,content):self.content=content;self.payload=None
    def post(self,*args,**kwargs):self.payload=kwargs['json'];return FakeResponse(self.content)


def test_no_key_uses_honest_deterministic_fallback():
    repo=DemoRepository();lead=run_engine(repo).leads[0]
    result=explain(packet_for_lead(repo,lead),api_key='')
    assert result.generation_mode=='DETERMINISTIC_FALLBACK'
    assert result.provider=='local-rules'
    assert result.supporting_evidence_ids==lead.evidence_ids
    assert result.caution=='Investigative lead, not proof of guilt.'


def test_groq_draft_must_cite_allowlisted_facts_and_evidence():
    repo=DemoRepository();packet=packet_for_lead(repo,run_engine(repo).leads[0])
    client=FakeClient({'explanation':packet.facts[0].statement,'why_flagged':packet.facts[1].statement,'review_suggestion':'Review the cited records before making any decision.','fact_ids':['lead-summary','involved-records']})
    result=explain(packet,api_key='test-key',client=client)
    assert result.generation_mode=='GROQ_GROUNDED'
    assert result.grounding_status=='VALIDATED'
    assert set(result.supporting_evidence_ids)<=set(packet.supporting_evidence_ids)
    assert client.payload['response_format']['json_schema']['strict'] is True


def test_invented_number_or_accusatory_language_is_rejected():
    repo=DemoRepository();packet=packet_for_lead(repo,run_engine(repo).leads[0])
    client=FakeClient({'explanation':'The person is guilty with score 99.','why_flagged':'This is a criminal conclusion.','review_suggestion':'Arrest immediately based on this output.','fact_ids':['lead-summary']})
    result=explain(packet,api_key='test-key',client=client)
    assert result.generation_mode=='DETERMINISTIC_FALLBACK'
    assert result.grounding_status=='FALLBACK'


def test_path_packet_and_public_fallback_endpoints(monkeypatch):
    monkeypatch.delenv('GROQ_API_KEY',raising=False)
    repo=DemoRepository();path=compute_path(repo,'rahul','vikram',8)
    packet=packet_for_path(repo,path)
    assert packet.finding_type=='PATH' and packet.supporting_evidence_ids
    client=TestClient(app)
    lead=client.get('/api/leads/17/explanation')
    assert lead.status_code==200 and lead.json()['generation_mode']=='DETERMINISTIC_FALLBACK'
    result=client.get('/api/cases/demo/path/explanation',params={'source':'rahul','target':'vikram','max_depth':8})
    assert result.status_code==200 and result.json()['finding_type']=='PATH'
