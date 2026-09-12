import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .intelligence import select_edges, find_path, temporal_leads

DATA=json.loads(Path(__file__).with_name('data').joinpath('trinetra.json').read_text(encoding='utf-8'))
app=FastAPI(title='VEIL · Synthetic demonstration API')
@contextmanager
def db():
    conn=sqlite3.connect(os.environ.get('VEIL_DB',str(Path(__file__).with_name('data')/'reviews.sqlite3')))
    conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, target_type TEXT, target_id TEXT, decision TEXT, rationale TEXT, actor TEXT, created_at TEXT)')
    try:
        with conn:
            yield conn
    finally:
        conn.close()

@app.get('/api/case')
def case():
    return {**DATA,'leads':temporal_leads(DATA)}

def filtered(relationship=None,start=None,end=None,include_inferred=False):
    if start and end and start>end: raise HTTPException(422,'Start date must be on or before end date')
    if relationship and relationship not in {e['type'] for e in DATA['edges']}: raise HTTPException(422,'Unknown relationship type')
    return select_edges(DATA,relationship,start,end,include_inferred)

@app.get('/api/graph')
def graph(relationship: str|None=None,start: date|None=None,end: date|None=None,include_inferred: bool=False):
    return dict(entities=DATA['entities'],edges=filtered(relationship,start,end,include_inferred))

@app.get('/api/path')
def path(source: str,target: str,relationship: str|None=None,start: date|None=None,end: date|None=None,include_inferred: bool=False):
    if any(i not in {n['id'] for n in DATA['entities']} for i in [source,target]): raise HTTPException(404,'Unknown entity')
    result=find_path(DATA,source,target,filtered(relationship,start,end,include_inferred))
    if result is None: raise HTTPException(404,'No path exists under the current filters. Try widening the date range or relationship filter.')
    return result

@app.get('/api/evidence/{evidence_id}')
def evidence(evidence_id: str):
    result=next((e for e in DATA['evidence'] if e['id']==evidence_id),None)
    if not result: raise HTTPException(404,'Evidence not found')
    return result

class Review(BaseModel):
    target_type: Literal['lead','alias']
    target_id: str
    decision: Literal['follow_up','dismiss','inconclusive','accept_match','reject_match']
    rationale: str=Field(min_length=8,max_length=1500)

@app.post('/api/reviews',status_code=201)
def review(body: Review):
    allowed={'lead':{'follow_up','dismiss','inconclusive'},'alias':{'accept_match','reject_match','inconclusive'}}
    targets=temporal_leads(DATA) if body.target_type=='lead' else DATA['aliases']
    if body.target_id not in {t['id'] for t in targets}: raise HTTPException(404,'Review target not found')
    if body.decision not in allowed[body.target_type] or len(body.rationale.strip())<8: raise HTTPException(422,'Invalid decision or rationale')
    with db() as conn:
        cursor=conn.execute('INSERT INTO reviews (target_type,target_id,decision,rationale,actor,created_at) VALUES (?,?,?,?,?,?)',(body.target_type,body.target_id,body.decision,body.rationale.strip(),'Demo reviewer',datetime.now(timezone.utc).isoformat()))
        result=dict(conn.execute('SELECT * FROM reviews WHERE id=?',(cursor.lastrowid,)).fetchone())
    return result

@app.get('/api/audit')
def audit():
    with db() as conn: return [dict(r) for r in conn.execute('SELECT * FROM reviews ORDER BY id DESC')]
