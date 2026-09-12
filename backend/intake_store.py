"""Small atomic intake snapshot store; filenames never become filesystem paths."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import json
import re
import sqlite3
from uuid import uuid4
from .intake_models import UploadSource,Manifest,Record,Mention,Claim,Summary,CreateCaseInput,CURRENT_PARSER_VERSION
from .intake_parser import parse,extract,digest
from .demo_schemas import Entity,Relationship,Evidence,Locator,Source,Event,ExtractionProvenance

SAMPLES=Path(__file__).resolve().parents[1]/'demo-data'/'intake'
MAX_BYTES=65536
class IntakeError(ValueError):pass

def empty():return {'files':[], 'records':[], 'mentions':[], 'claims':[], 'processed':False,'case':None}

def add_file(state,upload):
    name=upload.filename
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}\.(csv|txt)',name) or name.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}:raise IntakeError('Use a plain CSV/TXT filename; paths, reserved names and unsupported extensions are not allowed.')
    expected='.txt' if upload.source_type=='Report' else '.csv'
    if not name.endswith(expected):raise IntakeError(f'{upload.source_type} requires {expected}. PDF and other types are not supported in this controlled cycle.')
    if len(upload.content.encode('utf-8'))>MAX_BYTES:raise IntakeError('File exceeds 64 KiB UTF-8 limit.')
    if '\x00' in upload.content or any(ord(c)<32 and c not in '\r\n\t' for c in upload.content):raise IntakeError('Only UTF-8 text without binary control characters is supported.')
    checksum=digest(upload.content)
    for file in state['files']:
        if file['manifest']['checksum']==checksum and file['manifest']['source_type']==upload.source_type:return Manifest.model_validate(file['manifest'])
    if len(state['files'])>=16:raise IntakeError('Maximum 16 source files. Reset intake before loading another batch.')
    manifest=Manifest(source_file_id='F-'+digest(upload.source_type+'|'+checksum)[:20],case_id=(state.get('case') or {}).get('id','VEIL-DEMO-001'),filename=name,source_type=upload.source_type,checksum=checksum,uploaded_at=datetime.now(timezone.utc).isoformat(),processing_status='VALIDATED')
    records,errors=parse(manifest,upload.content)
    manifest.record_count=len(records)
    manifest.validation_errors=errors+[f'Row {r.row or r.span_start}: '+error for r in records for error in r.validation_errors]
    if errors:manifest.processing_status='INVALID'
    elif manifest.validation_errors:manifest.processing_status='VALIDATED_WITH_ERRORS'
    state['files'].append({'manifest':manifest.model_dump(),'content':upload.content})
    state['processed']=False
    return manifest

class IntakeStore:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS intake_audit_outbox (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS intake_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO intake_state VALUES (1,?)',(json.dumps(empty()),))
    def connect(self):return sqlite3.connect(self.path,timeout=10)
    def read(self):
        with self.connect() as db:return json.loads(db.execute('SELECT payload FROM intake_state WHERE id=1').fetchone()[0])
    def journal(self):
        with self.connect() as db:return [json.loads(r[0]) for r in db.execute("SELECT payload FROM intake_audit_outbox ORDER BY seq")]
    def change(self,fn,action):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');state=json.loads(db.execute('SELECT payload FROM intake_state WHERE id=1').fetchone()[0]);before=deepcopy(state);result=fn(state)
            def record(kind,object_id,old,new,source_type=None):
                entry={'id':str(uuid4()),'action':kind,'object_id':object_id,'old_state':old,'new_state':new,'created_at':datetime.now(timezone.utc).isoformat(),'source_types':[source_type] if source_type else [],'evidence_ids':['E-'+r['record_id'] for r in state['records'] if r['source_file_id']==object_id],'entity_ids':sorted({m['entity_id'] for m in state['mentions'] if m['source_file_id']==object_id and m['entity_id']})}
                db.execute('INSERT INTO intake_audit_outbox(payload) VALUES (?)',(json.dumps(entry),))
            if action=='INTAKE_RESET':record(action,(state.get('case') or before.get('case') or {}).get('id','VEIL-DEMO-001'),{'source_ids':[f['manifest']['source_file_id'] for f in before['files']]},{'source_ids':[f['manifest']['source_file_id'] for f in state['files']]})
            old_files={f['manifest']['source_file_id']:f['manifest'] for f in before['files']}
            for file in state['files']:
                m=file['manifest'];id=m['source_file_id']
                if action=='SOURCE_PROCESSED' or action=='INTAKE_RESET' or isinstance(result,Manifest) and result.source_file_id==id:
                    record('SOURCE_UPLOADED' if action=='INTAKE_RESET' else action,id,{} if action=='INTAKE_RESET' else old_files.get(id,{}),m,m['source_type'])
            db.execute('UPDATE intake_state SET payload=? WHERE id=1',(json.dumps(state),));return result
    def upload(self,upload):return self.change(lambda s:add_file(s,upload),'SOURCE_UPLOADED')
    def reset(self,reload_samples):
        def work(state):
            active_case=state.get('case')
            state.clear();state.update(empty())
            state['case']=active_case
            if reload_samples:
                for name,kind in [('report.txt','Report'),('cdr.csv','CDR'),('transactions.csv','Transaction'),('vehicles.csv','Vehicle')]:add_file(state,UploadSource(filename=name,source_type=kind,content=(SAMPLES/name).read_text(encoding='utf-8')))
        self.change(work,'INTAKE_RESET');return self.summary()
    def create_case(self,body: CreateCaseInput):
        def work(state):
            state.clear();state.update(empty())
            state['case']={'id':body.reference.upper(),'name':body.name.strip(),'purpose':body.purpose.strip(),'event_timestamp':body.event_timestamp,'fresh':True}
        self.change(work,'INTAKE_RESET')
        return self.read()['case']
    def process(self):
        def work(state):
            records=[]
            for file in state['files']:
                manifest=Manifest.model_validate(file['manifest']);rows,errors=parse(manifest,file['content']);records.extend(rows)
                manifest.record_count=len(rows);manifest.validation_errors=errors+[f'Row {r.row or r.span_start}: '+e for r in rows for e in r.validation_errors]
                manifest.processing_status='INVALID' if errors else 'PROCESSED_WITH_ERRORS' if manifest.validation_errors else 'PROCESSED'
                file['manifest']=manifest.model_dump()
            mentions,claims=extract(records)
            state.update(records=[r.model_dump() for r in records],mentions=[m.model_dump() for m in mentions],claims=[c.model_dump() for c in claims],processed=True)
        self.change(work,'SOURCE_PROCESSED');return self.summary()
    def review_claim(self, claim_id: str, status: str, reviewer: str = 'Demo investigator', reason: str = ''):
        def work(state):
            claim = next((c for c in state.get('claims', []) if c['claim_id'] == claim_id), None)
            if not claim:
                raise IntakeError(f'Claim {claim_id} not found.')
            claim['verification_status'] = status
            claim['reviewed_by'] = reviewer
            claim['review_reason'] = reason
            claim['reviewed_at'] = datetime.now(timezone.utc).isoformat()
            return Claim.model_validate(claim)
        return self.change(work, 'CLAIM_REVIEWED')

    def summary(self):
        s=self.read()
        records = s.get('records', [])
        mentions = s.get('mentions', [])
        needs_reprocess = False
        reprocess_reason = ''
        if s.get('files') and not s.get('processed'):
            needs_reprocess = True
            reprocess_reason = 'Source files loaded but extraction pipeline has not run.'
        elif records:
            stale = [r for r in records if r.get('parser_version') != CURRENT_PARSER_VERSION]
            missing = [r for r in records if r.get('span_start') is None]
            if stale or missing:
                needs_reprocess = True
                reprocess_reason = f'Parser version mismatch ({len(stale)} stale records) or missing character spans. Reprocess required.'
        return Summary(
            manifests=[Manifest.model_validate(f['manifest']) for f in s['files']],
            records_processed=len(records),
            valid_records=sum(r['status']=='VALID' for r in records),
            rejected_records=sum(r['status']=='INVALID' for r in records),
            entity_mentions=len(mentions),
            relationship_candidates=sum(c['disposition']=='GRAPH_CANDIDATE' for c in s.get('claims', [])),
            withheld_claims=sum(c['disposition']!='GRAPH_CANDIDATE' for c in s.get('claims', [])),
            processed=s.get('processed', False),
            parser_version=CURRENT_PARSER_VERSION,
            needs_reprocess=needs_reprocess,
            reprocess_reason=reprocess_reason
        )
    def augment(self,base):
        s=self.read();repo=deepcopy(base)
        if (s.get('case') or {}).get('fresh'):
            repo.entities={};repo.relationships={};repo.events={};repo.evidence={};repo.sources={};repo.leads={}
        records={r['record_id']:Record.model_validate(r) for r in s['records']}
        mentions=[Mention.model_validate(m) for m in s['mentions']];claims=[Claim.model_validate(c) for c in s['claims']]
        for m in mentions:
            if not m.entity_id:continue
            if m.entity_id not in repo.entities:
                origin=records[m.record_id].filename
                label=m.normalized_value+(' ('+origin+')' if m.kind=='Person' else '')
                repo.entities[m.entity_id]=Entity(id=m.entity_id,label=label,display_label=m.normalized_value,type=m.kind,identifier=m.normalized_value,description=f'Machine-extracted source mention from {origin}. UNVERIFIED; names are not automatically merged with existing people.',x=50,y=50,evidence_ids=[],verification_status='UNVERIFIED',extractor_version=m.extractor_version,extraction_provenance=[])
            if m.evidence_id not in repo.entities[m.entity_id].evidence_ids:repo.entities[m.entity_id].evidence_ids.append(m.evidence_id)
            prov = ExtractionProvenance(source_id=m.source_file_id,evidence_id=m.evidence_id,evidence_text=m.evidence_text or m.raw_value,span_start=m.span_start,span_end=m.span_end,extraction_method=m.extraction_method,confidence=m.confidence)
            if not any(p.evidence_id == prov.evidence_id and p.span_start == prov.span_start for p in repo.entities[m.entity_id].extraction_provenance):
                repo.entities[m.entity_id].extraction_provenance.append(prov)
        for c in claims:
            if c.verification_status == 'INVESTIGATOR_REJECTED':
                continue
            if c.disposition=='GRAPH_CANDIDATE' and c.subject_id and c.object_id:
                rel_prov = [ExtractionProvenance(source_id=c.source_file_id,evidence_id=eid,evidence_text=c.evidence_text,span_start=c.span_start,span_end=c.span_end,extraction_method=c.extraction_method,confidence=c.confidence) for eid in c.evidence_ids]
                repo.relationships[c.claim_id]=Relationship(id=c.claim_id,source=c.subject_id,target=c.object_id,type=c.relationship_type,status='recorded',evidence_ids=c.evidence_ids,verification_status=c.verification_status,extractor_version=c.extractor_version,extraction_provenance=rel_prov)
                r=records[c.record_id];fields=r.normalized_fields
                if r.source_type in ['CDR','Transaction']:
                    event_id='EV-'+r.record_id
                    repo.events[event_id]=Event(id=event_id,type='call' if r.source_type=='CDR' else 'transfer',timestamp=fields.get('started_at') or fields['occurred_at'],entity_ids=[c.subject_id,c.object_id],evidence_ids=c.evidence_ids,relationship_ids=[c.claim_id],amount_inr=fields.get('amount'),duration_seconds=fields.get('duration_seconds'),transaction_id=fields.get('transaction_id'))
                    repo.relationships[c.claim_id].event_ids=[event_id]
        for r in records.values():
            fields=list(r.raw_fields) or ['text'];stamp=r.normalized_fields.get('started_at') or r.normalized_fields.get('occurred_at') or r.normalized_fields.get('observed_at')
            repo.evidence['E-'+r.record_id]=Evidence(id='E-'+r.record_id,source_id=r.source_file_id,source_filename=r.filename,source_type=r.source_type,locator=Locator(row=r.row,span_start=r.span_start,span_end=r.span_end,fields=fields),timestamp=stamp,exact_excerpt=r.raw_excerpt,verification_status='UNVERIFIED',entity_ids=sorted({m.entity_id for m in mentions if m.record_id==r.record_id and m.entity_id}),relationship_ids=[c.claim_id for c in claims if c.record_id==r.record_id and c.disposition=='GRAPH_CANDIDATE'],parser_version=r.parser_version,source_record_id=r.record_id)
        for f in s['files']:
            manifest=Manifest.model_validate(f['manifest']);ids=['E-'+r.record_id for r in records.values() if r.source_file_id==manifest.source_file_id]
            if ids:repo.sources[manifest.source_file_id]=Source(id=manifest.source_file_id,filename=manifest.filename,type=manifest.source_type,description='Controlled uploaded synthetic source. '+manifest.processing_status,representation='uploaded_synthetic_file',evidence_ids=ids)
        if (s.get('case') or {}).get('fresh'):
            from .demo_schemas import Case
            people=[n.id for n in repo.entities.values() if n.type=='Person']
            preferred=lambda text:next((n.id for n in repo.entities.values() if n.type=='Person' and text in n.display_label.casefold()),None)
            start=preferred('rahul') or (people[0] if people else '')
            end=preferred('vikram') or (people[-1] if len(people)>1 else start)
            meta=s['case']
            repo.case=Case(id=meta['id'],name=meta['name'],description=meta['purpose'],classification='Synthetic Demonstration',status='Active Review',timezone='Asia/Kolkata',event_label='Case analysis replay',event_timestamp=meta['event_timestamp'],source_default=start,target_default=end,focus_entity_ids=[],max_depth=8)
        return repo
