"""Deterministic, evidence-gated rules. No fixture leads or model scores are read."""
from collections import Counter
from dataclasses import dataclass
from datetime import timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from statistics import median
import networkx as nx
from .demo_paths import compute_path
from .lead_models import ComputedSignal, ComputedLead, EngineResult, TimeWindow

VERSION='temporal-leads-v1'
@dataclass(frozen=True)
class Policy:
    baseline_days: int = 7
    minimum_observed_baseline_days: int = 3
    minimum_calls: int = 5
    call_multiplier: int = 3
    minimum_new_contacts: int = 3
    transfer_minutes: int = 90
    minimum_transfers: int = 3
    correlation_minutes: int = 90
    max_path_depth: int = 8
    minimum_path_accounts: int = 2

def stable_id(kind,parts):return kind+'-'+sha256('|'.join(parts).encode()).hexdigest()[:16]
def evidence_of(events):return sorted({eid for e in events for eid in e.evidence_ids})
def traceable(repo,ids):
    return bool(ids) and all((e:=repo.evidence.get(id)) is not None and e.source_id in repo.sources and e.id in repo.sources[e.source_id].evidence_ids and bool(e.exact_excerpt) and (e.locator.row is not None or e.locator.paragraph is not None or e.locator.span_start is not None) for id in ids)
def priority_for(categories):
    count=len(set(categories));return 'HIGH' if count>=3 else 'MEDIUM' if count==2 else 'LOW'

def rupees(value):
    whole,fraction=format(value,'.2f').split('.')
    tail=whole[-3:];head=whole[:-3];groups=[]
    while head:groups.insert(0,head[-2:]);head=head[:-2]
    return '₹'+','.join(groups+[tail])+('' if fraction=='00' else '.'+fraction)

def historical_counts(events,phone,day_start,policy):
    start=day_start-timedelta(days=policy.baseline_days)
    baseline=[e for e in events if e.entity_ids[0]==phone and start<=e.timestamp<day_start]
    counts=Counter(e.timestamp.astimezone(day_start.tzinfo).date() for e in baseline)
    series=[{'date':(start+timedelta(days=i)).date().isoformat(),'calls':counts[(start+timedelta(days=i)).date()]} for i in range(policy.baseline_days)]
    return baseline,series,float(median(row['calls'] for row in series))

def transfer_sequences(events,policy):
    """Weak account connectivity inside a sliding inclusive time window; no laundering inference."""
    ordered=sorted(events,key=lambda e:(e.timestamp,e.id));candidates={}
    for first in ordered:
        window=[e for e in ordered if first.timestamp<=e.timestamp<=first.timestamp+timedelta(minutes=policy.transfer_minutes)]
        graph=nx.Graph();graph.add_edges_from(e.entity_ids[:2] for e in window)
        for component in nx.connected_components(graph):
            group=[e for e in window if set(e.entity_ids[:2])<=component]
            if len(group)>=policy.minimum_transfers:candidates[tuple(sorted(e.id for e in group))]=group
    keys=sorted(candidates)
    return [candidates[key] for key in keys if not any(set(key)<set(other) for other in keys)]

