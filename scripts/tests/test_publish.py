"""Publisher security and workflow tests use a disposable local origin."""
import argparse
import hashlib
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
        self.fixture = test_import.ImportTests('test_dry_run_is_read_only_and_reports_exact_owner_evidence')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.source = self.fixture.repo, self.fixture.source
        self.git('branch', '-M', 'main')
        self.remote = self.repo.parent/'remote.git'
        subprocess.run(['git', 'clone', '-q', '--bare', str(self.repo), str(self.remote)], check=True)
        self.git('remote', 'add', 'origin', 'https://github.com/Planton361/hyperskill-projects.git')
        sys.path.insert(0, str(INFRA/'scripts'))
        self.addCleanup(lambda: sys.path.remove(str(INFRA/'scripts')))
        self.api = runpy.run_path(str(INFRA/'scripts/publish-hyperskill-project'))
        self.execute = self.api['execute']
        self.globals = self.execute.__globals__
        self.globals.update(ROOT=self.repo, IMPORTER=self.repo/'scripts/import-hyperskill-project')
        self.args = argparse.Namespace(source=str(self.source), project_url=None,
            completed_at='2026-10-08T12:00:00Z', title=None, language='auto', dry_run=False)
        self.calls = []
        self.review = None

    def git(self, *args, root=None):
        return subprocess.check_output(['git', '-C', str(root or self.repo), *args],
                                       stderr=subprocess.DEVNULL)

    def run_publisher(self, answers=('COMPLETE 7', 'PUBLISH 7'), push=True):
        original = subprocess.run
        source_before = snapshot(self.source)
        repo_before = snapshot(self.repo)
        root_before = self.globals['ROOT']

        def run(command, *args, **kwargs):
            command = list(command)
            self.calls.append(command)
            if command[0] == 'gh':
                return subprocess.CompletedProcess(command, 0)
            if command[0] == 'git' and 'fetch' in command:
                command[command.index('origin')] = str(self.remote)
            if command[0] == 'git' and 'push' in command:
                if not push:
                    raise subprocess.CalledProcessError(1, command)
                command[command.index('origin')] = str(self.remote)
            return original(command, *args, **kwargs)

        try:
            with patch('subprocess.run', side_effect=run), patch('builtins.input', side_effect=answers), redirect_stdout(io.StringIO()):
                self.execute(self.args)
        finally:
            self.assertEqual(snapshot(self.source), source_before, 'Academy source changed')
            if self.globals['ROOT'] != root_before:
                self.review = self.globals['ROOT']
                self.addCleanup(shutil.rmtree, self.review)
            self.assertEqual(snapshot(self.repo), repo_before, 'Publisher checkout was modified')

    def test_owner_confirmations_publish_only_a_new_source_archive_branch(self):
        head = self.git('rev-parse', 'HEAD')
        self.run_publisher()
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        changed = self.git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD', root=self.review).decode().splitlines()
        self.assertTrue(changed)
        self.assertTrue(all(path.startswith('java/Demo Project/') for path in changed))
        meta = json.loads((self.review/'java/Demo Project/.hyperskill-import.json').read_text())
        self.assertEqual(meta['schema'], 3)
        self.assertEqual(meta['project_id'], 7)
        self.assertEqual(meta['language'], 'java')
        self.assertFalse((self.repo/'java/Demo Project').exists())
        self.assertTrue(any(command[:2] == ['gh', 'pr'] for command in self.calls))
        self.assertTrue(any('push' in command for command in self.calls))
        self.assertTrue(all('--force' not in command for command in self.calls))

    def test_dirty_index_untracked_files_and_academy_are_untouched(self):
        (self.repo/'staged').write_text('mine'); self.git('add', 'staged')
        (self.repo/'untracked').write_text('mine')
        before = snapshot(self.repo); status = self.git('status', '--porcelain=v1')
        self.run_publisher()
        self.assertEqual(snapshot(self.repo), before)
        self.assertEqual(self.git('status', '--porcelain=v1'), status)

    def test_stale_checkout_uses_latest_remote_main(self):
        (self.repo/'upstream').write_text('remote main advance')
        self.git('add', 'upstream'); self.git('commit', '-qm', 'Remote main advance')
        self.git('push', str(self.remote), 'main')
        newest = self.git('rev-parse', 'HEAD')
        self.git('switch', '--detach', 'HEAD~1')
        self.run_publisher()
        self.assertEqual(self.git('rev-parse', 'HEAD^', root=self.review), newest)

    def test_original_git_write_access_is_not_needed(self):
        original = subprocess.run
        def block(command, *args, **kwargs):
            if command[0] == 'git' and str(self.repo) in command and any(
                    word in command for word in ('add', 'commit', 'switch', 'fetch', 'worktree')):
                raise PermissionError('original checkout .git is read-only')
            return original(command, *args, **kwargs)
        with patch('subprocess.run', side_effect=block):
            self.run_publisher()
        self.assertIsNotNone(self.review)

    def test_personal_confirmations_cannot_be_skipped_or_accepted_by_default(self):
        with self.assertRaisesRegex(ValueError, 'declined'):
            self.run_publisher(('NO',))
        self.assertFalse((self.review/'java/Demo Project').exists())
        self.globals['ROOT'] = self.repo
        with self.assertRaisesRegex(ValueError, 'declined'):
            self.run_publisher(('COMPLETE 7', 'NO'))
        self.assertFalse(any('push' in command for command in self.calls))

    def test_no_gradle_or_python_code_is_executed_or_copied(self):
        sentinel = self.source/'build-ran.txt'
        wrapper = self.source/'gradlew'
        wrapper.write_text(f'#!/bin/sh\nprintf ran > "{sentinel}"\n')
        wrapper.chmod(0o755)
        self.fixture.src.write_text('import missing_dependency; this is invalid Java\n')
        self.run_publisher()
        self.assertFalse(sentinel.exists())
        self.assertFalse(any('gradlew' in command[0] for command in self.calls))
        exported = self.review/'java/Demo Project'
        self.assertFalse((exported/'gradlew').exists())
        self.assertEqual((exported/'src/bot/Main.java').read_text(), 'import missing_dependency; this is invalid Java\n')

    def test_conflicting_metadata_stops_before_checkout(self):
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 8\n')
        self.args.project_url = 'https://hyperskill.org/projects/7'
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            self.run_publisher(())

    def test_dry_run_does_not_prompt_write_or_clone(self):
        self.args.dry_run = True
        source_before = snapshot(self.source); repo_before = snapshot(self.repo)
        self.run_publisher(())
        self.assertEqual(snapshot(self.source), source_before)
        self.assertEqual(snapshot(self.repo), repo_before)
        self.assertIsNone(self.review)

    def test_python_source_and_required_resource_are_archived_without_execution(self):
        self.fixture.src.unlink()
        self.fixture.src.parent.rmdir()
        (self.fixture.task/'src').rmdir()
        (self.source/'course-info.yaml').write_text('title: Demo Python\nprogramming_language: Python\n')
        main = self.fixture.task/'main.py'
        main.write_text('import unknown_module\nopen("data.json")\nraise SystemExit("must not run")\n')
        (self.fixture.task/'data.json').write_text('{"ok":true}\n')
        self.run_publisher()
        exported = self.review/'python/Demo Python'
        manifest = json.loads((exported/'.hyperskill-import.json').read_text())
        self.assertEqual(set(manifest['files']), {'src/main.py', 'src/data.json'})
        self.assertEqual((exported/'src/main.py').read_bytes(), main.read_bytes())
        self.assertFalse(any('python' in command[0] and 'main.py' in command for command in self.calls))

    def test_duplicate_project_id_prevents_second_export(self):
        self.run_publisher()
        self.globals['ROOT'] = self.repo
        self.git('push', str(self.remote), 'HEAD:refs/heads/main', root=self.review)
        self.globals['ROOT'] = self.repo
        with self.assertRaisesRegex(ValueError, 'Duplicate Project ID'):
            self.run_publisher(())

    def test_rejected_push_never_force_pushes_or_retries(self):
        with self.assertRaisesRegex(ValueError, 'Branch push rejected'):
            self.run_publisher(push=False)
        self.assertTrue(self.review.exists())
        self.assertFalse(any('--force' in command for command in self.calls))
        self.assertEqual(sum('push' in command for command in self.calls), 1)


if __name__ == '__main__':
    unittest.main()
