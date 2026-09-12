"""Explainable demo rules and graph traversal. No guilt/leadership scores."""
from datetime import datetime
import networkx as nx

def select_edges(data, relationship=None, start=None, end=None, include_inferred=False):
    return [e for e in data['edges'] if (include_inferred or e['status']!='inferred') and (not relationship or e['type']==relationship) and (not start or datetime.fromisoformat(e['timestamp']).date()>=start) and (not end or datetime.fromisoformat(e['timestamp']).date()<=end)]

def find_path(data, source, target, edges):
    graph=nx.MultiGraph()
    graph.add_nodes_from(n['id'] for n in data['entities'])
    for e in edges: graph.add_edge(e['source'],e['target'],key=e['id'],record=e)
    try: nodes=nx.shortest_path(graph,source,target)
    except nx.NetworkXNoPath: return None
    relationships=[sorted(graph[a][b].values(),key=lambda x:x['record']['id'])[0]['record'] for a,b in zip(nodes,nodes[1:])]
    return dict(nodes=nodes,edges=relationships,hops=len(relationships),evidence_ids=sorted({v for e in relationships for v in e['evidence_ids']}),method='NetworkX shortest path; undirected associations; equal edge cost. A path does not establish causation.')

def temporal_leads(data):
    """Rule T01: >=3 calls in 30 min, then transfer within 30 min to linked holder."""
    edges=data['edges']; leads=[]
    def linked(person,kind):
        return [e for e in edges if e['source']==person and e['type']==kind and e['status']=='recorded']
    for tx in [e for e in edges if e['type']=='transfer']:
        senders=[e for e in edges if e['type']=='account holder' and e['target']==tx['source']]
        receivers=[e for e in edges if e['type']=='account holder' and e['target']==tx['target']]
        for sender in senders:
            for receiver in receivers:
                for phone1 in linked(sender['source'],'listed phone'):
                    for phone2 in linked(receiver['source'],'listed phone'):
                        t=datetime.fromisoformat(tx['timestamp'])
                        calls=sorted([e for e in edges if e['type']=='call' and e['source']==phone1['target'] and e['target']==phone2['target'] and 0<=(t-datetime.fromisoformat(e['timestamp'])).total_seconds()<=3600],key=lambda e:e['timestamp'])
                        if len(calls)<3: continue
                        last=datetime.fromisoformat(calls[-1]['timestamp'])
                        calls=[c for c in calls if (last-datetime.fromisoformat(c['timestamp'])).total_seconds()<=1800]
                        if len(calls)<3 or (t-last).total_seconds()>1800: continue
                        gap=int((t-last).total_seconds()/60)
                        signals=[dict(title=f'{len(calls)} calls within 30 minutes',detail='Same directed SIM pair. Metadata only; conversation content unknown.',evidence_ids=[i for c in calls for i in c['evidence_ids']]),dict(title=f'Transfer {gap} minutes after last call',detail='The cited transaction follows the call sequence. Temporal proximity is not causation.',evidence_ids=tx['evidence_ids']),dict(title='Record-based holder connections',detail='Phone and account associations connect the records. They do not prove who operated either device or account.',evidence_ids=sender['evidence_ids']+receiver['evidence_ids']+phone1['evidence_ids']+phone2['evidence_ids'])]
                        leads.append(dict(id='T01-'+tx['id'],title='Calls followed by a transfer',subtitle=next(n['label'] for n in data['entities'] if n['id']==sender['source'])+' ↔ '+next(n['label'] for n in data['entities'] if n['id']==receiver['source']),rule='T01 · temporal sequence · v1',generated_by='computed_rule',priority='Review suggested',signals=signals,evidence_ids=sorted({i for s in signals for i in s['evidence_ids']}),limitations=['Could reflect an ordinary delivery or business payment.','No population baseline, call content, or independent identity verification.','This rule is a transparent prototype heuristic, not a validated predictive model.']))
    return leads


def compute_network_roles(repo):
    """Explainable Network Role & Centrality Analysis.
    Computes betweenness centrality and degree to identify key facilitators/bridges
    and operational hubs without predicting criminality or intent.
    Strictly investigative triage context.
    """
    graph = nx.Graph()
    for n in repo.entities.values():
        graph.add_node(n.id)
    for r in repo.relationships.values():
        if getattr(r, 'status', 'recorded') == 'recorded':
            graph.add_edge(r.source, r.target)

    betweenness = nx.betweenness_centrality(graph)
    degree = dict(graph.degree())

    roles = []
    for node_id in sorted(repo.entities):
        node = repo.entities[node_id]
        b_score = betweenness.get(node_id, 0.0)
        d_val = degree.get(node_id, 0)

        if b_score >= 0.08:
            role = "BRIDGE / FACILITATOR"
            category = "BRIDGE"
            reason = "High betweenness centrality: Critical intermediary connecting separate communication or financial subgraphs."
        elif d_val >= 4:
            role = "OPERATIONAL HUB"
            category = "HUB"
            reason = "High connection degree: High interaction volume; potential operational coordinator or public utility."
        else:
            role = "PERIPHERAL RECORD"
            category = "PERIPHERAL"
            reason = "Standard association node with localized connectivity."

        roles.append({
            "entity_id": node_id,
            "entity_label": node.label,
            "entity_type": node.type,
            "degree": d_val,
            "betweenness": round(b_score, 4),
            "role": role,
            "category": category,
            "reason": reason,
            "disclaimer": "Centrality reflects graph structural position, not criminal leadership, intent, or guilt."
        })
    return sorted(roles, key=lambda x: (x['betweenness'], x['degree']), reverse=True)

