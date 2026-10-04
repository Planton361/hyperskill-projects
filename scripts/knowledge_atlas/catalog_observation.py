"""Offline, positive-allowlist HAR extraction. Never retains account/request data."""
import base64
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs
from .snapshot import canonical, encode
import hashlib

VERSION = 1


def ordered_catalog(value):
    """Inventory arrays are sets; the API's hierarchy path keeps its order."""
    if isinstance(value, dict):
        return {k: (list(v) if k == 'hierarchy' else ordered_catalog(v)) for k, v in sorted(value.items())}
    if isinstance(value, list):
        def key(v):
            if type(v) is int: return (0, v)
            if isinstance(v, str): return (1, v)
            if isinstance(v, dict) and type(v.get('id')) is int: return (2, v['id'])
            return (3, encode(v))
        return sorted((ordered_catalog(v) for v in value), key=key)
    return value
CATEGORY_FIELDS = ('id', 'title', 'parent_id', 'children', 'descendants')
TOPIC_FIELDS = ('id', 'title', 'is_group', 'parent_id', 'children', 'hierarchy',
                'root_id', 'theory', 'prerequisites', 'explicit_prerequisites', 'followers')
# No platform flags are approved yet: enabled is not personal accessibility.
FORBIDDEN = re.compile(r'cookie|authorization|csrf|token|user_id|progress_id|study_plan_id|'
                       r'subscription|payment|certificate|email|profile|websocket|created_by', re.I)
SECRET_VALUE = re.compile(r'Bearer\s+\S+|(?:csrf|token|cookie|authorization|user_id|progress_id|study_plan_id)\s*[=:]|'
                          r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.|'
                          r'https?://[^\s]*[?#]|/(?:home|tmp)/', re.I)


def require(ok, message):
    if not ok:
        raise ValueError(message)  # Messages are constants, never raw values.


def security_guard(value):
    if isinstance(value, dict):
        for k, v in value.items():
            require(isinstance(k, str) and not FORBIDDEN.search(k), 'Sensitive field rejected')
            security_guard(v)
    elif isinstance(value, list):
        for v in value:
            security_guard(v)
    elif isinstance(value, str):
        require(not SECRET_VALUE.search(value), 'Sensitive value pattern rejected')
    else:
        require(value is None or type(value) in (int, bool), 'Unsupported catalog value')


def identifier(value):
    require(type(value) is int and value > 0, 'Invalid catalog identifier')
    return value


def ids(value):
    require(isinstance(value, list), 'Invalid identifier inventory')
    return sorted({identifier(v) for v in value})


def title(value):
    require(isinstance(value, str) and bool(value.strip()), 'Missing explicit catalog title')
    security_guard(value)
    return value


def category_record(raw):
    # Construct a new object. Unknown fields never pass through.
    require(isinstance(raw, dict) and all(k in raw for k in CATEGORY_FIELDS), 'Missing structural Category fields')
    row = {'id': identifier(raw.get('id')), 'title': title(raw.get('title')),
           'parent_id': None if raw.get('parent_id') is None else identifier(raw['parent_id']),
           'children': ids(raw.get('children')), 'descendants': ids(raw.get('descendants'))}
    require(bool(row['children']), 'Structural category must have explicit children')
    return row


def topic_record(raw):
    require(raw.get('is_group') is False, 'Explicit Topic type required')
    row = {'id': identifier(raw.get('id')), 'title': title(raw.get('title')), 'is_group': False}
    for k in TOPIC_FIELDS:
        if k in row or k not in raw:
            continue
        v = raw[k]
        if k == 'hierarchy':
            require(isinstance(v, list) and len(v) == len(set(v)), 'Invalid hierarchy path')
            row[k] = [identifier(i) for i in v]
        elif k in ('children', 'prerequisites', 'followers'):
            row[k] = ids(v)
        elif k == 'explicit_prerequisites':
            require(isinstance(v, list), 'Invalid explicit prerequisite inventory')
            row[k] = canonical([{'kind': identifier(x.get('kind')), 'source': identifier(x.get('source'))} for x in v])
        else:
            row[k] = None if v is None else identifier(v)
    security_guard(row)
    return row


