"""Read-only source identity and presentation boundary validation."""
import hashlib,json,pathlib
p=pathlib.Path(__file__).resolve().parents[1]
root=p.parents[1]
m=json.loads((p/'model.json').read_text())
for table in ['categories','topics','edges','projects','stages','courses','progress','evidence']:
    source=root/'data/knowledge'/f'{table}.json'
    assert m[table]==json.loads(source.read_text()),table
    assert m['source_hashes'][table]==hashlib.sha256(source.read_bytes()).hexdigest()
assert len(m['topics'])==89 and len(m['categories'])==46
assert sum(t['is_learned'] is True for t in m['progress']['topics'])==31
assert sum(t['is_verified'] is True for t in m['progress']['topics'])==12
assert not any(e['type']=='project_applies' for e in m['edges'])
assert len({e['target'] for e in m['edges'] if e['type']=='project_requires' and e['source']=='project:113'})==26
assert next(p for p in m['progress']['projects'] if p['project_id']==380)['completed_stage_ids']==[]
c=json.loads((p/'layout-checkpoint.json').read_text())
assert c['layout_schema_version']==5 and c['layout_algorithm_version']=='atlas-spatial-5'
assert len(c['categories'])==46
allowed={'anchor','width','height','box','band','childTop','children','sibling_order'}
for key,record in c['categories'].items():
    assert key.startswith('category:') and set(record)==allowed
    assert set(record['band'])=={'left','top','width','height','columns','rows','gapX','gapY','padding'}
    for child,slot in record['children'].items():
        assert child.startswith('category:') and set(slot)=={'x','y','width','height','overflow'}
assert 'topic:' not in json.dumps(c)
print('PASS: eight source tables identical; 89/46/31/12; exact 26 requirements; no applies; V6 presentation-only checkpoint')
