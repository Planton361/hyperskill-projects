"""Read-only projection and frozen-source integrity; no regeneration/migration."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('global_v66_build', HERE.parent / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
assert json.loads((HERE.parent / 'model.json').read_text()) == json.loads(json.dumps(builder.project())), 'Stale catalog projection'
before = json.loads((HERE / 'protected-source.json').read_text())
for file, expected in before.items():
    assert hashlib.sha256((ROOT / file).read_bytes()).hexdigest() == expected, file
result = dict(catalog_projection='current', protected_files=len(before), protected_content='byte-identical')
(HERE / 'generated').mkdir(exist_ok=True)
(HERE / 'generated/integrity.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
