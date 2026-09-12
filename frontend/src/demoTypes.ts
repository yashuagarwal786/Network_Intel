export type EntityType = 'Person'|'Phone'|'Account'|'Vehicle'|'Location'|'Organization';
export type ExtractionProvenance={source_id:string;evidence_id:string;evidence_text:string;span_start:number|null;span_end:number|null;extraction_method:string;confidence:number|null};
export type Entity = {id:string;label:string;display_label:string;type:EntityType;identifier:string;description:string;x:number;y:number;evidence_ids:string[];aliases:string[];original_entity_ids:string[];extraction_provenance?:ExtractionProvenance[];verification_status?:string};
export type Relationship = {id:string;source:string;target:string;type:string;status:'recorded'|'inferred';evidence_ids:string[];event_ids:string[];verification_status:string;extractor_version:string|null;extraction_provenance?:ExtractionProvenance[]};
export type Case = {id:string;name:string;classification:string;status:string;timezone:string;description:string;event_label:string;event_timestamp:string;source_default:string;target_default:string;focus_entity_ids:string[];max_depth:number};
export type Source = {id:string;filename:string;type:string;description:string;representation:string;evidence_ids:string[]};
export type {ComputedLead as Lead,ComputedSignal as Signal} from './leadTypes';
export type Evidence = {id:string;source_id:string;source_filename:string;source_type:string;locator:{row:number|null;page:number|null;paragraph:number|null;span_start:number|null;span_end:number|null;fields:string[]};timestamp:string|null;parser_version:string|null;source_record_id:string|null;exact_excerpt:string;verification_status:string;entity_ids:string[];relationship_ids:string[]};
export type GraphData = {nodes:Entity[];relationships:Relationship[]};
export type PathResult = GraphData & {node_ids:string[];relationship_ids:string[];steps:{from_id:string;to_id:string;relationship_id:string;traversal:'forward'|'reverse';evidence_ids:string[]}[];evidence_ids:string[];path_length:number;max_depth:number;method:string;disclaimer:string};
export type CaseResponse = {case:Case;counts:Record<string,number>};
export type Selection = {kind:'entity'|'relationship'|'lead'|'source'|'resolution';id:string}|{kind:'path';id:'path'}|{kind:'evidence';id:string};

export type MatchProposal={proposal_id:string;left_entity_id:string;right_entity_id:string;left_entity:Entity;right_entity:Entity;feature_comparisons:{feature:string;value:number;weight:number;explanation:string;evidence_ids:string[]}[];score:number;recommendation:string;status:string;algorithm_version:string;supporting_evidence_ids:string[];match_reason:string;strong_identifier_matches:string[]};
export type ResolutionDecision={decision_id:string;proposal_id:string;action:string;reviewer:string;reason:string;created_at:string;undoes_decision_id:string|null};
export type NetworkRole = {entity_id:string;entity_label:string;entity_type:EntityType;degree:number;betweenness:number;role:string;category:'BRIDGE'|'HUB'|'PERIPHERAL';reason:string;disclaimer:string};

