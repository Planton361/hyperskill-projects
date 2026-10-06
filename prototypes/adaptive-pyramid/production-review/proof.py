"""Focused exact-operator proof; every publication is confined to TemporaryDirectory."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from knowledge_atlas import adaptive_production as A

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
REL = 'prototypes/adaptive-pyramid/production-review/final-v1'
MANIFEST = ROOT / REL / 'apply-manifest.json'

def main():
    m = json.loads(MANIFEST.read_bytes())
    protected_before = {p: A.bound_tree(ROOT, p) for p in (A.PRODUCTION, A.STATE, A.KNOWLEDGE)}
    A.validate(ROOT, MANIFEST, m['manifest_fingerprint'], True)  # Read-only; no real apply.
    result = {'manifest_fingerprint': m['manifest_fingerprint'], 'default_deny': {}}
    with tempfile.TemporaryDirectory(prefix='adaptive-production-proof-') as temp:
        root = Path(temp).resolve()
        names = set(m['implementation']['inventory'])
        for key in ('source_production', 'source_state', 'source_knowledge'):
            names.update(m[key]['inventory'])
        names.add(A.REFERENCE)
        for name in names:
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, p)
        shutil.copytree(ROOT / REL, root / REL)
        # Git identity is read from the original gitdir; no git writer is invoked.
        gitdir = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '--absolute-git-dir'], text=True).strip()
        (root / '.git').write_text('gitdir: ' + gitdir + '\n')
        path = root / REL / 'apply-manifest.json'
        token = m['manifest_fingerprint']
        base = [sys.executable, '-B', str(root / 'scripts/update-knowledge-atlas.py')]
        arguments = ['--apply-adaptive-production', str(path), '--reviewed-fingerprint', token,
                     '--confirm-production-replacement', '--json']
        original = A.inventory(A.files(root))
        def reject(name, args):
            run = subprocess.run(base + args, capture_output=True, text=True)
            assert run.returncode != 0, name
            assert A.inventory(A.files(root)) == original, name + ' wrote files'
            result['default_deny'][name] = 'PASS'
        reject('missing manifest', ['--apply-adaptive-production', str(root / 'absent/apply-manifest.json'), '--reviewed-fingerprint', token, '--confirm-production-replacement'])
        reject('missing fingerprint', ['--apply-adaptive-production', str(path), '--confirm-production-replacement'])
        reject('wrong fingerprint', ['--apply-adaptive-production', str(path), '--reviewed-fingerprint', '0'*64, '--confirm-production-replacement'])
        reject('missing confirmation', ['--apply-adaptive-production', str(path), '--reviewed-fingerprint', token])
        for label, name in [('stale Production', A.PRODUCTION+'/style.css'), ('stale State', A.STATE+'/README.md'),
                            ('stale Knowledge', A.KNOWLEDGE+'/topics.json'),
                            ('modified target', REL+'/view/target/style.css'),
                            ('changed implementation', 'scripts/knowledge_atlas/adaptive_production.py')]:
            p = root / name
            saved = p.read_bytes()
            p.write_bytes(saved + b'\n')
            changed = A.inventory(A.files(root))
            run = subprocess.run(base + arguments, capture_output=True, text=True)
            assert run.returncode != 0, label
            assert A.inventory(A.files(root)) == changed, label + ' wrote files'
            result['default_deny'][label] = 'PASS'
            p.write_bytes(saved)
        def fault(point):
            if point == 'after_candidate_write': raise ValueError('Representative failure before publication')
        try:
            A.apply(root, path, token, True, fault=fault)
            raise AssertionError('Failure injection did not fire')
        except ValueError as e:
            assert str(e) == 'Representative failure before publication', str(e)
        assert A.inventory(A.files(root)) == original
        result['failure_before_publication'] = 'PASS source unchanged; staging cleaned'
        run = subprocess.run(base + arguments, capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
        applied = json.loads(run.stdout)
        assert applied['status'] == 'APPLIED'
        after = A.inventory(A.files(root))
        changed = [n for n in sorted(set(after)|set(original)) if after.get(n) != original.get(n)]
        assert all(n.startswith(A.PRODUCTION+'/') for n in changed)
        assert len(changed) == 24
        assert A.bound_tree(root, A.PRODUCTION) == m['target_production']
        assert A.bound_tree(root, A.STATE) == m['source_state']
        assert A.bound_tree(root, A.KNOWLEDGE) == m['source_knowledge']
        result['controlled_apply'] = applied
        result['only_production_changed'] = changed
        result['state_knowledge_active_history_generation_history_unchanged'] = True
        second = subprocess.run(base + arguments, capture_output=True, text=True)
        assert second.returncode == 0, second.stdout + second.stderr
        result['second_apply'] = json.loads(second.stdout)
        assert result['second_apply']['status'] == 'ALREADY_APPLIED'
        assert A.inventory(A.files(root)) == after
        result['atomic_helper'] = 'macOS renamex_np(RENAME_SWAP), same-parent staged directory exchange'
    assert {p: A.bound_tree(ROOT, p) for p in protected_before} == protected_before
    result['real_protected_unchanged'] = True
    result['protected'] = protected_before
    result['status'] = 'PASS'
    (HERE / 'proof-results.json').write_bytes(A.canonical(result))
    print(json.dumps({k:v for k,v in result.items() if k not in ('protected','only_production_changed')}, indent=2))

if __name__ == '__main__': main()
