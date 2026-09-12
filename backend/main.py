"""Golden-flow API with reversible resolution decisions; legacy detection is disabled."""
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .demo_repository import DemoRepository
from .demo_paths import compute_path
from .demo_schemas import (CaseResponse, GraphResponse, SourcesResponse,
                           EvidenceResponse, PathResponse, ErrorResponse)

from datetime import datetime
from .review_store import ReviewStore, ReviewInput, Review, AuditEvent, ReviewConflict
from .activity import TimelineItem, build_timeline, chronological
from pathlib import Path
import os
from .resolution import (proposals, project, ResolutionStore, DecisionInput, ResolutionDecision,
                         ProposalResponse, ProposalsResponse, DecisionConflict)
from .intake_store import IntakeStore, IntakeError
from .intake_models import UploadSource, Manifest, Summary, RecordsResponse, ClaimsResponse, Record, ResetInput, CreateCaseInput, CURRENT_PARSER_VERSION, ClaimReviewInput, Claim
from pydantic import ValidationError
intake_store = IntakeStore(os.environ.get('VEIL_INTAKE_DB', str(Path(__file__).with_name('data')/'intake.sqlite3')))
from .lead_engine import run_engine
from .lead_models import EngineResult, ComputedLeadResponse, ComputedSignal
from .explanation_models import EvidenceExplanation
from .evidence_explainer import explain, packet_for_lead, packet_for_path
from .behavioral_profiler import run_behavioral_profiler
from . import ner_service
review_store = ReviewStore(os.environ.get('VEIL_REVIEW_DB', str(Path(__file__).with_name('data')/'investigator_journal.sqlite3')))
repository = DemoRepository()
matches = proposals(repository)
resolution_store = ResolutionStore(os.environ.get('VEIL_RESOLUTION_DB', str(Path(__file__).with_name('data')/'resolution.sqlite3')))
app = FastAPI(title='VEIL - Golden Judge Flow',version='1.0.0')

def current_repository():
    return intake_store.augment(repository)

def current_matches():
    return proposals(current_repository())

def current_case_id():
    return current_repository().case.id

class DemoError(Exception):
    def __init__(self, code, message, status=404):
        self.code,self.message,self.status = code,message,status

@app.exception_handler(DemoError)
async def domain_error(request: Request, exc: DemoError):
    return JSONResponse(status_code=exc.status,content={'error':{'code':exc.code,'message':exc.message}})

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    message='; '.join(f"{'.'.join(map(str,e['loc'][1:]))}: {e['msg']}" for e in exc.errors())
    return JSONResponse(status_code=422,content={'error':{'code':'INVALID_REQUEST','message':message}})

ERRORS={404:{'model':ErrorResponse},409:{'model':ErrorResponse},422:{'model':ErrorResponse}}

@app.get('/api/cases/demo',response_model=CaseResponse)
def demo_case():
    current=current_repository()
    projected,_=project(current,current_matches(),resolution_store)
    counts={key:len(getattr(current,key)) for key in ['entities','relationships','evidence','sources']}
    counts['leads']=len(run_engine(projected).leads)
    return CaseResponse(case_id=current.case.id,case=current.case,counts=counts)

@app.get('/api/cases/demo/sources',response_model=SourcesResponse)
def sources():return SourcesResponse(case_id=current_case_id(),sources=list(current_repository().sources.values()))

@app.get('/api/cases/demo/graph',response_model=GraphResponse)
def graph():
    current,_=project(current_repository(),current_matches(),resolution_store)
    return GraphResponse(case_id=current.case.id,nodes=list(current.entities.values()),relationships=list(current.relationships.values()))

def computed_analysis():
    current,_=project(current_repository(),current_matches(),resolution_store)
    result=run_engine(current)
    result.case_id=current.case.id
    result.leads=[review_store.decorate(l) for l in result.leads]
    return result

@app.get('/api/cases/demo/leads',response_model=EngineResult)
def leads():return computed_analysis()

