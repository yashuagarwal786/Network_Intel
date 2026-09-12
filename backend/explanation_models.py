"""Typed boundary between deterministic findings and optional language generation."""
from typing import Literal
from pydantic import Field
from .demo_schemas import Model


class FindingFact(Model):
    fact_id: str
    statement: str
    entity_ids: list[str] = []
    relationship_ids: list[str] = []
    evidence_ids: list[str] = []


class FindingPacket(Model):
    case_id: str
    finding_id: str
    finding_type: Literal['LEAD','PATH']
    facts: list[FindingFact] = Field(min_length=1)
    involved_entity_ids: list[str]
    supporting_evidence_ids: list[str] = Field(min_length=1)
    caution: str = 'Investigative lead, not proof of guilt.'


class ExplanationDraft(Model):
    explanation: str = Field(min_length=10,max_length=700)
    why_flagged: str = Field(min_length=10,max_length=500)
    review_suggestion: str = Field(min_length=10,max_length=300)
    fact_ids: list[str] = Field(min_length=1)


class EvidenceExplanation(Model):
    case_id: str
    finding_id: str
    finding_type: Literal['LEAD','PATH']
    explanation: str
    why_flagged: str
    review_suggestion: str
    fact_ids: list[str]
    supporting_evidence_ids: list[str]
    generation_mode: Literal['GROQ_GROUNDED','DETERMINISTIC_FALLBACK']
    provider: str
    model: str | None = None
    grounding_status: Literal['VALIDATED','FALLBACK']
    fallback_reason: str | None = None
    caution: str = 'Investigative lead, not proof of guilt.'
