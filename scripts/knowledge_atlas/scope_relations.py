"""Inert scope relations: exact IDs, typed source evidence, no active-table writes."""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from .catalog_observation import require, identifier, title, timestamp, security_guard
from .snapshot import encode

TYPE = 'scope_relations_catalog'
SHA = re.compile(r'^[a-f0-9]{64}$')


def keys(row, allowed):
    require(isinstance(row, dict) and set(row) == set(allowed.split()), 'Invalid scope observation fields')


def unique_ids(values):
    require(isinstance(values, list), 'Missing explicit ID array')
    for value in values:
        identifier(value)
    require(len(values) == len(set(values)), 'Duplicate semantic relation')
    return set(values)


def inventory(rows):
    require(isinstance(rows, list), 'Invalid entity inventory')
    result = {}
    for row in rows:
        identifier(row.get('id'))
        require(row['id'] not in result, 'Duplicate semantic entity')
        result[row['id']] = row
    return result


def validate_observation(o, global_catalog=None):
    keys(o, 'observation_type schema_version sanitizer_schema_version captured_at_start captured_at_end candidate semantic_contract source_pages courses projects stages course_membership_evidence')
    require(o['observation_type'] == TYPE and type(o['schema_version']) is int and o['schema_version'] == 1 and type(o['sanitizer_schema_version']) is int and o['sanitizer_schema_version'] == 1, 'Unsupported scope observation schema')
    security_guard(o)
    require(not re.search(r'/Users/|/Library/|file://|account_id|password\s*[=:]', json.dumps(o), re.I), 'Sensitive scope value rejected')
    start, end = timestamp(o['captured_at_start']), timestamp(o['captured_at_end'])
    require(start <= end, 'Invalid capture interval')
    keys(o['candidate'], 'inventory_sha256 manifest_sha256 global_catalog_sha256 knowledge_inventory_sha256')
    require(all(isinstance(v, str) and SHA.fullmatch(v) for v in o['candidate'].values()), 'Invalid candidate provenance digest')
    contract = o['semantic_contract']
    keys(contract, 'report_sha256 client_url client_sha256 client_verified_at explicitly_observed_projects project_field project_ui_label stage_field stage_all_field stage_all_classification')
    require(SHA.fullmatch(contract['report_sha256']) and SHA.fullmatch(contract['client_sha256']), 'Invalid semantic contract digest')
    url = urlsplit(contract['client_url'])
    require(url.scheme == 'https' and url.netloc == 'hs.azureedge.net' and url.path.startswith('/static/hyperskill.org/') and not url.query and not url.fragment, 'Invalid public client provenance')
    timestamp(contract['client_verified_at'])
    explicit_ui = unique_ids(contract['explicitly_observed_projects'])
    require(contract['project_field'] == contract['stage_field'] == 'stages[].prerequisites' and contract['project_ui_label'] == "What you'll learn" and contract['stage_all_field'] == 'stages[].all_prerequisites' and contract['stage_all_classification'] == 'E', 'Unsupported relation semantics')
    sources, groups = {}, defaultdict(list)
    for s in o['source_pages']:
        keys(s, 'id endpoint captured_at http_status sanitized_sha256 meta')
        require(s['id'] == 'source:' + hashlib.sha256(encode({k: v for k, v in s.items() if k != 'id'})).hexdigest(), 'Invalid source identity')
        require(s['id'] not in sources, 'Duplicate source page')
        require(s['http_status'] == 200 and SHA.fullmatch(s['sanitized_sha256']), 'Invalid source response provenance')
        require(start <= timestamp(s['captured_at']) <= end, 'Source timestamp outside capture')
        u = urlsplit(s['endpoint']); q = parse_qs(u.query, strict_parsing=True)
        allowed = {'/api/tracks': {'page_size', 'page'}, '/api/projects': {'page_size', 'page'}, '/api/topic-relations': {'track_id', 'page_size', 'page'}, '/api/stages': {'ids', 'page_size', 'page'}}
        require(not u.scheme and not u.netloc and not u.fragment and u.path in allowed and set(q) == allowed[u.path] and all(len(v) == 1 for v in q.values()), 'Unapproved source endpoint')
        require(q['page_size'] == ['100'] and q['page'][0].isdigit() and int(q['page'][0]) > 0, 'Invalid source pagination')
        if 'track_id' in q: identifier(int(q['track_id'][0]))
        if 'ids' in q: unique_ids([int(v) for v in q['ids'][0].split(',')])
        keys(s['meta'], 'page has_next has_previous')
        require(s['meta']['page'] == int(q['page'][0]) and all(type(s['meta'][k]) is bool for k in ('has_next', 'has_previous')), 'Invalid page metadata')
        group = (u.path, q.get('track_id', q.get('ids', ['']))[0])
        groups[group].append(s); sources[s['id']] = (s, u.path, q)
    for pages in groups.values():
        pages.sort(key=lambda s: s['meta']['page'])
        require([s['meta']['page'] for s in pages] == list(range(1, len(pages)+1)), 'Incomplete pagination')
        require(all(s['meta']['has_previous'] == (i > 0) and s['meta']['has_next'] == (i < len(pages)-1) for i,s in enumerate(pages)), 'Incomplete terminal page evidence')
    require(('/api/tracks', '') in groups and ('/api/projects', '') in groups, 'Missing entity catalog provenance')
    def source(key, family, entity=None):
        require(key in sources and sources[key][1] == family, 'Invalid entity source reference')
        q = sources[key][2]
        if family == '/api/topic-relations': require(int(q['track_id'][0]) == entity, 'Wrong Course source')
        if family == '/api/stages': require(str(entity) in q['ids'][0].split(','), 'Wrong Stage source')
    courses, projects, stages = (inventory(o[t]) for t in ('courses', 'projects', 'stages'))
    require(explicit_ui <= projects.keys(), 'Unknown UI-evidenced Project')
    evidence = defaultdict(dict)
    for row in o['course_membership_evidence']:
        keys(row, 'course_id category_id topic_ids source_id')
        identifier(row['course_id'])
        require(row['course_id'] in courses, 'Unknown Course relation owner')
        identifier(row['category_id']); unique_ids(row['topic_ids'])
        source(row['source_id'], '/api/topic-relations', row['course_id'])
        require(row['category_id'] not in evidence[row['course_id']], 'Duplicate Course Category evidence')
        evidence[row['course_id']][row['category_id']] = row
    for c in courses.values():
        keys(c, 'id title is_public is_beta topics_count source_id topic_ids category_ids membership_state membership_source_ids')
        title(c['title']); require(c['is_public'] is True and c['is_beta'] is False and type(c['topics_count']) is int and c['topics_count'] >= 0, 'Invalid normal Course metadata')
        source(c['source_id'], '/api/tracks')
        require(c['membership_state'] == 'KNOWN', 'Unestablished Course membership')
        tids, cids = unique_ids(c['topic_ids']), unique_ids(c['category_ids'])
        rows = evidence[c['id']]
        require(cids == rows.keys() and tids == {t for r in rows.values() for t in r['topic_ids']} and len(tids) == c['topics_count'], 'Course evidence does not establish complete membership')
        require(len(c['membership_source_ids']) == len(set(c['membership_source_ids'])) and set(c['membership_source_ids']) == {s['id'] for s in groups.get(('/api/topic-relations', str(c['id'])), [])}, 'Missing Course pagination evidence')
        require(bool(c['membership_source_ids']), 'Missing explicit Course membership response')
    declared = set()
    for p in projects.values():
        keys(p, 'id title is_public is_beta is_deprecated is_lti is_template_based source_id stage_ids stages_count project_requires_state topic_ids requirement_qualification project_prerequisites_state entry_prerequisite_ids n_first_prerequisites n_last_prerequisites')
        title(p['title']); source(p['source_id'], '/api/projects')
        require(p['is_public'] is True and p['is_beta'] is False and p['is_deprecated'] is False and p['is_lti'] is False and type(p['is_template_based']) is bool, 'Invalid normal Project metadata')
        ids = unique_ids(p['stage_ids']); require(p['stages_count'] == len(ids) and type(p['stages_count']) is int, 'Incomplete Project Stage inventory')
        require(not declared.intersection(ids), 'Stage belongs to multiple Projects'); declared.update(ids)
        require(all(sid in stages and stages[sid]['project_id'] == p['id'] for sid in ids), 'Invalid Project Stage link')
        require(p['project_prerequisites_state'] == 'UNKNOWN' and p['entry_prerequisite_ids'] is None, 'No evidenced entry prerequisite ID source')
        for field in ('n_first_prerequisites', 'n_last_prerequisites'):
            require(p[field] is None or type(p[field]) is int and p[field] >= 0, 'Invalid numeric prerequisite metadata')
        qualification = p['requirement_qualification']
        if p['project_requires_state'] == 'UNKNOWN':
            require(p['topic_ids'] is None and qualification is None and p['is_template_based'] and p['id'] not in explicit_ui, 'Invalid UNKNOWN Project scope')
        else:
            require(p['project_requires_state'] == 'KNOWN', 'Invalid Project relation state')
            expected = 'EXPLICIT_PROJECT_UI' if p['id'] in explicit_ui else 'VERSION_VERIFIED_STANDARD_NON_TEMPLATE_COMPONENT'
            require(qualification == expected and (p['id'] in explicit_ui or not p['is_template_based']), 'Unqualified Project study-plan derivation')
            require(unique_ids(p['topic_ids']) == {t for sid in ids for t in stages[sid]['prerequisites']}, 'Incomplete evidenced Project study plan')
        require(len({stages[sid]['order'] for sid in ids}) == len(ids), 'Conflicting Stage order')
    require(declared == stages.keys(), 'Unlinked Stage entity')
    for s in stages.values():
        keys(s, 'id title project_id order previous_stage_id is_deprecated source_id stage_requires_state prerequisites all_prerequisites all_prerequisites_state')
        title(s['title']); identifier(s['project_id']); source(s['source_id'], '/api/stages', s['id'])
        require(type(s['order']) is int and s['order'] > 0 and type(s['is_deprecated']) is bool, 'Invalid Stage identity metadata')
        if s['previous_stage_id'] is not None:
            require(s['previous_stage_id'] in stages and stages[s['previous_stage_id']]['project_id'] == s['project_id'], 'Invalid previous Stage link')
        require(s['stage_requires_state'] == s['all_prerequisites_state'] == 'KNOWN', 'Missing explicit Stage relation')
        unique_ids(s['prerequisites']); unique_ids(s['all_prerequisites'])
    if global_catalog is not None:
        topics = {int(k.split(':')[1]) for k in global_catalog.topics}
        categories = {int(k.split(':')[1]) for k in global_catalog.categories}
        require(all(set(c['topic_ids']) <= topics and set(c['category_ids']) <= categories for c in courses.values()), 'Unknown Global Course entity')
        require(all(set(s['prerequisites']) <= topics and set(s['all_prerequisites']) <= topics for s in stages.values()), 'Unknown Global Stage Topic')
    return o


