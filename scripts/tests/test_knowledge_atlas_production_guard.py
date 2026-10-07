"""Focused production guard contracts; every mutation uses a disposable copy."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import adaptive_production as A, snapshot
from knowledge_atlas.catalog_observation import sanitize, validate_observation
from knowledge_atlas.production_guard import MANIFEST, verify_release


def future_catalog_observation():
    """Offline synthetic evidence built by the existing sanitizer, not a parser."""
    def entry(path, payload):
        return {'startedDateTime': '2026-10-08T12:00:00.000Z',
                'request': {'method': 'GET', 'url': 'https://hyperskill.org' + path},
                'response': {'status': 200, 'content': {'mimeType': 'application/json',
                                                     'text': json.dumps(payload)}}}
    return sanitize({'log': {'entries': [
        entry('/api/topic-relations?page=1&page_size=100', {
            'meta': {'page': 1, 'has_previous': False, 'has_next': False},
            'topic-relations': [{'id': 500001, 'title': 'Synthetic domain', 'parent_id': None,
                                 'children': [500002], 'descendants': [500002]}]}),
        entry('/api/learning-activities', {'learning-activities': [
            {'topic_id': 500002, 'title': 'Synthetic catalog Topic'}]}),
    ]}})


class ProductionGuardTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        # macOS temporary paths traverse /var -> /private/var. Resolve that
        # system alias before exercising the guard's deliberate symlink ban.
        self.root = Path(temp.name).resolve()
        for folder in (A.PRODUCTION, A.STATE, A.KNOWLEDGE):
            shutil.copytree(ROOT / folder, self.root / folder)
        for name in (MANIFEST, A.REFERENCE):
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        self.manifest = json.loads((self.root / MANIFEST).read_bytes())

    def write_observation(self, name, value):
        path = self.root / A.KNOWLEDGE / 'observations' / name
        path.write_bytes(snapshot.encode(value))
        return path

    def test_current_catalog_only_addition_passes_without_writes(self):
        folders = (A.PRODUCTION, A.STATE, A.KNOWLEDGE)
        before = {f: A.bound_tree(self.root, f) for f in folders}
        manifest_bytes = (self.root / MANIFEST).read_bytes()
        result = verify_release(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['production_fingerprint'],
                         '36679d13ac5b2f9deedfd9d9ff077de3305ed6c4398a0576a10bdd2837bb1ec7')
        additions = sorted(before[A.KNOWLEDGE]['inventory'].keys()
                           - self.manifest['source_knowledge']['inventory'].keys())
        self.assertEqual(len(additions), 1)
        self.assertEqual(result['validated_catalog_only_additions'], additions)
        self.assertTrue(result['active_semantic_hashes_unchanged'])
        self.assertEqual(before, {f: A.bound_tree(self.root, f) for f in folders})
        self.assertEqual(manifest_bytes, (self.root / MANIFEST).read_bytes())

    def test_historical_release_without_additions_still_passes(self):
        historical = self.manifest['source_knowledge']['inventory']
        current = A.bound_tree(self.root, A.KNOWLEDGE)['inventory']
        for name in current.keys() - historical.keys():
            (self.root / name).unlink()
        self.assertEqual(verify_release(self.root)['validated_catalog_only_additions'], [])

    def test_future_valid_catalog_has_no_filename_whitelist(self):
        self.write_observation('another-reviewed-capture.json', future_catalog_observation())
        result = verify_release(self.root)
        self.assertEqual(len(result['validated_catalog_only_additions']), 2)

    def test_changed_historical_knowledge_is_rejected(self):
        # Even whitespace-only changes must fail the byte identity contract.
        path = self.root / A.KNOWLEDGE / 'courses.json'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'Changed historical Knowledge file'):
            verify_release(self.root)

    def test_missing_historical_knowledge_is_rejected(self):
        (self.root / A.KNOWLEDGE / 'SCHEMA.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing historical Knowledge file'):
            verify_release(self.root)

    def test_arbitrary_extras_are_rejected(self):
        # Includes files ignored by the normal observation loader.
        for relative in ('extra.json', 'observations/extra.txt',
                         'observations/nested/capture.json'):
            with self.subTest(path=relative):
                path = self.root / A.KNOWLEDGE / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(snapshot.encode(future_catalog_observation()))
                try:
                    with self.assertRaisesRegex(ValueError, 'Unexpected additional Knowledge file'):
                        verify_release(self.root)
                finally:
                    path.unlink()

    def test_invalid_catalog_observation_is_rejected(self):
        row = future_catalog_observation()
        row['topics'][0]['is_learned'] = True
        self.write_observation('invalid.json', row)
        with self.assertRaisesRegex(ValueError, 'Unexpected Topic field'):
            verify_release(self.root)

    def test_malformed_or_unknown_observation_is_rejected(self):
        path = self.root / A.KNOWLEDGE / 'observations' / 'invalid.json'
        for text in ('{', '{"observation_type":"unrecognized"}'):
            with self.subTest(text=text):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    verify_release(self.root)

    def test_personal_and_legacy_observations_are_not_catalog_only(self):
        source = snapshot.load_source(self.root / A.KNOWLEDGE)
        row = copy.deepcopy(next(iter(source['observations'].values())))
        for typed in (False, True):
            with self.subTest(typed=typed):
                if typed:
                    row['observation_type'] = 'personal_progress'
                else:
                    row.pop('observation_type', None)
                self.write_observation('personal-addition.json', row)
                with self.assertRaisesRegex(ValueError, 'not catalog-only'):
                    verify_release(self.root)

    def test_schema_valid_catalog_conflicting_with_active_identity_is_rejected(self):
        data = snapshot.load_source(self.root / A.KNOWLEDGE)
        row = copy.deepcopy(next(iter(data['catalog_observations'].values())))
        active_ids = {t['id'] for t in data['topics']}
        topic = next(t for t in row['topics'] if t['id'] in active_ids)
        topic['title'] = 'Conflicting active title'
        row['captured_at_end'] = '2026-10-08T12:00:00.000Z'
        validate_observation(row)  # Valid schema alone is insufficient.
        self.write_observation('conflicting-catalog.json', row)
        with self.assertRaisesRegex(ValueError, 'Global/active title conflict'):
            verify_release(self.root)

    def test_valid_observation_cannot_change_active_tables_through_loader(self):
        self.write_observation('future-catalog.json', future_catalog_observation())
        data = snapshot.load_source(self.root / A.KNOWLEDGE)
        # Today's loader keeps these tables isolated. Simulate a future loader
        # promotion bug to independently exercise the critical hash invariant.
        mutations = {
            'courses': lambda d: d['courses'][0]['topic_ids'].append(500002),
            'projects': lambda d: d['projects'][0].update(title='Changed project'),
            'stages': lambda d: d['stages'][0]['required_topic_ids'].append(500002),
            'edges': lambda d: d['edges'].append({'type': 'project_requires',
                                                 'source': 'project:113', 'target': 'topic:500002'}),
            'learned': lambda d: d['progress']['topics'][0].update(
                is_learned=not d['progress']['topics'][0]['is_learned']),
            'verified': lambda d: d['progress']['topics'][0].update(
                is_verified=not d['progress']['topics'][0]['is_verified']),
        }
        for name, mutate in mutations.items():
            with self.subTest(table=name):
                changed = copy.deepcopy(data)
                mutate(changed)
                with patch('knowledge_atlas.production_guard.snapshot.load_source',
                           return_value=changed):
                    with self.assertRaisesRegex(ValueError, 'Semantic inputs changed'):
                        verify_release(self.root)

    def test_production_changes_are_rejected(self):
        path = self.root / A.PRODUCTION / 'model.json'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'Changed inventory: docs/knowledge-map'):
            verify_release(self.root)

    def test_state_changes_are_rejected(self):
        path = self.root / A.STATE / 'activation-state.json'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'Changed inventory: state/knowledge-atlas'):
            verify_release(self.root)

    def test_manifest_changes_cannot_be_hidden_by_regenerating_its_fingerprint(self):
        path = self.root / MANIFEST
        m = copy.deepcopy(self.manifest)
        m['state_migration'] = True
        for recompute in (False, True):
            with self.subTest(recompute=recompute):
                if recompute:
                    m['manifest_fingerprint'] = A.digest(
                        {k: v for k, v in m.items() if k != 'manifest_fingerprint'})
                path.write_bytes(snapshot.encode(m))
                with self.assertRaisesRegex(ValueError, 'Reviewed manifest changed'):
                    verify_release(self.root)

    def test_global_reference_and_symlinks_remain_protected(self):
        path = self.root / A.REFERENCE
        before = path.read_bytes()
        path.write_bytes(before + b'\n')
        with self.assertRaisesRegex(ValueError, 'Global reference changed'):
            verify_release(self.root)
        path.write_bytes(before)
        link = self.root / A.KNOWLEDGE / 'observations' / 'linked.json'
        link.symlink_to(self.root / A.KNOWLEDGE / 'topics.json')
        with self.assertRaisesRegex(ValueError, 'Symlink file refused'):
            verify_release(self.root)


if __name__ == '__main__':
    unittest.main()
