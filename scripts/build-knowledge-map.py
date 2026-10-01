#!/usr/bin/env python3
"""Offline deterministic production map and profile-summary generation."""
import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CONFIG = HERE / 'knowledge-map'
PUBLIC_URL = 'https://planton361.github.io/hyperskill-projects/knowledge-map/'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def project_model(root=REPO):
    spec = importlib.util.spec_from_file_location('source_contract', HERE / 'build-knowledge-graph.py')
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    contract.validate(contract.load(root))
    data = root / 'data/knowledge'
    tables = {name: load(data / f'{name}.json') for name in
              ['courses', 'categories', 'topics', 'projects', 'stages', 'edges', 'progress', 'evidence']}
    mapping = load(CONFIG / 'display-map.json')
    categories = {c['id']: c for c in tables['categories']}
    progress = {}
    for row in tables['progress']['topics']:
        old = progress.get(row['topic_id'])
        if old is None or row.get('observed_at', '') > old.get('observed_at', ''):
            progress[row['topic_id']] = row
        elif row.get('observed_at') == old.get('observed_at'):
            if (row['is_learned'], row['is_verified']) != (old['is_learned'], old['is_verified']):
                raise ValueError('Conflicting equally recent personal observations')

    def ancestry(parent):
        result = []
        while parent in categories:
            if parent in result:
                raise ValueError('Category cycle')
            result.append(parent)
            parent = categories[parent]['canonical_parent_id']
        return result

    topics = []
    for topic in sorted(tables['topics'], key=lambda t: t['id']):
        path = ancestry(topic['canonical_parent_id'])
        domain = next((d for cat in path for d in mapping['domains'] if cat in d['category_ids']), None)
        subdomain = next((s for cat in path for s in mapping['subdomains'] if cat in s['category_ids']), None)
        if domain is None or subdomain is None or subdomain['domain_id'] != domain['id']:
            raise ValueError(f'Unmapped topic {topic["id"]}; review taxonomy, do not silently drop')
        row = progress.get(topic['id'], {})
        topics.append({**topic, 'key': f'topic:{topic["id"]}',
                       'domain_id': domain['id'], 'subdomain_id': subdomain['id'],
                       'canonical_ancestry': path,
                       'course_ids': [c['id'] for c in tables['courses'] if topic['id'] in c['topic_ids']],
                       'is_learned': row.get('is_learned'), 'is_verified': row.get('is_verified'),
                       'verification_status': row.get('verification_status'), 'is_applied': None,
                       'progress_evidence_ids': row.get('evidence_ids', [])})
    assert len({t['id'] for t in topics}) == len(topics)

    def counts(items):
        return {'total': len(items), 'learned': sum(t['is_learned'] is True for t in items),
                'verified': sum(t['is_learned'] is True and t['is_verified'] is True for t in items),
                'not_learned': sum(t['is_learned'] is False for t in items),
                'unknown': sum(t['is_learned'] is None for t in items)}

    domains = [{**d, **counts([t for t in topics if t['domain_id'] == d['id']])} for d in mapping['domains']]
    subdomains = [{**s, **counts([t for t in topics if t['subdomain_id'] == s['id']])} for s in mapping['subdomains']]
    state = {p['project_id']: p for p in tables['progress']['projects']}
    projects = []
    for project in tables['projects']:
        requirements = [e for e in tables['edges'] if e['type'] == 'project_requires' and e['source'] == f'project:{project["id"]}']
        projects.append({**project, 'key': f'project:{project["id"]}',
                         'status': state.get(project['id'], {}).get('status', 'available'),
                         'completed_stage_ids': state.get(project['id'], {}).get('completed_stage_ids'),
                         'required_topic_ids': sorted({int(e['target'].split(':')[1]) for e in requirements}) if requirements else None})

    # Preserve all relation records and provenance; visual lines coalesce only
    # prerequisite/dependent corroboration for the same directed endpoints.
    grouped = {}
    for edge in tables['edges']:
        if edge['type'] not in ('prerequisite', 'dependent'):
            continue
        pair = (edge['source'], edge['target'])
        grouped.setdefault(pair, []).append(edge)
    connections = [{'source': a, 'target': b, 'records': records}
                   for (a, b), records in sorted(grouped.items())]
    capability_results = []
    by_id = {t['id']: t for t in topics}
    for cap in load(CONFIG / 'capabilities.json')['capabilities']:
        ids = cap['required_topic_ids']
        if any(id not in by_id for id in ids):
            raise ValueError('Unresolved capability evidence')
        capability_results.append({**cap, 'learned_evidence': sum(by_id[id]['is_learned'] is True for id in ids),
                                   'verified_evidence': sum(by_id[id]['is_verified'] is True for id in ids),
                                   'evidence_total': len(ids), 'proficiency': None})
    statistics = {**counts(topics), 'categories': len(categories), 'raw_edge_types': dict(Counter(e['type'] for e in tables['edges'])),
                  'connections': len(connections), 'completed_projects': sum(p['status'] == 'completed' for p in projects),
                  'active_projects': sum(p['status'] == 'active' for p in projects)}
    return {**tables, 'topics': topics, 'projects': projects, 'domains': domains, 'subdomains': subdomains,
            'connections': connections, 'capability_evidence': capability_results, 'statistics': statistics,
            'summary_policy': mapping['summary'],
            'source_hashes': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(data.rglob('*')) if p.is_file()}}


