#!/usr/bin/env python3
"""Experimental read-only projection. Writes only this prototype's generated file."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas.catalog import Catalog
from knowledge_atlas import snapshot


def project(data, history):
    catalog = Catalog(data)
    active = set(history['active_categories'] + history['active_topics'])
    entities = []
    for kind, records in [('category', catalog.categories.values()),
                          ('topic', catalog.topics.values()),
                          ('reference', catalog.references.values())]:
        for row in records:
            key = f"{kind}:{row['id']}"
            parents = sorted(catalog.memberships.get(row['id'], set()))
            accepted = row.get('accepted_metadata', {})
            entity = dict(key=key, id=row['id'], kind=kind,
                          parents=[f'category:{i}' for i in parents],
                          active=key in active,
                          resolution=catalog.get_resolution_status(key),
                          fact_sources=row.get('fact_sources', {}),
                          evidence_ids=accepted.get('evidence_ids', []))
            if kind != 'reference':
                entity['title'] = row['title']
                entity['canonical_parent'] = accepted.get('canonical_parent_id', row.get('parent_id'))
            # References deliberately have no title, URL or canonical Topic metadata.
            entities.append(entity)
    by_key = {r['key']: r for r in entities}
    assert len(by_key) == len(entities)
    def keys(projection):
        return sorted(f'{kind}:{r["id"]}' for table, kind in
                      [('categories', 'category'), ('topics', 'topic'), ('unresolved_references', 'reference')]
                      for r in projection[table])
    courses = []
    for row in sorted(data['courses'], key=lambda r: r['id']):
        courses.append({**row, 'key': f'course:{row["id"]}',
                        'scope': keys(catalog.get_course_projection(row['id']))})
    projects = []
    for row in sorted(data['projects'], key=lambda r: r['id']):
        stages = sorted([s for s in data['stages'] if s['project_id'] == row['id']], key=lambda s: s['position'])
        edges = sorted([e for e in data['edges'] if e['type'] == 'project_requires' and e['source'] == f'project:{row["id"]}'], key=lambda e: e['id'])
        # Complete inventory must be loaded; no edges alone prove a complete empty set.
        complete = bool(row['stage_ids']) and {s['id'] for s in stages} == set(row['stage_ids']) and all(s.get('required_topic_ids') is not None for s in stages)
        projects.append({**row, 'key': f'project:{row["id"]}',
                         'requirements_status': 'LOADED' if complete else 'UNKNOWN',
                         'required': sorted({e['target'] for e in edges}), 'requirements': edges,
                         'stages': [{**s, 'key': f'stage:{s["id"]}'} for s in stages],
                         'scope': keys(catalog.get_project_context(row['id']))})
    return dict(schema_version=1, experimental=True, authoritative=False,
                entities=sorted(entities, key=lambda r: r['key']),
                roots=sorted(r['key'] for r in entities if r['kind'] == 'category' and not r['parents']),
                hierarchy=sorted([[f'category:{p}', next(k for k in (f'category:{c}', f'topic:{c}', f'reference:{c}') if k in by_key)] for p, c in catalog.latest_hierarchy]),
                personal=sorted(active), courses=courses, projects=projects,
                progress=data['progress']['topics'], evidence=data['evidence'],
                provenance=catalog.provenance, observations=catalog.observation_ids,
                counts=dict(categories=len(catalog.categories), topics=len(catalog.topics),
                            references=len(catalog.references), positions=len(entities),
                            hierarchy=len(catalog.latest_hierarchy)))


def encoded():
    return snapshot.encode(project(snapshot.load_source(ROOT / 'data/knowledge'),
                                   json.loads((ROOT / 'state/knowledge-atlas/activation-state.json').read_text())))


if __name__ == '__main__':
    start = time.perf_counter()
    payload = encoded()
    destination = Path(__file__).resolve().parent / 'generated/catalog.json'
    if '--check' in sys.argv:
        assert destination.read_bytes() == payload, 'Stale prototype projection'
    else:
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(payload)
    print(json.dumps({'bytes': len(payload), 'build_ms': round((time.perf_counter()-start)*1000, 2)}))
