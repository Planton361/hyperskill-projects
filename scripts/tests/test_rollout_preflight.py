"""Read-only preflight rejects a changed baseline before claiming rollout readiness."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('preflight',ROOT/'scripts/preflight-project-index.py')
preflight=importlib.util.module_from_spec(spec);spec.loader.exec_module(preflight)

class RolloutPreflightTests(unittest.TestCase):
    def test_nonreproducible_payload_fails_before_any_publication(self):
        with patch.object(preflight,'generate',side_effect=[b'a',b'b']):
            with self.assertRaisesRegex(ValueError,'reproducible'):preflight.preflight(ROOT,ROOT,'a'*40)
    def test_selected_baseline_hashes_are_mandatory(self):
        with tempfile.TemporaryDirectory() as folder:
            atlas=Path(folder);p=atlas/'docs/contracts/hyperskill-baseline-v1.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps({'archive_sha256':{'existing':'0'*64}}))
            with patch.object(preflight,'generate',return_value=b'{"projects":[]}'),patch.object(preflight,'validate_index'),patch.object(preflight,'tree',return_value={'existing':['100644','blob','a'*40]}),patch.object(preflight,'blob',return_value=b'tampered'):
                with self.assertRaisesRegex(ValueError,'Baseline archive'):preflight.preflight(ROOT,atlas,'a'*40)
    def test_preflight_has_no_store_pointer_or_remote_mutations(self):
        source=(ROOT/'scripts/preflight-project-index.py').read_text()
        self.assertNotIn('project_index_store',source);self.assertNotIn("'push'",source)
        self.assertNotIn('stage(',source);self.assertNotIn('PROJECT_INDEX_ENABLED',source)
    def test_merged_phase5_provenance_survives_future_fixture_changes(self):
        contract=json.loads((ROOT/'scripts/templates/myatlas-acceptance.json').read_text())
        self.assertEqual(contract['review_commit'],'12377e3fac28817adcbdf2fca846828763c0dc99')
