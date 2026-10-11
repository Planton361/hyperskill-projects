"""Foreign GitHub contexts must not become an isolated MyAtlas build context."""
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
KEYS = ('GITHUB_SHA', 'GITHUB_REF', 'GITHUB_REF_NAME', 'GITHUB_REF_TYPE',
        'GITHUB_HEAD_REF', 'GITHUB_BASE_REF', 'MYATLAS_PRE_RELEASE_PROGRESS',
        'ACCEPTANCE_TOOLING_MARKER')
CONTEXTS = {
    'pull_request': dict(GITHUB_REF='refs/pull/17/merge', GITHUB_REF_NAME='17/merge',
                         GITHUB_HEAD_REF='feature', GITHUB_BASE_REF='main'),
    'main_push': dict(GITHUB_REF='refs/heads/main', GITHUB_REF_NAME='main',
                      GITHUB_HEAD_REF='', GITHUB_BASE_REF=''),
}
PROBE = ('import json, os; from pathlib import Path; '
         f'value = {{key: os.environ.get(key) for key in {KEYS!r}}}; ')


class AcceptanceContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            cls.growth = runpy.run_path(str(ROOT / 'scripts/test-portfolio-growth.py'))
            cls.single = runpy.run_path(str(ROOT / 'scripts/test-cross-repository.py'))
        finally:
            sys.path.remove(str(ROOT / 'scripts'))

    def foreign_context(self, context):
        return dict(context, GITHUB_SHA='1' * 40, GITHUB_REF_TYPE='branch',
                    MYATLAS_PRE_RELEASE_PROGRESS='0', ACCEPTANCE_TOOLING_MARKER='preserved')

    def assert_isolated(self, actual):
        for key in KEYS[:6]:
            self.assertIsNone(actual.get(key), key)
        self.assertEqual(actual['MYATLAS_PRE_RELEASE_PROGRESS'], '1')
        self.assertEqual(actual['ACCEPTANCE_TOOLING_MARKER'], 'preserved')

    def test_both_helpers_isolate_pr_and_main_without_mutating_parent(self):
        for name, context in CONTEXTS.items():
            for helper in (self.growth, self.single):
                with self.subTest(context=name, helper=helper['__file__']), \
                        patch.dict(os.environ, self.foreign_context(context)):
                    parent = dict(os.environ)
                    env = helper['isolated_myatlas_environment']()
                    self.assert_isolated(env)
                    self.assertEqual(dict(os.environ), parent)
                    self.assertEqual(env['PATH'], parent['PATH'])

    def test_real_child_processes_receive_isolation_in_pr_and_main_context(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'context.json'
            for name, context in CONTEXTS.items():
                for helper, function in ((self.growth, 'execute'), (self.single, 'call')):
                    with self.subTest(context=name, function=function), \
                            patch.dict(os.environ, self.foreign_context(context)):
                        env = helper['isolated_myatlas_environment']()
                        program = PROBE + f'Path({str(output)!r}).write_text(json.dumps(value))'
                        helper[function]([sys.executable, '-B', '-c', program], folder, env=env)
                        self.assert_isolated(json.loads(output.read_text()))

    def test_growth_projection_receives_isolation_in_pr_and_main_context(self):
        with tempfile.TemporaryDirectory() as folder:
            atlas = Path(folder)
            script = atlas / 'scripts/sync-hyperskill-projects.py'
            script.parent.mkdir()
            script.write_text(PROBE + 'print(json.dumps({"projection": value}))')
            for name, context in CONTEXTS.items():
                with self.subTest(context=name), \
                        patch.dict(os.environ, self.foreign_context(context)):
                    env = self.growth['isolated_myatlas_environment']()
                    self.assert_isolated(self.growth['projection'](atlas, atlas, env))


if __name__ == '__main__':
    unittest.main()
