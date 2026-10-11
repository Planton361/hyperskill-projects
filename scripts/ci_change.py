"""Fail-closed Git change policy. This file is executed from the trusted base tree in CI."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

SHA = re.compile(r'[0-9a-f]{40}')
ID = re.compile(r'projects/([1-9][0-9]*)/(.+)')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args],
                                   env=dict(os.environ, GIT_NO_REPLACE_OBJECTS='1'))


def commit(root, value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError('Full commit revision required')
    if git(root, 'cat-file', '-t', value).strip() != b'commit':
        raise ValueError('Revision is not a commit')
    return value


def classify(root, base, head, event):
    commit(root, head)
    result = dict(change_class='B', revision=head, base=base, project_ids=[],
                  full_required=True, reason='Unknown/mixed changes require full acceptance')
    if event in ('schedule', 'workflow_dispatch'):
        return dict(result, change_class='C', reason='Scheduled/manual system health acceptance')
    if event not in ('push', 'pull_request'):
        return result
    try:
        commit(root, base)
        comparison = git(root, 'merge-base', base, head).decode().strip() if event == 'pull_request' else base
        if event == 'push' and subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', base, head]).returncode:
            return dict(result, reason='Non-fast-forward push requires full acceptance')
        result['comparison_base'] = comparison
        raw = git(root, 'diff', '--name-status', '-z', '--no-renames', comparison, head).split(b'\0')
        pairs = [(raw[i].decode('ascii'), raw[i+1].decode('utf-8')) for i in range(0, len(raw)-1, 2)]
        ids = set()
        if not pairs:
            return dict(result, reason='Empty change set requires full acceptance')
        for status, name in pairs:
            match = ID.fullmatch(name)
            if status != 'A' or not match or int(match[1]) > 9007199254740991:
                return result
            pid = int(match[1]); ids.add(pid)
            if git(root, 'ls-tree', comparison, '--', 'projects/'+str(pid)).strip():
                return dict(result, reason='Existing archive evidence cannot use data-only acceptance')
            metadata = git(root, 'ls-tree', head, '--', name).split(b'\t')[0].split()
            if len(metadata) != 3 or metadata[:2] not in ([b'100644', b'blob'], [b'100755', b'blob']):
                return dict(result, reason='Non-regular Git object requires full acceptance')
        # Admission still requires the complete archive/index/reader validators.
        for pid in ids:
            manifest = json.loads(git(root, 'show', head+':projects/'+str(pid)+'/.hyperskill-import.json'))
            if type(manifest.get('schema')) is not int or manifest['schema'] != 4:
                return result
        return dict(result, change_class='A', full_required=False, project_ids=sorted(ids),
                    reason='Only regular newly added Schema-4 archive files; complete data validation mandatory')
    except (ValueError, KeyError, UnicodeError, subprocess.SubprocessError):
        return dict(result, reason='Unavailable/invalid comparison; full acceptance required')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path.cwd())
    parser.add_argument('--base', required=True); parser.add_argument('--head', required=True)
    parser.add_argument('--event', required=True); parser.add_argument('--github-output', type=Path)
    args = parser.parse_args()
    result = classify(args.repository, args.base, args.head, args.event)
    raw = json.dumps(result, sort_keys=True, indent=2)+'\n'
    print(raw); Path('change-report.json').write_text(raw)
    if args.github_output:
        with args.github_output.open('a') as output:
            output.write('class='+result['change_class']+'\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as output:
            output.write('### Change policy\n\n```json\n'+raw+'```\n')
