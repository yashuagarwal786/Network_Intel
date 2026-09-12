import {ArrowRight,Files,Network,ShieldCheck,Lightbulb} from 'lucide-react';
import type {CaseResponse,GraphData,Lead,MatchProposal} from '../demoTypes';
import type {ProcessingSummary} from '../intakeTypes';
import type {AuditEvent} from '../reviewTypes';
import {Panel,Badge,formatTime} from './WorkspaceUI';

export default function CaseOverview({caseData,graph,leads,proposals,processing,activity,onNavigate}:{caseData:CaseResponse;graph:GraphData;leads:Lead[];proposals:MatchProposal[];processing:ProcessingSummary|null;activity:AuditEvent[];onNavigate:(view:'network'|'intake'|'resolution'|'leads'|'audit')=>void}){
  const empty=!processing?.manifests.length;
  return <div className="overview-page"><Panel title={caseData.case.name} subtitle={caseData.case.description} actions={<Badge tone="info">{caseData.case.status}</Badge>}>
    <div className="overview-stats">{[[graph.nodes.length,'Entity records'],[graph.relationships.length,'Sourced relationships'],[proposals.filter(p=>p.status==='REVIEW'||p.status==='DEFERRED').length,'Pending identity reviews'],[leads.length,'Computed leads']].map(([value,label])=><div key={label}><strong>{value}</strong><span>{label}</span></div>)}</div><div className="overview-boundary">Synthetic case · Evidence, analytical inference and human decisions remain separate.</div>
  </Panel>{empty&&<section className="fresh-case-callout"><div><span>FRESH CASE · NO FIXTURE GRAPH</span><h2>Add source files to begin</h2><p>This workspace is empty by design. Entities, relationships and leads will be generated only from the evidence uploaded to this case.</p></div><button className="primary" onClick={()=>onNavigate('intake')}>Add evidence sources<ArrowRight size={15}/></button></section>}
  <div className="overview-columns"><Panel title="Investigation inputs" subtitle="Controlled source files with exact provenance" actions={<button onClick={()=>onNavigate('intake')}>Data Sources<ArrowRight size={14}/></button>}>
    {processing?.manifests.map(m=><div className="overview-source" key={m.source_file_id}><Files size={20}/><div><strong>{m.filename}</strong><small>{m.source_type} · {m.record_count} source records</small></div><Badge tone={m.validation_errors.length?'pending':'info'}>{m.processing_status.replaceAll('_',' ')}</Badge></div>)}{empty&&<p>No files have been added to this investigation.</p>}
  </Panel><Panel title="Continue investigation" subtitle="The next human decision stays in your hands"><div className="quick-actions">{[
    {view:'intake' as const,label:'Add Evidence Sources',icon:Files,detail:'Upload report, CDR, transaction and vehicle files'},
    {view:'resolution' as const,label:'Continue Entity Review',icon:ShieldCheck,detail:'Compare identifiers and original mentions'},
    {view:'network' as const,label:'Investigate Hidden Connection',icon:Network,detail:'Find an indirect, evidence-backed path'},
    {view:'leads' as const,label:'Review Leads',icon:Lightbulb,detail:'Inspect calculations before recording a decision'}
  ].map(a=><button key={a.label} aria-label={a.label} onClick={()=>onNavigate(a.view)}><a.icon size={20}/><span><strong>{a.label}</strong><small>{a.detail}</small></span><ArrowRight size={15}/></button>)}</div></Panel></div>
  <Panel title="Recent investigator activity" actions={<button onClick={()=>onNavigate('audit')}>Audit Trail<ArrowRight size={14}/></button>}><div className="recent-activity">{activity.slice().reverse().slice(0,3).map(a=><div key={a.audit_event_id}><Badge tone="info">{a.actor_type}</Badge><span><strong>{a.action.replaceAll('_',' ')}</strong><small>{a.actor} · {a.object_type} {a.object_id}</small></span><time>{formatTime(a.created_at)}</time></div>)}{!activity.length&&<p>No recorded activity yet.</p>}</div></Panel></div>
}
