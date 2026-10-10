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
