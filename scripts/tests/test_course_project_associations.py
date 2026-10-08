"""Focused association evidence, immutable replay, joins and active isolation."""
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
from knowledge_atlas.course_project_associations import TYPE, validate_observation, write_immutable
from knowledge_atlas.production_guard import verify_release, MANIFEST

EXPECTED = {
    8: [33,48,53,113,133,184,229,293,341,380,383],
    2: [68,69,73,74,78,79,80,82,90,97,98,99,105,109,112,114,127,128,136,145,146,151,155,157,159,161,162,163,173,175,208,213,258,264,268,307,326,343,351,355,378,391,549],
    3: [8,67,70,75,83,86,87,88,89,100,106,110,123,126,138,160,165,177,182,196,202,214,237,244,261,279,290,300,308,322,338,344,363,364,410,501],
}


class AssociationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot.load_source(ROOT/'data/knowledge')
        cls.catalog = Catalog(cls.data)
        cls.scopes = cls.catalog.scope_relations
        cls.identity, cls.o = next((k,v) for k,v in cls.data['catalog_observations'].items() if v['observation_type']==TYPE)

    def test_complete_counts_exact_fixtures_and_many_to_many(self):
        rows = {r['course_id']:r for r in self.o['courses']}
        self.assertEqual(len(rows),52)
        self.assertEqual([cid for cid,r in rows.items() if r['state']=='KNOWN_EMPTY'],[31,41,57,60])
        self.assertEqual(sum(r['state']=='KNOWN' for r in rows.values()),48)
        pairs = [(cid,pid) for cid,r in rows.items() for pid in r['project_ids']]
        self.assertEqual(len(pairs),867); self.assertEqual(len(set(pairs)),867)
        self.assertEqual(len({pid for _,pid in pairs}),299)
        self.assertTrue(all(pid in self.scopes.projects for _,pid in pairs))
        for cid, ids in EXPECTED.items(): self.assertEqual(rows[cid]['project_ids'],ids)
        self.assertIn(113,rows[8]['project_ids']); self.assertIn(113,rows[9]['project_ids'])
        self.assertIn(229,rows[8]['project_ids'])
        self.assertEqual(self.scopes.projects[229]['project_requires_state'],'UNKNOWN')

    def test_exact_provenance_and_composed_export(self):
        sources = {r['id']:r for r in self.o['source_pages']}
        self.assertEqual(len(sources),52)
        self.assertEqual(self.o['candidate']['inventory_sha256'],'9d60f781ca8762e818033bf0fb50ea8b36c3796d3afe4cc3191ec43da9cee360')
        for row in self.o['courses']:
            src = sources[row['source_id']]
            self.assertEqual(sorted(src['project_ids']),row['project_ids'])
            self.assertEqual(src['endpoint'],'/api/tracks/'+str(row['course_id']))
            self.assertTrue(src['captured_at'].startswith('2026-10-07T'))
            self.assertEqual(src['meta'],{'page':1,'has_next':False,'has_previous':False})
        self.assertEqual(json.loads((ROOT/'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_bytes()),self.scopes.index())
        validate_observation(self.o,self.scopes,self.data['courses'])

    def test_existing_scope_semantics_and_progress_unchanged(self):
        self.assertEqual((len(self.scopes.courses),len(self.scopes.projects),len(self.scopes.stages)),(52,391,1967))
        self.assertEqual([sum(len(r[k] or []) for r in table.values()) for table,k in
                          [(self.scopes.courses,'topic_ids'),(self.scopes.courses,'category_ids'),(self.scopes.projects,'topic_ids'),(self.scopes.stages,'prerequisites')]], [8195,3960,28480,28865])
        self.assertEqual(sum(p['project_requires_state']=='UNKNOWN' for p in self.scopes.projects.values()),16)
        self.assertEqual(sum(p['topic_ids']==[] for p in self.scopes.projects.values()),5)
        self.assertEqual(sum(s['prerequisites']==[] for s in self.scopes.stages.values()),328)
        self.assertEqual(len(self.scopes.projects[113]['topic_ids']),26)
        self.assertEqual(len(self.scopes.stages[617]['prerequisites']),12)
        self.assertEqual((len(self.catalog.categories),len(self.catalog.topics),len(self.catalog.references)),(849,3106,0))
        progress=self.data['progress']['topics']
        self.assertEqual((sum(t['is_learned'] is True for t in progress),sum(t['is_verified'] is True for t in progress)),(31,12))

    def test_replay_noop_and_valid_conflicting_inventory_stops(self):
        with tempfile.TemporaryDirectory() as folder:
            file,created=write_immutable(folder,self.o); self.assertTrue(created)
            before=file.read_bytes();same,created=write_immutable(folder,self.o)
            self.assertFalse(created);self.assertEqual(file,same);self.assertEqual(file.read_bytes(),before)
            conflict=copy.deepcopy(self.o);row=next(r for r in conflict['courses'] if r['course_id']==2)
            source=next(s for s in conflict['source_pages'] if s['id']==row['source_id'])
            row['project_ids'].remove(68);source['project_ids'].remove(68)
            source['id']='source:'+hashlib.sha256(snapshot.encode({k:v for k,v in source.items() if k!='id'})).hexdigest();row['source_id']=source['id']
            validate_observation(conflict,self.scopes,self.data['courses'])
            with self.assertRaisesRegex(ValueError,'Conflicting immutable'):write_immutable(folder,conflict)
            self.assertEqual(file.read_bytes(),before);self.assertEqual(len(list(Path(folder).iterdir())),1)

    def test_schema_provenance_coverage_and_no_fake_empty(self):
        mutations = [lambda o:o.update(geometry={}),lambda o:o['courses'].append(o['courses'][0]),
                     lambda o:o['courses'][0]['project_ids'].append(o['courses'][0]['project_ids'][0]),
                     lambda o:o['courses'][0].update(source_id='missing'),
                     lambda o:o['source_pages'][0]['meta'].update(has_next=True),
                     lambda o:o['semantic_contract'].update(response_field='projects_by_level'),
                     lambda o:o['courses'].pop(),
                     lambda o:next(r for r in o['courses'] if r['course_id']==31).update(state='UNKNOWN'),
                     lambda o:o['courses'][0].update(complete=False),
                     lambda o:o['courses'][0].update(title='not an entity table')]
        for i,mutate in enumerate(mutations):
            with self.subTest(case=i):
                o=copy.deepcopy(self.o);mutate(o)
                with self.assertRaises(ValueError):validate_observation(o,self.scopes,self.data['courses'])
        # Plausible invented source IDs still fail the exact normal-catalog join.
        o=copy.deepcopy(self.o);row=o['courses'][0];source=next(s for s in o['source_pages'] if s['id']==row['source_id'])
        row['project_ids'].append(999999999);source['project_ids'].append(999999999)
        source['id']='source:'+hashlib.sha256(snapshot.encode({k:v for k,v in source.items() if k!='id'})).hexdigest();row['source_id']=source['id']
        with self.assertRaisesRegex(ValueError,'Unknown catalog Project'):validate_observation(o,self.scopes,self.data['courses'])

    def assert_guard_rejects_bytes(self, path, payload):
        # V6.6 pins real evidence bytes rather than the historic active-loader
        # mock. Corrupt a read in memory; never write protected source evidence.
        original = Path.read_bytes
        self.assertNotEqual(original(path), payload)
        def read(candidate):
            return payload if candidate == path else original(candidate)
        with patch.object(Path, 'read_bytes', read):
            with self.assertRaisesRegex(ValueError, 'Changed (historical evidence|canonical source)'):
                verify_release(ROOT)

    def test_active_boundary_and_negative_guard(self):
        before=copy.deepcopy(self.data);before['catalog_observations'].pop(self.identity)
        self.assertEqual(active_projection(self.data),active_projection(before))
        self.assertEqual(snapshot.index(self.data),snapshot.index(before))
        manifest=json.loads((ROOT/MANIFEST).read_bytes())
        self.assertEqual({t:snapshot.digest(self.data[t]) for t in snapshot.TABLES},manifest['semantic_invariance']['source_hashes'])
        bad=copy.deepcopy(self.data);bad['catalog_observations'][self.identity]['courses'][0]['project_ids'].append(999999999)
        self.assert_guard_rejects_bytes(next((ROOT/'data/knowledge/observations').glob('course-project-associations-*.json')), snapshot.encode(bad['catalog_observations'][self.identity]))
        bad=copy.deepcopy(self.data);bad['progress']['topics'][0]['is_learned']=not bad['progress']['topics'][0]['is_learned']
        self.assert_guard_rejects_bytes(ROOT/'data/knowledge/progress.json', snapshot.encode(bad['progress']))


if __name__=='__main__': unittest.main()
