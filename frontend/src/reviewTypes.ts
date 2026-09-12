export const reviewActions=['USEFUL_LEAD','FALSE_POSITIVE','IRRELEVANT','NEEDS_MORE_EVIDENCE','VERIFIED_RELATIONSHIP','INCORRECT_ENTITY_MERGE'] as const;
export type ReviewAction=typeof reviewActions[number];
export type ReviewInput={reviewer:string;action:ReviewAction;reason:string;idempotency_key:string;lead_revision:string;object_id?:string};
export type Review=ReviewInput & {review_id:string;case_id:string;lead_id:string;created_at:string};
export type AuditEvent={audit_event_id:string;case_id:string;actor:string;actor_type:string;action:string;object_type:string;object_id:string;old_state:Record<string,unknown>;new_state:Record<string,unknown>;reason:string;created_at:string;involved_entity_ids:string[];evidence_ids:string[];source_types:string[]};
export type TimelineItem={timeline_id:string;case_id:string;timestamp:string|null;category:string;event_type:string;title:string;description:string;entity_ids:string[];evidence_ids:string[];source_types:string[];object_id:string};
