#!/usr/bin/env python3
"""Validate committed source archive evidence without running exported code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from export_metadata import validate_completion, validate_source_only_export, validate_universal_export, unique_object, universal_path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_STATEMENT = 'Completed as part of [Hyperskill](https://hyperskill.org/projects/113).'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def _safe_legacy_path(name):
    path = Path(name)
    return (not path.is_absolute() and '\\' not in name and path.as_posix() == name and
            '..' not in path.parts and not any(part.startswith('.') for part in path.parts))


def validate(root, allow_empty=False, revision='HEAD'):
    root = Path(root).resolve(strict=True)
    tree = git(root, 'ls-tree', '-rz', revision)
    entries = {}
    for item in tree.split(b'\0'):
        if item:
            metadata, raw_name = item.split(b'\t', 1)
            entries[raw_name.decode()] = metadata.decode().split()
    markers = sorted(name for name in entries
                     if len(name.split('/')) == 3 and name.endswith('/.hyperskill-import.json'))
    if not markers and not allow_empty:
        raise ValueError('No committed project archives')
    if any(name.split('/')[0] not in ('java', 'python', 'projects') for name in markers):
        raise ValueError('Unsupported archive language')
    for name in entries:
        if name.split('/')[0] in ('java', 'python', 'projects'):
            if name in ('java/README.md', 'python/README.md') and entries[name][:2] == ['100644', 'blob']:
                continue  # Existing namespace documentation, never project evidence.
            if len(name.split('/')) < 3:
                raise ValueError('Non-directory/orphan archive namespace member')
            prefix = '/'.join(name.split('/')[:2])
            if prefix + '/.hyperskill-import.json' not in markers:
                raise ValueError('Project directory missing archive manifest: ' + name)
            mode, kind, oid = entries[name]
            if mode not in ('100644', '100755') or kind != 'blob':
                raise ValueError('Non-regular archive Git object refused before reading blobs')
            relative = name[len(prefix) + 1:]
            if prefix.startswith('projects/') and relative != '.hyperskill-import.json':
                universal_path(relative)
            elif not prefix.startswith('projects/') and relative != '.hyperskill-import.json' and not _safe_legacy_path(relative):
                raise ValueError('Unsafe committed archive path')

    results, seen = [], set()
    with tempfile.TemporaryDirectory(prefix='validated-source-archives-') as folder:
        folder = Path(folder).resolve()
        for marker in markers:
            prefix = marker.rsplit('/', 1)[0]
            target = Path(folder) / prefix
            for name in sorted(name for name in entries if name.startswith(prefix + '/')):
                mode, kind, oid = entries[name]
                if mode not in ('100644', '100755') or kind != 'blob':
                    raise ValueError('Non-regular archive member')
                relative = name[len(prefix) + 1:]
                if prefix.startswith('projects/') and relative != '.hyperskill-import.json':
                    universal_path(relative)
                elif not prefix.startswith('projects/') and relative != '.hyperskill-import.json' and not _safe_legacy_path(relative):
                    raise ValueError('Unsafe committed archive path')
                path = Path(folder) / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(git(root, 'cat-file', 'blob', oid))
                if mode == '100755':
                    path.chmod(0o755)
            manifest = json.loads((target / '.hyperskill-import.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)
            language = prefix.split('/')[0]
            if not isinstance(manifest, dict):
                raise ValueError('Archive manifest must be an object')
            if language == 'projects':
                validate_universal_export(target, manifest)
                pid = manifest['project_id']
            elif manifest.get('schema') == 3:
                validate_source_only_export(target, manifest)
                pid = manifest['project_id']
                if manifest['language'] != language:
                    raise ValueError('Source-only archive folder language mismatch')
            elif manifest.get('schema') == 2:
                if manifest.get('language') != language or manifest.get('directory_name') != target.name:
                    raise ValueError('Invalid legacy export identity')
                files = manifest.get('files')
                if not isinstance(files, dict) or not files:
                    raise ValueError('Legacy export file manifest required')
                actual = {path.relative_to(target).as_posix() for path in target.rglob('*') if path.is_file()}
                if actual != set(files) | {'README.md', '.hyperskill-import.json'}:
                    raise ValueError('Unmanifested legacy export files')
                for name, expected in files.items():
                    if not _safe_legacy_path(name) or not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{64}', expected):
                        raise ValueError('Unsafe legacy export inventory')
                    if hashlib.sha256((target / name).read_bytes()).hexdigest() != expected:
                        raise ValueError('Legacy export manifest hash mismatch')
                completion = manifest.get('completion')
                if completion:
                    validate_completion(completion)
                    pid = completion['project_id']
                    if manifest.get('project_id') != pid:
                        raise ValueError('Exact Project ID missing/conflicting')
                elif (prefix == 'java/Simple Chat Bot with Java' and
                      LEGACY_STATEMENT in (target / 'README.md').read_text().splitlines()):
                    pid = 113
                else:
                    raise ValueError('Owner completion attestation missing')
                if language == 'java' and not any(
                        name.startswith('src/main/java/') and name.endswith('.java') for name in files):
                    raise ValueError('Legacy Java export has no solution source')
                if language == 'python':
                    if manifest.get('python_version') != '3.12' or manifest.get('dependencies') != []:
                        raise ValueError('Unsupported legacy Python archive metadata')
                    if manifest.get('entrypoint') not in files or not manifest['entrypoint'].endswith('.py'):
                        raise ValueError('Legacy Python entrypoint missing')
            else:
                raise ValueError('Unsupported export manifest schema')

            readme = (target / 'README.md').read_text(encoding='utf-8')
            urls = set(map(int, re.findall(r'https://hyperskill\.org/projects/([0-9]+)(?![0-9])', readme)))
            if (urls and urls != {pid} if language == 'projects' else urls != {pid}) or pid in seen:
                raise ValueError('Duplicate or conflicting Project ID')
            seen.add(pid)
            results.append(dict(project_id=pid, language=language,
                                archive_mode={4: 'code-archive', 3: 'source-only', 2: 'legacy-schema-2'}[manifest['schema']],
                                status='PASS'))
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(validate(args.repository), indent=2))
