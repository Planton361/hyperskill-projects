"""Reviewed Track.projects associations joined to the one dormant scope catalog."""
import hashlib
import json
import re
from pathlib import Path

from .catalog_observation import require, identifier, timestamp, security_guard
from .scope_relations import keys, unique_ids, SHA, verify_candidate
from .snapshot import encode

TYPE = 'course_project_associations_catalog'
CONTRACT = {'endpoint_family': '/api/tracks/<id>', 'object_type': 'Track',
            'response_field': 'tracks[].projects',
            'completeness': 'COMPLETE_SERIALIZED_FIELD_TERMINAL_SINGLE_TRACK'}


def validate_observation(o, scopes=None, active_courses=()):
    keys(o, 'observation_type schema_version sanitizer_schema_version captured_at_start captured_at_end candidate scope_catalog semantic_contract source_pages courses')
    require(o['observation_type'] == TYPE and type(o['schema_version']) is int and o['schema_version'] == 1 and type(o['sanitizer_schema_version']) is int and o['sanitizer_schema_version'] == 1, 'Unsupported association schema')
    security_guard(o)
    require(not re.search(r'/Users/|/Library/|file://|account_id|password\s*[=:]', json.dumps(o), re.I), 'Sensitive association value')
    start, end = timestamp(o['captured_at_start']), timestamp(o['captured_at_end'])
    require(start <= end, 'Invalid association capture interval')
    keys(o['candidate'], 'inventory_sha256 manifest_sha256 global_catalog_sha256 scope_index_sha256')
    require(all(isinstance(v, str) and SHA.fullmatch(v) for v in o['candidate'].values()), 'Invalid association candidate digest')
    keys(o['scope_catalog'], 'observation sha256')
    require(isinstance(o['scope_catalog']['observation'], str) and re.fullmatch(r'observations/scope-relations-[0-9-]+-[a-f0-9]{12}\.json', o['scope_catalog']['observation']) and isinstance(o['scope_catalog']['sha256'], str) and SHA.fullmatch(o['scope_catalog']['sha256']), 'Invalid scope catalog provenance')
    require(o['semantic_contract'] == CONTRACT, 'Unsupported Course Project semantics')
    require(isinstance(o['source_pages'], list) and isinstance(o['courses'], list), 'Invalid association inventory')
    sources = {}
    for s in o['source_pages']:
        keys(s, 'id course_id endpoint captured_at http_status sanitized_sha256 meta project_ids')
        identifier(s['course_id'])
        require(s['id'] == 'source:' + hashlib.sha256(encode({k: v for k, v in s.items() if k != 'id'})).hexdigest(), 'Invalid association source identity')
        require(s['id'] not in sources, 'Duplicate association source')
        require(s['endpoint'] == '/api/tracks/' + str(s['course_id']), 'Wrong Course source endpoint')
        require(type(s['http_status']) is int and s['http_status'] == 200 and isinstance(s['sanitized_sha256'], str) and SHA.fullmatch(s['sanitized_sha256']), 'Invalid association source response')
        require(start <= timestamp(s['captured_at']) <= end, 'Association timestamp outside capture')
        keys(s['meta'], 'page has_next has_previous')
        require(type(s['meta']['page']) is int and s['meta']['page'] == 1 and s['meta']['has_next'] is False and s['meta']['has_previous'] is False, 'Incomplete Course association source')
        unique_ids(s['project_ids'])
        sources[s['id']] = s
    owners = {}
    for row in o['courses']:
        keys(row, 'course_id state project_ids complete source_id')
        cid = identifier(row['course_id'])
        require(cid not in owners, 'Duplicate Course association inventory')
        ids = unique_ids(row['project_ids'])
        require(row['project_ids'] == sorted(ids), 'Noncanonical association ID order')
        require(row['complete'] is True and row['state'] == ('KNOWN' if ids else 'KNOWN_EMPTY'), 'UNKNOWN is not a complete association inventory')
        require(row['source_id'] in sources, 'Missing Course association provenance')
        source = sources[row['source_id']]
        require(source['course_id'] == cid and ids == set(source['project_ids']), 'Course association source mismatch')
        owners[cid] = row
    require(owners and len(owners) == len(sources) and {r['source_id'] for r in owners.values()} == sources.keys(), 'Incomplete association provenance coverage')
    if scopes is not None:
        require(o['scope_catalog'] == {'observation': scopes.identity, 'sha256': hashlib.sha256(encode(scopes.observation)).hexdigest()}, 'Scope catalog identity changed')
        require(o['candidate']['global_catalog_sha256'] == scopes.observation['candidate']['global_catalog_sha256'], 'Reviewed Global Catalog provenance changed')
        require(hashlib.sha256(encode(scopes.base_index())).hexdigest() == o['candidate']['scope_index_sha256'], 'Reviewed scope seed inventory changed')
        require(owners.keys() == scopes.courses.keys(), 'Incomplete Course association coverage')
        require(all(set(row['project_ids']) <= scopes.projects.keys() for row in owners.values()), 'Unknown catalog Project association')
        for course in active_courses:
            if 'project_ids' in course:
                require(course['id'] in owners and set(course['project_ids']) == set(owners[course['id']]['project_ids']), 'Historical Course Project association conflict')
    return o


def write_immutable(folder, o):
    from .observations import write_immutable_catalog
    return write_immutable_catalog(folder, o, 'course-project-associations')


