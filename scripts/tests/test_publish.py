"""Real disposable Git repositories; only remote network/publication is intercepted."""
import argparse
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from scripts.tests import test_import
snapshot, INFRA = test_import.snapshot, test_import.INFRA


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_import.ImportTests('test_dry_run_no_writes_and_unknown_version')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.source = self.fixture.repo, self.fixture.source
        self.git('config','user.name','Disposable owner')
        self.git('config','user.email','owner@example.invalid')
        self.git('branch','-M','main')
        self.git('add','.')
        self.git('commit','-qm','Test infrastructure')
        self.remote = self.repo.parent/'remote.git'
        subprocess.run(['git','clone','-q','--bare',str(self.repo),str(self.remote)],check=True)
        self.git('remote','add','origin','https://github.com/Planton361/hyperskill-projects.git')
        (self.source/'course-info.yaml').write_text('title: Demo Project\nprogramming_language: Java\n')
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 7\n')
        sys.path.insert(0,str(INFRA/'scripts'))
        self.addCleanup(lambda:sys.path.remove(str(INFRA/'scripts')))
        self.api=runpy.run_path(str(INFRA/'scripts/publish-hyperskill-project'))
        self.execute=self.api['execute'];self.g=self.execute.__globals__
        self.g.update(ROOT=self.repo,IMPORTER=self.repo/'scripts/import-hyperskill-project')
        self.args=argparse.Namespace(source=str(self.source),project_url=None,completed_at='2026-10-08T12:00:00Z',attest_completed=False,java_version=None,title=None,main_class=None,language='auto',dry_run=False,prepare_only=False,publish='pr')
        self.calls=[]
        self.review=None

    def git(self,*args,root=None):
        return subprocess.check_output(['git','-C',str(root or self.repo),*args],stderr=subprocess.DEVNULL)

    def helper(self,answers=('COMPLETE 7','PUBLISH 7'),build=True,push=True,real_build=False):
        original=subprocess.run
        before=snapshot(self.source)
        root_before=self.g['ROOT']
        def run(command,*args,**kwargs):
            self.calls.append(command)
            if command[0]=='git' and 'fetch' in command:
                command=[*command];command[command.index('origin')]=str(self.remote)
            if command[0].endswith('/gradlew') and not real_build:
                if not build:raise subprocess.CalledProcessError(1,command)
                return subprocess.CompletedProcess(command,0)
            if command[0]=='git' and 'push' in command:
                if not push:raise subprocess.CalledProcessError(1,command)
                return subprocess.CompletedProcess(command,0)
            return original(command,*args,**kwargs)
        try:
            with patch('subprocess.run',side_effect=run),patch('builtins.input',side_effect=answers),redirect_stdout(io.StringIO()):
                self.execute(self.args)
        finally:
            self.assertEqual(snapshot(self.source),before)
            if self.g['ROOT'] != root_before:
                self.review=self.g['ROOT'];self.addCleanup(shutil.rmtree,self.review)

    def test_clean_repository_uses_metadata_java23_and_only_commits_export(self):
        head=self.git('rev-parse','HEAD');self.helper()
        self.assertEqual(self.git('rev-parse','HEAD'),head)
        changed=self.git('diff-tree','--no-commit-id','--name-only','-r','HEAD',root=self.review).decode().splitlines()
        self.assertTrue(changed);self.assertTrue(all(n.startswith('java/Demo Project/') for n in changed))
        meta=json.loads((self.review/'java/Demo Project/.hyperskill-import.json').read_text())
        self.assertEqual(meta['java_version'],23);self.assertEqual(meta['project_id'],7)
        self.assertFalse((self.repo/'java/Demo Project').exists())

    def test_dirty_checkout_index_and_untracked_files_are_untouched(self):
        (self.repo/'staged').write_text('mine');self.git('add','staged')
        (self.repo/'untracked').write_text('mine');(self.repo/'.gitignore').write_text('# mine\n')
        before=snapshot(self.repo);status=self.git('status','--porcelain=v1');self.helper()
        self.assertEqual(snapshot(self.repo),before);self.assertEqual(self.git('status','--porcelain=v1'),status)

    def test_stale_checkout_uses_latest_remote_main(self):
        (self.repo/'upstream').write_text('upstream');self.git('add','upstream');self.git('commit','-qm','Upstream change')
        self.git('push',str(self.remote),'main')
        newest=self.git('rev-parse','HEAD')
        self.git('switch','--detach','HEAD~1')
        self.helper();self.assertEqual(self.git('rev-parse','HEAD^',root=self.review),newest)

    def test_missing_local_git_write_rights_never_requires_writing_original(self):
        original=subprocess.run
        def block(cmd,*a,**kw):
            if cmd[0]=='git' and str(self.repo) in cmd and any(x in cmd for x in ('add','commit','switch','fetch','worktree')):
                raise PermissionError('Codex cannot write original .git')
            return original(cmd,*a,**kw)
        with patch('subprocess.run',side_effect=block):self.helper()
        self.assertIsNotNone(self.review)

    def test_completion_and_publication_cannot_be_bypassed(self):
        with self.assertRaisesRegex(ValueError,'declined'):self.helper(['NO'])
        self.assertFalse((self.review/'java/Demo Project').exists())
        with self.assertRaisesRegex(ValueError,'declined'):self.helper(['COMPLETE 7','NO'])
        self.assertFalse(any('push' in c for c in self.calls))

    def test_build_failure_and_push_conflict_stop(self):
        with self.assertRaises(subprocess.CalledProcessError):self.helper(build=False)
        self.assertFalse(any('push' in c for c in self.calls))
        self.g['ROOT']=self.repo
        with self.assertRaisesRegex(ValueError,'Push rejected'):self.helper(push=False)
        self.assertTrue(self.git('log','-1','--format=%s',root=self.review).startswith(b'Publish owner-attested'))
        self.assertFalse(any('--force' in c for c in self.calls))

    def test_missing_and_conflicting_project_id_stop(self):
        (self.source/'course-remote-info.yaml').unlink()
        with self.assertRaisesRegex(ValueError,'Project ID'):self.helper([])
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 380\n')
        self.args.project_url='https://hyperskill.org/projects/7'
        with self.assertRaisesRegex(ValueError,'conflicts'):self.helper([])

    def test_duplicate_and_second_simulated_project(self):
        self.helper()
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.helper([])
        self.g['ROOT']=self.repo
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 8\n')
        self.args.project_url=None;self.args.title='Second simulated project';self.helper(['COMPLETE 8','PUBLISH 8'])
        self.assertTrue((self.review/'java/Second simulated project').exists())

    def test_dry_run_does_not_write_or_ask_for_confirmation(self):
        before=snapshot(self.repo);self.args.dry_run=True;self.helper([])
        self.assertEqual(snapshot(self.repo),before);self.assertIsNone(self.review)

    def test_prepare_only_real_gradle_build(self):
        self.args.prepare_only=True;self.helper(['COMPLETE 7'],real_build=True)
        self.assertTrue((self.review/'java/Demo Project/build/classes/java/main/bot/Main.class').exists())

    def test_python_sources_resources_and_no_dependency_install(self):
        shutil.rmtree(self.source/'Lesson/task/src')
        (self.source/'build.gradle').unlink();(self.source/'settings.gradle').unlink()
        (self.source/'course-info.yaml').write_text('title: Demo Python\nprogramming_language: Python\n')
        (self.source/'Lesson/task/main.py').write_text('import json\nwith open("data.json") as data:\n    print(json.load(data))\n')
        (self.source/'Lesson/task/data.json').write_text('{"hello": 1}\n')
        self.helper()
        meta=json.loads((self.review/'python/Demo Python/.hyperskill-import.json').read_text())
        self.assertEqual(meta['dependencies'],[]);self.assertIn('src/data.json',meta['files'])
        self.assertFalse(any('pip' in str(c) for c in self.calls))

    def test_nonwritable_temporary_destination_stops_without_source_changes(self):
        with patch('tempfile.mkdtemp',side_effect=PermissionError('no write access')):
            with self.assertRaises(PermissionError):self.helper([])
