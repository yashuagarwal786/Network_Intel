import sqlite3
from backend.prepare_demo import prepare
from backend.resolution import ResolutionStore,DecisionInput
from backend.intake_store import IntakeStore
from backend.demo_repository import DemoRepository
from backend.resolution import proposals,project
from backend.lead_engine import run_engine

def test_rehearsal_reset_archives_and_reseeds(tmp_path,monkeypatch):
    # Keep environment changes local to this test.
    for key in ['VEIL_INTAKE_DB','VEIL_RESOLUTION_DB','VEIL_REVIEW_DB']:monkeypatch.setenv(key,'unused')
    directory=tmp_path/'rehearsal';first=prepare(directory,True)
    assert first['processed_sources']==4 and first['records']==15 and first['rejected_records']==1
    store=ResolutionStore(directory/'resolution.sqlite3')
    store.decide('MP-rahul-rk-sharma',DecisionInput(action='CONFIRM_MATCH',reviewer='test',reason='Synthetic review'))
    prepare(directory,False);assert store.state('MP-rahul-rk-sharma')=='CONFIRMED'
    prepare(directory,True);assert store.state('MP-rahul-rk-sharma')=='REVIEW'
    archives=list((directory/'archives').glob('*/resolution.sqlite3'));assert archives
    assert any(sqlite3.connect(p).execute('SELECT count(*) FROM decisions').fetchone()[0]==1 for p in archives)
    repo=IntakeStore(directory/'intake.sqlite3').augment(DemoRepository());current,_=project(repo,proposals(repo),store)
    output=run_engine(current);assert output.leads[0].lead_id=='17' and output.leads[0].review_priority=='HIGH'
    assert prepare(directory,False)['records']==15
