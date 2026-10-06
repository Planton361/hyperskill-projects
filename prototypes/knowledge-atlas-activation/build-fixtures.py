"""Offline fixture adapter: all synthetic evidence stays in this prototype.

The real planner requires numeric identities. Temporary numeric IDs exist only
inside the adapter; the exported plan and scene use fixture-topic:* identities.
"""
import copy
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import snapshot, state
from knowledge_atlas.activation import ActivationPlanner
from knowledge_atlas.catalog import Catalog


def remap(value, names):
    if isinstance(value, dict):
        return {k: remap(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [remap(v, names) for v in value]
    return names.get(value, value) if isinstance(value, str) else value


def build():
    data = snapshot.load_source(ROOT / 'data/knowledge')
    checkpoint, _ = state.read(ROOT / 'state/knowledge-atlas')
    geometry = json.loads((ROOT / 'docs/knowledge-map/geometry.js').read_text().split('=', 1)[1].rstrip(';\n'))
    real = Catalog(data)
    fixtures = {}
    fixtures['baseline'] = {'label': 'Baseline', 'plan': ActivationPlanner(real, checkpoint, geometry).plan('CURRENT_COURSE', [8]), 'display': []}
    # Each pair is (explicit global structural category ID, synthetic Topic count).
    cases = {
        'small': ([(428, 6)], []),
        'large': ([(428, 48), (482, 36), (1202, 36), (1203, 36)], []),
        'blocked': ([(428, 6)], [333, 336]),
        'new-root': ([(525, 3)], []),
        'major': ([(521, 8)], []),
    }
    for scenario, (groups, blocked) in cases.items():
        catalog = Catalog(copy.deepcopy(data))
        evidence = 'fixture-only-explicit'
        catalog.active['evidence'].append({'id': evidence, 'confidence': 'explicit', 'fixture_only': True})
        names = {'course:900000': 'fixture-course:reveal'}
        ids, display = [], []
        for parent, count in groups:
            assert f'category:{parent}' in catalog.categories
            for i in range(count):
                numeric = 900001 + len(ids)
                key = f'fixture-topic:{scenario}-{len(ids)+1:03}'
                title = f'Fixture {len(ids)+1:02} · test only'
                ids.append(numeric)
                names[f'topic:{numeric}'] = key
                catalog.topics[f'topic:{numeric}'] = {'id': numeric, 'title': title, 'parent_id': parent,
                                                     'resolution': 'PARTIAL_TOPIC', 'fixture_only': True}
                catalog.memberships[numeric] = {parent}
                catalog.active['edges'].append({'id': f'fixture-placement-{numeric}', 'type': 'hierarchy',
                                               'source': f'category:{parent}', 'target': f'topic:{numeric}',
                                               'evidence_ids': [evidence]})
                display.append({'key': key, 'title': title, 'parent': f'category:{parent}',
                                'type': 'topic', 'fixture_only': True, 'adapter_id': numeric})
        catalog.active['courses'].append({'id': 900000, 'title': 'Fixture only: reveal simulation',
                                          'topic_ids': ids + blocked, 'category_ids': [], 'project_ids': [],
                                          'evidence_ids': [evidence], 'fixture_only': True})
        plan = remap(ActivationPlanner(catalog, checkpoint, geometry).plan('CURRENT_COURSE', [900000]), names)
        # No synthetic number is represented as a real Hyperskill identifier.
        for row in plan['entities']:
            if row['id'].startswith('fixture-topic:'):
                row['hyperskill_id'] = None
                row['fixture_only'] = True
        plan['context']['course_ids'] = ['fixture-course:reveal']
        for row in plan['entities']:
            if row['id'] in plan['new_categories']:
                display.append({'key': row['id'], 'title': row['title'], 'parent': row['canonical_parent'],
                                'type': 'category', 'fixture_context': True})
        fixtures[scenario] = {'label': scenario, 'plan': plan, 'display': sorted(display, key=lambda r: r['key'])}
    return {'schema_version': 1, 'fixture_only': True, 'baseline_commit': '4e4a15bf4cfb7fb9abf587aebdae74033bb5624d',
            'catalog_counts': {'roots': 5, 'categories': len(real.categories),
                               'leaf_references': len(real.topics) + len(real.references),
                               'resolved_topics': 1, 'partial_topics': 88, 'unresolved_references': len(real.references)},
            'scenarios': fixtures}


if __name__ == '__main__':
    out = HERE / 'fixtures/scenarios.json'
    content = json.dumps(build(), indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if not out.exists() or out.read_text() != content:
        out.write_text(content)
    print('Prototype fixture plans generated offline; Knowledge and State unchanged.')
