"""Validate explicit owner completion metadata independently of MyAtlas."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path, PurePosixPath
import re

SECRETS = re.compile(
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
    r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|'
    r'(?i:(?:password|passwd|api[_-]?key|access[_-]?token|secret)\s*[=:]\s*["\'][^"\'\n]{4,}["\'])'
)


def validate_completion(value):
    if not isinstance(value, dict) or set(value) != {'project_id', 'status', 'attested_by', 'observed_at'}:
        raise ValueError('Completion requires exact project_id/status/attested_by/observed_at fields')
    if type(value['project_id']) is not int or value['project_id'] <= 0:
        raise ValueError('Explicit positive Hyperskill Project ID required')
    if value['status'] != 'completed' or value['attested_by'] != 'owner':
        raise ValueError('Explicit owner completion attestation required')
    stamp = value['observed_at']
    if not isinstance(stamp, str) or not stamp.endswith('Z'):
        raise ValueError('UTC observation timestamp required')
    if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', stamp):
        raise ValueError('Exact UTC completion timestamp required')
    if datetime.fromisoformat(stamp.replace('Z', '+00:00')) > datetime.now(timezone.utc):
        raise ValueError('Completion timestamp is in the future')
    return value


def validate_source_only_export(directory, manifest):
    """Validate one exact schema-3 source-only archive without executing it."""
    directory = Path(directory)
    required = {'schema', 'mode', 'language', 'directory_name', 'project_id', 'completion', 'files'}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError('Source-only manifest has unexpected or missing fields')
    if type(manifest['schema']) is not int or manifest['schema'] != 3 or manifest['mode'] != 'source-only':
        raise ValueError('Source-only schema 3 required')
    language = manifest['language']
    if language not in ('java', 'python') or manifest['directory_name'] != directory.name:
        raise ValueError('Source-only language/directory mismatch')
    if type(manifest['project_id']) is not int or manifest['project_id'] <= 0:
        raise ValueError('Exact positive Project ID required')
    completion = validate_completion(manifest['completion'])
    if completion['project_id'] != manifest['project_id']:
        raise ValueError('Manifest Project ID conflicts with completion attestation')
    files = manifest['files']
    if not isinstance(files, dict) or not files:
        raise ValueError('Non-empty source-only file inventory required')
    code_suffix = '.java' if language == 'java' else '.py'
    resources = {'.txt', '.json', '.csv'}
    code_count = 0
    for name, expected in files.items():
        if not isinstance(name, str) or not name or '\\' in name or ':' in name:
            raise ValueError('Unsafe source-only path')
        member = PurePosixPath(name)
        if member.is_absolute() or member.as_posix() != name or len(member.parts) < 2 or member.parts[0] != 'src' or any(p in ('', '.', '..') or p.startswith('.') for p in member.parts):
            raise ValueError('Unsafe source-only path')
        if member.suffix.lower() == code_suffix:
            code_count += 1
        elif member.suffix.lower() not in resources:
            raise ValueError('Unsupported source-only file type: ' + name)
        if not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{64}', expected):
            raise ValueError('Invalid source-only SHA-256: ' + name)
        target = directory.joinpath(*member.parts)
        current = directory
        for part in member.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError('Symlink source-only member refused')
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Source-only file hash mismatch: ' + name)
        try:
            text = target.read_text(encoding='utf-8')
        except UnicodeDecodeError as error:
            raise ValueError('Source-only archive member is not UTF-8 text: ' + name) from error
        if SECRETS.search(text):
            raise ValueError('Possible secret in source-only archive member: ' + name)
    if not code_count:
        raise ValueError('At least one final solution source file is required')

    readme = directory / 'README.md'
    marker = directory / '.hyperskill-import.json'
    if not readme.is_file() or readme.is_symlink() or not marker.is_file() or marker.is_symlink():
        raise ValueError('Source-only export requires a regular README and manifest')
    actual = set()
    for path in directory.rglob('*'):
        if path.is_symlink():
            raise ValueError('Symlink in source-only export')
        if path.is_file():
            actual.add(path.relative_to(directory).as_posix())
        elif not path.is_dir():
            raise ValueError('Special file in source-only export')
    if actual != set(files) | {'README.md', '.hyperskill-import.json'}:
        raise ValueError('Source-only inventory does not exactly cover the archive')
    urls = set(map(int, re.findall(r'https://hyperskill\.org/projects/([1-9][0-9]*)(?![0-9])', readme.read_text(encoding='utf-8'))))
    if urls != {manifest['project_id']}:
        raise ValueError('README Project ID does not match the manifest')
    return manifest


# Contract 4.0 validation mirrors the reviewed MyAtlas reader at dc5870e.
# Cross-repository regression tests check producer/reader acceptance parity.
import unicodedata
HASH = re.compile(r'[a-f0-9]{64}')

# Schema 4 is selected by explicit identity and roles, never language/extensions.
MAX_PROJECT_ID = 2**53 - 1  # Exact across Python, JSON and the browser.
PRIVATE_NAME = re.compile(
    r'^(?:\.env(?:\..*)?|id_(?:rsa|ed25519)|.*\.(?:pem|key))$|'
    r'(?:^|[._-])(?:secrets?|credentials?|private|passwords?|tokens?)(?:[._-]|$)', re.I)
SECRETS = re.compile(
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
    r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|'
    r"(?i:(?:password|passwd|api[_-]?key|access[_-]?token|secret)\s*[=:]\s*[\"'][^\"'\n]{4,}[\"'])")
EXCLUDED = {'node_modules', '__pycache__', 'venv', 'env', 'target', 'dist'}
RESERVED = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
            *(f'LPT{i}' for i in range(1, 10))}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key in export manifest')
        result[key] = value
    return result


def universal_path(name):
    if not isinstance(name, str) or not name or unicodedata.normalize('NFC', name) != name:
        raise ValueError('Unsafe universal archive path')
    member = PurePosixPath(name)
    if name == 'README.md':
        return member
    if member.is_absolute() or member.as_posix() != name or len(member.parts) < 2 or member.parts[0] != 'solution':
        raise ValueError('Universal members must stay below solution/')
    for part in member.parts:
        if (part.startswith('.') or part.endswith((' ', '.')) or
                any(unicodedata.category(c).startswith('C') or c in '\\<>:"|?*' for c in part) or
                part.split('.', 1)[0].upper() in RESERVED or
                part.casefold() in EXCLUDED or PRIVATE_NAME.search(part)):
            raise ValueError('Unsafe/private universal archive path')
    return member


def public_text(raw, label, *, code=False):
    # Resource bytes remain resources; they never become code or Topic evidence.
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as error:
        if code:
            raise ValueError('Solution code must be UTF-8 text: ' + label) from error
        text = raw.decode('utf-8', errors='replace')
    if code and any(unicodedata.category(c) == 'Cc' and c not in '\n\r\t' for c in text):
        raise ValueError('Binary/control content is not solution code: ' + label)
    if SECRETS.search(text):
        raise ValueError('Possible secret in archive (contents withheld): ' + label)
    return text


def _universal_attestation(value):
    if not isinstance(value, dict) or set(value) != {'project_id', 'status', 'attested_by', 'observed_at'}:
        raise ValueError('Exact owner attestation fields required')
    if type(value['project_id']) is not int or value['project_id'] <= 0 or value['status'] != 'completed' or value['attested_by'] != 'owner':
        raise ValueError('Exact positive ID and owner completion required')
    stamp = value['observed_at']
    if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z', stamp):
        raise ValueError('UTC observation timestamp required')
    datetime.fromisoformat(stamp.replace('Z', '+00:00'))


def validate_universal_export(directory, manifest):
    directory = Path(directory)
    if directory.is_symlink() or any(p.is_symlink() for p in directory.parents):
        raise ValueError('Symlink archive parent refused')
    if not isinstance(manifest, dict):
        raise ValueError('Universal manifest must be an object')
    required = {'schema', 'mode', 'project_id', 'project_url', 'title', 'completion', 'files'}
    if not required <= set(manifest) or set(manifest) - required - {'languages'}:
        raise ValueError('Exact universal schema-4 manifest fields required')
    if type(manifest['schema']) is not int or manifest['schema'] != 4 or manifest['mode'] != 'code-archive':
        raise ValueError('Universal schema 4 / code-archive mode required')
    pid = manifest['project_id']
    if type(pid) is not int or not 0 < pid <= MAX_PROJECT_ID or directory.name != str(pid):
        raise ValueError('Exact positive Project ID and canonical projects/<ID> required')
    if manifest['project_url'] != f'https://hyperskill.org/projects/{pid}':
        raise ValueError('Exact Hyperskill Project URL required')
    title = manifest['title']
    if not isinstance(title, str) or not title.strip() or title != title.strip() or any(unicodedata.category(c).startswith('C') for c in title):
        raise ValueError('Non-empty public project title required')
    languages = manifest.get('languages', [])
    if not isinstance(languages, list) or any(not isinstance(v, str) or not v.strip() or v != v.strip() or any(unicodedata.category(c).startswith('C') for c in v) for v in languages):
        raise ValueError('Languages must be optional descriptive strings')
    if len({v.casefold() for v in languages}) != len(languages):
        raise ValueError('Duplicate language metadata')
    completion = manifest['completion']
    fields = {'project_id', 'status', 'attested_by', 'confirmed_at'}
    if not isinstance(completion, dict) or not fields <= set(completion) or set(completion) - fields - {'completed_at'}:
        raise ValueError('Exact universal owner completion fields required')
    _universal_attestation(dict(project_id=completion['project_id'], status=completion['status'],
                             attested_by=completion['attested_by'], observed_at=completion['confirmed_at']))
    if completion['project_id'] != pid:
        raise ValueError('Ambiguous Project ID in completion')
    if 'completed_at' in completion:
        _universal_attestation(dict(project_id=pid, status='completed', attested_by='owner', observed_at=completion['completed_at']))
        if datetime.fromisoformat(completion['completed_at'].replace('Z', '+00:00')) > datetime.fromisoformat(completion['confirmed_at'].replace('Z', '+00:00')):
            raise ValueError('Actual completion cannot follow owner confirmation')
    files = manifest['files']
    if not isinstance(files, dict) or not files:
        raise ValueError('Non-empty universal file inventory required')
    if not isinstance(files.get('README.md'), dict) or files['README.md'].get('role') != 'resource':
        raise ValueError('README.md must be inventoried as a resource')
    # Inspect the entire tree before opening any members (including parents).
    actual = set()
    for item in directory.rglob('*'):
        if item.is_symlink() or not (item.is_file() or item.is_dir()):
            raise ValueError('Symlink/special universal archive member refused')
        name = item.relative_to(directory).as_posix()
        if name not in ('README.md', '.hyperskill-import.json', 'solution'):
            universal_path(name)
        if item.is_file():
            actual.add(name)
    if actual != set(files) | {'.hyperskill-import.json'}:
        raise ValueError('Universal inventory must cover every archived file exactly')
    # Reject aliases on case-insensitive/Unicode-normalizing filesystems,
    # including directories shared by otherwise distinct file names.
    aliases = {}
    code_count = 0
    for name, entry in files.items():
        member = universal_path(name)
        for i in range(1, len(member.parts) + 1):
            prefix = '/'.join(member.parts[:i])
            alias = prefix.casefold()
            if alias in aliases and aliases[alias] != prefix:
                raise ValueError('Case-colliding universal archive paths')
            aliases[alias] = prefix
        if not isinstance(entry, dict) or set(entry) != {'sha256', 'role'} or entry['role'] not in ('solution', 'resource'):
            raise ValueError('Exact sha256/role inventory entry required')
        if not isinstance(entry['sha256'], str) or not HASH.fullmatch(entry['sha256']):
            raise ValueError('Invalid SHA-256 inventory entry')
        raw = directory.joinpath(*member.parts).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Export content does not match manifest: ' + name)
        code = entry['role'] == 'solution'
        public_text(raw, name, code=code)
        code_count += code
    if not code_count:
        raise ValueError('At least one explicitly selected solution file required')
    public_text((directory / 'README.md').read_bytes(), 'README.md', code=True)
    def check_metadata(value):
        if isinstance(value, str):
            public_text(value.encode('utf-8'), 'manifest metadata', code=True)
        elif isinstance(value, dict):
            for key, item in value.items():
                check_metadata(key)
                check_metadata(item)
        elif isinstance(value, list):
            for item in value:
                check_metadata(item)
    check_metadata(manifest)
    return dict(project_id=pid, status='completed', attested_by='owner', observed_at=completion['confirmed_at'])
