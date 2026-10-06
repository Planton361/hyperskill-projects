"""Capture/check local file integrity, never an activation checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'reports/protected-before.json'


def inventory():
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths
            if p and (ROOT / p).is_file() and not p.startswith('prototypes/knowledge-atlas-activation/')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true', help='Create the ignored baseline only if absent')
    args = parser.parse_args()
    if args.capture:
        if OUT.exists():
            parser.error('Baseline exists; refusing to replace historical integrity evidence')
        OUT.write_text(json.dumps(inventory(), indent=2, sort_keys=True) + '\n')
    before = json.loads(OUT.read_text())
    if before != inventory():
        raise SystemExit('FAIL: pre-existing file inventory or bytes changed')
    print(f'PASS: {len(before)} existing files unchanged; no Production/State writes.')
