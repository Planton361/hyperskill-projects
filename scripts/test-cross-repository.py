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
from acceptance_context import isolated_myatlas_environment

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
    parser.add_argument('--scenario', choices=('committed','java','python','unknown','unmapped'), default='committed')
    parser.add_argument('--output', type=Path, default=ROOT/'test-results/integration')
    args = parser.parse_args()
    atlas = args.myatlas_root.resolve(strict=True)
    if git(atlas,'remote','get-url','origin').removesuffix('.git') != 'https://github.com/Planton361/myatlas':
        raise ValueError('Unexpected MyAtlas origin')
    if git(atlas,'status','--porcelain','--untracked-files=no'):
        raise ValueError('MyAtlas acceptance requires clean committed sources')
    if not (atlas/'docs/contracts/hyperskill-code-archive-v4.md').is_file():
        raise ValueError('Reviewed Schema-4 MyAtlas reader required; no incompatible bootstrap fallback')
    env=isolated_myatlas_environment()
    report=dict(scenario=args.scenario,status='RUNNING',deployment='disabled',
                myatlas_commit=git(atlas,'rev-parse','HEAD'),hyperskill_commit=git(ROOT,'rev-parse','HEAD'))
    output=args.output.resolve()/args.scenario; output.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='hyperskill-universal-acceptance-') as folder:
            folder=Path(folder).resolve(); evidence=folder/'evidence'
            call(['git','clone','--no-hardlinks',ROOT,evidence],ROOT)
            call(['git','remote','set-url','origin','https://github.com/Planton361/hyperskill-projects.git'],evidence)
            original=git(evidence,'rev-parse','HEAD')
            call([sys.executable,'-B',ROOT/'scripts/validate-project-exports.py','--repository',evidence],ROOT)
            def projection():
                return json.loads(subprocess.check_output([sys.executable,'-B',atlas/'scripts/sync-hyperskill-projects.py','--evidence-root',evidence],cwd=atlas,env=env))['projection']
            baseline=projection(); project=None; pid=None
            if args.scenario!='committed':
                scopes=json.loads((atlas/'src/myatlas/knowledge-atlas-scope-pyramid/scope-index.json').read_text())
                if args.scenario=='unmapped':
                    pid=900000001
                    while pid in {p['scope_id'] for p in scopes['projects']}: pid+=1
                    project=dict(scope_id=pid,state='UNMAPPED',explicit_topic_ids=[])
                elif args.scenario=='unknown':
                    project=select_unknown_project(scopes,set(baseline['completed_project_ids']))
                else:
                    known=set(baseline['effective_learned_topic_ids'])
                    project=next(p for p in sorted(scopes['projects'],key=lambda p:len(p['explicit_topic_ids'] or []))
                                 if p['state']=='KNOWN' and p['scope_id'] not in baseline['completed_project_ids'] and set(p['explicit_topic_ids'])-known)
                pid=project['scope_id']; report['project_id']=pid
                academy=folder/'owner-source'; task=academy/'Lesson/task/src'; task.mkdir(parents=True)
                (academy/'course-info.yaml').write_text('title: Synthetic Owner Project\n')
                (academy/'course-remote-info.yaml').write_text(f'hyperskill_project:\n  id: {pid}\n')
                (academy/'build.gradle').write_text("throw new RuntimeException('must not execute')\n")
                if args.scenario=='unmapped':
                    files={'main.kt':b'import missing.Library; invalid Kotlin\n','helper.js':b'throw Error("must not run"); // topic_id=15\n',
                           'program':b'topic_ids=[15,999999]; course_completed=true; is_verified=true\n','code.future':b'unknown UTF-8 owner source\n',
                           'data.bin':b'\x00\xff\x10'}
                elif args.scenario=='python':
                    files={'main.py':b'import missing_dependency\nraise Exception("must not execute")\ndef invalid(:\n'}
                else:
                    files={'Main.java':b'import missing.Library; class Broken { invalid Java; }\n'}
                for name,raw in files.items(): (task/name).write_bytes(raw)
                selection=folder/'selection.json'
                selection.write_text(json.dumps(dict(schema=1,files={f'Lesson/task/src/{name}': 'resource' if name=='data.bin' else 'solution' for name in files})))
                importer=runpy.run_path(str(ROOT/'scripts/import-hyperskill-project'))
                before=source_snapshot(academy,importer['inventory'])
                command=[sys.executable,'-B',ROOT/'scripts/import-hyperskill-project',academy,'--repository',evidence,
                         '--project-url',f'https://hyperskill.org/projects/{pid}','--confirmed-at','2026-10-08T12:00:00Z']
                if args.scenario=='unmapped': command+=['--files-from',selection]
                call(command+['--dry-run'],ROOT); call(command,ROOT)
                if source_snapshot(academy,importer['inventory'])!=before: raise ValueError('Owner source modified')
                call(['git','config','user.name','Disposable Schema-4 acceptance'],evidence)
                call(['git','config','user.email','fixture@example.invalid'],evidence)
                call(['git','add','--',f'projects/{pid}'],evidence)
                call(['git','commit','-m','TEST ONLY: synthetic Schema-4 project'],evidence)
                changed=git(evidence,'diff','--name-only',original,'HEAD').splitlines()
                if not changed or any(not path.startswith(f'projects/{pid}/') for path in changed): raise ValueError('Unexpected candidate changes')
                call([sys.executable,'-B',ROOT/'scripts/validate-project-exports.py','--repository',evidence],ROOT)
            current=projection()
            expected=set(baseline['completed_project_ids']) | ({pid} if pid and project['state']!='UNMAPPED' else set())
            if current['completed_project_ids']!=sorted(expected): raise ValueError('Catalog completion IDs mismatch')
            if pid:
                register=current['completion_register']
                if register['completed_project_ids']!=sorted(set(baseline['completed_project_ids'])|{pid}): raise ValueError('Universal register IDs mismatch')
                row=next(r for r in register['projects'] if r['project_id']==pid)
                if row['requirements_state']!=project['state'] or row['topic_ids']!=sorted(set(project['explicit_topic_ids'] or [])): raise ValueError('Catalog/register mapping mismatch')
                if project['state']=='UNMAPPED' and (pid in {p['project_id'] for p in current['projects']} or register['unmapped_project_ids']!=[pid]): raise ValueError('Unmapped ID leaked into catalog runtime')
            expected_topics=set(baseline['effective_learned_topic_ids']) | (set(project['explicit_topic_ids']) if project and project['state']=='KNOWN' else set())
            if current['effective_learned_topic_ids']!=sorted(expected_topics) or current['global']['learned']!=len(expected_topics): raise ValueError('Invented source-derived Topics')
            # Independent Course attestations remain separate from the accepted
            # catalog's derived completed-project counts within Courses.
            if current['verified_topic_ids']!=baseline['verified_topic_ids'] or current['course_completion']!=baseline['course_completion']: raise ValueError('Independent verification/Course records changed')
            if project and project['state']=='UNMAPPED' and current['course_project_completion']!=baseline['course_project_completion']:
                raise ValueError('Unmapped archive changed catalog Course/project relationships')
            call([sys.executable,'-B',atlas/'scripts/validate-pages-candidate.py','--evidence-root',evidence],atlas,env)
            if json.loads((atlas/'build/pages/knowledge-map/progress.json').read_text())!=current: raise ValueError('Pages projection differs from validated archives')
            shutil.copytree(atlas/'test-results',output/'myatlas',dirs_exist_ok=True)
            report.update(status='PASS',candidate_commit=git(evidence,'rev-parse','HEAD'),
                          completed_project_ids=current['completed_project_ids'],completion_register=current.get('completion_register'),
                          learned=current['global']['learned'],verified=current['global']['verified'])
    except Exception as error:
        report.update(status='FAIL',error=str(error)); raise
    finally: (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
