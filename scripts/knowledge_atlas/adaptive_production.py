"""Exact human-reviewed, Production-only publication. No State migration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from . import snapshot, transaction

PRODUCTION = 'docs/knowledge-map'
STATE = 'state/knowledge-atlas'
KNOWLEDGE = 'data/knowledge'
REFERENCE = 'prototypes/global-pyramid/generated/global-geometry.json'
JOURNAL = 'docs/.adaptive-production-transaction.json'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def require(condition, message):
    if not condition: raise ValueError(message)

def files(folder):
    folder = Path(folder)
    require(folder.is_dir(), 'Missing managed directory: ' + str(folder))
    require(not any(p.is_symlink() for p in (folder, *folder.parents)), 'Symlink path refused')
    result = {}
    for p in sorted(folder.rglob('*')):
        require(not p.is_symlink(), 'Symlink file refused: ' + str(p))
        if p.is_dir(): continue
        require(p.is_file(), 'Non-regular package file')
        result[p.relative_to(folder).as_posix()] = p.read_bytes()
    return result

def inventory(outputs, prefix=''):
    return {prefix + n: hashlib.sha256(b).hexdigest() for n, b in sorted(outputs.items())}

def bound_tree(root, folder):
    inv = inventory(files(root / folder), folder + '/')
    return {'inventory': inv, 'fingerprint': digest(inv)}

def identity(root):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    return {'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD')}

def pending(root):
    for name in ('state/.knowledge-atlas-transaction.json', 'state/.knowledge-atlas-transaction.tmp',
                 JOURNAL, 'docs/.adaptive-production-transaction.tmp'):
        require(not (root / name).exists(), 'Pending publication transaction: ' + name)
    for parent in (root / 'docs', root / 'state'):
        require(not list(parent.glob('.atlas-candidate-*')), 'Pending publication candidate')

def implementation(root):
    # Include the dispatcher/operator/helper and all loader Python dependencies.
    paths = list((root / 'scripts/knowledge_atlas').glob('*.py'))
    for folder in ('adaptive_runtime', 'presentation', 'canonical_runtime'):
        paths += [p for p in (root / 'scripts/knowledge_atlas' / folder).rglob('*') if p.is_file()]
    paths += [root / 'scripts/update-knowledge-atlas.py',
              root / 'prototypes/adaptive-pyramid/production-preview/build.py']
    paths += [p for p in (root / 'prototypes/adaptive-pyramid/vendor').rglob('*') if p.is_file()]
    inv = {}
    for p in sorted(set(paths)):
        require(not p.is_symlink(), 'Implementation symlink refused')
        inv[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {'inventory': inv, 'fingerprint': digest(inv)}

def candidate(root):
    spec = importlib.util.spec_from_file_location('adaptive_candidate', root / 'prototypes/adaptive-pyramid/production-preview/build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.candidate(root)

def diff(source, target):
    return [{'source_path': PRODUCTION + '/' + n,
             'action': 'add' if n not in source else 'remove' if n not in target else 'unchanged' if source[n] == target[n] else 'replace',
             'source_sha256': source.get(n), 'target_sha256': target.get(n),
             'target_bytes_path': 'view/target/' + n if n in target else None}
            for n in sorted(set(source) | set(target))]

def semantics(root, source_bytes, target_bytes):
    source, target = json.loads(source_bytes), json.loads(target_bytes)
    data = snapshot.load_source(root / KNOWLEDGE)
    history = json.loads((root / STATE / 'activation-state.json').read_bytes())
    expected_hashes = {t: snapshot.digest(data[t]) for t in snapshot.TABLES}
    checks = {'Knowledge': source['source_hashes'] == target['source_hashes'] == expected_hashes}
    def sorted_rows(rows): return sorted(rows, key=lambda r: canonical(r))
    def same(rows, derived):
        by_id = {r['id']: r for r in derived}
        return all(r == {k: by_id[r['id']].get(k) for k in r} for r in rows) and len(rows) == len(derived)
    checks['Course membership'] = same(source['courses'], target['courses']) and same(data['courses'], target['courses'])
    checks['Project metadata'] = same(source['projects'], target['projects']) and same(data['projects'], target['projects'])
    stages = [s for p in target['projects'] for s in p['stages']]
    checks['Stage requirements'] = same(source['stages'], stages) and same(data['stages'], stages)
    for edge_type, name in [('project_requires', 'Project requirements'), ('prerequisite', 'Prerequisites'), ('dependent', 'Dependents')]:
        expected = sorted_rows([e for e in data['edges'] if e['type'] == edge_type])
        actual = [e for p in target['projects'] for e in p['requirements']] if edge_type == 'project_requires' else [e for e in target['relations'] if e['type'] == edge_type]
        checks[name] = expected == sorted_rows(actual) == sorted_rows([e for e in source['edges'] if e['type'] == edge_type])
    checks['learned state'] = checks['verified state'] = sorted_rows(source['progress']['topics']) == sorted_rows(target['progress']) == sorted_rows(data['progress']['topics'])
    checks['evidence'] = sorted_rows(source['evidence']) == sorted_rows(target['evidence']) == sorted_rows(data['evidence'])
    checks['ACTIVE_HISTORY'] = target['personal'] == sorted(history['active_categories'] + history['active_topics'])
    require(all(checks.values()), 'Semantic invariance failed: ' + str(checks))
    return {'status': 'PASS', 'checks': checks, 'source_hashes': expected_hashes,
            'active_history_sha256': hashlib.sha256((root / STATE / 'activation-state.json').read_bytes()).hexdigest(),
            'presentation_generation': json.loads((root / STATE / 'layout-checkpoint.json').read_bytes())['presentation_generation'],
            'history_version': history['history_version'], 'layout_generation': history['layout_generation']}

def validate(root, manifest_path, reviewed_fingerprint, confirmation, *, _staging=False):
    require(confirmation, 'Explicit --confirm-production-replacement required')
    require(reviewed_fingerprint, 'Exact --reviewed-fingerprint required')
    path = Path(manifest_path)
    require(path.is_absolute() and path.name == 'apply-manifest.json' and path.is_file(), 'Exact absolute apply-manifest.json required')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Manifest symlink refused')
    m = json.loads(path.read_bytes())
    require(m.get('schema_version') == 1 and m.get('operation') == 'adaptive-production-replacement', 'Invalid adaptive manifest')
    body = {k: v for k, v in m.items() if k != 'manifest_fingerprint'}
    require(digest(body) == m['manifest_fingerprint'] == reviewed_fingerprint, 'Reviewed manifest fingerprint mismatch')
    require(m['destination'] == PRODUCTION and m['state_migration'] is False, 'Invalid publication boundary')
    require(identity(root) == m['source_identity'], 'Changed branch/HEAD binding')
    if not _staging: pending(root)
    require(bound_tree(root, STATE) == m['source_state'], 'Stale State binding')
    require(bound_tree(root, KNOWLEDGE) == m['source_knowledge'], 'Stale Knowledge binding')
    require(implementation(root) == m['implementation'], 'Changed adaptive implementation binding')
    require(hashlib.sha256((root / REFERENCE).read_bytes()).hexdigest() == m['global_reference_sha256'], 'Changed global reference binding')
    package = files(path.parent)
    package.pop('apply-manifest.json')
    require(inventory(package) == m['package_inventory'] and digest(inventory(package)) == m['target_package_fingerprint'], 'Modified review package')
    target = files(path.parent / 'view/target')
    target_inv = inventory(target, PRODUCTION + '/')
    require(target_inv == m['target_production']['inventory'] and digest(target_inv) == m['target_production']['fingerprint'], 'Modified target package')
    source = files(path.parent / 'view/current')
    require(inventory(source, PRODUCTION + '/') == m['source_production']['inventory'], 'Modified frozen source')
    plan = diff(inventory(source), inventory(target))
    require(plan == m['production_diff'], 'File apply plan mismatch')
    require(semantics(root, source['model.json'], target['model.json']) == m['semantic_invariance'], 'Semantic invariance binding mismatch')
    actual = bound_tree(root, PRODUCTION)
    require(actual in (m['source_production'], m['target_production']), 'Stale source Production')
    return m, target, actual == m['target_production']

def apply(root, manifest_path, reviewed_fingerprint=None, confirmation=False, fault=None):
    root = Path(root).resolve()
    with transaction.lock(root, write=True):
        m, outputs, already = validate(root, manifest_path, reviewed_fingerprint, confirmation)
        if already: return {'status': 'ALREADY_APPLIED', 'applied': False, 'manifest_fingerprint': m['manifest_fingerprint']}
        def preflight():
            # Full second validation after staging, immediately before exchange.
            # Only the pending-stage check is skipped under our exclusive lock.
            second, staged_outputs, already_now = validate(root, manifest_path, reviewed_fingerprint,
                                                          confirmation, _staging=True)
            require(second == m and staged_outputs == outputs and not already_now,
                    'Source or reviewed package changed before publication')
        def verify():
            require(bound_tree(root, PRODUCTION) == m['target_production'], 'Post-publication target mismatch')
            require(bound_tree(root, STATE) == m['source_state'], 'State changed during publication')
            require(bound_tree(root, KNOWLEDGE) == m['source_knowledge'], 'Knowledge changed during publication')
        transaction.publish(root, [(root / PRODUCTION, outputs)], preflight=preflight, verify=verify,
                            journal=root / JOURNAL, fault=fault)
        return {'status': 'APPLIED', 'applied': True, 'manifest_fingerprint': m['manifest_fingerprint'],
                'target_production_fingerprint': m['target_production']['fingerprint'], 'state_knowledge_generation_history_unchanged': True}
