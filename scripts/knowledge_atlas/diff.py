"""Stable machine-readable deltas; no changes disappear behind a single enum."""
from .classify import CONTRACTS
from .snapshot import digest


def delta(before, after):
    order = lambda items: sorted(items, key=lambda k: (not str(k).isdigit(), int(k) if str(k).isdigit() else str(k)))
    return {'added': order(after.keys() - before.keys()), 'removed': order(before.keys() - after.keys()),
            'changed': order(k for k in before.keys() & after.keys() if before[k] != after[k])}


def compare(before, after):
    result = {k: delta(before[k], after[k]) for k in
              ('topics', 'categories', 'projects', 'stages', 'courses', 'relations', 'requirements',
               'other_edges', 'evidence', 'observations', 'topic_states', 'project_states', 'course_states', 'stage_states')}
    types = set()
    for table, singular in [('topics', 'TOPIC'), ('categories', 'CATEGORY'),
                            ('projects', 'PROJECT'), ('courses', 'COURSE')]:
        for action, prefix in [('added', 'NEW'), ('removed', 'REMOVED')]:
            if result[table][action]:
                types.add(prefix + '_' + singular)
    for table, kind in [('topics', 'REPARENT_TOPIC'), ('categories', 'REPARENT_CATEGORY')]:
        result[table]['reparented'] = [{'id': int(k), 'before': before[table][k]['parent'],
                                       'after': after[table][k]['parent']}
                                      for k in result[table]['changed']
                                      if before[table][k]['parent'] != after[table][k]['parent']]
        if result[table]['reparented']:
            types.add(kind)
        if any(before[table][k]['metadata'] != after[table][k]['metadata'] for k in result[table]['changed']):
            types.add('METADATA_ONLY')
    for prop in ('learned', 'verified'):
        for value, suffix in [(True, 'added'), (False, 'removed')]:
            result['topics'][prop + '_' + suffix] = sorted({int(k.split(':')[0]) for k, state in after['topic_states'].items()
                 if state[prop] == digest(value) and before['topic_states'].get(k, {}).get(prop) != digest(value)})
    result['projects']['completed'] = sorted({int(k.split(':')[0]) for k, v in after['project_states'].items()
         if v['status'] == digest('completed') and before['project_states'].get(k, {}).get('status') != digest('completed')})
    statuses = {digest(s): s for s in ('active', 'completed', 'available', 'unknown')}
    result['projects']['state_transitions'] = [{'id': int(k.split(':')[0]),
           'before': statuses.get(before['project_states'].get(k, {}).get('status')),
           'after': statuses.get(after['project_states'][k]['status'])}
           for k in result['project_states']['added'] + result['project_states']['changed']]
    if any(result['project_states'].values()): types.add('PROJECT_STATE_ONLY')
    if result['stage_states']['changed']: types.add('PROJECT_STATE_ONLY')
    if any(result['topic_states'].values()): types.add('PROGRESS_ONLY')
    if any(result['course_states'].values()): types.add('PROGRESS_ONLY')
    if any(result['requirements'].values()) or any(result['stages'].values()): types.add('PROJECT_EVIDENCE_ONLY')
    if result['projects']['changed']: types.add('PROJECT_EVIDENCE_ONLY')
    if any(result['relations'].values()): types.add('RELATION_ONLY')
    if any(result['evidence'].values()) or any(result['observations'].values()): types.add('EVIDENCE_ONLY')
    result['courses']['membership_changed'] = [int(k) for k in result['courses']['changed']
         if before['courses'][k]['membership'] != after['courses'][k]['membership']]
    if result['courses']['membership_changed']: types.add('COURSE_MEMBERSHIP_ONLY')
    if any(before['courses'][k]['metadata'] != after['courses'][k]['metadata'] for k in result['courses']['changed']):
        types.add('METADATA_ONLY')
    if any(result['other_edges'].values()): types.add('METADATA_ONLY')
    for field, kind in [('layout_schema_version', 'LAYOUT_SCHEMA_CHANGE'),
                        ('layout_algorithm_version', 'LAYOUT_ALGORITHM_CHANGE')]:
        if before[field] != after[field]: types.add(kind)
    if before['fingerprint'] != after['fingerprint'] and not types:
        types.add('METADATA_ONLY')
    result['change_types'] = [k for k in CONTRACTS if k in (types or {'NO_CHANGE'})]
    result['label_changes'] = [f"{kind}:{k}" for table, kind in [('categories', 'category'), ('topics', 'topic')]
                               for k in result[table]['changed'] if before[table][k]['title'] != after[table][k]['title']]
    pairs = lambda rows: {'|'.join(k.split('|')[1:3]) for k in rows}
    result['relations']['pairs_added'] = sorted(pairs(after['relations']) - pairs(before['relations']))
    result['relations']['pairs_removed'] = sorted(pairs(before['relations']) - pairs(after['relations']))
    for table in ('topics', 'categories', 'projects', 'stages', 'courses', 'stage_states'):
        for action in ('added', 'removed', 'changed'):
            result[table][action] = [int(k) for k in result[table][action]]
    return result
