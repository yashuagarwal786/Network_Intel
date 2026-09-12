"""UTF-8 CSV/text intake parser with ML-based NER for free-text reports.

Structured sources (CDR, Transaction, Vehicle) continue to use deterministic
regex/CSV grammar.  Free-text Report lines use spaCy NER (via ner_service) for
Person / Organization / Location extraction.  All structured identifiers
(phone, account, vehicle number, money, date, …) are always extracted by regex
regardless of NER availability.

If the spaCy model cannot be loaded, extraction falls back to the explicit
WHITELIST_* constants below.  The fallback is clearly labelled and never
silently pretends ML ran.
"""
import csv
import hashlib
import io
import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from . import ner_service
from .intake_models import Record, Mention, Claim

logger = logging.getLogger(__name__)

HEADERS={
 'CDR':['call_id','caller_phone','receiver_phone','started_at','duration_seconds','tower_location'],
 'Transaction':['transaction_id','sender_account','receiver_account','occurred_at','amount','currency','channel'],
 'Vehicle':['record_id','vehicle_number','relationship_type','person_name','observed_at','location','source_type']}

HEADER_SYNONYMS = {
    'CDR': {
        'call_id': {'call_id', 'callid', 'call_identifier', 'record_id', 'id', 'cdr_id', 'call_ref'},
        'caller_phone': {'caller_phone', 'caller', 'calling_number', 'caller_number', 'calling_no', 'from_phone', 'source_phone', 'calling_party', 'caller_msisdn', 'msisdn_a', 'calling_num', 'a_party'},
        'receiver_phone': {'receiver_phone', 'receiver', 'called_number', 'receiver_number', 'called_no', 'to_phone', 'destination_phone', 'called_party', 'receiver_msisdn', 'msisdn_b', 'dialed_number', 'dialled_number', 'called_num', 'b_party'},
        'started_at': {'started_at', 'start_time', 'call_time', 'timestamp', 'date_time', 'datetime', 'call_start', 'call_start_time', 'call_date', 'date'},
        'duration_seconds': {'duration_seconds', 'duration', 'duration_sec', 'call_duration', 'duration_s', 'call_duration_sec', 'call_duration_seconds', 'seconds'},
        'tower_location': {'tower_location', 'tower', 'location', 'cell_tower', 'cell_location', 'cell_id', 'tower_site', 'site_name', 'cell_site', 'first_cell'}
    },
    'Transaction': {
        'transaction_id': {'transaction_id', 'tx_id', 'txn_id', 'transaction_ref', 'reference_id', 'utr', 'ref_no', 'txn_number', 'id', 'trans_id'},
        'sender_account': {'sender_account', 'sender', 'from_account', 'source_account', 'debit_account', 'remitter_account', 'payer_account', 'from_acc', 'remitter_acc'},
        'receiver_account': {'receiver_account', 'receiver', 'to_account', 'dest_account', 'credit_account', 'beneficiary_account', 'payee_account', 'to_acc', 'beneficiary_acc'},
        'occurred_at': {'occurred_at', 'txn_date', 'timestamp', 'date_time', 'datetime', 'transaction_time', 'txn_timestamp', 'value_date', 'date', 'trans_date'},
        'amount': {'amount', 'txn_amount', 'value', 'transaction_amount', 'sum', 'amt'},
        'currency': {'currency', 'curr', 'currency_code', 'ccy'},
        'channel': {'channel', 'mode', 'payment_mode', 'txn_channel', 'payment_method', 'txn_type', 'type', 'channel_type'}
    },
    'Vehicle': {
        'record_id': {'record_id', 'id', 'log_id', 'entry_id', 's_no', 'sr_no'},
        'vehicle_number': {'vehicle_number', 'vehicle_no', 'registration_no', 'reg_no', 'plate_number', 'license_plate', 'registration_number', 'vehicle'},
        'relationship_type': {'relationship_type', 'relation', 'relationship', 'association_type', 'connection_type', 'role'},
        'person_name': {'person_name', 'name', 'driver_name', 'owner_name', 'person', 'individual'},
        'observed_at': {'observed_at', 'timestamp', 'date_time', 'datetime', 'observation_time', 'date', 'seen_at'},
        'location': {'location', 'place', 'spot', 'site', 'checkpoint', 'area'},
        'source_type': {'source_type', 'source', 'data_source', 'capture_method', 'extract_type'}
    }
}

