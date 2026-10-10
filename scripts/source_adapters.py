"""Read-only source-only adapters for final Hyperskill task folders."""
from pathlib import Path, PurePosixPath
import re
import sys


def fail(message):
    raise ValueError(message)


def workspace(path):
    path = Path(path).resolve(strict=True)
    if path.is_file():
        path = path.parent
    for candidate in (path, *path.parents):
        marker = candidate / 'course-info.yaml'
        if marker.is_file() and not marker.is_symlink():
            return candidate
    fail('Academy workspace not found: course-info.yaml required; supply its root directory.')


def project_url(source, explicit=None):
    ids = set()
    remote = source / 'course-remote-info.yaml'
    if remote.is_file() and not remote.is_symlink():
        text = remote.read_text(encoding='utf-8')
        blocks = re.findall(r'(?m)^hyperskill_project:\s*\n((?:[ \t]+[^\n]*\n?)*)', text)
        for block in blocks:
            ids.update(map(int, re.findall(r'(?m)^  id:\s*([1-9][0-9]*)\s*$', block)))
            ids.update(map(int, re.findall(r'https://hyperskill.org/api/projects/([1-9][0-9]*)/', block)))
    if explicit:
        if not re.fullmatch(r'https://hyperskill\.org/projects/[1-9][0-9]*/?', explicit):
            fail('Supply an exact HTTPS Hyperskill Project URL.')
        pid = int(explicit.rstrip('/').split('/')[-1])
        if ids and ids != {pid}:
            fail('Explicit Project ID conflicts with course-remote-info.yaml; review metadata.')
        return explicit.rstrip('/')
    if len(ids) != 1:
        fail('Project ID missing or ambiguous in course-remote-info.yaml; supply --project-url.')
    return 'https://hyperskill.org/projects/' + str(next(iter(ids)))


def detect(source, requested=None):
    meta = (source / 'course-info.yaml').read_text(encoding='utf-8')
    matches = re.findall(r'(?m)^programming_language:\s*["\']?(Java|Python)["\']?\s*$', meta)
    found = {value.lower() for value in matches}
    if requested and requested != 'auto':
        if found and found != {requested}:
            fail('Language conflicts with Academy metadata.')
        language = requested
    elif len(found) == 1:
        language = found.pop()
    else:
        fail('Language missing or ambiguous; supply --language java or python.')
    if language not in ('java', 'python'):
        fail('Unsupported language; reviewed adapter required.')
    if language == 'python' and sys.version_info < (3, 12):
        fail('The Python source-only adapter requires Python 3.12 or newer.')
    return language


def unsafe_source_path(path):
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
                *(f'LPT{i}' for i in range(1, 10))}
    for part in Path(path).parts:
        if (not part or part in {'.', '..'} or part.endswith((' ', '.')) or
                any(ord(char) < 32 or ord(char) == 127 or char in '\\<>:"|?*' for char in part) or
                part.split('.', 1)[0].upper() in reserved):
            return True
        try:
            part.encode('utf-8')
        except UnicodeEncodeError:
            return True
    return False


PRIVATE_NAME = re.compile(
    r'^(?:\.env(?:\..*)?|id_(?:rsa|ed25519)|.*\.(?:pem|key))$|'
    r'(?:^|[._-])(?:secrets?|credentials?|private|passwords?|tokens?)(?:[._-]|$)', re.IGNORECASE)
PLATFORM_TEST = re.compile(r'(?i)hyperskill\.hstest|org\.hyperskill|\bStageTest\b|\bCheckResult\.')
RESOURCE_SUFFIXES = {'.txt', '.json', '.csv'}


def _resource_literals(language, text):
    if language == 'python':
        # Only unambiguous default-read or explicit read-mode calls. Do not
        # mistake files opened for writing for required project resources.
        return {value for _, value, _ in re.findall(
            r'\bopen\s*\(\s*(["\'])([^"\'\n]+)\1\s*(?:,\s*(["\'])(?:r|rt|rb)\3\s*)?\)', text)}
    patterns = (
        r'\bgetResource(?:AsStream)?\s*\(\s*"([^"\n]+)"',
        r'\bnew\s+(?:java\.io\.)?(?:FileReader|FileInputStream)\s*\(\s*"([^"\n]+)"',
        r'\bFiles\.(?:readString|readAllLines|newInputStream)\s*\(\s*(?:Path\.of|Paths\.get)\s*\(\s*"([^"\n]+)"',
    )
    return {match for pattern in patterns for match in re.findall(pattern, text)}


