#!/usr/bin/env python3
"""Package the frozen V6.6 runtime; publish no test tooling or fixtures."""
import argparse,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]
ROOT=SOURCE.parents[1]
DEST=ROOT/'docs/knowledge-atlas-preview'
ASSETS=['app.js','index.html','layout-checkpoint.json','layout-checkpoint.schema.json','layout.js','model.js','model.json','routing.js','style.css','vendor/D3-LICENSE','vendor/d3-7.9.0.min.js']
sha=lambda b:hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
raw=json.loads((SOURCE/'model.json').read_text())
for table in ['categories','topics','edges','projects','stages','courses','progress','evidence']:
 data=(ROOT/'data/knowledge'/f'{table}.json').read_bytes();assert raw[table]==json.loads(data),table;assert raw['source_hashes'][table]==sha(data),table
assert (len(raw['topics']),len(raw['categories']))==(89,46)
assert sum(t['is_learned'] is True for t in raw['progress']['topics'])==31
assert sum(t['is_verified'] is True for t in raw['progress']['topics'])==12
req={e['target']for e in raw['edges']if e['type']=='project_requires'and e['source']=='project:113'}
stage=next(s for s in raw['stages']if s['project_id']==113 and s['position']==4)
assert len(req)==26 and len({e['target']for e in raw['edges']if e['type']=='project_requires'and e['source']=='project:113'and e['stage_id']==stage['id']})==12
assert not any(e['type']=='project_applies'for e in raw['edges'])
assert next(p for p in raw['progress']['projects']if p['project_id']==113)['status']=='completed'
assert next(p for p in raw['projects']if p['id']==113)['title']=='Simple Chat Bot with Java'
source={name:(SOURCE/name).read_bytes()for name in ASSETS}
prior=HERE/'source-before.json'
source_hashes={name:sha(data)for name,data in source.items()}
if prior.exists():assert json.loads(prior.read_text())==source_hashes,'Accepted source changed after capture'
else:prior.write_text(json.dumps(source_hashes,indent=2)+'\n')
expected=dict(source)
html=source['index.html'].decode();assert html.count('<title>Knowledge Atlas · V6.6 focus + context prototype</title>')==1
html=html.replace('<title>Knowledge Atlas · V6.6 focus + context prototype</title>','<title>Knowledge Atlas · Preview</title>')
assert html.count('<h1>Knowledge Map <small>· Prototype V6.6</small></h1>')==1
html=html.replace('<h1>Knowledge Map <small>· Prototype V6.6</small></h1>','<h1>Knowledge Atlas <small>· Preview</small></h1>')
expected['index.html']=html.encode()
for name,data in expected.items():assert not re.search(rb'/home/anton|localhost|127\.0\.0\.1|file://|node_modules',data),name
manifest={'sourceVersion':'accepted V6.6 release candidate; frozen V6.5 spatial geometry','deploymentPath':'docs/knowledge-atlas-preview/','publicUrl':'https://planton361.github.io/hyperskill-projects/knowledge-atlas-preview/','layoutSchemaVersion':5,'layoutAlgorithmVersion':'atlas-spatial-5','data':{'topics':89,'categories':46,'learned':31,'verified':12,'project113':{'title':'Simple Chat Bot with Java','status':'completed','distinctProjectRequires':26,'stage4ExplicitRequirements':12},'projectApplies':0,'source_sha256':raw['source_hashes']},'sourceAssets':source_hashes,'assets':{name:sha(data)for name,data in expected.items()},'brandingOnlyDifference':'index title and quiet Knowledge Atlas · Preview heading'}
expected['release-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
if not args.check:
 DEST.mkdir(parents=True,exist_ok=True)
 for name,data in expected.items():p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
else:
 for name,data in expected.items():assert (DEST/name).read_bytes()==data,name
allowed=set(expected)|{'PREVIEW-NOTES.md'}
assert {p.relative_to(DEST).as_posix()for p in DEST.rglob('*')if p.is_file()}<=allowed,'Unexpected published files'
assert source_hashes=={name:sha((SOURCE/name).read_bytes())for name in ASSETS},'Source mutated during packaging'
(HERE/'source-after.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('PASS: real data; immutable source/checkpoint; branding-only HTML; static runtime; no fixtures; '+('verified'if args.check else'packaged'))