class ScopeRelationCatalog:
    """Read-only indexed seeds; geometry never becomes a semantic fact."""
    def __init__(self, observation, identity, global_catalog):
        validate_observation(observation, global_catalog)
        self.observation, self.identity = observation, identity
        self.courses, self.projects, self.stages = (inventory(observation[t]) for t in ('courses', 'projects', 'stages'))
        self.course_project_associations = None

    def scope(self, kind, ident):
        require(kind in ('course', 'project', 'stage'), 'Unknown scope kind')
        table = {'course': self.courses, 'project': self.projects, 'stage': self.stages}[kind]
        require(ident in table, 'Unknown scope identity')
        r = table[ident]
        state = r[{'course':'membership_state','project':'project_requires_state','stage':'stage_requires_state'}[kind]]
        tids = r['prerequisites'] if kind == 'stage' else r['topic_ids']
        return {'scope_type': kind, 'scope_id': ident, 'title': r['title'], 'state': state,
                'explicit_topic_ids': None if tids is None else sorted(tids),
                'explicit_category_ids': sorted(r['category_ids']) if kind == 'course' else [],
                **({'project_id': r['project_id'], 'order': r['order']} if kind == 'stage' else {})}

    def base_index(self):
        return {'schema_version': 1, 'observation': self.identity,
                'observation_sha256': hashlib.sha256(encode(self.observation)).hexdigest(),
                **{name: [self.scope(kind, i) for i in sorted(table)] for name,kind,table in [('courses','course',self.courses),('projects','project',self.projects),('stages','stage',self.stages)]}}

    def index(self):
        result = self.base_index()
        if self.course_project_associations is not None:
            result['course_project_associations'] = self.course_project_associations
        return result

    def attach_course_projects(self, observation, identity, active_courses):
        from .course_project_associations import validate_observation
        validate_observation(observation, self, active_courses)
        self.course_project_associations = {
            'observation': identity,
            'observation_sha256': hashlib.sha256(encode(observation)).hexdigest(),
            'courses': observation['courses'],
            'sources': [{k: s[k] for k in ('id', 'course_id', 'endpoint', 'captured_at', 'sanitized_sha256')}
                        for s in observation['source_pages']],
        }


