"""Reviewed geometry transactions run only in disposable repository copies."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas import activation_persistence as ap, snapshot, transaction, pipeline, build
FIXTURES=Path(__file__).parent/'fixtures/activation'


def adapt(value):
    text=json.dumps(value)
    for i in range(1,157):
        for scenario in ('small','large','blocked'):
            text=text.replace(f'fixture-topic:{scenario}-{i:03d}',f'topic:{900000+i}')
    return json.loads(text)


class ActivationPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='atlas-persistence-fixture-')
        cls.base=Path(cls.tmp.name)
        for name in ('data/knowledge','state/knowledge-atlas','docs/knowledge-map','docs/knowledge-atlas-preview','prototypes/knowledge-atlas-v6'):
            shutil.copytree(ROOT/name,cls.base/name,ignore=shutil.ignore_patterns('tests','build','__pycache__'))
        (cls.base/'.atlas-disposable-test').touch()
        if not (cls.base/'state/knowledge-atlas'/ap.NAME).exists(): ap.bootstrap(cls.base)
        cls.scenarios=adapt(json.loads((FIXTURES/'scenarios.json').read_text()))['scenarios']
        cls.small=cls.scenarios['small']
        # Numeric IDs are a disposable normalized-schema adapter, never Hyperskill claims.
        source=cls.base/'data/knowledge'
        data=snapshot.load_source(source)
        data['evidence'].append({'id':'fixture-only-explicit','confidence':'explicit','source':'fixture',
                                'method':'manual','fields':['id','title','canonical_parent_id'],'observed_on':'2026-10-04','url':None,'note':'DISPOSABLE TEST ONLY'})
        for row in cls.small['display']:
            kind=row['type'];numeric=int(row['key'].split(':')[1]);parent=int(row['parent'].split(':')[1])
            data['categories' if kind=='category' else 'topics'].append({'id':numeric,'title':row['title'],
                'canonical_parent_id':parent,'evidence_ids':['fixture-only-explicit'],'url':None})
            data['edges'].append({'id':'fixture-hierarchy-'+row['key'],'type':'hierarchy','source':row['parent'],
                                  'target':row['key'],'evidence_ids':['fixture-only-explicit']})
        for table in snapshot.TABLES: (source/(table+'.json')).write_bytes(snapshot.encode(data[table]))
        cls.preview=cls.base.parent/(cls.base.name+'-preview')
        ap.package_preview(cls.base,cls.preview,'centering',fixture=cls.small)
        cls.reviewed=adapt(json.loads((FIXTURES/'reviewed-centering.json').read_text()))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.preview,ignore_errors=True);cls.tmp.cleanup()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='atlas-persistence-test-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'repo';shutil.copytree(self.base,self.root)
        self.preview_dir=Path(self.tmp.name)/'preview';shutil.copytree(self.preview,self.preview_dir)
        self.manifest=self.preview_dir/'activation-manifest.json'
        self.reviewed_fingerprint=json.loads(self.manifest.read_text())['manifest_fingerprint']
        self.before={n:transaction.inventory(self.root/n) for n in ('state/knowledge-atlas','docs/knowledge-map','data/knowledge')}

    def approve(self,**kwargs):
        return ap.approve(self.root,self.manifest,reviewed_fingerprint=self.reviewed_fingerprint,test_context=self.small,**kwargs)

    def unchanged(self):
        for n,h in self.before.items(): self.assertEqual(transaction.inventory(self.root/n),h,n)

    def test_baseline_bootstrap_and_overwrite(self):
        p=self.root/'state/knowledge-atlas'/ap.NAME;p.unlink()
        checkpoint=(p.parent/'layout-checkpoint.json').read_bytes()
        prod=transaction.inventory(self.root/'docs/knowledge-map')
        first=ap.bootstrap(self.root);value=json.loads(p.read_text())
        self.assertEqual(first['generation'],0);self.assertEqual(len(value['active_categories']),46);self.assertEqual(len(value['active_topics']),89)
        self.assertEqual(p.read_bytes(),(ROOT/'state/knowledge-atlas'/ap.NAME).read_bytes());self.assertEqual(checkpoint,(p.parent/'layout-checkpoint.json').read_bytes());self.assertEqual(prod,transaction.inventory(self.root/'docs/knowledge-map'))
        with self.assertRaisesRegex(ValueError,'ALREADY_EXISTS'):ap.bootstrap(self.root)

    def test_schema_rejects_future_or_unknown_fields(self):
        value=json.loads((self.root/'state/knowledge-atlas'/ap.NAME).read_text())
        for k,v in [('schema_version',99),('hidden',True)]:
            bad={**value,k:v}
            with self.subTest(k=k),self.assertRaisesRegex(ValueError,'MIGRATION_REQUIRED'):ap.check_history(bad)

    def test_preview_exact_reviewed_bounds_and_read_only(self):
        out=Path(self.tmp.name)/'second-preview'
        ap.package_preview(self.root,out,'centering',fixture=self.small)
        for name in (*ap.FILES,'activation-manifest.json'):
            self.assertEqual((out/name).read_bytes(),(self.preview_dir/name).read_bytes())
        g=json.loads((out/'candidate-geometry.json').read_text())
        for key in ('nodes','trays','connectorSegments'):self.assertEqual(g[key],self.reviewed[key])
        self.unchanged()

    def test_plan_inventory_order_independence(self):
        p=copy.deepcopy(self.small['plan']);p['entities'].reverse();p['new_topics'].reverse()
        self.assertEqual(ap.plan_fingerprint(p),ap.plan_fingerprint(self.small['plan']))

    def test_exact_coordinates_are_hashed(self):
        g=copy.deepcopy(self.reviewed);before=ap.fingerprint(g);g['nodes'][-1]['x']+=.00000001
        self.assertNotEqual(before,ap.fingerprint(g))

    def test_stale_inputs_and_artifacts(self):
        for name in ('courses','projects','stages','progress','edges','evidence'):
            p=self.root/'data/knowledge'/(name+'.json');original=p.read_bytes();obj=json.loads(original)
            if isinstance(obj,list):obj[0]['fixture_change']=True
            else:obj['fixture_change']=True
            p.write_bytes(snapshot.encode(obj))
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):self.approve()
            p.write_bytes(original)
        for name in (*ap.FILES,'activation-manifest.json'):
            p=self.preview_dir/name;original=p.read_bytes();obj=json.loads(original);obj['changed']=True;p.write_bytes(snapshot.encode(obj))
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):self.approve()
            p.write_bytes(original)
        self.unchanged()

    def test_stale_catalog(self):
        p=next((self.root/'data/knowledge/observations').glob('global*.json'));obj=json.loads(p.read_text());obj['captured_at_end']='2026-10-04T23:00:00Z';p.write_bytes(snapshot.encode(obj))
        with self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):self.approve()

    def test_stale_existing_geometry_and_connectors(self):
        p=self.root/'state/knowledge-atlas'/ap.NAME;old=p.read_bytes();obj=json.loads(old)
        for field in ('nodes','connectorSegments'):
            bad=copy.deepcopy(obj)
            if field=='nodes':bad['accepted_geometry'][field][0]['x']+=1
            else:bad['accepted_geometry'][field][0]['points'][0]['x']+=1
            p.write_bytes(snapshot.encode(bad))
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'INTEGRITY_MISMATCH'):self.approve()
        p.write_bytes(old);self.unchanged()

    def test_variant_binding(self):
        p=self.manifest;m=json.loads(p.read_text());m['selected_variant']='CURRENT'
        m['manifest_fingerprint']=ap.fingerprint({k:v for k,v in m.items() if k!='manifest_fingerprint'});p.write_bytes(snapshot.encode(m))
        with self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):self.approve()
        self.unchanged()

    def test_fixture_forbidden_without_disposable_adapter(self):
        with self.assertRaisesRegex(ValueError,'FIXTURE_ACTIVATION_FORBIDDEN'):ap.approve(self.root,self.manifest,reviewed_fingerprint=self.reviewed_fingerprint)
        self.unchanged()

    def test_apply_exact_then_idempotent(self):
        result=self.approve();self.assertEqual(result['generation'],1)
        cp,prev,h,g,loaded=ap.accepted(self.root)
        candidate=json.loads((self.preview_dir/'candidate-geometry.json').read_text());self.assertEqual(g,candidate)
        self.assertEqual(len(h['active_categories']),49);self.assertEqual(len(h['active_topics']),95)
        self.assertEqual(h['history_version'],1);self.assertEqual(cp['presentation_generation'],1)
        for field in ('nodes','trays','connectorSegments'):self.assertEqual(g[field][:len(self.reviewed[field])-({'nodes':9,'trays':1,'connectorSegments':0}[field])],self.reviewed[field][:len(g[field])-({'nodes':9,'trays':1,'connectorSegments':0}[field])])
        build.verify_release(self.root/'docs/knowledge-map')
        after={n:transaction.inventory(self.root/n) for n in self.before}
        self.assertEqual(self.approve()['outcome'],'NO_CHANGE')
        for n,h in after.items():self.assertEqual(transaction.inventory(self.root/n),h)
        self.assertEqual(after['data/knowledge'],self.before['data/knowledge'])

    def test_failures_rollback_every_boundary(self):
        for point in ('after_activation_state_candidate','after_geometry_candidate','before_state_staging','after_candidate_write','before_final_rename','after_publish_0','after_publish_1','before_journal_completion'):
            def fault(p):
                if p==point:raise RuntimeError('injected '+p)
            with self.subTest(point=point),self.assertRaisesRegex(RuntimeError,'injected'):self.approve(fault=fault)
            self.unchanged();self.assertFalse((self.root/'state/.knowledge-atlas-transaction.json').exists())

    def test_hard_crash_recovery(self):
        for point in ('before_state_staging','after_activation_state_candidate','after_geometry_candidate','after_candidate_write','before_final_rename','after_publish_0','after_publish_1','before_journal_completion'):
            pid=os.fork()
            if pid==0:
                try:self.approve(fault=lambda p:os._exit(71) if p==point else None)
                except BaseException:os._exit(72)
                os._exit(73)
            _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),71)
            transaction.recover(self.root/'state/.knowledge-atlas-transaction.json',self.root)
            self.unchanged()

    def test_large_blocked_new_root_guards(self):
        for name,outcome,variant in [('large','ACTIVATION_REBALANCE_REQUIRED','current'),('blocked','METADATA_REQUIRED','current'),('new-root','ACTIVATION_REBALANCE_REQUIRED','current')]:
            fixture=self.scenarios[name];folder=Path(self.tmp.name)/name
            m=ap.package_preview(self.root,folder,variant,fixture=fixture)
            self.assertEqual(m['outcome'],outcome)
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,outcome):
                ap.approve(self.root,folder/'activation-manifest.json',reviewed_fingerprint=m['manifest_fingerprint'],test_context=fixture)
        self.unchanged()

    def test_normal_production_cannot_activate(self):
        # Explicit synthetic test-course membership, only in the disposable copy.
        p=self.root/'data/knowledge/courses.json';courses=json.loads(p.read_text());course=copy.deepcopy(courses[0]);course.update(id=9000,title='Fixture course',topic_ids=[900001],category_ids=[331,1201,428],project_ids=[],topics_count=1,capstone_topics_count=0,evidence_ids=['fixture-only-explicit']);courses.append(course);p.write_bytes(snapshot.encode(courses))
        prod_before=transaction.inventory(self.root/'docs/knowledge-map')
        report=pipeline.run(self.root,production=True)
        self.assertEqual(report['status'],'REVIEW_REQUIRED');self.assertFalse(report['applied'])
        self.assertEqual(prod_before,transaction.inventory(self.root/'docs/knowledge-map'))

    def test_stale_runtime(self):
        p=self.root/'prototypes/knowledge-atlas-v6/layout.js';p.write_bytes(p.read_bytes()+b'\n// changed\n')
        with self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):self.approve()

    def test_stale_checkpoint(self):
        p=self.root/'state/knowledge-atlas/layout-checkpoint.json';obj=json.loads(p.read_text());obj['categories']['category:1164']['slot_anchor']['x']+=1;p.write_bytes(snapshot.encode(obj))
        with self.assertRaisesRegex(ValueError,'INTEGRITY_MISMATCH'):self.approve()

    def test_current_no_change_static_preview(self):
        # Remove disposable added rows before checking the real Course fixture.
        out=Path(self.tmp.name)/'real-baseline-preview'
        manifest=ap.package_preview(self.root,out,'centering',context={'mode':'CURRENT_COURSE','course_ids':[8]})
        self.assertEqual(manifest['outcome'],'NO_CHANGE');self.assertEqual(manifest['expected_generation_change'],0)
        self.assertTrue((out/'view/index.html').is_file())
        result=ap.approve(self.root,out/'activation-manifest.json',reviewed_fingerprint=manifest['manifest_fingerprint']);self.assertEqual(result['generation'],0)
        self.unchanged()

    def test_accepted_history_survives_evidence_only_updates(self):
        self.approve()
        data=snapshot.load_source(self.root/'data/knowledge')
        row=next(r for r in data['progress']['projects'] if r['project_id']==380);row['status']='completed'
        course=data['progress']['courses'][0];course['active_project']=None;course['completed_projects'].append(380)
        source=self.root/'data/knowledge';(source/'progress.json').write_bytes(snapshot.encode(data['progress']))
        report=pipeline.run(self.root,production=True)
        self.assertTrue(report['applied']);self.assertEqual(report['presentation']['generation'],1)
        cp,prev,h,g,loaded=ap.accepted(self.root);self.assertEqual(len(h['active_topics']),95)
        self.assertEqual(h['history_version'],1)
        # Explicit per-topic progress evidence in the disposable observation only.
        row=next(r for r in data['progress']['topics'] if not r['is_learned'])
        row.update(is_learned=True,is_completed=True,is_verified=True,verification_status='verified')
        filename=next(iter(data['observations']));observation=data['observations'][filename]
        observed=next(r for r in observation['topics'] if r['topic_id']==row['topic_id']);observed.update(is_learned=True,is_completed=True,verification_status='verified')
        observation['learned_topics_count']+=1;observation['learned_topic_ids']=sorted(observation['learned_topic_ids']+[row['topic_id']])
        course['learned_topics_count']+=1;course['learned_topic_ids']=sorted(course['learned_topic_ids']+[row['topic_id']]);course['verified_topic_ids']=sorted(course['verified_topic_ids']+[row['topic_id']])
        (source/filename).write_bytes(snapshot.encode(observation));(source/'progress.json').write_bytes(snapshot.encode(data['progress']))
        report=pipeline.run(self.root,production=True);self.assertTrue(report['applied']);self.assertEqual(report['presentation']['generation'],1)
        self.assertEqual(g,ap.accepted(self.root)[3])

    def test_stale_algorithm(self):
        from unittest.mock import patch
        with patch.object(ap,'algorithm_hash',return_value='0'*64),self.assertRaisesRegex(ValueError,'STALE_ACTIVATION_PREVIEW'):
            self.approve()
        self.unchanged()

    def test_unknown_geometry_fields_require_migration(self):
        value=json.loads((self.root/'state/knowledge-atlas'/ap.NAME).read_text())
        value['accepted_geometry']['nodes'][0]['hidden']=True
        value['geometry_hashes']=ap.geometry_hashes(value['accepted_geometry'])
        with self.assertRaisesRegex(ValueError,'MIGRATION_REQUIRED'):ap.check_history(value)

    def test_operator_api_without_fixture_override_in_disposable_copy(self):
        source=self.root/'data/knowledge';courses=json.loads((source/'courses.json').read_text())
        course=copy.deepcopy(courses[0]);course.update(id=9000,title='Disposable course fixture',topic_ids=list(range(900001,900007)),category_ids=[331,428,1201],project_ids=[],topics_count=6,capstone_topics_count=0,evidence_ids=['fixture-only-explicit']);courses.append(course)
        (source/'courses.json').write_bytes(snapshot.encode(courses))
        folder=Path(self.tmp.name)/'operator-preview'
        manifest=ap.package_preview(self.root,folder,'centering',{'mode':'CURRENT_COURSE','course_ids':[9000]})
        self.assertFalse(manifest['fixture_only']);self.assertEqual(manifest['outcome'],'ACTIVATION_REVIEW_REQUIRED')
        candidate=json.loads((folder/'candidate-geometry.json').read_text())
        for key in ('nodes','trays','connectorSegments'):self.assertEqual(candidate[key],self.reviewed[key])
        result=ap.approve(self.root,folder/'activation-manifest.json',reviewed_fingerprint=manifest['manifest_fingerprint']);self.assertEqual(result['generation'],1)
        self.assertEqual(ap.accepted(self.root)[3],candidate)

    def test_consistent_artifact_replacement_invalidates_review_token(self):
        m=json.loads(self.manifest.read_text())
        candidate_path=self.preview_dir/'candidate-geometry.json'
        candidate=json.loads(candidate_path.read_text());candidate['nodes'][-1]['x']+=.01
        candidate_path.write_bytes(snapshot.encode(candidate))
        m['bindings']['candidate']=ap.fingerprint(candidate)
        m['manifest_fingerprint']=ap.fingerprint({k:v for k,v in m.items() if k!='manifest_fingerprint'})
        self.manifest.write_bytes(snapshot.encode(m))
        with self.assertRaisesRegex(ValueError,'reviewed manifest identity changed'):self.approve()
        self.unchanged()

    def test_missing_review_token_cannot_approve(self):
        with self.assertRaisesRegex(ValueError,'REVIEW_FINGERPRINT_REQUIRED'):
            ap.approve(self.root,self.manifest,test_context=self.small)
        self.unchanged()
