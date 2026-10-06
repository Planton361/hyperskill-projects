"""Generalized source evidence contract; baseline-specific assertions stay in old tests."""
import math
TYPES = {'courses': 'course', 'categories': 'category', 'topics': 'topic', 'projects': 'project', 'stages': 'stage'}


def validate_global_catalog(observation):
    """Separate data-forest contract; V6's active single-root contract is intact."""
    from .catalog_observation import validate_observation
    return validate_observation(observation)

def validate_evidence(data):
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    evidence = {e['id']: e for e in data['evidence']}
    entities = {}
    for table, kind in TYPES.items():
        rows = data[table]
        require(len({x['id'] for x in rows}) == len(rows), f'duplicate IDs: {table}')
        for row in rows:
            require(isinstance(row['id'], int), f'non-numeric Hyperskill ID: {table}')
            entities[f"{kind}:{row['id']}"] = row
    require(len(evidence) == len(data['evidence']), 'duplicate evidence IDs')
    def check_evidence(row):
        refs = row.get('evidence_ids', [])
        require(bool(refs) and all(x in evidence for x in refs), 'missing evidence')
    for row in entities.values():
        check_evidence(row)
    require(len({e['id'] for e in data['edges']}) == len(data['edges']), 'duplicate edge IDs')
    signatures = set()
    for edge in data['edges']:
        kind, source, target = edge['type'], edge['source'], edge['target']
        require(source in entities and target in entities, 'dangling edge')
        check_evidence(edge)
        require(all(evidence[e]['confidence'] == 'explicit' for e in edge['evidence_ids']), 'non-explicit edge')
        require(kind in ('hierarchy', 'prerequisite', 'dependent', 'project_requires', 'project_applies', 'course_contains'), 'unknown relation')
        signature = (kind, source, target, edge.get('stage_id'))
        require(signature not in signatures, 'duplicate relationship')
        signatures.add(signature)
        if kind in ('project_requires', 'project_applies'):
            require(source.startswith('project:') and target.startswith('topic:'), 'invalid project relation endpoints')
        if kind in ('prerequisite', 'dependent'):
            require(source.startswith('topic:') and target.startswith('topic:'), 'invalid topic relation endpoints')
        if kind == 'hierarchy':
            require(source.startswith('category:') and target.split(':')[0] in ('category','topic'), 'invalid hierarchy')
        if kind == 'project_applies':
            require(any(evidence[e].get('assertion') == {'type': kind, 'source': source, 'target': target} for e in edge['evidence_ids']), 'project_applies needs a matching explicit application assertion')
        if 'stage_id' in edge:
            stage = entities.get(f"stage:{edge['stage_id']}")
            require(stage is not None and source == f"project:{stage['project_id']}", 'invalid edge stage')
            if kind == 'project_requires':
                require(int(target.split(':')[1]) in stage['required_topic_ids'], 'stage does not require target')
    for course in data['courses']:
        for field, kind in [('topic_ids','topic'),('category_ids','category'),('project_ids','project')]:
            ids = course[field]
            require(len(ids) == len(set(ids)), f'duplicate course {field}')
            require(all(f'{kind}:{i}' in entities for i in ids), f'unknown course {field}')
        require(len(course['topic_ids']) == course['topics_count'], 'course count mismatch')
    for stage in data['stages']:
        require(f"project:{stage['project_id']}" in entities, 'missing stage project')
        for field in ('required_topic_ids','cumulative_required_topic_ids'):
            require(all(f'topic:{i}' in entities for i in stage[field]), 'missing stage topic')
    p = data['progress']
    for snapshot in data.get('observations', {}).values():
        course = entities.get(f"course:{snapshot['course_id']}")
        require(course is not None, 'unknown observation course')
        rows = snapshot['topics']
        ids = [r['topic_id'] for r in rows]
        require(len(ids) == len(set(ids)) and set(ids) <= set(course['topic_ids']), 'observation coverage mismatch')
        require(all(type(r['is_learned']) is bool and type(r['is_skipped']) is bool for r in rows), 'invalid observation booleans')
        learned = sorted(r['topic_id'] for r in rows if r['is_learned'])
        require(snapshot['learned_topic_ids'] == learned and len(learned) == snapshot['learned_topics_count'], 'observation learned mismatch')
        require(sum(r['is_skipped'] for r in rows) == snapshot['skipped_topics_count'], 'observation skipped mismatch')
    for table, kind in [('courses','course'),('topics','topic'),('projects','project')]:
        require(len({(x.get('course_id'), x[kind+'_id']) for x in p[table]}) == len(p[table]), 'duplicate progress')
        for item in p[table]:
            require(f"{kind}:{item[kind+'_id']}" in entities, 'unknown progress entity')
            check_evidence(item)
    for item in p['topics']:
        require(type(item.get('is_learned')) is bool, 'non-boolean learned status')
        require(type(item.get('is_skipped')) is bool, 'non-boolean skipped status')
        expected_verified = None if item.get('verification_status') is None else item['verification_status'] == 'verified'
        require(item.get('is_verified') is expected_verified, 'verification status mismatch')
        for ref in item['evidence_ids']:
            filename = evidence[ref].get('snapshot_file')
            if filename:
                snapshot = data.get('observations', {}).get(filename)
                require(snapshot is not None, 'missing observation snapshot')
                matches = [t for t in snapshot['topics'] if t['topic_id'] == item['topic_id']]
                require(len(matches) == 1, 'missing or duplicate observation topic')
                require(snapshot['course_id'] == item['course_id'], 'observation course mismatch')
                require(item.get('observed_at') == snapshot['observed_at'], 'observation timestamp mismatch')
                require(all(item.get(k) == matches[0].get(k) for k in ('is_learned','is_skipped','is_completed','verification_status')), 'status disagrees with observation')
        if item.get('is_applied') is True:
            assertion = {'type':'topic_applied','topic_id':item['topic_id']}
            require(any(evidence[e].get('assertion') == assertion for e in item['evidence_ids']), 'unproven applied topic')
    for item in p['courses']:
        course = entities[f"course:{item['course_id']}"]
        for field, total in [('learned_topics_count','learned_topics_total'),('applied_topics_count','applied_topics_total')]:
            require(0 <= item[field] <= item[total], 'invalid progress counts')
        require(item['learned_topics_total'] == course['topics_count'] and item['applied_topics_total'] == course['capstone_topics_count'], 'progress denominator mismatch')
        for field, count, status in [('learned_topic_ids','learned_topics_count','is_learned'),('applied_topic_ids','applied_topics_count','is_applied')]:
            if item[field] is not None:
                require(len(set(item[field])) == len(item[field]) == item[count], 'incomplete full status set')
                explicit = {t['topic_id'] for t in p['topics'] if t.get(status) is True and t['course_id'] == item['course_id']}
                require(set(item[field]) == explicit, 'unproven full status set')
        if item.get('topic_status_coverage') == 'complete':
            rows = [t for t in p['topics'] if t['course_id'] == item['course_id']]
            require({t['topic_id'] for t in rows} == set(course['topic_ids']), 'incomplete topic coverage')
            require(sum(t['is_learned'] for t in rows) == item['learned_topics_count'], 'learned count mismatch')
            require(sum(t['is_skipped'] for t in rows) == item['skipped_topics_count'], 'skipped count mismatch')
            verified = sorted(t['topic_id'] for t in rows if t['is_verified'] is True)
            require(item.get('verified_topic_ids') == verified, 'verified IDs mismatch')
            for t in rows:
                require(any(evidence[e].get('snapshot_file') for e in t['evidence_ids']), 'complete status needs observation evidence')
    return entities


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(data, canonical=False):
    """Validate normalized v1 tables before any layout or write."""
    for table in (*TYPES, 'edges', 'evidence'):
        require(isinstance(data.get(table), list), 'schema: expected array ' + table)
        require(all(isinstance(r, dict) for r in data[table]), 'schema: expected objects ' + table)
    require(isinstance(data.get('progress'), dict), 'schema: progress object required')
    for table in TYPES:
        for r in data[table]:
            require(type(r.get('id')) is int and r['id'] > 0, 'schema: invalid ID ' + table)
            require(isinstance(r.get('title'), str) and bool(r['title']), 'schema: title required ' + table)
    for table in ('categories', 'topics'):
        for r in data[table]:
            require('canonical_parent_id' in r, 'missing canonical parent ' + str(r['id']))
    categories = {r['id']: r for r in data['categories']}
    require(len(categories) == len(data['categories']), 'duplicate IDs: categories')
    roots = [r for r in categories.values() if r['canonical_parent_id'] is None]
    require(bool(roots) if canonical else len(roots) == 1, 'taxonomy must have canonical roots')
    for row in data['categories'] + data['topics']:
        parent = row['canonical_parent_id']
        require(parent in categories or (row in roots), 'missing canonical parent ' + str(row['id']))
        seen = {row['id']} if row in data['categories'] else set()
        while parent is not None:
            require(parent not in seen, 'taxonomy cycle at ' + str(parent))
            seen.add(parent)
            require(parent in categories, 'missing canonical ancestor')
            parent = categories[parent]['canonical_parent_id']
    entities = validate_evidence(data)
    hierarchy = {(e['source'], e['target']) for e in data['edges'] if e['type'] == 'hierarchy'}
    for table, kind in [('categories', 'category'), ('topics', 'topic')]:
        for row in data[table]:
            if row['canonical_parent_id'] is not None:
                require((f"category:{row['canonical_parent_id']}", f"{kind}:{row['id']}") in hierarchy,
                        'canonical hierarchy evidence missing')
    adjacency = {}
    for source, target in hierarchy:
        if target.startswith('category:'): adjacency.setdefault(source, []).append(target)
    visiting, visited = set(), set()
    def walk(key):
        require(key not in visiting, 'hierarchy membership cycle')
        if key in visited: return
        visiting.add(key)
        for target in adjacency.get(key, []): walk(target)
        visiting.remove(key); visited.add(key)
    for key in adjacency: walk(key)
    projects = {r['id']: r for r in data['projects']}
    stages = {r['id']: r for r in data['stages']}
    courses = {r['id']: r for r in data['courses']}
    for course in courses.values():
        require(set(course['topic_ids']) == {r['id'] for r in data['topics'] if r['id'] in course['topic_ids']},
                'invalid course membership')
    for project in projects.values():
        require(len(project['stage_ids']) == len(set(project['stage_ids'])), 'duplicate project stage IDs')
    for stage in stages.values():
        require(stage['id'] in projects[stage['project_id']]['stage_ids'], 'invalid stage inventory reference')
        require(type(stage['position']) is int and stage['position'] > 0, 'invalid stage position')
        for field in ('required_topic_ids', 'cumulative_required_topic_ids'):
            require(len(stage[field]) == len(set(stage[field])), 'duplicate stage requirement')
        require(set(stage['required_topic_ids']) <= set(stage['cumulative_required_topic_ids']),
                'invalid cumulative stage requirements')
        targets = {int(e['target'].split(':')[1]) for e in data['edges']
                   if e['type'] == 'project_requires' and e.get('stage_id') == stage['id']}
        require(targets == set(stage['required_topic_ids']), 'stage requirements/edges disagree')
    for project in projects:
        rows = sorted((s for s in stages.values() if s['project_id'] == project), key=lambda s: s['position'])
        require(len({s['position'] for s in rows}) == len(rows), 'duplicate stage position')
        cumulative = set()
        for stage in rows:
            cumulative |= set(stage['required_topic_ids'])
            # Partial stage inventories may include earlier unloaded requirements.
            require(cumulative <= set(stage['cumulative_required_topic_ids']), 'inconsistent cumulative requirements')
    for r in data['progress']['projects']:
        require(r['status'] in ('active', 'completed', 'available', 'unknown'), 'invalid project status')
        ids = r.get('completed_stage_ids')
        require(ids is None or (isinstance(ids, list) and len(ids) == len(set(ids)) and
                set(ids) <= set(projects[r['project_id']]['stage_ids'])), 'invalid completed stage reference')
        require(not (r['status'] == 'available' and ids), 'available project has completed stages')
    for r in data['progress']['courses']:
        course = courses[r['course_id']]
        active = r.get('active_project')
        require(active is None or active in course['project_ids'], 'active project outside course')
        require(set(r.get('completed_projects', [])) <= set(course['project_ids']), 'completed project outside course')
        states = {p['project_id']: p['status'] for p in data['progress']['projects'] if p['course_id'] == r['course_id']}
        require(active is None or states.get(active) == 'active', 'active project status disagrees with course')
        require(all(states.get(p) == 'completed' for p in r.get('completed_projects', [])), 'completed project status disagrees with course')
    for table, field, membership in [('topics', 'topic_id', 'topic_ids'), ('projects', 'project_id', 'project_ids')]:
        for r in data['progress'][table]:
            require(r.get('course_id') in courses, 'unknown progress course')
            require(r[field] in courses[r['course_id']][membership], 'progress outside course membership')
    for e in data['edges']:
        if e['type'] in ('prerequisite', 'dependent'):
            require(e['source'] != e['target'], 'self relation')
        if e['type'] == 'course_contains':
            require(e['source'].startswith('course:'), 'invalid course_contains source')
            target_type, target_id = e['target'].split(':')
            field = {'category': 'category_ids', 'topic': 'topic_ids', 'project': 'project_ids'}.get(target_type)
            require(field is not None and int(target_id) in courses[int(e['source'].split(':')[1])][field],
                    'course edge disagrees with membership')
    return entities


