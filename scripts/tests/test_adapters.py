"""Language selection and source-only path/resource safety regressions."""
import re
import sys
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import source_adapters
from source_adapters import detect, project_url, source_only_files, unsafe_source_path, workspace
from scripts.tests import test_import
IMPORT = test_import.ImportTests
IMPORT_MODULE = __import__('runpy').run_path(str(ROOT/'scripts/import-hyperskill-project'))


class SourceOnlyAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='adapter source-only ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.task = self.root/'Demo/task'
        self.src = self.task/'src'
        (self.src/'pkg').mkdir(parents=True)
        (self.src/'pkg/Main.java').write_text('invalid Java is still archiveable\n')
        (self.root/'course-info.yaml').write_text('title: Demo\nprogramming_language: Java\n')
        (self.root/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 380\n')

    def extract(self, language='java', title='Demo'):
        importer = IMPORT_MODULE
        return source_only_files(self.root, language, importer['inventory'], importer['excluded'],
                                 unsafe_source_path, importer['SECRETS'], title)

    def test_workspace_language_and_exact_project_identity(self):
        file = self.src/'pkg/Main.java'
        self.assertEqual(workspace(file), self.root)
        self.assertEqual(detect(self.root), 'java')
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            detect(self.root, 'python')
        self.assertEqual(project_url(self.root), 'https://hyperskill.org/projects/380')
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            project_url(self.root, 'https://hyperskill.org/projects/113')
        (self.root/'course-remote-info.yaml').write_text('hyperskill_project:\n  id: 380\n  another: 1\nhyperskill_project:\n  id: 229\n')
        with self.assertRaisesRegex(ValueError, 'missing or ambiguous'):
            project_url(self.root)

    def test_final_named_task_wins_over_earlier_stages_without_merging_them(self):
        earlier = self.root/'Earlier Stage/task/src/Old.java'
        earlier.parent.mkdir(parents=True); earlier.write_text('earlier stage')
        foreign = self.src/'experimental.py'; foreign.write_text('raise SystemExit("not Java")')
        _, payload = self.extract()
        self.assertEqual(set(payload), {'src/pkg/Main.java'})
        self.assertEqual(payload['src/pkg/Main.java'], b'invalid Java is still archiveable\n')

    def test_python_adapter_archives_invalid_code_and_unknown_imports_without_execution(self):
        (self.root/'course-info.yaml').write_text('title: Demo\nprogramming_language: Python\n')
        shutil.rmtree(self.src)
        main = self.task/'main.py'; main.write_text('import requests\nraise SystemExit("must not run")\ndef broken(:\n')
        self.assertEqual(detect(self.root), 'python')
        _, payload = self.extract('python')
        self.assertEqual(payload, {'src/main.py': main.read_bytes()})

    def test_python_literals_select_only_local_allowlisted_text_resources(self):
        (self.root/'course-info.yaml').write_text('title: Demo\nprogramming_language: Python\n')
        shutil.rmtree(self.src)
        main = self.task/'main.py'; main.write_text('open("data.json")\nopen("out.txt", "w")\nopen(input())\n')
        (self.task/'data.json').write_text('{"ok":true}\n')
        (self.task/'out.txt').write_text('generated output\n')
        (self.task/'unused.txt').write_text('not referenced\n')
        _, payload = self.extract('python')
        self.assertEqual(set(payload), {'src/main.py', 'src/data.json'})
        self.assertEqual(payload['src/data.json'], b'{"ok":true}\n')
        (self.task/'outside.txt').write_text('private')
        main.write_text('open("../outside.txt")\n')
        _, payload = self.extract('python')
        self.assertEqual(set(payload), {'src/main.py'})

    def test_private_looking_source_and_secrets_stop_without_printing_contents(self):
        private = self.src/'.env'; private.write_text('token=x')
        with self.assertRaisesRegex(ValueError, 'Private-looking'):
            self.extract()
        private.unlink()
        source = self.src/'pkg/Main.java'; source.write_text('String password = "do-not-leak-123";\n')
        with self.assertRaisesRegex(ValueError, 'secret'):
            self.extract()

    def test_symlinks_and_cross_platform_unsafe_paths_stop(self):
        link = self.src/'pkg/Outside.java'; link.symlink_to(self.root/'course-info.yaml')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.extract()
        link.unlink()
        self.assertTrue(unsafe_source_path(Path('bad\nname.java')))
        self.assertTrue(unsafe_source_path(Path(r'..\escape.java')))
        self.assertTrue(unsafe_source_path(Path('CON.java')))

    def test_python_requires_supported_interpreter(self):
        (self.root/'course-info.yaml').write_text('title: Demo\nprogramming_language: Python\n')
        with patch.object(source_adapters.sys, 'version_info', (3, 11)):
            with self.assertRaisesRegex(ValueError, 'Python 3.12'):
                detect(self.root)


if __name__ == '__main__':
    unittest.main()
