"""Focused immutable relation ingestion, exact semantics and Production isolation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from knowledge_atlas import snapshot
from knowledge_atlas.catalog import Catalog, active_projection
from knowledge_atlas.scope_relations import validate_observation, write_immutable, ScopeRelationCatalog
from knowledge_atlas.production_guard import verify_release, MANIFEST


class ScopeRelationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot.load_source(ROOT/'data/knowledge')
        cls.catalog = Catalog(cls.data)
        cls.relations = cls.catalog.scope_relations
        cls.o = cls.relations.observation

    def test_complete_normalized_counts_and_global_join(self):
        r = self.relations
        self.assertEqual((len(r.courses),len(r.projects),len(r.stages)),(52,391,1967))
        self.assertEqual(sum(len(c['topic_ids']) for c in r.courses.values()),8195)
        self.assertEqual(sum(len(c['category_ids']) for c in r.courses.values()),3960)
        self.assertEqual(sum(len(p['topic_ids'] or []) for p in r.projects.values()),28480)
        self.assertEqual(sum(len(s['prerequisites']) for s in r.stages.values()),28865)
        self.assertEqual((len(self.catalog.categories),len(self.catalog.topics),len(self.catalog.references)),(849,3106,0))
        self.assertEqual(sum(t.get('resolution')=='RESOLVED_TOPIC' for t in self.catalog.topics.values()),3018)
        self.assertEqual(sum(t.get('resolution')=='PARTIAL_TOPIC' for t in self.catalog.topics.values()),88)
        progress = self.data['progress']['topics']
        self.assertEqual((sum(t['is_learned'] is True for t in progress),sum(t['is_verified'] is True for t in progress)),(31,12))
        validate_observation(self.o,self.catalog)

    def test_exact_accepted_fixture_sets_not_just_counts(self):
        fixtures=json.loads((ROOT/'prototypes/knowledge-atlas-scope-pyramid/scopes.json').read_bytes())
        for f in fixtures:
            actual=self.catalog.get_scope_projection(f['scope_type'],f['scope_id'])
            self.assertEqual(actual['explicit_topic_ids'],sorted(f['explicit_topic_ids']))
            self.assertEqual(actual['explicit_category_ids'],sorted(f['explicit_category_ids']))
        self.assertEqual(self.relations.projects[380]['topic_ids'],[9,14,15,27,30,31,112,113,146,147,148,193,307,518,1248])
        self.assertEqual(self.relations.projects[380]['n_last_prerequisites'],12)
        self.assertIsNone(self.relations.projects[380]['entry_prerequisite_ids'])

    def test_unknown_empty_and_opaque_relations_remain_distinct(self):
        r=self.relations
        self.assertEqual([p['id'] for p in r.projects.values() if p['project_requires_state']=='UNKNOWN'],[95,97,98,126,196,206,221,225,229,310,312,377,444,553,554,578])
        self.assertEqual([p['id'] for p in r.projects.values() if p['topic_ids']==[]],[405,454,455,462,580])
        self.assertEqual(sum(s['prerequisites']==[] for s in r.stages.values()),328)
        self.assertTrue(all(p['entry_prerequisite_ids'] is None and p['project_prerequisites_state']=='UNKNOWN' for p in r.projects.values()))
        self.assertIsNone(r.scope('project',95)['explicit_topic_ids'])
        self.assertEqual(r.scope('project',405)['explicit_topic_ids'],[])
        self.assertEqual(r.scope('stage',618)['explicit_topic_ids'],[])
        self.assertEqual(len(r.stages[617]['prerequisites']),12)
        self.assertEqual(len(r.stages[617]['all_prerequisites']),26)
        self.assertEqual(self.o['semantic_contract']['stage_all_classification'],'E')

    def test_capture_provenance_and_export_replay(self):
        sources={s['id']:s for s in self.o['source_pages']}
        self.assertEqual(len(sources),96)
        self.assertEqual(self.o['candidate']['inventory_sha256'],'3edd24dfffb842033ba1166dd75fca38804eb65dd3cf5c96859d39e7c56be43f')
        self.assertTrue(all(s['captured_at'].startswith('2026-10-07T') and s['http_status']==200 for s in sources.values()))
        self.assertTrue(all(s['source_id'] in sources for s in self.o['stages']))
        exported=json.loads((ROOT/'prototypes/knowledge-atlas-scope-pyramid/scope-index.json').read_bytes())
        self.assertEqual(exported,self.relations.index())
        self.assertEqual(exported['observation_sha256'],hashlib.sha256(snapshot.encode(self.o)).hexdigest())

    def test_immutable_replay_is_noop_and_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path,created=write_immutable(folder,self.o);self.assertTrue(created)
            before=path.read_bytes()
            same,created=write_immutable(folder,self.o);self.assertFalse(created);self.assertEqual(path,same);self.assertEqual(before,path.read_bytes())
            changed=copy.deepcopy(self.o);changed['projects'][0]['title']+=' conflict'
            with self.assertRaisesRegex(ValueError,'Conflicting immutable'):write_immutable(folder,changed)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(len(list(Path(folder).iterdir())),1)

    def test_schema_duplicates_unknown_ids_and_semantic_fabrication_rejected(self):
        mutations = [
            lambda o:o.update(geometry={}),
            lambda o:o['stages'][0].update(is_learned=True),
            lambda o:o['stages'][0]['prerequisites'].append(o['stages'][0]['prerequisites'][0]),
            lambda o:o['stages'][0]['all_prerequisites'].append(999999999),
            lambda o:next(p for p in o['projects'] if p['id']==95).update(topic_ids=[]),
            lambda o:o['projects'][0].update(entry_prerequisite_ids=[]),
            lambda o:o['courses'][0].update(title='/Users/private/account'),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                changed=copy.deepcopy(self.o);mutate(changed)
                with self.assertRaises(ValueError):validate_observation(changed,self.catalog)

    def test_active_projection_is_exactly_isolated(self):
        historical=copy.deepcopy(self.data)
        historical['catalog_observations']={k:v for k,v in historical['catalog_observations'].items() if v['observation_type']!='scope_relations_catalog'}
        self.assertEqual(active_projection(self.data),active_projection(historical))
        self.assertEqual(snapshot.index(self.data),snapshot.index(historical))
        manifest=json.loads((ROOT/MANIFEST).read_bytes())
        self.assertEqual({t:snapshot.digest(self.data[t]) for t in snapshot.TABLES},manifest['semantic_invariance']['source_hashes'])

    def test_invalid_relation_and_future_active_loader_mutation_fail_guard(self):
        # In-memory negative inputs exercise the actual release verifier without
        # writing to protected surfaces or cloning the entire repository.
        changed=copy.deepcopy(self.data)
        row=next(v for v in changed['catalog_observations'].values() if v['observation_type']=='scope_relations_catalog')
        row['stages'][0]['prerequisites'].append(999999999)
        with patch('knowledge_atlas.production_guard.snapshot.load_source',return_value=changed):
            with self.assertRaises(ValueError):verify_release(ROOT)
        mutations=[lambda d:d['courses'][0]['topic_ids'].append(999999999),lambda d:d['progress']['topics'][0].update(is_learned=not d['progress']['topics'][0]['is_learned'])]
        for mutate in mutations:
            changed=copy.deepcopy(self.data);mutate(changed)
            with patch('knowledge_atlas.production_guard.snapshot.load_source',return_value=changed):
                with self.assertRaisesRegex(ValueError,'Semantic inputs changed'):verify_release(ROOT)


if __name__=='__main__':unittest.main()
