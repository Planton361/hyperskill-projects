"""Contract-1 project data from committed blobs; never evaluate archive code."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import quote

from export_metadata import unique_object, public_text, universal_path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Planton361/hyperskill-projects'
ORIGIN = 'https://github.com/' + REPOSITORY
RAW = 'https://raw.githubusercontent.com/' + REPOSITORY
VERSION = '1.0'
IMPLEMENTATION = ('scripts/project_index.py', 'scripts/validate-project-exports.py',
                  'scripts/export_metadata.py')
SHA = re.compile(r'[a-f0-9]{40}')
HASH = re.compile(r'[a-f0-9]{64}')

def git(root, *args):
    env = dict(os.environ, GIT_NO_REPLACE_OBJECTS='1')
    return subprocess.check_output(['git', '-C', str(root), *args], env=env)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')

def decode(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-JSON number')))

def revision(root, value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError('Explicit full lowercase commit SHA required')
    if git(root, 'cat-file', '-t', value).strip() != b'commit':
        raise ValueError('Selected Git object must be a commit')
    return value

def repository(root):
    root = Path(root).resolve(strict=True)
    if git(root, 'remote', 'get-url', 'origin').decode().strip().removesuffix('.git') != ORIGIN:
        raise ValueError('Foreign or missing canonical repository origin')
    return root

def tree(root, rev):
    entries = {}
    for item in git(root, 'ls-tree', '-rz', rev).split(b'\0'):
        if item:
            metadata, name = item.split(b'\t', 1)
            entries[name.decode('utf-8')] = metadata.decode().split()
    return entries

def blob(root, oid):
    return git(root, 'cat-file', 'blob', oid)

def implementation(root, rev):
    value = git(root, 'log', '-1', '--format=%H', rev, '--', *IMPLEMENTATION).decode().strip()
    revision(root, value)
    entries = tree(root, value)
    for name in IMPLEMENTATION:
        if name not in entries or entries[name][:2] != ['100644', 'blob']:
            raise ValueError('Missing regular committed validator implementation')
    return value

def archive_validation(root, rev):
    # Reuse the existing accepted validator, with its Git replacement guard too.
    spec = importlib.util.spec_from_file_location('index_archive_validator', ROOT/'scripts/validate-project-exports.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.git = git
    return module.validate(root, revision=rev)

def code_url(rev, name):
    return ORIGIN + '/blob/' + rev + '/' + '/'.join(quote(p, safe='') for p in name.split('/'))

def safe_path(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Unsafe index path')
    p = PurePosixPath(name)
    if p.is_absolute() or p.as_posix() != name or '..' in p.parts or any(ord(c)<32 for c in name):
        raise ValueError('Unsafe index path')
    for part in p.parts:
        if part != '.hyperskill-import.json':
            universal_path('solution/'+part)
    return name

def identities(root, rev, entries, accepted):
    """Extract only validated identities and original owner attestations."""
    by_prefix = {}
    aliases={}
    for path in entries:
        if path.split('/')[0] not in ('java','python','projects') or len(path.split('/'))<3:
            continue
        safe_path(path)
        parts=path.split('/')
        for i in range(1,len(parts)+1):
            name='/'.join(parts[:i]);key=name.casefold()
            if key in aliases and aliases[key]!=name:
                raise ValueError('Case/Unicode alias in index archive paths')
            aliases[key]=name
    for marker in sorted(n for n in entries if n.endswith('/.hyperskill-import.json') and len(n.split('/')) == 3):
        prefix = marker.rsplit('/', 1)[0]
        m = decode(blob(root, entries[marker][2]))
        schema = m['schema']
        pid = m.get('project_id')
        completion = m.get('completion')
        if completion is None:
            if prefix != 'java/Simple Chat Bot with Java' or schema != 2:
                raise ValueError('Missing reviewed legacy identity')
            # Accepted MyAtlas observation of the reviewed README statement;
            # not a historical completion date inferred from Git or a clock.
            pid = 113
            completion = dict(project_id=113, status='completed', attested_by='owner',
                              observed_at='2026-10-08T00:00:00Z')
        if type(pid) is not int or not 0 < pid <= 9007199254740991 or type(schema) is not int:
            raise ValueError('Invalid exact index project identity/schema')
        title = m['title'] if schema == 4 else m.get('original_project_name', m.get('directory_name'))
        if not isinstance(title, str) or title != title.strip() or not title:
            raise ValueError('Public project title required')
        public_text(title.encode('utf-8'), 'index title')
        languages = m.get('languages') if schema == 4 else [m['language']]
        record = dict(project_id=pid, project_url=f'https://hyperskill.org/projects/{pid}',
                      title=title, archive_schema=schema, archive_path=prefix,
                      completion=completion, evidence_id=f'hyperskill:{pid}')
        if languages is not None:
            record['languages'] = languages
        by_prefix[prefix] = (record, m)
    if sorted(r[0]['project_id'] for r in by_prefix.values()) != sorted(r['project_id'] for r in accepted):
        raise ValueError('Index identities differ from archive validator')
    return by_prefix

def members(root, rev, prefix, manifest, entries):
    files = []
    for path in sorted(n for n in entries if n.startswith(prefix + '/')):
        safe_path(path)
        mode, kind, oid = entries[path]
        if mode not in ('100644','100755') or kind != 'blob':
            raise ValueError('Non-regular index Git object')
        relative = path[len(prefix)+1:]
        if relative == '.hyperskill-import.json':
            role = 'metadata'
        elif relative == 'README.md':
            role = 'resource'
        elif manifest['schema'] == 4:
            role = manifest['files'][relative]['role']
        else:
            suffix = '.java' if manifest['language'] == 'java' else '.py'
            role = 'solution' if relative.startswith('src/') and relative.endswith(suffix) else 'resource'
        raw=blob(root,oid)
        public_text(raw,'index member (contents withheld)')
        item = dict(path=path, git_blob=oid, sha256=sha(raw), role=role)
        if role == 'solution':
            item['code_url'] = code_url(rev, path)
        files.append(item)
    return files

def reference(member):
    return {k:member[k] for k in ('path','git_blob','sha256')}

def generate(root, rev):
    root = repository(root); revision(root, rev)
    accepted = archive_validation(root, rev)  # entire revision, before indexing
    impl = implementation(root, rev)
    # Build only with exactly the committed reviewed implementation, never
    # execute validator code fetched from the source repository/revision.
    impl_entries = tree(root, impl)
    for name in IMPLEMENTATION:
        if (ROOT/name).read_bytes() != blob(root, impl_entries[name][2]):
            raise ValueError('Running validator differs from selected committed implementation')
    entries = tree(root, rev)
    projects = []
    for prefix, (record, m) in identities(root, rev, entries, accepted).items():
        files = members(root, rev, prefix, m, entries)
        record['files'] = files
        record['manifest'] = reference(next(f for f in files if f['role'] == 'metadata'))
        if m.get('completion') is None:
            record['manifest']['attestation'] = reference(next(f for f in files if f['path'] == prefix+'/README.md'))
        projects.append(record)
    return encode(dict(schema=1, kind='hyperskill-project-index', repository=REPOSITORY,
                       revision=rev, validator=dict(version=VERSION, implementation_revision=impl),
                       projects=sorted(projects, key=lambda p:p['project_id'])))

def validate_index(root, raw, expected_revision=None):
    """Independent read-side check against all committed blobs, not generator output."""
    root = repository(root)
    data = decode(raw)
    if not isinstance(data, dict) or set(data) != {'schema','kind','repository','revision','validator','projects'}:
        raise ValueError('Exact index fields required')
    if type(data['schema']) is not int or data['schema'] != 1 or data['kind'] != 'hyperskill-project-index' or data['repository'] != REPOSITORY:
        raise ValueError('Unsupported/foreign index identity')
    rev = revision(root, data['revision'])
    if expected_revision is not None and rev != expected_revision:
        raise ValueError('Index selected revision mismatch')
    validator = dict(version=VERSION, implementation_revision=implementation(root, rev))
    if data['validator'] != validator:
        raise ValueError('Invalid immutable validator provenance')
    accepted = archive_validation(root, rev)
    entries = tree(root, rev)
    records = identities(root, rev, entries, accepted)
    projects = data['projects']
    if not isinstance(projects, list) or len(projects) != len(records):
        raise ValueError('Full project inventory required')
    previous = 0
    for p in projects:
        if not isinstance(p, dict) or type(p.get('project_id')) is not int or p['project_id'] <= previous:
            raise ValueError('Projects must have unique sorted exact IDs')
        previous = p['project_id']
        prefix = p.get('archive_path')
        if prefix not in records:
            raise ValueError('Unknown archive path')
        base, m = records[prefix]
        if set(p) != set(base) | {'files','manifest'} or any(encode(p[k]) != encode(v) for k,v in base.items()):
            raise ValueError('Index metadata/attestation differs from committed evidence')
        expected = members(root, rev, prefix, m, entries)
        if encode(p['files']) != encode(expected):
            raise ValueError('Index full inventory/hash/blob/role/code URL mismatch')
        marker = reference(next(f for f in expected if f['role']=='metadata'))
        if m.get('completion') is None:
            marker['attestation'] = reference(next(f for f in expected if f['path']==prefix+'/README.md'))
        if p['manifest'] != marker:
            raise ValueError('Manifest/legacy attestation reference mismatch')
    if raw != encode(data):
        raise ValueError('Canonical deterministic JSON bytes required')
    return data

def index_url(store_commit, source_revision):
    if not SHA.fullmatch(store_commit) or not SHA.fullmatch(source_revision):
        raise ValueError('Immutable store/source commits required')
    return RAW+'/'+store_commit+'/portfolio/revisions/'+source_revision+'/index.json'

def pointer(source_revision, store_commit, raw):
    return encode(dict(schema=1, repository=REPOSITORY, revision=source_revision,
                       index_url=index_url(store_commit, source_revision), index_sha256=sha(raw)))

def validate_pointer(raw, payload):
    p = decode(raw); d = decode(payload)
    if not isinstance(p, dict) or set(p) != {'schema','repository','revision','index_url','index_sha256'}:
        raise ValueError('Exact current pointer fields required')
    if type(p['schema']) is not int or p['schema']!=1 or p['repository']!=REPOSITORY:
        raise ValueError('Unsupported/foreign pointer')
    rev = p['revision']
    if not isinstance(rev,str) or not SHA.fullmatch(rev) or d.get('revision')!=rev or d.get('repository')!=REPOSITORY:
        raise ValueError('Pointer/payload identity mismatch')
    pattern = re.escape(RAW)+r'/([a-f0-9]{40})/portfolio/revisions/'+rev+r'/index\.json'
    if not isinstance(p['index_url'],str) or not re.fullmatch(pattern,p['index_url']):
        raise ValueError('Untrusted/non-immutable index URL')
    if p['index_sha256']!=sha(payload) or raw!=encode(p):
        raise ValueError('Pointer/payload hash or encoding mismatch')
    return p
