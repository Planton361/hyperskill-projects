"""Package a read-only Production candidate; never call a Production writer."""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas.adaptive_preview import artifacts

HERE = Path(__file__).resolve().parent
PROTECTED = ['docs/knowledge-map', 'state/knowledge-atlas', 'data/knowledge',
             'prototypes/global-pyramid/generated']

def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()

def inventory(folder):
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / folder).rglob('*')) if p.is_file()}

def protected():
    return {folder: {'files': inventory(folder), 'aggregate_sha256': hashlib.sha256(
        json.dumps(inventory(folder), sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        for folder in PROTECTED}

def candidate(root=None):
    out = artifacts(ROOT if root is None else root)
    out.pop('preview-manifest.json')
    html = out['index.html'].decode().replace('Knowledge Atlas · Adaptive Preview', 'Knowledge Atlas')
    html = html.replace('Adaptive preview · Production migration paused', 'Production candidate · read-only review')
    start, end = html.index('<optgroup'), html.index('</optgroup>') + len('</optgroup>')
    html = html[:start] + html[end:]
    html = html.replace('id="mask"', 'id="mask" hidden')
    out['index.html'] = html.encode()
    out['app.js'] = out['app.js'].replace(b'Adaptive preview \xc2\xb7 Production migration paused',
                                        b'Production candidate \xc2\xb7 read-only review')
    out['release-manifest.json'] = encode({
        'target': 'isolated-production-candidate', 'deployment_path_if_approved': 'docs/knowledge-map/',
        'architecture': 'GLOBAL REFERENCE + ADAPTIVE LOCAL PYRAMID',
        'default_view': 'explicitly-learned-topics-plus-hierarchy-context',
        'local_geometry_storage': 'derived-memory-only', 'state_migration': False,
        'authorizes_apply': False,
        'assets': {n: hashlib.sha256(v).hexdigest() for n, v in sorted(out.items())}})
    return out

def write_tree(folder, files):
    folder.mkdir(parents=True, exist_ok=True)
    existing = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if existing - set(files):
        raise ValueError('Unexpected package files: ' + str(existing - set(files)))
    for name, data in files.items():
        p = folder / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

def main():
    before = protected()
    baseline = HERE / 'protected-before.json'
    if not baseline.exists():
        baseline.write_bytes(encode(before))
    assert before == json.loads(baseline.read_bytes()), 'Protected files changed since first build'
    start = time.perf_counter()
    first, repeat = candidate(), candidate()
    assert first == repeat, 'Non-deterministic target build'
    hashes = {n: hashlib.sha256(v).hexdigest() for n, v in sorted(first.items())}
    previous_result = HERE / 'build-results.json'
    same_as_previous = (json.loads(previous_result.read_bytes())['target_hashes'] == hashes
                        if previous_result.exists() else None)
    write_tree(HERE / 'target', first)
    current = {p.relative_to(ROOT / 'docs/knowledge-map').as_posix(): p.read_bytes()
               for p in (ROOT / 'docs/knowledge-map').rglob('*') if p.is_file()}
    write_tree(HERE / 'current', current)
    runtime = {'index.html', 'style.css', 'app.js', 'atlas.js', 'labels.js', 'ux.js',
               'adaptive.cjs', 'registry.cjs', 'views.cjs'}
    changes = []
    for n in sorted(set(first) | set(current)):
        action = 'add' if n not in current else 'remove' if n not in first else 'unchanged' if first[n] == current[n] else 'replace'
        category = 'global reference asset' if n == 'global-reference.json' else 'generated model/config' if n in {'model.json', 'release-manifest.json'} else 'runtime/UI' if n in runtime or n.startswith('vendor/') else 'retired legacy presentation asset'
        changes.append({'path': 'docs/knowledge-map/' + n, 'action': action, 'category': category,
                        'current_bytes': len(current.get(n, b'')), 'target_bytes': len(first.get(n, b''))})
    assert protected() == before
    result = {'status': 'PASS', 'deterministic_rebuild': True, 'build_seconds_two_builds': time.perf_counter()-start,
              'target_hashes_equal_previous_build': same_as_previous,
              'current_bytes': sum(map(len, current.values())), 'target_bytes': sum(map(len, first.values())),
              'current_files': len(current), 'target_files': len(first), 'changes': changes,
              'protected_unchanged': True, 'protected': before,
              'target_hashes': hashes}
    (HERE / 'build-results.json').write_bytes(encode(result))
    print(json.dumps({k: v for k, v in result.items() if k not in {'changes','protected','target_hashes'}}, indent=2))

if __name__ == '__main__':
    main()
