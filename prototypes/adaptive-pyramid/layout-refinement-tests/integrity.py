import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=Path(__file__).parent
baseline=json.loads((p/'baseline.json').read_text())
groups=['docs/knowledge-map','state/knowledge-atlas','data/knowledge','prototypes/global-pyramid/generated']
actual={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for d in groups for f in (root/d).rglob('*') if f.is_file()}
assert actual==baseline,'Protected bytes/inventory changed'
result={'protected_files':len(actual),'unchanged':True,'file_hashes':actual,'aggregate_sha256':{d:hashlib.sha256(json.dumps({k:v for k,v in actual.items() if k.startswith(d+'/')},sort_keys=True,separators=(',',':')).encode()).hexdigest() for d in groups},'global_geometry_sha256':actual['prototypes/global-pyramid/generated/global-geometry.json']}
assert hashlib.sha256((root/'docs/knowledge-map-adaptive-preview/global-reference.json').read_bytes()).hexdigest()==result['global_geometry_sha256']
(p/'integrity-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='file_hashes'},indent=2))
