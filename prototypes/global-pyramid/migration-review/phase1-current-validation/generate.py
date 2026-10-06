"""Read-only Phase 1 packaging. No approval, seal or publication calls."""
from pathlib import Path
import json,importlib.util,tempfile,hashlib,time
ROOT=Path('/home/anton/IdeaProjects/hyperskill-projects')
BASE=ROOT/'prototypes/global-pyramid/migration-review';EVIDENCE=BASE/'phase1-current-validation';OUT=BASE/'real-current'
spec=importlib.util.spec_from_file_location('review',BASE/'review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def protect():
    out={}
    for d in ('docs/knowledge-map','state/knowledge-atlas','data/knowledge'):
        for p in sorted((ROOT/d).rglob('*')):
            assert not p.is_symlink()
            if p.is_file():out[p.relative_to(ROOT).as_posix()]=R.sha(p.read_bytes())
    p=ROOT/'prototypes/global-pyramid/generated/global-geometry.json';out[p.relative_to(ROOT).as_posix()]=R.sha(p.read_bytes());return out
preflight=R.read(EVIDENCE/'preflight.json');assert protect()==preflight['protected_before']
for file,count in [('migration-tests.txt',15),('durable-tests.txt',9)]:
    log=(EVIDENCE/file).read_text();assert log.strip().endswith('OK') and f'Ran {count} tests' in log,'Required validation failed/incomplete: '+file
for file in ('legacy-check.json','legacy-dry-run.json'):
    r=R.read(EVIDENCE/file);assert r['status']=='SAFE_TO_APPLY' and not r['applied'] and not r['state_changed'] and r['presentation']['generation']==0
assert not OUT.exists(),'Never overwrite review packages'
old_fingerprints={R.read(p)['manifest_fingerprint'] for p in (BASE/'packages').glob('*/migration-manifest.json')}
start=time.perf_counter()
with tempfile.TemporaryDirectory(prefix='atlas-phase1-fresh-preview-') as temp:
    preview=Path(temp);outputs,diff_ms=R.P.artifacts(ROOT);repeated,_=R.P.artifacts(ROOT);assert outputs==repeated
    for name,raw in outputs.items():(preview/name).write_bytes(raw)
    m=R.make_package(ROOT,preview,OUT)
assert m['manifest_fingerprint'] not in old_fingerprints and m['fixture_only'] is False
# Independent read-only validation; no approval/authorization API is invoked.
files=R.tree(OUT);assert R.fp({k:v for k,v in m.items() if k!='manifest_fingerprint'})==m['manifest_fingerprint']
assert files['manifest-core.json']==R.encoded({k:v for k,v in m.items() if k!='manifest_fingerprint'})
assert R.digest_files({k:v for k,v in files.items() if k not in ('manifest-core.json','migration-manifest.json')})==m['files']
data=R.validate_source(ROOT,m);data['_root']=ROOT;R.validate_material(m,files,data)
assert len(m['contract']['mapping'])==len({r['slot'] for r in m['contract']['mapping']})==135
assert all(r['slot']=='leaf:'+r['key'].split(':')[1] for r in m['contract']['mapping'] if r['key'].startswith('topic:'))
assert protect()==preflight['protected_before']
assert data['checkpoint']['presentation_generation']==0 and data['history']['history_version']==0
assert not (ROOT/'state/knowledge-atlas/spatial-authority.json').exists()
result=dict(status='AWAITING_EXPLICIT_HUMAN_REVIEW',real_migration_applied=False,authority='LEGACY',generation=0,history_version=0,
 package=str(OUT),manifest=str(OUT/'migration-manifest.json'),manifest_fingerprint=m['manifest_fingerprint'],
 canonical_geometry_fingerprint=m['contract']['target']['geometry_fingerprint'],canonical_geometry_sha256=m['contract']['target']['geometry_sha256'],
 source_production_inventory_fingerprint=R.fp(m['contract']['source']['production_inventory']),source_accepted_geometry_fingerprint=m['contract']['source']['accepted_geometry_fingerprint'],
 mapping=dict(mapped=135,categories=46,topics=89,missing=0,duplicates=0,all_topics_use_leaf_slots=True),
 fresh_metrics=R.read(OUT/'migration-metrics.json'),package_files=len(files),package_bytes=sum(map(len,files.values())),build_ms=(time.perf_counter()-start)*1000,diff_ms=diff_ms,
 protected_after=protect(),protected_unchanged=True,approval_seal_created=False)
(EVIDENCE/'package-verification.json').write_bytes(R.encoded(result))
print('Fresh real review package generated and independently validated; unapproved; real migration NOT APPLIED.')