def run_engine(repo,policy=Policy()):
    if not 1<=policy.max_path_depth<=8:raise ValueError('Path depth must be within 1–8')
    if policy.baseline_days<1:raise ValueError('Baseline requires at least one day')
    # Controlled 2026 India dataset: fixed IST avoids a tzdata dependency on Windows.
    as_of=repo.case.event_timestamp.astimezone(timezone(timedelta(hours=5,minutes=30)))
    day_start=as_of.replace(hour=0,minute=0,second=0,microsecond=0)
    baseline_start=day_start-timedelta(days=policy.baseline_days)
    diagnostics=[];signals=[];leads=[]
    eligible=[]
    for e in sorted(repo.events.values(),key=lambda e:(e.timestamp,e.id)):
        if e.type not in ['call','transfer']:continue
        if len(e.entity_ids)!=2 or not set(e.entity_ids)<=repo.entities.keys() or not traceable(repo,e.evidence_ids):
            diagnostics.append(f'{e.id}: omitted because entity/evidence trace is incomplete.');continue
        if e.type=='transfer' and (e.amount_inr is None or e.amount_inr<=0):continue
        if e.timestamp<=as_of:eligible.append(e)
    calls=[e for e in eligible if e.type=='call']
    transfers=[e for e in eligible if e.type=='transfer' and day_start<=e.timestamp]
    def signal(kind,category,key,title,ids,window,observed,expected,calculation,threshold,eids,events,baseline='No historical expectation used.',limitations=None,**extra):
        return ComputedSignal(signal_id=stable_id(kind,[repo.case.id,*key]),case_id=repo.case.id,signal_type=kind,category=category,title=title,involved_entity_ids=sorted(set(ids)),time_window=window,baseline_definition=baseline,observed_value=observed,expected_value=expected,calculation=calculation,threshold=threshold,supporting_evidence_ids=sorted(set(eids)),event_ids=sorted(e.id for e in events),algorithm_version=VERSION,limitations=limitations or ['Synthetic metadata only; source assertions are not independently verified.'],generated_at=as_of,**extra)
    communication={}
    for phone in sorted({e.entity_ids[0] for e in calls if day_start<=e.timestamp}):
        current=[e for e in calls if e.entity_ids[0]==phone and day_start<=e.timestamp<=as_of]
        baseline,series,expected=historical_counts(calls,phone,day_start,policy)
        observed_days=sum(row['calls']>0 for row in series)
        if observed_days<policy.minimum_observed_baseline_days:
            diagnostics.append(f'{phone}: insufficient baseline history ({observed_days} observed days); no communication signal.');continue
        definition=f'{policy.baseline_days} complete IST calendar days [{baseline_start.isoformat()}, {day_start.isoformat()}); outgoing calls, missing dataset days counted as zero.'
        window=TimeWindow(start=day_start,end=as_of)
        limits=['Incomplete records can change the baseline; absence in this dataset is not absence of real activity.','Current day is counted only through the replay analysis timestamp. Call content and operator identity are unknown.']
        bucket=[];threshold=max(policy.minimum_calls,expected*policy.call_multiplier)
        if len(current)>=threshold:
            s=signal('COMMUNICATION_BURST','COMMUNICATION',[phone,day_start.isoformat()],f'{expected:g} calls/day → {len(current)} calls',[phone],window,{'calls':len(current),'daily_baseline':series,'activity_start':min(e.timestamp for e in current).isoformat(),'activity_end':max(e.timestamp for e in current).isoformat()},{'median_calls_per_day':expected},f'Median of {[r["calls"] for r in series]} = {expected:g}; current outgoing records = {len(current)}. Trigger at max({policy.minimum_calls}, {policy.call_multiplier} × median) = {threshold:g}.',{'minimum_calls':policy.minimum_calls,'median_multiplier':policy.call_multiplier,'effective_calls':threshold},evidence_of(baseline+current),baseline+current,definition,limits)
            signals.append(s);bucket.append(s)
        old={e.entity_ids[1] for e in baseline};new=sorted({e.entity_ids[1] for e in current}-old)
        if len(new)>=policy.minimum_new_contacts:
            relevant=[e for e in current if e.entity_ids[1] in new]
            s=signal('NEW_CONTACT_BURST','COMMUNICATION',[phone,day_start.isoformat()],f'{len(new)} contacts new to the baseline',[phone,*new],window,{'new_contacts':len(new),'contact_ids':new,'baseline_contact_ids':sorted(old)},{'baseline_new_contacts':0},f'Event-day distinct recipients minus baseline recipients = {new}; count = {len(new)}.',{'minimum_new_contacts':policy.minimum_new_contacts},evidence_of(baseline+relevant),baseline+relevant,definition,['New means not observed in the selected records/window, not a new real-world relationship.','Shares the communication category with call volume; it does not add an independent priority vote.'])
            signals.append(s);bucket.append(s)
        if bucket:communication[phone]=(bucket,current)
    financial=[]
    for group in transfer_sequences(transfers,policy):
        start=min(e.timestamp for e in group);end=max(e.timestamp for e in group);total=sum((Decimal(e.amount_inr) for e in group),Decimal(0));accounts=sorted({id for e in group for id in e.entity_ids})
        s=signal('TRANSACTION_SEQUENCE','FINANCIAL',[e.id for e in group],f'{len(group)} connected transfers · {rupees(total)}',accounts,TimeWindow(start=start,end=end),{'transfers':len(group),'total_inr':str(total),'elapsed_minutes':(end-start).total_seconds()/60,'transaction_ids':[e.transaction_id or e.id for e in group],'account_ids':accounts},{},f'{" + ".join(str(e.amount_inr) for e in group)} = INR {total}; {(end-start).total_seconds()/60:g} elapsed minutes; weakly connected account component.',{'minimum_transfers':policy.minimum_transfers,'window_minutes':policy.transfer_minutes},evidence_of(group),group,limitations=['Total transfer volume can count the same funds more than once.','Account connectivity and temporal proximity do not establish purpose, money laundering or crime.','Overlapping strict-subset windows are suppressed; distinct event IDs are treated as separate records.'])
        signals.append(s);financial.append(s)
    # Explicit case-scoped investigation endpoints; the path itself is always computed.
    source,target=repo.case.source_default,repo.case.target_default
    path=compute_path(repo,source,target,policy.max_path_depth) if source in repo.entities and target in repo.entities else None
    for phone,(comm,current) in sorted(communication.items()):
        for tx in financial:
            if path is None or phone not in path.node_ids:continue
            accounts=sorted(set(tx.involved_entity_ids)&set(path.node_ids))
            if len(accounts)<policy.minimum_path_accounts:continue
            near=[e for e in current if tx.time_window.start-timedelta(minutes=policy.correlation_minutes)<=e.timestamp<=tx.time_window.end+timedelta(minutes=policy.correlation_minutes)]
            if not near or not traceable(repo,path.evidence_ids):continue
            independent=sorted({eid for r in path.relationships if r.type in ['USES','USED_PHONE','USED_BY','CONTROLS','CONTROLLED_BY'] for eid in r.evidence_ids}-{eid for s in comm+[tx] for eid in s.supporting_evidence_ids})
            graph_signal=signal('GRAPH_PATH','GRAPH_CONTEXT',[phone,tx.signal_id,source,target],f'{path.path_length}-hop path connects communication and transfers',path.node_ids,TimeWindow(start=min(e.timestamp for e in near),end=max(tx.time_window.end,max(e.timestamp for e in near))),{'path_length':path.path_length,'phone_on_path':phone,'accounts_on_path':accounts,'sequence_accounts':tx.involved_entity_ids,'independent_association_evidence_ids':independent},{},f'Bounded NetworkX path contains {phone} and {len(accounts)} of {len(tx.involved_entity_ids)} transaction accounts. No new graph edge is inferred.',{'max_path_depth':policy.max_path_depth,'minimum_path_accounts':policy.minimum_path_accounts,'temporal_tolerance_minutes':policy.correlation_minutes},path.evidence_ids,[],limitations=['A path is an association trace, not chronology, causation, leadership or wrongdoing.','Accounts outside the returned path are not represented as being on it.','Operational categories are distinct evidence checks, not proven statistical independence.'],path=path,independent_category=bool(independent))
            selected=comm+[tx,graph_signal]
            if not all(traceable(repo,s.supporting_evidence_ids) for s in selected):continue
            categories=sorted({s.category for s in selected if s.independent_category})
            if len(categories)<2:continue
            signals.append(graph_signal)
            priority=priority_for(categories)
            leads.append(ComputedLead(lead_id=str(17+len(leads)),case_id=repo.case.id,title='Communication burst followed by connected transfers',review_priority=priority,summary=f'{day_start.date().isoformat()} · {phone}: '+ '; '.join(s.title for s in comm)+f'. {tx.title} over {tx.observed_value["elapsed_minutes"]:g} minutes. A computed {path.path_length}-hop association path connects the records.',involved_entity_ids=sorted({id for s in selected for id in s.involved_entity_ids}),signal_ids=[s.signal_id for s in selected],evidence_ids=sorted({eid for s in selected for eid in s.supporting_evidence_ids}),generated_at=as_of,engine_version=VERSION,limitations=['Deterministic rules over synthetic records; no real-world accuracy estimate.','Ordinary business coordination or payments could explain the same records.','Priority is a review-order policy, not a risk model. Human assessment is recorded separately from analytical priority.','Generation time uses the deterministic case replay clock, not wall-clock request time.'],signal_categories=categories,priority_explanation=f'{priority}: {len(categories)} distinct categories ({", ".join(c.replace("_"," ") for c in categories)}), time proximity, bounded connectivity and complete evidence traces. Burst and new contacts count once. Graph context counts only with separate phone/account association evidence.',time_window=graph_signal.time_window,signals=selected))
    return EngineResult(leads=leads,signals=sorted({s.signal_id:s for s in signals}.values(),key=lambda s:s.signal_id),engine_version=VERSION,generated_at=as_of,diagnostics=sorted(diagnostics))
