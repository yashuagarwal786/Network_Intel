import {useState} from 'react';
import {FileText,ArrowUpRight} from 'lucide-react';

export default function EvidenceRefs({ids,onOpen}:{ids:string[];onOpen:(id:string)=>void}){
  const [expanded,setExpanded]=useState(false);
  return <div className="refs">{(expanded?ids:ids.slice(0,3)).map(id=><button key={id} onClick={()=>onOpen(id)} aria-label={'Open evidence '+id}><FileText size={11}/>{id}<ArrowUpRight size={11}/></button>)}
    {ids.length>3&&<button onClick={()=>setExpanded(!expanded)}>{expanded?'Show fewer':`+${ids.length-3} more`}</button>}
  </div>;
}
