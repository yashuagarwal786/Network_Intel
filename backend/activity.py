"""Chronological projection of source records, claims, signals and audit actions."""
from datetime import datetime, timezone
from typing import Literal
from .demo_schemas import Model

class TimelineItem(Model):
    timeline_id: str
    case_id: str
    timestamp: datetime | None
    category: Literal['OBSERVED_SOURCE_EVENT','EXTRACTED_CLAIM','ANALYTICAL_SIGNAL','HUMAN_SYSTEM_ACTION']
    event_type: str
    title: str
    description: str
    entity_ids: list[str]
    evidence_ids: list[str]
    source_types: list[str]
    object_id: str

def chronological(items,stamp):
    return sorted(items,key=lambda x:(stamp(x) is None, datetime.fromisoformat(str(stamp(x))).astimezone(timezone.utc) if stamp(x) is not None else datetime.max.replace(tzinfo=timezone.utc)))

def build_timeline(repo,intake,analysis,audit):
    items=[];covered=set();case=repo.case.id
    def add(id,stamp,category,kind,title,description,entities,evidence,object_id=None):
        items.append(TimelineItem(timeline_id=id,case_id=case,timestamp=stamp,category=category,event_type=kind,title=title,description=description,entity_ids=sorted(set(entities)),evidence_ids=evidence,source_types=sorted({repo.evidence[e].source_type for e in evidence if e in repo.evidence}),object_id=object_id or id))
    for e in repo.events.values():
        # Imported activity appears below as extracted claims, preserving its epistemic status.
        if e.id.startswith('EV-F-'):continue
        covered.update(e.evidence_ids)
        add(e.id,e.timestamp,'OBSERVED_SOURCE_EVENT',e.type,e.type.replace('_',' ').title(),'; '.join(repo.evidence[x].exact_excerpt for x in e.evidence_ids),e.entity_ids,e.evidence_ids)
    for e in repo.evidence.values():
        if e.id not in covered and not e.source_record_id and e.source_type in ['Report','Vehicle']:
            add('source:'+e.id,e.timestamp,'OBSERVED_SOURCE_EVENT','report' if e.source_type=='Report' else 'vehicle_observation',e.source_filename,e.exact_excerpt,e.entity_ids,[e.id])
    for claim in intake['claims']:
        ev=[repo.evidence[e] for e in claim['evidence_ids'] if e in repo.evidence]
        stamp=next((e.timestamp for e in ev if e.timestamp),None)
        kind={'CDR':'call','Transaction':'transfer','Vehicle':'vehicle_observation','Report':'report'}.get(ev[0].source_type if ev else '', 'claim')
        add(claim['claim_id'],stamp,'EXTRACTED_CLAIM',kind,claim['relationship_type']+' · '+claim['disposition'],claim['polarity']+' / '+claim['uncertainty']+'. '+claim['explanation']+' '+('Timestamp not specified in source.' if stamp is None else ''),[x for x in [claim['subject_id'],claim['object_id']] if x],claim['evidence_ids'])
    for signal in analysis.signals:
        add(signal.signal_id,signal.generated_at,'ANALYTICAL_SIGNAL',signal.signal_type,signal.title,'Replay analysis timestamp. '+signal.calculation,signal.involved_entity_ids,signal.supporting_evidence_ids)
    for event in audit:
        items.append(TimelineItem(timeline_id=event.audit_event_id,case_id=case,timestamp=event.created_at,category='HUMAN_SYSTEM_ACTION',event_type=event.action,title=event.action.replace('_',' '),description=event.actor+' · '+event.object_type+' '+event.object_id+' · '+event.reason,entity_ids=event.involved_entity_ids,evidence_ids=event.evidence_ids,source_types=event.source_types or sorted({repo.evidence[e].source_type for e in event.evidence_ids if e in repo.evidence}),object_id=event.object_id))
    return chronological(items,lambda x:x.timestamp)