@app.get('/api/leads/{lead_id}',response_model=ComputedLeadResponse,responses=ERRORS)
def lead(lead_id: str):
    found=next((lead for lead in computed_analysis().leads if lead.lead_id==lead_id),None)
    if found is None:raise DemoError('LEAD_NOT_FOUND','No computed lead currently meets the policy for this ID.')
    review_store.append(current_case_id(),'Local demo session','HUMAN','LEAD_OPENED','lead',lead_id,new_state={'lead_revision':found.lead_revision},involved_entity_ids=found.involved_entity_ids,evidence_ids=found.evidence_ids)
    return ComputedLeadResponse(lead=found)

@app.get('/api/leads/{lead_id}/explanation',response_model=EvidenceExplanation,responses=ERRORS)
def lead_explanation(lead_id: str):
    current,_=project(current_repository(),current_matches(),resolution_store)
    found=current_lead(lead_id)
    return explain(packet_for_lead(current,found))

@app.get('/api/cases/demo/signals',response_model=list[ComputedSignal])
def signals():return computed_analysis().signals

@app.get('/api/evidence/{evidence_id}',response_model=EvidenceResponse,responses=ERRORS)
def evidence(evidence_id: str):
    current=intake_store.augment(repository)
    if evidence_id not in current.evidence:raise DemoError('EVIDENCE_NOT_FOUND',f'Evidence {evidence_id} was not found. Open a reference from the graph or lead.')
    ev=current.evidence[evidence_id]
    review_store.append(current_case_id(),'Local demo session','HUMAN','EVIDENCE_OPENED','evidence',evidence_id,new_state={'access':'opened'},involved_entity_ids=ev.entity_ids,evidence_ids=[ev.id],source_types=[ev.source_type])
    return EvidenceResponse(case_id=current_case_id(),evidence=ev)

@app.get('/api/cases/demo/path',response_model=PathResponse,responses=ERRORS)
def path(source: str=Query(min_length=1,max_length=80),target: str=Query(min_length=1,max_length=80),max_depth: int=Query(default=8,ge=1,le=8)):
    combined=current_repository()
    for entity_id in [source,target]:
        if entity_id not in combined.entities:raise DemoError('ENTITY_NOT_FOUND',f'Entity {entity_id} was not found. Choose a name or identifier from this case.')
    current,canonical=project(combined,current_matches(),resolution_store)
    result=compute_path(current,canonical[source],canonical[target],max_depth)
    if result is None:raise DemoError('NO_PATH_WITHIN_DEPTH',f'No recorded association path was found within {max_depth} hops. The entities may be disconnected; maximum supported depth is 8.')
    return result

@app.get('/api/cases/demo/path/explanation',response_model=EvidenceExplanation,responses=ERRORS)
def path_explanation(source: str=Query(min_length=1,max_length=80),target: str=Query(min_length=1,max_length=80),max_depth: int=Query(default=8,ge=1,le=8)):
    combined=current_repository()
    for entity_id in [source,target]:
        if entity_id not in combined.entities:raise DemoError('ENTITY_NOT_FOUND',f'Entity {entity_id} was not found. Choose a name or identifier from this case.')
    current,canonical=project(combined,current_matches(),resolution_store)
    result=compute_path(current,canonical[source],canonical[target],max_depth)
    if result is None:raise DemoError('NO_PATH_WITHIN_DEPTH',f'No recorded association path was found within {max_depth} hops.')
    return explain(packet_for_path(current,result))


def proposal_detail(proposal_id):
    active=current_matches()
    if proposal_id not in active:raise DemoError('PROPOSAL_NOT_FOUND','Resolution proposal not found.')
    p=active[proposal_id].model_copy(update={'status':resolution_store.state(proposal_id)})
    return ProposalResponse(proposal=p,decisions=resolution_store.history(proposal_id))

@app.get('/api/cases/demo/resolution-proposals',response_model=ProposalsResponse)
def resolution_proposals():
    return ProposalsResponse(proposals=[proposal_detail(id).proposal for id in current_matches()])