def summary(model):
    """Bounded editorial presentation, never a proficiency score."""
    policy = model['summary_policy']
    rows = sorted([d for d in model['domains'] if d['learned']], key=lambda d: (-d['learned'], d['id']))
    limit = policy['max_domain_rows']
    cut = limit if len(rows) <= limit else limit - 1
    shown, rest = rows[:cut], rows[cut:]
    courses = sorted(model['progress']['courses'], key=lambda c: (c.get('active_project') is None, c['course_id']))
    course = courses[0]
    title = next(c['title'] for c in model['courses'] if c['id'] == course['course_id'])
    verified = sum(t['is_learned'] is True and t['is_verified'] is True for t in model['topics'] if course['course_id'] in t['course_ids'])
    lines = ['### My Learning', '', title + '<br>',
             f'{course["learned_topics_count"]} / {course["learned_topics_total"]} course topics learned · {verified} verified',
             '', 'Knowledge areas:', '']
    for d in shown:
        lines.append(f'- [{d["title"]}]({PUBLIC_URL}?domain={d["id"].split(":")[-1]}) — {d["learned"]} learned')
    if rest:
        lines.append(f'- Other areas ({len(rest)}) — {sum(d["learned"] for d in rest)} learned')
    completed = sorted([p for p in model['projects'] if p['status'] == 'completed'], key=lambda p: p['id'])
    if completed:
        p = completed[0]
        lines += ['', 'Project evidence:', '', f'- [{p["title"]}]({p["url"]}) — completed']
        if p['required_topic_ids'] is not None:
            lines.append(f'- {len(p["required_topic_ids"])} required topics across its stages')
    lines += ['', f'[Explore my interactive Knowledge Map →]({PUBLIC_URL})', '']
    return '\n'.join(lines)


def render(root=REPO, check=False):
    model = project_model(root)
    outputs = {root / 'docs/knowledge-map/model.json': encode(model),
               root / 'generated/profile-learning-summary.md': summary(model)}
    for file, value in outputs.items():
        if check:
            if not file.exists() or file.read_text(encoding='utf-8') != value:
                raise ValueError(f'Stale generated output: {file}')
        else:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(value, encoding='utf-8')
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=REPO)
    parser.add_argument('--check', action='store_true', help='Validate sources and compare deterministic outputs without writing.')
    args = parser.parse_args()
    model = render(args.root.resolve(), args.check)
    print(encode(model['statistics']), end='')
