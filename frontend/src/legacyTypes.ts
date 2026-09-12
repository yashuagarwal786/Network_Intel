export type Entity={id:string;label:string;type:string;x:number;y:number;description:string};
export type Edge={id:string;source:string;target:string;type:string;status:string;evidence_ids:string[];timestamp:string};
export type Evidence={id:string;kind:string;file:string;locator:string;timestamp:string;excerpt:string};
export type Lead={id:string;title:string;subtitle:string;rule:string;priority:string;signals:{title:string;detail:string;evidence_ids:string[]}[];evidence_ids:string[];limitations:string[]};
export type Alias={id:string;left:string;right:string;evidence_ids:string[];reason:string};
export type CaseData={case:{name:string;reference:string};entities:Entity[];edges:Edge[];evidence:Evidence[];leads:Lead[];aliases:Alias[]};
export type PathResult={nodes:string[];edges:Edge[];hops:number;evidence_ids:string[];method:string};
export type Audit={id:number;target_type:string;target_id:string;decision:string;rationale:string;actor:string;created_at:string};
export async function api<T>(url:string,options?:RequestInit):Promise<T>{const response=await fetch('/api'+url,options);if(!response.ok){let message='Request failed';try{const body=await response.json();message=typeof body.detail==='string'?body.detail:'Please check the submitted fields.';}catch{}throw new Error(message)}return response.json()}