@app.get('/api/cases',include_in_schema=False)
def case_list():
    current=demo_case()
    return {'cases':[{'id':current.case.id,'name':current.case.name,'status':current.case.status,'description':current.case.description,'counts':current.counts,'active':True},{'id':'NI-2026-025','name':'Operation Crosswind','status':'Ready for ingestion','description':'Multi-hop narcotics and Hawala corridor across 4 source types','counts':{'entities':12,'relationships':10,'leads':2},'active':False},{'id':'NI-2026-011','name':'Financial Link Review','status':'Review complete','description':'Synthetic archived workspace','counts':{'entities':38,'relationships':31,'leads':0},'active':False},{'id':'NI-2026-012','name':'Interstate Contact Review','status':'Awaiting evidence','description':'Synthetic archived workspace','counts':{'entities':24,'relationships':19,'leads':1},'active':False}]}

@app.post('/api/cases',include_in_schema=False)
def create_case(body: CreateCaseInput):
    intake_store.create_case(body)
    return demo_case()

@app.get('/api/resolution-proposals/{proposal_id}',response_model=ProposalResponse,responses=ERRORS)
def resolution_proposal(proposal_id: str):return proposal_detail(proposal_id)

@app.post('/api/resolution-proposals/{proposal_id}/decisions',response_model=ResolutionDecision,responses=ERRORS)
def decision(proposal_id: str,body: DecisionInput):
    proposal_detail(proposal_id)
    try:
        result=resolution_store.decide(proposal_id,body)
        sync_resolution_audit()
        return result
    except DecisionConflict as exc:raise DemoError('DECISION_CONFLICT',str(exc),409)

@app.post('/api/resolution-decisions/{decision_id}/undo',response_model=ResolutionDecision,responses=ERRORS)
def undo(decision_id: str,body: DecisionInput):
    original=resolution_store.find(decision_id)
    if not original:raise DemoError('DECISION_NOT_FOUND','Resolution decision not found.')
    if body.action!='UNDO_CONFIRMED_MATCH':raise DemoError('INVALID_ACTION','Undo requires UNDO_CONFIRMED_MATCH.',422)
    if original.action!='CONFIRM_MATCH':raise DemoError('DECISION_CONFLICT','Only confirmations can be undone.',409)
    try:
        result=resolution_store.decide(original.proposal_id,body,decision_id)
        sync_resolution_audit()
        return result
    except DecisionConflict as exc:raise DemoError('DECISION_CONFLICT',str(exc),409)


@app.exception_handler(IntakeError)
async def intake_error(request: Request, exc: IntakeError):
    return JSONResponse(status_code=422,content={'error':{'code':'INVALID_SOURCE','message':str(exc)}})

@app.post('/api/cases/demo/sources/upload',response_model=Manifest,responses=ERRORS)
async def upload_source(request: Request):
    if request.headers.get('content-type','').split(';')[0]!='application/json':
        raise DemoError('UNSUPPORTED_MEDIA_TYPE','Send UTF-8 text in a JSON filename/source_type/content envelope.',415)
    data=bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data)>400000:raise DemoError('FILE_TOO_LARGE','Upload request exceeds the bounded JSON envelope limit.',413)
    try:body=UploadSource.model_validate_json(data)
    except ValidationError as exc:raise DemoError('INVALID_SOURCE','Invalid upload envelope: '+str(exc.errors()[0]['msg']),422)
    result=intake_store.upload(body)
    sync_intake_audit()
    return result

@app.post('/api/cases/demo/process',response_model=Summary)
def process_sources():
    result=intake_store.process()
    sync_intake_audit()
    return result

@app.post('/api/cases/demo/intake/reprocess',response_model=Summary,include_in_schema=False)
def reprocess_sources():
    result=intake_store.process()
    sync_intake_audit()
    return result

