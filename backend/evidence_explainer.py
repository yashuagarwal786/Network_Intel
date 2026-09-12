"""Grounded evidence explanations over facts computed elsewhere.

The language model never receives authority to discover edges, score people or
create evidence. It may only rephrase an allowlisted FindingPacket. Any API,
schema or grounding failure returns a deterministic explanation.
"""
from __future__ import annotations
import json
import os
import re
from typing import Any
import httpx
from .demo_repository import DemoRepository
from .demo_schemas import PathResponse
from .explanation_models import EvidenceExplanation, ExplanationDraft, FindingFact, FindingPacket
from .lead_models import ComputedLead

GROQ_URL='https://api.groq.com/openai/v1/chat/completions'
DEFAULT_MODEL='openai/gpt-oss-20b'
FORBIDDEN=(r'\bguilty\b',r'\bcriminal\b',r'\bmastermind\b',r'\bculprit\b',r'\bprobability of guilt\b')


def _label(repo: DemoRepository, entity_id: str) -> str:
    entity=repo.entities.get(entity_id)
    return entity.display_label if entity else entity_id


def packet_for_lead(repo: DemoRepository, lead: ComputedLead) -> FindingPacket:
    labels=', '.join(_label(repo,i) for i in lead.involved_entity_ids[:6])
    path=next((signal.path for signal in lead.signals if signal.path),None)
    summary=(f'{_label(repo,path.node_ids[0])} and {_label(repo,path.node_ids[-1])} have no direct recorded edge in this result; a computed {path.path_length}-hop association path connects their records through source-backed relationships.' if path else f'The deterministic backend surfaced {lead.title.casefold()} across {len(lead.signal_categories)} independent review categories.')
    facts=[FindingFact(fact_id='lead-summary',statement=summary,entity_ids=lead.involved_entity_ids,evidence_ids=lead.evidence_ids)]
    facts.append(FindingFact(fact_id='involved-records',statement=f'The computed finding involves these records: {labels}.',entity_ids=lead.involved_entity_ids,evidence_ids=lead.evidence_ids))
    for index,signal in enumerate(lead.signals,1):
        facts.append(FindingFact(fact_id=f'signal-{index}',statement=f'{signal.title}. {signal.calculation}',entity_ids=signal.involved_entity_ids,evidence_ids=signal.supporting_evidence_ids))
        if signal.path:
            path=signal.path
            facts.append(FindingFact(fact_id=f'path-{index}',statement=f'{_label(repo,path.node_ids[0])} and {_label(repo,path.node_ids[-1])} are connected by a computed {path.path_length}-hop association path with evidence on every step.',entity_ids=path.node_ids,relationship_ids=path.relationship_ids,evidence_ids=path.evidence_ids))
    return FindingPacket(case_id=lead.case_id,finding_id=lead.lead_id,finding_type='LEAD',facts=facts,involved_entity_ids=lead.involved_entity_ids,supporting_evidence_ids=lead.evidence_ids)


def packet_for_path(repo: DemoRepository, path: PathResponse) -> FindingPacket:
    names=[_label(repo,i) for i in path.node_ids]
    facts=[FindingFact(fact_id='path-summary',statement=f'{names[0]} and {names[-1]} have no asserted direct edge in this result; the bounded graph search found a {path.path_length}-hop association path.',entity_ids=path.node_ids,relationship_ids=path.relationship_ids,evidence_ids=path.evidence_ids)]
    for index,step in enumerate(path.steps,1):
        relation=next(r for r in path.relationships if r.id==step.relationship_id)
        facts.append(FindingFact(fact_id=f'path-step-{index}',statement=f'{_label(repo,step.from_id)} is connected to {_label(repo,step.to_id)} by the recorded {relation.type.replace("_"," ")} relationship ({step.traversal} traversal).',entity_ids=[step.from_id,step.to_id],relationship_ids=[step.relationship_id],evidence_ids=step.evidence_ids))
    return FindingPacket(case_id=repo.case.id,finding_id=f'{path.node_ids[0]}::{path.node_ids[-1]}',finding_type='PATH',facts=facts,involved_entity_ids=path.node_ids,supporting_evidence_ids=path.evidence_ids)


