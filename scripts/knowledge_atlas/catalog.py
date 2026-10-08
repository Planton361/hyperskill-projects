"""One composed catalog, pure-data projections, no presentation allocations.

Global facts live in typed observations. Accepted normalized entities are joined
by stable identity, never copied into a second maintained global entity table.
"""
from copy import deepcopy
from .catalog_observation import validate_observation, resolution, require
from .snapshot import TABLES, digest


def active_projection(data):
    """Explicit compatibility boundary: only accepted active tables reach V6.

    Global ingestion is not permission to activate new nodes. Existing trusted
    active data continues to be governed by the established migration gates.
    """
    return {k: data[k] for k in (*TABLES, 'observations') if k in data}


class Catalog:
    def __init__(self, data, allow_metadata_updates=False):
        self.active = active_projection(data)
        self.categories, self.topics, self.references = {}, {}, {}
        self.reference_history, self.memberships = {}, {}
        self.observation_ids = []
        self.global_relations = {'prerequisite_records': [], 'follower_records': []}
        self.fact_history = {}
        self.provenance = {}
        self.snapshot_positions = {'categories': {f"category:{r['id']}" for r in data['categories']},
                                   'leaves': {r['id'] for r in data['topics']}}
        self.latest_hierarchy = set()
        observations = sorted(((name, row) for name, row in data.get('catalog_observations', {}).items()
                               if row['observation_type'] == 'global_knowledge_catalog'),
                              key=lambda item: (item[1]['captured_at_end'], item[0]))
        for name, observation in observations:
            validate_observation(observation)
            self.snapshot_positions = {'categories': {f"category:{r['id']}" for r in observation['categories']},
                                       'leaves': {r['id'] for r in observation['topics'] + observation['unresolved_references']}}
            self.latest_hierarchy = {(r['parent_id'], r['child_id']) for r in observation['hierarchy_records']}
            self.observation_ids.append(name)
            for src in observation['source_pages']:
                self.provenance.setdefault(src['id'], []).append({'observation': name, 'source': src})
            for rows, target, kind in [('categories', self.categories, 'category'), ('topics', self.topics, 'topic')]:
                for row in observation[rows]:
                    key = f"{kind}:{row['id']}"
                    self.fact_history.setdefault(key, []).append({'observation': name, 'facts': deepcopy(row)})
                    # Merge explicit fields only; absence never retracts earlier facts.
                    old = target.get(key, {})
                    merged = {**old, **deepcopy(row)}
                    merged['fact_sources'] = {**old.get('fact_sources', {}), **deepcopy(row['fact_sources'])}
                    if kind == 'topic':
                        merged['resolution'] = resolution(merged)
                    target[key] = merged
            # Membership changes belong to the newest complete structural capture.
            latest_memberships = {}
            for row in observation['hierarchy_records']:
                latest_memberships.setdefault(row['child_id'], set()).add(row['parent_id'])
            for row in observation['categories']:
                if row['parent_id'] is None:
                    latest_memberships[row['id']] = set()
            # Missing nodes are retained for review; absence is not deletion.
            self.memberships.update(latest_memberships)
            for row in observation['unresolved_references']:
                self.reference_history.setdefault(row['id'], []).append({'observation': name, 'facts': deepcopy(row)})
                if f"topic:{row['id']}" not in self.topics:
                    self.references[row['id']] = deepcopy(row)
            for key in self.global_relations:
                self.global_relations[key].extend({'observation': name, **deepcopy(r)} for r in observation[key])
        # Accepted active metadata is joined under exactly the same global keys.
        # Capture resolution describes captured facts, not richness of legacy data.
        for table, target, kind in [('categories', self.categories, 'category'), ('topics', self.topics, 'topic')]:
            for row in data[table]:
                key = f"{kind}:{row['id']}"
                if key in target:
                    require(allow_metadata_updates or target[key]['title'] == row['title'], 'Global/active title conflict requires review')
                    parent = row['canonical_parent_id']
                    require(parent is None or parent in self.memberships.get(row['id'], set()), 'Global/active structural conflict requires review')
                else:
                    target[key] = {'id': row['id'], 'title': row['title'], 'parent_id': row['canonical_parent_id'],
                                   **({'resolution': 'RESOLVED_TOPIC'} if kind == 'topic' else {})}
                target[key]['accepted_metadata'] = deepcopy(row)
                if allow_metadata_updates: target[key]['title'] = row['title']
                for evidence in row.get('evidence_ids', []):
                    self.provenance.setdefault(evidence, []).append({'accepted_evidence': evidence})
        for edge in data['edges']:
            if edge['type'] == 'hierarchy':
                self.memberships.setdefault(int(edge['target'].split(':')[1]), set()).add(int(edge['source'].split(':')[1]))
                if not observations:
                    self.latest_hierarchy.add((int(edge['source'].split(':')[1]), int(edge['target'].split(':')[1])))
        for key in self.topics:
            self.references.pop(int(key.split(':')[1]), None)

        # Separate inert relation index; accepted active course/project APIs stay unchanged.
        from .scope_relations import ScopeRelationCatalog
        relations = [(name, row) for name, row in data.get('catalog_observations', {}).items()
                     if row['observation_type'] == 'scope_relations_catalog']
        require(len(relations) <= 1, 'Conflicting immutable scope catalogs')
        self.scope_relations = ScopeRelationCatalog(relations[0][1], relations[0][0], self) if relations else None
        associations = [(name, row) for name, row in data.get('catalog_observations', {}).items()
                        if row['observation_type'] == 'course_project_associations_catalog']
        require(len(associations) <= 1, 'Conflicting immutable Course association catalogs')
        if associations:
            require(self.scope_relations is not None, 'Course associations require the existing scope catalog')
            self.scope_relations.attach_course_projects(associations[0][1], associations[0][0], data['courses'])

    def get_scope_projection(self, scope_type, scope_id):
        require(self.scope_relations is not None, 'Scope relations not established')
        return self.scope_relations.scope(scope_type, scope_id)

    def get_resolution_status(self, identifier):
        numeric = int(str(identifier).split(':')[-1])
        if f'category:{numeric}' in self.categories:
            return 'CATEGORY'
        if f'topic:{numeric}' in self.topics:
            return self.topics[f'topic:{numeric}']['resolution']
        return 'UNRESOLVED_REFERENCE' if numeric in self.references else 'UNKNOWN'

    def get_catalog_ancestors(self, identifier):
        numeric = int(str(identifier).split(':')[-1])
        found, pending = set(), list(self.memberships.get(numeric, set()))
        while pending:
            node = pending.pop()
            if node in found:
                continue
            found.add(node)
            pending.extend(self.memberships.get(node, set()))
        return [f'category:{i}' for i in sorted(found)]

    def _projection(self, topic_ids, category_ids=(), project_ids=(), course_ids=()):
        topics, categories = set(topic_ids), set(category_ids)
        unknown = sorted(i for i in topics if self.get_resolution_status(i) == 'UNKNOWN')
        for i in topics | categories:
            categories.update(int(k.split(':')[1]) for k in self.get_catalog_ancestors(i))
        nodes = topics | categories
        return {'course_ids': sorted(set(course_ids)), 'project_ids': sorted(set(project_ids)),
                'categories': [deepcopy(self.categories[f'category:{i}']) for i in sorted(categories) if f'category:{i}' in self.categories],
                'topics': [deepcopy(self.topics[f'topic:{i}']) for i in sorted(topics) if f'topic:{i}' in self.topics],
                'unresolved_references': [deepcopy(self.references[i]) for i in sorted(topics) if i in self.references],
                'unknown_candidates': unknown,
                'hierarchy_records': [{'parent_id': p, 'child_id': i} for i in sorted(nodes)
                                      for p in sorted(self.memberships.get(i, set())) if p in categories],
                'accepted_edges': [deepcopy(e) for e in self.active['edges'] if
                                   (e['type'] in ('prerequisite', 'dependent') and int(e['source'].split(':')[1]) in topics and int(e['target'].split(':')[1]) in topics)
                                   or (e['type'] == 'project_requires' and int(e['source'].split(':')[1]) in project_ids and int(e['target'].split(':')[1]) in topics)],
                'progress': {table: [deepcopy(r) for r in self.active['progress'][table]
                                    if (table == 'topics' and r['topic_id'] in topics) or
                                       (table == 'projects' and r['project_id'] in project_ids) or
                                       (table == 'courses' and r['course_id'] in course_ids)]
                             for table in ('courses', 'topics', 'projects')}}

    def get_course_projection(self, course_id):
        return self.get_tracked_courses_projection([course_id])

    def get_projection(self, mode, course_ids=None, project_id=None):
        """Future view scopes as data queries only, with no visibility persistence."""
        if mode == 'GLOBAL_CATALOG':
            return self._projection({int(k.split(':')[1]) for k in self.topics} | set(self.references),
                                    {int(k.split(':')[1]) for k in self.categories})
        if mode == 'PROJECT_CONTEXT':
            return self.get_project_context(project_id)
        if mode in ('COURSE', 'TRACKED_COURSES', 'PERSONAL'):
            selected = [r['id'] for r in self.active['courses']] if course_ids is None else course_ids
            require(mode != 'COURSE' or len(selected) == 1, 'Course scope requires exactly one course')
            return self.get_tracked_courses_projection(selected)
        raise ValueError('Unknown projection mode')

    def get_tracked_courses_projection(self, course_ids):
        selected = [r for r in self.active['courses'] if r['id'] in course_ids]
        require({r['id'] for r in selected} == set(course_ids), 'Unknown course; explicit membership required')
        return self._projection({i for r in selected for i in r['topic_ids']},
                                {i for r in selected for i in r['category_ids']},
                                {i for r in selected for i in r['project_ids']}, course_ids)

    def get_project_context(self, project_id):
        require(any(p['id'] == project_id for p in self.active['projects']), 'Unknown project')
        # A project-filtered map or study plan is deliberately not a seed source.
        topics = {int(e['target'].split(':')[1]) for e in self.active['edges']
                  if e['type'] == 'project_requires' and e['source'] == f'project:{project_id}'}
        return self._projection(topics, project_ids=[project_id])

    def get_relevance(self, identifier, context=None):
        context = context or {'course_ids': [r['id'] for r in self.active['courses']]}
        numeric = int(str(identifier).split(':')[-1])
        course_scope = self.get_tracked_courses_projection(context.get('course_ids', []))
        course_nodes = {r['id'] for table in ('categories', 'topics', 'unresolved_references') for r in course_scope[table]}
        project_nodes = set()
        for project_id in context.get('project_ids', []):
            p = self.get_project_context(project_id)
            project_nodes.update(r['id'] for table in ('categories', 'topics', 'unresolved_references') for r in p[table])
        states = [r for r in self.active['progress']['topics'] if r['topic_id'] == numeric and
                  (not context.get('course_ids') or r['course_id'] in context['course_ids'])]
        def explicit(field):
            values = [r.get(field) for r in states if r.get(field) is not None]
            return True if True in values else (False if values and all(v is False for v in values) else None)
        known = self.get_resolution_status(numeric) != 'UNKNOWN'
        return {'catalog_known': known, 'course_relevant': numeric in course_nodes,
                'project_relevant': numeric in project_nodes, 'learned': explicit('is_learned'),
                'verified': explicit('is_verified'),
                'dormant': known and numeric not in course_nodes and numeric not in project_nodes}

    def promote_reference(self, identifier, observation, observation_id=None):
        """Pure promotion; original catalog and observation history remain intact."""
        require(identifier in self.references, 'Promotion requires an existing structural reference')
        validate_observation(observation)
        matches = [r for r in observation['topics'] if r['id'] == identifier]
        require(len(matches) == 1, 'Promotion requires explicit sanitized Topic evidence')
        record = deepcopy(matches[0])
        require(record.get('parent_id') is None or record['parent_id'] in self.memberships[identifier], 'Promotion canonical parent conflict')
        promoted = deepcopy(self)
        name = observation_id or ('sanitized-observation:' + digest(observation))
        for src in observation['source_pages']:
            promoted.provenance.setdefault(src['id'], []).append({'observation': name, 'source': deepcopy(src)})
        promoted.references.pop(identifier)
        promoted.topics[f'topic:{identifier}'] = record
        promoted.fact_history.setdefault(f'topic:{identifier}', []).append({'observation': name, 'facts': record})
        for field in promoted.global_relations:
            for row in observation[field]:
                owner = row['target_id'] if field == 'prerequisite_records' else row['source_id']
                if owner == identifier:
                    promoted.global_relations[field].append({'observation': name, **deepcopy(row)})
        return promoted