def resolution(row):
    complete = ('parent_id', 'theory', 'prerequisites', 'explicit_prerequisites', 'followers')
    return 'RESOLVED_TOPIC' if row.get('is_group') is False and all(k in row for k in complete) and row['theory'] is not None else 'PARTIAL_TOPIC'


def forest(categories):
    """Validate structural forest independently from the single-root renderer."""
    by_id = {r['id']: r for r in categories}
    require(len(by_id) == len(categories), 'Duplicate structural IDs')
    pairs = {(r['id'], c) for r in categories for c in r['children']}
    require(all(a != b for a, b in pairs), 'Self structural relation')
    roots = sorted(i for i, r in by_id.items() if r['parent_id'] is None)
    require(bool(roots), 'Missing structural roots')
    for i, r in by_id.items():
        parent = r['parent_id']
        require(parent is None or parent in by_id, 'Missing Category parent')
        incoming = {a for a, b in pairs if b == i}
        require(incoming == (set() if parent is None else {parent}), 'Inconsistent Category parent evidence')
    leaves = {b for _, b in pairs if b not in by_id}
    visited, visiting, closures, depths = set(), set(), {}, {}
    def visit(i, depth):
        require(i not in visiting, 'Category cycle')
        visiting.add(i)
        visited.add(i)
        depths[i] = depth
        found = set()
        for child in by_id[i]['children']:
            if child in by_id:
                found.update(visit(child, depth + 1))
            else:
                found.add(child)
        require(found == set(by_id[i]['descendants']), 'Inconsistent explicit descendants')
        closures[i] = found
        visiting.remove(i)
        return found
    for root in roots:
        visit(root, 0)
    require(visited == set(by_id), 'Unreachable structural positions')
    memberships = {i: sorted(a for a, b in pairs if b == i) for i in leaves}
    return {'roots': roots, 'category_count': len(by_id), 'leaf_reference_count': len(leaves),
            'hierarchy_count': len(pairs), 'category_hierarchy_count': sum(b in by_id for _, b in pairs),
            'leaf_membership_count': sum(b in leaves for _, b in pairs),
            'maximum_leaf_depth': max((depths[a] + 1 for a, b in pairs if b in leaves), default=0),
            'cycles': 0, 'self_relations': 0, 'missing_category_parents': 0, 'unreachable_positions': 0,
            'multiple_leaf_memberships': [{'id': i, 'parent_ids': parents} for i, parents in sorted(memberships.items()) if len(parents) > 1]}


def timestamp(raw):
    require(isinstance(raw, str), 'Missing capture timestamp')
    try:
        d = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        require(d.tzinfo is not None, 'Capture timestamp needs timezone')
        return d.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    except (ValueError, TypeError):
        raise ValueError('Invalid capture timestamp') from None