def write_immutable(folder, observation):
    from .observations import write_immutable_catalog
    return write_immutable_catalog(folder, observation, 'scope-relations')



def verify_candidate(folder, expected_digest):
    """Offline inventory verification and credential scan of every constituent."""
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    if 'inventory' in manifest:
        keys(manifest, 'schema_version digest_kind inventory_digest inventory')
        require(manifest['schema_version'] == 1 and manifest['digest_kind'] == 'SHA256_CANONICAL_MANIFEST_INVENTORY', 'Invalid inventory contract')
        digest = hashlib.sha256(encode(manifest['inventory'])).hexdigest()
        require(digest == manifest['inventory_digest'] == expected_digest, 'Candidate inventory integrity failed')
        files = []
        for r in manifest['inventory']:
            keys(r, 'path sha256 bytes')
            files.append({'file': r['path'], 'sha256': r['sha256'], 'bytes': r['bytes']})
    else:
        files = manifest['files']
        digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        require(digest == manifest['bundle_sha256'] == expected_digest, 'Candidate inventory integrity failed')
    require(len({r['file'] for r in files}) == len(files) and
            {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()} == {r['file'] for r in files} | {'manifest.json'}, 'Unexpected candidate constituent')
    forbidden = re.compile(r'^(?:cookies?|authorization|csrf(?:_token)?|bearer|password|access_token|refresh_token|sessionid|user_id|account_id|email|headers|raw_headers|browser_storage|local_storage)$', re.I)
    secret = re.compile(r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|/Users/|/home/|file://|Bearer\s+[A-Za-z0-9._-]{12,}', re.I)
    def scan(v):
        if isinstance(v, dict):
            for k,x in v.items(): require(not forbidden.fullmatch(k), 'Sensitive candidate field'); scan(x)
        elif isinstance(v, list):
            for x in v: scan(x)
        elif isinstance(v, str) and v.startswith(('/api/', 'https://hyperskill.org/api/')):
            require(set(parse_qs(urlsplit(v).query)) <= {'page', 'page_size', 'ids', 'track_id', 'project'}, 'Sensitive candidate query')
    for r in files + [{'file': 'manifest.json'}]:
        name = r['file']
        require(isinstance(name, str) and not Path(name).is_absolute() and
                all(part not in ('', '.', '..') for part in name.split('/')) and '\\' not in name, 'Invalid candidate constituent path')
        p = folder / name; require(p.is_file() and not p.is_symlink(), 'Invalid candidate constituent')
        require(not any(folder.joinpath(*Path(name).parts[:i]).is_symlink() for i in range(len(Path(name).parts))), 'Candidate symlink rejected')
        body = p.read_bytes()
        if 'sha256' in r: require(len(body) == r['bytes'] and hashlib.sha256(body).hexdigest() == r['sha256'], 'Candidate constituent integrity failed')
        require(not secret.search(body.decode()), 'Sensitive candidate value')
        if p.suffix == '.json': scan(json.loads(body))
    require(json.loads((folder / 'security_audit.json').read_bytes())['status'] == 'PASS', 'Candidate security audit failed')
    return manifest


def observation_from_candidate(folder, expected_digest, global_catalog):
    """Allowlisted conversion; raw browser material is never an ingestion input."""
    folder = Path(folder); manifest = verify_candidate(folder, expected_digest)
    read = lambda name: json.loads((folder / (name + '.json')).read_bytes())
    metadata, states, requests = read('acquisition_metadata'), read('relation_states'), read('request_provenance')['requests']
    sources, native = {}, {}
    for r in sorted(requests, key=lambda r: r['endpoint']):
        require(r['state'] == 'SUCCESS' and r['http_result'] == 200, 'Incomplete source request')
        path = folder.parent / 'sanitized' / (hashlib.sha256(r['endpoint'].encode()).hexdigest() + '.json')
        require(path.is_file() and not path.is_symlink(), 'Missing sanitized provenance page')
        body = path.read_bytes(); require(hashlib.sha256(body).hexdigest() == r['sanitized_digest'], 'Sanitized source integrity failed')
        capture = json.loads(body)
        require(capture['endpoint'] == r['endpoint'] and capture['status'] == 200 and capture['state'] == 'SUCCESS', 'Wrong sanitized source page')
        s = {'endpoint': r['endpoint'], 'captured_at': r['timestamp'], 'http_status': 200,
             'sanitized_sha256': r['sanitized_digest'], 'meta': {k: capture['meta'][k] for k in ('page','has_next','has_previous')}}
        s['id'] = 'source:' + hashlib.sha256(encode(s)).hexdigest()
        sources[r['endpoint']] = s; native[r['endpoint']] = {v['id']: v for v in capture['rows']}
    source_id = lambda endpoint: sources[endpoint]['id']
    contract = metadata['client_contract']
    o = {'observation_type': TYPE, 'schema_version': 1, 'sanitizer_schema_version': 1,
         'captured_at_start': min(r['timestamp'] for r in requests), 'captured_at_end': max(r['timestamp'] for r in requests),
         'candidate': {'inventory_sha256': expected_digest, 'manifest_sha256': hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                       'global_catalog_sha256': metadata['source_global_catalog_sha256'], 'knowledge_inventory_sha256': metadata['source_knowledge_inventory_sha256']},
         'semantic_contract': {'report_sha256': metadata['semantic_contract_report_sha256'], 'client_url': contract['url'], 'client_sha256': contract['sha256'],
                               'client_verified_at': contract['verified_at'], 'explicitly_observed_projects': metadata['project_contract_qualification']['explicitly_observed_projects'],
                               'project_field': 'stages[].prerequisites', 'project_ui_label': "What you'll learn", 'stage_field': 'stages[].prerequisites',
                               'stage_all_field': 'stages[].all_prerequisites', 'stage_all_classification': 'E'},
         'source_pages': list(sources.values()), 'courses': [], 'projects': [], 'stages': [], 'course_membership_evidence': []}
    course_states = {r['course_id']: r for r in states['courses']}
    project_states = {r['project_id']: r for r in states['projects']}
    stage_states = {r['stage_id']: r for r in states['stages']}
    relation_maps = {}
    for family, owner, member in [('course_topic_memberships','course_id','topic_id'),('course_category_memberships','course_id','category_id'),('project_requires','project_id','topic_id'),('stage_requires','stage_id','topic_id')]:
        relation_maps[family] = defaultdict(set)
        for r in read(family):
            require(r[member] not in relation_maps[family][r[owner]], 'Duplicate candidate relation')
            relation_maps[family][r[owner]].add(r[member])
    require(read('project_prerequisites') == [], 'Unexpected entry prerequisite evidence')
    for c in read('courses'):
        endpoint = c['provenance']['endpoint']; original = native[endpoint][c['id']]
        fields = 'id title is_public is_beta topics_count'.split()
        require(all(c[k] == original[k] for k in fields), 'Course metadata provenance mismatch')
        state = course_states[c['id']]
        o['courses'].append({**{k: c[k] for k in fields}, 'source_id': source_id(endpoint),
                             'topic_ids': sorted(relation_maps['course_topic_memberships'][c['id']]),
                             'category_ids': sorted(relation_maps['course_category_memberships'][c['id']]),
                             'membership_state': state['topic_membership_state'], 'membership_source_ids': sorted(source_id(e) for e in state['provenance']['endpoints'])})
        require(state['category_membership_state'] == 'KNOWN', 'Unknown Course Category membership')
        for e in state['provenance']['endpoints']:
            for row in native[e].values():
                o['course_membership_evidence'].append({'course_id': c['id'], 'category_id': row['id'], 'topic_ids': sorted({identifier(v) for v in row['descendants']}), 'source_id': source_id(e)})
    for s in read('stages'):
        endpoint = s['provenance']['endpoint']; row = native[endpoint][s['id']]
        fields = 'id title project_id order previous_stage_id is_deprecated'.split()
        require(all(s[k] == row['project' if k == 'project_id' else k] for k in fields), 'Stage identity provenance mismatch')
        require(set(row['prerequisites']) == relation_maps['stage_requires'][s['id']], 'Stage relation provenance mismatch')
        require(stage_states[s['id']]['stage_requires_state'] == 'KNOWN', 'Unknown Stage source')
        o['stages'].append({**{k: s[k] for k in fields}, 'source_id': source_id(endpoint), 'stage_requires_state': 'KNOWN',
                            'prerequisites': list(dict.fromkeys(identifier(v) for v in row['prerequisites'])), 'all_prerequisites': list(dict.fromkeys(identifier(v) for v in row['all_prerequisites'])), 'all_prerequisites_state': 'KNOWN'})
    for p in read('projects'):
        endpoint = p['provenance']['endpoint']; row = native[endpoint][p['id']]; state = project_states[p['id']]
        fields = 'id title is_public is_beta is_deprecated is_lti is_template_based stages_count'.split()
        require(all(p[k] == row[k] for k in fields) and p['stages_ids'] == row['stages_ids'], 'Project metadata provenance mismatch')
        known = state['project_requires_state'] == 'KNOWN'
        require(state['project_prerequisites_state'] == 'UNKNOWN', 'Unsupported entry prerequisite relation')
        qualification = ('EXPLICIT_PROJECT_UI' if p['id'] in o['semantic_contract']['explicitly_observed_projects'] else 'VERSION_VERIFIED_STANDARD_NON_TEMPLATE_COMPONENT') if known else None
        o['projects'].append({**{k: p[k] for k in fields}, 'source_id': source_id(endpoint), 'stage_ids': list(p['stages_ids']),
                              'project_requires_state': state['project_requires_state'], 'topic_ids': sorted(relation_maps['project_requires'][p['id']]) if known else None,
                              'requirement_qualification': qualification, 'project_prerequisites_state': 'UNKNOWN', 'entry_prerequisite_ids': None,
                              'n_first_prerequisites': row['n_first_prerequisites'], 'n_last_prerequisites': row['n_last_prerequisites']})
        require(known or not relation_maps['project_requires'][p['id']], 'UNKNOWN Project has fabricated requirements')
        if known:
            prov = state['project_requires_provenance']
            require(prov['client_contract_sha256'] == contract['sha256'] and prov['semantic_report_sha256'] == metadata['semantic_contract_report_sha256'] and set(prov['stage_ids']) == set(p['stages_ids']), 'Missing Project derivation evidence')
    validate_observation(o, global_catalog)
    return o
