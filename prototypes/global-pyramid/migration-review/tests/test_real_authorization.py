"""Lean authorization coverage; all publication occurs in isolated git checkouts."""
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
ROOT=BASE.parents[2]
spec=importlib.util.spec_from_file_location('operator',BASE/'review.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)


def clone(root):
    root.mkdir()
    for name in ('scripts','docs/knowledge-map','state/knowledge-atlas','data/knowledge'):
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
    gp=root/'prototypes/global-pyramid';gp.mkdir(parents=True)
    for name in ('app.js','atlas.js','labels.js','ux.js','index.html','style.css'):
        shutil.copyfile(BASE.parent/name,gp/name)
    for name in ('generated','migration-preview','migration-review/runtime'):
        shutil.copytree(BASE.parent/name,gp/name,ignore=shutil.ignore_patterns('tests','__pycache__'))
    shutil.copyfile(BASE/'review.py',gp/'migration-review/review.py')
    subprocess.run(['git','init','-q','-b','main',str(root)],check=True)


class RealAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.home=Path(cls.temp.name);cls.root=cls.home/'repo';clone(cls.root)
        spec=importlib.util.spec_from_file_location('controlled_operator',cls.root/'prototypes/global-pyramid/migration-review/review.py')
        cls.op=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.op)
        files,_=cls.op.P.artifacts(cls.root);preview=cls.home/'preview';preview.mkdir()
        for n,b in files.items():(preview/n).write_bytes(b)
        cls.package=cls.root/'prototypes/global-pyramid/migration-review/fresh'
        cls.manifest=cls.op.make_package(cls.root,preview,cls.package);cls.path=cls.package/'migration-manifest.json';cls.token=cls.manifest['manifest_fingerprint']
        cls.state=R.tree(cls.root/'state/knowledge-atlas');cls.production=R.tree(cls.root/'docs/knowledge-map');cls.knowledge=R.tree(cls.root/'data/knowledge')
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def tearDown(self):
        for name,files in [('state/knowledge-atlas',self.state),('docs/knowledge-map',self.production)]:
            target=self.root/name;shutil.rmtree(target);target.mkdir()
            for n,b in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (self.root/'state/.knowledge-atlas-transaction.json').unlink(missing_ok=True)
    def refuses(self,fn,status):
        with self.assertRaises(ValueError) as e:fn()
        self.assertIn(status,str(e.exception))
        self.assertEqual(R.tree(self.root/'state/knowledge-atlas'),self.state)
        self.assertEqual(R.tree(self.root/'docs/knowledge-map'),self.production)
    def test_default_deny_normal_approval_and_disposable_api(self):
        self.refuses(lambda:self.op.approve(self.root,self.path,self.token),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
        self.refuses(lambda:self.op.apply_test(self.root,self.path,{}),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
    def test_missing_confirmation_absolute_path_and_tokens(self):
        for path,token,confirm,status in [(self.path,self.token,False,'REAL_SPATIAL_MIGRATION_FORBIDDEN'),(Path('migration-manifest.json'),self.token,True,'REAL_SPATIAL_MIGRATION_FORBIDDEN'),(self.path,None,True,'REVIEWED_SPATIAL_FINGERPRINT_REQUIRED'),(self.path,'0'*64,True,R.STALE)]:
            with self.subTest(status=status):self.refuses(lambda:self.op.apply_real(self.root,path,token,confirm),status)
    def test_old_real_package_stale(self):
        old=BASE/'real-current/migration-manifest.json';token=R.read(old)['manifest_fingerprint']
        self.assertEqual(token,'f4350c3f9e455091c01481517a50286899699a813f014ca222a35bac793784d3')
        self.refuses(lambda:R.inspect_package(old,token),R.STALE)
        self.refuses(lambda:self.op.apply_real(self.root,old,token,True),R.STALE)
    def test_fixture_refused(self):
        modified=self.home/'fixture-manifest.json';m=dict(self.manifest,fixture_only=True);modified.write_bytes(R.encoded(m))
        self.refuses(lambda:self.op.apply_real(self.root,modified,self.token,True),'FIXTURE_SPATIAL_MIGRATION_FORBIDDEN')
    def test_pending_transaction_and_wrong_repository_refused(self):
        p=self.root/'state/.knowledge-atlas-transaction.json';p.write_text('{}')
        try:self.refuses(lambda:self.op.apply_real(self.root,self.path,self.token,True),'SPATIAL_RECOVERY_REQUIRED')
        finally:p.unlink()
        self.refuses(lambda:self.op.apply_real(self.home,self.path,self.token,True),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
        subprocess.run(['git','-C',str(self.root),'symbolic-ref','HEAD','refs/heads/other'],check=True)
        try:self.refuses(lambda:self.op.apply_real(self.root,self.path,self.token,True),'REAL_SPATIAL_MIGRATION_FORBIDDEN')
        finally:subprocess.run(['git','-C',str(self.root),'symbolic-ref','HEAD','refs/heads/main'],check=True)
    def test_source_and_runtime_changes_refused(self):
        for name in ('docs/knowledge-map/app.js','state/knowledge-atlas/layout-checkpoint.json','data/knowledge/progress.json','prototypes/global-pyramid/generated/global-geometry.json','scripts/update-knowledge-atlas.py'):
            p=self.root/name;original=p.read_bytes();p.write_bytes(original+b' ')
            try:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(ValueError,R.STALE):self.op.apply_real(self.root,self.path,self.token,True)
            finally:p.write_bytes(original)
        with patch.object(self.op,'implementation',return_value={'changed':'runtime'}):self.refuses(lambda:self.op.apply_real(self.root,self.path,self.token,True),R.STALE)
    def test_controlled_exact_apply_replay_and_cli_dispatch(self):
        with patch.object(self.op.P,'artifacts',side_effect=AssertionError('No regeneration')),patch.object(self.op,'candidate',side_effect=AssertionError('No regeneration')),patch.object(self.op.transaction,'publish',wraps=self.op.transaction.publish) as writer:
            result=self.op.apply_real(self.root,self.path,self.token,True)
            self.assertEqual(result['status'],'APPLIED_SPATIAL_MIGRATION');self.assertEqual(writer.call_count,1)
            state=R.tree(self.root/'state/knowledge-atlas');production=R.tree(self.root/'docs/knowledge-map')
            self.assertEqual(self.op.apply_real(self.root,self.path,self.token,True)['status'],'ALREADY_APPLIED');self.assertEqual(writer.call_count,1)
        self.assertEqual(self.op.validate_installed(self.root,self.path,self.token)['accepted_positions'],135)
        self.assertEqual(R.tree(self.root/'data/knowledge'),self.knowledge)
        command=[sys.executable,'-B',str(self.root/'scripts/update-knowledge-atlas.py'),'--apply-spatial-migration',str(self.path),'--reviewed-fingerprint',self.token,'--confirm-real-spatial-migration','--json']
        p=subprocess.run(command,capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr+p.stdout);self.assertEqual(json.loads(p.stdout)['status'],'ALREADY_APPLIED')
        self.assertEqual(state,R.tree(self.root/'state/knowledge-atlas'));self.assertEqual(production,R.tree(self.root/'docs/knowledge-map'))
        # Normal canonical writer recognizes a real, reviewed installed receipt.
        p=subprocess.run([sys.executable,'-B','-c',"import sys;sys.path.insert(0,sys.argv[1]);from knowledge_atlas.canonical import writer_guard;from pathlib import Path;writer_guard(Path(sys.argv[2]))",str(self.root/'scripts'),str(self.root)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_one_injected_failure_existing_rollback(self):
        def fault(boundary):
            if boundary=='after_state_swap':raise RuntimeError('representative authorized failure')
        with self.assertRaisesRegex(RuntimeError,'representative authorized failure'):self.op.apply_real(self.root,self.path,self.token,True,fault=fault)
        self.assertEqual(R.tree(self.root/'state/knowledge-atlas'),self.state);self.assertEqual(R.tree(self.root/'docs/knowledge-map'),self.production)
        self.assertFalse((self.root/'state/.knowledge-atlas-transaction.json').exists())
    def test_actual_real_authorities_unchanged(self):
        baseline=R.read(BASE/'real-apply-enablement/protected-before.json')
        self.assertTrue(all(R.sha((ROOT/n).read_bytes())==h for n,h in baseline.items()))
        self.assertFalse((ROOT/'state/knowledge-atlas/spatial-authority.json').exists())

if __name__=='__main__':unittest.main()