def checkpoint(cp, category_keys=None):
    from .snapshot import SCHEMA, ALGORITHM, STATE_SCHEMA
    require(cp.get('state_schema_version') == STATE_SCHEMA, 'STATE_MIGRATION_REQUIRED: checkpoint state schema mismatch')
    require(cp.get('layout_schema_version') == SCHEMA, 'checkpoint schema mismatch; explicit migration required')
    require(cp.get('layout_algorithm_version') == ALGORITHM, 'checkpoint algorithm mismatch; explicit migration required')
    require(set(cp) == {'state_schema_version', 'layout_schema_version', 'layout_algorithm_version', 'presentation_generation', 'categories'},
            'unexpected checkpoint fields')
    require(type(cp['presentation_generation']) is int and cp['presentation_generation'] >= 0, 'invalid generation')
    fields = {'slot_anchor', 'visible_extent', 'allocated_width', 'allocated_height', 'reserved_capacity',
              'sibling_order', 'topic_order', 'card_allocation', 'tray_allocation', 'slot_row'}
    for key, r in cp['categories'].items():
        require(key.startswith('category:') and set(r) == fields, 'invalid presentation region ' + key)
        for field, names in [('slot_anchor', {'x', 'y'}), ('visible_extent', {'left', 'top', 'width', 'height'}),
                             ('reserved_capacity', {'width', 'height'})]:
            require(set(r[field]) == names, 'unexpected checkpoint region field')
            require(all(type(x) in (float, int) and math.isfinite(x) for x in r[field].values()), 'invalid checkpoint number')
        require(r['allocated_width'] + .001 >= r['visible_extent']['width'] >= 0 and
                r['allocated_height'] + .001 >= r['visible_extent']['height'] >= 0, 'region capacity exhausted')
        for field in ('sibling_order', 'topic_order'):
            require(len(r[field]) == len(set(r[field])), 'duplicate stable order')
        require(r['reserved_capacity']['width'] >= 0 and r['reserved_capacity']['height'] >= 0, 'negative reserve')
        require(abs(r['reserved_capacity']['width'] - max(0, r['allocated_width']-r['visible_extent']['width'])) < .001 and
                abs(r['reserved_capacity']['height'] - max(0, r['allocated_height']-r['visible_extent']['height'])) < .001,
                'reserve accounting mismatch')
        require(set(r['card_allocation']) == {'width', 'height', 'font', 'line'}, 'invalid card allocation')
        require(type(r['slot_row']) is int and r['slot_row'] >= 0, 'invalid slot row')
        require(all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in r['card_allocation'].values()), 'invalid card measurement')
        tray = r['tray_allocation']
        if tray is not None:
            require(set(tray) == {'left', 'top', 'width', 'height', 'padding', 'row_gap', 'rows'}, 'invalid tray allocation')
            require(all(type(tray[k]) in (int, float) and math.isfinite(tray[k]) for k in tray if k != 'rows'), 'invalid tray measurement')
            require(len({s['key'] for s in tray['rows']}) == len(tray['rows']), 'duplicate row allocation')
            for slot in tray['rows']:
                require(set(slot) == {'key', 'width', 'height'} and slot['key'].startswith('topic:'), 'invalid row allocation')
                require(slot['width'] > 0 and slot['height'] > 0, 'invalid row measurement')
    if category_keys is not None:
        require(set(cp['categories']) == set(category_keys), 'checkpoint category inventory mismatch')


