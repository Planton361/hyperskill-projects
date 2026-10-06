"""Independent source/regression audit; no Knowledge or presentation writes."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import snapshot, state
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.activation import ActivationPlanner


class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot.load_source(ROOT / 'data/knowledge')
        cls.catalog = Catalog(cls.data)
        cls.cp, _ = state.read(ROOT / 'state/knowledge-atlas')
        cls.geometry = json.loads((ROOT / 'docs/knowledge-map/geometry.js').read_text().split('=', 1)[1].rstrip(';\n'))
        cls.planner = ActivationPlanner(cls.catalog, cls.cp, cls.geometry)
        cls.fixtures = json.loads((HERE / 'fixtures/scenarios.json').read_text())

    def test_global_catalog(self):
        cats = self.catalog.categories
        self.assertEqual(len(cats), 849)
        self.assertEqual(len([c for c in cats.values() if c.get('parent_id') is None]), 5)
        self.assertEqual(len(self.catalog.topics) + len(self.catalog.references), 3106)
        self.assertEqual(Counter(t['resolution'] for t in self.catalog.topics.values()), {'RESOLVED_TOPIC': 1, 'PARTIAL_TOPIC': 88})
        self.assertEqual(len(self.catalog.references), 3017)

    def test_course_8(self):
        data = self.catalog.get_course_projection(8)
        self.assertEqual((len(data['categories']), len(data['topics']), len(data['hierarchy_records'])), (46, 89, 136))
        pairs = {kind: {(e['source'], e['target']) for e in self.data['edges'] if e['type'] == kind}
                 for kind in ('prerequisite', 'dependent')}
        self.assertEqual({k: len(v) for k, v in pairs.items()}, {'prerequisite': 137, 'dependent': 137})
        p = self.planner.plan('CURRENT_COURSE', [8])
        self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')
        self.assertEqual(len(p['already_active']), 135)

    def test_project_and_personal(self):
        edges = [e for e in self.data['edges'] if e['type'] == 'project_requires' and e['source'] == 'project:113']
        self.assertEqual(len({e['target'] for e in edges}), 26)
        self.assertEqual(len({e['target'] for e in edges if e.get('stage_id') == 617}), 12)
        self.assertFalse(any(e['type'] == 'project_applies' for e in self.data['edges']))
        p = self.planner.plan('PROJECT_FOCUS', project_ids=[113])
        self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')
        topics = [r for r in self.planner.plan()['entities'] if r['entity_type'] == 'topic']
        self.assertEqual(sum(r['personal_learning'] is True for r in topics), 31)
        self.assertEqual(sum(r['personal_verification'] is True for r in topics), 12)

    def test_all_existing_files_unchanged(self):
        before = json.loads((HERE / 'reports/protected-before.json').read_text())
        after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in before}
        self.assertEqual(before, after)
        self.assertEqual(sum(p.startswith('docs/knowledge-map/') for p in before), 14)

    def test_checkpoint(self):
        self.assertEqual(self.cp['presentation_generation'], 0)
        self.assertEqual(self.cp['layout_schema_version'], 2)
        self.assertEqual(self.cp['layout_algorithm_version'], 'atlas-incremental-2')

    def test_fixture_identity_boundary(self):
        for name, fixture in self.fixtures['scenarios'].items():
            for r in fixture['display']:
                if r['type'] == 'topic':
                    self.assertTrue(r['key'].startswith('fixture-topic:'))
                    self.assertTrue(r['fixture_only'])
                    self.assertNotIn(f"topic:{r['adapter_id']}", self.catalog.topics)
                    entity = next(e for e in fixture['plan']['entities'] if e['id'] == r['key'])
                    self.assertIsNone(entity['hyperskill_id'])
                    self.assertTrue(entity['fixture_only'])
                    self.assertEqual(entity['renderability'], 'RENDERABLE')
                    self.assertIsNone(entity['personal_learning'])
                    self.assertIsNone(entity['personal_verification'])
                else:
                    self.assertEqual(r['title'], self.catalog.categories[r['key']]['title'])

    def test_known_blocked_references(self):
        rows = self.fixtures['scenarios']['blocked']['plan']['blocked_references']
        self.assertEqual({r['id'] for r in rows}, {'reference:333', 'reference:336'})
        for row in rows:
            self.assertEqual(row['structural_memberships'], ['category:428'])
            self.assertIsNone(row['title'])
            self.assertEqual(row['renderability'], 'BLOCKED_ON_METADATA')


if __name__ == '__main__':
    unittest.main()
