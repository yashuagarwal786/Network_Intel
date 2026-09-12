"""Conservative, explainable resolution over immutable source mentions."""
from copy import deepcopy
from datetime import datetime, timezone
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from typing import Literal
import re
import sqlite3
import unicodedata
from uuid import uuid4
from pydantic import Field, field_validator
from .demo_schemas import Model, Entity

VERSION='resolution-rules-v1'
class FeatureComparison(Model):
    feature: str
    value: float
    weight: float
    explanation: str
    evidence_ids: list[str]

class MatchProposal(Model):
    proposal_id: str
    case_id: str = 'VEIL-DEMO-001'
    left_entity_id: str
    right_entity_id: str
    left_entity: Entity
    right_entity: Entity
    feature_comparisons: list[FeatureComparison]
    score: float
    recommendation: Literal['YES','REVIEW','NO']
    supporting_evidence_ids: list[str]
    match_reason: str = 'Possible identity match. Review the cited source records.'
    strong_identifier_matches: list[str] = []
    status: Literal['REVIEW','CONFIRMED','REJECTED','DEFERRED'] = 'REVIEW'
    created_at: str = '2026-08-15T20:00:00+05:30'
    algorithm_version: str = VERSION

class DecisionInput(Model):
    action: Literal['CONFIRM_MATCH','REJECT_MATCH','DEFER','UNDO_CONFIRMED_MATCH']
    reviewer: str = Field(min_length=1,max_length=100)
    reason: str = Field(min_length=1,max_length=1000)
    @field_validator('reviewer','reason')
    @classmethod
    def nonblank(cls,v):
        if not v.strip():raise ValueError('Must not be blank')
        return v.strip()

class ResolutionDecision(DecisionInput):
    decision_id: str
    proposal_id: str
    created_at: str
    undoes_decision_id: str | None = None

class ProposalResponse(Model):
    proposal: MatchProposal
    decisions: list[ResolutionDecision]

class ProposalsResponse(Model):
    proposals: list[MatchProposal]

def clean_name(name):
    # Strip trailing file tag annotations, e.g. (report.txt), (cdr.csv), or other parenthetical filename noise
    cleaned = re.sub(r'\s*\([^)]*\.(?:txt|csv)\)', '', name, flags=re.IGNORECASE)
    return cleaned.strip()

def normalize(name):
    cleaned = clean_name(name)
    return ' '.join(re.sub(r'[^\w\s]', ' ', unicodedata.normalize('NFKC', cleaned).casefold()).split())

def name_compatibility(left, right):
    """Supporting signal only; abbreviated tokens may align by initial."""
    x, y = normalize(left).split(), normalize(right).split()
    raw = SequenceMatcher(None, ' '.join(x), ' '.join(y)).ratio()
    if not x or not y:
        return raw
    shorter, longer = (x, y) if len(x) <= len(y) else (y, x)
    aligned = all(any(a == b or (len(a) == 1 and b.startswith(a)) or (len(b) == 1 and a.startswith(b)) for b in longer) for a in shorter)

    # Conflict penalty: when both names have multi-letter surnames that do not match
    if len(x) >= 2 and len(y) >= 2 and len(x[-1]) > 1 and len(y[-1]) > 1 and x[-1] != y[-1]:
        return min(raw * 0.4, 0.25)

    return max(raw, 0.9 if aligned and shorter != longer else raw)

def name_block(left, right):
    x, y = normalize(left).split(), normalize(right).split()
    if not x or not y:
        return False
    same_surname = x[-1] == y[-1] and x[0][0] == y[0][0]
    abbreviated_surname = x[0] == y[0] and (x[-1].startswith(y[-1]) or y[-1].startswith(x[-1])) and min(len(x[-1]), len(y[-1])) == 1
    return same_surname or abbreviated_surname

def assets(repo, person, kind):
    result = {}
    for r in repo.relationships.values():
        other = r.target if r.source == person else r.source if r.target == person else None
        if other and repo.entities[other].type == kind and r.status == 'recorded':
            result.setdefault(other, []).extend(r.evidence_ids)
    return result

def candidates(repo):
    people = sorted((n for n in repo.entities.values() if n.type == 'Person'), key=lambda n: n.id)
    for a, b in combinations(people, 2):
        # Phone and Account are strong personal identity signals; Vehicle is shared property
        strong = any(set(assets(repo, a.id, kind)) & set(assets(repo, b.id, kind)) for kind in ['Phone', 'Account'])
        shared_vehicle = bool(set(assets(repo, a.id, 'Vehicle')) & set(assets(repo, b.id, 'Vehicle')))
        if name_block(a.label, b.label) or strong or shared_vehicle:
            yield a, b

