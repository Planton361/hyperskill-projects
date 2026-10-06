import hashlib
import json
from pathlib import Path
import subprocess
import unittest
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
class UXContracts(unittest.TestCase):
    def test_locked_master_and_protected_baseline(self):
        baseline=json.loads((BASE/'tests/ux-baseline.json').read_text())
        geometry=BASE/'generated/global-geometry.json'
        self.assertEqual(hashlib.sha256(geometry.read_bytes()).hexdigest(),baseline['geometry_sha256'])
        self.assertEqual(json.loads(geometry.read_text())['geometry_fingerprint'],baseline['geometry_fingerprint'])
        current={str(p.relative_to(ROOT)) for folder in ('docs/knowledge-map','state/knowledge-atlas','data/knowledge') for p in (ROOT/folder).rglob('*') if p.is_file()}
        self.assertEqual(current,set(baseline['protected']))
        for name,expected in baseline['protected'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected,name)
    def test_presentation_helpers(self):subprocess.run(['node',str(BASE/'tests/ux.cjs')],check=True)
