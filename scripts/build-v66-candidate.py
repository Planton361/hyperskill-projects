#!/usr/bin/env python3
"""Candidate-only deterministic package; refuse original/non-disposable worktrees."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'.git').is_dir() or not (ROOT/'.git').is_file():
    raise SystemExit('Requires an isolated linked Git worktree')
OUT=ROOT/'docs/knowledge-map'
HISTORY=ROOT/'prototypes/project-completion/candidate-history'
HISTORY.mkdir(parents=True,exist_ok=True)
if not (HISTORY/'production').exists():
    shutil.copytree(OUT,HISTORY/'production')
manifest_source=ROOT/'prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json'
shutil.copy2(manifest_source,HISTORY/'apply-manifest.json')
projection=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'scripts/sync-project-completion.py')]))['projection']
ledger=[]
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir(parents=True)
def copy(source,target):
    raw=(ROOT/source).read_bytes();dest=OUT/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    ledger.append(dict(source=source,target=target,source_sha256=hashlib.sha256(raw).hexdigest()))
def adapt(name,old,new):
    path=OUT/name;s=path.read_text()
    if old not in s:raise ValueError('Adapter source mismatch: '+name)
    path.write_text(s.replace(old,new))
for name in ['index.html','shell.css','shell.js']:
    copy('prototypes/knowledge-atlas-navigation/'+name,name)
for name in ['navigation.js','navigation.css']:
    copy('prototypes/knowledge-atlas-navigation/'+name,'views/knowledge-atlas-navigation/'+name)
adapt('shell.js',"'../knowledge-atlas-", "'views/knowledge-atlas-")
adapt('views/knowledge-atlas-navigation/navigation.js',"new URL('index.html',script)","new URL('../../index.html',script)")
adapt('index.html','Knowledge Atlas · V6.6 prototype','Knowledge Atlas · V6.6')
sets={
'knowledge-atlas-v6-global':['index.html','style.css','renderer.css','viewport.css','app.js','layout.js','model.js','model.json','routing.js','tile-paint.js','tile-worker.js','tiled-renderer.js','vendor/d3-7.9.0.min.js','vendor/D3-LICENSE'],
'knowledge-atlas-v6-skill-tree':['index.html','style.css','app.js','layout.js','model.js','model.json','global-registry.js','routing.js','progress-analytics.js','progress-presentation.js','progress-ui.js','progress.css','global.html','vendor/d3-7.9.0.min.js','vendor/D3-LICENSE'],
'knowledge-atlas-scope-pyramid':['index.html','style.css','scope.css','app.js','layout.js','layout-worker.js','projection.js','routing.js','ux-model.js','scope-index.json','catalog.json','global.html']}
for folder,names in sets.items():
    for name in names:copy('prototypes/'+folder+'/'+name,'views/'+folder+'/'+name)
for name in ['courses.json','evidence.json']:copy('data/knowledge/'+name,'data/knowledge/'+name)
# Resolve dormant personal snapshot references from committed catalog identities.
# Preserve the accepted existing Topic/Category metadata and renderer geometry.
personal_path=OUT/'views/knowledge-atlas-v6-skill-tree/model.json'
personal=json.loads(personal_path.read_text())
catalog=json.loads((OUT/'views/knowledge-atlas-scope-pyramid/catalog.json').read_text())
existing={row['id']:row for row in personal['topics']}
personal['topics']=[existing.get(row['id'],row) for row in catalog['topics']]
resolved={row['id'] for row in personal['topics']}
personal['references']=[row for row in personal['references'] if row['id'] not in resolved]
personal_path.write_text(json.dumps(personal,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

for folder,file in [('knowledge-atlas-v6-global','app.js'),('knowledge-atlas-v6-skill-tree','app.js'),('knowledge-atlas-v6-skill-tree','progress-ui.js'),('knowledge-atlas-scope-pyramid','app.js')]:
    adapt('views/'+folder+'/'+file,"../project-completion/progress.json","../../progress.json")
for folder in sets:
    name='views/'+folder+'/index.html'
    adapt(name,'src="../knowledge-atlas-v6-skill-tree/progress-analytics.js"></script>' if folder!='knowledge-atlas-v6-skill-tree' else 'src="progress-analytics.js"></script>',
          ('src="../knowledge-atlas-v6-skill-tree/progress-analytics.js"></script>' if folder!='knowledge-atlas-v6-skill-tree' else 'src="progress-analytics.js"></script>')+'<script src="../../projection-adapter.js"></script>')
(OUT/'projection-adapter.js').write_text("""/* Release boundary validation; the accepted aggregator remains authoritative. */
(() => {
const original=ProgressAnalytics.create;
ProgressAnalytics.create=function(input){
 const projection=input.completion||input.catalog.projectCompletion;
 if(projection?.schema!==2)throw Error('Generated public projection required');
 const analytics=original(input),learned=[],verified=[];
 for(const topic of input.catalog.topics){const s=analytics.topic(topic.id);if(s.learned===true)learned.push(topic.id);if(s.verified===true)verified.push(topic.id);}
 const sort=ids=>[...ids].sort((a,b)=>a-b);
 for(const [actual,expected] of [[learned,projection.effective_learned_topic_ids],[verified,projection.verified_topic_ids]])
  if(JSON.stringify(sort(actual))!==JSON.stringify(sort(expected)))throw Error('Public projection and source evidence disagree');
 globalThis.PublicProgress=projection;return analytics;
};
})();
""")
(OUT/'progress.json').write_text(json.dumps(projection,sort_keys=True,indent=2)+'\n')
shutil.copytree(HISTORY/'production',OUT/'previous-adaptive')
# Retain the historic release manifest at its original name as well as in archive.
shutil.copy2(HISTORY/'production/release-manifest.json',OUT/'release-manifest.json')
shutil.copy2(HISTORY/'apply-manifest.json',OUT/'historical-release-manifest.json')
(OUT/'global.html').write_text('<!doctype html><meta charset="utf-8"><title>Knowledge Atlas</title><script>const u=new URL("index.html",location.href);u.search=location.search;if(!u.searchParams.has("key")&&/^(topic|category):[1-9][0-9]*$/.test(location.hash.slice(1)))u.searchParams.set("key",location.hash.slice(1));location.replace(u.href);</script>')
legacy="""<script>const q=new URLSearchParams(location.search);let changed=false;for(const k of ['course','project','stage'])if(q.has(k+'_id')&&!q.has(k)){q.set(k,q.get(k+'_id'));q.delete(k+'_id');changed=true;}if(['my','my-atlas','my-knowledge'].includes(q.get('view'))){q.set('view','skill-tree');changed=true;}if(!q.has('key')&&/^(topic|category):[1-9][0-9]*$/.test(location.hash.slice(1))){q.set('key',location.hash.slice(1));changed=true;}if(changed)history.replaceState(null,'','?'+q);</script>"""
adapt('index.html','<script src="shell.js">',legacy+'<script src="shell.js">')
inventory={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()}
record=dict(schema=1,edition='unified-v66-candidate',source_commit=projection['source']['commit'],source_assets=ledger,inventory=inventory,adapters=['relative base-path relocation','generated projection boundary validation','personal dormant-ID resolution from committed Global catalog','legacy URL adapters'],historical_manifest_sha256=hashlib.sha256(manifest_source.read_bytes()).hexdigest())
(OUT/'candidate-manifest.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print(json.dumps(dict(files=len(inventory)+1,learned=projection['global']['learned'],verified=projection['global']['verified'],completed=projection['completed_project_count'])))
