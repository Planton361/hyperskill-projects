"""Complete archive/index acceptance without an application build or imported-code execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from acceptance_context import isolated_myatlas_environment
from project_index import generate, encode, git, validate_index, sha

MIN_READER = '266c1195d5552753f3a63246ec1591ccc5c2b332'


def validate_data(root, atlas, revision):
    root, atlas = Path(root).resolve(), Path(atlas).resolve()
    first = generate(root, revision); second = generate(root, revision)
    if first != second:
        raise ValueError('Non-reproducible index bytes')
    validate_index(root, first, revision)
    if subprocess.run(['git','-C',str(atlas),'merge-base','--is-ancestor',MIN_READER,'HEAD'],capture_output=True).returncode:
        raise ValueError('Merged Phase-4 reader required; incompatible fallback refused')
    if git(atlas,'remote','get-url','origin').decode().strip().removesuffix('.git') != 'https://github.com/Planton361/myatlas':
        raise ValueError('Wrong MyAtlas repository')
    # Existing committed scanner and serializer bind exact identities to the trusted catalog.
    code = '''import json,sys; from pathlib import Path
sys.path.insert(0,sys.argv[1])
from scripts.knowledge_atlas.external_completion import external_inputs,project_external
root,evidence=Path(sys.argv[1]),Path(sys.argv[2])
print(json.dumps(dict(inputs=external_inputs(root,evidence,sys.argv[3]),expected=project_external(root,evidence,sys.argv[3])['projection'])))'''
    raw = subprocess.check_output([sys.executable,'-B','-c',code,str(atlas),str(root),revision],env=isolated_myatlas_environment())
    data = json.loads(raw)
    data.update(index=first.decode('utf-8'),revision=revision,
                binding=dict(application_revision=git(atlas,'rev-parse','HEAD').decode().strip(),
                             catalog_sha256=sha(git(atlas,'show','HEAD:src/myatlas/knowledge-atlas-scope-pyramid/catalog.json')),scopes_sha256=sha(git(atlas,'show','HEAD:src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json'))))
    report = json.loads(subprocess.check_output(['node',str(Path(__file__).with_name('project-data-contract.cjs')),str(atlas)],input=json.dumps(data).encode(),env=isolated_myatlas_environment()))
    report.update(revision=revision,index_sha256=hashlib.sha256(first).hexdigest(),
                  checks=['committed archives','deterministic index twice','independent index validator','merged browser wire contract','accepted catalog analytics parity'],
                  browser_build='not required for archive data',next_step='Owner reviews and manually merges; index publication remains gated')
    return report
