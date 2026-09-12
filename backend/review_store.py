"""Local append-only review journal. No tamper-resistance claim."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Any
from uuid import uuid4
import hashlib
import json
import sqlite3
from pydantic import Field, field_validator
from .demo_schemas import Model

ReviewAction = Literal['USEFUL_LEAD','FALSE_POSITIVE','IRRELEVANT','NEEDS_MORE_EVIDENCE','VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE']

class ReviewInput(Model):
    reviewer: str = Field(min_length=1, max_length=100)
    action: ReviewAction
    reason: str = Field(default='', max_length=2000)
    idempotency_key: str = Field(min_length=8, max_length=100)
    lead_revision: str = Field(min_length=64, max_length=64)
    object_id: str | None = Field(default=None, max_length=100)

    @field_validator('reviewer','idempotency_key')
    @classmethod
    def nonblank(cls, value):
        if not value.strip(): raise ValueError('Must not be blank')
        return value.strip()

class Review(ReviewInput):
    review_id: str
    case_id: str
    lead_id: str
    created_at: str

class AuditEvent(Model):
    audit_event_id: str
    case_id: str
    actor: str
    actor_type: Literal['HUMAN','SYSTEM']
    action: str
    object_type: str
    object_id: str
    old_state: dict[str, Any]
    new_state: dict[str, Any]
    reason: str
    created_at: str
    involved_entity_ids: list[str] = []
    evidence_ids: list[str] = []
    source_types: list[str] = []

class ReviewConflict(ValueError): pass

def now(): return datetime.now(timezone.utc).isoformat()

def revision(lead):
    data=lead.model_dump(mode='json',exclude={'review_status','lead_revision'})
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class ReviewStore:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            columns={r[1] for r in db.execute('PRAGMA table_info(reviews)')}
            if columns and 'payload' not in columns:
                raise ValueError('VEIL_REVIEW_DB points to an incompatible legacy database. Choose a separate investigator journal file; existing records were not changed.')
            db.execute('CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY, case_id TEXT NOT NULL, dedupe TEXT, payload TEXT NOT NULL, UNIQUE(case_id,dedupe))')
            db.execute('CREATE TABLE IF NOT EXISTS reviews (seq INTEGER PRIMARY KEY, case_id TEXT NOT NULL, lead_id TEXT NOT NULL, revision TEXT NOT NULL, request_key TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(case_id,request_key))')
    def connect(self): return sqlite3.connect(self.path,timeout=10)
    def append(self,case_id,actor,actor_type,action,object_type,object_id,old_state=None,new_state=None,reason='',dedupe=None,created_at=None,involved_entity_ids=None,evidence_ids=None,source_types=None,db=None):
        if db is None:
            with self.connect() as conn:
                return self.append(case_id,actor,actor_type,action,object_type,object_id,old_state,new_state,reason,dedupe,created_at,involved_entity_ids,evidence_ids,source_types,conn)
        event=AuditEvent(audit_event_id=str(uuid4()),case_id=case_id,actor=actor,actor_type=actor_type,action=action,object_type=object_type,object_id=object_id,old_state=old_state or {},new_state=new_state or {},reason=reason,created_at=created_at or now(),involved_entity_ids=involved_entity_ids or [],evidence_ids=evidence_ids or [],source_types=source_types or [])
        db.execute('INSERT OR IGNORE INTO audit(case_id,dedupe,payload) VALUES (?,?,?)',(case_id,dedupe,event.model_dump_json()))
        return event
    def audit(self,case_id):
        with self.connect() as db:
            return [AuditEvent.model_validate_json(row[0]) for row in db.execute('SELECT payload FROM audit WHERE case_id=? ORDER BY seq',(case_id,))]
    def history(self,case_id,lead_id,db=None):
        if db is None:
            with self.connect() as conn:return self.history(case_id,lead_id,conn)
        return [Review.model_validate_json(row[0]) for row in db.execute('SELECT payload FROM reviews WHERE case_id=? AND lead_id=? ORDER BY seq',(case_id,lead_id))]
    def decorate(self,lead):
        rev=revision(lead)
        self.append(lead.case_id,lead.engine_version,'SYSTEM','LEAD_GENERATED','lead',lead.lead_id,new_state={'lead_revision':rev,'review_priority':lead.review_priority,'review_status':'UNREVIEWED','analysis_timestamp':lead.generated_at.isoformat()},dedupe='generated:'+rev,involved_entity_ids=lead.involved_entity_ids,evidence_ids=lead.evidence_ids)
        history=[r for r in self.history(lead.case_id,lead.lead_id) if r.lead_revision==rev]
        return lead.model_copy(update={'lead_revision':rev,'review_status':history[-1].action if history else 'UNREVIEWED'})
    def submit(self,lead,body,object_type='lead',entity_ids=None,evidence_ids=None):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT payload FROM reviews WHERE case_id=? AND request_key=?',(lead.case_id,body.idempotency_key)).fetchone()
            if row:
                prior=Review.model_validate_json(row[0])
                if prior.lead_id!=lead.lead_id or any(getattr(prior,k)!=v for k,v in body.model_dump().items()):raise ReviewConflict('This submission key was already used for a different review.')
                return prior
            if body.lead_revision!=lead.lead_revision:raise ReviewConflict('The lead changed. Reopen it and review the current evidence before submitting.')
            history=[r for r in self.history(lead.case_id,lead.lead_id,db) if r.lead_revision==body.lead_revision]
            old=history[-1].action if history else 'UNREVIEWED'
            review=Review(**body.model_dump(),review_id=str(uuid4()),case_id=lead.case_id,lead_id=lead.lead_id,created_at=now())
            db.execute('INSERT INTO reviews(case_id,lead_id,revision,request_key,payload) VALUES (?,?,?,?,?)',(lead.case_id,lead.lead_id,body.lead_revision,body.idempotency_key,review.model_dump_json()))
            self.append(lead.case_id,body.reviewer,'HUMAN','LEAD_REVIEW_SUBMITTED',object_type,body.object_id or lead.lead_id,old_state={'review_status':old,'lead_revision':body.lead_revision},new_state={'review_status':body.action,'lead_id':lead.lead_id,'review_id':review.review_id,'lead_revision':body.lead_revision},reason=body.reason,created_at=review.created_at,involved_entity_ids=entity_ids or lead.involved_entity_ids,evidence_ids=evidence_ids or lead.evidence_ids,db=db)
            return review
