"""Activation evidence, metadata gates and immutable accepted geography."""
import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import snapshot, state
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.catalog_observation import ordered_catalog
from knowledge_atlas.activation import ActivationPlanner, OUTCOMES


def protected():
    paths = []
    for folder in ('data/knowledge', 'state/knowledge-atlas', 'docs/knowledge-map',
                   'docs/knowledge-atlas-preview', 'docs/knowledge-map-preview'):
        paths.extend(p for p in (ROOT / folder).rglob('*') if p.is_file())
    paths.append(ROOT / 'README.md')
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


class ActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot.load_source(ROOT / 'data/knowledge')
        cls.cp, cls.previous = state.read(ROOT / 'state/knowledge-atlas')
        cls.geometry = json.loads((ROOT / 'docs/knowledge-map/geometry.js').read_text().split('=', 1)[1].rstrip(';\n'))
        cls.baseline = ActivationPlanner(Catalog(cls.data), cls.cp, cls.geometry)

    def synthetic(self, resolve=True, root=None):
        """Only in-memory claims. No real Course/Python membership is created."""
        data = copy.deepcopy(self.data)
        data['evidence'].append({'id': 'synthetic-explicit', 'confidence': 'explicit'})
        data['courses'].append({'id': 900000, 'title': 'Synthetic future course',
                                'topic_ids': [518, 333, 336], 'category_ids': [],
                                'project_ids': [900000], 'evidence_ids': ['synthetic-explicit'], 'status': 'completed'})
        data['projects'].append({'id': 900000, 'title': 'Synthetic future project',
                                 'evidence_ids': ['synthetic-explicit'], 'status': 'completed'})
        for i in (518, 333, 336):
            data['edges'].append({'id': f'synthetic-requires-{i}', 'type': 'project_requires',
                                  'source': 'project:900000', 'target': f'topic:{i}',
                                  'evidence_ids': ['synthetic-explicit']})
        catalog = Catalog(data)
        if resolve:
            # Future explicit Topic evidence fixture; still structurally captured ID 333.
            observation = copy.deepcopy(next(iter(data['catalog_observations'].values())))
            source_id = 'source:' + 'f' * 64
            topic = {'id': 333, 'title': 'Synthetic explicit Topic title', 'is_group': False,
                     'parent_id': 428, 'resolution': 'PARTIAL_TOPIC'}
            topic['fact_sources'] = {k: [source_id] for k in topic if k != 'resolution'}
            observation['topics'].append(topic)
            observation['source_pages'].append({'id': source_id, 'method': 'GET',
                                               'path': '/api/topics/333', 'content_type': 'application/json'})
            observation['unresolved_references'] = [r for r in observation['unresolved_references'] if r['id'] != 333]
            for r in observation['hierarchy_records']:
                if r['child_id'] == 333:
                    r['child_type'] = 'TOPIC'
            catalog = catalog.promote_reference(333, ordered_catalog(observation), 'observations/synthetic-future.json')
        if root is not None:
            # Explicit synthetic hierarchy evidence for a new-root policy fixture.
            catalog.memberships[333] = {root}
            catalog.active['edges'].append({'id': 'synthetic-hierarchy', 'type': 'hierarchy',
                                           'source': f'category:{root}', 'target': 'topic:333',
                                           'evidence_ids': ['synthetic-explicit']})
            catalog.topics['topic:333']['parent_id'] = root
        return catalog, ActivationPlanner(catalog, self.cp, self.geometry)

    def entities(self, plan):
        return {r['id']: r for r in plan['entities']}

    def test_course_8_no_change(self):
        p = self.baseline.plan('CURRENT_COURSE', [8])
        self.assertEqual(sum(k.startswith('category:') for k in p['already_active']), 46)
        self.assertEqual(sum(k.startswith('topic:') for k in p['already_active']), 89)
        self.assertEqual((p['new_categories'], p['new_topics'], p['blocked_references']), ([], [], []))
        self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')
        self.assertEqual(p['pipeline_outcome'], 'SAFE_TO_APPLY')
        self.assertFalse(p['geometry_required'])
        self.assertEqual(p['newly_activated'], [])
        self.assertEqual(p['future_displacement'], 0)
        self.assertEqual(len([e for e in self.data['edges'] if e['type'] == 'hierarchy']), 136)

    def test_project_113_no_change(self):
        p = self.baseline.plan('PROJECT_FOCUS', project_ids=[113])
        self.assertEqual(sum(k.startswith('topic:') for k in p['already_active']), 26)
        self.assertEqual(p['blocked_references'], [])
        self.assertFalse(p['geometry_required'])
        self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')
        self.assertTrue(all(r['project_reasons'] == ['project:113'] for r in p['entities'] if r['entity_type'] == 'topic'))

    def test_personal_dimensions_unchanged(self):
        p = self.baseline.plan()
        topics = [r for r in p['entities'] if r['entity_type'] == 'topic']
        self.assertEqual(sum(r['personal_learning'] is True for r in topics), 31)
        self.assertEqual(sum(r['personal_verification'] is True for r in topics), 12)
        self.assertEqual(len(topics), 89)
        failed = self.entities(p)['topic:113']
        self.assertTrue(failed['personal_learning'])
        self.assertFalse(failed['personal_verification'])
        self.assertEqual(failed['verification_statuses'], ['failed'])
        self.assertEqual(self.entities(p)['topic:1']['personal_learning'], False)
        self.assertEqual(self.entities(p)['topic:1']['presentation_activation'], 'ALREADY_ACTIVE')

    def test_multiple_reasons_with_evidence(self):
        p = self.baseline.plan()
        rows = [r for r in p['entities'] if r['course_reasons'] and r['project_reasons'] and r['personal_relevant']]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual({r['kind'] for r in row['activation_reasons']}, {'COURSE', 'PROJECT', 'PERSONAL'})
            self.assertTrue(all(r['evidence_ids'] for r in row['activation_reasons']))
        structural = [r for row in p['entities'] for r in row['activation_reasons'] if r['kind'] == 'STRUCTURAL_ANCESTOR']
        self.assertTrue(structural)
        self.assertTrue(all(r['membership_sources'] for r in structural))

    def test_synthetic_course_overlap_renderable_and_blocked(self):
        _, planner = self.synthetic()
        p = planner.plan('CURRENT_COURSE', [900000])
        rows = self.entities(p)
        self.assertEqual(rows['topic:518']['presentation_activation'], 'ALREADY_ACTIVE')
        self.assertEqual(rows['topic:333']['presentation_activation'], 'ACTIVATION_CANDIDATE')
        self.assertEqual(rows['topic:333']['resolution'], 'PARTIAL_TOPIC')
        self.assertIsNone(rows['topic:333']['personal_learning'])
        self.assertEqual(rows['reference:336']['presentation_activation'], 'BLOCKED_ON_METADATA')
        self.assertEqual(rows['reference:336']['missing_metadata'], ['topic_entity_type', 'title'])
        self.assertIsNone(rows['reference:336']['title'])
        self.assertEqual(rows['reference:336']['structural_memberships'], ['category:428'])
        self.assertNotIn('topic:336', rows)
        self.assertEqual(p['recommended_outcome'], 'METADATA_REQUIRED')
        self.assertIn('ACTIVATION_REVIEW_REQUIRED', p['conditions'])
        self.assertIsNone(p['pipeline_outcome'])
        self.assertFalse(p['presentation_mutation_permitted'])

    def test_synthetic_project_only_explicit_requirements(self):
        _, planner = self.synthetic()
        p = planner.plan('PROJECT_FOCUS', project_ids=[900000])
        rows = self.entities(p)
        self.assertEqual(set(p['seed_entities']), {'topic:518', 'topic:333', 'reference:336'})
        self.assertEqual(rows['topic:333']['project_reasons'], ['project:900000'])
        self.assertEqual(rows['topic:333']['course_reasons'], [])
        self.assertEqual(p['new_topics'], ['topic:333'])
        self.assertEqual(len(p['blocked_references']), 1)

    def test_structural_closure_no_siblings(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [333]
        p = planner.plan('CURRENT_COURSE', [900000])
        expected = set(catalog.get_catalog_ancestors(333)) | {'topic:333'}
        self.assertEqual(set(self.entities(p)), expected)
        for sibling in (335, 336, 399, 404, 418):
            self.assertNotIn(f'reference:{sibling}', self.entities(p))
        row = self.entities(p)['topic:333']
        place = row['placements'][0]
        self.assertEqual(place['nearest_active_ancestor'], 'category:1164')
        self.assertEqual(place['required_new_category_chain'][-1], 'category:428')
        self.assertEqual(place['major_branch'], 'category:1164')
        self.assertTrue(row['outside_tracked_course_membership'] is False)

    def test_multiple_structural_memberships(self):
        p = self.baseline.plan('CURRENT_COURSE', [8])
        for numeric, parents in ((36, [35, 306]), (1425, [1260, 1423])):
            row = self.entities(p)[f'topic:{numeric}']
            self.assertEqual(row['structural_memberships'], [f'category:{i}' for i in parents])
            self.assertEqual(len(row['placements']), 2)

    def test_same_root_review(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [333]
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(p['recommended_outcome'], 'ACTIVATION_REVIEW_REQUIRED')
        self.assertEqual(p['pipeline_outcome'], 'REVIEW_REQUIRED')
        self.assertEqual(p['new_roots'], [])
        self.assertEqual(p['planning_displacement'], {'categories': 0, 'topics': 0})
        self.assertIsNone(p['future_displacement'])

    def test_every_new_root_requires_rebalance(self):
        for root in (525, 2148, 3051, 4055):
            with self.subTest(root=root):
                catalog, planner = self.synthetic(root=root)
                catalog.active['courses'][-1]['topic_ids'] = [333]
                p = planner.plan('CURRENT_COURSE', [900000])
                self.assertEqual(p['recommended_outcome'], 'ACTIVATION_REBALANCE_REQUIRED')
                self.assertEqual(p['pipeline_outcome'], 'REBALANCE_REQUIRED')
                self.assertEqual(p['new_roots'], [f'category:{root}'])

    def test_metadata_precedence_over_new_root(self):
        catalog, planner = self.synthetic(root=525)
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(p['conditions'], ['METADATA_REQUIRED', 'ACTIVATION_REBALANCE_REQUIRED'])
        self.assertEqual(p['recommended_outcome'], 'METADATA_REQUIRED')

    def test_minimum_contract_independent_of_full_topic_details(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [333]
        self.assertEqual(planner.plan('CURRENT_COURSE', [900000])['new_topics'], ['topic:333'])
        catalog.topics['topic:333']['title'] = ''
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(p['blocked_references'][0]['missing_metadata'], ['title'])
        catalog.topics['topic:333']['title'] = 'Synthetic title'
        catalog.memberships[333] = set()
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(p['blocked_references'][0]['missing_metadata'], ['structural_membership'])

    def test_unknown_ids_blocked_not_invented(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [999999]
        row = planner.plan('CURRENT_COURSE', [900000])['blocked_references'][0]
        self.assertEqual(row['catalog_status'], 'UNKNOWN')
        self.assertEqual(row['missing_metadata'], ['topic_entity_type', 'title', 'structural_membership'])
        self.assertIsNone(row['title'])

    def test_relations_do_not_activate_endpoints(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [518]
        catalog.active['edges'].append({'id': 'synthetic-prerequisite', 'type': 'prerequisite',
                                       'source': 'topic:518', 'target': 'topic:333',
                                       'evidence_ids': ['synthetic-explicit']})
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertNotIn('topic:333', self.entities(p))
        self.assertIn('synthetic-prerequisite', p['relations']['deferred_until_both_endpoints_active'])
        self.assertEqual(p['relations']['relation_seeds'], [])

    def test_course_completion_does_not_remove_history(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][0]['status'] = 'completed'
        p = planner.plan()
        self.assertIn('topic:518', p['already_active'])
        self.assertIn(8, p['context']['course_ids'])
        scoped = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(len(scoped['retained_active_history']), 135)
        self.assertEqual(scoped['removed_geometry'], [])
        no_relevance = planner.plan(course_ids=[], project_ids=[], include_personal=False)
        self.assertEqual(len(no_relevance['already_active']), 135)
        self.assertTrue(all(r['relevance'] == 'DORMANT' and r['presentation_history'] == 'ACTIVE_HISTORY'
                            for r in no_relevance['entities']))

    def test_completed_project_evidence_persists(self):
        catalog, planner = self.synthetic()
        p = planner.plan(course_ids=[], include_personal=False)
        self.assertIn('project:113', self.entities(p)['topic:112']['project_reasons'])
        self.assertIn('project:900000', self.entities(p)['topic:333']['project_reasons'])
        self.assertIsNone(self.entities(p)['topic:333']['personal_verification'])

    def test_personal_reveal_without_course_membership(self):
        catalog, planner = self.synthetic()
        catalog.active['progress']['topics'].append({'topic_id': 333, 'course_id': 900000,
                'is_learned': True, 'is_verified': False, 'verification_status': 'evaluation',
                'evidence_ids': ['synthetic-explicit']})
        p = planner.plan(course_ids=[], project_ids=[])
        row = self.entities(p)['topic:333']
        self.assertTrue(row['personal_relevant'])
        self.assertEqual(row['course_reasons'], [])
        self.assertEqual(row['project_reasons'], [])
        self.assertEqual(row['presentation_activation'], 'ACTIVATION_CANDIDATE')

    def test_verified_relevance_does_not_infer_learning(self):
        catalog, planner = self.synthetic()
        catalog.active['progress']['topics'].append({'topic_id': 333, 'course_id': 900000,
                'is_learned': None, 'is_verified': True, 'verification_status': 'verified',
                'evidence_ids': ['synthetic-explicit']})
        row = self.entities(planner.plan(course_ids=[], project_ids=[]))['topic:333']
        self.assertTrue(row['personal_relevant'])
        self.assertTrue(row['personal_verification'])
        self.assertIsNone(row['personal_learning'])

    def test_project_reveal_outside_tracked_courses_is_explicit(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'] = [c for c in catalog.active['courses'] if c['id'] != 900000]
        row = self.entities(planner.plan('PROJECT_FOCUS', project_ids=[900000]))['topic:333']
        self.assertTrue(row['outside_tracked_course_membership'])
        self.assertEqual(row['project_reasons'], ['project:900000'])

    def test_reference_promotion_retains_structural_history(self):
        catalog, planner = self.synthetic()
        row = self.entities(planner.plan('CURRENT_COURSE', [900000]))['topic:333']
        self.assertEqual(row['structural_memberships'], ['category:428'])
        self.assertTrue(catalog.reference_history[333])
        self.assertEqual(catalog.fact_history['topic:333'][-1]['observation'], 'observations/synthetic-future.json')
        self.assertNotIn(333, catalog.references)
        self.assertEqual(self.baseline.catalog.get_resolution_status(333), 'UNRESOLVED_REFERENCE')

    def test_scope_query_preserves_accepted_history(self):
        row = self.baseline.get_entity_status('topic:1', mode='PROJECT_FOCUS', project_ids=[380])
        self.assertEqual(row['relevance'], 'DORMANT')
        self.assertEqual(row['presentation_history'], 'ACTIVE_HISTORY')
        self.assertEqual(row['presentation_activation'], 'ALREADY_ACTIVE')

    def test_personal_numeric_truth_is_rejected(self):
        catalog, planner = self.synthetic()
        catalog.active['progress']['topics'][0]['is_learned'] = 1
        with self.assertRaisesRegex(ValueError, 'explicit booleans'):
            planner.plan()

    def test_category_seed_does_not_activate_descendants(self):
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1].update(topic_ids=[], category_ids=[428])
        p = planner.plan('CURRENT_COURSE', [900000])
        self.assertEqual(p['new_topics'], [])
        self.assertEqual(p['blocked_references'], [])
        self.assertIn('category:428', p['new_categories'])

    def test_explicit_project_evidence_required(self):
        catalog, planner = self.synthetic()
        edge = next(e for e in catalog.active['edges'] if e['id'] == 'synthetic-requires-333')
        edge['evidence_ids'] = []
        with self.assertRaisesRegex(ValueError, 'explicit evidence'):
            planner.plan('PROJECT_FOCUS', project_ids=[900000])

    def test_project_catalog_and_completion_are_not_requirements(self):
        p = self.baseline.plan('PROJECT_FOCUS', project_ids=[380])
        self.assertEqual(p['seed_entities'], [])
        self.assertEqual(p['new_topics'], [])
        self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')

    def test_stage_requirement_mismatch_is_rejected(self):
        catalog, planner = self.synthetic()
        edge = next(e for e in catalog.active['edges'] if e['id'] == 'synthetic-requires-333')
        edge['stage_id'] = 617  # Stage belongs to Project 113, not the synthetic Project.
        with self.assertRaisesRegex(ValueError, 'Stage evidence'):
            planner.plan('PROJECT_FOCUS', project_ids=[900000])

    def test_dormant_global_entities(self):
        for key in ('category:331', 'category:209', 'category:525', 'category:4055', 'reference:333'):
            row = self.baseline.get_entity_status(key)
            self.assertEqual(row['catalog_status'], 'CATALOG_KNOWN')
            self.assertEqual(row['relevance'], 'DORMANT')
            self.assertEqual(row['presentation_activation'], 'DORMANT')

    def test_order_independence_and_unique_global_identities(self):
        catalog, planner = self.synthetic()
        expected = snapshot.encode(planner.plan())
        randomizer = random.Random(42)
        for table in ('courses', 'projects', 'edges', 'evidence'):
            randomizer.shuffle(catalog.active[table])
        for row in catalog.active['courses']:
            for field in ('topic_ids', 'category_ids', 'project_ids', 'evidence_ids'):
                randomizer.shuffle(row[field])
        randomizer.shuffle(catalog.active['progress']['topics'])
        actual = snapshot.encode(planner.plan())
        self.assertEqual(actual, expected)
        self.assertEqual(snapshot.encode(planner.plan()), expected)
        ids = [r['id'] for r in planner.plan()['entities']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_planning_does_not_mutate_inputs_or_write(self):
        catalog, planner = self.synthetic()
        before = copy.deepcopy((catalog.__dict__, self.cp, self.geometry))
        with patch('pathlib.Path.write_text', side_effect=AssertionError('write')), \
             patch('pathlib.Path.write_bytes', side_effect=AssertionError('write')):
            planner.plan()
        self.assertEqual((catalog.__dict__, self.cp, self.geometry), before)

    def test_cli_read_only_production_state_and_generation(self):
        before = protected()
        for args in (['--course', '8'], ['--project', '113'], []):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/plan-knowledge-atlas-activation.py'),
                                     *args, '--json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            p = json.loads(result.stdout)
            self.assertEqual(p['accepted_presentation']['generation'], 0)
            self.assertEqual(p['accepted_presentation']['checkpoint_fingerprint'], self.previous['checkpoint_fingerprint'])
            self.assertEqual(p['accepted_presentation']['geometry_fingerprint'], self.previous['geometry_fingerprint'])
            self.assertEqual(p['recommended_outcome'], 'NO_CHANGE')
        self.assertEqual(protected(), before)

    def test_global_and_semantic_regression(self):
        catalog = self.baseline.catalog
        self.assertEqual((len(catalog.categories), len(catalog.topics), len(catalog.references)), (849, 89, 3017))
        self.assertEqual(len(catalog.snapshot_positions['leaves']), 3106)
        self.assertEqual(sum(not catalog.memberships.get(r['id']) for r in catalog.categories.values()), 5)
        self.assertEqual(sum(t['resolution'] == 'RESOLVED_TOPIC' for t in catalog.topics.values()), 1)
        self.assertEqual(sum(t['resolution'] == 'PARTIAL_TOPIC' for t in catalog.topics.values()), 88)
        for kind in ('prerequisite', 'dependent'):
            self.assertEqual(len({(e['source'], e['target']) for e in self.data['edges'] if e['type'] == kind}), 137)
        stage = next(s for s in self.data['stages'] if s['project_id'] == 113 and s['position'] == 4)
        self.assertEqual(len(stage['required_topic_ids']), 12)
        self.assertFalse(any(e['type'] == 'project_applies' for e in self.data['edges']))

    def test_invalid_context_identity_geometry_and_structural_graph(self):
        for kwargs in ({'mode': 'UNKNOWN'}, {'mode': 'CURRENT_COURSE', 'course_ids': []},
                       {'mode': 'PROJECT_FOCUS', 'project_ids': [999999]}):
            with self.assertRaises(ValueError): self.baseline.plan(**kwargs)
        catalog, planner = self.synthetic()
        catalog.active['courses'][-1]['topic_ids'] = [428]
        with self.assertRaisesRegex(ValueError, 'explicit Category'): planner.plan('CURRENT_COURSE', [900000])
        catalog.active['courses'][-1]['topic_ids'] = [333]
        catalog.memberships[428] = {428}
        with self.assertRaisesRegex(ValueError, 'Cycle'): planner.plan('CURRENT_COURSE', [900000])
        geometry = copy.deepcopy(self.geometry)
        geometry['nodes'].pop()
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            ActivationPlanner(self.baseline.catalog, self.cp, geometry)

    def test_outcome_mapping_is_unambiguous(self):
        self.assertEqual(OUTCOMES, {'NO_CHANGE': 'SAFE_TO_APPLY',
            'ACTIVATION_REVIEW_REQUIRED': 'REVIEW_REQUIRED',
            'ACTIVATION_REBALANCE_REQUIRED': 'REBALANCE_REQUIRED', 'METADATA_REQUIRED': None})


if __name__ == '__main__':
    unittest.main()
