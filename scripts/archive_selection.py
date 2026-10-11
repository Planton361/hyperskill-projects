"""Owner file selection and byte-only inspection; no language admission or builds."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import unicodedata

from export_metadata import public_text, universal_path, unique_object, MAX_PROJECT_ID
from source_adapters import PLATFORM_TEST, unsafe_source_path

BLOCKED = {'.git', '.idea', '.vscode', '.settings', '.metadata', '.fleet', '.run',
           '.gradle', '.m2', '.cache', '.venv', '.pytest_cache', '.mypy_cache',
           '.ruff_cache', 'venv', 'node_modules', 'build', 'target', 'out', 'dist',
           'coverage', 'generated', 'generated-sources', 'generated-test-sources',
           'frameworkLessonHistory', '.hyperskill', '.education', '__pycache__'}


def inventory(root):
    entries = []
    for parent, dirs, files in os.walk(root, followlinks=False,
                                      onerror=lambda error: (_ for _ in ()).throw(error)):
        entries.extend((Path(parent) / name).relative_to(root) for name in sorted(dirs + files))
    return sorted(entries)


def excluded(path):
    if any(part in BLOCKED or part.startswith('.author_contents_storage_db') for part in path.parts):
        return 'IDE/Git/build/dependency/cache/history'
    if path.name == 'task.html' or path.name.endswith('-info.yaml'):
        return 'Academy metadata/task statement'
    if path.name in {'gradlew', 'gradlew.bat', 'pom.xml', 'requirements.txt', 'package.json',
                     'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'pyproject.toml',
                     'Pipfile', 'Pipfile.lock', 'Cargo.toml', 'Cargo.lock', 'go.mod', 'go.sum'} or path.name.endswith(('.gradle', '.gradle.kts')):
        return 'Academy/dependency build configuration'
    if path.name.endswith(('.tmp', '.swp', '.bak', '.log', '.class', '.pyc', '.pyo', '~')):
        return 'temporary/generated file'
    if 'test' in path.parts or 'tests' in path.parts or re.search(r'(?i)(?:^|[_-])tests?(?:[_-]|\.)', path.name):
        return 'tests (explicit selection required for ambiguous owner code)'
    return None


def title_from_source(source, override=None):
    if override is not None:
        return public_title(override)
    marker = source / 'course-info.yaml'
    if marker.is_symlink() or not marker.is_file():
        raise ValueError('Project title missing; supply --title.')
    matches = re.findall(r'(?m)^title:\s*(.*?)\s*$', marker.read_text(encoding='utf-8'))
    if len(matches) != 1:
        raise ValueError('Project title ambiguous; supply --title.')
    value = matches[0]
    if value.startswith('"'):
        return public_title(json.loads(value))
    if value.startswith("'") and value.endswith("'"):
        return public_title(value[1:-1].replace("''", "'"))
    return public_title(re.split(r'\s+#', value, maxsplit=1)[0].strip())


def public_title(value):
    if not isinstance(value, str) or not value or value != value.strip() or any(unicodedata.category(c).startswith('C') for c in value):
        raise ValueError('Trimmed non-empty public title required')
    public_text(value.encode('utf-8'), 'project title', code=True)
    return value


def identity(source, explicit=None):
    marker = source / 'course-remote-info.yaml'
    ids = []
    if marker.is_symlink():
        raise ValueError('Symlink identity metadata refused')
    if marker.is_file():
        text = marker.read_text(encoding='utf-8')
        blocks = re.findall(r'(?m)^hyperskill_project:\s*\n((?:[ \t]+[^\n]*\n?)*)', text)
        if len(blocks) > 1 or (not blocks and 'hyperskill_project:' in text):
            raise ValueError('Academy identity ambiguous or unsupported; review metadata')
        block = blocks[0] if blocks else ''
        values = re.findall(r'(?m)^  id:\s*(.*?)\s*$', block)
        urls = re.findall(r'https://hyperskill.org/api/projects/([^/\s]+)/', block)
        if len(values) > 1 or any(not re.fullmatch(r'[1-9][0-9]*', v) for v in values + urls):
            raise ValueError('Invalid or ambiguous Academy Project ID')
        ids = list(map(int, values + urls))
        if len(set(ids)) > 1:
            raise ValueError('Academy Project ID ambiguous')
    if explicit is not None:
        if not re.fullmatch(r'https://hyperskill\.org/projects/[1-9][0-9]*', explicit):
            raise ValueError('Exact Hyperskill URL required (no trailing slash/query/fragment)')
        pid = int(explicit.rsplit('/', 1)[-1])
        if ids and set(ids) != {pid}:
            raise ValueError('Explicit Project ID conflicts with Academy metadata')
    elif ids:
        pid = ids[0]
    else:
        raise ValueError('Project identity missing; supply --project-url.')
    if not 0 < pid <= MAX_PROJECT_ID:
        raise ValueError('Project ID outside exact positive JSON integer range')
    return pid, f'https://hyperskill.org/projects/{pid}'


def select(source, title, files_from=None):
    """Return exact workspace-relative paths and explicit/proposed roles."""
    entries = inventory(source)
    # Never follow/open a workspace symlink or special file, even if omitted.
    for relative in entries:
        path = source / relative
        if unsafe_source_path(relative) or any(unicodedata.category(c).startswith('C') for c in str(relative)):
            raise ValueError('Unsafe path in workspace (contents withheld)')
        public_text(str(relative).encode('utf-8'), 'workspace path', code=True)
        if path.is_symlink():
            raise ValueError('Symlink in source workspace refused: ' + str(relative))
        if not (path.is_file() or path.is_dir()):
            raise ValueError('Special file in source workspace refused: ' + str(relative))
    if files_from:
        choice = Path(files_from).absolute()
        if any(p.is_symlink() for p in (choice, *choice.parents)) or not choice.is_file():
            raise ValueError('Selection must be a regular file without symlink parents')
        declaration = json.loads(choice.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        if not isinstance(declaration, dict) or set(declaration) != {'schema', 'files'} or type(declaration['schema']) is not int or declaration['schema'] != 1 or not isinstance(declaration['files'], dict):
            raise ValueError('Selection requires exact schema: 1 and files: {relative_path: role}')
        roles = declaration['files']
    else:
        tasks = [p for p in entries if p.name == 'task' and len(p.parts) == 2 and (source / p).is_dir() and not excluded(p)]
        named = [p for p in tasks if p.parts[0] == title]
        candidates = named if len(named) == 1 else tasks
        if len(candidates) != 1:
            raise ValueError('Expected one unambiguous final task; supply --files-from.')
        task = candidates[0]
        root = task / 'src' if (source / task / 'src').is_dir() else task
        roles = {p.as_posix(): 'solution' for p in entries if p.is_relative_to(root)
                 and (source / p).is_file() and not excluded(p)}
        print('Final source folder: ' + root.as_posix())
    if not roles or 'solution' not in roles.values():
        raise ValueError('Select at least one owner solution file; supply --files-from.')
    payload, aliases = {}, {}
    for relative, role in sorted(roles.items()):
        member = universal_path('solution/' + relative)
        if role not in ('solution', 'resource'):
            raise ValueError('Selection roles must be solution or resource')
        for i in range(2, len(member.parts) + 1):
            prefix = '/'.join(member.parts[:i])
            if prefix.casefold() in aliases and aliases[prefix.casefold()] != prefix:
                raise ValueError('Case-colliding selected paths')
            aliases[prefix.casefold()] = prefix
        path = source.joinpath(*member.parts[1:])
        if not path.is_file() or not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError('Missing/non-regular selected file: ' + relative)
        for parent in (path, *path.parents):
            if parent.is_symlink():
                raise ValueError('Symlink selected file/parent refused')
        raw = path.read_bytes()
        try:
            text = public_text(raw, relative, code=role == 'solution')
        except ValueError as error:
            if not files_from:
                raise ValueError(str(error) + '; use --files-from to declare safe solution/resource roles') from error
            raise
        if not files_from and PLATFORM_TEST.search(text):
            print('OMIT ' + relative + ': Academy platform test')
            continue
        payload[member.as_posix()] = (raw, role)
    if not any(role == 'solution' for raw, role in payload.values()):
        raise ValueError('No owner solution selected; supply --files-from.')
    selected = {name.removeprefix('solution/') for name in payload}
    for relative in entries:
        if relative.as_posix() not in selected:
            print('OMIT ' + relative.as_posix() + ': ' + (excluded(relative) or 'not selected'))
    return payload


def fingerprint(payload):
    return {name: {'sha256': hashlib.sha256(raw).hexdigest(), 'role': role}
            for name, (raw, role) in sorted(payload.items())}
