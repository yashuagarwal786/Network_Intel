import type {ReactNode} from 'react';
export function Badge({children,tone='neutral'}:{children:ReactNode;tone?:'neutral'|'info'|'pending'|'verified'|'signal'|'error'}){return <span className={'lab-badge '+tone}>{children}</span>}
export function Panel({title,subtitle,children,actions}:{title:string;subtitle?:string;children:ReactNode;actions?:ReactNode}){return <section className="lab-panel"><div className="lab-panel-heading"><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>{actions}</div>{children}</section>}
export const formatTime=(value:string)=>new Date(value).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',dateStyle:'medium',timeStyle:'short'})+' IST';