def proposals(repo):
    result = {}
    for a, b in candidates(repo):
        # Prefer the expanded mention as the canonical display record.
        a, b = sorted((a, b), key=lambda n: (-len(normalize(n.label)), n.id))
        x, y = normalize(a.label), normalize(b.label)
        name = round(name_compatibility(a.label, b.label), 4)
        features = [FeatureComparison(
            feature='Normalized name similarity',
            value=name,
            weight=0.2,
            explanation=f'Normalized strings: {x} / {y}. Sequence similarity only; initials are not proof of identity.',
            evidence_ids=sorted(set(a.evidence_ids + b.evidence_ids))
        )]
        strong_matches = []
        for kind, weight in [('Phone', 0.5), ('Vehicle', 0.1), ('Account', 0.2)]:
            left, right = assets(repo, a.id, kind), assets(repo, b.id, kind)
            shared = sorted(left.keys() & right.keys())
            if shared and kind in ['Phone', 'Account']:
                strong_matches.append(kind)
            explanation = (
                f'Same source identifier: {", ".join(shared)}. Shared use remains possible; human verification required.'
                if shared
                else f'No shared identifier recorded. Missing evidence is not a contradiction.'
            )
            features.append(FeatureComparison(
                feature=f'Exact shared {kind.lower()}',
                value=float(bool(shared)),
                weight=weight,
                explanation=explanation,
                evidence_ids=sorted({e for key in shared for e in left[key] + right[key]}) or sorted(set(a.evidence_ids + b.evidence_ids))
            ))
        score = round(sum(f.value * f.weight for f in features), 4)
        shared_veh = any(f.feature == 'Exact shared vehicle' and f.value > 0 for f in features)
        recommendation = 'YES' if score >= 0.85 and len(strong_matches) >= 2 else 'REVIEW' if strong_matches or name >= 0.35 or shared_veh else 'NO'
        if strong_matches:
            reason = f'Possible match because {", ".join("same " + k.casefold() for k in strong_matches)}{" and compatible name." if name >= 0.55 else "."}'
        elif shared_veh:
            reason = 'Shared vehicle recorded in source data. Vehicles are corroborating property and do not establish shared personal identity; independent review required.'
        else:
            reason = 'Possible match because the normalized names are compatible; no strong identifier is shared.'
        pid = f'MP-{a.id}-{b.id}'
        result[pid] = MatchProposal(
            proposal_id=pid,
            left_entity_id=a.id,
            right_entity_id=b.id,
            left_entity=a,
            right_entity=b,
            feature_comparisons=features,
            score=score,
            recommendation=recommendation,
            supporting_evidence_ids=sorted({e for f in features for e in f.evidence_ids}),
            match_reason=reason,
            strong_identifier_matches=strong_matches
        )
    return result

class DecisionConflict(ValueError):pass

class ResolutionStore:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS decisions (seq INTEGER PRIMARY KEY AUTOINCREMENT, decision_id TEXT UNIQUE NOT NULL, proposal_id TEXT NOT NULL, payload TEXT NOT NULL)')
    def connect(self):return sqlite3.connect(self.path,timeout=10)
    def history(self,pid,db=None):
        if db is None:
            with self.connect() as conn:return self.history(pid,conn)
        return [ResolutionDecision.model_validate_json(row[0]) for row in db.execute('SELECT payload FROM decisions WHERE proposal_id=? ORDER BY seq',(pid,))]
    def state(self,pid,db=None):
        history=self.history(pid,db)
        if not history:return 'REVIEW'
        return {'CONFIRM_MATCH':'CONFIRMED','REJECT_MATCH':'REJECTED','DEFER':'DEFERRED','UNDO_CONFIRMED_MATCH':'REVIEW'}[history[-1].action]
    def decide(self,pid,body,undo_id=None):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            history=self.history(pid,db);state=self.state(pid,db)
            if body.action=='UNDO_CONFIRMED_MATCH':
                if state!='CONFIRMED' or not history or (undo_id and history[-1].decision_id!=undo_id):
                    raise DecisionConflict('Only the currently active confirmation can be undone.')
                undo_id=history[-1].decision_id
            elif state=='CONFIRMED':raise DecisionConflict('Undo the active confirmation before another decision.')
            decision=ResolutionDecision(**body.model_dump(),decision_id=str(uuid4()),proposal_id=pid,created_at=datetime.now(timezone.utc).isoformat(),undoes_decision_id=undo_id)
            db.execute('INSERT INTO decisions(decision_id,proposal_id,payload) VALUES (?,?,?)',(decision.decision_id,pid,decision.model_dump_json()))
            return decision
    def find(self,id):
        with self.connect() as db:
            row=db.execute('SELECT payload FROM decisions WHERE decision_id=?',(id,)).fetchone()
            return ResolutionDecision.model_validate_json(row[0]) if row else None
    def reset(self):
        with self.connect() as db:db.execute('DELETE FROM decisions')

def project(repo, matches, store):
    """Non-destructive projection. Original mentions and relationship IDs survive."""
    projected=deepcopy(repo);canonical={n:n for n in repo.entities}
    with store.connect() as db:
        db.execute('BEGIN')
        for p in matches.values():
            if store.state(p.proposal_id,db)=='CONFIRMED':canonical[p.right_entity_id]=p.left_entity_id
    def root(id):
        while canonical[id]!=id:id=canonical[id]
        return id
    canonical={id:root(id) for id in canonical}
    projected.entities={}
    for id in sorted(set(canonical.values())):
        members=[n for n in repo.entities.values() if canonical[n.id]==id]
        projected.entities[id]=repo.entities[id].model_copy(update={'aliases':[n.label for n in members if n.id!=id], 'original_entity_ids':[n.id for n in members], 'evidence_ids':sorted({e for n in members for e in n.evidence_ids})})
    projected.relationships={r.id:r.model_copy(update={'source':canonical[r.source],'target':canonical[r.target],'original_source':r.source,'original_target':r.target}) for r in repo.relationships.values()}
    return projected,canonical
