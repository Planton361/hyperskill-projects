#!/usr/bin/env python3
"""Read-only spatial migration contract. No apply/approval/placement API."""
import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas import snapshot, activation_persistence, build as packaging, validate, transaction
VERSION='spatial-preview-1'
MASTER_HASH='bf79e7309129421b32899900a47f1c9f47d624f2fa16a4eb8b503f1be52aab25'
class Gate(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason

def require(ok,status,reason):
    if not ok:raise Gate(status,reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def fp(v):return snapshot.ordered_digest(v)
def read(p):return json.loads(p.read_bytes())
def inventory(root):
    paths=[p for d in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge','scripts/knowledge_atlas'] for p in (root/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [root/'prototypes/global-pyramid/generated/global-geometry.json',root/'prototypes/global-pyramid/generated/catalog.json']
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(paths)}
def runtime():
    paths=[BASE/'build.py',*sorted((BASE/'view').glob('*')),BASE.parent/'labels.js']
    return {str(p.relative_to(BASE.parent)):sha(p.read_bytes()) for p in paths if p.is_file()}
def load(root=ROOT):
    require(not (root/'state/.knowledge-atlas-transaction.json').exists(),'MIGRATION_SOURCE_CHANGED','Pending transaction requires separately authorized recovery')
    masterpath=root/'prototypes/global-pyramid/generated/global-geometry.json'
    require(sha(masterpath.read_bytes())==MASTER_HASH,'MIGRATION_TARGET_INVALID','Frozen master byte hash mismatch')
    try:
        packaging.verify_release(root/'docs/knowledge-map')
        data=snapshot.load_source(root/'data/knowledge')
        cp,previous,history,current,_=activation_persistence.accepted(root,data)
        validate.geometry(data,cp,current)
    except ValueError as e:raise Gate('MIGRATION_GEOMETRY_CONFLICT',str(e)) from e
    production=json.loads((root/'docs/knowledge-map/geometry.js').read_text().split('=',1)[1].rstrip(';\n'))
    require(production==current,'MIGRATION_GEOMETRY_CONFLICT','Production and ACTIVE_HISTORY geometry differ')
    require((root/'docs/knowledge-map/layout-checkpoint.json').read_bytes()==(root/'state/knowledge-atlas/layout-checkpoint.json').read_bytes(),'MIGRATION_GEOMETRY_CONFLICT','Production/state checkpoints differ')
    model=read(root/'docs/knowledge-map/model.json')
    require(all(snapshot.digest(model[t])==snapshot.digest(data[t]) for t in snapshot.TABLES),'MIGRATION_SEMANTIC_MISMATCH','Production semantic tables differ from accepted Knowledge')
    return dict(model=model,history=history,current=current,checkpoint=cp,master=read(masterpath))
def bounds(nodes):
    return dict(x=min(n['x'] for n in nodes),y=min(n['y'] for n in nodes),w=max(n['x']+n['w'] for n in nodes)-min(n['x'] for n in nodes),h=max(n['y']+n['h'] for n in nodes)-min(n['y'] for n in nodes))
def extent(b):return {**b,'width':b['w'],'height':b['h'],'area':b['w']*b['h'],'aspect_ratio':b['w']/b['h']}
def distribution(values):
    a=sorted(values);p=lambda q:a[max(0,math.ceil(q*len(a))-1)]
    return dict(count=len(a),min=min(a),max=max(a),mean=statistics.mean(a),median=statistics.median(a),p95=p(.95),p99=p(.99),total=math.fsum(a),unchanged=sum(v==0 for v in a),moved=sum(v!=0 for v in a))
def construct(model,history,current,checkpoint,master):
    status='MIGRATION_MAPPING_INCOMPLETE';active=history['active_categories']+history['active_topics'];keys=sorted(active)
    require(len(active)==len(set(active))==135 and len(history['active_categories'])==46 and len(history['active_topics'])==89,status,'Expected exact accepted 46 Category / 89 Topic inventory')
    facts={f'{kind}:{r["id"]}':r for table,kind in [('categories','category'),('topics','topic')] for r in model[table]}
    source={n['key']:n for n in current['nodes']}
    require(len(facts)==sum(len(model[t]) for t in ['categories','topics'])==135 and len(source)==len(current['nodes']) and set(keys)==set(source)==set(facts),status,'Accepted, Production geometry and semantic identity inventories differ')
    positions={n['key']:n for n in master['positions']};roots={s['root'] for s in master['root_sectors']}
    require(len(positions)==len(master['positions'])==3955 and len(roots)==5,'MIGRATION_TARGET_INVALID','Master duplicate slots / counts / roots')
    require(master['counts']==dict(categories=849,structural_leaves=3106,positions=3955,hierarchy_pairs=3952),'MIGRATION_TARGET_INVALID','Master counts differ')
    core={k:v for k,v in master.items() if k!='geometry_fingerprint'}
    require(fp(core)==master['geometry_fingerprint'],'MIGRATION_TARGET_INVALID','Embedded master fingerprint mismatch')
    aliases={r['slot']:r['semantic_aliases'] for r in master['leaf_identity_mapping']}
    require(len(aliases)==3106,'MIGRATION_TARGET_INVALID','Leaf alias inventory invalid')
    for n in positions.values():
        require(all(type(n[k]) in (int,float) and math.isfinite(n[k]) for k in ['x','y','w','h']) and n['w']>0 and n['h']>0,'MIGRATION_TARGET_INVALID','Invalid rectangle: '+n['key'])
        require(all(p in positions and p.startswith('category:') for p in n['parents']),'MIGRATION_TARGET_INVALID','Invalid secondary structural membership: '+n['key'])
        parent=n['primary_parent'];require(n['root'] in roots and (parent is None or parent in n['parents'] and parent in positions),'MIGRATION_TARGET_INVALID','Invalid parent/root: '+n['key'])
        if parent:require(positions[parent]['y']<n['y'],'MIGRATION_TARGET_INVALID','Invalid vertical hierarchy: '+n['key'])
        if n['key'].startswith('leaf:'):require(aliases.get(n['key'])==['reference:'+n['key'][5:],'topic:'+n['key'][5:]],'MIGRATION_TARGET_INVALID','Invalid leaf aliases')
    for i,a in enumerate(master['root_sectors']):
        for b in master['root_sectors'][i+1:]:require(a['x']+a['w']<=b['x'] or b['x']+b['w']<=a['x'],'MIGRATION_TARGET_INVALID','Overlapping sectors')
    require(len(master['hierarchy_routes'])==3955 and {r['child'] for r in master['hierarchy_routes']}==set(positions),'MIGRATION_TARGET_INVALID','Invalid route inventory')
    for r in master['hierarchy_routes']:require(r['parent']==(positions[r['child']]['primary_parent'] or 'presentation:hyperskill') and all(len(p)==2 and all(math.isfinite(v) for v in p) for p in r['points']),'MIGRATION_TARGET_INVALID','Invalid persisted route')
    def path(key,parent):
        out=[]
        while key:
            require(key not in out,'MIGRATION_GEOMETRY_CONFLICT','Cyclic display ancestry');out.append(key);key=parent(key)
        return list(reversed(out))
    cparent=lambda k:('category:'+str(facts[k]['canonical_parent_id'])) if facts[k]['canonical_parent_id'] is not None else None
    mapped=[];diff=[];cur=[];target=[];context=set()
    for key in keys:
        slot=key if key.startswith('category:') else 'leaf:'+key.split(':')[1]
        require(slot in positions,status,'Missing mapping: '+key+' -> '+slot)
        if key.startswith('topic:'):require(key in aliases[slot],status,'Ambiguous Topic alias: '+key)
        n=source[key];p=positions[slot];cp=cparent(key);cpath=path(key,cparent);tpath=path(slot,lambda k:positions[k]['primary_parent']);context.update(tpath)
        c=dict(key=key,slot=key,x=n['x']-n['width']/2,y=n['y'],w=n['width'],h=n['height'],native_x=n['x'],native_y=n['y'],depth=n['depth'],parent=cp,path=cpath,title=facts[key]['title'],type=key.split(':')[0])
        t=dict(key=key,slot=slot,x=p['x'],y=p['y'],w=p['w'],h=p['h'],depth=p['depth'],parent=p['primary_parent'],parents=p['parents'],root=p['root'],path=tpath,title=facts[key]['title'],type=key.split(':')[0])
        dx=t['x']-c['x'];dy=t['y']-c['y'];cdx=(t['x']+t['w']/2)-n['x'];cdy=(t['y']+t['h']/2)-(n['y']+n['height']/2)
        diff.append(dict(key=key,entity_type=c['type'],current_x=c['x'],current_y=c['y'],target_x=t['x'],target_y=t['y'],delta_x=dx,delta_y=dy,displacement=math.hypot(dx,dy),center_delta_x=cdx,center_delta_y=cdy,center_displacement=math.hypot(cdx,cdy),current_native_x=n['x'],current_native_y=n['y'],current_width=c['w'],current_height=c['h'],target_width=t['w'],target_height=t['h'],delta_width=t['w']-c['w'],delta_height=t['h']-c['h'],current_depth=c['depth'],target_depth=t['depth'],current_branch=cpath[2] if len(cpath)>2 else cpath[-1],current_path=cpath,target_path=tpath,target_global_root=p['root'],target_global_parent=p['primary_parent'],target_slot=slot))
        mapped.append(dict(key=key,slot=slot));cur.append(c);target.append(t)
    require(len({r['slot'] for r in mapped})==135,status,'Duplicate physical mappings')
    semantics={t:deepcopy(model[t]) for t in snapshot.TABLES};counts=dict(categories=46,topics=89,learned=len({p['topic_id'] for p in model['progress']['topics'] if p['is_learned'] is True}),verified=len({p['topic_id'] for p in model['progress']['topics'] if p['is_verified'] is True}),project_113=len({e['target'] for e in model['edges'] if e['type']=='project_requires' and e['source']=='project:113'}),stage_617=len({e['target'] for e in model['edges'] if e['type']=='project_requires' and e['source']=='project:113' and e.get('stage_id')==617}),generation=checkpoint['presentation_generation'],history_version=history['history_version'])
    require(counts==dict(categories=46,topics=89,learned=31,verified=12,project_113=26,stage_617=12,generation=0,history_version=0),'MIGRATION_SEMANTIC_MISMATCH','Baseline semantic counters differ')
    groups=defaultdict(list)
    for t in target:
        if t['type']=='topic':groups[t['parent']].append(t['slot'])
    metrics=dict(coordinate_convention='Displacement uses visual rectangle LEFT/TOP in native world units, no alignment/scaling/translation. V6 native x=center retained separately. Center-displacement separately measures visual centers. Percentiles: nearest rank.',displacement={kind:distribution([r['displacement'] for r in diff if kind=='all' or r['entity_type']==kind]) for kind in ['category','topic','all']},center_displacement={kind:distribution([r['center_displacement'] for r in diff if kind=='all' or r['entity_type']==kind]) for kind in ['category','topic','all']},current_bounds=extent(dict(x=current['bounds']['x0'],y=current['bounds']['y0'],w=current['bounds']['x1']-current['bounds']['x0'],h=current['bounds']['y1']-current['bounds']['y0'])),current_scope_extent=extent(bounds(cur)),target_scope_extent=extent(bounds(target)),target_world_bounds=extent(master['bounds']),size_changes=sum(r['delta_width']!=0 or r['delta_height']!=0 for r in diff),primary_parent_changes=[r['key'] for r,c,t in zip(diff,cur,target) if c['parent']!=t['parent']],current_trays=len(current['trays']),target_leaf_groups=len(groups),current_connector_segments=len(current['connectorSegments']),current_category_branches=len(current['branches']),current_hierarchy_pairs=sum(e['type']=='hierarchy' for e in model['edges']),target_scope_primary_routes=len(context),target_world_primary_routes=len(master['hierarchy_routes']),target_structural_pairs=3952,semantic_counts=counts,semantic_hashes_before={t:snapshot.digest(semantics[t]) for t in snapshot.TABLES},semantic_hashes_after={t:snapshot.digest(semantics[t]) for t in snapshot.TABLES})
    current_art=dict(schema_version=1,coordinate_convention='positions are left/top rectangles; native_geometry x is horizontal center/top',native_geometry=current,positions=cur,routes=[dict(parent=r['parent'],children=r['children'],points=[[p['x'],p['y']] for p in r['points']]) for r in current['connectorSegments']],bounds=metrics['current_bounds'],semantic_fingerprint=snapshot.digest(semantics))
    target_art=dict(schema_version=1,master_fingerprint=master['geometry_fingerprint'],master_sha256=MASTER_HASH,master_reference='../../generated/global-geometry.json',coordinate_convention='master left/top rectangles, exact coordinates',positions=target,context_positions=[positions[k] for k in sorted(context-set(r['slot'] for r in mapped))],hierarchy_routes=[r for r in master['hierarchy_routes'] if r['child'] in context],root_sectors=master['root_sectors'],world_bounds=master['bounds'],scope_extent=metrics['target_scope_extent'],leaf_groups=[dict(parent=k,slots=v) for k,v in sorted(groups.items())],trays='No V6 tray surfaces copied or reconstructed. Persisted global terminal leaf slots and routes are authoritative.',semantic_fingerprint=snapshot.digest(semantics))
    canonical_routes={r['child']:r for r in master['hierarchy_routes']}
    category_routes=[dict(child=r['child'],current_parent=r['parent'],target_parent=canonical_routes[r['child']]['parent'],current_points=[[p['x'],p['y']] for p in r['points']],target_points=canonical_routes[r['child']]['points'],changed=[[p['x'],p['y']] for p in r['points']]!=canonical_routes[r['child']]['points']) for r in current['branches']]
    target_nodes={n['key']:n for n in target}
    tray_comparison=[dict(current_surface=tray,target_slot_envelope=bounds([target_nodes[k] for k in tray['topics']]),topic_mapping=[dict(key=k,slot=target_nodes[k]['slot'],target_parent=target_nodes[k]['parent'],x=target_nodes[k]['x'],y=target_nodes[k]['y']) for k in tray['topics']],note='Envelope is comparison metadata only, not a new tray or layout region.') for tray in current['trays']]
    comparison=dict(schema_version=1,category_routes=category_routes,changed_category_routes=sum(r['changed'] for r in category_routes),topic_trays=tray_comparison,route_contract='V6 shared connector segments/tray rails are not one-to-one Topic edges. They are preserved in current-geometry; target uses only persisted global primary routes. Secondary memberships remain metadata and semantic hierarchy edges are unchanged.',root_placement=[r for r in diff if r['key'] in roots],source_geometry_fingerprint=fp(current),target_master_fingerprint=master['geometry_fingerprint'])
    return {'current-geometry.json':current_art,'target-geometry.json':target_art,'migration-diff.json':dict(schema_version=1,coordinate_convention=metrics['coordinate_convention'],entities=diff),'migration-metrics.json':metrics,'geometry-comparison.json':comparison,'semantic-snapshot.json':semantics},mapped

def artifacts(root=ROOT):
    before=inventory(root)
    with transaction.lock(root,write=False):
        inputs=load(root);start=time.perf_counter();values,mapping=construct(**inputs);diff_ms=(time.perf_counter()-start)*1000
        bindings=dict(input_files=before,source_production_geometry=fp(inputs['current']),source_checkpoint=fp(inputs['checkpoint']),source_activation_state=fp(inputs['history']),source_knowledge=snapshot.digest(snapshot.load_source(root/'data/knowledge')),target_global_geometry=inputs['master']['geometry_fingerprint'],target_global_bytes=MASTER_HASH,runtime_files=runtime(),preview_runtime=fp(runtime()))
        output={k:snapshot.encode(v) for k,v in values.items()}
        manifest=dict(schema_version=1,status='MIGRATION_PREVIEW_READY',dry_run=True,algorithm=VERSION,bindings=bindings,accepted_inventory=[r['key'] for r in mapping],target_mapping=mapping,artifact_hashes={k:sha(v) for k,v in output.items()},generation_change=0,history_change=0,mapping_failures=[])
        manifest['manifest_fingerprint']=fp(manifest);output['migration-manifest.json']=snapshot.encode(manifest)
        require(before==inventory(root),'MIGRATION_SOURCE_CHANGED','Inputs changed while building preview')
    return output,diff_ms

def check(root=ROOT,directory=BASE):
    try:manifest=read(directory/'migration-manifest.json')
    except (OSError,ValueError):raise Gate('MIGRATION_SOURCE_CHANGED','Missing/invalid preview manifest')
    require(manifest.get('manifest_fingerprint')==fp({k:v for k,v in manifest.items() if k!='manifest_fingerprint'}),'MIGRATION_GEOMETRY_CONFLICT','Manifest integrity mismatch')
    require(manifest['bindings']['input_files']==inventory(root) and manifest['bindings']['runtime_files']==runtime(),'MIGRATION_SOURCE_CHANGED','Preview is stale: source or implementation changed')
    for name,h in manifest['artifact_hashes'].items():require((directory/name).is_file() and sha((directory/name).read_bytes())==h,'MIGRATION_GEOMETRY_CONFLICT','Preview artifact mismatch: '+name)
    fresh,_=artifacts(root)
    require(all((directory/n).read_bytes()==v for n,v in fresh.items()),'MIGRATION_GEOMETRY_CONFLICT','Deterministic artifact mismatch')
    return dict(status='MIGRATION_PREVIEW_READY',dry_run=True,manifest_fingerprint=manifest['manifest_fingerprint'])
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();start=time.perf_counter()
    try:
        if args.check:result=check()
        else:
            output,diff_ms=artifacts()
            for n,v in output.items():(BASE/n).write_bytes(v)
            result=dict(status='MIGRATION_PREVIEW_READY',dry_run=True,diff_computation_ms=diff_ms,artifact_bytes=sum(map(len,output.values())))
        result['preview_build_ms']=(time.perf_counter()-start)*1000;print(json.dumps(result))
    except Gate as e:print(json.dumps(dict(status=e.status,reason=e.reason,dry_run=True)));sys.exit(1)
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps(dict(status='MIGRATION_SOURCE_CHANGED',reason='Invalid or unavailable source/preview input',dry_run=True)));sys.exit(1)