def clean_header_col(col: str) -> str:
    return re.sub(r'[^a-z0-9_]', '', re.sub(r'[\s\-]+', '_', col.strip().lower()))

def map_csv_headers(source_type: str, raw_header: list[str]):
    if source_type not in HEADERS:
        return None, f"Unknown source type: {source_type}"
    canonical_fields = HEADERS[source_type]
    if raw_header == canonical_fields:
        return {i: col for i, col in enumerate(canonical_fields)}, None
    synonyms = HEADER_SYNONYMS.get(source_type, {})
    mapping = {}
    used_canonical = set()
    for i, raw in enumerate(raw_header):
        cleaned = clean_header_col(raw)
        matched = None
        if cleaned in canonical_fields:
            matched = cleaned
        else:
            for canon, syn_set in synonyms.items():
                if cleaned in syn_set:
                    matched = canon
                    break
        if matched and matched not in used_canonical:
            mapping[i] = matched
            used_canonical.add(matched)
    missing = [c for c in canonical_fields if c not in used_canonical]
    if missing:
        return None, f"Header must match or map to required columns: {', '.join(canonical_fields)} (missing: {', '.join(missing)})"
    return mapping, None

# ---------------------------------------------------------------------------
# Legacy demo dictionaries retained for import compatibility only. Report NER
# and uploaded CSV validation no longer depend on these case-specific values.
# ---------------------------------------------------------------------------
WHITELIST_PEOPLE    = ['Rahul Kumar Sharma','Rahul Sharma','R.K. Sharma','Vikram Singh',
                       'Amit Verma','A. Verma','Neha Kapoor','Arjun Mehta']
WHITELIST_LOCATIONS = ['Rivergate depot','East market','Canal junction','North yard']
WHITELIST_ORGS      = ['Mira Logistics','Northline Trading','Cedar Services']

# Keep legacy aliases so that validate_row (Vehicle CSV) can still reference them.
PEOPLE    = WHITELIST_PEOPLE
LOCATIONS = WHITELIST_LOCATIONS
ORGS      = WHITELIST_ORGS
PHONE=r'\+[0-9]{10,15}(?![0-9])'
ACCOUNT=r'DEMO-A[0-9]{3,8}'
VEHICLE=r'DEMO-VH-[0-9]{2,4}'
DATE=r'\d{4}-\d{2}-\d{2}(?:T[0-9:+-]+)?|\d{1,2} August(?: 2026)?'

def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def phone(value):
    digits=re.sub(r'[ ()+-]','',value)
    if not re.fullmatch(r'[0-9]{10,15}',digits):raise ValueError('phone must contain 10-15 digits')
    return '+'+digits
def timestamp(value):
    dt=datetime.fromisoformat(value)
    if dt.utcoffset() is None:raise ValueError('timestamp must include timezone')
    return dt.isoformat()

def safe_label(value,min_length=2,max_length=120):
    if not min_length<=len(value)<=max_length or not re.fullmatch(r"[\w .,'()/-]+",value,re.UNICODE):raise ValueError('text label contains unsupported characters or length')
    return value

