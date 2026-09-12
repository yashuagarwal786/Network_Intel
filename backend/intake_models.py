from typing import Literal
from pydantic import Field
from .demo_schemas import Model

CURRENT_PARSER_VERSION = 'controlled-intake-v1'

EpistemicStatus = Literal[
    'EXTRACTED_UNVERIFIED',
    'INVESTIGATOR_VERIFIED',
    'INVESTIGATOR_REJECTED',
    'INVESTIGATOR_CORROBORATED',
    'INFERRED_CANDIDATE',
    'UNVERIFIED'
]

class ClaimReviewInput(Model):
    status: Literal['INVESTIGATOR_VERIFIED', 'INVESTIGATOR_REJECTED', 'INVESTIGATOR_CORROBORATED', 'EXTRACTED_UNVERIFIED']
    reviewer: str = 'Demo investigator'
    reason: str = ''

SourceType=Literal['CDR','Transaction','Vehicle','Report']
class UploadSource(Model):
    filename: str = Field(min_length=1,max_length=100)
    source_type: SourceType
    content: str = Field(min_length=1,max_length=65536)

class Manifest(Model):
    source_file_id: str
    case_id: str = 'VEIL-DEMO-001'
    filename: str
    source_type: SourceType
    checksum: str
    parser_version: str = CURRENT_PARSER_VERSION
    uploaded_at: str
    record_count: int = 0
    processing_status: Literal['VALIDATED','VALIDATED_WITH_ERRORS','INVALID','PROCESSED','PROCESSED_WITH_ERRORS']
    validation_errors: list[str] = []

class Record(Model):
    record_id: str
    source_file_id: str
    filename: str
    source_type: SourceType
    row: int | None = None
    span_start: int
    span_end: int
    raw_excerpt: str
    raw_fields: dict[str,str] = {}
    normalized_fields: dict[str,str] = {}
    parser_version: str = CURRENT_PARSER_VERSION
    verification_status: EpistemicStatus = 'UNVERIFIED'
    status: Literal['VALID','INVALID']
    validation_errors: list[str] = []

class Mention(Model):
    mention_id: str
    record_id: str
    source_file_id: str
    source_id: str | None = None
    kind: str
    raw_value: str
    normalized_value: str
    field: str | None = None
    evidence_id: str
    extractor_version: str = CURRENT_PARSER_VERSION
    extraction_method: str = 'deterministic-rule'
    confidence: float | None = None
    evidence_text: str = ''
    span_start: int | None = None
    span_end: int | None = None
    verification_status: EpistemicStatus = 'UNVERIFIED'
    entity_id: str | None = None

class Claim(Model):
    claim_id: str
    record_id: str
    source_file_id: str
    source_id: str | None = None
    subject_id: str | None
    object_id: str | None
    relationship_type: str
    polarity: Literal['POSITIVE','NEGATIVE','UNKNOWN']
    uncertainty: Literal['ASSERTED','POSSIBLE','UNKNOWN']
    disposition: Literal['GRAPH_CANDIDATE','NEGATED','UNCERTAIN','UNSUPPORTED']
    explanation: str
    evidence_ids: list[str]
    extractor_version: str = CURRENT_PARSER_VERSION
    extraction_method: str = 'deterministic-rule'
    confidence: float | None = None
    evidence_text: str = ''
    span_start: int | None = None
    span_end: int | None = None
    verification_status: EpistemicStatus = 'UNVERIFIED'
    reviewed_by: str | None = None
    review_reason: str | None = None
    reviewed_at: str | None = None

class Summary(Model):
    manifests: list[Manifest]
    records_processed: int
    valid_records: int
    rejected_records: int
    entity_mentions: int
    relationship_candidates: int
    withheld_claims: int
    processed: bool
    parser_version: str = CURRENT_PARSER_VERSION
    needs_reprocess: bool = False
    reprocess_reason: str = ''

class RecordsResponse(Model):
    records: list[Record]

class ClaimsResponse(Model):
    mentions: list[Mention]
    claims: list[Claim]

class ResetInput(Model):
    reload_samples: bool = True

class CreateCaseInput(Model):
    name: str = Field(min_length=3,max_length=80)
    reference: str = Field(min_length=3,max_length=40,pattern=r'^[A-Za-z0-9][A-Za-z0-9-]*$')
    purpose: str = Field(min_length=3,max_length=240)
    event_timestamp: str = '2026-08-18T20:00:00+05:30'
