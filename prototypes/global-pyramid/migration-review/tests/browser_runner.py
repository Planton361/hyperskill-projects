"""All publication/approval in this harness is confined to a temporary root."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('review_tests',BASE/'test_review.py');T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T);M=T.M
with tempfile.TemporaryDirectory() as d:
    home=Path(d);root=home/'root';T.clone(root);folder=home/'review';m=M.make_package(root,M.BASE.parent/'migration-preview',folder);seal=M.approve(root,folder/'migration-manifest.json',m['manifest_fingerprint']);applied=M.apply_test(root,folder/'migration-manifest.json',seal);validation=M.validate_installed(root,folder/'migration-manifest.json',m['manifest_fingerprint']);replay=M.apply_test(root,folder/'migration-manifest.json',seal)
    result=subprocess.run(['node',str(BASE/'browser.cjs'),str(M.BASE/'packages/accepted-v6-to-canonical-a-r3'),str(root/'docs/knowledge-map')],check=True,capture_output=True,text=True)
    (BASE/'browser-console.txt').write_text(result.stdout+result.stderr)
    (BASE/'disposable-apply-results.json').write_bytes(M.encoded(dict(fixture_only=True,applied=applied,validation=validation,replay=replay,layout_regenerated=False,source_generation=0,target_generation=1,knowledge_unchanged=M.tree(root/'data/knowledge')==M.tree(M.ROOT/'data/knowledge'))))
