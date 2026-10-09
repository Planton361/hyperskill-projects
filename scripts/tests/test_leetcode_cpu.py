import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cpu_build', ROOT / 'scripts/build-leetcode-atlas.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CpuPublication(unittest.TestCase):
    def test_exact_accepted_source_and_metadata(self):
        baseline = builder.validate_snapshot()
        self.assertEqual(baseline['geometrySHA256'], 'c23469da99adc627db3a52d89d316082e53514d8d7210e46c1b13cc8296504a6')
        catalog = json.loads((builder.SOURCE / 'data/catalog.json').read_text())
        fields = {'displayNumber', 'title', 'slug', 'difficulty', 'topicTags', 'premium', 'id', 'platform', 'site', 'catalog',
                  'officialQuestionId', 'canonicalUrl', 'urlAliases', 'tagsCompleteness', 'primaryTaxonomyId',
                  'secondaryTaxonomyIds', 'placement', 'studyPlanIds', 'catalogStatus', 'provenance'}
        for row in catalog['problems']:
            self.assertEqual(set(row), fields)
        for name in baseline['localEvaluationInputs']:
            text = (builder.SOURCE / 'data' / name).read_text()
            for forbidden in ['github_pat_', 'ghp_', 'Authorization', '/Users/', '/var/folders/', 'localhost', '127.0.0.1']:
                self.assertNotIn(forbidden, text)

    def test_public_refresh_never_rebuilds_geometry(self):
        source = builder.adapt_cpu((builder.SOURCE / 'app.js').read_text())
        hook = source[source.index('function setPublicProgress(value)'):source.index('window.LeetCodeAtlas={')]
        for forbidden in ['layout(', 'V.compile(', 'M.validate(', 'M.buildHierarchy(']:
            self.assertNotIn(forbidden, hook)

    def test_sibling_and_license_notices(self):
        self.assertEqual(builder.OUTPUT, ROOT / 'build/pages/leetcode-atlas')
        self.assertIn('publisher declares MIT', (builder.SOURCE / 'NOTICE.txt').read_text())
        self.assertIn('separate LeetCode rights-holder grant', (builder.SOURCE / 'NOTICE.txt').read_text())
        self.assertIn('MIT License', (builder.SOURCE / 'LICENSE').read_text())


if __name__ == '__main__':
    unittest.main()
