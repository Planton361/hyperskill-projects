#!/usr/bin/env python3
"""Package only committed legacy redirects; never bundle MyAtlas source or data."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
OUT = ROOT / 'build/pages'
FILES = {'.nojekyll', 'index.html', 'redirect.js', 'knowledge-map/index.html',
         'knowledge-map/global.html', 'leetcode-atlas/index.html', 'leetcode-progress/index.html'}
actual = {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*') if p.is_file()}
if actual != FILES or any(p.is_symlink() for p in SOURCE.rglob('*')):
    raise SystemExit('Unexpected redirect assets')
for name in ['scripts/build-redirects.py', *('site/' + f for f in sorted(FILES))]:
    if (ROOT / name).read_bytes() != subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name]):
        raise SystemExit('Uncommitted redirect input')
if any(p.is_symlink() for p in [OUT, *OUT.parents]):
    raise SystemExit('Unsafe redirect build destination')
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SOURCE, OUT)
print('Packaged 7 redirect-only Pages files; no Atlas runtime or catalog.')
