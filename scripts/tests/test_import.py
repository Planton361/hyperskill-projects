"""Universal imports use only disposable owner workspaces and Git repositories."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

INFRA = Path(__file__).resolve().parents[2]
JAVA_SOURCE = b'package bot; public class Main { public static void main(String[] args) {} }\n'


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='universal owner fixture ')
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.repo, self.source = base / 'repo', base / 'source'
        self.repo.mkdir()
        shutil.copytree(INFRA / 'scripts', self.repo / 'scripts')
        shutil.copy2(INFRA / '.gitignore', self.repo / '.gitignore')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic owner fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.task = self.source / 'Demo Project/task'
        self.src = self.task / 'src/bot/Main.java'
        self.src.parent.mkdir(parents=True)
        self.src.write_bytes(JAVA_SOURCE)
        self.build, self.settings = self.source / 'build.gradle', self.source / 'settings.gradle'
        self.build.write_text("throw new RuntimeException('must not run')\n")
        self.settings.write_text("includeBuild 'must-not-load'\n")
        (self.source / 'course-info.yaml').write_text('title: Demo Project\nprogramming_language: Java\n')
        (self.source / 'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 7\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Synthetic infrastructure')
        self.target = self.repo / 'projects/7'
        self.code_path = 'solution/Demo Project/task/src/bot/Main.java'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.DEVNULL)

    def declaration(self, files):
        path = self.source.parent / 'selection.json'
        path.write_text(json.dumps({'schema': 1, 'files': files}))
        return path

    def invoke(self, *flags, language='java', success=True, confirm=True):
        before = snapshot(self.source)
        command = ['python3.12', '-B', str(self.repo / 'scripts/import-hyperskill-project'), str(self.source)]
        if confirm:
            command += ['--confirmed-at', '2026-10-08T12:00:00Z']
        if language:
            command += ['--language', language]
        result = subprocess.run(command + list(map(str, flags)), text=True, capture_output=True)
        self.assertEqual(snapshot(self.source), before, 'Owner workspace changed')
        self.assertEqual(result.returncode, 0 if success else 2, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def manifest(self):
        return json.loads((self.target / '.hyperskill-import.json').read_text())

    def commit_archive(self):
        self.git('add', 'projects'); self.git('commit', '-qm', 'TEST ONLY owner archive')
        result = subprocess.run(['python3.12', '-B', self.repo / 'scripts/validate-project-exports.py'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_dry_run_is_read_only_and_reports_exact_owner_evidence(self):
        before = snapshot(self.repo)
        output = self.invoke('--dry-run', confirm=False)
        for text in ('Project ID: 7', 'Final source folder:', 'DRY-RUN OK', 'no Academy build or solution code was executed', 'role solution', 'sha256', 'OMIT build.gradle'):
            self.assertIn(text, output)
        self.assertEqual(snapshot(self.repo), before)
        self.assertFalse(self.target.exists())

    def test_universal_archive_exact_inventory_bytes_and_separate_time_semantics(self):
        self.invoke()
        manifest = self.manifest()
        self.assertEqual(set(manifest), {'schema','mode','project_id','project_url','title','languages','completion','files'})
        self.assertEqual(manifest['schema'], 4)
        self.assertEqual(manifest['mode'], 'code-archive')
        self.assertEqual(manifest['completion'], dict(project_id=7, status='completed', attested_by='owner', confirmed_at='2026-10-08T12:00:00Z'))
        self.assertEqual(set(snapshot(self.target)), {'.hyperskill-import.json','README.md',self.code_path})
        self.assertEqual((self.target / self.code_path).read_bytes(), JAVA_SOURCE)
        for name, row in manifest['files'].items():
            self.assertEqual(hashlib.sha256((self.target / name).read_bytes()).hexdigest(), row['sha256'])
        self.assertEqual(self.commit_archive()[0]['archive_mode'], 'code-archive')

    def test_optional_actual_completion_is_preserved_and_not_inferred(self):
        self.invoke('--completed-at', '2026-10-01T01:02:03Z')
        self.assertEqual(self.manifest()['completion']['completed_at'], '2026-10-01T01:02:03Z')

    def test_invalid_or_future_completion_and_actual_after_confirmation_rejected(self):
        for flags in [('--confirmed-at','now'), ('--completed-at','now'),
                      ('--confirmed-at','2026-02-30T12:00:00Z'),
                      ('--completed-at','2026-10-09T00:00:00Z')]:
            with self.subTest(flags=flags):
                self.invoke(*flags, success=False)
                self.assertFalse(self.target.exists())
        self.invoke(success=False, confirm=False)

    def test_all_languages_unknown_suffix_and_extensionless_sources_need_no_adapters(self):
        self.src.unlink()
        for name in ('main.py','Main.kt','main.js','code.future','program'):
            (self.task / 'src' / name).write_text('invalid code; topic_id=999999; must not execute\n')
        self.invoke('--language', 'kotlin', '--language', 'javascript')
        self.assertEqual(len(self.manifest()['files']), 6)
        self.assertIn('solution/Demo Project/task/src/program', self.manifest()['files'])
        self.assertEqual(self.manifest()['languages'], ['java','kotlin','javascript'])
        self.commit_archive()

    def test_python_without_src_uses_same_generic_selection(self):
        shutil.rmtree(self.task / 'src')
        (self.task / 'main.py').write_text('import missing_dependency\nraise Exception("must not execute")\ndef invalid(:\n')
        self.invoke(language='python')
        self.assertIn('solution/Demo Project/task/main.py', self.manifest()['files'])
        self.commit_archive()

    def test_build_variants_and_code_are_never_run_or_included(self):
        sentinel = self.source / 'executed'
        for text in ('invalid Gradle', f"new File('{sentinel}').text = 'ran'", 'plugins { totally.unknown() }'):
            self.build.write_text(text); self.settings.write_text(text)
            self.invoke('--dry-run')
            self.assertFalse(sentinel.exists())
        self.src.write_text('import missing.Library; class Broken { invalid syntax; }\n')
        self.invoke()
        self.assertFalse(sentinel.exists())
        self.assertEqual((self.target / self.code_path).read_bytes(), self.src.read_bytes())
        self.assertFalse(any('gradle' in name for name in self.manifest()['files']))

    def test_automatic_selection_omits_prior_tasks_platform_tests_and_generated_material(self):
        for name in ('Earlier/task/src/Old.java','.idea/workspace.xml','.gradle/cache/data','build/report.html',
                     'Demo Project/task/test/PlatformTest.java','Demo Project/task/src/node_modules/pkg/code.js',
                     'Demo Project/task/src/generated/Generated.java','Demo Project/task/task.html'):
            p=self.source/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('not owner final code')
        platform = self.task / 'src/Platform.java'
        platform.write_text('import org.hyperskill.hstest.StageTest; class AcademyTest {}')
        self.invoke()
        self.assertEqual(set(self.manifest()['files']), {'README.md',self.code_path})

    def test_ambiguous_final_tasks_stop_but_explicit_selection_succeeds(self):
        another = self.source / 'Other/task/src/code'
        another.parent.mkdir(parents=True); another.write_text('owner final source')
        self.assertIn('--files-from', self.invoke('--title','Unmatched',success=False))
        choice = self.declaration({'Other/task/src/code':'solution'})
        self.invoke('--title','Unmatched','--files-from',choice)
        self.assertEqual((self.target/'solution/Other/task/src/code').read_bytes(), another.read_bytes())

    def test_explicit_selection_without_any_academy_metadata_preserves_paths(self):
        (self.source/'course-info.yaml').unlink(); (self.source/'course-remote-info.yaml').unlink()
        choice = self.declaration({'Demo Project/task/src/bot/Main.java':'solution'})
        self.invoke('--files-from',choice,'--project-url','https://hyperskill.org/projects/7','--title','Generic owner code',language=None)
        self.assertNotIn('languages', self.manifest())
        self.assertEqual((self.target/self.code_path).read_bytes(), JAVA_SOURCE)

    def test_explicit_text_and_binary_resources_remain_resources(self):
        (self.task/'src/data.json').write_bytes(b'{"fixture":true}\n')
        (self.task/'src/image.bin').write_bytes(b'\x00\xff\x10\x80')
        self.assertIn('UTF-8', self.invoke(success=False))
        choice = self.declaration({'Demo Project/task/src/bot/Main.java':'solution',
                                 'Demo Project/task/src/data.json':'resource','Demo Project/task/src/image.bin':'resource'})
        self.invoke('--files-from',choice)
        self.assertEqual((self.target/'solution/Demo Project/task/src/image.bin').read_bytes(), b'\x00\xff\x10\x80')
        self.assertEqual(self.manifest()['files']['solution/Demo Project/task/src/image.bin']['role'], 'resource')
        self.commit_archive()

    def test_no_solution_binary_as_code_and_unsupported_roles_rejected(self):
        binary = self.source/'blob'; binary.write_bytes(b'\x00\xff')
        for files in ({'blob':'solution'}, {'blob':'resource'}, {'Demo Project/task/src/bot/Main.java':'unknown'}):
            self.invoke('--files-from',self.declaration(files),success=False)
            self.assertFalse(self.target.exists())

    def test_private_names_secrets_and_metadata_are_rejected_without_leaking_values(self):
        token = 'ghp_' + 'x' * 30
        self.src.write_text('token = "' + token + '"')
        self.assertNotIn(token, self.invoke(success=False))
        self.src.write_bytes(JAVA_SOURCE)
        private = self.task/'src/.env'; private.write_text('private fixture')
        self.invoke(success=False)
        private.unlink()
        self.assertNotIn(token, self.invoke('--title', token, success=False))

    def test_symlinks_at_file_parent_workspace_and_special_files_rejected(self):
        external = self.source.parent/'outside'; external.write_text('external')
        link = self.task/'src/link'; link.symlink_to(external)
        self.assertIn('Symlink',self.invoke(success=False)); link.unlink()
        directory = self.task/'src/alias'; directory.symlink_to(external.parent, target_is_directory=True)
        self.assertIn('Symlink', self.invoke(success=False)); directory.unlink()
        import os
        fifo=self.task/'src/pipe'; os.mkfifo(fifo)
        self.assertIn('Special', self.invoke(success=False))

    def test_invalid_paths_case_aliases_and_unicode_aliases_rejected(self):
        for relative in ('../outside','/absolute','bad\\name','CON','bad:name','x/../code','e\u0301'):
            with self.subTest(relative=relative):
                self.invoke('--files-from', self.declaration({relative:'solution'}),success=False)
        (self.task/'src/A').write_text('one'); (self.task/'src/a').write_text('two')
        # On case-insensitive hosts the names alias physically; declaration still must fail.
        choice=self.declaration({'Demo Project/task/src/A':'solution','Demo Project/task/src/a':'solution'})
        self.invoke('--files-from',choice,success=False)

    def test_missing_duplicate_json_keys_and_missing_selected_files_rejected(self):
        choice=self.declaration({'missing':'solution'})
        self.invoke('--files-from',choice,success=False)
        choice.write_text('{"schema":1,"files":{"program":"solution","program":"resource"}}')
        self.assertIn('Duplicate', self.invoke('--files-from',choice,success=False))

    def test_exact_identity_malformed_or_conflicting_metadata_rejected(self):
        for url in ('https://hyperskill.org/projects/07','https://hyperskill.org/projects/7/',
                    'https://hyperskill.org/projects/0','https://hyperskill.org/projects/7?x=1',
                    'https://hyperskill.org/projects/9007199254740992','https://example.com/projects/7'):
            self.invoke('--project-url',url,success=False)
        self.assertIn('conflicts',self.invoke('--project-url','https://hyperskill.org/projects/8',success=False))
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 07\n')
        self.invoke('--project-url','https://hyperskill.org/projects/7',success=False)

    def test_duplicate_id_stops_even_after_first_archive_is_committed(self):
        self.invoke(); self.invoke(success=False); self.commit_archive()
        self.assertIn('Duplicate', self.invoke(success=False))


class ExistingExportValidationTests(unittest.TestCase):
    def test_published_113_229_380_are_accepted_byte_for_byte_without_builds(self):
        exports=[INFRA/'java/Simple Chat Bot with Java',INFRA/'java/My First Project with Java',INFRA/'java/Zookeeper with Java']
        before={str(p):snapshot(p) for p in exports}
        result=subprocess.run(['python3.12','-B',INFRA/'scripts/validate-project-exports.py'],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        rows={r['project_id']:r for r in json.loads(result.stdout)}
        self.assertEqual(set(rows),{113,229,380})
        self.assertEqual(rows[113]['archive_mode'],'legacy-schema-2')
        self.assertEqual(rows[229]['archive_mode'],'source-only')
        self.assertEqual({str(p):snapshot(p) for p in exports},before)


class UnknownAcceptanceFixtureSelectionTests(unittest.TestCase):
    def test_unknown_fixture_prefers_229_then_an_uncompleted_catalog_project(self):
        import runpy,sys
        from unittest.mock import patch
        with patch.object(sys,'path',[str(INFRA/'scripts'),*sys.path]):
            select=runpy.run_path(str(INFRA/'scripts/test-cross-repository.py'))['select_unknown_project']
        scopes={'projects':[{'scope_id':229,'state':'UNKNOWN'},{'scope_id':250,'state':'UNKNOWN'},{'scope_id':100,'state':'KNOWN'}]}
        self.assertEqual(select(scopes,set())['scope_id'],229)
        self.assertEqual(select(scopes,{229})['scope_id'],250)
        with self.assertRaises(ValueError): select(scopes,{229},requested_id=229)
