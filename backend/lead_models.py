"""Computed signal/lead contracts, separate from graph storage."""
from datetime import datetime
from typing import Literal, Any
from pydantic import Field
from .demo_schemas import Model, Meta, PathResponse

class TimeWindow(Model):
    start: datetime
    end: datetime
    timezone: str = 'Asia/Kolkata'
    boundary: str = 'start inclusive; end inclusive unless stated otherwise'

class ComputedSignal(Model):
    signal_id: str
    case_id: str
    signal_type: Literal['COMMUNICATION_BURST','NEW_CONTACT_BURST','TRANSACTION_SEQUENCE','GRAPH_PATH','ANOMALOUS_BEHAVIORAL_PROFILE']
    category: Literal['COMMUNICATION','FINANCIAL','GRAPH_CONTEXT','BEHAVIORAL_ANOMALY']
    independent_category: bool = True
    title: str
    involved_entity_ids: list[str]
    time_window: TimeWindow
    baseline_definition: str
    observed_value: dict[str,Any]
    expected_value: dict[str,Any]
    calculation: str
    threshold: dict[str,Any]
    supporting_evidence_ids: list[str] = Field(min_length=1)
    event_ids: list[str]
    algorithm_version: str
    limitations: list[str]
    generated_at: datetime
    path: PathResponse | None = None

class ComputedLead(Model):
    lead_id: str
    case_id: str
    title: str
    review_priority: Literal['HIGH','MEDIUM','LOW']
    summary: str
    involved_entity_ids: list[str]
    signal_ids: list[str]
    evidence_ids: list[str] = Field(min_length=1)
    generated_at: datetime
    engine_version: str
    review_status: Literal['UNREVIEWED','USEFUL_LEAD','FALSE_POSITIVE','IRRELEVANT','NEEDS_MORE_EVIDENCE','VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE'] = 'UNREVIEWED'
    lead_revision: str = ''
    limitations: list[str]
    disclaimer: str = 'Review priority determines examination order. It is not a probability of criminal activity.'
    signal_categories: list[str]
    priority_explanation: str
    time_window: TimeWindow
    signals: list[ComputedSignal]

class EngineResult(Meta):
    leads: list[ComputedLead]
    signals: list[ComputedSignal]
    engine_version: str
    generated_at: datetime
    generation_clock: str = 'Deterministic replay clock: case analysis timestamp, not request wall time.'
    diagnostics: list[str]

class ComputedLeadResponse(Meta):
    lead: ComputedLead
