#!/usr/bin/env python3
"""Archive a candidate in a disposable repo and run the real MyAtlas Pages acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import stat
import subprocess
import sys
import tempfile
from source_adapters import detect, project_url, workspace

ROOT = Path(__file__).resolve().parents[1]


def source_snapshot(root, inventory):
    result = {}
    for relative in inventory(root):
        path = root / relative
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            value = ('symlink', os.readlink(path), mode)
        elif path.is_file():
            value = ('file', hashlib.sha256(path.read_bytes()).hexdigest(), mode)
        elif path.is_dir():
            value = ('directory', mode)
        else:
            value = ('special', mode)
        result[str(relative)] = value
    return result


def call(command, cwd, env=None):
    print('+ ' + ' '.join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, env=env, check=True)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()


def select_unknown_project(scopes, completed_ids, requested_id=None):
    """Select an uncompleted UNKNOWN catalog project for disposable acceptance."""
    candidates = {project['scope_id']: project for project in scopes['projects']
                  if project['state'] == 'UNKNOWN' and project['scope_id'] not in completed_ids}
    if requested_id is not None:
        if requested_id not in candidates:
            raise ValueError('Requested UNKNOWN Project ID is unavailable or already completed')
        return candidates[requested_id]
    if 229 in candidates:
        return candidates[229]  # Preserve the historical fixture until its first publication.
    if not candidates:
        raise ValueError('No uncompleted UNKNOWN project exists for the disposable fixture')
    return candidates[min(candidates)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--myatlas-root', required=True, type=Path)
    parser.add_argument('--scenario', choices=('committed', 'java', 'python', 'unknown'), default='committed')
    parser.add_argument('--project-id', type=int, help='use this exact Atlas project scope')
    parser.add_argument('--academy-source', type=Path, help='read a real Academy workspace; never modified')
    parser.add_argument('--completed-at', help='actual UTC time; required with a real Academy workspace')
    parser.add_argument('--output', type=Path, default=ROOT/'test-results/integration')
    args = parser.parse_args()
    atlas = args.myatlas_root.resolve(strict=True)
    if args.scenario == 'committed' and (args.project_id is not None or args.academy_source is not None):
        raise ValueError('--project-id and --academy-source require a java, python, or unknown scenario')
    if args.scenario == 'unknown' and args.academy_source is not None:
        raise ValueError('The unknown scenario only supports disposable catalog fixtures')
    if args.project_id is not None and args.project_id <= 0:
        raise ValueError('--project-id must be positive')
    if args.academy_source is not None and not args.completed_at:
        raise ValueError('A real Academy workspace requires its actual --completed-at UTC timestamp')
    completed_at = args.completed_at or '2026-10-08T12:00:00Z'
    if git(atlas, 'remote', 'get-url', 'origin').removesuffix('.git') != 'https://github.com/Planton361/myatlas':
        raise ValueError('Unexpected MyAtlas origin')
    if git(atlas, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('MyAtlas acceptance requires clean committed sources')
    env = dict(os.environ)
    env.pop('GITHUB_SHA', None)
    report = dict(scenario=args.scenario, status='RUNNING', myatlas_commit=git(atlas, 'rev-parse', 'HEAD'),
                  hyperskill_commit=git(ROOT, 'rev-parse', 'HEAD'), deployment='disabled')
    output = args.output.resolve() / args.scenario
    output.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='hyperskill-atlas-e2e-') as folder:
            folder = Path(folder)
            evidence = folder/'evidence'
            call(['git', 'clone', '--no-hardlinks', ROOT, evidence], ROOT)
            call(['git', 'remote', 'set-url', 'origin', 'https://github.com/Planton361/hyperskill-projects.git'], evidence)
            original = git(evidence, 'rev-parse', 'HEAD')
            call([sys.executable, '-B', ROOT/'scripts/validate-project-exports.py', '--repository', evidence], ROOT)
            baseline = json.loads(subprocess.check_output(
                [sys.executable, '-B', atlas/'scripts/sync-hyperskill-projects.py', '--evidence-root', evidence],
                cwd=atlas, env=env))['projection']
            project = None
            if args.scenario != 'committed':
                language = 'python' if args.scenario == 'python' else 'java'
                scopes = json.loads((atlas/'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_text())
                known = set(baseline['effective_learned_topic_ids'])
                if args.academy_source is not None:
                    academy = workspace(args.academy_source)
                    detected = detect(academy)
                    if detected != language:
                        raise ValueError('Academy source language does not match scenario')
                    url = project_url(academy)
                    pid = int(url.rsplit('/', 1)[-1])
                    if args.project_id is not None and args.project_id != pid:
                        raise ValueError('Academy Project ID does not match --project-id')
                else:
                    academy = folder/'academy'
                    task = academy/'Lesson/task'
                    task.mkdir(parents=True)
                    if args.scenario == 'unknown':
                        project = select_unknown_project(scopes, set(baseline['completed_project_ids']),
                                                         args.project_id)
                        pid = project['scope_id']
                    else:
                        pid = args.project_id
                    if pid is None:
                        project = next(p for p in sorted(scopes['projects'], key=lambda p: len(p['explicit_topic_ids'] or []))
                                       if p['state'] == 'KNOWN' and p['scope_id'] not in baseline['completed_project_ids']
                                       and set(p['explicit_topic_ids']) - known)
                        pid = project['scope_id']
                    else:
                        project = next((p for p in scopes['projects'] if p['scope_id'] == pid), None)
                        if project is None:
                            raise ValueError('Project ID absent from MyAtlas scope catalog')
                    fixture_title = project['title']
                    (academy/'course-info.yaml').write_text(f'title: {fixture_title}\nprogramming_language: {language.title()}\n')
                    (academy/'course-remote-info.yaml').write_text(f'hyperskill_project:\n  id: {pid}\n')
                    url = f'https://hyperskill.org/projects/{pid}'
                    if language == 'java':
                        (task/'src').mkdir()
                        (task/'src/Main.java').write_text(
                            '// Literal project-topic-looking text must never become Atlas evidence.\n'
                            'import com.example.UnverifiedDependency;\nclass Main { invalid syntax }\n')
                        (academy/'build.gradle').write_text(
                            "tasks.register('mustNotRun') { throw new RuntimeException('foreign build executed') }\n")
                        (academy/'settings.gradle').write_text("throw new RuntimeException('must not execute')\n")
                    else:
                        (task/'main.py').write_text(
                            'import unverified_dependency\nopen("data.json")\nraise SystemExit("must not run")\n')
                        (task/'data.json').write_text('{"fixture": true}\n')
                if pid in baseline['completed_project_ids']:
                    raise ValueError('Project is already completed in the committed baseline')
                project = next((p for p in scopes['projects'] if p['scope_id'] == pid), None)
                if project is None:
                    raise ValueError('Project ID absent from MyAtlas scope catalog')
                report.update(project_id=pid, project_title=project['title'], requirements_state=project['state'])
                importer = runpy.run_path(str(ROOT/'scripts/import-hyperskill-project'))
                before = source_snapshot(academy, importer['inventory'])
                call([sys.executable, '-B', ROOT/'scripts/import-hyperskill-project', academy, language,
                      '--repository', evidence, '--project-url', url, '--completed-at', completed_at], ROOT)
                if source_snapshot(academy, importer['inventory']) != before:
                    raise ValueError('Academy source was modified')
                call(['git', 'config', 'user.name', 'Disposable integration fixture'], evidence)
                call(['git', 'config', 'user.email', 'fixture@example.invalid'], evidence)
                call(['git', 'switch', '-c', 'validation-only/project-pr'], evidence)
                call(['git', 'add', '--', language], evidence)
                call(['git', 'commit', '-m', 'TEST ONLY: simulated source-only project PR evidence'], evidence)
                changed = git(evidence, 'diff', '--name-only', original, 'HEAD').splitlines()
                title = importer['title_from_source'](academy, None)
                directory = importer['safe_directory_name'](title)
                prefix = language + '/' + directory + '/'
                if not changed or any(not path.startswith(prefix) for path in changed):
                    raise ValueError('Unexpected candidate PR changes')
                call([sys.executable, '-B', ROOT/'scripts/validate-project-exports.py', '--repository', evidence], ROOT)

            current = json.loads(subprocess.check_output(
                [sys.executable, '-B', atlas/'scripts/sync-hyperskill-projects.py', '--evidence-root', evidence],
                cwd=atlas, env=env))['projection']
            expected_ids = set(baseline['completed_project_ids']) | (
                {report['project_id']} if args.scenario != 'committed' else set())
            if current['completed_project_ids'] != sorted(expected_ids):
                raise ValueError('Exact completion IDs mismatch')
            if current['verified_topic_ids'] != baseline['verified_topic_ids']:
                raise ValueError('Project archive changed independent verification')
            project_topics = (set(project['explicit_topic_ids'] or [])
                              if args.scenario != 'committed' and project['state'] == 'KNOWN' else set())
            expected_topics = set(baseline['effective_learned_topic_ids']) | project_topics
            if (current['effective_learned_topic_ids'] != sorted(expected_topics) or
                    current['global']['learned'] != len(expected_topics)):
                raise ValueError('Atlas-catalog topic projection mismatch')
            call([sys.executable, '-B', atlas/'scripts/validate-pages-candidate.py', '--evidence-root', evidence], atlas, env)
            built = json.loads((atlas/'build/pages/knowledge-map/progress.json').read_text())
            if built != current:
                raise ValueError('Built Pages projection differs from committed archive evidence')
            shutil.copytree(atlas/'test-results', output/'myatlas', dirs_exist_ok=True)
            report.update(status='PASS', candidate_commit=git(evidence, 'rev-parse', 'HEAD'),
                          completed_project_ids=current['completed_project_ids'],
                          newly_learned_topic_ids=sorted(expected_topics-set(baseline['effective_learned_topic_ids'])),
                          already_known_topic_ids=sorted(set(current['project_learned_topic_ids']) &
                                                         set(baseline['effective_learned_topic_ids'])),
                          verified_topic_count=current['global']['verified'],
                          learned_topic_count=current['global']['learned'])
    except Exception as error:
        report.update(status='FAIL', error=str(error))
        raise
    finally:
        (output/'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
