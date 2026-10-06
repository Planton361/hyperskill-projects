import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'scripts'))
from knowledge_atlas.adaptive_preview import artifacts,run
from knowledge_atlas.architecture import PRODUCTION_MIGRATION
out=artifacts(root);assert out==artifacts(root)
assert out['global-reference.json']==(root/'prototypes/global-pyramid/generated/global-geometry.json').read_bytes()
assert PRODUCTION_MIGRATION=='PAUSED_PENDING_ADAPTIVE_VIEW_ACCEPTANCE'
manifest=json.loads(out['preview-manifest.json']);assert manifest['target']=='non-production-preview' and manifest['local_geometry_storage']=='derived-memory-only'
run(root,check=True)
baseline=json.loads((Path(__file__).parent/'task-start.json').read_text())['files']
protected=['docs/knowledge-map/','state/knowledge-atlas/','data/knowledge/']
hashes={p:h for p,h in baseline.items() if any(p.startswith(d) for d in protected)}
changed=[p for p,h in hashes.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h];assert not changed
actual={p.relative_to(root).as_posix() for d in protected for p in (root/d).rglob('*') if p.is_file()}
assert actual==set(hashes),'Protected file inventory changed'
allowed={'prototypes/global-pyramid/README.md','scripts/knowledge_atlas/README.md','scripts/knowledge_atlas/spatial_authorization.py','scripts/update-knowledge-atlas.py'}
existing_changes=[]
for p,h in baseline.items():
    assert (root/p).is_file(),'Original file removed: '+p
    if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h:existing_changes.append(p)
assert set(existing_changes)==allowed,'Unexpected existing file change'
groups={d:{p:h for p,h in hashes.items() if p.startswith(d)} for d in protected}
result={'deterministic_build':True,'protected_files':len(hashes),'protected_inventory_unchanged':True,'changed':changed,'original_files':len(baseline),'original_files_byte_unchanged':len(baseline)-len(existing_changes),'intentional_existing_changes':sorted(existing_changes),'removed_original_files':[],'hashes':groups,'aggregate_sha256':{d:hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest() for d,rows in groups.items()},'global_reference_sha256':manifest['global_reference_sha256']}
(Path(__file__).parent/'integrity-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='hashes'}))