def _fallback(packet: FindingPacket, reason: str | None=None) -> EvidenceExplanation:
    primary=packet.facts[0]
    signal_facts=[f for f in packet.facts if f.fact_id.startswith('signal-')]
    short=[f.statement.split('. ',1)[0].rstrip('.') for f in signal_facts]
    why=('The backend surfaced this finding because: '+'; '.join(short[:4])+'.') if short else primary.statement
    return EvidenceExplanation(case_id=packet.case_id,finding_id=packet.finding_id,finding_type=packet.finding_type,explanation=primary.statement,why_flagged=why,review_suggestion='Review the cited source records and assess whether an ordinary explanation accounts for the observed connections.',fact_ids=[f.fact_id for f in packet.facts],supporting_evidence_ids=packet.supporting_evidence_ids,generation_mode='DETERMINISTIC_FALLBACK',provider='local-rules',grounding_status='FALLBACK',fallback_reason=reason,caution=packet.caution)


def _schema() -> dict[str,Any]:
    return {'type':'object','properties':{'explanation':{'type':'string'},'why_flagged':{'type':'string'},'review_suggestion':{'type':'string'},'fact_ids':{'type':'array','items':{'type':'string'}}},'required':['explanation','why_flagged','review_suggestion','fact_ids'],'additionalProperties':False}


def _validate(draft: ExplanationDraft, packet: FindingPacket) -> None:
    known={f.fact_id for f in packet.facts}
    if not set(draft.fact_ids)<=known:raise ValueError('Model cited an unknown fact ID.')
    if not draft.fact_ids:raise ValueError('Model cited no facts.')
    combined=' '.join([draft.explanation,draft.why_flagged,draft.review_suggestion])
    if any(re.search(pattern,combined,re.I) for pattern in FORBIDDEN):raise ValueError('Model used prohibited accusatory language.')
    allowed_numbers=set(re.findall(r'\b\d+(?:\.\d+)?\b',' '.join(f.statement for f in packet.facts)))
    generated_numbers=set(re.findall(r'\b\d+(?:\.\d+)?\b',combined))
    if not generated_numbers<=allowed_numbers:raise ValueError('Model introduced a number absent from the finding packet.')


def explain(packet: FindingPacket, api_key: str | None=None, client: Any | None=None, model: str | None=None) -> EvidenceExplanation:
    key=api_key if api_key is not None else os.getenv('GROQ_API_KEY','').strip()
    chosen=model or os.getenv('GROQ_MODEL',DEFAULT_MODEL)
    if not key:return _fallback(packet,'GROQ_API_KEY is not configured; no external AI claim is made.')
    facts=[{'fact_id':f.fact_id,'statement':f.statement} for f in packet.facts]
    payload={'model':chosen,'temperature':0,'messages':[{'role':'system','content':'You explain an investigator finding using only the supplied facts. Do not add names, edges, evidence, numbers, scores, intent, guilt or conclusions. Use cautious neutral language. Cite every used fact via fact_ids. Return JSON only.'},{'role':'user','content':json.dumps({'facts':facts,'caution':packet.caution})}], 'response_format':{'type':'json_schema','json_schema':{'name':'grounded_evidence_explanation','strict':True,'schema':_schema()}}}
    owned=client is None
    http=client or httpx.Client(timeout=8.0)
    try:
        response=http.post(GROQ_URL,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=payload)
        response.raise_for_status()
        content=response.json()['choices'][0]['message']['content']
        draft=ExplanationDraft.model_validate_json(content)
        _validate(draft,packet)
        used=set(draft.fact_ids)
        evidence=sorted({e for f in packet.facts if f.fact_id in used for e in f.evidence_ids})
        if not evidence:raise ValueError('Model explanation has no supporting evidence.')
        return EvidenceExplanation(case_id=packet.case_id,finding_id=packet.finding_id,finding_type=packet.finding_type,**draft.model_dump(),supporting_evidence_ids=evidence,generation_mode='GROQ_GROUNDED',provider='groq',model=chosen,grounding_status='VALIDATED',caution=packet.caution)
    except Exception as exc:
        return _fallback(packet,f'Grounded generation unavailable: {type(exc).__name__}.')
    finally:
        if owned:http.close()