@app.get('/api/cases/demo/processing-summary',response_model=Summary)
def processing_summary():return intake_store.summary()

@app.get('/api/cases/demo/source-records',response_model=RecordsResponse)
def source_records():return RecordsResponse(records=intake_store.read()['records'])

@app.get('/api/source-records/{record_id}',response_model=Record,responses=ERRORS)
def source_record(record_id: str):
    record=next((r for r in intake_store.read()['records'] if r['record_id']==record_id),None)
    if record is None:raise DemoError('RECORD_NOT_FOUND','Source record not found. Process a loaded source first.')
    return Record.model_validate(record)

@app.get('/api/cases/demo/extracted-claims',response_model=ClaimsResponse)
def extracted_claims():
    state=intake_store.read();return ClaimsResponse(mentions=state['mentions'],claims=state['claims'])

@app.post('/api/claims/{claim_id}/review',response_model=Claim,responses=ERRORS,include_in_schema=False)
def review_claim_endpoint(claim_id: str, body: ClaimReviewInput):
    try:
        updated = intake_store.review_claim(claim_id, body.status, body.reviewer, body.reason)
        review_store.append(
            current_case_id(),
            body.reviewer,
            'HUMAN',
            'CLAIM_VERIFICATION_REVIEW',
            'claim',
            claim_id,
            new_state={'verification_status': body.status, 'reason': body.reason},
            reason=body.reason
        )
        return updated
    except IntakeError as exc:
        raise DemoError('CLAIM_NOT_FOUND', str(exc), 404)

@app.post('/api/cases/demo/intake/reset',response_model=Summary)
def reset_intake(body: ResetInput):
    result=intake_store.reset(body.reload_samples)
    sync_intake_audit()
    return result

@app.get('/api/cases/demo/ner-status',include_in_schema=False)
def ner_status():
    available=ner_service.is_available()
    model=ner_service.DEFAULT_MODEL
    ver=ner_service.current_extractor_version()
    status_text=f"NER Model: {model} • Active" if available else "NER Model unavailable • Structured extraction only"
    return {
        "available":available,
        "model":model,
        "extractor_version":ver,
        "status_text":status_text
    }

@app.get('/api/cases/demo/source-files',include_in_schema=False)
def source_files():
    state=intake_store.read()
    return [{'manifest':f['manifest'],'content':f['content']} for f in state.get('files',[])]

@app.post('/api/cases/demo/load-demo-report',include_in_schema=False)
def load_demo_report():
    sample_content=(
        "Field Intelligence Dispatch. Case VEIL-DEMO-001. Date 14 August 2026.\n"
        "Vikram Singh met Arjun Mehta near Jaipur Railway Station before contacting Meridian Logistics.\n"
        "Kavya Rao was observed meeting with Devansh Batra in New Delhi.\n"
        "Meridian Logistics operates vehicle DEMO-VH-02 from warehouse near Jaipur.\n"
        "Suspect uses phone +910000000303 for unlisted coordination.\n"
        "Wire transfer of INR 150000.00 routed to account DEMO-A777 on 14 August 2026.\n"
    )
    manifest=intake_store.upload(UploadSource(
        filename='field_dispatch_report.txt',
        source_type='Report',
        content=sample_content
    ))
    intake_store.process()
    sync_intake_audit()
    return {'manifest':manifest.model_dump(),'summary':intake_store.summary().model_dump()}


def sync_intake_audit():
    # Outbox commits atomically with source changes; this mirror is safe to retry.
    for e in intake_store.journal():
        system=e['action']=='SOURCE_PROCESSED'
        review_store.append(current_case_id(),CURRENT_PARSER_VERSION if system else 'Local demo session','SYSTEM' if system else 'HUMAN',e['action'],'case' if e['action']=='INTAKE_RESET' else 'source',e['object_id'],old_state=e['old_state'],new_state=e['new_state'],dedupe='intake:'+e['id'],created_at=e['created_at'],involved_entity_ids=e['entity_ids'],evidence_ids=e['evidence_ids'],source_types=e['source_types'])

