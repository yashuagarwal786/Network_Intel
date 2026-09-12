import {useMemo,useState} from 'react';
import {Search,ArrowRight,X} from 'lucide-react';
import type {Entity} from '../demoTypes';
import {colors} from '../Graph';
export default function EntitySearch({nodes,onPick}:{nodes:Entity[];onPick:(id:string)=>void}){
 const [query,setQuery]=useState(''),[open,setOpen]=useState(false);
 const matches=useMemo(()=>nodes.filter(n=>[n.label,n.id,n.identifier,...n.aliases].some(v=>v.toLowerCase().includes(query.trim().toLowerCase()))).sort((a,b)=>Number(a.id.startsWith('I-'))-Number(b.id.startsWith('I-'))||a.label.localeCompare(b.label)).slice(0,7),[nodes,query]);
 function pick(id:string){onPick(id);setQuery('');setOpen(false)}
 return <div className="entity-search golden-search global-search"><Search size={16}/><input aria-label="Search entities" placeholder="Search entities, phones, accounts…" value={query} autoComplete="off" onFocus={()=>setOpen(true)} onChange={e=>{setQuery(e.target.value);setOpen(true)}} onKeyDown={e=>{if(e.key==='Escape')setOpen(false);if(e.key==='Enter'&&matches[0])pick(matches[0].id)}}/>{query&&<button aria-label="Clear search" onClick={()=>setQuery('')}><X size={13}/></button>}{open&&query.trim()&&<div className="search-results" role="listbox" aria-label="Entity search results">{matches.length?matches.map(n=><button role="option" aria-selected={false} key={n.id} onClick={()=>pick(n.id)}><i style={{background:colors[n.type]}}/><span>{n.label}<small>{n.type} · {n.identifier}</small></span><ArrowRight size={14}/></button>):<p>No matching entity. Try Rahul, P101 or A17.</p>}</div>}</div>
}
