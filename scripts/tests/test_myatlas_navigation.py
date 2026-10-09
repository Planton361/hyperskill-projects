"""The navigation exception accepts exact edits and rejects broader mutations."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.knowledge_atlas.navigation_release import MANIFEST, REVIEWED_SHA, transform, verify_navigation

ROOT = Path(__file__).resolve().parents[2]


class NavigationReleaseTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.site = Path(folder.name) / 'knowledge-map'
        shutil.copytree(ROOT / 'docs/knowledge-map', self.site)
        patches = json.loads((ROOT / MANIFEST).read_bytes())['patches']
        runtime = json.loads((self.site / 'runtime-manifest.json').read_bytes())
        for name, patch in patches.items():
            original = (self.site / name).read_bytes()
            changed = transform(original, patch)
            self.assertEqual(transform(changed, patch, reverse=True), original)
            (self.site / name).write_bytes(changed)
            runtime['inventory'][name] = patch['after_sha256']
        runtime['navigation_release'] = {'manifest': MANIFEST, 'sha256': REVIEWED_SHA}
        (self.site / 'runtime-manifest.json').write_text(json.dumps(runtime))

    def test_exact_navigation_and_immutable_baseline(self):
        self.assertEqual(verify_navigation(ROOT, self.site, current_head=False)['status'], 'PASS')

    def test_changed_navigation_and_extra_asset_rejected(self):
        p = self.site / 'shell.js'
        raw = p.read_bytes()
        p.write_bytes(raw + b'// unreviewed')
        with self.assertRaises(ValueError): verify_navigation(ROOT, self.site, current_head=False)
        p.write_bytes(raw)
        (self.site / 'extra.js').write_text('unreviewed')
        with self.assertRaises(ValueError): verify_navigation(ROOT, self.site, current_head=False)

    def test_other_application_asset_and_progress_rejected(self):
        p = self.site / 'projection-adapter.js'
        raw = p.read_bytes()
        p.write_bytes(raw + b'// unreviewed')
        with self.assertRaises(ValueError): verify_navigation(ROOT, self.site, current_head=False)
        p.write_bytes(raw)
        p = self.site / 'progress.json'
        value = json.loads(p.read_bytes())
        value['global']['learned'] += 1
        p.write_text(json.dumps(value))
        with self.assertRaises(ValueError): verify_navigation(ROOT, self.site, current_head=False)

    def test_navigation_provenance_required(self):
        p = self.site / 'runtime-manifest.json'
        value = json.loads(p.read_bytes())
        del value['navigation_release']
        p.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'Missing navigation provenance'):
            verify_navigation(ROOT, self.site, current_head=False)