def sync_resolution_audit():
    # Idempotent reconciliation recovers an interrupted audit mirror from durable decisions.
    states={'CONFIRM_MATCH':'CONFIRMED','REJECT_MATCH':'REJECTED','DEFER':'DEFERRED','UNDO_CONFIRMED_MATCH':'REVIEW'}
    for pid,p in current_matches().items():
        old='REVIEW'
        for d in resolution_store.history(pid):
            new=states[d.action]
            review_store.append(current_case_id(),d.reviewer,'HUMAN','RESOLUTION_DECISION_UNDONE' if d.action=='UNDO_CONFIRMED_MATCH' else 'ENTITY_RESOLUTION_DECISION','resolution_proposal',pid,old_state={'status':old},new_state={'status':new,'decision_id':d.decision_id,'decision_action':d.action,'undoes_decision_id':d.undoes_decision_id},reason=d.reason,dedupe='resolution:'+d.decision_id,created_at=d.created_at,involved_entity_ids=[p.left_entity_id,p.right_entity_id],evidence_ids=p.supporting_evidence_ids)
            old=new

def current_lead(lead_id):
    found=next((l for l in computed_analysis().leads if l.lead_id==lead_id),None)
    if found is None:raise DemoError('LEAD_NOT_FOUND','No computed lead currently meets the policy for this ID.')
    return found

@app.post('/api/leads/{lead_id}/reviews',response_model=Review,responses=ERRORS)
def submit_review(lead_id: str,body: ReviewInput):
    found=current_lead(lead_id);object_type='lead';entities=None;evidence_ids=None
    if body.action=='VERIFIED_RELATIONSHIP':
        current,_=project(current_repository(),current_matches(),resolution_store)
        relation=current.relationships.get(body.object_id)
        if relation is None or not set(relation.evidence_ids)&set(found.evidence_ids):raise DemoError('INVALID_REVIEW_OBJECT','Select a supporting relationship from this lead.',422)
        object_type='relationship';entities=[relation.source,relation.target];evidence_ids=relation.evidence_ids
    elif body.action=='INCORRECT_ENTITY_MERGE':
        p=current_matches().get(body.object_id)
        if p is None or resolution_store.state(body.object_id)!='CONFIRMED' or not {p.left_entity_id,p.right_entity_id}&set(found.involved_entity_ids):raise DemoError('INVALID_REVIEW_OBJECT','Select a currently confirmed resolution proposal involved in this lead. Use Resolution review to undo it.',422)
        object_type='resolution_proposal';entities=[p.left_entity_id,p.right_entity_id];evidence_ids=p.supporting_evidence_ids
    elif body.object_id is not None:raise DemoError('INVALID_REVIEW_OBJECT','Object ID applies only to relationship or merge assessments.',422)
    try:return review_store.submit(found,body,object_type,entities,evidence_ids)
    except ReviewConflict as exc:raise DemoError('REVIEW_CONFLICT',str(exc),409)

@app.get('/api/leads/{lead_id}/reviews',response_model=list[Review])
def lead_reviews(lead_id: str):
    history=review_store.history(current_case_id(),lead_id)
    if not history:current_lead(lead_id)
    return history

def validate_range(start,end):
    if any(d and d.utcoffset() is None for d in [start,end]):raise DemoError('INVALID_RANGE','Date filters must include a timezone offset.',422)
    if start and end and start>end:raise DemoError('INVALID_RANGE','Start must not be after end.',422)

@app.get('/api/cases/demo/audit',response_model=list[AuditEvent])
def audit(start: datetime|None=None,end: datetime|None=None,action: str|None=None,actor: str|None=None,object_id: str|None=None):
    validate_range(start,end);sync_resolution_audit();sync_intake_audit()
    entries=review_store.audit(current_case_id())
    return chronological([e for e in entries if (not start or datetime.fromisoformat(e.created_at)>=start) and (not end or datetime.fromisoformat(e.created_at)<=end) and (not action or e.action==action) and (not actor or actor.casefold() in e.actor.casefold()) and (not object_id or e.object_id==object_id)],lambda x:x.created_at)

