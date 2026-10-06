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
    if cp.get('spatial_authority'):
        return canonical_artifacts(runtime.parents[1], data, cp, geom, snapshot)
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


def production_outputs(outputs, preview):
    """Package the accepted persistent-state build; branding is the only UI edit."""
    if 'spatial-authority.json' in outputs:
        result={k:v for k,v in outputs.items() if k not in ('build-manifest.json','update-snapshot.json')}
        cp=json.loads(result['layout-checkpoint.json'])
        result['release-manifest.json']=encode(dict(pipeline_version=3,target='production',runtime_contract='global-canonical-1',generation=cp['presentation_generation'],assets={n:hashlib.sha256(b).hexdigest() for n,b in sorted(result.items())}))
        return result
    result = preview_outputs(outputs)
    result.pop('release-manifest.json')
    html = result['index.html'].decode().replace('<title>Knowledge Atlas · Preview</title>', '<title>Knowledge Atlas</title>')
    html = html.replace('Knowledge Atlas <small>· Preview</small>', 'Knowledge Atlas')
    if 'Preview' in html or 'Prototype' in html: raise ValueError('production branding mismatch')
    result['index.html'] = html.encode()
    unchanged = ('style.css','model.js','routing.js','taxonomy-relations.js','vendor/D3-LICENSE','vendor/d3-7.9.0.min.js')
    for name in unchanged:
        if result[name] != (preview/name).read_bytes(): raise ValueError('accepted runtime changed: '+name)
    expected_app=(preview/'app.js').read_text().replace('known=ss.length>0,','known=ss.length>0||m.raw.indexes.projects[String(p.id)].requirements_loaded,')
    if result['app.js'] != expected_app.encode(): raise ValueError('unexpected project adapter change')
    expected_layout=(preview/'layout.js').read_bytes()+b'\n'+(Path(__file__).parent/'layout_update.js').read_bytes()+b'\nAtlasLayout.build=(m,measure,cp)=>AtlasIncremental.hydrate(m,AtlasBuildGeometry,cp);\n'
    if result['layout.js'] != expected_layout: raise ValueError('unexpected geometry adapter change')
    expected_html=(preview/'index.html').read_text().replace('<title>Knowledge Atlas · Preview</title>','<title>Knowledge Atlas</title>')
    expected_html=expected_html.replace('Knowledge Atlas <small>· Preview</small>','Knowledge Atlas').replace('<script src="app.js">','<script src="geometry.js"></script><script src="app.js">')
    if result['index.html'] != expected_html.encode(): raise ValueError('unexpected production HTML change')
    reasons={'index.html':'Preview title/header removed; accepted geometry.js hydration script loaded',
             'app.js':'Already accepted generic project-requirement index adapter; no project-specific code',
             'layout.js':'Already accepted deterministic hydration adapter; same frozen node/tray/hierarchy geometry',
             'model.json':'Canonical knowledge serialization, deterministic hashes and derived evidence/membership indexes',
             'layout-checkpoint.json':'Accepted persistent presentation state schema 2 replaces legacy preview schema 5',
             'layout-checkpoint.schema.json':'Schema for accepted persistent state',
             'geometry.js':'Runtime-required geometry derived from persistent state; no fresh layout generation'}
    comparisons=[]
    for name,content in sorted(result.items()):
        reference=preview/name
        equal=reference.is_file() and reference.read_bytes()==content
        if not equal and name not in reasons:raise ValueError('unexplained production asset difference: '+name)
        comparisons.append({'asset':name,'identical':equal,'reason':'byte-identical accepted asset' if equal else reasons[name],
                            'preview_sha256':hashlib.sha256(reference.read_bytes()).hexdigest() if reference.is_file() else None,
                            'production_sha256':hashlib.sha256(content).hexdigest()})
    cp=json.loads(result['layout-checkpoint.json'])
    result['release-manifest.json']=encode({'pipeline_version':2,'target':'production','deployment_path':'docs/knowledge-map/',
        'public_url':'https://planton361.github.io/hyperskill-projects/knowledge-map/',
        'state_schema_version':cp['state_schema_version'],'layout_schema_version':cp['layout_schema_version'],
        'layout_algorithm_version':cp['layout_algorithm_version'],'generation':cp['presentation_generation'],
        'preview_comparison':comparisons,'assets':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(result.items())}})
    return result


def verify_release(path, expected=None):
    manifest=json.loads((path/'release-manifest.json').read_text())
    if manifest.get('target')!='production':raise ValueError('invalid production release manifest')
    names={p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()}
    if names != set(manifest['assets'])|{'release-manifest.json'}:raise ValueError('stale/missing production files')
    for name,sha in manifest['assets'].items():
        if hashlib.sha256((path/name).read_bytes()).hexdigest()!=sha:raise ValueError('production integrity mismatch: '+name)
    if expected is not None and any((path/n).read_bytes()!=b for n,b in expected.items()):
        raise ValueError('production is not reproducible from current data/state')


def canonical_artifacts(root, data, cp, geom, previous):
    """Package installed immutable master plus current semantic projection."""
    from . import canonical, catalog_projection, snapshot as snapshots
    root=Path(root);runtime=Path(__file__).parent/'canonical_runtime'
    loaded=snapshots.load_source(root/'data/knowledge')
    history={'active_categories':[k for k in cp['accepted_inventory'] if k.startswith('category:')],
             'active_topics':[k for k in cp['accepted_inventory'] if k.startswith('topic:')]}
    out={p.relative_to(runtime).as_posix():p.read_bytes() for p in runtime.rglob('*') if p.is_file()}
    master=canonical.master(root,cp['spatial_authority']);canonical.validate_geometry(master,geom,cp['accepted_inventory'])
    raw={t:data[t] for t in TABLES};raw['source_hashes']={t:digest(data[t]) for t in TABLES};raw['source_hash_policy']='sha256 canonical normalized JSON; independent of input ordering';raw['indexes']=evidence_index(data)
    out.update({'model.json':encode(raw),'layout-checkpoint.json':encode(cp),'spatial-authority.json':encode(cp['spatial_authority']),
                'target-geometry.json':encode(geom),'update-snapshot.json':encode(previous),
                'generated/global-geometry.json':(root/'docs/knowledge-map/generated/global-geometry.json').read_bytes(),
                'generated/catalog.json':encode(catalog_projection.project(loaded,history))})
    out['build-manifest.json']=encode(dict(pipeline_version=3,state_schema_version=3,layout_schema_version=cp['layout_schema_version'],layout_algorithm_version=cp['layout_algorithm_version'],assets={n:hashlib.sha256(v).hexdigest() for n,v in sorted(out.items())}))
    return out
