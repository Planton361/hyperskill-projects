"""Strict installed canonical authority, hydration and reserved-slot selection.

No generator, allocator, prototype import or alternate coordinates. Metadata is
not part of spatial identity. The persisted migration contract remains schema 1.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from . import snapshot, transaction

AUTHORITY_FIELDS={'kind','schema_version','geometry_schema_version','geometry_fingerprint','geometry_sha256','catalog_fingerprint','layout_algorithm_version','review_candidate_fingerprint','slot_contract','master_asset'}
CP_FIELDS={'state_schema_version','layout_schema_version','layout_algorithm_version','presentation_generation','spatial_authority','accepted_inventory','target_geometry_fingerprint'}
HISTORY_FIELDS={'schema_version','history_version','layout_generation','active_categories','active_topics','events','spatial_authority','accepted_geometry','geometry_fingerprint'}
TARGET_FIELDS={'schema_version','master_fingerprint','master_sha256','master_reference','coordinate_convention','positions','context_positions','hierarchy_routes','root_sectors','world_bounds','scope_extent','leaf_groups','trays','semantic_fingerprint'}
SLOT_CONTRACT='category:<id> -> category:<id>; reference:<id> and topic:<id> -> leaf:<id>'
MIGRATION='SPATIAL_AUTHORITY_MIGRATION_REQUIRED'
EXTENSION='SPATIAL_AUTHORITY_EXTENSION_REQUIRED'
REAL_ROOT=Path(__file__).resolve().parents[2]

def require(ok,message,status=MIGRATION):
    if not ok:raise ValueError(status+': '+message)
def read(p):return json.loads(Path(p).read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def fp(v):return snapshot.ordered_digest(v)
def slot(key):
    kind,number=key.split(':');require(kind in ('category','topic','reference') and number.isdigit() and int(number)>0,'Invalid slot identity',EXTENSION)
    return key if kind=='category' else 'leaf:'+number

def installed(path):
    """Presence is a dispatch trigger, never evidence of a valid authority."""
    path=Path(path)
    if (path/'spatial-authority.json').exists():return True
    for n in ('layout-checkpoint.json','update-snapshot.json','activation-state.json'):
        if (path/n).exists():
            v=read(path/n)
            if 'spatial_authority' in v or v.get('state_schema_version')==3 or n=='activation-state.json' and v.get('schema_version')==2:
                raise ValueError(MIGRATION+': partial authority')
    return False

def writer_guard(root):
    """Real writes require an explicitly reviewed, installed migration receipt."""
    root=Path(root).resolve();marker=root/'.atlas-disposable-test'
    from . import spatial_authorization as authorization
    if root==authorization.ROOT and (root/'.git').exists():
        authorization.real_repository(root)
        require((root/'state/knowledge-atlas/spatial-authority.json').is_file(),'No reviewed canonical authority installed','REAL_CANONICAL_PUBLICATION_FORBIDDEN')
        restore(root/'state/knowledge-atlas')
        receipt=read(root/'state/knowledge-atlas/spatial-migration-review.json')
        require(receipt.get('fixture_only') is False and receipt['contract']['policy']['publication_policy']==authorization.PUBLICATION_POLICY,'Real canonical authority requires a real migration receipt','REAL_CANONICAL_PUBLICATION_FORBIDDEN')
        return
    require(not (root/'.git').exists() and marker.is_file() and not marker.is_symlink() and marker.read_text()=='spatial-migration-tests-v1\n','Canonical publication requires external disposable root','REAL_CANONICAL_PUBLICATION_FORBIDDEN')
    for parent in (root, *root.parents):
        require(not (parent/'.git').exists(),'Canonical writes inside a real checkout are disabled','REAL_CANONICAL_PUBLICATION_FORBIDDEN')
    for d in ('state','docs','data','state/knowledge-atlas','docs/knowledge-map','data/knowledge'):
        require(not (root/d).is_symlink(),'Symlink refused','REAL_CANONICAL_PUBLICATION_FORBIDDEN')

def master(root,authority):
    require(set(authority)==AUTHORITY_FIELDS and authority.get('kind')=='global-canonical-pyramid' and type(authority.get('schema_version')) is int and authority['schema_version']==1,'Unknown authority schema')
    require(type(authority['geometry_schema_version']) is int and authority['geometry_schema_version']==1 and authority['layout_algorithm_version'] in ('canonical-pyramid-a-1','canonical-pyramid-a-2-root-composition') and authority['master_asset']=='generated/global-geometry.json' and authority['slot_contract']==SLOT_CONTRACT,'Unknown geometry/slot contract')
    for field in ('geometry_fingerprint','geometry_sha256','catalog_fingerprint','review_candidate_fingerprint'):
        require(isinstance(authority[field],str) and len(authority[field])==64 and all(c in '0123456789abcdef' for c in authority[field]),'Invalid authority fingerprint')
    p=Path(root)/'docs/knowledge-map'/authority['master_asset'];require(p.is_file() and not p.is_symlink(),'Installed master missing');raw=p.read_bytes();g=json.loads(raw)
    require(sha(raw)==authority['geometry_sha256'] and g['geometry_fingerprint']==authority['geometry_fingerprint'] and fp({k:v for k,v in g.items() if k!='geometry_fingerprint'})==g['geometry_fingerprint'],'Master fingerprint mismatch')
    require(g['geometry_schema_version']==authority['geometry_schema_version'] and g['layout_algorithm_version']==authority['layout_algorithm_version'] and g['source_catalog_fingerprint']==authority['catalog_fingerprint'],'Authority/master version mismatch')
    slots={n['key']:n for n in g['positions']};require(len(slots)==len(g['positions']),'Duplicate slots')
    aliases={r['slot']:r['semantic_aliases'] for r in g['leaf_identity_mapping']}
    for key,n in slots.items():
        require(key==n['key'] and (n['primary_parent'] is None or n['primary_parent'] in n['parents'] and n['primary_parent'] in slots),'Invalid primary parent')
        if key.startswith('leaf:'):require(set(aliases.get(key,[]))=={'reference:'+key.split(':')[1],'topic:'+key.split(':')[1]},'Invalid leaf aliases')
    require(len(g['root_sectors'])==5 and {s['root'] for s in g['root_sectors']}=={n['key'] for n in slots.values() if n['primary_parent'] is None},'Invalid roots')
    require(len(g['hierarchy_routes'])==len(slots) and {r['child'] for r in g['hierarchy_routes']}==set(slots),'Route inventory mismatch')
    for route in g['hierarchy_routes']:require(route['parent']==(slots[route['child']]['primary_parent'] or 'presentation:hyperskill'),'Route parent mismatch')
    return g

def path(slots,key):
    out=[]
    while key:
        require(key not in out and key in slots,'Invalid ancestor path');out.insert(0,key);key=slots[key]['primary_parent']
    return out

def extent(rows):
    x=min(n['x'] for n in rows);y=min(n['y'] for n in rows);w=max(n['x']+n['w'] for n in rows)-x;h=max(n['y']+n['h'] for n in rows)-y
    return dict(x=x,y=y,w=w,h=h,width=w,height=h,area=w*h,aspect_ratio=w/h)

def validate_geometry(g,geometry,keys):
    require(set(geometry)==TARGET_FIELDS and type(geometry['schema_version']) is int and geometry['schema_version']==1,'Unknown accepted geometry')
    slots={n['key']:n for n in g['positions']};rows=geometry['positions'];require([n['key'] for n in rows]==sorted(keys),'Accepted inventory mismatch')
    used=set();context=set()
    for n in rows:
        require(set(n)=={'key','slot','x','y','w','h','depth','parent','parents','root','path','title','type'} and isinstance(n['title'],str) and bool(n['title']),'Unknown position fields/metadata')
        s=slot(n['key']);require(s in slots and s not in used,'Missing/duplicate slot',EXTENSION);used.add(s);p=slots[s];chain=path(slots,s);context.update(chain)
        require(n['slot']==s and all(n[k]==p[k] for k in ('x','y','w','h','depth','root','parents')) and n['parent']==p['primary_parent'] and n['path']==chain and n['type']==n['key'].split(':')[0],'Noncanonical accepted position')
    require(geometry['master_fingerprint']==g['geometry_fingerprint'] and geometry['master_sha256']==sha(snapshot.encode(g)),'Accepted master mismatch')
    require(geometry['world_bounds']==g['bounds'] and geometry['root_sectors']==g['root_sectors'] and geometry['scope_extent']==extent(rows),'Accepted bounds/sectors mismatch')
    require(geometry['hierarchy_routes']==[r for r in g['hierarchy_routes'] if r['child'] in context] and geometry['context_positions']==[slots[k] for k in sorted(context-used)],'Noncanonical routes/context')
    groups={}
    for n in rows:
        if n['type']=='topic':groups.setdefault(n['parent'],[]).append(n['slot'])
    require(geometry['leaf_groups']==[dict(parent=k,slots=v) for k,v in sorted(groups.items())],'Invalid leaf groups')
    return geometry

def restore(state_path, *, _in_transaction=False):
    state_path=Path(state_path);root=state_path.parents[1]
    require(state_path==root/'state/knowledge-atlas','Canonical state must be installed at standard path')
    require(not any(p.is_symlink() for p in state_path.rglob('*')),'Symlinked authority state')
    require(_in_transaction or not (root/'state/.knowledge-atlas-transaction.json').exists(),'Pending transaction','RECOVERY_REQUIRED')
    a=read(state_path/'spatial-authority.json');cp=read(state_path/'layout-checkpoint.json');prev=read(state_path/'update-snapshot.json');h=read(state_path/'activation-state.json');g=master(root,a)
    require(set(cp)==CP_FIELDS and cp['state_schema_version']==3 and cp['spatial_authority']==a and cp['layout_schema_version']==a['geometry_schema_version'] and cp['layout_algorithm_version']==a['layout_algorithm_version'],'Checkpoint/authority mismatch')
    require(set(h)==HISTORY_FIELDS and h['schema_version']==2 and h['spatial_authority']==a and h['layout_generation']==cp['presentation_generation'],'History/authority mismatch')
    for field,kind in [('active_categories','category'),('active_topics','topic')]:
        require(h[field]==sorted(set(h[field])) and all(k.startswith(kind+':') for k in h[field]),'Invalid ACTIVE_HISTORY')
    keys=sorted(h['active_categories']+h['active_topics']);require(cp['accepted_inventory']==keys,'Checkpoint/history inventory mismatch')
    require(all(type(v) is int for v in (cp['state_schema_version'],cp['layout_schema_version'],h['schema_version'],h['layout_generation'])),'Noninteger schema/counter')
    geom=validate_geometry(g,h['accepted_geometry'],keys)
    require(cp['target_geometry_fingerprint']==h['geometry_fingerprint']==fp(geom),'Accepted geometry hash mismatch')
    require(set(prev)=={'state_schema_version','spatial_authority','checkpoint_fingerprint','geometry_fingerprint','source_index'} and prev['state_schema_version']==3 and prev['spatial_authority']==a and prev['checkpoint_fingerprint']==fp(cp) and prev['geometry_fingerprint']==fp(geom),'Snapshot mismatch')
    require(type(h['history_version']) is int and len(h['events'])==h['history_version'],'Invalid activation version')
    event_fields={'manifest_fingerprint','plan_fingerprint','candidate_fingerprint','variant','generation'}
    for e in h['events']:
        require(set(e)==event_fields and e['variant'] in ('current','parent-distance','centering','connector','balanced','canonical-reveal') and type(e['generation']) is int and 0<e['generation']<=cp['presentation_generation'],'Invalid activation event')
        for k in ('manifest_fingerprint','plan_fingerprint','candidate_fingerprint'):require(isinstance(e[k],str) and len(e[k])==64 and all(c in '0123456789abcdef' for c in e[k]),'Invalid activation fingerprint')
        if e['variant']=='canonical-reveal':
            review=read(state_path/'activation-reviews'/f"{e['manifest_fingerprint']}.json")
            require(review['manifest_fingerprint']==e['manifest_fingerprint'] and fp({k:v for k,v in review.items() if k!='manifest_fingerprint'})==e['manifest_fingerprint'],'Reveal receipt changed')
    events=read(state_path/'spatial-migrations.json');receipt=read(state_path/'spatial-migration-review.json')
    require(set(events)=={'schema_version','spatial_history_version','events'} and events['schema_version']==1 and events['spatial_history_version']==1 and len(events['events'])==1,'Unknown spatial history')
    event=events['events'][0];require(event==dict(type='SPATIAL_AUTHORITY_MIGRATION',version=1,review_candidate_fingerprint=a['review_candidate_fingerprint'],from_geometry=receipt['contract']['source']['accepted_geometry_fingerprint'],to_geometry=a['geometry_fingerprint'],generation_before=receipt['contract']['source']['presentation_generation'],generation_after=cp['presentation_generation'],active_history_identity=receipt['contract']['source']['active_history_identity']),'Spatial event mismatch')
    require(cp['presentation_generation']==event['generation_before']+1 and type(cp['presentation_generation']) is int and h['layout_generation']==cp['presentation_generation'],'Spatial Generation mismatch')
    require(fp({k:v for k,v in receipt.items() if k!='manifest_fingerprint'})==receipt['manifest_fingerprint'] and receipt['review_candidate_fingerprint']==a['review_candidate_fingerprint'],'Migration receipt mismatch')
    require(fp(receipt['contract'])==a['review_candidate_fingerprint'] and receipt['files']['candidate/state/spatial-authority.json']==sha(snapshot.encode(a)),'Authority is not the reviewed migration binding')
    require(receipt['contract']['target']==dict(geometry_fingerprint=a['geometry_fingerprint'],geometry_sha256=a['geometry_sha256'],geometry_schema_version=a['geometry_schema_version'],layout_algorithm_version=a['layout_algorithm_version'],catalog_fingerprint=a['catalog_fingerprint']),'Authority target differs from migration receipt')
    return cp,prev,h,geom,g

def validate_structure(loaded,g,previous=None):
    from .catalog import Catalog
    try:c=Catalog(loaded, allow_metadata_updates=True)
    except ValueError as e:raise ValueError(EXTENSION+': '+str(e)) from e
    slots={n['key']:n for n in g['positions']}
    for kind,records in [('category',c.categories),('topic',c.topics)]:
        for key,row in records.items():
            s=slot(key);require(s in slots,'Unknown structural entity '+key,EXTENSION)
            parent=row.get('accepted_metadata',{}).get('canonical_parent_id',row.get('parent_id'))
            require(parent is None and not slots[s]['parents'] or 'category:'+str(parent) in slots[s]['parents'],'Changed structural parent '+key,EXTENSION)
            if previous:
                before=previous['source_index']['categories' if kind=='category' else 'topics'].get(key.split(':')[1])
                if before:require(before['parent']==snapshot.digest(parent),'Changed accepted structural parent '+key,EXTENSION)
    for n in g['positions']:
        numeric=int(n['key'].split(':')[1]);require(c.memberships.get(numeric,set())=={int(k.split(':')[1]) for k in n['parents']},'Changed structural memberships '+n['key'],EXTENSION)
    require(c.snapshot_positions['categories']=={k for k in slots if k.startswith('category:')} and c.snapshot_positions['leaves']=={int(k.split(':')[1]) for k in slots if k.startswith('leaf:')},'Changed captured structural inventory',EXTENSION)
    return c

def reveal_geometry(g,frozen,keys,catalog):
    """Extend visibility by copying reserved records, preserving accepted rows."""
    out=deepcopy(frozen);existing={n['key']:n for n in frozen['positions']};slots={n['key']:n for n in g['positions']};rows=[];context=set();used=set();groups={}
    for key in sorted(keys):
        s=slot(key);require(s in slots,'Unknown '+key,EXTENSION);p=slots[s];chain=path(slots,s);context.update(chain);used.add(s)
        if key in existing:n=deepcopy(existing[key])
        else:
            fact=(catalog.categories if key.startswith('category:') else catalog.topics).get(key)
            require(fact and fact.get('accepted_metadata') and fact.get('title'),'Topic/Category metadata required '+key,'METADATA_REQUIRED')
            n=dict(key=key,slot=s,x=p['x'],y=p['y'],w=p['w'],h=p['h'],depth=p['depth'],parent=p['primary_parent'],parents=p['parents'],root=p['root'],path=chain,title=fact['title'],type=key.split(':')[0])
        rows.append(n)
        if n['type']=='topic':groups.setdefault(n['parent'],[]).append(s)
    out.update(positions=rows,context_positions=[deepcopy(slots[k]) for k in sorted(context-used)],hierarchy_routes=[deepcopy(r) for r in g['hierarchy_routes'] if r['child'] in context],scope_extent=extent(rows),leaf_groups=[dict(parent=k,slots=v) for k,v in sorted(groups.items())])
    return validate_geometry(g,out,keys)

def complete(data,cp,geom):
    index=snapshot.index(data);index['checkpoint_fingerprint']=fp(cp);index['geometry_fingerprint']=fp(geom)
    return dict(state_schema_version=3,spatial_authority=cp['spatial_authority'],checkpoint_fingerprint=fp(cp),geometry_fingerprint=fp(geom),source_index=index)

def outputs(path,cp,previous,history=None):
    out={p.relative_to(path).as_posix():p.read_bytes() for p in Path(path).rglob('*') if p.is_file()}
    out.update({'layout-checkpoint.json':snapshot.encode(cp),'update-snapshot.json':snapshot.encode(previous)})
    if history is not None:out['activation-state.json']=snapshot.encode(history)
    return out

def restore_after_swap(path):
    return restore(path, _in_transaction=True)

def recover_staging(root):
    """Explicit disposable recovery also clears stages orphaned before journaling."""
    import shutil
    root=Path(root);writer_guard(root)
    for parent in (root/'state',root/'docs'):
        for p in parent.glob('.atlas-candidate-*'):
            require(p.is_dir() and not p.is_symlink(),'Unsafe orphan staging directory','RECOVERY_REQUIRED')
            shutil.rmtree(p);transaction.sync_dir(parent)