def validate_row(kind,row):
    result={k:v.strip() for k,v in row.items()}
    if any(not v for v in result.values()):raise ValueError('required field is empty')
    if kind=='CDR':
        if not re.fullmatch(r'CALL-[A-Z0-9-]+',result['call_id']):raise ValueError('invalid call_id')
        for field in ['caller_phone','receiver_phone']:result[field]=phone(result[field])
        result['started_at']=timestamp(result['started_at'])
        duration=int(result['duration_seconds'])
        if not 0<=duration<=86400:raise ValueError('duration_seconds must be between 0 and 86400')
        result['duration_seconds']=str(duration)
        result['tower_location']=safe_label(result['tower_location'])
    elif kind=='Transaction':
        if not re.fullmatch(r'TX-[A-Z0-9-]+',result['transaction_id']):raise ValueError('invalid transaction_id')
        for field in ['sender_account','receiver_account']:
            if not re.fullmatch(ACCOUNT,result[field]):raise ValueError('account must use DEMO-A followed by 3-8 digits')
        result['occurred_at']=timestamp(result['occurred_at'])
        amount=Decimal(result['amount'])
        if not amount.is_finite() or amount<=0 or amount>Decimal('1000000000') or amount.as_tuple().exponent < -2:raise ValueError('amount must be positive, finite and have at most two decimal places')
        result['amount']=format(amount,'.2f')
        if result['currency']!='INR' or result['channel'] not in ['NEFT','IMPS','UPI','RTGS']:raise ValueError('unsupported currency or channel')
    else:
        if not re.fullmatch(r'VR-[A-Z0-9-]+',result['record_id']):raise ValueError('invalid record_id')
        if not re.fullmatch(VEHICLE,result['vehicle_number']):raise ValueError('invalid synthetic vehicle number')
        if result['relationship_type'] not in ['REGISTERED_KEEPER','OBSERVED_WITH']:raise ValueError('unsupported vehicle relationship_type')
        result['person_name']=safe_label(result['person_name'],2,80);result['location']=safe_label(result['location'])
        result['observed_at']=timestamp(result['observed_at'])
        if result['source_type'] not in ['registration_extract','synthetic_observation']:raise ValueError('unsupported vehicle source_type')
    return result

def parse(manifest,text):
    records=[];errors=[]
    if manifest.source_type=='Report':
        for i,match in enumerate(re.finditer(r'[^\r\n]+',text)):
            if not match.group().strip():continue
            records.append(Record(record_id=f'{manifest.source_file_id}-r{i+1}',source_file_id=manifest.source_file_id,filename=manifest.filename,source_type='Report',span_start=match.start(),span_end=match.end(),raw_excerpt=match.group(),normalized_fields={'text':match.group().strip()},status='VALID'))
        return records,errors
    lines=text.splitlines(keepends=True);offsets=[0]
    for line in lines:offsets.append(offsets[-1]+len(line))
    reader=csv.reader(io.StringIO(text,newline=''),strict=True)
    try:
        header=next(reader)
        col_map, err = map_csv_headers(manifest.source_type, header)
        if err: return [], [err]
        primary_key = HEADERS[manifest.source_type][0]
        previous=reader.line_num;seen=set()
        for index,values in enumerate(reader,1):
            start,end=offsets[previous],offsets[reader.line_num];line=previous+1;previous=reader.line_num
            record=Record(record_id=f'{manifest.source_file_id}-r{index}',source_file_id=manifest.source_file_id,filename=manifest.filename,source_type=manifest.source_type,row=line,span_start=start,span_end=end,raw_excerpt=text[start:end],status='VALID')
            try:
                if len(values)!=len(header):raise ValueError('column count does not match header')
                record.raw_fields={col_map[i]: values[i] for i in col_map if i < len(values)}
                record.normalized_fields=validate_row(manifest.source_type,record.raw_fields)
                key=record.normalized_fields[primary_key]
                if key in seen:raise ValueError('duplicate source record identifier')
                seen.add(key)
            except (ValueError,InvalidOperation,OverflowError) as exc:
                record.status='INVALID';record.normalized_fields={};record.validation_errors=[str(exc)]
            records.append(record)
    except (csv.Error,StopIteration) as exc:return [],[f'Malformed or empty CSV: {exc}']
    return records,errors

