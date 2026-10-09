"""Owner helper regressions: disposable exports, mocked publication, no real Academy writes."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from scripts.tests import test_import
snapshot = test_import.snapshot

ROOT = Path(__file__).resolve().parents[2]


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_import.ImportTests('test_dry_run_no_writes_and_unknown_version')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.source, self.target = self.fixture.repo, self.fixture.source, self.fixture.target
        self.git('branch', '-M', 'main')
        self.git('config', 'user.name', 'Disposable owner')
        self.git('config', 'user.email', 'owner@example.invalid')
        self.git('remote', 'add', 'origin', 'https://github.com/Planton361/hyperskill-projects.git')
        self.git('add', '.')
        self.git('commit', '-qm', 'Disposable infrastructure')
        self.head=self.git('rev-parse','HEAD').decode().strip()
        sys.path.insert(0,str(ROOT/'scripts'))
        self.addCleanup(lambda:sys.path.remove(str(ROOT/'scripts')))
        loaded=runpy.run_path(str(ROOT/'scripts/publish-hyperskill-project'))
        self.execute=loaded['execute']
        self.globals=self.execute.__globals__
        self.globals.update(ROOT=self.repo,IMPORTER=self.repo/'scripts/import-hyperskill-project')
        self.calls=[]
        self.args=argparse.Namespace(source=str(self.source),project_url='https://hyperskill.org/projects/7',completed_at='2026-10-08T12:00:00Z',attest_completed=True,java_version=23,title=None,main_class=None,dry_run=False,prepare_only=False,publish='pr')

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.DEVNULL)

    def run_helper(self,build_ok=True,answers=('COMPLETE 7','PUBLISH 7'),real_build=False,push_ok=True):
        original=subprocess.run
        before=snapshot(self.source)
        def mocked(command,*args,**kwargs):
            self.calls.append(command)
            if command[0].endswith('/gradlew') and not real_build:
                if not build_ok:raise subprocess.CalledProcessError(1,command)
                return subprocess.CompletedProcess(command,0)
            if command[0]=='git' and 'ls-remote' in command:
                return subprocess.CompletedProcess(command,0,stdout=self.head+'\trefs/heads/main\n')
            if command[0]=='git' and 'push' in command:
                if not push_ok:raise subprocess.CalledProcessError(1,command)
                return subprocess.CompletedProcess(command,0)
            return original(command,*args,**kwargs)
        try:
            with patch('subprocess.run',side_effect=mocked),patch('builtins.input',side_effect=answers),redirect_stdout(io.StringIO()):
                self.execute(self.args)
        finally:
            self.assertEqual(snapshot(self.source),before,'Original IDE source modified')

    def test_new_export_preserves_schema_and_never_commits_unrelated_staged_or_dirty_files(self):
        staged=self.repo/'unrelated.txt';staged.write_text('Unrelated staged work\n');self.git('add','unrelated.txt')
        (self.repo/'untracked.txt').write_text('Unrelated untracked work\n')
        (self.repo/'.gitignore').write_text((self.repo/'.gitignore').read_text()+'# unrelated dirty edit\n')
        self.run_helper()
        meta=json.loads((self.target/'.hyperskill-import.json').read_text())
        self.assertEqual(meta['schema'],2);self.assertEqual(meta['completion']['attested_by'],'owner')
        self.assertEqual(meta['completion']['observed_at'],self.args.completed_at)
        changed=self.git('diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().splitlines()
        self.assertTrue(changed);self.assertTrue(all(n.startswith('java/Demo Project/') for n in changed))
        self.assertEqual(self.git('diff','--cached','--name-only').decode().strip(),'unrelated.txt')
        self.assertIn('untracked.txt',self.git('status','--short').decode());self.assertIn('.gitignore',self.git('diff','--name-only').decode())
        pushes=[c for c in self.calls if c[0]=='git' and 'push' in c]
        self.assertEqual(len(pushes),1);self.assertIn('HEAD:refs/heads/publish/hyperskill-7-',pushes[0][-1]);self.assertNotIn('--force',pushes[0])

    def test_owner_attestation_and_actual_utc_are_mandatory(self):
        for field,value in [('attest_completed',False),('completed_at','2039-01-01T00:00:00Z'),('completed_at','2026-10-08T12:00:00+02:00')]:
            old=getattr(self.args,field);setattr(self.args,field,value)
            with self.assertRaises(ValueError):self.run_helper()
            setattr(self.args,field,old)
        self.assertFalse(self.target.exists())

    def test_unsupported_layout_fails_without_import_build_or_publication(self):
        (self.source/'Other/task/src').mkdir(parents=True)
        with self.assertRaises(subprocess.CalledProcessError):self.run_helper()
        self.assertFalse(self.target.exists());self.assertFalse(any(c[0].endswith('/gradlew') for c in self.calls))

    def test_build_failure_keeps_review_candidate_but_never_stages_commits_or_pushes(self):
        with self.assertRaises(subprocess.CalledProcessError):self.run_helper(build_ok=False)
        self.assertTrue(self.target.exists());self.assertEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
        self.assertEqual(self.git('diff','--cached','--name-only'),b'')
        self.assertFalse(any(c[0]=='git' and 'push' in c for c in self.calls))

    def test_completion_declined_before_import_and_publication_declined_after_build(self):
        with self.assertRaises(ValueError):self.run_helper(answers=['NO'])
        self.assertFalse(self.target.exists())
        with self.assertRaises(ValueError):self.run_helper(answers=['COMPLETE 7','NO'])
        self.assertTrue(self.target.exists());self.assertEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
        self.assertEqual(self.git('diff','--cached','--name-only'),b'')

    def test_dry_run_and_prepare_only_do_not_publish(self):
        self.args.dry_run=True;self.run_helper(answers=[]);self.assertFalse(self.target.exists())
        self.args.dry_run=False;self.args.prepare_only=True;self.run_helper(answers=['COMPLETE 7'])
        self.assertTrue(self.target.exists());self.assertEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
        self.assertEqual(self.git('diff','--cached','--name-only'),b'')

    def test_duplicate_project_id_is_rejected_without_new_import(self):
        self.args.prepare_only=True;self.run_helper(answers=['COMPLETE 7'])
        self.args.title='Second export of same Project'
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.run_helper(answers=[])
        self.assertFalse((self.repo/'java/Second export of same Project').exists())

    def test_committed_duplicate_is_rejected_even_if_local_export_is_removed(self):
        self.run_helper()
        import shutil
        shutil.rmtree(self.target)
        self.args.title = 'Second committed ID'
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.run_helper(answers=[])
        self.assertFalse((self.repo / 'java/Second committed ID').exists())

    def test_invalid_existing_manifest_bytes_block_publication(self):
        self.args.prepare_only = True
        self.run_helper(answers=['COMPLETE 7'])
        (self.target / 'src/main/java/bot/Main.java').write_text('tampered')
        self.args.project_url = 'https://hyperskill.org/projects/8'
        self.args.title = 'Another project'
        with self.assertRaisesRegex(ValueError, 'evidence is invalid'):
            self.run_helper(answers=[])
        self.assertFalse((self.repo / 'java/Another project').exists())

    def test_push_rejection_keeps_commit_without_force_or_automatic_retry(self):
        self.args.publish='push'
        with self.assertRaisesRegex(ValueError,'Push rejected'):self.run_helper(push_ok=False)
        self.assertNotEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
        self.assertEqual(len([c for c in self.calls if c[0]=='git' and 'push' in c]),1)

    def test_git_conversion_cannot_publish_bytes_that_break_manifest_hashes(self):
        self.git('config','core.autocrlf','true')
        with self.assertRaisesRegex(ValueError,'Git filters'):
            self.run_helper()
        self.assertEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
        self.assertEqual(self.git('diff','--cached','--name-only'),b'')
        self.assertFalse(any(c[0]=='git' and 'push' in c for c in self.calls))

    def test_real_standalone_gradle_build_in_disposable_export(self):
        self.args.prepare_only=True
        self.run_helper(real_build=True,answers=['COMPLETE 7'])
        self.assertTrue((self.target/'build/classes/java/main/bot/Main.class').is_file())
        self.assertEqual(self.git('rev-parse','HEAD').decode().strip(),self.head)
