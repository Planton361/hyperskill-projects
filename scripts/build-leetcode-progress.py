#!/usr/bin/env python3
"""Package only the four reviewed metadata-free assets as a sibling Pages route."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/leetcode-progress'
OUTPUT = ROOT / 'build/pages/leetcode-progress'
# Hashes of the exact summary reviewed at foundation commit 691c02146ac3bcb497c554c745c10b3f30c217f1.
ASSETS = {
    'summary.html': ('index.html', 'ee337a3702b40cd213ed516f01c2f981ab0b8fe359c1dcd110ffcd8a6e2c506c'),
    'summary.css': ('summary.css', '045a6d52145fe5d26770a5511a31d5b9fbc6ee6422dc702546883b1f6b815db5'),
    'summary.js': ('summary.js', '0e382168c0f320020eaf1d006327d546bdf8088c7ac14e687286f98870896031'),
    'loader.js': ('loader.js', 'a121d826a624661448bc8ad89feec5ba095011f9240956a33d36eb1934ef60c2'),
}


def reviewed_assets(source=SOURCE):
    if source.is_symlink() or {p.name for p in source.iterdir()} != set(ASSETS):
        raise ValueError('Unexpected summary source inventory')
    result = {}
    for name, (target, expected) in ASSETS.items():
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Unsafe summary asset: ' + name)
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Changed reviewed summary asset: ' + name)
        result[target] = raw
    return result


def build():
    # Mirror the production build's committed-source boundary without changing it.
    for name in ['scripts/build-leetcode-progress.py', *('src/leetcode-progress/' + p for p in ASSETS)]:
        committed = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name])
        if committed != (ROOT / name).read_bytes():
            raise ValueError('Uncommitted summary implementation refused: ' + name)
    assets = reviewed_assets()
    if any(p.is_symlink() for p in [OUTPUT, *OUTPUT.parents]):
        raise ValueError('Unsafe summary build destination')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for name, raw in assets.items():
        (OUTPUT / name).write_bytes(raw)
    return {'route': 'leetcode-progress/', 'catalogIncluded': False,
            'assets': {name: hashlib.sha256(raw).hexdigest() for name, raw in assets.items()}}


if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True, indent=2))
