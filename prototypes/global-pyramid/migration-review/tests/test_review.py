import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('spatial_review',BASE/'review.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def clone(destination):
    destination.mkdir()
    for d in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge','scripts/knowledge_atlas']:
        shutil.copytree(M.ROOT/d,destination/d,ignore=shutil.ignore_patterns('__pycache__'))
    g=destination/'prototypes/global-pyramid/generated';g.mkdir(parents=True)
    for n in ['global-geometry.json','catalog.json']:shutil.copyfile(M.ROOT/'prototypes/global-pyramid/generated'/n,g/n)
    (destination/M.MARKER).write_text('spatial-migration-tests-v1\n')
def rehash_package(folder):
    m=M.read(folder/'migration-manifest.json');m['files']=M.digest_files({k:v for k,v in M.tree(folder).items() if k not in ['migration-manifest.json','manifest-core.json']});m.pop('manifest_fingerprint');(folder/'manifest-core.json').write_bytes(M.encoded(m));m['manifest_fingerprint']=M.fp(m);(folder/'migration-manifest.json').write_bytes(M.encoded(m));return m
class Review(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox=tempfile.TemporaryDirectory();cls.home=Path(cls.sandbox.name);cls.origin=cls.home/'source';clone(cls.origin);cls.preview=cls.home/'fresh-preview';cls.preview.mkdir();files,_=M.P.artifacts(cls.origin);[(cls.preview/n).write_bytes(b) for n,b in files.items()];cls.package=cls.home/'package';cls.manifest=M.make_package(cls.origin,cls.preview,cls.package);cls.token=cls.manifest['manifest_fingerprint'];cls.seal=M.approve(cls.origin,cls.package/'migration-manifest.json',cls.token);cls.old_state=M.tree(cls.origin/'state/knowledge-atlas');cls.old_production=M.tree(cls.origin/'docs/knowledge-map');cls.knowledge=M.tree(cls.origin/'data/knowledge')
    @classmethod
    def tearDownClass(cls):cls.sandbox.cleanup()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.home=Path(self.temp.name);self.root=self.home/'root';shutil.copytree(self.origin,self.root);self.path=self.package/'migration-manifest.json'
    def tearDown(self):self.temp.cleanup()
    def expect_stale(self,fn,status=M.STALE):
        with self.assertRaises(M.Refusal) as e:fn()
        self.assertEqual(e.exception.status,status)
    def test_deterministic_package_and_refused_overwrite(self):
        folder=self.home/'again';m=M.make_package(self.root,self.preview,folder);self.assertEqual(M.tree(folder),M.tree(self.package));self.assertEqual(m,self.manifest)
        self.expect_stale(lambda:M.make_package(self.root,self.preview,folder),'SPATIAL_REVIEW_ALREADY_EXISTS')
        self.assertEqual(M.fp({k:v for k,v in m.items() if k!='manifest_fingerprint'}),self.token)
    def test_missing_wrong_external_token(self):
        self.expect_stale(lambda:M.approve(self.root,self.path,None),'REVIEWED_SPATIAL_FINGERPRINT_REQUIRED')
        self.expect_stale(lambda:M.approve(self.root,self.path,'0'*64))
    def test_artifact_mutations_rejected(self):
        for name in ['current-geometry.json','target-geometry.json','migration-diff.json','migration-metrics.json','semantic-invariance.json','transaction-plan.json','migration-manifest.json','manifest-core.json','candidate/state/activation-state.json','candidate/production/app.js']:
            folder=self.home/name.replace('/','_');shutil.copytree(self.package,folder);(folder/name).write_bytes((folder/name).read_bytes()+b' ')
            with self.subTest(name=name):self.expect_stale(lambda:M.approve(self.root,folder/'migration-manifest.json',self.token))
    def test_consistent_rehash_cannot_reuse_old_human_token(self):
        folder=self.home/'rehash';shutil.copytree(self.package,folder);page=folder/'view/index.html';page.write_bytes(page.read_bytes().replace(b'Exact spatial migration review',b'Changed spatial migration review'));m=rehash_package(folder)
        self.assertNotEqual(self.token,m['manifest_fingerprint']);self.expect_stale(lambda:M.approve(self.root,folder/'migration-manifest.json',self.token));self.expect_stale(lambda:M.apply_test(self.root,folder/'migration-manifest.json',self.seal))
        # A fresh explicitly supplied review identity can validate this benign UI edit.
        self.assertEqual(M.approve(self.root,folder/'migration-manifest.json',m['manifest_fingerprint'])['status'],'APPROVED_FOR_APPLY')
    def test_stale_production_state_knowledge_and_master(self):
        cases={'production':'docs/knowledge-map/app.js','checkpoint':'state/knowledge-atlas/layout-checkpoint.json','activation':'state/knowledge-atlas/activation-state.json','knowledge':'data/knowledge/progress.json','global':'prototypes/global-pyramid/generated/global-geometry.json','accepted_geometry':'state/knowledge-atlas/activation-state.json','active_history':'state/knowledge-atlas/activation-state.json','generation':'state/knowledge-atlas/layout-checkpoint.json','history_version':'state/knowledge-atlas/activation-state.json'}
        for label,name in cases.items():
            p=self.root/name;before=p.read_bytes()
            try:
                if label in ['accepted_geometry','active_history','generation','history_version']:
                    v=json.loads(before)
                    if label=='accepted_geometry':v['accepted_geometry']['nodes'][0]['x']+=1
                    elif label=='active_history':v['active_topics'].pop()
                    elif label=='generation':v['presentation_generation']+=1
                    else:v['history_version']+=1
                    p.write_bytes(M.encoded(v))
                else:p.write_bytes(before+b' ')
                with self.subTest(binding=label):self.expect_stale(lambda:M.approve(self.root,self.path,self.token))
            finally:p.write_bytes(before)
    def test_validation_implementation_change_rejected(self):
        with patch.object(M,'implementation',return_value={'synthetic-runtime':'changed'}):self.expect_stale(lambda:M.approve(self.root,self.path,self.token))
    def test_seal_nonoverwrite_and_exact_binding(self):
        output=self.home/'seal.json';s=M.approve(self.root,self.path,self.token,output);self.assertEqual(M.read(output),s);self.assertEqual(s,self.seal)
        self.expect_stale(lambda:M.approve(self.root,self.path,self.token,output),'SPATIAL_REVIEW_ALREADY_EXISTS')
        bad=copy.deepcopy(s);bad['reviewed_fingerprint']='a'*64;self.expect_stale(lambda:M.apply_test(self.root,self.path,bad))
    def test_exact_apply_no_layout_replay_and_semantics(self):
        with patch.object(M.P,'construct',side_effect=AssertionError('preview regeneration forbidden')),patch.object(M.P,'artifacts',side_effect=AssertionError('preview regeneration forbidden')),patch.object(M,'candidate',side_effect=AssertionError('candidate reconstruction forbidden')):
            seal=M.approve(self.root,self.path,self.token);r=M.apply_test(self.root,self.path,seal);self.assertEqual(r['status'],'APPLIED_DISPOSABLE_ONLY');self.assertEqual(M.validate_installed(self.root,self.path,self.token)['status'],'PASS')
            before_state=M.tree(self.root/'state/knowledge-atlas');before_production=M.tree(self.root/'docs/knowledge-map');self.assertEqual(M.apply_test(self.root,self.path,seal)['status'],'ALREADY_APPLIED');self.assertEqual(before_state,M.tree(self.root/'state/knowledge-atlas'));self.assertEqual(before_production,M.tree(self.root/'docs/knowledge-map'))
        expected={k.removeprefix('candidate/production/'):v for k,v in M.tree(self.package).items() if k.startswith('candidate/production/')};self.assertEqual(expected,before_production)
        h=M.read(self.root/'state/knowledge-atlas/activation-state.json');old=M.read(self.origin/'state/knowledge-atlas/activation-state.json');self.assertEqual(h['active_categories'],old['active_categories']);self.assertEqual(h['active_topics'],old['active_topics']);self.assertEqual(h['events'],old['events']);self.assertEqual(h['history_version'],0);self.assertEqual(h['layout_generation'],1)
        self.assertEqual(M.read(self.root/'state/knowledge-atlas/spatial-migrations.json')['spatial_history_version'],1);self.assertEqual(M.tree(self.root/'data/knowledge'),self.knowledge);self.assertEqual(M.read(self.root/'docs/knowledge-map/model.json'),M.read(self.origin/'docs/knowledge-map/model.json'))
        self.assertEqual((self.root/'docs/knowledge-map/target-geometry.json').read_bytes(),(self.package/'target-geometry.json').read_bytes());M.build.verify_release(self.root/'docs/knowledge-map')
        self.assertEqual((self.root/'state/knowledge-atlas/spatial-migration-review.json').read_bytes(),self.path.read_bytes())
        self.assertEqual(M.read(self.root/'state/knowledge-atlas/spatial-migration-review.json')['manifest_fingerprint'],self.token)
        self.assertEqual(M.P.activation_persistence.state.read(self.root/'state/knowledge-atlas')[0]['presentation_generation'],1)
    def test_future_reveal_and_reference_promotion(self):
        M.apply_test(self.root,self.path,self.seal);master=M.read(self.root/'docs/knowledge-map/generated/global-geometry.json');authority=M.read(self.root/'state/knowledge-atlas/spatial-authority.json');h=M.read(self.root/'state/knowledge-atlas/activation-state.json');keys=h['active_categories']+h['active_topics'];visible=M.reserved_projection(master,authority,keys);frozen=copy.deepcopy(master);comparisons=0
        for key in ['reference:333','reference:334']:
            before=copy.deepcopy(visible);keys.append(key);visible=M.reserved_projection(master,authority,keys)
            for k,g in before.items():self.assertEqual(visible[k],g);comparisons+=1
        reference=visible['reference:333'];promoted_keys=[k if k!='reference:333' else 'topic:333' for k in keys];promoted=M.reserved_projection(master,authority,promoted_keys);self.assertEqual(reference,promoted['topic:333']);self.assertEqual(master,frozen);self.assertEqual(comparisons,271)
        self.expect_stale(lambda:M.reserved_projection(master,authority,['reference:333','topic:333']))
        # Synthetic valid semantic evidence is disposable, separate from slot data.
        from knowledge_atlas.catalog import Catalog
        fixture=M.snapshot.load_source(self.root/'data/knowledge');self.assertEqual(Catalog(fixture).get_resolution_status(333),'UNRESOLVED_REFERENCE')
        topic=dict(id=333,title='Fixture-only Topic 333',canonical_parent_id=int(reference['geometry']['primary_parent'].split(':')[1]),theory_step_id=333000,url='https://hyperskill.org/learn/step/333000',evidence_ids=[]);fixture['topics'].append(topic)
        (self.root/'fixture-topic-evidence.json').write_bytes(M.encoded(fixture));resolved=Catalog(fixture);self.assertEqual(resolved.get_resolution_status(333),'RESOLVED_TOPIC');self.assertIn('topic:333',resolved.topics);self.assertNotIn(333,resolved.references);self.assertEqual(M.reserved_projection(master,authority,['topic:333'])['topic:333'],reference)
        for k in h['active_categories']+h['active_topics']:self.assertEqual(promoted[k],visible[k])
        self.assertEqual(M.tree(self.root/'data/knowledge'),self.knowledge);self.assertEqual(M.validate_installed(self.root,self.path,self.token)['generation'],1)
        (BASE/'tests/future-reveal.json').write_bytes(M.encoded(dict(fixture_only=True,steps=2,reveal_existing_comparisons=comparisons,maximum_displacement=0,promotion_id=333,promotion_displacement=0,placement_search=False)))
    def test_progress_project_only_has_no_geometry_increment(self):
        M.apply_test(self.root,self.path,self.seal);before=M.tree(self.root/'state/knowledge-atlas');master=M.read(self.root/'docs/knowledge-map/generated/global-geometry.json');authority=M.read(self.root/'state/knowledge-atlas/spatial-authority.json');keys=self.manifest['contract']['source']['accepted_inventory'];coords=M.reserved_projection(master,authority,keys)
        p=self.root/'data/knowledge/progress.json';value=M.read(p);value['topics'][0]['is_learned']=not value['topics'][0]['is_learned'];value['projects'][0]['status']='active';p.write_bytes(M.encoded(value))
        self.assertEqual(before,M.tree(self.root/'state/knowledge-atlas'));self.assertEqual(coords,M.reserved_projection(master,authority,keys));self.assertEqual(M.read(self.root/'state/knowledge-atlas/layout-checkpoint.json')['presentation_generation'],1)
        self.expect_stale(lambda:M.apply_test(self.root,self.path,self.seal)) # Stale evidence cannot be replay-authorized.
    def test_unknown_authority_history_checkpoint_versions_fields_fail_closed(self):
        M.apply_test(self.root,self.path,self.seal)
        for name,field in [('spatial-authority.json','schema_version'),('activation-state.json','schema_version'),('layout-checkpoint.json','state_schema_version')]:
            p=self.root/'state/knowledge-atlas'/name;before=p.read_bytes()
            for edit in ['version','unknown']:
                v=json.loads(before)
                if edit=='version':v[field]=999
                else:v['unknown_future_field']=True
                p.write_bytes(M.encoded(v))
                with self.subTest(name=name,edit=edit):self.expect_stale(lambda:M.validate_installed(self.root,self.path,self.token))
                p.write_bytes(before)
    def test_failures_roll_back_coherent_old_unit(self):
        for boundary in ['after_approval_validation','before_state_staging','after_state_staging','after_production_staging','before_final_rename','after_state_swap','before_production_swap','after_production_swap','before_durable_commit']:
            def fault(name):
                if name==boundary:raise RuntimeError('injected '+boundary)
            with self.subTest(boundary=boundary),self.assertRaises(RuntimeError):M.apply_test(self.root,self.path,self.seal,fault)
            self.assertEqual(M.tree(self.root/'state/knowledge-atlas'),self.old_state);self.assertEqual(M.tree(self.root/'docs/knowledge-map'),self.old_production);self.assertFalse((self.root/'state/.knowledge-atlas-transaction.json').exists());self.assertEqual(M.tree(self.root/'data/knowledge'),self.knowledge)
    def test_hard_crash_recovery(self):
        results=[]
        boundaries=['after_candidate_construction','after_approval_validation','before_state_staging','after_state_staging','after_production_staging','before_final_rename','after_state_swap','before_production_swap','after_production_swap','before_durable_commit','after_durable_commit','after_cleanup']
        for boundary in boundaries:
            r=self.home/boundary;shutil.copytree(self.origin,r);seal=self.home/(boundary+'.seal.json');seal.write_bytes(M.encoded(self.seal));runner=BASE/'tests/crash.py';result=subprocess.run([sys.executable,'-B',str(runner),str(r),str(self.path),str(seal),boundary,str(self.preview)],capture_output=True,text=True);self.assertEqual(result.returncode,77,(boundary,result.stdout,result.stderr))
            if (r/'state/.knowledge-atlas-transaction.json').exists():self.expect_stale(lambda:M.validate_installed(r,self.path,self.token),'SPATIAL_RECOVERY_REQUIRED')
            M.recover_test(r)
            committed=boundary in ['after_durable_commit','after_cleanup']
            if committed:self.assertEqual(M.validate_installed(r,self.path,self.token)['status'],'PASS')
            else:self.assertEqual(M.tree(r/'state/knowledge-atlas'),self.old_state);self.assertEqual(M.tree(r/'docs/knowledge-map'),self.old_production)
            self.assertEqual(M.tree(r/'data/knowledge'),self.knowledge);self.assertFalse((r/'state/.knowledge-atlas-transaction.json').exists());self.assertFalse(list((r/'state').glob('.atlas-candidate-*')));self.assertFalse(list((r/'docs').glob('.atlas-candidate-*')));results.append(dict(boundary=boundary,result='NEW_COMMITTED' if committed else 'OLD_ROLLED_BACK',knowledge_unchanged=True))
        (BASE/'tests/recovery-results.json').write_bytes(M.encoded(results))
    def test_real_root_and_fixture_domains_forbidden(self):
        self.expect_stale(lambda:M.apply_test(M.ROOT,self.path,self.seal),'REAL_SPATIAL_MIGRATION_FORBIDDEN');self.expect_stale(lambda:M.recover_test(M.ROOT),'REAL_SPATIAL_MIGRATION_FORBIDDEN');self.expect_stale(lambda:M.approve(M.ROOT,self.path,self.token),'FIXTURE_SPATIAL_MIGRATION_FORBIDDEN')
        (self.root/M.MARKER).unlink();self.expect_stale(lambda:M.apply_test(self.root,self.path,self.seal),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
        # Even an accidental real marker cannot bypass canonical root identity.
        with patch.object(M,'ROOT',self.origin):self.expect_stale(lambda:M.apply_test(self.origin,self.path,self.seal),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
    def test_real_protected_bytes_unchanged(self):
        before=M.read(BASE/'tests/baseline.json');current={str(p.relative_to(M.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge'] for p in (M.ROOT/d).rglob('*') if p.is_file()};p=M.ROOT/'prototypes/global-pyramid/generated/global-geometry.json';current[str(p.relative_to(M.ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();self.assertEqual(before,current)
if __name__=='__main__':unittest.main()
