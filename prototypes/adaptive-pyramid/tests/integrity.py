"""Task-start bytes, including independent untracked files, are never refreshed."""
import hashlib,json,subprocess
from pathlib import Path
base=Path(__file__).resolve().parent
root=base.parents[2]
baseline=json.loads((base/'task-start.json').read_text())
changed=[p for p,h in baseline['files'].items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
new_protected=[]
preexisting_ignored=[]
for directory in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge','prototypes/global-pyramid']:
    for p in (root/directory).rglob('*'):
        relative=str(p.relative_to(root))
        if not p.is_file() or relative in baseline['files']:continue
        # git's task-start inventory excludes ignored historical log files.
        # Do not refresh its hashes: prove they predate the baseline separately.
        ignored=subprocess.run(['git','check-ignore',relative],cwd=root,capture_output=True).returncode==0
        if ignored and p.stat().st_mtime_ns < (base/'task-start.json').stat().st_mtime_ns:
            preexisting_ignored.append(relative)
        else:new_protected.append(relative)
current_status=subprocess.check_output(['git','status','--short'],cwd=root).decode()
initial_status_unchanged='\n'.join(line for line in current_status.splitlines() if 'prototypes/adaptive-pyramid/' not in line)+'\n'==baseline['git_status']
result=dict(original_files=len(baseline['files']),changed=changed,new_protected=new_protected,preexisting_ignored_logs=preexisting_ignored,initial_git_status_unchanged=initial_status_unchanged)
(base/'integrity-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));assert not changed and not new_protected and initial_status_unchanged
