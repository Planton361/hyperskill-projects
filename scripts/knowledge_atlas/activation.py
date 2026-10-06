"""Pure activation planning: relevance is evidence, activation is presentation.

No layout allocator, filesystem writes, network access, or source mutation.
Catalog and accepted geometry remain separate inputs; candidates are not active.
"""
from collections import defaultdict
from copy import deepcopy
import math
from . import snapshot, validate


OUTCOMES = {
    'NO_CHANGE': 'SAFE_TO_APPLY',
    'ACTIVATION_REVIEW_REQUIRED': 'REVIEW_REQUIRED',
    'ACTIVATION_REBALANCE_REQUIRED': 'REBALANCE_REQUIRED',
    'METADATA_REQUIRED': None,
}


def order(key):
    kind, number = key.split(':')
    return kind, int(number)


class ActivationPlanner:
    def __init__(self, catalog, checkpoint, geometry):
        self.catalog = catalog
        canonical = checkpoint.get('spatial_authority') is not None
        if canonical:
            categories = {k for k in checkpoint['accepted_inventory'] if k.startswith('category:')}
            topics = set(checkpoint['accepted_inventory']) - categories
        else:
            validate.checkpoint(checkpoint)
            categories = set(checkpoint['categories'])
            topics = {k for r in checkpoint['categories'].values() for k in r['topic_order']}
        nodes = geometry['positions'] if canonical else geometry['nodes']
        keys = [n['key'] for n in nodes]
        if len(keys) != len(set(keys)) or set(keys) != categories | topics:
            raise ValueError('Accepted geometry/checkpoint inventory mismatch')
        for node in nodes:
            if canonical: node = {**node, 'width': node['w'], 'height': node['h']}
            if any(type(node.get(f)) not in (int, float) or not math.isfinite(node[f])
                   for f in ('x', 'y', 'width', 'height')) or node['width'] <= 0 or node['height'] <= 0:
                raise ValueError('Invalid accepted geometry bounds')
        self.active = categories | topics
        self.generation = checkpoint['presentation_generation']
        self.presentation = {'checkpoint_fingerprint': snapshot.ordered_digest(checkpoint),
                             'geometry_fingerprint': snapshot.ordered_digest(geometry),
                             'generation': self.generation,
                             'layout_schema_version': checkpoint['layout_schema_version'],
                             'layout_algorithm_version': checkpoint['layout_algorithm_version']}
        self.evidence = {r['id']: r for r in catalog.active['evidence']}
        # Identity, title and placement must be known even for accepted history.
        for key in sorted(self.active, key=order):
            if self.missing(key):
                raise ValueError('Accepted geometry lacks renderable catalog metadata: ' + key)

    def explicit(self, row):
        refs = sorted(set(row.get('evidence_ids', [])))
        if not refs or any(self.evidence.get(e, {}).get('confidence') != 'explicit' for e in refs):
            raise ValueError('Activation seeds require accepted explicit evidence')
        return refs

    def identity(self, numeric, kind='topic'):
        if type(numeric) is not int or numeric <= 0:
            raise ValueError('Activation identities require positive integer Hyperskill IDs')
        key = f'{kind}:{numeric}'
        if kind == 'topic' and key not in self.catalog.topics:
            if f'category:{numeric}' in self.catalog.categories:
                raise ValueError('Topic membership references an explicit Category')
            return f'reference:{numeric}'
        return key

    def paths(self, key):
        """Ordered root-to-parent paths, preserving every structural membership."""
        numeric = int(key.split(':')[1])
        def walk(node, seen):
            if node in seen:
                raise ValueError('Cycle in activation structural closure')
            if f'category:{node}' not in self.catalog.categories:
                raise ValueError('Missing structural Category in activation closure')
            parents = sorted(self.catalog.memberships.get(node, set()))
            if not parents:
                root = self.catalog.categories[f'category:{node}']
                if 'parent_id' not in root or root['parent_id'] is not None:
                    raise ValueError('Unplaced Category in activation closure')
                return [[f'category:{node}']]
            return [path + [f'category:{node}'] for p in parents
                    for path in walk(p, seen | {node})]
        return [path for parent in sorted(self.catalog.memberships.get(numeric, set()))
                for path in walk(parent, {numeric})]

    def missing(self, key):
        kind, numeric = key.split(':')
        row = self.catalog.categories.get(key) if kind == 'category' else self.catalog.topics.get(key)
        missing = []
        if row is not None and (type(row.get('id')) is not int or row['id'] != int(numeric)):
            raise ValueError('Catalog entity has inconsistent stable identity')
        if row is None:
            missing.append('category_entity_type' if kind == 'category' else 'topic_entity_type')
        if row is None or not isinstance(row.get('title'), str) or not row['title'].strip():
            missing.append('title')
        if kind != 'category' and not self.paths(key):
            missing.append('structural_membership')
        if kind == 'category' and row is not None:
            self.paths(key)  # validates non-root placement without demanding a root parent
            if ('parent_id' not in row or row['parent_id'] is not None) and not self.catalog.memberships.get(int(numeric)):
                missing.append('structural_membership')
        return missing

    def structural_sources(self, child, parent):
        child_id = int(child.split(':')[1])
        sources = []
        for h in self.catalog.fact_history.get(parent, []):
            if child_id in h['facts'].get('children', []):
                sources.append({'observation': h['observation'],
                                'source_ids': sorted(h['facts']['fact_sources'].get('children', []))})
        for edge in self.catalog.active['edges']:
            if edge['type'] == 'hierarchy' and edge['source'] == parent and edge['target'] == f"{'category' if child.startswith('category:') else 'topic'}:{child_id}":
                sources.append({'edge_id': edge['id'], 'evidence_ids': self.explicit(edge)})
        if not sources:
            raise ValueError('Structural membership lacks traceable evidence')
        return sorted(sources, key=lambda s: snapshot.encode(s))

    def plan(self, mode='MY_ATLAS', course_ids=None, project_ids=None, include_personal=None):
        if mode not in ('MY_ATLAS', 'CURRENT_COURSE', 'PROJECT_FOCUS'):
            raise ValueError('Unknown activation context')
        courses = {r['id']: r for r in self.catalog.active['courses']}
        projects = {r['id']: r for r in self.catalog.active['projects']}
        course_ids = sorted(set(courses if course_ids is None and mode == 'MY_ATLAS' else course_ids or []))
        project_ids = sorted(set(projects if project_ids is None and mode == 'MY_ATLAS' else project_ids or []))
        include_personal = mode == 'MY_ATLAS' if include_personal is None else include_personal
        if mode == 'CURRENT_COURSE' and (len(course_ids) != 1 or project_ids):
            raise ValueError('Current Course requires one course and no project context')
        if mode == 'PROJECT_FOCUS' and (course_ids or not project_ids):
            raise ValueError('Project Focus requires projects and no course context')
        if not set(course_ids) <= set(courses) or not set(project_ids) <= set(projects):
            raise ValueError('Unknown course/project; explicit accepted evidence required')
        reasons = defaultdict(list)
        def add(key, reason):
            if reason not in reasons[key]:
                reasons[key].append(reason)
        for i in course_ids:
            course = courses[i]
            refs = self.explicit(course)
            for field, kind in [('topic_ids', 'topic'), ('category_ids', 'category')]:
                for numeric in sorted(set(course[field])):
                    add(self.identity(numeric, kind), {'kind': 'COURSE', 'source': f'course:{i}',
                                                      'field': field, 'evidence_ids': refs})
        for edge in sorted(self.catalog.active['edges'], key=lambda e: e['id']):
            if edge['type'] != 'project_requires' or edge['source'] not in {f'project:{i}' for i in project_ids}:
                continue
            if not edge['target'].startswith('topic:'):
                raise ValueError('Project requirement must explicitly target a Topic ID')
            if edge.get('stage_id') is not None:
                stage = next((s for s in self.catalog.active['stages'] if s['id'] == edge['stage_id']), None)
                if stage is None or edge['source'] != f"project:{stage['project_id']}" or \
                   int(edge['target'].split(':')[1]) not in stage['required_topic_ids']:
                    raise ValueError('Project requirement disagrees with accepted Stage evidence')
            add(self.identity(int(edge['target'].split(':')[1])),
                {'kind': 'PROJECT', 'source': edge['source'], 'edge_id': edge['id'],
                 'stage_id': edge.get('stage_id'), 'evidence_ids': self.explicit(edge)})
        personal = defaultdict(list)
        for row in self.catalog.active['progress']['topics']:
            if any(row.get(field) is not None and type(row[field]) is not bool
                   for field in ('is_learned', 'is_verified')):
                raise ValueError('Personal learning/verification must be explicit booleans or null')
            key = self.identity(row['topic_id'])
            personal[key].append(row)
            if include_personal and (row.get('is_learned') is True or row.get('is_verified') is True):
                add(key, {'kind': 'PERSONAL', 'source': key, 'course_id': row.get('course_id'),
                          'observed_at': row.get('observed_at'), 'evidence_ids': self.explicit(row)})
        seeds = sorted(reasons, key=order)
        required_ancestors = set()
        # Preserve why closure exists, with provenance for each traversed pair.
        for seed in seeds:
            for path in self.paths(seed):
                child = seed
                for parent in reversed(path):
                    required_ancestors.add(parent)
                    add(parent, {'kind': 'STRUCTURAL_ANCESTOR', 'source': seed,
                                 'child': child, 'membership_sources': self.structural_sources(child, parent)})
                    child = parent
        scope = set(reasons)
        # History is not a fabricated relevance fact. It is accepted presentation.
        inventory = scope | self.active if mode == 'MY_ATLAS' else scope
        rows = []
        for key in sorted(inventory, key=order):
            numeric = int(key.split(':')[1])
            kind = key.split(':')[0]
            row = self.catalog.categories.get(key) if kind == 'category' else self.catalog.topics.get(key)
            missing = self.missing(key)
            paths = self.paths(key)
            own_path = paths or ([[]] if kind == 'category' and row and not missing else [])
            memberships = [f'category:{i}' for i in sorted(self.catalog.memberships.get(numeric, set()))]
            rs = sorted(reasons.get(key, []), key=lambda r: snapshot.encode(r))
            def explicit_state(field):
                values = [r[field] for r in personal.get(key, []) if r.get(field) is not None]
                return True if True in values else False if values and all(v is False for v in values) else None
            status = 'ALREADY_ACTIVE' if key in self.active else 'BLOCKED_ON_METADATA' if missing else 'ACTIVATION_CANDIDATE'
            placement = []
            for path in own_path:
                nearest = next((p for p in reversed(path) if p in self.active), None)
                full_path = path + [key] if kind == 'category' and key not in path else path
                placement.append({'ancestor_chain': path,
                                  'active_ancestors': [p for p in path if p in self.active],
                                  'dormant_ancestors': [p for p in path if p not in self.active],
                                  'nearest_active_ancestor': nearest,
                                  'required_new_category_chain': [p for p in path if p not in self.active],
                                  'root': full_path[0], 'major_branch': full_path[1] if len(full_path) > 1 else None})
            rows.append({'id': key, 'hyperskill_id': numeric, 'entity_type': kind if row else 'reference',
                         'title': row['title'] if row and 'title' not in missing else None,
                         'catalog_status': 'CATALOG_KNOWN' if row or numeric in self.catalog.references else 'UNKNOWN',
                         'resolution': 'CATEGORY' if kind == 'category' and row else
                                       row['resolution'] if row else 'UNRESOLVED_REFERENCE' if numeric in self.catalog.references else 'UNKNOWN',
                         'relevance': 'RELEVANT' if rs else 'DORMANT', 'activation_reasons': rs,
                         'presentation_history': 'ACTIVE_HISTORY' if key in self.active else None,
                         'course_reasons': sorted({r['source'] for r in rs if r['kind'] == 'COURSE'}),
                         'project_reasons': sorted({r['source'] for r in rs if r['kind'] == 'PROJECT'}),
                         'personal_relevant': any(r['kind'] == 'PERSONAL' for r in rs),
                         'personal_learning': explicit_state('is_learned'),
                         'personal_verification': explicit_state('is_verified'),
                         'verification_statuses': sorted({r['verification_status'] for r in personal.get(key, []) if r.get('verification_status') is not None}),
                         'personal_evidence': sorted({e for r in personal.get(key, []) for e in r.get('evidence_ids', [])}),
                         'renderability': 'BLOCKED_ON_METADATA' if missing else 'RENDERABLE',
                         'missing_metadata': missing, 'structural_memberships': memberships,
                         'canonical_parent': f"category:{row['accepted_metadata']['canonical_parent_id']}" if row and row.get('accepted_metadata', {}).get('canonical_parent_id') else
                                             f"category:{row['parent_id']}" if row and row.get('parent_id') else None,
                         'presentation_activation': status, 'placements': placement,
                         'outside_tracked_course_membership': kind != 'category' and not any(numeric in c['topic_ids'] for c in courses.values())})
        groups = {s: [r['id'] for r in rows if r['presentation_activation'] == s]
                  for s in ('ALREADY_ACTIVE', 'ACTIVATION_CANDIDATE', 'BLOCKED_ON_METADATA')}
        candidates = [r for r in rows if r['presentation_activation'] == 'ACTIVATION_CANDIDATE']
        roots = sorted({p['root'] for r in rows for p in r['placements']}, key=order)
        branches = sorted({p['major_branch'] for r in rows for p in r['placements'] if p['major_branch']}, key=order)
        new_roots = [r for r in roots if r not in self.active]
        conditions = []
        if groups['BLOCKED_ON_METADATA']: conditions.append('METADATA_REQUIRED')
        if new_roots: conditions.append('ACTIVATION_REBALANCE_REQUIRED')
        elif candidates: conditions.append('ACTIVATION_REVIEW_REQUIRED')
        if not conditions: conditions.append('NO_CHANGE')
        outcome = conditions[0]  # metadata > new root > same-root review > no change
        new_categories = [r['id'] for r in candidates if r['entity_type'] == 'category']
        new_topics = [r['id'] for r in candidates if r['entity_type'] == 'topic']
        routable, deferred = [], []
        for e in sorted(self.catalog.active['edges'], key=lambda e: e['id']):
            if e['type'] in ('prerequisite', 'dependent') and (e['source'] in scope or e['target'] in scope):
                (routable if {e['source'], e['target']} <= self.active else deferred).append(e['id'])
        return {'schema_version': 1, 'context': {'mode': mode, 'course_ids': course_ids,
                                                'project_ids': project_ids, 'include_personal': include_personal},
                'entities': rows, 'seed_entities': seeds, 'required_ancestors': sorted(required_ancestors, key=order),
                'already_active': groups['ALREADY_ACTIVE'], 'new_categories': new_categories, 'new_topics': new_topics,
                'blocked_references': [deepcopy(r) for r in rows if r['presentation_activation'] == 'BLOCKED_ON_METADATA'],
                'newly_activated': [], 'affected_roots': roots, 'new_roots': new_roots, 'affected_major_branches': branches,
                'geometry_required': bool(candidates), 'conditions': conditions, 'recommended_outcome': outcome,
                'pipeline_outcome': OUTCOMES[outcome], 'presentation_mutation_permitted': False,
                'planning_displacement': {'categories': 0, 'topics': 0},
                'future_displacement': None if candidates or groups['BLOCKED_ON_METADATA'] else 0,
                'estimated_content_size': {'new_categories': len(new_categories), 'new_topics': len(new_topics),
                                           'blocked_references': len(groups['BLOCKED_ON_METADATA'])},
                'accepted_presentation': deepcopy(self.presentation),
                'retained_active_history': sorted(self.active, key=order), 'removed_geometry': [],
                'catalog_inventory': {'categories': len(self.catalog.categories), 'described_topics': len(self.catalog.topics),
                                      'unresolved_references': len(self.catalog.references),
                                      'dormant_for_context': len((set(self.catalog.categories) | set(self.catalog.topics) |
                                                                {f'reference:{i}' for i in self.catalog.references}) - scope - self.active)},
                'relations': {'routable_existing': routable, 'deferred_until_both_endpoints_active': deferred,
                              'relation_seeds': []}}

    def get_entity_status(self, identifier, **context):
        """Query dormant entities without putting them in a presentation plan."""
        plan = self.plan(**context)
        for row in plan['entities']:
            if row['id'] == identifier:
                return row
        if identifier in self.active:
            history = self.plan(course_ids=[], project_ids=[], include_personal=False)
            return next(row for row in history['entities'] if row['id'] == identifier)
        kind, number = identifier.split(':')
        key = self.identity(int(number), kind) if kind != 'reference' else self.identity(int(number))
        if key != identifier:
            raise ValueError('Identity type disagrees with catalog resolution')
        known = key in self.catalog.categories or key in self.catalog.topics or int(number) in self.catalog.references
        personal = [r for r in self.catalog.active['progress']['topics'] if r['topic_id'] == int(number)] if kind != 'category' else []
        def explicit_state(field):
            values = [r[field] for r in personal if r.get(field) is not None]
            return True if True in values else False if values and all(v is False for v in values) else None
        return {'id': key, 'catalog_status': 'CATALOG_KNOWN' if known else 'UNKNOWN',
                'relevance': 'DORMANT', 'activation_reasons': [],
                'presentation_history': None,
                'course_reasons': [], 'project_reasons': [], 'personal_relevant': False,
                'personal_learning': explicit_state('is_learned'), 'personal_verification': explicit_state('is_verified'),
                'resolution': self.catalog.get_resolution_status(key),
                'structural_memberships': [f'category:{i}' for i in sorted(self.catalog.memberships.get(int(number), set()))],
                'renderability': 'BLOCKED_ON_METADATA' if self.missing(key) else 'RENDERABLE',
                'missing_metadata': self.missing(key), 'presentation_activation': 'DORMANT'}


def human(plan):
    active = plan['already_active']
    context = plan['context']
    label = f"Course {context['course_ids'][0]}" if context['mode'] == 'CURRENT_COURSE' else \
            'Projects ' + ', '.join(map(str, context['project_ids'])) if context['mode'] == 'PROJECT_FOCUS' else 'My Atlas'
    return '\n'.join(['Activation Plan', '---------------', f"Context: {label}",
                      f"Already active topics: {sum(k.startswith('topic:') for k in active)}",
                      f"Already active categories: {sum(k.startswith('category:') for k in active)}",
                      f"New renderable topics: {len(plan['new_topics'])}", f"New categories: {len(plan['new_categories'])}",
                      f"Blocked references: {len(plan['blocked_references'])}",
                      f"Geometry required: {'yes' if plan['geometry_required'] else 'no'}",
                      f"Outcome: {plan['recommended_outcome']}", f"Pipeline outcome: {plan['pipeline_outcome']}",
                      f"Generation: {plan['accepted_presentation']['generation']} (unchanged)",
                      'Planning only; no presentation mutation is permitted.'])
