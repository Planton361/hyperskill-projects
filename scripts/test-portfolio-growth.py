#!/usr/bin/env python3
"""Prove multiple future Java/Python archives compose in one disposable portfolio.

Never changes canonical Git trees, Academy workspaces, personal progress, or Pages.
The final isolated Pages validation retains all browser/geometry/LeetCode gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
from acceptance_context import isolated_myatlas_environment

ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / 'scripts/import-hyperskill-project'
VALIDATOR = ROOT / 'scripts/validate-project-exports.py'


def execute(command, cwd, *, successful=True, env=None):
    print('+', ' '.join(map(str, command)), flush=True)
    result = subprocess.run(list(map(str, command)), cwd=cwd, env=env,
                            capture_output=True, text=True)
    if successful and result.returncode:
        raise ValueError(f'Command failed (exit {result.returncode}): {command[0]}: '
                         f'{result.stdout[-800:]} {result.stderr[-800:]}')
    if not successful and result.returncode == 0:
        raise ValueError('A deliberately rejected import unexpectedly succeeded')
    return result


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def projection(atlas, evidence, env):
    raw = subprocess.check_output([sys.executable, '-B', str(atlas / 'scripts/sync-hyperskill-projects.py'),
                                   '--evidence-root', str(evidence)], cwd=atlas, env=env)
    return json.loads(raw)['projection']


def file_inventory(root):
    """Exact read-only bytes of the disposable Academy fixture, including earlier stages."""
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


def fixture(base, pid, language):
    title = f'Future Portfolio {language.title()} {pid}'
    academy = base / f'academy-{pid}'
    task = academy / title / 'task'
    task.mkdir(parents=True)
    (academy / 'course-info.yaml').write_text(
        f'title: {title}\nprogramming_language: {language.title()}\n')
    (academy / 'course-remote-info.yaml').write_text(
        f'hyperskill_project:\n  id: {pid}\n')
    (academy / 'build.gradle').write_text(
        "throw new RuntimeException('Academy build must not execute')\n")
    (academy / 'settings.gradle').write_text(
        "includeBuild 'never-evaluate-academy'\n")
    old = academy / 'Stage 1/task/src' / ('Old.java' if language == 'java' else 'Old.py')
    old.parent.mkdir(parents=True)
    old.write_text('historical task source; must not publish\n')
    if language == 'java':
        source = task / 'src/pkg/Main.java'
        source.parent.mkdir(parents=True)
        source.write_text('// Topic ID 999999 must never count as learned evidence.\n'
                          'import example.unavailable.Library;\n'
                          'class Main { invalid Java intentionally; }\n')
        expected_files = {f'solution/{title}/task/src/pkg/Main.java': source.read_bytes()}
    else:
        source = task / 'main.py'
        source.write_text('# Topic ID 999999 must never count as learned evidence.\n'
                          'import definitely_unavailable_dependency\n'
                          'open("data.json")\n'
                          'raise RuntimeError("must not execute")\n')
        data = task / 'data.json'
        data.write_text('{"safe": true}\n')
        expected_files = {f'solution/{title}/task/main.py': source.read_bytes(), f'solution/{title}/task/data.json': data.read_bytes()}
    (academy / '.idea').mkdir()
    (academy / '.idea/workspace.xml').write_text('private IDE cache must be omitted\n')
    return academy, title, expected_files


def future_projects(scopes, baseline):
    completed = set(baseline['completed_project_ids'])
    learned = set(baseline['effective_learned_topic_ids'])
    available = [p for p in scopes['projects'] if p['scope_id'] not in completed]
    known = []
    for p in sorted(available, key=lambda p: (len(p['explicit_topic_ids'] or []), p['scope_id'])):
        if p['state'] == 'KNOWN' and set(p['explicit_topic_ids'] or []) - learned:
            known.append(p)
            learned.update(p['explicit_topic_ids'])
            if len(known) == 2:
                break
    unknown = next((p for p in sorted(available, key=lambda p: p['scope_id'])
                    if p['state'] == 'UNKNOWN'), None)
    if len(known) != 2 or unknown is None:
        raise ValueError('Future-project CI requires two unused KNOWN identities and one UNKNOWN '
                         'identity in the trusted Atlas catalog')
    return [('java', known[0]), ('python', known[1]), ('python', unknown)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--myatlas-root', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'test-results/integration')
    args = parser.parse_args()
    atlas = args.myatlas_root.resolve(strict=True)
    if git(atlas, 'remote', 'get-url', 'origin').removesuffix('.git') != \
            'https://github.com/Planton361/myatlas':
        raise ValueError('Unexpected MyAtlas checkout')
    if git(atlas, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('MyAtlas checkout must be clean')

    report = {'scenario': 'growth', 'status': 'RUNNING', 'deployment': 'disabled',
              'hyperskill_commit': git(ROOT, 'rev-parse', 'HEAD'),
              'myatlas_commit': git(atlas, 'rev-parse', 'HEAD'), 'added': []}
    output = args.output.resolve() / 'growth'
    output.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='hyperskill-portfolio-growth-') as folder:
            folder = Path(folder).resolve()
            evidence = folder / 'evidence'
            execute(['git', 'clone', '--no-hardlinks', str(ROOT), str(evidence)], ROOT)
            execute(['git', '-C', str(evidence), 'remote', 'set-url', 'origin',
                     'https://github.com/Planton361/hyperskill-projects.git'], ROOT)
            execute(['git', '-C', str(evidence), 'config', 'user.name', 'Disposable portfolio CI'], ROOT)
            execute(['git', '-C', str(evidence), 'config', 'user.email', 'fixture@example.invalid'], ROOT)
            original = git(evidence, 'rev-parse', 'HEAD')
            execute([sys.executable, '-B', str(VALIDATOR), '--repository', str(evidence)], ROOT)

            env = isolated_myatlas_environment()
            baseline = projection(atlas, evidence, env)
            scopes = json.loads((atlas / 'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_text())
            completed = set(baseline['completed_project_ids'])
            topics = set(baseline['effective_learned_topic_ids'])
            verified = baseline['verified_topic_ids']
            importer = runpy.run_path(str(IMPORTER))
            for step, (language, project) in enumerate(future_projects(scopes, baseline), start=1):
                pid = project['scope_id']
                academy, title, files = fixture(folder, pid, language)
                before = file_inventory(academy)
                selection = folder / f'selection-{pid}.json'
                selection.write_text(json.dumps(dict(schema=1, files={name.removeprefix('solution/'): 'resource' if name.endswith('/data.json') else 'solution' for name in files})))
                command = [sys.executable, '-B', str(IMPORTER), str(academy), '--language', language, '--files-from', str(selection),
                           '--repository', str(evidence), '--project-url',
                           f'https://hyperskill.org/projects/{pid}',
                           '--confirmed-at', '2026-10-08T12:00:00Z']
                execute(command + ['--dry-run'], ROOT)
                if file_inventory(academy) != before:
                    raise ValueError('Dry-run modified disposable Academy source')
                execute(command, ROOT)
                if file_inventory(academy) != before:
                    raise ValueError('Importer modified disposable Academy source')

                exported = evidence / 'projects' / str(pid)
                manifest = json.loads((exported / '.hyperskill-import.json').read_text())
                if manifest['schema'] != 4 or manifest['project_id'] != pid or manifest['languages'] != [language]:
                    raise ValueError('Source-only identity mismatch')
                if set(manifest['files']) != set(files) | {'README.md'}:
                    raise ValueError('Missing or unexpected future archive files')
                for name, raw in files.items():
                    if (exported / name).read_bytes() != raw or \
                            manifest['files'][name]['sha256'] != hashlib.sha256(raw).hexdigest():
                        raise ValueError('Published file bytes differ from owner source')
                members = {p.relative_to(exported).as_posix()
                           for p in exported.rglob('*') if p.is_file()}
                if members != set(files) | {'README.md', '.hyperskill-import.json'}:
                    raise ValueError('Academy/IDE/build material leaked into archive')

                # Each completed project is committed to the DISPOSABLE evidence repository.
                execute(['git', '-C', str(evidence), 'add', '--', f'projects/{pid}'], ROOT)
                execute(['git', '-C', str(evidence), 'commit', '-m',
                         f'TEST ONLY: future source-only Project {pid}'], ROOT)
                check = execute([sys.executable, '-B', str(VALIDATOR),
                                 '--repository', str(evidence)], ROOT)
                archive_ids = {r['project_id'] for r in json.loads(check.stdout)}
                completed.add(pid)
                if archive_ids != completed:
                    raise ValueError('Validator lost or added a committed Project ID')
                if project['state'] == 'KNOWN':
                    topics.update(project['explicit_topic_ids'])
                current = projection(atlas, evidence, env)
                if current['completion_register']['completed_project_ids'] != sorted(completed):
                    raise ValueError('Universal register failed incremental growth')
                if current['verified_topic_ids'] != baseline['verified_topic_ids']:
                    raise ValueError('Independent verifications changed')
                if current['completed_project_ids'] != sorted(completed) or \
                        current['completed_project_count'] != len(completed):
                    raise ValueError('MyAtlas failed incremental portfolio growth')
                if current['effective_learned_topic_ids'] != sorted(topics) or \
                        current['global']['learned'] != len(topics):
                    raise ValueError('Topics were inferred outside the trusted Atlas catalog')
                if current['verified_topic_ids'] != verified:
                    raise ValueError('Archive incorrectly changed independent verification')
                row = next(r for r in current['projects'] if r['project_id'] == pid)
                if row['requirements_state'] != project['state'] or \
                        row['topic_ids'] != sorted(set(project['explicit_topic_ids'] or [])):
                    raise ValueError('Project requirements changed from trusted catalog')
                if project['state'] == 'UNKNOWN' and row['topic_ids']:
                    raise ValueError('UNKNOWN requirements invented learned Topics')
                # A second publication of the same ID must fail, not create a new export.
                execute(command, ROOT, successful=False)
                if file_inventory(academy) != before:
                    raise ValueError('Duplicate attempt modified Academy source')
                report['added'].append(dict(project_id=pid, language=language,
                                            requirements_state=project['state'],
                                            archive_files=sorted(files)))
                print(f'GROWTH STEP {step} PASS: {pid} {language}; '
                      f'{len(completed)} completed; {len(topics)} learned', flush=True)

            all_changes = git(evidence, 'diff', '--name-only', original, 'HEAD').splitlines()
            allowed = {f'projects/{row["project_id"]}/'
                       for row in report['added']}
            if not all_changes or any(not any(path.startswith(prefix) for prefix in allowed)
                                      for path in all_changes):
                raise ValueError('Future-project integration modified unrelated files')
            execute([sys.executable, '-B', str(atlas / 'scripts/validate-pages-candidate.py'),
                     '--evidence-root', str(evidence)], atlas, env=env)
            built = json.loads((atlas / 'build/pages/knowledge-map/progress.json').read_text())
            if built != current:
                raise ValueError('Pages artifact diverged from exact committed portfolio evidence')
            shutil.copytree(atlas / 'test-results', output / 'myatlas', dirs_exist_ok=True)
            report.update(status='PASS', completed_project_ids=sorted(completed),
                          learned=len(topics), verified=len(verified),
                          evidence_commit=git(evidence, 'rev-parse', 'HEAD'),
                          geometry_validation='full Pages acceptance')
    except Exception as error:
        report.update(status='FAIL', error=str(error))
        raise
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
