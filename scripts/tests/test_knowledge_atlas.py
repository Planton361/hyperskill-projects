"""Real baseline + synthetic updates only in temporary test data/build directories."""
import copy
import json
from pathlib import Path
import sys
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_atlas import build, diff, layout_update, pipeline, snapshot, validate, state
from knowledge_atlas.classify import CONTRACTS


class AtlasUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=json.loads((ROOT/'prototypes/knowledge-atlas-v6/model.json').read_text())
        raw['observations']={name:json.loads((ROOT/'data/knowledge'/name).read_text())
                             for name in {e['snapshot_file'] for e in raw['evidence'] if e.get('snapshot_file')}}
        accepted,cp,geom=state.baseline(ROOT/'prototypes/knowledge-atlas-v6',raw)
        cls._fixture_data=snapshot.canonical(accepted)
        cls._fixture_state_bytes=state.outputs(Path('/nonexistent/atlas-fixture'),cp,state.complete(accepted,cp,geom))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='atlas-test-', dir=ROOT / 'prototypes')
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.source = self.work / 'source'
        self.output = self.work / 'build'
        self.state = self.work / 'state'
        self.state.mkdir()
        for name in ('layout-checkpoint.json','update-snapshot.json'):
            (self.state/name).write_bytes(self._fixture_state_bytes[name])
        self.data = copy.deepcopy(self._fixture_data)
        self.save()

    def save(self):
        self.source.mkdir(exist_ok=True)
        for table in snapshot.TABLES:
            (self.source / (table + '.json')).write_bytes(snapshot.encode(self.data[table]))
        for name, value in self.data['observations'].items():
            p = self.source / name
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(snapshot.encode(value))

    def run_update(self, mode='build', **kwargs):
        self.save()
        return pipeline.run(ROOT, self.output, self.source, mode, state=self.state, **kwargs)

    def baseline(self):
        r = self.run_update()
        self.assertEqual(r['status'], 'SAFE_TO_APPLY')
        self.assertEqual(r['diff']['change_types'], ['NO_CHANGE'])
        return r

    def files(self):
        return {p.relative_to(self.output).as_posix(): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}

    def zero(self, r, kind):
        self.assertEqual(r['status'], 'SAFE_TO_APPLY')
        self.assertIn(kind, r['diff']['change_types'])
        self.assertEqual(r['presentation']['category_displacement']['max'], 0)
        self.assertEqual(r['presentation']['topic_displacement']['max'], 0)
        self.assertFalse(r['presentation']['checkpoint_changed'])
        self.assertEqual(r['presentation']['repacked_topic_trays'], [])

    def completion(self):
        row = next(p for p in self.data['progress']['projects'] if p['project_id'] == 380)
        row['status'] = 'completed'
        course = self.data['progress']['courses'][0]
        course['active_project'] = None
        course['completed_projects'].append(380)

    def progress(self):
        row = next(p for p in self.data['progress']['topics'] if p['is_learned'] is False)
        row.update(is_learned=True, is_completed=True, is_verified=True, verification_status='verified')
        observation = next(iter(self.data['observations'].values()))
        observed = next(p for p in observation['topics'] if p['topic_id'] == row['topic_id'])
        observed.update(is_learned=True, is_completed=True, verification_status='verified')
        observation['learned_topics_count'] += 1
        observation['learned_topic_ids'].append(row['topic_id'])
        observation['learned_topic_ids'].sort()
        course = self.data['progress']['courses'][0]
        course['learned_topics_count'] += 1
        course['learned_topic_ids'].append(row['topic_id'])
        course['learned_topic_ids'].sort()
        course['verified_topic_ids'].append(row['topic_id'])
        course['verified_topic_ids'].sort()

    def relation(self):
        existing = {(e['source'], e['target']) for e in self.data['edges'] if e['type'] in ('prerequisite', 'dependent')}
        for a in self.data['topics']:
            for b in reversed(self.data['topics']):
                pair = (f"topic:{a['id']}", f"topic:{b['id']}")
                if a != b and pair not in existing:
                    self.data['edges'].append({'id': 'synthetic-relation', 'type': 'prerequisite',
                       'source': pair[0], 'target': pair[1], 'evidence_ids': ['map-8']})
                    return

    def topics(self, count=3, parent=None, first=90001):
        if parent is None: parent = next(c['id'] for c in self.data['categories'] if c['title'] == 'Basics')
        for i in range(count):
            self.data['topics'].append({'id': first+i, 'title': 'Synthetic topic ' + str(i),
                'canonical_parent_id': parent, 'url': 'https://hyperskill.org/', 'evidence_ids': ['map-8']})
            self.data['edges'].append({'id': 'synthetic-hierarchy-' + str(first+i), 'type': 'hierarchy',
                'source': f'category:{parent}', 'target': f'topic:{first+i}', 'evidence_ids': ['map-8']})

    def category(self):
        parent = next(c['id'] for c in self.data['categories'] if c['title'] == 'Java')
        self.data['categories'].append({'id': 90000, 'title': 'Synthetic category', 'canonical_parent_id': parent,
                                      'url': 'https://hyperskill.org/', 'evidence_ids': ['map-8']})
        self.data['edges'].append({'id': 'synthetic-category', 'type': 'hierarchy', 'source': f'category:{parent}',
                                  'target': 'category:90000', 'evidence_ids': ['map-8']})

    def project(self, with_stage=True):
        ids = [self.data['topics'][0]['id'], self.data['topics'][1]['id']]
        self.data['projects'].append({'id': 99000, 'title': 'Synthetic project', 'language': 'java',
            'stage_ids': [99001] if with_stage else [], 'url': 'https://hyperskill.org/', 'evidence_ids': ['map-8']})
        if with_stage:
            self.data['stages'].append({'id': 99001, 'title': 'Synthetic stage', 'position': 1,
               'project_id': 99000, 'required_topic_ids': ids, 'cumulative_required_topic_ids': ids, 'evidence_ids': ['map-8']})
        for topic in ids:
            e = {'id': 'synthetic-requires-' + str(topic), 'type': 'project_requires', 'source': 'project:99000',
                 'target': f'topic:{topic}', 'evidence_ids': ['map-8']}
            if with_stage: e['stage_id'] = 99001
            self.data['edges'].append(e)

    def course(self, topics=None):
        ids = topics or [self.data['topics'][0]['id']]
        self.data['courses'].append({'id': 99000 + len(self.data['courses']), 'title': 'Synthetic course',
            'topic_ids': ids, 'category_ids': [], 'project_ids': [], 'topics_count': len(ids),
            'capstone_topics_count': 0, 'url': 'https://hyperskill.org/', 'evidence_ids': ['map-8']})

    def test_baseline_idempotency_and_check(self):
        self.baseline()
        accepted=json.loads((ROOT/'scripts/knowledge_atlas/fixtures/accepted-v6-geometry.json').read_text())['coordinates']
        built=json.loads((self.output/'geometry.json').read_text())['nodes']
        self.assertEqual(sorted(accepted),sorted([n['key'],n['x'],n['y'],n['width'],n['height']] for n in built))
        before = self.files()
        self.assertEqual(self.run_update()['diff']['change_types'], ['NO_CHANGE'])
        self.assertEqual(self.files(), before)
        self.assertEqual(self.run_update('check')['status'], 'SAFE_TO_APPLY')
        self.assertEqual(self.files(), before)

    def test_project_completion_zero(self):
        self.baseline(); self.completion()
        r = self.run_update(); self.zero(r, 'PROJECT_STATE_ONLY')
        self.assertEqual(r['diff']['projects']['completed'], [380])

    def test_progress_zero(self):
        self.baseline(); self.progress(); self.zero(self.run_update(), 'PROGRESS_ONLY')

    def test_relation_zero(self):
        self.baseline(); self.relation(); self.zero(self.run_update(), 'RELATION_ONLY')

    def test_new_project_zero_and_evidence(self):
        self.baseline(); self.project()
        self.zero(self.run_update(), 'NEW_PROJECT')
        raw = json.loads((self.output / 'model.json').read_text())
        self.assertEqual(raw['indexes']['projects']['99000']['required_topic_ids'], [1, 2])
        self.assertFalse(any(e['type'] == 'project_applies' for e in raw['edges']))

    def test_project_evidence_only_and_completed_stages_zero(self):
        self.baseline()
        row=next(p for p in self.data['progress']['projects'] if p['project_id']==380)
        row['status']='completed'
        # Use the actual public Project 380 inventory; never infer a stage completion.
        row['completed_stage_ids']=[next(p for p in self.data['projects'] if p['id']==380)['stage_ids'][0]]
        self.completion()
        self.zero(self.run_update(),'PROJECT_STATE_ONLY')
        self.data['edges'].append({'id':'synthetic-project-380-requires','type':'project_requires',
               'source':'project:380','target':'topic:1','evidence_ids':['map-8']})
        self.zero(self.run_update(),'PROJECT_EVIDENCE_ONLY')

    def test_stage_state_only_zero(self):
        self.baseline(); self.data['stages'][0]['status']='completed'
        self.zero(self.run_update(),'PROJECT_STATE_ONLY')

    def test_removed_topic_and_category_retain_survivors(self):
        self.baseline(); self.category(); self.topics(1,90000); self.run_update(approve_review=True)
        self.data['topics']=[t for t in self.data['topics'] if t['id']!=90001]
        self.data['edges']=[e for e in self.data['edges'] if e['target']!='topic:90001']
        r=self.run_update(); self.assertEqual(r['status'],'SAFE_TO_APPLY'); self.assertIn('REMOVED_TOPIC',r['diff']['change_types'])
        self.assertEqual(r['presentation']['category_displacement']['max'],0)
        self.data['categories']=[c for c in self.data['categories'] if c['id']!=90000]
        self.data['edges']=[e for e in self.data['edges'] if e['target']!='category:90000']
        r=self.run_update(); self.assertEqual(r['status'],'SAFE_TO_APPLY'); self.assertIn('REMOVED_CATEGORY',r['diff']['change_types'])
        self.assertEqual(r['presentation']['category_displacement']['max'],0)

    def test_layout_versions_classified(self):
        before=snapshot.index(self.data); after=copy.deepcopy(before)
        after['layout_schema_version']=999; after['layout_algorithm_version']='next'
        types=diff.compare(before,after)['change_types']
        self.assertIn('LAYOUT_SCHEMA_CHANGE',types); self.assertIn('LAYOUT_ALGORITHM_CHANGE',types)

    def test_title_change_requires_review(self):
        self.baseline(); self.data['topics'][0]['title']='Changed title'
        before=self.files(); r=self.run_update()
        self.assertEqual(r['status'],'REVIEW_REQUIRED'); self.assertEqual(before,self.files())

    def test_direct_requirements_without_loaded_stages(self):
        self.baseline(); self.project(False); self.zero(self.run_update(), 'PROJECT_EVIDENCE_ONLY')
        raw = json.loads((self.output / 'model.json').read_text())
        self.assertTrue(raw['indexes']['projects']['99000']['requirements_loaded'])

    def test_new_course_existing_topics_zero(self):
        self.baseline(); self.course(); self.zero(self.run_update(), 'NEW_COURSE')
        raw = json.loads((self.output / 'model.json').read_text())
        self.assertEqual(len(raw['topics']), 89)
        self.assertEqual(raw['indexes']['topic_courses']['1'], [8, 99001])

    def test_membership_zero(self):
        self.baseline(); self.course(); self.run_update()
        self.data['courses'][-1]['topic_ids'].append(2)
        self.data['courses'][-1]['topics_count'] += 1
        self.zero(self.run_update(), 'COURSE_MEMBERSHIP_ONLY')

    def test_topic_local_growth(self):
        self.baseline(); self.topics()
        r = self.run_update(); self.assertEqual(r['status'], 'REBALANCE_REQUIRED')
        self.assertFalse(r['applied'])
        self.assertLessEqual(r['presentation']['category_displacement']['max'], 384)
        self.assertLessEqual(r['presentation']['topic_displacement']['max'], 384)
        self.assertEqual(len(r['presentation']['repacked_topic_trays']), 1)

    def test_existing_tray_append_preserves_rows(self):
        self.baseline()
        parent = next(c['id'] for c in self.data['categories'] if c['title'] == 'JVM basics')
        before = json.loads((self.output / 'geometry.json').read_text())
        self.topics(3, parent)
        r = self.run_update()
        self.assertEqual(r['status'], 'SAFE_TO_APPLY')
        self.assertEqual(r['presentation']['category_displacement']['max'], 0)
        self.assertEqual(r['presentation']['topic_displacement']['max'], 0)
        after = json.loads((self.output / 'geometry.json').read_text())
        old = {n['key']: n for n in before['nodes']}
        for n in after['nodes']:
            if n['key'] in old: self.assertEqual(n, old[n['key']])

    def test_category_local_growth(self):
        self.baseline(); self.category()
        r = self.run_update(); self.assertEqual(r['status'], 'REVIEW_REQUIRED')
        r = self.run_update(approve_review=True); self.assertTrue(r['applied'])
        cp = json.loads((self.output / 'layout-checkpoint.json').read_text())
        java = next(c['id'] for c in self.data['categories'] if c['title'] == 'Java')
        self.assertEqual(cp['categories'][f'category:{java}']['sibling_order'][-1], 'category:90000')

    def test_reparent_stops_and_explicit_rebalance(self):
        self.baseline()
        row = next(c for c in self.data['categories'] if c['title'] == 'Basics')
        old = row['canonical_parent_id']; row['canonical_parent_id'] = 1162
        next(e for e in self.data['edges'] if e['type']=='hierarchy' and e['target']==f"category:{row['id']}" and
             e['source']==f'category:{old}')['source']='category:1162'
        before = self.files()
        r = self.run_update(); self.assertEqual(r['status'], 'REBALANCE_REQUIRED')
        self.assertIn('REPARENT_CATEGORY', r['diff']['change_types']); self.assertEqual(before, self.files())
        r = self.run_update(rebalance=True); self.assertTrue(r['applied'])
        self.assertTrue(r['presentation']['explicit_rebalance'])

    def test_overflow_budget_stops_before_writes(self):
        self.baseline()
        # Wide new lateral tray under a left-hand subtree forces geography propagation.
        parent = next(c['id'] for c in self.data['categories'] if c['title'] == 'JVM basics')
        self.topics(2, parent)
        for t in self.data['topics'][-2:]: t['title'] = 'W' * 200
        before = self.files()
        r = self.run_update(); self.assertEqual(r['status'], 'REBALANCE_REQUIRED')
        self.assertGreater(r['estimated_displacement'], 240); self.assertEqual(self.files(), before)

    def test_dry_run_no_writes_and_stale_check(self):
        self.baseline(); before = self.files(); self.completion()
        self.zero(self.run_update('dry-run'), 'PROJECT_STATE_ONLY'); self.assertEqual(before, self.files())
        with self.assertRaisesRegex(ValueError, 'STATE_OUT_OF_DATE'): self.run_update('check')
        self.assertEqual(before, self.files())

    def test_reversed_input_identical(self):
        self.baseline(); before = self.files()
        def reverse(x):
            if isinstance(x, dict): return {k: reverse(v) for k, v in reversed(list(x.items()))}
            if isinstance(x, list): return [reverse(v) for v in reversed(x)]
            return x
        self.data = reverse(self.data)
        self.assertEqual(self.run_update()['diff']['change_types'], ['NO_CHANGE'])
        self.assertEqual(before, self.files())

    def test_structural_reversed_input_and_repeat(self):
        self.topics(3,next(c['id'] for c in self.data['categories'] if c['title']=='JVM basics'))
        self.category(); self.course()
        r=self.run_update(approve_review=True); self.assertTrue(r['applied']); original=self.files()
        def reverse(x):
            if isinstance(x,dict): return {k:reverse(v) for k,v in reversed(list(x.items()))}
            if isinstance(x,list): return [reverse(v) for v in reversed(x)]
            return x
        self.data=reverse(self.data); self.save()
        other=self.work/'reversed-build'
        (self.work/'other-state').mkdir()
        for name,content in self._fixture_state_bytes.items():(self.work/'other-state'/name).write_bytes(content)
        r=pipeline.run(ROOT,other,self.source,state=self.work/'other-state',approve_review=True); self.assertTrue(r['applied'])
        self.assertEqual(original,{p.relative_to(other).as_posix():p.read_bytes() for p in other.rglob('*') if p.is_file()})
        self.assertEqual(self.run_update()['diff']['change_types'],['NO_CHANGE']); self.assertEqual(original,self.files())

    def test_progress_join_across_courses(self):
        self.baseline(); self.course()
        self.data['evidence'].append({'id':'synthetic-personal','confidence':'explicit','source':'test',
            'fields':['is_learned'],'observed_on':'2026-10-04','method':'owner_provided'})
        self.data['progress']['topics'].append({'topic_id':1,'course_id':99001,'is_learned':False,
            'is_verified':False,'verification_status':'evaluation','is_skipped':False,
            'is_applied':None,'evidence_ids':['synthetic-personal']})
        self.zero(self.run_update(),'NEW_COURSE')
        raw=json.loads((self.output/'model.json').read_text()); self.assertEqual(len(raw['topics']),89)

    def test_dry_run_bootstrap_creates_no_files(self):
        self.save(); before={p.relative_to(self.work).as_posix():p.read_bytes() for p in self.work.rglob('*') if p.is_file()}
        r=pipeline.run(ROOT,self.output,self.source,'dry-run',state=self.state); self.assertEqual(r['status'],'SAFE_TO_APPLY')
        self.assertFalse(self.output.exists())
        self.assertEqual(before,{p.relative_to(self.work).as_posix():p.read_bytes() for p in self.work.rglob('*') if p.is_file()})

    def test_preview_packaging_includes_routes_and_no_state(self):
        self.baseline(); outputs=self.files(); packaged=build.preview_outputs(outputs)
        self.assertIn('taxonomy-relations.js',packaged); self.assertIn('geometry.js',packaged)
        self.assertNotIn('snapshot.json',packaged); self.assertNotIn('geometry.json',packaged)
        self.assertNotIn('update-report.json',packaged)
        self.assertIn(b'<title>Knowledge Atlas \xc2\xb7 Preview</title>',packaged['index.html'])

    def test_missing_parent_duplicate_cycle(self):
        for kind in ['missing', 'duplicate', 'cycle']:
            d = copy.deepcopy(self.data)
            if kind == 'missing': d['topics'][0]['canonical_parent_id'] = 999999
            if kind == 'duplicate': d['topics'].append(d['topics'][0])
            if kind == 'cycle': d['categories'][0]['canonical_parent_id'] = d['categories'][0]['id']
            with self.subTest(kind=kind), self.assertRaises(ValueError): validate.validate(d)

    def test_invalid_project_stage_relation_and_application(self):
        for kind in ['project', 'stage', 'relation', 'application']:
            d = copy.deepcopy(self.data)
            if kind == 'project': next(e for e in d['edges'] if e['type']=='project_requires')['source']='topic:1'
            if kind == 'stage': d['stages'][0]['project_id']=999999
            if kind == 'relation': next(e for e in d['edges'] if e['type']=='prerequisite')['target']='topic:999999'
            if kind == 'application': next(e for e in d['edges'] if e['type']=='project_requires')['type']='project_applies'
            with self.subTest(kind=kind), self.assertRaises(ValueError): validate.validate(d)

    def test_checkpoint_rejects_semantics_and_versions(self):
        self.baseline(); cp=json.loads((self.output/'layout-checkpoint.json').read_text())
        for key, value in [('layout_schema_version',999),('layout_algorithm_version','unknown'),('learned',True)]:
            d=copy.deepcopy(cp); d[key]=value
            with self.subTest(key=key), self.assertRaises(ValueError): validate.checkpoint(d)

    def test_tampered_state_stops(self):
        self.baseline(); (self.output/'geometry.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'integrity mismatch'): self.run_update()

    def test_sequential_real_baseline(self):
        results = [self.baseline()]
        self.completion(); results.append(self.run_update()); self.zero(results[-1], 'PROJECT_STATE_ONLY')
        self.progress(); results.append(self.run_update()); self.zero(results[-1], 'PROGRESS_ONLY')
        self.relation(); results.append(self.run_update()); self.zero(results[-1], 'RELATION_ONLY')
        self.topics(); blocked=self.run_update(); self.assertEqual(blocked['status'],'REBALANCE_REQUIRED'); results.append(self.run_update(rebalance=True)); self.assertTrue(results[-1]['applied'])
        self.category(); blocked=self.run_update(); self.assertEqual(blocked['status'],'REVIEW_REQUIRED'); results.append(self.run_update(approve_review=True)); self.assertTrue(results[-1]['applied'])
        self.project(); results.append(self.run_update()); self.zero(results[-1], 'NEW_PROJECT')
        self.course(); results.append(self.run_update()); self.zero(results[-1], 'NEW_COURSE')
        self.topics(5, 90000, 91001); self.course(list(range(91001,91006))); results.append(self.run_update())
        self.assertEqual(results[-1]['status'],'SAFE_TO_APPLY'); self.assertIn('NEW_TOPIC',results[-1]['diff']['change_types'])
        before=self.files(); self.assertEqual(self.run_update()['diff']['change_types'],['NO_CHANGE']); self.assertEqual(before,self.files())
        self.assertEqual(len(results),9)

    def test_all_required_contracts_exist(self):
        self.assertTrue({'NO_CHANGE','PROGRESS_ONLY','PROJECT_STATE_ONLY','PROJECT_EVIDENCE_ONLY','RELATION_ONLY',
          'NEW_TOPIC','REMOVED_TOPIC','NEW_CATEGORY','REMOVED_CATEGORY','REPARENT_CATEGORY','COURSE_MEMBERSHIP_ONLY',
          'NEW_COURSE','LAYOUT_SCHEMA_CHANGE','LAYOUT_ALGORITHM_CHANGE'} <= CONTRACTS.keys())


if __name__ == '__main__': unittest.main()