def sanitize(har):
    require(isinstance(har, dict) and isinstance(har.get('log', {}).get('entries'), list), 'Invalid HAR structure')
    pages, sources, topic_candidates, times = {}, {}, {}, []
    def source(path, payload, **metadata):
        key = 'source:' + hashlib.sha256(encode(ordered_catalog({'endpoint': path, 'payload': payload, **metadata}))).hexdigest()
        sources[key] = {'id': key, 'method': 'GET', 'path': path, 'content_type': 'application/json', **metadata}
        return key
    def add_topic(row, src):
        topic_candidates.setdefault(row['id'], []).append((row, src))
    for entry in har['log']['entries']:
        times.append(timestamp(entry.get('startedDateTime')))
        request, response = entry.get('request', {}), entry.get('response', {})
        try:
            u = urlsplit(request.get('url', ''))
            query = parse_qs(u.query, keep_blank_values=True)
        except ValueError:
            continue
        if u.scheme != 'https' or u.hostname != 'hyperskill.org' or request.get('method') != 'GET' or response.get('status') != 200:
            continue
        is_map = u.path == '/api/topic-relations' and set(query) <= {'page', 'page_size'}
        is_topic = bool(re.fullmatch(r'/api/topics/[1-9][0-9]*', u.path))
        is_activity = u.path == '/api/learning-activities'
        if not (is_map or is_topic or is_activity):
            continue
        content = response.get('content', {})
        body = content.get('text')
        if not body:
            continue  # HAR duplicates may omit bodies; decoded logical pages must still be complete.
        require('json' in content.get('mimeType', '').lower(), 'Relevant response is not JSON')
        try:
            if content.get('encoding') == 'base64':
                body = base64.b64decode(body, validate=True).decode('utf-8')
            decoded = json.loads(body)
        except (ValueError, UnicodeError, TypeError):
            raise ValueError('Relevant response body cannot be decoded') from None
        require(isinstance(decoded, dict), 'Invalid response envelope')
        if is_map:
            meta = decoded.get('meta', {})
            page = identifier(meta.get('page'))
            require(query.get('page', [str(page)]) == [str(page)], 'Pagination request/response mismatch')
            require('page_size' in query or 'page_size' in meta, 'Missing explicit pagination size')
            try:
                size = identifier(int(query['page_size'][0])) if 'page_size' in query else identifier(meta['page_size'])
            except (ValueError, TypeError):
                raise ValueError('Invalid pagination size') from None
            require(type(meta.get('has_next')) is bool and type(meta.get('has_previous')) is bool, 'Missing pagination flags')
            raw_rows = decoded.get('topic-relations')
            require(isinstance(raw_rows, list), 'Missing structural records')
            rows = canonical([category_record(r) for r in raw_rows])
            require(len({r['id'] for r in rows}) == len(rows), 'Duplicate IDs within page')
            page_meta = {'page': page, 'page_size': size, 'has_next': meta['has_next'],
                         'has_previous': meta['has_previous'], 'returned_record_count': len(rows),
                         'reported_total': None}
            src = source(u.path, rows, **page_meta)
            candidate = (rows, page_meta, src)
            require(page not in pages or pages[page] == candidate, 'Inconsistent repeated global page')
            pages[page] = candidate
        elif is_topic:
            for raw in decoded.get('topics', []):
                if raw.get('is_group') is not False:
                    continue
                row = topic_record(raw)
                require(row['id'] == int(u.path.rsplit('/', 1)[1]), 'Topic endpoint identity mismatch')
                add_topic(row, source(u.path, row))
        else:
            for raw in decoded.get('learning-activities', []):
                # topic_id is an explicit Topic foreign key, unlike a structural leaf ID.
                if raw.get('topic_id') is not None and raw.get('title'):
                    row = {'id': identifier(raw['topic_id']), 'title': title(raw['title'])}
                    add_topic(row, source(u.path, {'topic_id': row['id'], 'title': row['title']}))
    require(bool(pages), 'No global structural response pages')
    last = max(pages)
    require(sorted(pages) == list(range(1, last + 1)), 'Missing global pagination page')
    sizes = {m['page_size'] for _, m, _ in pages.values()}
    require(len(sizes) == 1, 'Inconsistent page sizes')
    for page, (rows, m, _) in pages.items():
        require(m['has_previous'] == (page > 1) and m['has_next'] == (page < last), 'Incomplete pagination boundary')
        require(len(rows) <= m['page_size'] and (page == last or len(rows) == m['page_size']), 'Incomplete pagination page')
    categories = []
    for page in sorted(pages):
        rows, _, src = pages[page]
        categories.extend({**r, 'fact_sources': {k: [src] for k in CATEGORY_FIELDS}} for r in rows)
    stats = forest(categories)
    category_ids = {r['id'] for r in categories}
    leaf_ids = {i for r in categories for i in r['children']} - category_ids
    topics = []
    for i, candidates in sorted(topic_candidates.items()):
        if i not in leaf_ids:
            continue
        fields, facts = {}, {}
        for row, src in candidates:
            for k, v in row.items():
                require(k not in fields or fields[k] == v, 'Conflicting explicit Topic metadata')
                fields[k] = v
                facts.setdefault(k, set()).add(src)
        topics.append({**fields, 'resolution': resolution(fields), 'fact_sources': {k: sorted(v) for k, v in facts.items()}})
    resolved_ids = {t['id'] for t in topics}
    references = [{'id': i, 'resolution': 'UNRESOLVED_REFERENCE',
                   'parent_ids': sorted(r['id'] for r in categories if i in r['children']),
                   'source_ids': sorted({s for r in categories if i in r['children'] for s in r['fact_sources']['children']})}
                  for i in sorted(leaf_ids - resolved_ids)]
    hierarchy = [{'parent_id': r['id'], 'child_id': c,
                  'child_type': 'CATEGORY' if c in category_ids else ('TOPIC' if c in resolved_ids else 'UNKNOWN_REFERENCE'),
                  'source_ids': r['fact_sources']['children']} for r in categories for c in r['children']]
    prerequisites, followers = [], []
    for t in topics:
        for field, output in [('prerequisites', prerequisites), ('followers', followers)]:
            for target in t.get(field, []):
                output.append({'source_id': target if field == 'prerequisites' else t['id'],
                               'target_id': t['id'] if field == 'prerequisites' else target,
                               'source_ids': t['fact_sources'][field]})
    # Retain only sources actually referenced by accepted global facts.
    used = {s for r in categories + topics for values in r['fact_sources'].values() for s in values}
    observation = {'observation_type': 'global_knowledge_catalog', 'schema_version': VERSION,
                   'sanitizer_schema_version': VERSION, 'captured_at_start': min(times), 'captured_at_end': max(times),
                   'snapshot_status': 'PARTIAL', 'categories': categories, 'topics': topics,
                   'unresolved_references': references, 'hierarchy_records': hierarchy,
                   'prerequisite_records': prerequisites, 'follower_records': followers,
                   'source_pages': [v for k, v in sorted(sources.items()) if k in used],
                   'coverage': {'taxonomy_pagination': 'COMPLETE_FOR_CAPTURED_ENDPOINT',
                                'category_metadata': 'COMPLETE_FOR_CAPTURED_ENDPOINT',
                                'leaf_references': 'COMPLETE_FOR_CAPTURED_ENDPOINT',
                                'topic_metadata': 'PARTIAL', 'prerequisites': 'PARTIAL', 'followers': 'PARTIAL',
                                'reported_total': None}, 'validation': stats}
    observation = ordered_catalog(observation)
    validate_observation(observation)
    return observation


