"""Typed contracts for the read-only, synthetic golden-flow demo."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

class ExtractionProvenance(Model):
    source_id: str
    evidence_id: str
    evidence_text: str
    span_start: int | None = None
    span_end: int | None = None
    extraction_method: str
    confidence: float | None = None


class Entity(Model):
    id: str
    label: str
    display_label: str
    type: Literal['Person', 'Phone', 'Account', 'Vehicle', 'Location', 'Organization']
    identifier: str
    description: str
    x: float
    y: float
    evidence_ids: list[str]
    aliases: list[str] = []
    original_entity_ids: list[str] = []
    verification_status: str = 'Synthetic source record · not independently verified'
    extractor_version: str | None = None
    extraction_provenance: list[ExtractionProvenance] = []


class Relationship(Model):
    id: str
    source: str
    target: str
    type: str
    status: Literal['recorded', 'inferred'] = 'recorded'
    evidence_ids: list[str] = Field(min_length=1)
    event_ids: list[str] = []
    original_source: str | None = None
    original_target: str | None = None
    verification_status: str = 'Synthetic source record · not independently verified'
    extractor_version: str | None = None
    extraction_provenance: list[ExtractionProvenance] = []


class Locator(Model):
    row: int | None = None
    page: int | None = None
    paragraph: int | None = None
    span_start: int | None = None
    span_end: int | None = None
    fields: list[str]


class Evidence(Model):
    id: str
    source_id: str
    source_filename: str
    source_type: Literal['CDR', 'Transaction', 'Report', 'Vehicle']
    locator: Locator
    timestamp: datetime | None
    exact_excerpt: str
    verification_status: Literal['Synthetic source record · not independently verified','UNVERIFIED']
    entity_ids: list[str]
    relationship_ids: list[str]
    parser_version: str | None = None
    source_record_id: str | None = None


class Source(Model):
    id: str
    filename: str
    type: Literal['CDR', 'Transaction', 'Report', 'Vehicle']
    description: str
    representation: Literal['canonical_synthetic_records','uploaded_synthetic_file']
    evidence_ids: list[str]


class Event(Model):
    id: str
    type: Literal['call', 'transfer', 'report', 'vehicle_observation']
    timestamp: datetime
    entity_ids: list[str]
    evidence_ids: list[str]
    relationship_ids: list[str]
    amount_inr: Decimal | None = None
    duration_seconds: int | None = None
    transaction_id: str | None = None


class Case(Model):
    id: str
    name: str
    classification: str = 'Synthetic Demonstration'
    status: str = 'Active Review'
    timezone: str
    description: str
    event_label: str
    event_timestamp: datetime
    source_default: str
    target_default: str
    focus_entity_ids: list[str]
    max_depth: int


class Meta(Model):
    case_id: str = 'VEIL-DEMO-001'
    synthetic: Literal[True] = True
    data_version: Literal['golden-v1'] = 'golden-v1'


class CaseResponse(Meta):
    case: Case
    counts: dict[str, int]


class GraphResponse(Meta):
    nodes: list[Entity]
    relationships: list[Relationship]


class SourcesResponse(Meta):
    sources: list[Source]


class EvidenceResponse(Meta):
    evidence: Evidence


class Step(Model):
    from_id: str
    to_id: str
    relationship_id: str
    traversal: Literal['forward', 'reverse']
    evidence_ids: list[str]


class PathResponse(GraphResponse):
    node_ids: list[str]
    relationship_ids: list[str]
    evidence_ids: list[str]
    steps: list[Step]
    path_length: int
    max_depth: int
    method: str = 'NetworkX bounded shortest path · undirected associations · deterministic ID ordering'
    disclaimer: str = 'A connected path is an investigative lead, not proof of criminal activity or a chronological sequence.'


class ErrorDetail(Model):
    code: str
    message: str


class ErrorResponse(Model):
    error: ErrorDetail