def extract(records):
    mentions=[];claims=[]
    for r in records:
        if r.status!='VALID':continue
        eid='E-'+r.record_id
        def mention(kind,value,field=None,extractor_version='controlled-intake-v2',extraction_method='deterministic-regex',confidence=None,local_span=None,normalized_value=None):
            normalized=normalized_value or (phone(value) if kind=='Phone' else value.strip())
            if kind=='Money':normalized=format(Decimal(value.removeprefix('INR').strip()),'.2f')+' INR'
            if kind=='Date' and 'August' in value:
                parts=value.split();normalized=f'{parts[2]}-08-{int(parts[0]):02d}' if len(parts)==3 else f'08-{int(parts[0]):02d} (year unspecified)'
            scope=r.source_file_id if kind=='Person' else ''
            node_id='I-'+digest(kind+'|'+scope+'|'+normalized)[:20] if kind in ['Person','Phone','Account','Vehicle','Location','Organization'] else None
            if local_span is None:
                start=r.raw_excerpt.find(value);local_span=(start,start+len(value)) if start>=0 else (0,len(r.raw_excerpt))
            absolute=(r.span_start+local_span[0],r.span_start+local_span[1])
            exact=r.raw_excerpt[local_span[0]:local_span[1]] or value
            m=Mention(mention_id='M-'+digest(r.record_id+'|'+kind+'|'+value+'|'+str(field))[:20],record_id=r.record_id,source_file_id=r.source_file_id,source_id=r.source_file_id,kind=kind,raw_value=value,normalized_value=normalized,field=field,evidence_id=eid,entity_id=node_id,extractor_version=extractor_version,extraction_method=extraction_method,confidence=confidence,evidence_text=exact,span_start=absolute[0],span_end=absolute[1])
            if not any(x.mention_id==m.mention_id for x in mentions):mentions.append(m)
            return node_id
        def claim(subject,obj,kind,polarity='POSITIVE',uncertainty='ASSERTED',explanation='Exact source template; machine extraction remains unverified.',extraction_method='deterministic-relation-template'):
            disposition='NEGATED' if polarity=='NEGATIVE' else 'UNCERTAIN' if uncertainty=='POSSIBLE' else 'UNSUPPORTED' if polarity=='UNKNOWN' else 'GRAPH_CANDIDATE'
            if disposition=='NEGATED':explanation='Negative source assertion retained. No positive graph relationship is created.'
            if disposition=='UNCERTAIN':explanation='Possible relationship retained for review. Uncertainty prevents adding a graph edge.'
            claims.append(Claim(claim_id='C-'+digest(r.record_id+'|'+kind+'|'+str(subject)+'|'+str(obj))[:20],record_id=r.record_id,source_file_id=r.source_file_id,source_id=r.source_file_id,subject_id=subject,object_id=obj,relationship_type=kind,polarity=polarity,uncertainty=uncertainty,disposition=disposition,explanation=explanation,evidence_ids=[eid],extractor_version='controlled-intake-v2',extraction_method=extraction_method,evidence_text=r.raw_excerpt,span_start=r.span_start,span_end=r.span_end))
        f=r.normalized_fields
        if r.source_type=='CDR':
            a=mention('Phone',r.raw_fields['caller_phone'],'caller_phone',extraction_method='deterministic-csv-field');b=mention('Phone',r.raw_fields['receiver_phone'],'receiver_phone',extraction_method='deterministic-csv-field');mention('Location',f['tower_location'],'tower_location',extraction_method='deterministic-csv-field');mention('Date',f['started_at'],'started_at',extraction_method='deterministic-csv-field');mention('CallIdentifier',f['call_id'],'call_id',extraction_method='deterministic-csv-field');claim(a,b,'CALLED',extraction_method='deterministic-cdr-schema')
        elif r.source_type=='Transaction':
            a=mention('Account',f['sender_account'],'sender_account',extraction_method='deterministic-csv-field');b=mention('Account',f['receiver_account'],'receiver_account',extraction_method='deterministic-csv-field');mention('Money',r.raw_fields['amount'],'amount',extraction_method='deterministic-csv-field');mention('Date',f['occurred_at'],'occurred_at',extraction_method='deterministic-csv-field');mention('TransactionIdentifier',f['transaction_id'],'transaction_id',extraction_method='deterministic-csv-field');claim(a,b,'TRANSFERRED_TO',extraction_method='deterministic-transaction-schema')
        elif r.source_type=='Vehicle':
            a=mention('Person',f['person_name'],'person_name',extraction_method='deterministic-csv-field');b=mention('Vehicle',f['vehicle_number'],'vehicle_number',extraction_method='deterministic-csv-field');mention('Location',f['location'],'location',extraction_method='deterministic-csv-field');mention('Date',f['observed_at'],'observed_at',extraction_method='deterministic-csv-field');claim(a,b,f['relationship_type'],extraction_method='deterministic-vehicle-schema')
        else:
            text=f['text'];found={};found_types={}
            def register(key,node_id,kind):found[key]=node_id;found_types[key]=kind
            ner_entities,ner_error=ner_service.extract(text);ner_extractor=ner_service.current_extractor_version()
            if ner_error:
                logger.warning('NER and EntityRuler unavailable for %s: %s',r.record_id,ner_error)
            for ent in ner_entities:
                node_id=mention(ent.kind,ent.raw_text,extractor_version=ner_extractor,extraction_method=ent.extraction_method,confidence=None,local_span=(ent.start_char,ent.end_char),normalized_value=ent.normalized)
                register(ent.raw_text,node_id,ent.kind);register(ent.normalized,node_id,ent.kind)
            for kind,pattern in [('Phone',PHONE),('Account',ACCOUNT),('Vehicle',VEHICLE),('Date',DATE),('Money',r'INR\s+[0-9]+(?:\.[0-9]{2})?'),('CaseIdentifier',r'VEIL-DEMO-[0-9]{3}'),('TransactionIdentifier',r'TX-[A-Z0-9-]+')]:
                for match in re.finditer(pattern,text):
                    node_id=mention(kind,match.group(),local_span=match.span(),extraction_method='deterministic-regex');register(match.group(),node_id,kind)
            rel_patterns=[
                (r'(.+?) uses phone ('+PHONE+r')\.', 'USED_PHONE', {'Person'}, {'Phone'}),
                (r'(.+?) is associated with vehicle ('+VEHICLE+r')\.', 'ASSOCIATED_WITH', {'Person'}, {'Vehicle'}),
                (r'(.+?) controls account ('+ACCOUNT+r')\.', 'CONTROLS', {'Person'}, {'Account'}),
                (r'(.+?) is located at (.+?)\.', 'LISTED_AT', {'Organization'}, {'Location'}),
                (r'(.+?) visited (.+?) on (?:'+DATE+r')\.', 'VISITED', {'Person'}, {'Location'}),
                (r'(.+?) visited (.+?)\.', 'VISITED', {'Person'}, {'Location'}),
                (r'(.+?) called (.+?) on (?:'+DATE+r')\.', 'CALLED', {'Person','Phone'}, {'Person','Phone'}),
                (r'(.+?) called (.+?)\.', 'CALLED', {'Person','Phone'}, {'Person','Phone'}),
                (r'(.+?) is associated with (.+?)\.', 'ASSOCIATED_WITH', {'Person','Organization'}, {'Person','Organization','Location','Vehicle'}),
            ]
            matched=False
            for pattern,kind,subject_types,object_types in rel_patterns:
                match=re.fullmatch(pattern,text)
                if not match:continue
                subj,obj=match.group(1).strip(),match.group(2).strip()
                if subj in found and obj in found and found_types.get(subj) in subject_types and found_types.get(obj) in object_types:
                    claim(found[subj],found[obj],kind);matched=True;break
            meeting=re.fullmatch(r'(.+?) (did not meet|may meet|met) (.+?) on (\d{1,2} August(?: 2026)?)\.',text)
            if meeting:
                subj,obj=meeting.group(1).strip(),meeting.group(3).strip()
                # Grammar supplies a conservative type hint when the small NER
                # model mislabels a meeting participant (the claim is still UNVERIFIED).
                for value in [subj,obj]:
                    if found_types.get(value)!='Person' and re.fullmatch(r"[A-Z][\w.']+(?:\s+[A-Z][\w.']+)+",value):
                        start=text.find(value);node_id=mention('Person',value,extraction_method='deterministic-relation-argument',local_span=(start,start+len(value)))
                        register(value,node_id,'Person')
                if found_types.get(subj)=='Person' and found_types.get(obj)=='Person':
                    claim(found[subj],found[obj],'MET','NEGATIVE' if meeting.group(2)=='did not meet' else 'POSITIVE','POSSIBLE' if meeting.group(2)=='may meet' else 'ASSERTED');matched=True
            if not matched:claim(None,None,'UNSUPPORTED','UNKNOWN','UNKNOWN','No supported relationship template. Extracted values are retained; no graph relationship asserted.','no-reliable-relation-rule')
    return mentions,claims
