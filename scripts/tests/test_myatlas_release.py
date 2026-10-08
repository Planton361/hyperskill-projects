"""Focused V6.6 migration integrity tests; all corruptions use disposable artifacts."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts.knowledge_atlas.myatlas_guard import verify_release
from scripts.knowledge_atlas import myatlas_guard

ROOT = Path(__file__).resolve().parents[2]

class MyAtlasReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name) / 'knowledge-map'
        shutil.copytree(ROOT / 'docs/knowledge-map', self.site)

    def test_reviewed_migration_and_baseline(self):
        result = verify_release(ROOT, self.site)
        self.assertEqual(result['status'], 'PASS')
        p = json.loads((self.site / 'progress.json').read_text())
        self.assertEqual((p['global']['eligible'], p['global']['learned'], p['global']['verified']), (3106,31,12))
        self.assertEqual(p['completed_project_ids'], [113])
        self.assertIsNone(p['portfolio']['completed_course_count'])
        c = next(c for c in p['course_project_completion'] if c['course_id'] == 8)
        self.assertEqual((c['completed'], c['eligible']), (1,11))

    def test_changed_asset_missing_or_extra_file_rejected(self):
        target = self.site / 'index.html'
        original = target.read_bytes()
        target.write_bytes(original + b'corruption')
        with self.assertRaises(ValueError): verify_release(ROOT, self.site)
        target.write_bytes(original)
        (self.site / 'unexpected.txt').write_text('unreviewed')
        with self.assertRaises(ValueError): verify_release(ROOT, self.site)
        (self.site / 'unexpected.txt').unlink()
        target.unlink()
        with self.assertRaises(ValueError): verify_release(ROOT, self.site)

    def test_fabricated_progress_or_manifest_rejected(self):
        target = self.site / 'progress.json'
        original = target.read_bytes()
        p = json.loads(original); p['global']['learned'] += 1
        target.write_text(json.dumps(p))
        with self.assertRaises(ValueError): verify_release(ROOT, self.site)
        target.write_bytes(original)
        (self.site / 'release-manifest.json').write_text('{}')
        with self.assertRaises(ValueError): verify_release(ROOT, self.site)

    def test_historical_evidence_is_still_a_gate(self):
        original = myatlas_guard.bound_tree
        def changed(root, folder):
            result = original(root, folder)
            if folder == 'state/knowledge-atlas': result = {'inventory': {}, 'fingerprint': 'changed'}
            return result
        with patch.object(myatlas_guard, 'bound_tree', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'Changed historical evidence'): verify_release(ROOT, self.site)

    def test_stale_reference_snapshot_rejected_for_current_artifact(self):
        with self.assertRaisesRegex(ValueError, 'Outdated artifact'):
            verify_release(ROOT, self.site, current_head=True)

    def test_mismatched_source_inputs_and_runtime_provenance_rejected(self):
        target = self.site / 'progress.json'
        original = target.read_bytes()
        p = json.loads(original); p['source']['evidence'][0]['sha256'] = '0' * 64
        target.write_text(json.dumps(p))
        with self.assertRaisesRegex(ValueError, 'committed evidence'):
            verify_release(ROOT, self.site)
        target.write_bytes(original)
        target = self.site / 'runtime-manifest.json'
        p = json.loads(target.read_bytes()); p['source_input_digest'] = '0' * 64
        target.write_text(json.dumps(p))
        with self.assertRaisesRegex(ValueError, 'Source input digest mismatch'):
            verify_release(ROOT, self.site)
