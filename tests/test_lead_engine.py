from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
import json
import pytest
from fastapi.testclient import TestClient
from backend import main
from backend.demo_repository import DemoRepository
from backend.intake_store import IntakeStore
from backend.resolution import ResolutionStore
from backend.lead_engine import run_engine,Policy,historical_counts,transfer_sequences,priority_for,traceable
from backend.temporal_validation import make_dataset,evaluate,ROOT

@pytest.fixture
def repo():return DemoRepository()

def by_type(result,kind):return next(s for s in result.signals if s.signal_type==kind)

def test_baseline_includes_zero_days_and_calendar_boundaries(repo):
    start=repo.case.event_timestamp.replace(hour=0,minute=0,second=0)
    calls=[e for e in repo.events.values() if e.type=='call']
    baseline,series,expected=historical_counts(calls,'P101',start,Policy())
    assert len(baseline)==14 and [row['calls'] for row in series]==[2]*7 and expected==2
    reduced=[e for e in calls if e.timestamp.day!=8]
    assert historical_counts(reduced,'P101',start,Policy())[1][0]['calls']==0
    # Exact start of event day is not included in baseline.
    calls[0]=calls[0].model_copy(update={'timestamp':start})
    assert len(historical_counts(calls,'P101',start,Policy())[0])==13

def test_demo_signals_priority_and_evidence(repo):
    output=run_engine(repo);lead=output.leads[0]
    assert lead.lead_id=='17' and lead.review_priority=='HIGH'
    assert lead.signal_categories==['COMMUNICATION','FINANCIAL','GRAPH_CONTEXT']
    assert lead.review_status=='UNREVIEWED'
    burst=by_type(output,'COMMUNICATION_BURST');assert burst.observed_value['calls']==11 and burst.expected_value['median_calls_per_day']==2
    assert burst.threshold['effective_calls']==6
    new=by_type(output,'NEW_CONTACT_BURST');assert new.observed_value['new_contacts']==7
    assert set(new.observed_value['contact_ids'])=={'P305','P306','P307','P308','P309','P310','P311'}
    tx=by_type(output,'TRANSACTION_SEQUENCE');assert tx.observed_value['total_inr']=='195000' and tx.observed_value['transfers']==3 and tx.observed_value['elapsed_minutes']==75
    assert tx.threshold['window_minutes']==90 and len(tx.observed_value['transaction_ids'])==3
    path=by_type(output,'GRAPH_PATH');assert path.path.path_length==6
    assert path.observed_value['accounts_on_path']==['A17','A31'] and 'A44' not in path.path.node_ids
    assert set(path.observed_value['independent_association_evidence_ids'])>={'E-SUB-01','E-ACC-01'}
    for s in output.signals:assert traceable(repo,s.supporting_evidence_ids)
    assert set(lead.evidence_ids)=={id for s in lead.signals for id in s.supporting_evidence_ids}
    assert 'not a probability' in lead.disclaimer

def test_transaction_window_inclusive_boundary_and_connectivity(repo):
    events=sorted([deepcopy(e) for e in repo.events.values() if e.type=='transfer'],key=lambda e:e.timestamp)
    events[-1].timestamp=events[0].timestamp+timedelta(minutes=90)
    assert len(transfer_sequences(events,Policy()))==1
    events[-1].timestamp+=timedelta(seconds=1)
    assert not transfer_sequences(events,Policy())
    events[-1].timestamp=events[0].timestamp+timedelta(minutes=60)
    events[-1].entity_ids=['A85','A96']
    assert not transfer_sequences(events,Policy())

def test_no_lead_from_one_weak_category(repo):
    repo.events={id:e for id,e in repo.events.items() if e.type!='transfer'}
    output=run_engine(repo)
    assert len(output.signals)==2 and not output.leads
    assert {s.category for s in output.signals}=={'COMMUNICATION'}
    single=run_engine(repo,replace(Policy(),minimum_new_contacts=999))
    assert len(single.signals)==1 and not single.leads
    assert priority_for(['COMMUNICATION','COMMUNICATION'])=='LOW'

def test_priority_needs_separate_graph_association_evidence(repo):
    for r in repo.relationships.values():
        if r.type in ['USES','USED_BY','CONTROLS','CONTROLLED_BY']:r.type='CONTEXT_ASSERTION'
    output=run_engine(repo);assert output.leads[0].review_priority=='MEDIUM'
    assert not by_type(output,'GRAPH_PATH').independent_category

def test_no_path_or_temporal_overlap_no_lead(repo):
    assert not run_engine(repo,replace(Policy(),max_path_depth=5)).leads
    for e in repo.events.values():
        if e.type=='transfer':e.timestamp-=timedelta(hours=10)
    assert any(s.signal_type=='TRANSACTION_SEQUENCE' for s in run_engine(repo).signals)
    assert not run_engine(repo).leads

def test_incomplete_evidence_blocks_high_and_no_fixture_fallback(repo,tmp_path,monkeypatch):
    del repo.evidence['E-TX-01'];assert not run_engine(repo).leads
    repo.events={};repo.leads={'17':{'title':'DO NOT SERVE THIS FIXTURE'}}
    monkeypatch.setattr(main,'repository',repo)
    monkeypatch.setattr(main,'intake_store',IntakeStore(tmp_path/'intake.db'))
    monkeypatch.setattr(main,'resolution_store',ResolutionStore(tmp_path/'resolution.db'))
    with TestClient(main.app) as client:
        assert client.get('/api/cases/demo/leads').json()['leads']==[]
        assert client.get('/api/leads/17').status_code==404

def test_output_changes_with_events_and_is_order_invariant(repo):
    original=run_engine(repo).model_dump_json()
    repo.events=dict(reversed(list(repo.events.items())));repo.relationships=dict(reversed(list(repo.relationships.items())))
    assert run_engine(repo).model_dump_json()==original
    event=next(e for e in repo.events.values() if e.id=='EV-E-TX-01');event.amount_inr=Decimal('75000.25')
    assert by_type(run_engine(repo),'TRANSACTION_SEQUENCE').observed_value['total_inr']=='195000.25'
    assert run_engine(repo).model_dump_json()!=original

def test_benign_and_alternate_validation():
    benign=run_engine(make_dataset('benign_only'));assert not benign.leads
    assert any(s.signal_type=='COMMUNICATION_BURST' and s.involved_entity_ids==['P314'] for s in benign.signals)
    alternate=run_engine(DemoRepository(ROOT/'alternate_seed_22'))
    assert by_type(alternate,'COMMUNICATION_BURST').expected_value['median_calls_per_day']==3
    assert next(s for s in alternate.signals if s.signal_type=='COMMUNICATION_BURST' and s.involved_entity_ids==['P101']).observed_value['calls']==14
    result=evaluate()
    for r in result['results']:
        assert r['planted_signal_recall']==1 and r['false_leads']==0 and r['missing_expected_leads']==0
        assert r['evidence_trace_coverage']==1 and r['expected_priority_result'] and r['deterministic_repeatability'] and r['benign_non_leads_preserved']

def test_processed_intake_events_reach_engine(repo,tmp_path):
    store=IntakeStore(tmp_path/'intake.db');store.reset(True);store.process();combined=store.augment(repo)
    imported=[e for e in combined.events.values() if e.id.startswith('EV-F-')]
    assert len(imported)==4 and {e.transaction_id for e in imported if e.type=='transfer'}=={'TX-001','TX-002'}
    assert run_engine(combined).leads[0].review_priority=='HIGH'