def observation_from_candidate(folder, expected_digest, scopes, active_courses):
    """Verify the entire bundle, then construct only native association facts."""
    folder = Path(folder)
    verify_candidate(folder, expected_digest)
    read = lambda name: json.loads((folder / (name + '.json')).read_bytes())
    metadata, contract, states, relations, provenance = (read(name) for name in ('metadata', 'source-contract', 'course_states', 'course_project_memberships', 'provenance'))
    keys(metadata, 'candidate_type complete contract_file course_count ingested normal_project_catalog_count provenance_file sanitizer_version schema_version source_global_catalog_sha256 source_scope_index_sha256 source_timestamps_preserved')
    require(metadata['candidate_type'] == 'course_project_association_catalog' and metadata['complete'] is True and metadata['ingested'] is False and metadata['sanitizer_version'] == metadata['schema_version'] == 1 and metadata['source_timestamps_preserved'] is True, 'Invalid reviewed association candidate')
    require(metadata['course_count'] == len(scopes.courses) and metadata['normal_project_catalog_count'] == len(scopes.projects) and metadata['contract_file'] == 'source-contract.json' and metadata['provenance_file'] == 'provenance.json', 'Candidate scope inventory mismatch')
    require(contract['source_endpoint_family'] == '/api/tracks/<course_id>' and contract['enclosing_object'] == 'Track' and contract['source_field'] == 'tracks[].projects', 'Wrong association source interpretation')
    require(read('out_of_catalog_references') == [], 'Out-of-catalog association review required')
    o = {'observation_type': TYPE, 'schema_version': 1, 'sanitizer_schema_version': 1,
         'captured_at_start': min(p['observed_at'] for p in provenance),
         'captured_at_end': max(p['observed_at'] for p in provenance),
         'candidate': {'inventory_sha256': expected_digest,
                       'manifest_sha256': hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                       'global_catalog_sha256': metadata['source_global_catalog_sha256'],
                       'scope_index_sha256': metadata['source_scope_index_sha256']},
         'scope_catalog': {'observation': scopes.identity, 'sha256': hashlib.sha256(encode(scopes.observation)).hexdigest()},
         'semantic_contract': CONTRACT.copy(), 'source_pages': [], 'courses': []}
    source_ids, source_rows = {}, {}
    require(isinstance(provenance, list) and isinstance(states, list) and isinstance(relations, list), 'Invalid candidate relation tables')
    for p in provenance:
        keys(p, 'source_id course_id endpoint method response_object response_field observed_at http_result meta sanitizer_version sanitized_file sanitized_sha256 completeness')
        cid = identifier(p['course_id'])
        require(cid not in source_rows and p['sanitized_file'] == f'sources/course-{cid}.json', 'Duplicate or invalid candidate Course source')
        body = (folder/p['sanitized_file']).read_bytes()
        require(hashlib.sha256(body).hexdigest() == p['sanitized_sha256'], 'Candidate source digest mismatch')
        native = json.loads(body)
        keys(native, 'schema_version endpoint http_result captured_at object_type response_field course_id state native_project_ids project_ids meta auxiliary_lists projects_by_level has_project_count projects_count project_field_names')
        security_guard(native)
        require(native['course_id'] == cid and native['endpoint'] == p['endpoint'] == '/api/tracks/' + str(cid) and p['method'] == 'GET', 'Wrong candidate Course source')
        require(native['captured_at'] == p['observed_at'] and native['http_result'] == p['http_result'] == 200 and native['meta'] == p['meta'], 'Candidate capture provenance mismatch')
        require(native['object_type'] == p['response_object'] == 'Track' and native['response_field'] == p['response_field'] == 'tracks[].projects' and p['completeness'] == CONTRACT['completeness'], 'Candidate field provenance mismatch')
        require(p['source_id'] == f"track-projects-{cid}-{p['sanitized_sha256'][:12]}" and p['sanitizer_version'] == native['schema_version'] == 1, 'Invalid native candidate identity')
        ids = unique_ids(native['native_project_ids'])
        require(native['project_ids'] == sorted(ids) and native['state'] == ('KNOWN' if ids else 'KNOWN_EMPTY'), 'Invalid candidate source ID inventory')
        s = {'course_id': cid, 'endpoint': p['endpoint'], 'captured_at': p['observed_at'],
             'http_status': 200, 'sanitized_sha256': p['sanitized_sha256'], 'meta': p['meta'],
             'project_ids': native['native_project_ids']}
        s['id'] = 'source:' + hashlib.sha256(encode(s)).hexdigest()
        o['source_pages'].append(s); source_ids[p['source_id']] = s['id']; source_rows[cid] = native
    expected = []
    for row in states:
        keys(row, 'course_id state project_ids complete source_id')
        require(row['source_id'] in source_ids and row['course_id'] in source_rows, 'Unknown association state source')
        native = source_rows[row['course_id']]
        require(row['state'] == native['state'] and row['project_ids'] == native['project_ids'] and row['complete'] is True, 'Candidate association state/source mismatch')
        o['courses'].append({**row, 'source_id': source_ids[row['source_id']]})
        expected.extend({'course_id': row['course_id'], 'project_id': pid, 'provenance_id': row['source_id']} for pid in row['project_ids'])
    for row in relations:
        keys(row, 'course_id project_id provenance_id')
    require(relations == expected and len({(r['course_id'],r['project_id']) for r in relations}) == len(relations), 'Normalized association relations mismatch')
    o['courses'].sort(key=lambda r: r['course_id']); o['source_pages'].sort(key=lambda r: r['course_id'])
    validate_observation(o, scopes, active_courses)
    return o
