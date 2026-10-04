"""Production packaging and publication failures, entirely in temporary trees."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from . import build, pipeline, snapshot, transaction

ROOT = Path(__file__).resolve().parents[2]


class ProductionPackaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview = ROOT / 'docs/knowledge-atlas-preview'
        data = snapshot.load_source(ROOT / 'data/knowledge')
        cp = json.loads((ROOT / 'state/knowledge-atlas/layout-checkpoint.json').read_text())
        cls.generation = cp['presentation_generation']
        # Geometry is validated by the pipeline/browser; these pure packaging
        # tests intentionally use a minimal synthetic derived geometry object.
        cls.outputs = build.artifacts(ROOT / 'prototypes/knowledge-atlas-v6', data, cp,
                                      {'nodes': []}, {})

    def package(self):
        return build.production_outputs(self.outputs, self.preview)

    def test_exact_manifest_branding_and_required_files(self):
        assets = self.package()
        manifest = json.loads(assets['release-manifest.json'])
        self.assertEqual(set(assets), set(manifest['assets']) | {'release-manifest.json'})
        self.assertEqual(len(assets), 14)
        self.assertIn(b'<title>Knowledge Atlas</title>', assets['index.html'])
        self.assertIn(b'<h1>Knowledge Atlas</h1>', assets['index.html'])
        self.assertNotIn(b'Preview', assets['index.html'])
        self.assertNotIn('update-snapshot.json', assets)
        self.assertNotIn('geometry.json', assets)
        self.assertNotIn('PREVIEW-NOTES.md', assets)
        for name, expected in manifest['assets'].items():
            self.assertEqual(hashlib.sha256(assets[name]).hexdigest(), expected)
        for key, value in [('state_schema_version', 2), ('layout_schema_version', 2),
                           ('layout_algorithm_version', 'atlas-incremental-2'), ('generation', self.generation)]:
            self.assertEqual(manifest[key], value)

    def test_stable_packaging(self):
        self.assertEqual(self.package(), self.package())

    def test_unexplained_runtime_changes_refused(self):
        for name in ('style.css', 'app.js', 'layout.js', 'index.html', 'routing.js'):
            with self.subTest(asset=name):
                altered = {**self.outputs, name: self.outputs[name] + b'\n/* unexpected */\n'}
                with self.assertRaises(ValueError):
                    build.production_outputs(altered, self.preview)

    def test_stale_or_corrupted_release_refused(self):
        assets = self.package()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            for name, content in assets.items():
                p = destination / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(content)
            build.verify_release(destination, assets)
            stale = destination / 'old-v3.js'
            stale.write_bytes(b'stale')
            with self.assertRaisesRegex(ValueError, 'stale/missing'):
                build.verify_release(destination)
            stale.unlink()
            (destination / 'app.js').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
                build.verify_release(destination)

    def test_production_cannot_bypass_review_or_migration(self):
        for flag in ('approve_review', 'rebalance', 'preview', 'bootstrap', 'migrate', 'recover'):
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'SAFE_TO_APPLY'):
                pipeline.run(ROOT, production=True, **{flag: True})


class ProductionTransactions(unittest.TestCase):
    def test_failed_joint_state_production_publication_rolls_back(self):
        for point in ('before_final_rename', 'after_publish_0', 'after_publish_1', 'final_verification'):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state, production = root / 'state/knowledge-atlas', root / 'docs/knowledge-map'
                for target in (state, production):
                    target.mkdir(parents=True)
                    (target / 'old.json').write_bytes(b'last known good\n')
                before = [transaction.inventory(p) for p in (state, production)]
                def fault(step):
                    if step == point:
                        raise ValueError('injected failure')
                def verify():
                    if point == 'final_verification':
                        raise ValueError('injected final verification failure')
                with self.assertRaisesRegex(ValueError, 'injected'):
                    transaction.publish(root, [(state, {'checkpoint.json': b'candidate'}),
                                               (production, {'index.html': b'candidate'})],
                                        fault=fault, verify=verify)
                self.assertEqual(before, [transaction.inventory(p) for p in (state, production)])
                self.assertFalse((root / 'state/.knowledge-atlas-transaction.json').exists())
                self.assertFalse(list(root.rglob('.atlas-candidate-*')))

    def test_final_verification_precedes_commit_and_removes_stale_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'docs/knowledge-map'
            target.mkdir(parents=True)
            (target / 'old-v3.js').write_bytes(b'old')
            def verify():
                self.assertEqual((target / 'index.html').read_bytes(), b'V6')
                self.assertFalse((target / 'old-v3.js').exists())
                journal = json.loads((root / 'state/.knowledge-atlas-transaction.json').read_text())
                self.assertEqual(journal['phase'], 'COMMITTING')
            transaction.publish(root, [(target, {'index.html': b'V6'})], verify=verify)
            self.assertEqual([p.name for p in target.iterdir()], ['index.html'])


if __name__ == '__main__':
    unittest.main()
