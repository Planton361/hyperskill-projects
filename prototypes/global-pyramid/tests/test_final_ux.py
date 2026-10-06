import hashlib
import json
import subprocess
import unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
class FinalUX(unittest.TestCase):
    def test_frozen_geometry_bytes_hash_and_fingerprint(self):
        record=json.loads((BASE/'tests/final-ux-baseline.json').read_text());payload=(BASE/'generated/global-geometry.json').read_bytes()
        self.assertEqual(len(payload),record['geometry_bytes']);self.assertEqual(hashlib.sha256(payload).hexdigest(),record['geometry_sha256']);self.assertEqual(json.loads(payload)['geometry_fingerprint'],record['geometry_fingerprint'])
    def test_labels_and_region_metrics(self):subprocess.run(['node',str(BASE/'tests/final-labels.cjs')],check=True)

    def test_protected_production_state_and_knowledge(self):
        root=BASE.parents[1]
        record=json.loads((BASE/'tests/final-ux-baseline.json').read_text())['protected']
        current={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for directory in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge']
                 for p in (root/directory).rglob('*') if p.is_file()}
        self.assertEqual(current,record)
