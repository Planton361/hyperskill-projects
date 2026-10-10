"""Source-only archive tests use disposable Academy trees and Git repositories."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

INFRA = Path(__file__).resolve().parents[2]
JAVA_SOURCE = b'''package bot;
public class Main {
    public static void main(String[] args) { System.out.println("Hello"); }
}
'''


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file() and not path.is_symlink()}


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='hyperskill source-only paths ')
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.repo = base / 'repo'
        self.source = base / 'source'
        self.repo.mkdir()
        shutil.copytree(INFRA / 'scripts', self.repo / 'scripts')
        shutil.copy2(INFRA / '.gitignore', self.repo / '.gitignore')
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        for key, value in (('user.name', 'Source-only fixture'), ('user.email', 'fixture@example.invalid')):
            subprocess.run(['git', '-C', str(self.repo), 'config', key, value], check=True)
        self.task = self.source / 'Demo Project/task'
        self.src = self.task / 'src/bot/Main.java'
        self.src.parent.mkdir(parents=True)
        self.src.write_bytes(JAVA_SOURCE)
        self.build = self.source / 'build.gradle'
        self.build.write_text("settingsEvaluated { throw new GradleException('must never execute') }\n")
        self.settings = self.source / 'settings.gradle'
        self.settings.write_text("includeBuild 'untrusted-academy-build-logic'\n")
        (self.source / 'course-info.yaml').write_text(
            'title: Demo Project\nprogramming_language: Java\nprogramming_language_version: 11\n')
        (self.source / 'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 7\n')
        subprocess.run(['git', '-C', str(self.repo), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-qm', 'Infrastructure fixture'], check=True)
        self.target = self.repo / 'java/Demo Project'

    def invoke(self, *flags, language='java', success=True):
        before = snapshot(self.source)
        command = ['python3.12', '-B', str(self.repo / 'scripts/import-hyperskill-project'),
                   str(self.source), language, '--completed-at', '2026-10-08T12:00:00Z']
        result = subprocess.run(command + list(flags), text=True, capture_output=True)
        self.assertEqual(snapshot(self.source), before, 'Importer modified Academy source')
        self.assertEqual(result.returncode, 0 if success else 2, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_dry_run_is_read_only_and_reports_exact_owner_evidence(self):
        before = snapshot(self.repo)
        output = self.invoke('--dry-run')
        self.assertIn('Project ID: 7', output)
        self.assertIn('Final source folder:', output)
        self.assertIn('DRY-RUN OK', output)
        self.assertIn('no Academy build or solution code was executed', output)
        self.assertEqual(snapshot(self.repo), before)
        self.assertFalse(self.target.exists())

    def test_source_only_archive_preserves_bytes_and_has_exact_manifest(self):
        self.invoke()
        self.assertEqual(snapshot(self.target), {
            '.hyperskill-import.json': hashlib.sha256((self.target/'.hyperskill-import.json').read_bytes()).hexdigest(),
            'README.md': hashlib.sha256((self.target/'README.md').read_bytes()).hexdigest(),
            'src/bot/Main.java': hashlib.sha256(JAVA_SOURCE).hexdigest(),
        })
        self.assertEqual((self.target/'src/bot/Main.java').read_bytes(), JAVA_SOURCE)
        self.assertFalse(any(path.name in {'gradlew', 'gradlew.bat', 'build.gradle.kts', 'settings.gradle.kts'}
                             for path in self.target.rglob('*')))
        manifest = json.loads((self.target/'.hyperskill-import.json').read_text())
        self.assertEqual(set(manifest), {'schema', 'mode', 'language', 'directory_name',
                                         'project_id', 'completion', 'files'})
        self.assertEqual(manifest['schema'], 3)
        self.assertEqual(manifest['mode'], 'source-only')
        self.assertEqual(manifest['language'], 'java')
        self.assertEqual(manifest['directory_name'], 'Demo Project')
        self.assertEqual(manifest['project_id'], 7)
        self.assertEqual(manifest['completion'], dict(project_id=7, status='completed',
            attested_by='owner', observed_at='2026-10-08T12:00:00Z'))
        self.assertEqual(manifest['files'], {'src/bot/Main.java': hashlib.sha256(JAVA_SOURCE).hexdigest()})
        self.assertIn('Source-only archive', (self.target/'README.md').read_text())

    def test_untrusted_gradle_variants_are_never_parsed_or_executed(self):
        sentinel = self.source/'gradle-was-executed.txt'
        variants = [
            ("description = 'harmless Academy metadata'\n", "rootProject.name = 'Changed title'\n"),
            ("plugins { id 'org.hyperskill.academy' version '999.42' }\n", "includeBuild 'another-untrusted-build'\n"),
            ("plugins {\n id 'java'\n}\ndependencies { implementation 'example.invalid:x:1' }\n",
             "rootProject.name\n =\n 'reformatted'\n"),
            (f"tasks.register('bad') {{ doLast {{ new File('{sentinel}').text = 'ran' }} }}\n",
             "settingsEvaluated { throw new GradleException('must never execute') }\n"),
            ('this is deliberately not valid Gradle syntax\n', 'also not valid Gradle syntax\n'),
        ]
        for build, settings in variants:
            with self.subTest(build=build):
                self.build.write_text(build)
                self.settings.write_text(settings)
                self.invoke('--dry-run')
                self.assertFalse(sentinel.exists())
                self.assertFalse(self.target.exists())
        self.build.write_text('plugins { id "java" version "77" }\n')
        self.settings.write_text("throw new RuntimeException('never execute')\n")
        self.invoke()
        self.assertFalse(sentinel.exists())
        self.assertEqual((self.target/'src/bot/Main.java').read_bytes(), JAVA_SOURCE)
        self.assertFalse(any(path.name.endswith(('.gradle', '.gradle.kts'))
                             for path in self.target.rglob('*')))

    def test_final_task_filter_excludes_stages_tests_ide_builds_and_unreferenced_files(self):
        prior = self.source/'Stage 1/task/src/Old.java'; prior.parent.mkdir(parents=True); prior.write_text('old')
        platform_test = self.task/'test/ZookeeperTest.java'; platform_test.parent.mkdir(); platform_test.write_text('test')
        for name in ('.idea/workspace.xml', '.gradle/cache/data', 'build/reports/report.html',
                     'Demo Project/task/task.html', 'Demo Project/task/task-info.yaml',
                     'Demo Project/task/custom-src/Helper.java',
                     'Demo Project/task/src/.venv/lib/python/Injected.py',
                     'Demo Project/task/src/node_modules/pkg/Injected.java'):
            path = self.source/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('ignore me')
        (self.task/'src/data.txt').write_text('zoo data\n')
        (self.task/'src/unreferenced.txt').write_text('not a required resource\n')
        self.src.write_bytes(JAVA_SOURCE.replace(b'System.out.println("Hello");',
            b'System.out.println(Main.class.getResource("data.txt"));'))
        self.invoke()
        names = {path.relative_to(self.target).as_posix() for path in self.target.rglob('*') if path.is_file()}
        self.assertEqual(names, {'.hyperskill-import.json', 'README.md', 'src/bot/Main.java', 'src/data.txt'})
        self.assertEqual((self.target/'src/data.txt').read_bytes(), b'zoo data\n')

    def test_external_dependencies_invalid_java_and_missing_main_are_archived(self):
        raw = b'import com.example.Library;\npublic class Broken { this is not Java; }\n'
        self.src.write_bytes(raw)
        self.invoke()
        self.assertEqual((self.target/'src/bot/Main.java').read_bytes(), raw)

    def test_python_source_is_archived_without_import_validation_or_execution(self):
        (self.source/'course-info.yaml').write_text('title: Demo Project\nprogramming_language: Python\n')
        self.src.unlink()
        shutil.rmtree(self.task/'src')
        self.python_source = self.task/'main.py'
        self.python_source.write_text('import unknown_third_party_package\nraise SystemExit("must not run")\ndef invalid(:\n')
        self.invoke(language='python')
        archived = self.target.parent.parent/'python/Demo Project'
        self.assertEqual((archived/'src/main.py').read_bytes(), self.python_source.read_bytes())
        manifest = json.loads((archived/'.hyperskill-import.json').read_text())
        self.assertEqual(manifest['language'], 'python')
        self.assertEqual(set(manifest['files']), {'src/main.py'})

    def test_python_referenced_text_resource_is_included_without_parsing_source(self):
        (self.source/'course-info.yaml').write_text('title: Demo Project\nprogramming_language: Python\n')
        self.src.unlink()
        shutil.rmtree(self.task/'src')
        main = self.task/'main.py'; main.write_text('open("data.json")\ndef invalid(:\n')
        (self.task/'data.json').write_text('{"name":"zoo"}\n')
        (self.task/'unused.txt').write_text('not referenced\n')
        self.invoke(language='python')
        archived = self.repo/'python/Demo Project'
        self.assertEqual((archived/'src/main.py').read_bytes(), main.read_bytes())
        self.assertEqual((archived/'src/data.json').read_bytes(), b'{"name":"zoo"}\n')
        self.assertFalse((archived/'src/unused.txt').exists())

    def test_private_paths_secrets_symlinks_and_unsafe_names_stop(self):
        self.src.write_text('String token = "ghp_123456789012345678901234567890";\n')
        output = self.invoke(success=False)
        self.assertNotIn('ghp_123456789012345678901234567890', output)
        self.assertFalse(self.target.exists())
        self.src.write_bytes(JAVA_SOURCE)
        private = self.task/'src/.env'; private.write_text('password=x')
        self.invoke(success=False)
        private.unlink()
        ignored_link = self.source/'.idea/external.xml'; ignored_link.parent.mkdir(parents=True)
        ignored_link.symlink_to(self.repo/'.gitignore')
        self.assertIn('Symlink', self.invoke(success=False))
        ignored_link.unlink()
        unsafe = self.source/'.gradle/bad\npath'; unsafe.parent.mkdir(parents=True, exist_ok=True)
        unsafe.write_text('ignored')
        self.assertIn('Unsafe path', self.invoke(success=False))
        unsafe.unlink()

    def test_duplicate_project_id_and_metadata_conflict_stop(self):
        self.invoke()
        self.invoke(success=False)
        (self.source/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 8\n')
        self.assertIn('conflicts', self.invoke('--project-url', 'https://hyperskill.org/projects/7', success=False))

    def test_missing_and_invalid_completion_timestamp_stop(self):
        command = ['python3.12', '-B', str(self.repo/'scripts/import-hyperskill-project'),
                   str(self.source), 'java', '--project-url', 'https://hyperskill.org/projects/7']
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('timestamp', result.stderr)
        self.invoke('--completed-at', 'now', success=False)

    def test_only_one_final_task_source_root_is_selected(self):
        (self.source/'Another/task/src').mkdir(parents=True)
        self.invoke('--title', 'A different title', success=False)

    def test_title_and_source_path_are_safe(self):
        (self.source/'course-info.yaml').write_text('title: CON\nprogramming_language: Java\n')
        self.invoke(success=False)


class ExistingExportValidationTests(unittest.TestCase):
    def test_published_113_and_380_are_accepted_byte_for_byte_without_builds(self):
        exports = [INFRA/'java/Simple Chat Bot with Java', INFRA/'java/My First Project with Java']
        before = {str(path): snapshot(path) for path in exports}
        result = subprocess.run(['python3.12', '-B', INFRA/'scripts/validate-project-exports.py'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual({row['project_id'] for row in report}, {113, 380})
        self.assertEqual({row['archive_mode'] for row in report}, {'legacy-schema-2'})
        self.assertEqual({str(path): snapshot(path) for path in exports}, before)
        changed = subprocess.check_output(['git', '-C', str(INFRA), 'diff', '--name-only', '--',
                                            'java/Simple Chat Bot with Java',
                                            'java/My First Project with Java']).decode().splitlines()
        self.assertEqual(changed, [])


if __name__ == '__main__':
    unittest.main()