def source_only_files(source, language, inventory, excluded, unsafe_source_path, secret_pattern, title):
    """Return final task sources plus safely identifiable local text resources.

    This only reads bytes. It never parses, compiles, imports, or runs student or
    Academy build code. File names and paths under task/src remain unchanged.
    """
    entries = inventory(source)
    for relative in entries:
        if unsafe_source_path(relative):
            fail('Unsafe path in Academy workspace: ' + repr(str(relative)))
        path = source / relative
        if path.is_symlink():
            fail('Symlink in Academy workspace: ' + str(relative))
        if not path.is_dir() and not path.is_file():
            fail('Special file in Academy workspace: ' + str(relative))

    tasks = [p for p in entries if p.name == 'task' and len(p.parts) == 2
             and (source / p).is_dir() and not (source / p).is_symlink() and not excluded(p)]
    if language == 'java':
        candidates = [p / 'src' for p in tasks if (source / p / 'src').is_dir()
                      and not (source / p / 'src').is_symlink()]
        exact = [p for p in candidates if p.parts[0] == title]
        if len(exact) == 1:
            candidates = exact
        if len(candidates) != 1:
            fail('Expected one final <lesson>/task/src Java source folder; found: ' + repr([str(p) for p in candidates]))
        code_root = candidates[0]
        task_root = code_root.parent
    else:
        if len(tasks) != 1:
            fail('Expected exactly one final <lesson>/task Python folder; found: ' + repr([str(p) for p in tasks]))
        task_root = tasks[0]
        code_root = task_root / 'src' if (source / task_root / 'src').is_dir() else task_root
        if (source / code_root).is_symlink():
            fail('Symlink final Python source folder refused')

    print('Finaler Quellordner: ' + code_root.as_posix())
    sources, texts, resources = {}, {}, {}
    ignored = {}
    for relative in entries:
        if not relative.is_relative_to(code_root):
            continue
        path = source / relative
        reason = excluded(relative)
        if reason:
            ignored[reason] = ignored.get(reason, 0) + 1
            continue
        if path.is_dir():
            continue
        if PRIVATE_NAME.search(path.name):
            fail('Private-looking file in final source folder refused: ' + str(relative))
        suffix = path.suffix.lower()
        raw = path.read_bytes()
        if suffix in ('.java', '.py'):
            expected = '.java' if language == 'java' else '.py'
            if suffix != expected:
                ignored['other-language source'] = ignored.get('other-language source', 0) + 1
                continue
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                fail('Source file is not UTF-8 text: ' + str(relative))
            if secret_pattern.search(text):
                fail('Possible secret in source file (contents withheld): ' + str(relative))
            if language == 'java' and PLATFORM_TEST.search(text):
                ignored['Academy platform test'] = ignored.get('Academy platform test', 0) + 1
                continue
            archived = 'src/' + relative.relative_to(code_root).as_posix()
            sources[archived] = raw
            texts[relative] = text
            print(f'ARCHIVE source {relative.as_posix()} -> {archived}')
        elif suffix in RESOURCE_SUFFIXES:
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                ignored['non-text resource'] = ignored.get('non-text resource', 0) + 1
                continue
            resources[relative.relative_to(code_root).as_posix()] = (raw, text)
        elif suffix in ('.class', '.pyc', '.pyo', '.tmp', '.swp', '.bak', '.log') or path.name.endswith('~'):
            ignored['generated file'] = ignored.get('generated file', 0) + 1
        else:
            ignored['non-source file'] = ignored.get('non-source file', 0) + 1

    if not sources:
        fail('No final Java/Python solution source found')

    requested = set()
    for text in texts.values():
        requested.update(_resource_literals(language, text))
    for literal in sorted(requested):
        member = PurePosixPath(literal.lstrip('/') if language == 'java' else literal)
        if member.is_absolute() or any(part in ('', '.', '..') for part in member.parts) or '\\' in literal:
            continue
        relative = member.as_posix()
        if relative not in resources:
            continue
        raw, text = resources[relative]
        if len(raw) > 1024 * 1024:
            fail('Referenced text resource exceeds the 1 MiB archive limit: ' + relative)
        if PRIVATE_NAME.search(Path(relative).name) or secret_pattern.search(text):
            fail('Possible private data or secret in referenced resource (contents withheld): ' + relative)
        archived = 'src/' + relative
        sources[archived] = raw
        print(f'ARCHIVE resource {relative} -> {archived}')
    for reason, count in sorted(ignored.items()):
        print(f'IGNORE {reason}: {count} item(s) in final task source folder')
    return code_root, sources
