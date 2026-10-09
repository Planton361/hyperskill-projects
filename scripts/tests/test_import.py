"""Behavior tests against disposable repositories; never modify real coursework."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


INFRA = Path(__file__).resolve().parents[2]
SIMPLE = b'''package bot;
public class Main {
    public static void main(String[] args) { System.out.println("Hello"); }
}
'''


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="hyperskill paths ")
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.repo = base / "repo"
        self.source = base / "source"
        self.repo.mkdir()
        shutil.copytree(INFRA / "scripts", self.repo / "scripts")
        shutil.copy2(INFRA / ".gitignore", self.repo / ".gitignore")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.src = self.source / "Lesson/task/src/bot/Main.java"
        self.src.parent.mkdir(parents=True)
        self.src.write_bytes(SIMPLE)
        # A synthetic reviewed profile tests the same exact-byte gate, without
        # copying or executing educational build scripts in test repositories.
        self.build = self.source / "build.gradle"
        self.build.write_text("def userJava = JavaVersion.current()\n")
        self.settings = self.source / "settings.gradle"
        self.settings.write_text("include 'util'\n")
        (self.source / "course-info.yaml").write_text("title: Demo Project\n")
        self.approve_fixture_profile()
        self.target = self.repo / "java/Demo Project"

    def approve_fixture_profile(self, additional_profiles=None):
        data = {
            "id": "fixture-legacy",
            "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (self.build, self.settings)},
        }
        if additional_profiles:
            data["additional_profiles"] = additional_profiles
        (self.repo / "scripts/templates/academy-profile.json").write_text(json.dumps(data))

    def invoke(self, *flags, version=True, success=True):
        before = snapshot(self.source)
        cmd = ["python3", "-B", str(self.repo / "scripts/import-hyperskill-project")]
        if version:
            cmd += ["--java-version", "23"]
        result = subprocess.run(cmd + list(flags) + [str(self.source), "java"],
                                text=True, capture_output=True)
        self.assertEqual(snapshot(self.source), before, "Importer modified its source")
        self.assertEqual(result.returncode, 0 if success else 2, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_independent_completion_validator_rejects_non_owner_attestation(self):
        import runpy
        validate = runpy.run_path(str(self.repo / 'scripts/export_metadata.py'))['validate_completion']
        with self.assertRaises(ValueError):
            validate(dict(project_id=7, status='completed', attested_by='platform',
                          observed_at='2026-10-08T12:00:00Z'))

    def test_explicit_owner_completion_metadata(self):
        self.invoke('--completed-at', '2026-10-08T12:00:00Z', success=False)
        self.invoke('--project-url', 'https://hyperskill.org/projects/113',
                    '--completed-at', '2026-10-08T12:00:00Z')
        meta = json.loads((self.target / '.hyperskill-import.json').read_text())
        self.assertEqual(meta['completion'], dict(project_id=113, status='completed',
            attested_by='owner', observed_at='2026-10-08T12:00:00Z'))
        self.invoke('--update', success=False)

    def test_dry_run_no_writes_and_unknown_version(self):
        before = snapshot(self.repo)
        self.assertIn("Java-Zielversion: 23", self.invoke("--dry-run", version=False))
        self.invoke("--dry-run")
        self.assertEqual(snapshot(self.repo), before)
        self.assertFalse(self.target.exists())

    def test_build_variants_ignore_comments_and_whitespace_without_sha_registration(self):
        self.build.write_text("// new Academy revision\n\nplugins { id 'application' }\n")
        self.settings.write_text("rootProject.name = 'New project'\n")
        self.assertIn('Reviewed Academy statement', self.invoke('--dry-run'))
        self.build.write_text("  def userJava = JavaVersion.current()\n")
        self.assertIn('Reviewed Academy statement', self.invoke('--dry-run'))

    def test_import_allowlist_and_no_commit(self):
        for name in (".git/config", ".idea/workspace.xml", ".gradle/cache", "build/report.html",
                     "Lesson/old-stage/src/Old.java", "Lesson/task/test/Tests.java",
                     "Lesson/task/src/bot/.git/config", "Lesson/task/src/bot/cache.tmp",
                     "Lesson/task/task.html", "Lesson/task/task-info.yaml"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("must not be imported\n")
        output = self.invoke()
        self.assertIn("IGNORE", output)
        expected = {".hyperskill-import.json", "README.md", "build.gradle.kts", "settings.gradle.kts",
                    "gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar",
                    "gradle/wrapper/gradle-wrapper.properties", "src/main/java/bot/Main.java"}
        self.assertEqual(set(snapshot(self.target)), expected)
        self.assertEqual((self.target / "src/main/java/bot/Main.java").read_bytes(), SIMPLE)
        manifest = json.loads((self.target / ".hyperskill-import.json").read_text())
        self.assertEqual(manifest["original_project_name"], "Demo Project")
        self.assertEqual(manifest["directory_name"], "Demo Project")
        self.assertNotIn("README.md", manifest["files"])
        self.assertEqual((self.target / "settings.gradle.kts").read_text(),
                         'rootProject.name = "Demo Project"\n')
        self.assertTrue(os.access(self.target / "gradlew", os.X_OK))
        self.assertEqual(subprocess.run(["git", "-C", str(self.repo), "rev-parse", "--verify", "HEAD"],
                                       capture_output=True).returncode, 128)

    def test_updates_require_flag_and_preserve_edits(self):
        self.invoke()
        self.invoke(success=False)
        self.src.write_bytes(SIMPLE.replace(b"Hello", b"Updated"))
        self.invoke("--update")
        exported = self.target / "src/main/java/bot/Main.java"
        self.assertIn(b"Updated", exported.read_bytes())
        exported.write_bytes(SIMPLE.replace(b"Hello", b"Local work"))
        before = snapshot(self.target)
        self.assertIn("Lokale Änderung", self.invoke("--update", success=False))
        self.assertEqual(snapshot(self.target), before)

    def test_project_title_override_and_safe_filename_documentation(self):
        (self.source / "course-info.yaml").write_text("title: Original / Name\n")
        output = self.invoke("--dry-run")
        self.assertIn("WARNUNG", output)
        self.assertIn("Original ／ Name", output)
        self.invoke()
        manifest = json.loads((self.repo / "java/Original ／ Name/.hyperskill-import.json").read_text())
        self.assertEqual(manifest["original_project_name"], "Original / Name")
        self.assertEqual(manifest["directory_name"], "Original ／ Name")
        output = self.invoke("--dry-run", "--title", "Coffee Machine")
        self.assertIn("Ziel: " + str(self.repo / "java/Coffee Machine"), output)

    def test_title_is_required_when_not_reliably_detectable(self):
        (self.source / "course-info.yaml").write_text("programming_language: Java\n")
        self.assertIn("--title", self.invoke(success=False))

    def test_update_preserves_user_edited_readme(self):
        self.invoke()
        readme = self.target / "README.md"
        readme.write_text("Curated project documentation\n")
        self.src.write_bytes(SIMPLE.replace(b"Hello", b"Updated"))
        self.invoke("--update")
        self.assertEqual(readme.read_text(), "Curated project documentation\n")

    def test_update_does_not_delete_missing_files(self):
        helper = self.src.with_name("Helper.java")
        helper.write_text("package bot; class Helper {}\n")
        self.invoke()
        helper.unlink()  # Remove only this disposable test fixture.
        before = snapshot(self.target)
        self.invoke("--update", success=False)
        self.assertEqual(snapshot(self.target), before)

    def test_unknown_build_plugins_dependencies_sourcesets_abort(self):
        original = self.build.read_text()
        for addition in ("plugins { id 'org.springframework.boot' }", "implementation 'foo:bar:1'",
                         "sourceSets.main.java.srcDir 'custom'", "apply from: 'other.gradle'"):
            with self.subTest(addition=addition):
                self.build.write_text(original + addition)
                self.assertIn("Unreviewed Academy", self.invoke(success=False))
                self.assertFalse(self.target.exists())
        self.build.write_text(original)

        original_settings = self.settings.read_text()
        for addition in ("plugins { id 'com.example.unknown' version '1.0' }",
                         "includeBuild 'unreviewed-build-logic'",
                         "apply from: 'other.settings.gradle'"):
            with self.subTest(settings_addition=addition):
                self.settings.write_text(original_settings + addition)
                self.assertIn("Unreviewed Academy", self.invoke(success=False))
                self.assertFalse(self.target.exists())
        self.settings.write_text(original_settings)

    def test_extra_builds_resources_modules_abort(self):
        for name in ("pom.xml", "module/build.gradle.kts", "gradle/libs.versions.toml",
                     "Lesson/task/resources/config.json", "Lesson/task/src/banner.txt", "util/src/Helper.java"):
            with self.subTest(name=name):
                path = self.source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("complex project\n")
                self.invoke(success=False)
                self.assertFalse(self.target.exists())
                path.unlink()

    def test_platform_secrets_database_and_dependency_in_source_abort(self):
        for extra in ("import org.hyperskill.hstest.stage.StageTest;", 'String password = "sensitive-value";',
                      'String connection = "jdbc:h2:demo";', "import com.example.External;"):
            with self.subTest(extra=extra):
                self.src.write_bytes(SIMPLE + extra.encode())
                output = self.invoke(success=False)
                self.assertNotIn("sensitive-value", output)
                self.assertFalse(self.target.exists())

    def test_source_symlink_is_not_followed(self):
        self.src.with_name("Outside.java").symlink_to(self.repo / "README.md")
        self.assertIn("Symlink", self.invoke(success=False))

    def test_destination_symlink_is_rejected(self):
        (self.repo / "java").symlink_to(self.source, target_is_directory=True)
        self.assertIn("Symlink", self.invoke(success=False))

    def test_ambiguous_layout_aborts(self):
        (self.source / "Second/task/src").mkdir(parents=True)
        self.invoke(success=False)

    def test_explicit_and_inferred_java_version(self):
        self.build.write_text("java.toolchain.languageVersion = JavaLanguageVersion.of(21)\n")
        self.approve_fixture_profile()
        self.assertIn("Java-Zielversion: 23", self.invoke("--dry-run", version=False))
        self.src.write_bytes(SIMPLE + b'// """ text block syntax\n')
        self.assertIn("Untergrenze", self.invoke("--java-version", "11", success=False))

    def test_explicit_java_23_overrides_course_metadata(self):
        (self.source / "course-info.yaml").write_text(
            "title: Demo Project\nprogramming_language_version: 11\n")
        self.src.write_bytes(b'''package bot;
public class Main {
    public static void main(String[] args) {
        String text = """
            Java 23 export
            """;
        System.out.println(text);
    }
}
''')
        output = self.invoke("--dry-run")
        self.assertIn("Kursangabe=11", output)
        self.assertIn("Syntax-Untergrenze=15", output)
        self.assertIn("Java-Zielversion: 23", output)

    def test_wrapper_tampering_is_detected(self):
        (self.repo / "scripts/templates/wrapper/gradlew").write_text("modified\n")
        self.assertIn("Wrapper-Prüfsumme", self.invoke(success=False))

    def test_whitespace_rejected_even_for_untracked_files(self):
        self.src.write_bytes(SIMPLE.replace(b"package bot;", b"package bot;  "))
        self.assertIn("Whitespace", self.invoke(success=False))


if __name__ == "__main__":
    unittest.main()
