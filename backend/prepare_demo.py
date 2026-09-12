"""Prepare a dedicated rehearsal state; archive its journal before an explicit reset."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import sqlite3
from .intake_store import IntakeStore
from .resolution import ResolutionStore
from .review_store import ReviewStore

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_STATE=ROOT/'backend'/'data'/'rehearsal'

def prepare(state_dir=DEFAULT_STATE,reset=False):
    root=Path(state_dir).resolve()
    # Never target the old fixture/legacy database directory accidentally.
    if root in [ROOT,ROOT/'backend',ROOT/'backend'/'data',ROOT/'backend'/'data'/'demo']:
        raise ValueError('Choose a dedicated rehearsal subdirectory, not the fixture or legacy data directory.')
    root.mkdir(parents=True,exist_ok=True)
    paths={'VEIL_INTAKE_DB':root/'intake.sqlite3','VEIL_RESOLUTION_DB':root/'resolution.sqlite3','VEIL_REVIEW_DB':root/'investigator_journal.sqlite3'}
    if reset:
        backup=root/'archives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        for path in paths.values():
            if path.exists():
                backup.mkdir(parents=True,exist_ok=True)
                with sqlite3.connect(path) as source,sqlite3.connect(backup/path.name) as target:source.backup(target)
    intake=IntakeStore(paths['VEIL_INTAKE_DB']);resolution=ResolutionStore(paths['VEIL_RESOLUTION_DB']);review=ReviewStore(paths['VEIL_REVIEW_DB'])
    if reset:
        with resolution.connect() as db:db.execute('DELETE FROM decisions')
        with review.connect() as db:
            db.execute('DELETE FROM reviews');db.execute('DELETE FROM audit')
        with intake.connect() as db:db.execute('DELETE FROM intake_audit_outbox')
    if reset or not intake.summary().manifests:
        intake.reset(True);intake.process()
    os.environ.update({key:str(path) for key,path in paths.items()})
    return {'state_directory':str(root),'processed_sources':len(intake.summary().manifests),'records':intake.summary().records_processed,'rejected_records':intake.summary().rejected_records,'environment':{k:str(v) for k,v in paths.items()}}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir',default=str(DEFAULT_STATE));parser.add_argument('--reset',action='store_true',help='Stop the server first. Archives previous dedicated rehearsal databases before resetting.')
    args=parser.parse_args();print(json.dumps(prepare(args.state_dir,args.reset),indent=2))