def compare_catalogs(before, after):
    """Absence is a review candidate, never an automatic deletion instruction."""
    types, details = set(), {}
    for field, new_type, missing_type in [('categories', 'GLOBAL_NEW_CATEGORY', 'GLOBAL_MISSING_CATEGORY_CANDIDATE'),
                                         ('topics', 'GLOBAL_NEW_TOPIC', 'GLOBAL_MISSING_TOPIC_CANDIDATE'),
                                         ('references', 'GLOBAL_NEW_REFERENCE', 'GLOBAL_MISSING_REFERENCE_CANDIDATE')]:
        old, new = getattr(before, field), getattr(after, field)
        added, missing = set(new) - set(old), set(old) - set(new)
        if field == 'categories':
            missing |= set(old) - after.snapshot_positions['categories']
        elif field == 'topics':
            missing |= {key for key in old if int(key.split(':')[1]) not in after.snapshot_positions['leaves']}
        else:
            missing |= set(old) - after.snapshot_positions['leaves']
        if field == 'topics':
            promoted = {k for k in added if int(k.split(':')[1]) in before.references}
            if promoted:
                types.add('REFERENCE_RESOLVED')
            added -= promoted
            details['resolved_references'] = sorted(promoted)
        if field == 'references':
            missing = {i for i in missing if f'topic:{i}' not in after.topics}
        details[field] = {'added': sorted(added), 'missing_candidates': sorted(missing)}
        if added: types.add(new_type)
        if missing: types.add(missing_type)
        for key in set(old) & set(new):
            def metadata(row):
                return {k: v for k, v in row.items() if k not in ('accepted_metadata', 'fact_sources', 'source_ids', 'parent_ids')}
            if digest(metadata(old[key])) != digest(metadata(new[key])):
                types.add('GLOBAL_METADATA_CHANGE')
            if 'parent_id' in old[key] and 'parent_id' in new[key] and old[key]['parent_id'] != new[key]['parent_id']:
                types.add('GLOBAL_REPARENT')
            if field == 'topics' and any(k in old[key] and k in new[key] and old[key][k] != new[key][k]
                                         for k in ('prerequisites', 'explicit_prerequisites', 'followers')):
                types.add('GLOBAL_RELATION_CHANGE')
    if before.memberships != after.memberships or before.latest_hierarchy != after.latest_hierarchy:
        types.add('GLOBAL_RELATION_CHANGE')
    def relation_pairs(catalog):
        return {k: sorted({(r['source_id'], r['target_id']) for r in rows}) for k, rows in catalog.global_relations.items()}
    if digest(relation_pairs(before)) != digest(relation_pairs(after)):
        types.add('GLOBAL_RELATION_CHANGE')
    active_changed = digest(before.active) != digest(after.active)
    if types and not active_changed:
        types.add('GLOBAL_CATALOG_ONLY')
    return {'change_types': sorted(types) or ['NO_CHANGE'], 'active_projection_changed': active_changed, **details}


def summary(data):
    catalogs = data.get('catalog_observations', {})
    if not catalogs:
        return {'observation_count': 0, 'change_types': ['NO_CHANGE'], 'active_projection_changed': False}
    catalog = Catalog(data)
    legacy = Catalog(active_projection(data))
    changes = compare_catalogs(legacy, catalog)
    return {'change_types': changes['change_types'], 'active_projection_changed': changes['active_projection_changed'],
            'global_additions': {k: len(changes[k]['added']) for k in ('categories', 'topics', 'references')},
            'comparison_basis': 'accepted active catalog; global history is separate',
            'observation_count': len(catalogs), 'categories': len(catalog.categories), 'described_topics': len(catalog.topics),
            'unresolved_references': len(catalog.references), 'geometry_activation': False}
