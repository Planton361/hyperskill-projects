"""Canonical serialization and compact comparison indexes, never layout state."""
import hashlib
import json
from pathlib import Path

TABLES = ('courses', 'categories', 'topics', 'projects', 'stages', 'edges', 'progress', 'evidence')
STATE_SCHEMA = 2
SCHEMA = 2
ALGORITHM = 'atlas-incremental-2'


def canonical(value):
    # All source arrays in v1 are sets/inventories. Stage position is an explicit field.
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        def key(v):
            if type(v) in (int, float): return (0, v)
            if isinstance(v, str): return (1, v)
            if isinstance(v, dict) and type(v.get('id')) is int: return (2, v['id'])
            return (3, json.dumps(v, sort_keys=True))
        return sorted((canonical(v) for v in value), key=key)
    return value


def encode(value):
    # Presentation arrays have intentional order: never sort them here.
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def presentation(value):
    """Six decimal layout units; geometry is reconstructed using relative offsets."""
    if isinstance(value, dict): return {k: presentation(v) for k, v in value.items()}
    if isinstance(value, list): return [presentation(v) for v in value]
    if isinstance(value, float):
        rounded = round(value, 6)
        return int(rounded) if rounded.is_integer() else rounded
    return value


def digest(value):
    return hashlib.sha256(encode(canonical(value))).hexdigest()


def ordered_digest(value):
    """Presentation array order is meaningful; never normalize it away."""
    return hashlib.sha256(encode(value)).hexdigest()


def load_source(path):
    data = {t: json.loads((Path(path) / (t + '.json')).read_text()) for t in TABLES}
    data['observations'] = {'observations/' + p.name: json.loads(p.read_text())
                            for p in sorted((Path(path) / 'observations').glob('*.json'))}
    return canonical(data)


def index(data):
    out = {'state_schema_version': STATE_SCHEMA, 'layout_schema_version': SCHEMA,
           'layout_algorithm_version': ALGORITHM,
           'fingerprint': digest({k: data[k] for k in (*TABLES, 'observations') if k in data})}
    for table in ('topics', 'categories'):
        out[table] = {str(r['id']): {'parent': digest(r['canonical_parent_id']), 'title': digest(r['title']),
                     'metadata': digest({k: v for k, v in r.items() if k != 'canonical_parent_id'})}
                     for r in sorted(data[table], key=lambda r: r['id'])}
    out['courses'] = {str(r['id']): {'membership': digest({k: r[k] for k in
                       ('topic_ids', 'category_ids', 'project_ids')}),
                       'metadata': digest({k: v for k, v in r.items() if k not in
                                           ('topic_ids', 'category_ids', 'project_ids', 'topics_count')})}
                      for r in data['courses']}
    out['projects'] = {str(r['id']): digest(r) for r in data['projects']}
    state_fields = ('status', 'is_completed', 'completed_at')
    out['stages'] = {str(r['id']): digest({k: v for k, v in r.items() if k not in state_fields}) for r in data['stages']}
    out['stage_states'] = {str(r['id']): digest({k: r[k] for k in state_fields if k in r}) for r in data['stages']}
    out['project_states'] = {str(r['project_id']) + ':' + str(r.get('course_id')):
                            {'status': digest(r['status']), 'fingerprint': digest(r)}
                            for r in data['progress']['projects']}
    out['topic_states'] = {str(r['topic_id']) + ':' + str(r.get('course_id')):
                          {'learned': digest(r.get('is_learned')), 'verified': digest(r.get('is_verified')),
                           'fingerprint': digest(r)} for r in data['progress']['topics']}
    out['course_states'] = {str(r['course_id']): digest(r) for r in data['progress']['courses']}
    for field, types in [('relations', ('prerequisite', 'dependent')),
                         ('requirements', ('project_requires',)),
                         ('other_edges', ('hierarchy', 'course_contains', 'project_applies'))]:
        out[field] = {f"{r['type']}|{r['source']}|{r['target']}|{r.get('stage_id', '')}": digest(r)
                      for r in data['edges'] if r['type'] in types}
    out['evidence'] = {r['id']: digest(r) for r in data['evidence']}
    out['observations'] = {k: digest(v) for k, v in data.get('observations', {}).items()}
    return canonical(out)
