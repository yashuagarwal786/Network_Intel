"""Deterministic additional source mentions; never overwrite originals."""
def extend(entities, relationships, evidence, sources, focus):
    for id, label, x, y in [('rk-sharma','R.K. Sharma',40,260),('a-verma','A. Verma',665,390)]:
        entities.append(dict(id=id,label=label,display_label=label,type='Person',identifier=id,
            description='Unresolved synthetic source mention. Similarity does not establish identity.',x=x,y=y,evidence_ids=[]))
        focus.append(id)
    source=dict(id='S09',filename='resolution-mentions.csv',type='Report',description='Fictional named mentions and asserted identifiers for resolution review.',representation='canonical_synthetic_records',evidence_ids=[])
    sources.append(source)
    rows=[('rk-sharma','P101','USES'),('rahul','V02','ASSOCIATED_WITH'),('rk-sharma','V02','ASSOCIATED_WITH'),('a-verma',None,None),('amit',None,None)]
    labels={n['id']:n['label'] for n in entities}
    for i,(person,asset,kind) in enumerate(rows,1):
        eid=f'E-RES-{i:02d}';rid=f'R-RES-{i:02d}';ids=[person]+([asset] if asset else [])
        excerpt=f'Mention: {labels[person]}; '+(f'{kind}: {asset}. Identity not independently verified.' if asset else 'No phone or vehicle identifier supplied.')
        evidence.append(dict(id=eid,source_id='S09',source_filename=source['filename'],source_type='Report',locator=dict(row=i+1,page=None,paragraph=None,fields=['name','associated_identifier']),timestamp='2026-08-15T17:00:00+05:30',exact_excerpt=excerpt,verification_status='Synthetic source record · not independently verified',entity_ids=ids,relationship_ids=[rid] if asset else []))
        source['evidence_ids'].append(eid)
        for n in entities:
            if n['id'] in ids:n['evidence_ids'].append(eid)
        if asset:relationships.append(dict(id=rid,source=person,target=asset,type=kind,status='recorded',evidence_ids=[eid],event_ids=[]))
