"""Production V2 projection contract; fixtures are disposable roots only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('knowledge_map', ROOT / 'scripts/build-knowledge-map.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class KnowledgeMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = build.project_model()

    def test_exact_personal_snapshot(self):
        observation = build.load(ROOT / 'data/knowledge/observations/learned-2026-10-01.json')
        actual = {t['id']: t for t in self.model['topics']}
        self.assertEqual(len(actual), 89)
        self.assertEqual(sum(t['is_learned'] is True for t in actual.values()), 31)
        self.assertEqual(sum(t['is_verified'] is True for t in actual.values()), 12)
        self.assertEqual(sum(t['is_learned'] is False for t in actual.values()), 58)
        for row in observation['topics']:
            self.assertEqual(actual[row['topic_id']]['is_learned'], row['is_learned'])
            self.assertEqual(actual[row['topic_id']]['is_verified'], row['verification_status'] == 'verified')
        self.assertTrue(actual[113]['is_learned'])
        self.assertFalse(actual[113]['is_verified'])
        self.assertTrue(all(t['is_applied'] is None for t in actual.values()))
        self.assertIsNone(self.model['progress']['courses'][0]['applied_topic_ids'])

    def test_hierarchy_partition_and_source_edges_unchanged(self):
        m = self.model
        self.assertEqual(sum(d['total'] for d in m['domains']), 89)
        self.assertEqual(sum(d['learned'] for d in m['domains']), 31)
        self.assertEqual(sum(s['total'] for s in m['subdomains']), 89)
        self.assertEqual(m['edges'], build.load(ROOT / 'data/knowledge/edges.json'))
        self.assertGreater(len([e for e in m['edges'] if e['type'] == 'hierarchy' and e['target'] == 'topic:36']), 1)

    def test_connections_and_project_evidence(self):
        m = self.model
        source_ids = {e['id'] for e in m['edges']}
        keys = {t['key'] for t in m['topics']}
        self.assertEqual(len(m['connections']), 137)
        for c in m['connections']:
            self.assertIn(c['source'], keys)
            self.assertIn(c['target'], keys)
            for e in c['records']:
                self.assertIn(e['id'], source_ids)
                self.assertTrue(e['evidence_ids'])
        p = {p['id']: p for p in m['projects']}
        self.assertEqual(len(set(p[113]['required_topic_ids'])), 26)
        self.assertEqual(p[380]['completed_stage_ids'], [])
        self.assertIsNone(p[380]['required_topic_ids'])
        self.assertFalse(any(e['type'] == 'project_applies' for e in m['edges']))

    def test_bounded_production_summary_and_capability(self):
        m = self.model
        summary = build.summary(m)
        self.assertIn('31 / 89 course topics learned · 12 verified', summary)
        self.assertIn(build.PUBLIC_URL, summary)
        self.assertNotIn('For loop', summary)
        self.assertNotIn('verification_status', summary)
        self.assertLess(len(summary.splitlines()), 25)
        expanded = {**m, 'domains': [{**m['domains'][0], 'id': f'test:{i}', 'title': f'Test area {i}', 'learned': 1000} for i in range(30)]}
        area_part = build.summary(expanded).split('Knowledge areas:')[1].split('Project evidence:')[0]
        self.assertEqual(sum(line.startswith('- ') for line in area_part.splitlines()), 4)
        self.assertIn('Other areas (27)', area_part)
        cap = m['capability_evidence'][0]
        self.assertEqual((cap['learned_evidence'], cap['verified_evidence']), (4, 3))
        self.assertEqual(cap['required_topic_ids'], [25, 89, 87, 88])
        self.assertIsNone(cap['proficiency'])

    def test_deterministic_outputs_and_source_integrity(self):
        self.assertEqual(build.encode(self.model), build.encode(build.project_model()))
        build.render(check=True)
        for name, digest in self.model['source_hashes'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_rebuild_from_sources_not_existing_artifact(self):
        with tempfile.TemporaryDirectory(prefix='knowledge map sources ') as name:
            root = Path(name)
            shutil.copytree(ROOT / 'data/knowledge', root / 'data/knowledge')
            old = root / 'docs/knowledge-graph/preserved.txt'
            old.parent.mkdir(parents=True)
            old.write_text('Legacy route must remain untouched.')
            before = old.read_bytes()
            # No V2 artifact exists: generation must read normalized sources.
            self.assertFalse((root / 'docs/knowledge-map/model.json').exists())
            self.assertEqual(build.encode(build.render(root)), build.encode(self.model))
            self.assertEqual(old.read_bytes(), before)
            build.render(root, check=True)
            (root / 'docs/knowledge-map/model.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Stale generated'):
                build.render(root, check=True)
            build.render(root)
            self.assertEqual(json.loads((root / 'docs/knowledge-map/model.json').read_text())['statistics']['learned'], 31)

    def test_unmapped_taxonomy_fails_closed(self):
        original = build.load
        def read(path):
            value = original(path)
            if path.name == 'display-map.json':
                value['domains'] = []
            return value
        with patch.object(build, 'load', side_effect=read):
            with self.assertRaisesRegex(ValueError, 'Unmapped topic'):
                build.project_model()


if __name__ == '__main__':
    unittest.main()
