import type {ReviewInput,Review,AuditEvent,TimelineItem} from './reviewTypes';
import type {EngineResult,EvidenceExplanation} from './leadTypes';
import type {Manifest,ProcessingSummary,SourceRecord,Mention,Claim} from './intakeTypes';
import type {MatchProposal, ResolutionDecision, CaseResponse, GraphData, Lead, Source, Evidence, PathResult} from './demoTypes';

// Only concurrent reads are shared; no stale cache and no automatic mutation retries.
const pending=new Map<string,Promise<unknown>>();
async function get<T>(route:string,signal?:AbortSignal,body?:unknown):Promise<T> {
  const send=async()=>{
    let response:Response;
    try{response=await fetch('/api'+route,{signal:AbortSignal.timeout(12000),...(body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})})}
    catch{throw new Error('The case service did not respond. Check the local backend and retry. Your current view is preserved.')}
    if(!response.ok){const data=await response.json().catch(()=>null);throw new Error(data?.error?.message||'The case service is unavailable. Check the backend and retry.')}
    return response.json();
  };
  let work=body?send():pending.get(route);
  if(!work){work=send().finally(()=>pending.delete(route));pending.set(route,work)}
  if(!signal)return work as Promise<T>;
  if(signal.aborted)throw new DOMException('Aborted','AbortError');
  return new Promise<T>((resolve,reject)=>{
    const abort=()=>reject(new DOMException('Aborted','AbortError'));
    signal.addEventListener('abort',abort,{once:true});
    work.then(value=>{signal.removeEventListener('abort',abort);if(!signal.aborted)resolve(value as T)},error=>{signal.removeEventListener('abort',abort);reject(error)});
  });
}
export const api={
  cases:()=>get<{cases:Array<{id:string;name:string;status:string;description:string;counts:Record<string,number>;active:boolean}>}>('/cases'),
  createCase:(name:string,reference:string,purpose:string)=>get<CaseResponse>('/cases',undefined,{name,reference,purpose}),
  review:(id:string,body:ReviewInput)=>get<Review>('/leads/'+encodeURIComponent(id)+'/reviews',undefined,body),
  reviews:(id:string)=>get<Review[]>('/leads/'+encodeURIComponent(id)+'/reviews'),
  audit:(query='')=>get<AuditEvent[]>('/cases/demo/audit?'+query),
  timeline:(query='')=>get<TimelineItem[]>('/cases/demo/timeline?'+query),
  upload:(filename:string,source_type:string,content:string)=>get<Manifest>('/cases/demo/sources/upload',undefined,{filename,source_type,content}),
  resetIntake:(reload_samples:boolean)=>get<ProcessingSummary>('/cases/demo/intake/reset',undefined,{reload_samples}),
  process:()=>get<ProcessingSummary>('/cases/demo/process',undefined,{}),
  processing:()=>get<ProcessingSummary>('/cases/demo/processing-summary'),
  records:()=>get<{records:SourceRecord[]}>('/cases/demo/source-records'),

  record:(id:string)=>get<SourceRecord>('/source-records/'+encodeURIComponent(id)),
  claims:()=>get<{mentions:Mention[];claims:Claim[]}>('/cases/demo/extracted-claims'),
  reviewClaim:(claimId:string,status:string,reviewer:string,reason:string)=>get<Claim>('/claims/'+encodeURIComponent(claimId)+'/review',undefined,{status,reviewer,reason}),
  proposals:()=>get<{proposals:MatchProposal[]}>('/cases/demo/resolution-proposals'),
  proposal:(id:string,signal?:AbortSignal)=>get<{proposal:MatchProposal;decisions:ResolutionDecision[]}>('/resolution-proposals/'+encodeURIComponent(id),signal),
  decide:(id:string,action:string,reviewer:string,reason:string)=>get<ResolutionDecision>('/resolution-proposals/'+encodeURIComponent(id)+'/decisions',undefined,{action,reviewer,reason}),
  undo:(id:string,reviewer:string,reason:string)=>get<ResolutionDecision>('/resolution-decisions/'+encodeURIComponent(id)+'/undo',undefined,{action:'UNDO_CONFIRMED_MATCH',reviewer,reason}),
  case:(signal?:AbortSignal)=>get<CaseResponse>('/cases/demo',signal),
  graph:(signal?:AbortSignal)=>get<GraphData>('/cases/demo/graph',signal),
  leads:(signal?:AbortSignal)=>get<EngineResult>('/cases/demo/leads',signal),
  sources:(signal?:AbortSignal)=>get<{sources:Source[]}>('/cases/demo/sources',signal),
  lead:(id:string,signal?:AbortSignal)=>get<{lead:Lead}>('/leads/'+encodeURIComponent(id),signal),
  explainLead:(id:string,signal?:AbortSignal)=>get<EvidenceExplanation>('/leads/'+encodeURIComponent(id)+'/explanation',signal),
  evidence:(id:string,signal?:AbortSignal)=>get<{evidence:Evidence}>('/evidence/'+encodeURIComponent(id),signal),
  path:(source:string,target:string,depth:number,signal?:AbortSignal)=>get<PathResult>('/cases/demo/path?'+new URLSearchParams({source,target,max_depth:String(depth)}),signal),
  explainPath:(source:string,target:string,depth:number,signal?:AbortSignal)=>get<EvidenceExplanation>('/cases/demo/path/explanation?'+new URLSearchParams({source,target,max_depth:String(depth)}),signal),
  nerStatus:()=>get<{available:boolean;model:string;extractor_version:string;status_text:string}>('/cases/demo/ner-status'),
  sourceFiles:()=>get<{manifest:Manifest;content:string}[]>('/cases/demo/source-files'),
  loadDemoReport:()=>get<{manifest:Manifest;summary:ProcessingSummary}>('/cases/demo/load-demo-report',undefined,{}),
  anomalies:(signal?:AbortSignal)=>get<any>('/cases/demo/anomalies',signal),
  networkRoles:(signal?:AbortSignal)=>get<{case_id:string;roles:import('./demoTypes').NetworkRole[]}>('/cases/demo/network-roles',signal),
};
