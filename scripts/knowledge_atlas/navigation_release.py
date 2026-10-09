"""Exact owner-approved navigation delta over the immutable V6.6 baseline."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from .adaptive_production import bound_tree, require
from .myatlas_guard import verify_release, REVIEWED_FINGERPRINT

MANIFEST = 'docs/releases/myatlas-leetcode-navigation.json'
REVIEWED_SHA = '7b9ce97b0b1d4c5ad319ac9324a3a694011fafb4b8faf70587cfa9df3b54a857'
INPUTS = [MANIFEST, 'scripts/build-myatlas-navigation.py',
          'scripts/knowledge_atlas/navigation_release.py']


def approved(root):
    root = Path(root)
    for name in INPUTS:
        path = root / name
        require(not path.is_symlink() and path.read_bytes() == subprocess.check_output(
            ['git', '-C', str(root), 'show', 'HEAD:' + name]), 'Uncommitted navigation input: ' + name)
    raw = (root / MANIFEST).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA, 'Unreviewed navigation delta')
    value = json.loads(raw)
    require(value['base_manifest_fingerprint'] == REVIEWED_FINGERPRINT, 'Wrong navigation baseline')
    require(set(value['patches']) == {'index.html', 'shell.js', 'shell.css'}, 'Unexpected navigation files')
    return value


def transform(raw, patch, reverse=False):
    before, after = (patch['after_sha256'], patch['before_sha256']) if reverse else (patch['before_sha256'], patch['after_sha256'])
    require(hashlib.sha256(raw).hexdigest() == before, 'Changed navigation input')
    text = raw.decode()
    old, new = (patch['new'], patch['old']) if reverse else (patch['old'], patch['new'])
    if old:
        require(text.count(old) == 1, 'Ambiguous navigation patch')
        text = text.replace(old, new)
    else:
        text += new
    result = text.encode()
    require(hashlib.sha256(result).hexdigest() == after, 'Unexpected navigation output')
    return result


def verify_navigation(root, site, current_head=True):
    root, site = Path(root).resolve(), Path(site).resolve()
    value = approved(root)
    # Inventory/symlink validation happens before copying the artifact.
    actual = bound_tree(site.parent, site.name)['inventory']
    runtime = json.loads((site / 'runtime-manifest.json').read_bytes())
    require(runtime.get('navigation_release') == {'manifest': MANIFEST, 'sha256': REVIEWED_SHA},
            'Missing navigation provenance')
    relative = {Path(p).relative_to(site.name).as_posix(): sha for p, sha in actual.items()}
    require(runtime['inventory'] == {p: sha for p, sha in relative.items() if p != 'runtime-manifest.json'},
            'Navigation runtime inventory mismatch')
    # Reverse ONLY the three pinned edits; run every existing V6.6 gate intact.
    # Any other asset, manifest, progress, geometry or evidence change still fails.
    with tempfile.TemporaryDirectory(prefix='myatlas-nav-check-') as folder:
        canonical = Path(folder) / 'knowledge-map'
        shutil.copytree(site, canonical)
        for name, patch in value['patches'].items():
            (canonical / name).write_bytes(transform((canonical / name).read_bytes(), patch, reverse=True))
            runtime['inventory'][name] = patch['before_sha256']
        del runtime['navigation_release']
        (canonical / 'runtime-manifest.json').write_text(json.dumps(runtime, sort_keys=True, indent=2) + '\n')
        result = verify_release(root, canonical, current_head=current_head)
    return {**result, 'navigation_release': REVIEWED_SHA, 'changed_runtime_files': sorted(value['patches'])}


def apply_navigation(root, site):
    root, site = Path(root).resolve(), Path(site).resolve()
    require(root / 'build' in site.parents and not any(p.is_symlink() for p in [site, *site.parents]),
            'Unsafe navigation build destination')
    value = approved(root)
    verify_release(root, site, current_head=True)
    # Validate all inputs before mutating the disposable build.
    edits = {name: transform((site / name).read_bytes(), patch) for name, patch in value['patches'].items()}
    runtime = json.loads((site / 'runtime-manifest.json').read_bytes())
    for name, raw in edits.items():
        (site / name).write_bytes(raw)
        runtime['inventory'][name] = hashlib.sha256(raw).hexdigest()
    runtime['navigation_release'] = {'manifest': MANIFEST, 'sha256': REVIEWED_SHA}
    (site / 'runtime-manifest.json').write_text(json.dumps(runtime, sort_keys=True, indent=2) + '\n')
    return verify_navigation(root, site)
