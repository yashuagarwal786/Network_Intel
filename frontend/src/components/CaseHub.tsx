import {useEffect,useState} from 'react';
import {ArrowRight,FolderOpen,Plus,ShieldCheck,X} from 'lucide-react';
import {api} from '../api';

type CaseCard={id:string;name:string;status:string;description:string;counts:Record<string,number>;active:boolean};

export default function CaseHub({onOpen,onCreated}:{onOpen:()=>void;onCreated:()=>void}){
  const [cases,setCases]=useState<CaseCard[]>([]),[creating,setCreating]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const [name,setName]=useState('Operation Riverglass'),[reference,setReference]=useState('NI-2026-019'),[purpose,setPurpose]=useState('Cross-source relationship analysis from synthetic investigation records.');
  useEffect(()=>{api.cases().then(r=>setCases(r.cases)).catch(e=>setError(e.message))},[]);
  async function create(){setBusy(true);setError('');try{await api.createCase(name,reference,purpose);setCreating(false);onCreated()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
  const attention=cases.filter(c=>c.active||c.counts.leads||c.status.includes('Awaiting'));
  return <div className="case-hub">
    <header className="case-hub-top"><div className="case-hub-brand"><img src="/assets/network-intel-mark.png" alt=""/><strong>Network Intel</strong><span>Investigation Console</span></div><div className="synthetic"><span/>Synthetic Demonstration Data</div></header>
    <main className="case-hub-main"><div className="case-hub-heading"><div><div className="eyebrow">CASE WORKSPACE</div><h1>Investigation cases</h1><p>Open an existing workspace or create a fresh case from source files.</p></div><button className="primary" onClick={()=>setCreating(true)}><Plus size={16}/>Create New Investigation</button></div>
      {error&&<p className="caution" role="alert">{error}</p>}
      <section className="case-summary" aria-label="Case summary"><span><strong>{cases.filter(c=>c.status==='Active Review').length}</strong>active cases</span><span><strong>{cases.reduce((n,c)=>n+(c.counts.leads||0),0)}</strong>computed leads</span><span><strong>{cases.reduce((n,c)=>n+(c.counts.relationships||0),0)}</strong>sourced relationships</span></section>
      <section><div className="case-section-title"><div><h2>Needs attention</h2><p>Continue the next evidence or review action.</p></div><ShieldCheck size={20}/></div><div className="case-grid">{attention.map(c=><article className={'case-card'+(c.active?' active':'')} key={c.id}><div><span className="case-status-dot"/>{c.status}</div><h3>{c.name}</h3><p>{c.description}</p><dl><div><dt>Entities</dt><dd>{c.counts.entities||0}</dd></div><div><dt>Relationships</dt><dd>{c.counts.relationships||0}</dd></div><div><dt>Leads</dt><dd>{c.counts.leads||0}</dd></div></dl><button disabled={!c.active} onClick={onOpen}>{c.active?'Open investigation':'Reference case'}<ArrowRight size={14}/></button></article>)}</div></section>
      <section className="case-all"><div className="case-section-title"><div><h2>All cases</h2><p>Synthetic workspaces available to this local prototype.</p></div><FolderOpen size={20}/></div><div className="case-list">{cases.map(c=><div className="case-row" key={'all-'+c.id}><span className="case-status-dot"/><div><strong>{c.name}</strong><small>{c.id} · {c.status}</small></div><span>{c.counts.entities||0} entities · {c.counts.relationships||0} relationships</span><button disabled={!c.active} onClick={onOpen}>{c.active?'Open':'Reference'}</button></div>)}</div></section>
    </main>
    {creating&&<div className="case-modal-backdrop"><section className="case-create" role="dialog" aria-modal="true" aria-label="Create new investigation"><header><div><div className="eyebrow">NEW CASE</div><h2>Create investigation</h2></div><button aria-label="Close" onClick={()=>setCreating(false)}><X size={18}/></button></header><p>Start with an empty case. The graph and leads will be generated only from files you upload next.</p><label>Case title<input value={name} onChange={e=>setName(e.target.value)} autoFocus/></label><label>Internal reference<input value={reference} onChange={e=>setReference(e.target.value)}/></label><label>Purpose<textarea value={purpose} onChange={e=>setPurpose(e.target.value)}/></label><div className="case-create-actions"><button onClick={()=>setCreating(false)}>Cancel</button><button className="primary" disabled={busy||name.trim().length<3||reference.trim().length<3||purpose.trim().length<3} onClick={create}>{busy?'Creating…':'Create and add sources'}<ArrowRight size={14}/></button></div></section></div>}
  </div>
}
