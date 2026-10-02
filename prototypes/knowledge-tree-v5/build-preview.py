#!/usr/bin/env python3
"""Validate and package accepted V5.2; writes only docs/knowledge-map-preview/.

The browser consumes static assets. Python/Node are release validation tools only.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
TARGET = ROOT / 'docs/knowledge-map-preview'
ARTIFACTS = SOURCE / 'tests/release'
ASSETS = ('app.js', 'layout.js', 'routing.js', 'style.css', 'model.json',
          'layout-checkpoint.json', 'layout-checkpoint.schema.json',
          'vendor/d3-7.9.0.min.js', 'vendor/D3-LICENSE')
TABLES = ('courses', 'categories', 'topics', 'projects', 'stages', 'edges', 'progress', 'evidence')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    spec = importlib.util.spec_from_file_location('source_contract', ROOT / 'scripts/build-knowledge-graph.py')
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    contract.validate(contract.load(ROOT))
    raw = json.loads((SOURCE / 'model.json').read_text())
    for table in TABLES:
        actual = ROOT / 'data/knowledge' / (table + '.json')
        assert raw[table] == json.loads(actual.read_text()), f'Non-source data: {table}'
        assert raw['source_sha256'][table] == sha(actual), f'Stale source hash: {table}'
    course = next(c for c in raw['courses'] if c['id'] == 8)
    assert course['title'] == 'Introduction to Java'
    assert len(course['topic_ids']) == len(set(course['topic_ids'])) == 89
    assert len(raw['topics']) == len({t['id'] for t in raw['topics']}) == 89
    progress = [p for p in raw['progress']['topics'] if p['topic_id'] in course['topic_ids']]
    assert sum(p['is_learned'] is True for p in progress) == 31
    assert sum(p['is_verified'] is True for p in progress) == 12
    project = next(p for p in raw['projects'] if p['id'] == 113)
    assert project['title'] == 'Simple Chat Bot with Java'
    assert next(p for p in raw['progress']['projects'] if p['project_id'] == 113)['status'] == 'completed'
    requirements = {e['target'] for e in raw['edges'] if e['type'] == 'project_requires' and e['source'] == 'project:113'}
    assert len(requirements) == 26
    assert not any(e['type'] == 'project_applies' for e in raw['edges'])
    p380 = next(p for p in raw['progress']['projects'] if p['project_id'] == 380)
    assert p380 == next(p for p in json.loads((ROOT / 'data/knowledge/progress.json').read_text())['projects'] if p['project_id'] == 380)
    subprocess.run(['node', str(SOURCE / 'tests/release/checkpoint.cjs')], check=True)
    return {'course': course['title'], 'courseTopics': 89, 'learned': 31, 'verified': 12,
            'project113': {'title': project['title'], 'status': 'completed', 'distinctRequiredTopics': 26},
            'project380': p380, 'projectApplies': 0, 'source_sha256': raw['source_sha256']}


def package(check=False):
    data = validate()  # Validate before any preview asset is written.
    files = {name: (SOURCE / name).read_bytes() for name in ASSETS}
    html = (SOURCE / 'index.html').read_text()
    html = html.replace('Knowledge atlas · Tree V5.1', 'Knowledge Map · Preview')
    html = html.replace('KNOWLEDGE ATLAS / EXPERIMENT 05.1', 'KNOWLEDGE ATLAS / PREVIEW')
    files['index.html'] = html.encode()
    for name in ('index.html', 'app.js', 'layout.js', 'routing.js', 'style.css'):
        text = files[name].decode()
        assert not re.search(r'/home/anton|localhost|127\.0\.0\.1|file://|node_modules|require\(', text), name
    for name, payload in files.items():
        target = TARGET / name
        if check:
            assert target.read_bytes() == payload, f'Preview drift: {name}'
        elif not target.exists() or target.read_bytes() != payload:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    allowed = set(files) | {'PREVIEW-NOTES.md', 'release-manifest.json'}
    if TARGET.exists():
        unexpected = [p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.relative_to(TARGET).as_posix() not in allowed]
        assert not unexpected, f'Unexpected preview assets (not published): {unexpected}'
    manifest = {'sourceVersion': 'accepted V5.2 + Project Coverage overlay/reveal/fit', 'deploymentPath': 'docs/knowledge-map-preview/',
                'layoutSchemaVersion': 2, 'layoutAlgorithmVersion': 'persistent-geography-2',
                'data': data, 'assets': {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(files.items())},
                'sourceAssets': {name: sha(SOURCE / name) for name in sorted((*ASSETS, 'index.html'))},
                'brandingOnlyDifference': 'index title and quiet preview eyebrow'}
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if check:
        assert (TARGET / 'release-manifest.json').read_text() == encoded, 'Manifest drift'
    else:
        (TARGET / 'release-manifest.json').write_text(encoded)
    print(json.dumps({'validated': True, 'checkOnly': check, 'path': 'docs/knowledge-map-preview/',
                      'topics': 89, 'learned': 31, 'verified': 12, 'required': 26}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    package(parser.parse_args().check)
