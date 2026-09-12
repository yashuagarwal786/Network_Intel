import networkx as nx
from .demo_repository import DemoRepository
from .demo_schemas import PathResponse, Step


def compute_path(repo: DemoRepository, source: str, target: str, max_depth: int):
    """Bounded breadth-first traversal. Fixture display positions are not read."""
    graph = nx.MultiGraph()
    graph.add_nodes_from(sorted(repo.entities))
    for r in sorted(repo.relationships.values(),key=lambda r:(min(r.source,r.target),max(r.source,r.target),r.id)):
        if r.status == 'recorded': graph.add_edge(r.source,r.target,key=r.id)
    paths = nx.single_source_shortest_path(graph,source,cutoff=max_depth)
    ids = paths.get(target)
    if ids is None:return None
    edges = [repo.relationships[sorted(graph[a][b])[0]] for a,b in zip(ids,ids[1:])]
    steps = [Step(from_id=a,to_id=b,relationship_id=r.id,
                  traversal='forward' if r.source==a else 'reverse',evidence_ids=r.evidence_ids)
             for a,b,r in zip(ids,ids[1:],edges)]
    return PathResponse(nodes=[repo.entities[n] for n in ids],relationships=edges,node_ids=ids,
                        relationship_ids=[r.id for r in edges],evidence_ids=sorted({e for r in edges for e in r.evidence_ids}),
                        steps=steps,path_length=len(edges),max_depth=max_depth)
