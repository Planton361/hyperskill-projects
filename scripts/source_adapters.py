"""Reviewed source-only Academy adapters. Never execute Academy build logic."""
import ast
from pathlib import Path
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
        text = remote.read_text()
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
    meta = (source / 'course-info.yaml').read_text()
    matches = re.findall(r'(?m)^programming_language:\s*[\"\']?(Java|Python)[\"\']?\s*$', meta)
    found = {s.lower() for s in matches}
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
    return language



# Explicit portable subset; no environment-dependent stdlib allow-all.
PYTHON_MODULES = {'math', 'random', 're', 'datetime', 'json', 'collections', 'itertools',
                  'string', 'statistics', 'decimal', 'fractions', 'functools', 'typing',
                  'enum', 'dataclasses', 'time'}


def python_sources(source, inventory, excluded, platform, secrets):
    if sys.version_info < (3, 12):
        fail('The Python adapter requires Python 3.12 or newer; restart the helper with python3.12.')
    tasks = [p for p in inventory(source) if p.name == 'task' and len(p.parts) == 2
             and (source / p).is_dir() and not (source / p).is_symlink()]
    if len(tasks) != 1:
        fail('Expected exactly <lesson>/task for simple Python; ambiguous layout.')
    task = tasks[0]
    code_root = task / 'src' if (source / task / 'src').is_dir() else task
    payload, trees, resources = {}, {}, set()
    for rel in inventory(source):
        path = source / rel
        if excluded(rel):
            continue
        if path.is_symlink():
            fail('Symlink in Python source: ' + str(rel))
        if path.is_dir():
            continue
        if not path.is_file():
            fail('Special file in Python workspace')
        if rel.name in ('requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', 'poetry.lock'):
            if rel.name != 'requirements.txt' or any(l.strip() and not l.lstrip().startswith('#') for l in path.read_text().splitlines()):
                fail('Unreviewed Python dependencies/build metadata; no installation performed.')
            continue
        if rel.is_relative_to(code_root):
            name = rel.relative_to(code_root).as_posix()
            raw = path.read_bytes()
            text = raw.decode('utf-8')
            if platform.search(text) or secrets.search(text):
                fail('Platform code or possible secret in Python input')
            if path.suffix == '.py':
                try:
                    trees[name] = ast.parse(text, filename=name)
                except SyntaxError as error:
                    fail('Invalid Python source ' + name + ': ' + error.msg)
                payload['src/' + name] = raw
            else:
                if path.suffix not in ('.txt', '.json', '.csv') or len(raw) > 1024 * 1024:
                    fail('Unsupported Python resource: ' + str(rel))
                resources.add(name)
                payload['src/' + name] = raw
        elif rel.is_relative_to(task.parent) and not rel.is_relative_to(task):
            continue  # earlier stages
        elif rel.as_posix() not in ('README.md', '.gitignore'):
            fail('Unknown Python workspace file: ' + str(rel))
    if not trees:
        fail('No Python source found')
    modules = {Path(n).stem for n in trees if '/' not in n}
    required = set()
    for name, tree in trees.items():
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "open":
                parent = parents.get(node)
                if not isinstance(parent, ast.Call) or parent.func is not node:
                    fail("Aliased Python file access requires adapter review")
            imports = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else ([node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module and not node.level else [])
            if isinstance(node, ast.ImportFrom) and (node.level or not node.module):
                fail('Relative Python imports require adapter review')
            if any(m not in PYTHON_MODULES | modules for m in imports):
                fail('Unreviewed Python import in ' + name)
            if isinstance(node, ast.Attribute) and node.attr.startswith('__'):
                fail('Dynamic Python introspection requires adapter review')
            if isinstance(node, ast.Name) and node.id.startswith('__') and node.id != '__name__':
                fail('Dynamic Python internals require adapter review')
            if isinstance(node, ast.Name) and node.id in {'eval', 'exec', 'compile', '__import__', 'getattr', 'globals', 'locals', 'vars', 'setattr', 'delattr', 'breakpoint', 'input_module'}:
                fail('Dynamic Python execution requires adapter review')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                    fail('Python resource path must be a literal')
                resource = node.args[0].value
                mode = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else 'r' if len(node.args) == 1 else None
                if node.keywords or mode not in ('r', 'rt') or resource not in resources:
                    fail('Only declared local text resources opened read-only are supported')
                required.add(resource)
    if resources != required:
        fail('Unreferenced Python resources require explicit adapter review')
    mains = [n for n,t in trees.items() if n in ('main.py', 'app.py') or any(isinstance(x, ast.Compare) and isinstance(x.left, ast.Name) and x.left.id == '__name__' for x in ast.walk(t))]
    if len(mains) != 1:
        fail('Python entrypoint ambiguous; use a single main.py or __main__ guard')
    # Run from src so explicitly checked relative resource paths resolve.
    return payload, mains[0]


def validate_python_export(target, manifest):
    if manifest.get('dependencies') != [] or manifest.get('entrypoint') not in manifest['files']:
        fail('Unsupported Python export contract')
    for name in manifest['files']:
        if name.endswith('.py'):
            compile((target / name).read_text(), name, 'exec')  # compile only; never execute coursework
