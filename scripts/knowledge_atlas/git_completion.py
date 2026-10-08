"""Committed evidence reader. Git objects only; no checkout, index or history writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from .project_completion import scan
from .course_completion import validate_records

CATALOG = 'prototypes/knowledge-atlas-scope-pyramid/catalog.json'
SCOPES = 'prototypes/knowledge-atlas-scope-pyramid/scope-index.json'
ACCEPTED = 'prototypes/project-completion/accepted-sync.json'
LANGUAGES = ('java',)  # The current importer supports Java only.


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def committed_inputs(root, ref='HEAD'):
    commit = git(root, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    entries = {}
    for record in git(root, 'ls-tree', '-rz', commit).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        entries[name.decode()] = (mode, kind, oid)
    refs = []

    def read(name):
        mode, kind, oid = entries[name]
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('Non-regular committed evidence: ' + name)
        content = git(root, 'cat-file', 'blob', oid)
        refs.append(dict(path=name, git_blob=oid, sha256=hashlib.sha256(content).hexdigest()))
        return content

    catalog, scopes = json.loads(read(CATALOG)), json.loads(read(SCOPES))
    with tempfile.TemporaryDirectory(prefix='atlas-git-evidence-') as temp:
        destination = Path(temp)
        manifests = sorted(n for n in entries if len(n.split('/')) == 3 and
                           n.split('/')[0] in LANGUAGES and n.endswith('/.hyperskill-import.json'))
        for name in manifests:
            folder = name.rsplit('/', 1)[0]
            # Materialize committed export blobs only, never working-tree files.
            # A symlink anywhere in a candidate is a hard validation failure.
            for member in sorted(n for n in entries if n.startswith(folder + '/')):
                target = destination / member
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(read(member))
        completion = scan(destination, scopes)
    if completion['rejected']:
        raise ValueError('Rejected committed exports: ' + json.dumps(completion['rejected'], sort_keys=True))
    course_path = 'prototypes/project-completion/course-completions.json'
    completion['course_completion'] = validate_records(json.loads(read(course_path)) if course_path in entries else {'schema': 1, 'records': []}, scopes)
    baseline = next((p for p in (ACCEPTED, 'prototypes/project-completion/progress.json') if p in entries), None)
    previous = json.loads(read(baseline)) if baseline else None
    return dict(catalog=catalog, scopes=scopes, completion=completion, previous=previous,
                source=dict(commit=commit, evidence=sorted(refs, key=lambda r:r['path'])))
