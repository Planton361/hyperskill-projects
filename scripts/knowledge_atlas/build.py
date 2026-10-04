"""Deterministic derived assets and transactional isolated publication."""
import hashlib
import json
from pathlib import Path
from .snapshot import TABLES, canonical, digest, encode

ASSETS = ('app.js', 'index.html', 'layout.js', 'model.js', 'routing.js', 'taxonomy-relations.js',
          'style.css', 'vendor/D3-LICENSE', 'vendor/d3-7.9.0.min.js')


def evidence_index(data):
    projects = {}
    topics = {str(t['id']): [] for t in data['topics']}
    for p in data['projects']:
        requirements = [e for e in data['edges'] if e['type'] == 'project_requires' and e['source'] == f"project:{p['id']}"]
        stages = [s for s in data['stages'] if s['project_id'] == p['id']]
        projects[str(p['id'])] = {'requirements_loaded': bool(stages or requirements),
                                  'required_topic_ids': sorted({int(e['target'].split(':')[1]) for e in requirements}),
                                  'stage_ids': [s['id'] for s in sorted(stages, key=lambda s: s['position'])]}
        for edge in requirements:
            topics[edge['target'].split(':')[1]].append({'project_id': p['id'], 'stage_id': edge.get('stage_id'),
                                                        'evidence_ids': edge['evidence_ids']})
    memberships = {str(t['id']): sorted(c['id'] for c in data['courses'] if t['id'] in c['topic_ids'])
                   for t in data['topics']}
    return canonical({'projects': projects, 'topic_project_evidence': topics, 'topic_courses': memberships})


def artifacts(runtime, data, cp, geom, snapshot):
    out = {name: (runtime / name).read_bytes() for name in ASSETS}
    raw = {t: data[t] for t in TABLES}
    raw['source_hashes'] = {t: digest(data[t]) for t in TABLES}
    raw['source_hash_policy'] = 'sha256 canonical normalized JSON; independent of input ordering'
    raw['indexes'] = evidence_index(data)
    out['model.json'] = encode(raw)
    out['update-snapshot.json'] = encode(snapshot)
    out['layout-checkpoint.json'] = encode(cp)
    out['geometry.json'] = encode(geom)
    out['geometry.js'] = b'globalThis.AtlasBuildGeometry=' + encode(geom).strip() + b';\n'
    adapter = (Path(__file__).parent / 'layout_update.js').read_bytes()
    out['layout.js'] += b'\n' + adapter + b'\nAtlasLayout.build=(m,measure,cp)=>AtlasIncremental.hydrate(m,AtlasBuildGeometry,cp);\n'
    html = out['index.html'].decode().replace('<script src="app.js">', '<script src="geometry.js"></script><script src="app.js">')
    out['index.html'] = html.encode()
    # Data plumbing only: known direct project requirements also enable existing coverage UI.
    app = out['app.js'].decode().replace('known=ss.length>0,', 'known=ss.length>0||m.raw.indexes.projects[String(p.id)].requirements_loaded,')
    if 'known=ss.length>0||m.raw.indexes' not in app:
        raise ValueError('accepted project inspector integration changed; review build adapter')
    out['app.js'] = app.encode()
    out['layout-checkpoint.schema.json'] = (Path(__file__).parent / 'checkpoint.schema.json').read_bytes()
    manifest = {'pipeline_version': 2, 'state_schema_version': cp['state_schema_version'], 'layout_schema_version': cp['layout_schema_version'],
                'layout_algorithm_version': cp['layout_algorithm_version'],
                'assets': {name: hashlib.sha256(value).hexdigest() for name, value in sorted(out.items())}}
    out['build-manifest.json'] = encode(manifest)
    return out


def verify_state(destination):
    manifest = json.loads((destination / 'build-manifest.json').read_text())
    for name, expected in manifest['assets'].items():
        p = destination / name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError('build state integrity mismatch: ' + name)


def preview_outputs(outputs):
    allowed = set(ASSETS) | {'geometry.js', 'model.json', 'layout-checkpoint.json', 'layout-checkpoint.schema.json'}
    result = {k: v for k, v in outputs.items() if k in allowed}
    html = result['index.html'].decode().replace('Knowledge Atlas · V6.6 focus + context prototype', 'Knowledge Atlas · Preview')
    html = html.replace('Knowledge Map <small>· Prototype V6.6</small>', 'Knowledge Atlas <small>· Preview</small>')
    result['index.html'] = html.encode()
    result['release-manifest.json'] = encode({'pipeline_version': 1, 'assets': {
        k: hashlib.sha256(v).hexdigest() for k, v in sorted(result.items())}})
    return result
