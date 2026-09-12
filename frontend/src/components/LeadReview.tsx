import {useEffect,useRef,useState} from 'react';
import {api} from '../api';
import type {ComputedLead} from '../leadTypes';
import {reviewActions,type ReviewAction,type Review,type ReviewInput} from '../reviewTypes';
const label=(s:string)=>s.replaceAll('_',' ').toLowerCase().replace(/^./,c=>c.toUpperCase());
export default function LeadReview({lead,onSaved}:{lead:ComputedLead;onSaved:()=>Promise<void>}){
  const [action,setAction]=useState<ReviewAction>('NEEDS_MORE_EVIDENCE'),[reviewer,setReviewer]=useState(''),[reason,setReason]=useState(''),[object,setObject]=useState('');
  const [history,setHistory]=useState<Review[]>([]),[confirm,setConfirm]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
  const lock=useRef(false),request=useRef<ReviewInput|null>(null);
  useEffect(()=>{api.reviews(lead.lead_id).then(setHistory).catch(e=>setError(e.message))},[lead.lead_id,lead.review_status]);
  async function submit(){
    if(lock.current)return;lock.current=true;setBusy(true);setError('');
    request.current??={action,reviewer,reason,lead_revision:lead.lead_revision,idempotency_key:crypto.randomUUID(),...(['VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE'].includes(action)?{object_id:object}:{})};
    try{const result=await api.review(lead.lead_id,request.current);setHistory(await api.reviews(lead.lead_id));setMessage('Saved: '+label(result.action)+'. Recorded in audit history.');setConfirm(false);request.current=null;await onSaved()}
    catch(e){setError((e as Error).message)}finally{lock.current=false;setBusy(false)}
  }
  return <section className="lead-review" aria-label="Lead review"><h3>Record investigator review</h3><p className="micro">Current status: <strong>{label(lead.review_status)}</strong>. Reviewer identity is self-declared for this local demo.</p>
    <fieldset disabled={busy||confirm}><label>Reviewer<input aria-label="Reviewer's name" maxLength={100} value={reviewer} onChange={e=>setReviewer(e.target.value)}/></label><label>Decision<select aria-label="Lead review action" value={action} onChange={e=>{setAction(e.target.value as ReviewAction);setObject('')}}>{reviewActions.map(a=><option key={a} value={a}>{label(a)}</option>)}</select></label>
    {['VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE'].includes(action)&&<><label>{action==='VERIFIED_RELATIONSHIP'?'Supporting relationship ID':'Confirmed resolution proposal ID'}<input aria-label="Review object ID" value={object} onChange={e=>setObject(e.target.value)} placeholder={action==='VERIFIED_RELATIONSHIP'?'R01':'MP-rahul-rk-sharma'}/></label><p className="micro">Records your assessment. Source verification flags stay unchanged; use Resolution review to undo a merge.</p></>}
    <label>Reason (optional)<textarea aria-label="Review reasoning" maxLength={2000} rows={3} value={reason} onChange={e=>setReason(e.target.value)}/></label></fieldset>
    {!confirm?<button className="primary" disabled={!reviewer.trim()||(['VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE'].includes(action)&&!object.trim())} onClick={()=>{request.current=null;setConfirm(true);setMessage('')}}>Review submission</button>:<div className="caution"><p>Record <strong>{label(action)}</strong> as {reviewer}?{reason&&' Reason: '+reason}</p><button className="primary" disabled={busy} onClick={submit}>{busy?'Saving…':'Confirm submission'}</button><button disabled={busy} onClick={()=>{setConfirm(false);request.current=null}}>Edit</button></div>}
    {message&&<p role="status" className="review-success">{message}</p>}{error&&<p role="alert">{error}</p>}
    <details><summary>Review history ({history.length})</summary>{history.map(r=><article key={r.review_id}><strong>{label(r.action)}</strong><p className="micro">{r.reviewer} · {new Date(r.created_at).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})} IST{r.lead_revision!==lead.lead_revision?' · Earlier lead revision':''}</p><p>{r.reason||'No reason supplied.'}</p></article>)}</details>
  </section>;
}
