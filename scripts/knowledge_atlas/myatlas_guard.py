"""Explicit V6.6 migration gate: frozen application, preserved evidence, Git-only progress."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from .adaptive_production import bound_tree, digest, require

MANIFEST = 'docs/releases/myatlas-v6.6.json'
REVIEWED_FINGERPRINT = '57d2cff0731ad02bd447a5efe25342d293522a123a560d78d48a04442b4103b4'
HISTORIC_FINGERPRINT = '36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7'
DYNAMIC = {'progress.json', 'runtime-manifest.json', 'release-manifest.json'}


def verify_release(root, site=None, current_head=False):
    root = Path(root).resolve()
    site = Path(site).resolve() if site else root / 'docs/knowledge-map'
    manifest = json.loads((root / MANIFEST).read_bytes())
    body = {k: v for k, v in manifest.items() if k != 'manifest_fingerprint'}
    require(digest(body) == manifest['manifest_fingerprint'] == REVIEWED_FINGERPRINT, 'Unreviewed V6.6 manifest')
    require(manifest['edition'] == 'myatlas-v6.6', 'Wrong release edition')
    actual = bound_tree(site.parent, site.name)['inventory']
    actual = {Path(p).relative_to(site.name).as_posix(): sha for p, sha in actual.items()}
    require(set(actual) == set(manifest['application_inventory']) | DYNAMIC, 'Unexpected application inventory')
    require({p: sha for p, sha in actual.items() if p not in DYNAMIC} == manifest['application_inventory'], 'Changed accepted application')
    require((site / 'release-manifest.json').read_bytes() == (root / MANIFEST).read_bytes(), 'Packaged release manifest mismatch')
    for name, sha in manifest['source_inventory'].items():
        path = root / name
        require(path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == sha, 'Changed canonical source: ' + name)
    for folder, expected in manifest['protected_evidence'].items():
        require(bound_tree(root, folder) == expected, 'Changed historical evidence: ' + folder)
    historic_path = root / 'docs/releases/knowledge-atlas-pre-v6.6-manifest.json'
    historic = json.loads(historic_path.read_bytes())
    require(digest({k: v for k,v in historic.items() if k != 'manifest_fingerprint'}) == historic['manifest_fingerprint'] == 'b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069', 'Historic release evidence changed')
    require(historic['target_production']['fingerprint'] == HISTORIC_FINGERPRINT, 'Wrong historic edition')
    for name, sha in manifest['historic_manifests'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, 'Historic manifest bytes changed')
    progress = json.loads((site / 'progress.json').read_bytes())
    ref = progress['source']['commit']
    require(len(ref) == 40 and all(c in '0123456789abcdef' for c in ref), 'Exact evidence commit required')
    subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', ref, 'HEAD'], check=True)
    if current_head:
        require(ref == subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD']).decode().strip(), 'Outdated artifact')
    expected = json.loads(subprocess.check_output([sys.executable, '-B', str(root / 'scripts/sync-project-completion.py'), '--ref', ref]))['projection']
    require(progress == expected, 'Progress not reconstructed from committed evidence')
    runtime = json.loads((site / 'runtime-manifest.json').read_bytes())
    require(runtime['source_commit'] == ref and runtime['edition'] == 'myatlas-v6.6', 'Runtime source identity mismatch')
    require(runtime['inventory'] == {p:sha for p,sha in actual.items() if p != 'runtime-manifest.json'}, 'Runtime inventory mismatch')
    for row in runtime['source_assets']:
        require(manifest['source_inventory'].get(row['source']) == row['source_sha256'], 'Unreviewed runtime source')
    return dict(status='PASS', edition='myatlas-v6.6', manifest_fingerprint=REVIEWED_FINGERPRINT,
                application_fingerprint=digest(manifest['application_inventory']), artifact_fingerprint=digest(actual),
                historic_fingerprint=HISTORIC_FINGERPRINT, evidence_commit=ref,
                historical_evidence_unchanged=True, git_progress_reproduced=True)