def validate_observation(o):
    security_guard(o)
    keys = {'observation_type', 'schema_version', 'sanitizer_schema_version', 'captured_at_start', 'captured_at_end',
            'snapshot_status', 'categories', 'topics', 'unresolved_references', 'hierarchy_records',
            'prerequisite_records', 'follower_records', 'source_pages', 'coverage', 'validation'}
    require(set(o) == keys and o['observation_type'] == 'global_knowledge_catalog' and
            type(o['schema_version']) is int and o['schema_version'] == VERSION and
            type(o['sanitizer_schema_version']) is int and o['sanitizer_schema_version'] == VERSION, 'Unsupported global observation schema')
    require(timestamp(o['captured_at_start']) <= timestamp(o['captured_at_end']), 'Invalid capture interval')
    require(o['snapshot_status'] == 'PARTIAL', 'Unsupported authoritative replacement claim')
    sources = {s['id']: s for s in o['source_pages']}
    require(len(sources) == len(o['source_pages']), 'Duplicate source identifiers')
    for s in sources.values():
        require(set(s) <= {'id', 'method', 'path', 'content_type', 'page', 'page_size', 'has_next', 'has_previous', 'returned_record_count', 'reported_total'}, 'Unexpected source metadata')
        require(s['method'] == 'GET' and s['content_type'] == 'application/json' and
                (s['path'] in ('/api/topic-relations', '/api/learning-activities') or re.fullmatch(r'/api/topics/[1-9][0-9]*', s['path'])), 'Unexpected source endpoint')
    for r in o['categories']:
        require(set(r) == set(CATEGORY_FIELDS) | {'fact_sources'}, 'Unexpected Category field')
        require(category_record(r) == {k: r[k] for k in CATEGORY_FIELDS}, 'Noncanonical Category metadata')
        require(all(s in sources and sources[s]['path'] == '/api/topic-relations' for refs in r['fact_sources'].values() for s in refs),
                'Category fact has no structural source')
    for r in o['topics']:
        require(set(r) <= set(TOPIC_FIELDS) | {'resolution', 'fact_sources'}, 'Unexpected Topic field')
        identifier(r['id']); title(r['title'])
        if 'is_group' in r:
            require(topic_record(r) == {k: v for k, v in r.items() if k in TOPIC_FIELDS}, 'Noncanonical Topic fields')
        else:
            require(set(r) == {'id', 'title', 'resolution', 'fact_sources'}, 'Partial identity must originate in an explicit Topic foreign key')
        require(r['resolution'] == resolution(r), 'Incorrect Topic resolution state')
        for field in set(r) - {'resolution', 'fact_sources'}:
            refs = r['fact_sources'].get(field, [])
            allowed_paths = {f"/api/topics/{r['id']}"}
            if field in ('id', 'title'):
                allowed_paths.add('/api/learning-activities')
            require(refs and all(ref in sources and sources[ref]['path'] in allowed_paths for ref in refs), 'Topic fact has no explicit entity source')
    for r in o['categories'] + o['topics']:
        require(set(r['fact_sources']) == set(r) - {'resolution', 'fact_sources'}, 'Missing per-field provenance')
        require(all(v and set(v) <= set(sources) for v in r['fact_sources'].values()), 'Unknown fact source')
    require(forest(o['categories']) == o['validation'], 'Structural validation mismatch')
    cats = {r['id'] for r in o['categories']}
    leaves = {c for r in o['categories'] for c in r['children']} - cats
    topics = {r['id'] for r in o['topics']}
    refs = {r['id'] for r in o['unresolved_references']}
    require(len(topics) == len(o['topics']) and len(refs) == len(o['unresolved_references']) and
            not topics & refs and topics | refs == leaves, 'Leaf resolution coverage mismatch')
    for r in o['topics']:
        if r.get('parent_id') is not None:
            require(r['parent_id'] in cats and any(c['id'] == r['parent_id'] and r['id'] in c['children'] for c in o['categories']),
                    'Explicit Topic parent conflicts with structural membership')
        if 'children' in r:
            require(not r['children'], 'Topic leaf has structural children')
    for r in o['unresolved_references']:
        require(set(r) == {'id', 'resolution', 'parent_ids', 'source_ids'} and r['resolution'] == 'UNRESOLVED_REFERENCE', 'Invalid structural reference')
        require(r['parent_ids'] == sorted(c['id'] for c in o['categories'] if r['id'] in c['children']) and
                r['source_ids'] and set(r['source_ids']) <= set(sources), 'Reference membership mismatch')
    expected = canonical([{'parent_id': r['id'], 'child_id': c,
                          'child_type': 'CATEGORY' if c in cats else ('TOPIC' if c in topics else 'UNKNOWN_REFERENCE'),
                          'source_ids': r['fact_sources']['children']} for r in o['categories'] for c in r['children']])
    require(canonical(o['hierarchy_records']) == expected, 'Hierarchy fact mismatch')
    for field, records in [('prerequisites', 'prerequisite_records'), ('followers', 'follower_records')]:
        expected = canonical([{'source_id': v if field == 'prerequisites' else t['id'],
                               'target_id': t['id'] if field == 'prerequisites' else v,
                               'source_ids': t['fact_sources'][field]} for t in o['topics'] for v in t.get(field, [])])
        require(canonical(o[records]) == expected, 'Topic relation evidence mismatch')
    pages = sorted((s for s in sources.values() if s['path'] == '/api/topic-relations'), key=lambda s: s['page'])
    require([p['page'] for p in pages] == list(range(1, len(pages) + 1)) and bool(pages), 'Missing sanitized source page')
    for p in pages:
        require(p['has_previous'] == (p['page'] > 1) and p['has_next'] == (p['page'] < len(pages)) and p['reported_total'] is None,
                'Invalid sanitized pagination boundary')
        require(sum(p['id'] in r['fact_sources']['id'] for r in o['categories']) == p['returned_record_count'], 'Source page record count mismatch')
        require(p['returned_record_count'] <= p['page_size'] and (not p['has_next'] or p['returned_record_count'] == p['page_size']), 'Incomplete sanitized page')
    require(o['coverage'] == {'taxonomy_pagination': 'COMPLETE_FOR_CAPTURED_ENDPOINT', 'category_metadata': 'COMPLETE_FOR_CAPTURED_ENDPOINT',
                              'leaf_references': 'COMPLETE_FOR_CAPTURED_ENDPOINT', 'topic_metadata': 'PARTIAL', 'prerequisites': 'PARTIAL',
                              'followers': 'PARTIAL', 'reported_total': None}, 'Unsupported coverage claim')
    return o['validation']
