import json
from pathlib import Path
from .demo_schemas import Case, Entity, Relationship, Evidence, Source, Event


class DemoRepository:
    """Load once and validate all fixture provenance before serving requests."""
    def __init__(self, root: Path | None = None):
        root = root or Path(__file__).with_name('data') / 'demo'
        raw = {name: json.loads((root / f'{name}.json').read_text(encoding='utf-8'))
               for name in ['entities','relationships','events','evidence','sources']}
        for name, value in raw.items():
            if (value['case_id'],value['synthetic'],value['data_version'],value['schema_version']) != ('VEIL-DEMO-001',True,'golden-v1',1):
                raise ValueError(f'{name}: inconsistent fixture metadata')
        self.case = Case.model_validate(raw['entities']['case'])
        for name, model in [('entities',Entity),('relationships',Relationship),('events',Event),('evidence',Evidence),('sources',Source)]:
            items = [model.model_validate(item) for item in raw[name]['items']]
            if len({x.id for x in items}) != len(items): raise ValueError(f'{name}: duplicate IDs')
            setattr(self,name,{x.id:x for x in items})
        def refs(ids, table, owner, required=False):
            if (required and not ids) or not set(ids)<=set(table):
                raise ValueError(f'{owner}: empty or unresolved references {ids}')
        refs(self.case.focus_entity_ids,self.entities,'case focus',True)
        refs([self.case.source_default,self.case.target_default],self.entities,'default path',True)
        for node in self.entities.values(): refs(node.evidence_ids,self.evidence,node.id,True)
        for r in self.relationships.values():
            refs([r.source,r.target],self.entities,r.id,True)
            refs(r.evidence_ids,self.evidence,r.id,True)
            refs(r.event_ids,self.events,r.id)
        for e in self.evidence.values():
            refs([e.source_id],self.sources,e.id,True)
            refs(e.entity_ids,self.entities,e.id,True)
            refs(e.relationship_ids,self.relationships,e.id)
            source=self.sources[e.source_id]
            if source.filename != e.source_filename or source.type != e.source_type or e.id not in source.evidence_ids:
                raise ValueError(f'{e.id}: source identity mismatch')
            if e.timestamp.utcoffset() is None: raise ValueError(f'{e.id}: timestamp needs timezone')
        for source in self.sources.values():refs(source.evidence_ids,self.evidence,source.id,True)
        for event in self.events.values():
            refs(event.entity_ids,self.entities,event.id,True)
            refs(event.evidence_ids,self.evidence,event.id,True)
            refs(event.relationship_ids,self.relationships,event.id)
        # Leads are computed from events; no fixture lead file is loaded.
        self.leads = {}
