"""Persistent state ownership, explicit versions and frozen baseline bootstrap."""
import json
from pathlib import Path
from . import snapshot, layout_update, validate

NAMES = ('layout-checkpoint.json', 'update-snapshot.json')


def read(path, allow_layout_migration=False):
    from . import canonical
    if canonical.installed(path):
        cp, previous, _, _, _ = canonical.restore(path)
        return cp, previous
    present = [(path / n).is_file() for n in NAMES]
    if not all(present):
        raise ValueError('STATE_MIGRATION_REQUIRED: persistent state missing/partial; use --bootstrap-state only when both files are absent')
    cp, previous = (json.loads((path/n).read_text()) for n in NAMES)
    if cp.get('state_schema_version') != snapshot.STATE_SCHEMA or previous.get('state_schema_version') != snapshot.STATE_SCHEMA:
        raise ValueError('STATE_MIGRATION_REQUIRED: incompatible state schema; no automatic fallback')
    for field, expected in [('layout_schema_version', snapshot.SCHEMA), ('layout_algorithm_version', snapshot.ALGORITHM)]:
        if (cp.get(field) != expected or previous.get(field) != expected) and not allow_layout_migration:
            raise ValueError('REBALANCE_REQUIRED: incompatible ' + field + '; explicit state migration required')
    checking = {**cp, 'layout_schema_version': snapshot.SCHEMA, 'layout_algorithm_version': snapshot.ALGORITHM}
    validate.checkpoint(checking)
    if previous.get('checkpoint_fingerprint') != snapshot.ordered_digest(cp):
        raise ValueError('STATE_INTEGRITY_MISMATCH: checkpoint/snapshot pair disagrees')
    category_parents = {key: parent for parent, r in cp['categories'].items() for key in r['sibling_order']}
    if set(cp['categories']) != {f'category:{k}' for k in previous['categories']}:
        raise ValueError('STATE_INTEGRITY_MISMATCH: category index/allocation disagree')
    for key in cp['categories']:
        parent = category_parents.get(key)
        if previous['categories'][key.split(':')[1]]['parent'] != snapshot.digest(int(parent.split(':')[1]) if parent else None):
            raise ValueError('STATE_INTEGRITY_MISMATCH: canonical category fingerprint/allocation disagree')
    topic_parents = {key: parent for parent, r in cp['categories'].items() for key in r['topic_order']}
    if set(topic_parents) != {f'topic:{k}' for k in previous['topics']}:
        raise ValueError('STATE_INTEGRITY_MISMATCH: topic index/order disagree')
    for key,parent in topic_parents.items():
        if previous['topics'][key.split(':')[1]]['parent'] != snapshot.digest(int(parent.split(':')[1])):
            raise ValueError('STATE_INTEGRITY_MISMATCH: canonical topic fingerprint/order disagree')
    return cp, previous


def complete(data, cp, geometry):
    previous = snapshot.index(data)
    previous['checkpoint_fingerprint'] = snapshot.ordered_digest(cp)
    previous['geometry_fingerprint'] = snapshot.ordered_digest(geometry)
    return previous


def baseline(runtime, source_data):
    accepted = json.loads((runtime / 'model.json').read_text())
    accepted['observations'] = source_data.get('observations', {})
    legacy = json.loads((runtime / 'layout-checkpoint.json').read_text())
    if legacy.get('layout_schema_version') != 5 or legacy.get('layout_algorithm_version') != 'atlas-spatial-5':
        raise ValueError('STATE_MIGRATION_REQUIRED: frozen bootstrap checkpoint incompatible')
    seeded = layout_update.bridge(runtime, action='bootstrap', data=accepted, legacy=legacy)
    cp = snapshot.presentation(seeded['checkpoint'])
    seeded = layout_update.bridge(runtime, action='restore', data=accepted, checkpoint=cp)
    geom = seeded['geometry']
    frozen = json.loads((Path(__file__).parent / 'fixtures/accepted-v6-geometry.json').read_text())['coordinates']
    coords = [[n['key'], n['x'], n['y'], n['width'], n['height']] for n in geom['nodes']]
    if sorted(coords) != sorted(frozen):
        raise ValueError('BASELINE_GEOMETRY_MISMATCH: bootstrap does not reproduce all frozen bounds exactly')
    validate.geometry(accepted, cp, geom)
    return accepted, cp, geom


def outputs(path, cp, previous):
    result = {NAMES[0]: snapshot.encode(cp), NAMES[1]: snapshot.encode(previous)}
    activation = path/'activation-state.json'
    if activation.exists(): result['activation-state.json'] = activation.read_bytes()
    readme = path/'README.md'
    if readme.exists(): result['README.md'] = readme.read_bytes()
    return result


def migrate_ordered_hashes(path, data, runtime):
    """One explicit, recognized state-schema 1 → 2 migration; no layout fallback."""
    cp, previous = (json.loads((path/n).read_text()) for n in NAMES)
    if cp.get('state_schema_version') != 1 or previous.get('state_schema_version') != 1:
        raise ValueError('STATE_MIGRATION_REQUIRED: only schema 1 ordered-hash migration is supported')
    if cp.get('layout_schema_version') != snapshot.SCHEMA or cp.get('layout_algorithm_version') != snapshot.ALGORITHM:
        raise ValueError('STATE_MIGRATION_REQUIRED: incompatible layout requires dedicated migration')
    if previous.get('checkpoint_fingerprint') != snapshot.digest(cp):
        raise ValueError('STATE_INTEGRITY_MISMATCH: legacy checkpoint pair disagrees')
    if previous['fingerprint'] != snapshot.index(data)['fingerprint']:
        raise ValueError('STATE_MIGRATION_REQUIRED: source must match legacy snapshot before migration')
    geom = layout_update.bridge(runtime,action='restore',data=data,checkpoint=cp)['geometry']
    if previous.get('geometry_fingerprint') != snapshot.digest(geom):
        raise ValueError('STATE_INTEGRITY_MISMATCH: legacy geometry/order no longer matches')
    candidate = {**cp,'state_schema_version':snapshot.STATE_SCHEMA}
    validate.geometry(data,candidate,geom)
    return candidate, complete(data,candidate,geom), geom