@app.get('/api/cases/demo/timeline',response_model=list[TimelineItem])
def timeline(start: datetime|None=None,end: datetime|None=None,event_type: str|None=None,entity_id: str|None=None,source_type: str|None=None,category: str|None=None):
    validate_range(start,end);sync_resolution_audit();sync_intake_audit()
    current=intake_store.augment(repository);analysis=computed_analysis()
    _,canonical=project(current,current_matches(),resolution_store)
    if entity_id and entity_id not in canonical:raise DemoError('ENTITY_NOT_FOUND','Timeline entity is not in this case.')
    items=build_timeline(current,intake_store.read(),analysis,review_store.audit(current_case_id()))
    return [i for i in items if (not start or i.timestamp is not None and i.timestamp>=start) and (not end or i.timestamp is not None and i.timestamp<=end) and (not event_type or i.event_type==event_type) and (not category or i.category==category) and (not source_type or source_type in i.source_types) and (not entity_id or any(canonical.get(e,e)==canonical[entity_id] for e in i.entity_ids))]

@app.get('/api/cases/demo/anomalies', include_in_schema=False)
def case_anomalies():
    """Unsupervised Multi-Modal Behavioral Anomaly Detection via Isolation Forest.
    Strictly an investigative triage tool - does NOT predict guilt, intent, or criminality.
    """
    current, _ = project(current_repository(), current_matches(), resolution_store)
    result = run_behavioral_profiler(current)
    return {
        'status': result.status,
        'message': result.message,
        'sample_size': result.sample_size,
        'min_required_sample_size': result.min_required_sample_size,
        'case_id': result.case_id,
        'generated_at': result.generated_at.isoformat(),
        'disclaimer': result.disclaimer,
        'feature_definitions': result.feature_definitions,
        'cohort_stats': result.cohort_stats,
        'profiles': [
            {
                'entity_id': p.entity_id,
                'entity_label': p.entity_label,
                'entity_type': p.entity_type,
                'total_events': p.total_events,
                'anomaly_score': p.anomaly_score,
                'anomaly_percentile': p.anomaly_percentile,
                'is_outlier': p.is_outlier,
                'rank': p.rank,
                'top_drivers': p.top_drivers,
                'feature_deviations': p.feature_deviations,
                'features': p.features,
                'raw_metrics': p.raw_metrics,
                'supporting_evidence_ids': p.supporting_evidence_ids,
                'event_ids': p.event_ids,
                'time_window': {
                    'start': p.time_window.start.isoformat(),
                    'end': p.time_window.end.isoformat(),
                    'timezone': p.time_window.timezone
                }
            }
            for p in result.profiles
        ],
        'signals': [s.model_dump(mode='json') for s in result.signals]
    }

@app.get('/api/cases/demo/network-roles', include_in_schema=False)
def case_network_roles():
    """Explainable Network Roles & Centrality Analysis (Bridge/Facilitator & Hub detection)."""
    current, _ = project(current_repository(), current_matches(), resolution_store)
    from .intelligence import compute_network_roles
    return {'case_id': current.case.id, 'roles': compute_network_roles(current)}

# The built UI is served locally by the same process for the offline judge demo.
# API routes are registered first; a failed API never becomes an HTML fallback.
from fastapi.staticfiles import StaticFiles
@app.api_route('/api/{unmatched:path}',methods=['GET','POST','PUT','PATCH','DELETE'],include_in_schema=False)
def unknown_api(unmatched: str):
    raise DemoError('ENDPOINT_NOT_FOUND','This API endpoint does not exist.',404)

static_root=Path(__file__).resolve().parents[1]/'frontend'/'dist'
if static_root.is_dir():
    app.mount('/',StaticFiles(directory=static_root,html=True),name='demo-ui')