def geometry(data, cp, geom):
    """Semantic boxes, tray containment, region containment and strict hierarchy crossings."""
    nodes = {r['key']: r for r in geom['nodes']}
    require(len(nodes) == len(geom['nodes']), 'duplicate topic/category geometry')
    expected = {f"{kind}:{r['id']}": r for table, kind in [('topics', 'topic'), ('categories', 'category')]
                for r in data[table]}
    require(set(nodes) == set(expected), 'orphan/missing geometry node')
    checkpoint(cp, [k for k in expected if k.startswith('category:')])
    for n in nodes.values():
        require(all(type(n[f]) in (int, float) and math.isfinite(n[f]) for f in ('x', 'y', 'width', 'height')),
                'invalid geometry number')
    rects = [{'key': n['key'], 'x': n['x'] - n['width']/2, 'y': n['y'], 'w': n['width'], 'h': n['height']}
             for n in nodes.values() if n['key'].startswith('category:')]
    trays = {t['parent']: t for t in geom['trays']}
    require(len(trays) == len(geom['trays']), 'duplicate tray')
    rects += [{'key': t['parent'] + ' tray', 'x': t['x'], 'y': t['y'], 'w': t['width'], 'h': t['height']}
              for t in trays.values()]
    def intersects(a, b):
        return (a['x'] < b['x'] + b['w'] - .001 and a['x'] + a['w'] > b['x'] + .001 and
                a['y'] < b['y'] + b['h'] - .001 and a['y'] + a['h'] > b['y'] + .001)
    for i, a in enumerate(rects):
        for b in rects[i+1:]:
            require(not intersects(a, b), 'semantic overlap: ' + a['key'] + ', ' + b['key'])
    topic_rects = []
    for key, row in expected.items():
        if not key.startswith('topic:'): continue
        parent = 'category:' + str(row['canonical_parent_id'])
        require(parent in trays and key in trays[parent]['topics'], 'topic outside canonical tray ' + key)
        n, t = nodes[key], trays[parent]
        r = {'key': key, 'x': n['x'] - n['width']/2, 'y': n['y'], 'w': n['width'], 'h': n['height']}
        require(r['x'] >= t['x'] - .001 and r['x'] + r['w'] <= t['x'] + t['width'] + .001 and
                r['y'] >= t['y'] - .001 and r['y'] + r['h'] <= t['y'] + t['height'] + .001, 'topic tray containment ' + key)
        for other in topic_rects:
            require(not intersects(r, other), 'topic row overlap')
        topic_rects.append(r)
    for key, r in cp['categories'].items():
        children = [k for k, row in expected.items() if row['canonical_parent_id'] is not None and
                    'category:' + str(row['canonical_parent_id']) == key]
        require(set(r['sibling_order']) == {k for k in children if k.startswith('category:')}, 'sibling inventory mismatch')
        require(set(r['topic_order']) == {k for k in children if k.startswith('topic:')}, 'topic order inventory mismatch')
        parent = expected[key]['canonical_parent_id']
        p = nodes.get('category:'+str(parent), {'x':0,'y':0})
        require(abs(r['slot_anchor']['x']-(nodes[key]['x']-p['x'])) < .000001 and
                abs(r['slot_anchor']['y']-(nodes[key]['y']-p['y'])) < .000001, 'category anchor mismatch')
        a = nodes[key]
        e = r['visible_extent']
        for child in children:
            n = nodes[child]
            require(n['x']-n['width']/2 >= a['x']+e['left']-.001 and
                    n['x']+n['width']/2 <= a['x']+e['left']+r['allocated_width']+.001 and
                    n['y']+n['height'] <= a['y']+r['allocated_height']+.001, 'node outside canonical region ' + child)
    segments = []
    for branch in geom['branches']:
        require(branch['parent'] in nodes and branch['child'] in nodes, 'invalid hierarchy endpoint')
        require('category:' + str(expected[branch['child']]['canonical_parent_id']) == branch['parent'], 'noncanonical hierarchy route')
    require({(e['parent'], e['child']) for e in geom['branches']} ==
            {('category:' + str(r['canonical_parent_id']), k) for k, r in expected.items()
             if k.startswith('category:') and r['canonical_parent_id'] is not None}, 'missing hierarchy connection')
    for route in geom['connectorSegments']:
        require(route['parent'] in nodes and all(k in nodes for k in route['children']), 'invalid route endpoint')
        for a, b in zip(route['points'], route['points'][1:]):
            require(a['x'] == b['x'] or a['y'] == b['y'], 'nonorthogonal hierarchy route')
            segments.append((route['parent'], a, b))
            for r in rects:
                if a['x'] == b['x']:
                    hit = r['x'] + .001 < a['x'] < r['x'] + r['w'] - .001 and max(a['y'], b['y']) > r['y'] + .001 and min(a['y'], b['y']) < r['y'] + r['h'] - .001
                else:
                    hit = r['y'] + .001 < a['y'] < r['y'] + r['h'] - .001 and max(a['x'], b['x']) > r['x'] + .001 and min(a['x'], b['x']) < r['x'] + r['w'] - .001
                require(not hit, 'hierarchy enters semantic box ' + r['key'])
    for i, (p, a, b) in enumerate(segments):
        for q, c, d in segments[i+1:]:
            if p == q: continue
            if a['x'] != b['x']: a, b, c, d = c, d, a, b
            if a['x'] == b['x'] and c['y'] == d['y']:
                hit = min(c['x'], d['x']) + .001 < a['x'] < max(c['x'], d['x']) - .001 and min(a['y'], b['y']) + .001 < c['y'] < max(a['y'], b['y']) - .001
                require(not hit, 'hierarchy crossing ' + p + ', ' + q)
    return {'semantic_overlaps': 0, 'hierarchy_crossings': 0, 'topics': len(topic_rects), 'categories': len(cp['categories'])}
