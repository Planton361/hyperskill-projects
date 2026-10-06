"""Explicit real repository identity checks; no environment or debug bypass."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_POLICY = 'marked external disposable roots or explicitly confirmed real apply'
SEAL_POLICY = 'exact-reviewed-explicit-apply'


def real_repository(root, intended_root=ROOT):
    from .architecture import require_strict_migration_approval
    require_strict_migration_approval()
    root = Path(root)
    if not root.is_absolute() or root != root.resolve() or root != Path(intended_root).resolve():
        raise ValueError('REAL_SPATIAL_MIGRATION_FORBIDDEN: unintended repository root')
    if not (root/'.git').is_dir() or (root/'.git').is_symlink() or (root/'.atlas-disposable-test').exists():
        raise ValueError('REAL_SPATIAL_MIGRATION_FORBIDDEN: real checkout identity required')
    top = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], text=True).strip()
    branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip()
    if Path(top) != root or branch != 'main':
        raise ValueError('REAL_SPATIAL_MIGRATION_FORBIDDEN: intended main checkout required')
    for name in ('state', 'docs', 'data', 'state/knowledge-atlas', 'docs/knowledge-map', 'data/knowledge'):
        if (root/name).is_symlink():
            raise ValueError('REAL_SPATIAL_MIGRATION_FORBIDDEN: destination symlink')
    return root
