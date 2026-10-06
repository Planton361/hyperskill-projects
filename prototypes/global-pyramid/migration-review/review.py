#!/usr/bin/env python3
"""Exact review/approval contract; explicit real authorization shares the marked-test transaction."""
import argparse
from copy import deepcopy
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas import snapshot, transaction, build, spatial_authorization as authorization
spec=importlib.util.spec_from_file_location('spatial_preview',BASE.parent/'migration-preview/build.py')
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
VERSION='exact-spatial-review-1'
STALE='STALE_SPATIAL_MIGRATION_PREVIEW'
MARKER='.atlas-disposable-test'
MANIFEST_FIELDS={'schema_version','algorithm_version','fixture_only','contract','review_candidate_fingerprint','files','manifest_fingerprint'}
AUTHORITY_FIELDS={'kind','schema_version','geometry_schema_version','geometry_fingerprint','geometry_sha256','catalog_fingerprint','layout_algorithm_version','review_candidate_fingerprint','slot_contract','master_asset'}
CP_FIELDS={'state_schema_version','layout_schema_version','layout_algorithm_version','presentation_generation','spatial_authority','accepted_inventory','target_geometry_fingerprint'}
HISTORY_FIELDS={'schema_version','history_version','layout_generation','active_categories','active_topics','events','spatial_authority','accepted_geometry','geometry_fingerprint'}
EVENT_FIELDS={'schema_version','spatial_history_version','events'}
TRANSACTION_PLAN=dict(schema_version=1,destinations=['state/knowledge-atlas','docs/knowledge-map'],knowledge_writes=False,commit_point='durable COMMITTED journal after exact post-swap verification',generation_policy='one spatial increment; activation history unchanged',replay_policy='ALREADY_APPLIED only after exact package/output/source verification',spatial_history_policy='separate typed event, exactly once',publication_policy=authorization.PUBLICATION_POLICY,detached_state_receipt='spatial-migration-review.json = exact reviewed migration-manifest.json bytes; external reviewed fingerprint binds the manifest itself',recovery='pre-commit rollback both; post-commit preserve both and cleanup')
class Refusal(ValueError):
    def __init__(self,status,reason):self.status=status;self.reason=reason;super().__init__(status+': '+reason)
def need(condition,reason,status=STALE):
    if not condition:raise Refusal(status,reason)
def sha(b):return hashlib.sha256(b).hexdigest()
def fp(v):return snapshot.ordered_digest(v)
def read(p):return json.loads(Path(p).read_bytes())
def encoded(v):return snapshot.encode(v)
def digest_files(files):return {k:sha(v) for k,v in sorted(files.items())}
def tree(path):
    path=Path(path);out={}
    need(path.is_dir(),'Missing directory: '+str(path))
    for p in sorted(path.rglob('*')):
        need(not p.is_symlink(),'Symlink refused: '+str(p))
        if p.is_file():out[p.relative_to(path).as_posix()]=p.read_bytes()
    return out
def disposable(root):
    root=Path(root).resolve()
    need(root!=ROOT and not root.is_relative_to(ROOT) and (root/MARKER).is_file() and not (root/MARKER).is_symlink() and (root/MARKER).read_text()=='spatial-migration-tests-v1\n','Real publication is disabled; marked external disposable root required','REAL_SPATIAL_MIGRATION_FORBIDDEN')
    for d in ['state','docs','data','state/knowledge-atlas','docs/knowledge-map','data/knowledge']:
        need(not (root/d).is_symlink(),'Disposable destination symlink refused','REAL_SPATIAL_MIGRATION_FORBIDDEN')
    # Reject symlinked files and aliased directories before any writer/recovery call.
    for d in ['state/knowledge-atlas','docs/knowledge-map','data/knowledge']:tree(root/d)
    return root
def safe_new(path):
    p=Path(path).resolve()
    need(not p.exists(),'Output already exists; choose a new review/seal path','SPATIAL_REVIEW_ALREADY_EXISTS')
    if p.is_relative_to(ROOT):need(p.is_relative_to(BASE),'Only isolated migration-review outputs allowed','UNSAFE_SPATIAL_REVIEW_OUTPUT')
    return p
def implementation():
    paths=[BASE/'review.py',*sorted((BASE/'runtime').rglob('*')),*[BASE.parent/n for n in ['app.js','atlas.js','labels.js','ux.js','index.html','style.css']],*[BASE.parent/'migration-preview/view'/n for n in ['app.js','index.html','style.css']],BASE.parent/'migration-preview/build.py']
    paths += [ROOT/'scripts/update-knowledge-atlas.py']
    paths += [ROOT/'scripts/knowledge_atlas'/n for n in ['spatial_authorization.py','canonical.py','transaction.py','snapshot.py','build.py','state.py','activation_persistence.py','validate.py']]
    return {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in paths if p.is_file()}
def source(root):
    data=P.load(root);h=data['history'];cp=data['checkpoint'];master=data['master']
    return dict(input_files=P.inventory(root),production_inventory=digest_files(tree(Path(root)/'docs/knowledge-map')),accepted_geometry_fingerprint=fp(data['current']),checkpoint_fingerprint=fp(cp),activation_state_fingerprint=fp(h),knowledge_fingerprint=snapshot.digest(snapshot.load_source(Path(root)/'data/knowledge')),active_history_identity=fp({'categories':h['active_categories'],'topics':h['active_topics']}),presentation_generation=cp['presentation_generation'],history_version=h['history_version'],activation_events_fingerprint=fp(h['events']),accepted_inventory=sorted(h['active_categories']+h['active_topics'])),data

def candidate(root,core,candidate_id,files,data):
    """Package-time adapter only. NEVER called by approval or apply."""
    master=data['master'];h=data['history'];target=read_bytes(files['target-geometry.json'])
    authority=dict(kind='global-canonical-pyramid',schema_version=1,geometry_schema_version=master['geometry_schema_version'],geometry_fingerprint=master['geometry_fingerprint'],geometry_sha256=P.MASTER_HASH,catalog_fingerprint=master['source_catalog_fingerprint'],layout_algorithm_version=master['layout_algorithm_version'],review_candidate_fingerprint=candidate_id,slot_contract='category:<id> -> category:<id>; reference:<id> and topic:<id> -> leaf:<id>',master_asset='generated/global-geometry.json')
    cp=dict(state_schema_version=3,layout_schema_version=master['geometry_schema_version'],layout_algorithm_version=master['layout_algorithm_version'],presentation_generation=h['layout_generation']+1,spatial_authority=authority,accepted_inventory=core['source']['accepted_inventory'],target_geometry_fingerprint=fp(target))
    history=dict(schema_version=2,history_version=h['history_version'],layout_generation=cp['presentation_generation'],active_categories=h['active_categories'],active_topics=h['active_topics'],events=h['events'],spatial_authority=authority,accepted_geometry=target,geometry_fingerprint=fp(target))
    event=dict(schema_version=1,spatial_history_version=1,events=[dict(type='SPATIAL_AUTHORITY_MIGRATION',version=1,review_candidate_fingerprint=candidate_id,from_geometry=core['source']['accepted_geometry_fingerprint'],to_geometry=master['geometry_fingerprint'],generation_before=h['layout_generation'],generation_after=cp['presentation_generation'],active_history_identity=core['source']['active_history_identity'])])
    previous=read(Path(root)/'state/knowledge-atlas/update-snapshot.json')
    # Original source index is retained, not reinterpreted as V6 allocation.
    snapshot_state=dict(state_schema_version=3,spatial_authority=authority,checkpoint_fingerprint=fp(cp),geometry_fingerprint=fp(target),source_index=previous)
    state_out={'spatial-authority.json':encoded(authority),'layout-checkpoint.json':encoded(cp),'activation-state.json':encoded(history),'spatial-migrations.json':encoded(event),'update-snapshot.json':encoded(snapshot_state),'README.md':b'Global canonical authority schema 1. Checkpoint 3 / activation 2. Hydrate exact slots; never fall back to V6 allocation. Spatial migration is not activation. Disposable adapter only.\n'}
    production={n:(BASE.parent/n).read_bytes() for n in ['atlas.js','ux.js','labels.js','style.css','app.js']}
    html=(BASE.parent/'index.html').read_text().replace('Experimental Global Pyramid','Knowledge Atlas - disposable canonical candidate').replace('EXPERIMENTAL · READ ONLY','DISPOSABLE CANONICAL AUTHORITY').replace('<script src="app.js"></script>','<script src="authority-guard.js"></script>')
    production.update({'index.html':html.encode(),'authority-guard.js':(BASE/'runtime/authority-guard.js').read_bytes(),'generated/global-geometry.json':files['global-geometry.json'],'generated/catalog.json':files['catalog.json'],'model.json':(Path(root)/'docs/knowledge-map/model.json').read_bytes(),'target-geometry.json':files['target-geometry.json'],'layout-checkpoint.json':state_out['layout-checkpoint.json'],'spatial-authority.json':state_out['spatial-authority.json']})
    production['release-manifest.json']=encoded(dict(pipeline_version=3,target='production',runtime_contract='global-canonical-disposable-1',generation=cp['presentation_generation'],assets=digest_files(production)))
    return {**{'candidate/state/'+k:v for k,v in state_out.items()},**{'candidate/production/'+k:v for k,v in production.items()}}
def read_bytes(b):return json.loads(b)

def make_package(root,preview,out,fault=None):
    root=Path(root).resolve();out=safe_new(out);fixture=root!=ROOT
    if fixture:disposable(root)
    with transaction.lock(root,write=False):
        bindings,data=source(root);data['_root']=root;preview=Path(preview);pm=read(preview/'migration-manifest.json')
        need(pm['bindings']['input_files']==bindings['input_files'],'Preview source changed')
        need(pm['bindings']['runtime_files']==P.runtime(),'Preview implementation changed')
        need(pm['manifest_fingerprint']==fp({k:v for k,v in pm.items() if k!='manifest_fingerprint'}),'Preview manifest changed')
        files={n:(preview/n).read_bytes() for n in pm['artifact_hashes']}
        need(digest_files(files)==pm['artifact_hashes'],'Preview artifacts changed')
        files['preview-manifest.json']=(preview/'migration-manifest.json').read_bytes()
        files['global-geometry.json']=(root/'prototypes/global-pyramid/generated/global-geometry.json').read_bytes()
        files['catalog.json']=(root/'prototypes/global-pyramid/generated/catalog.json').read_bytes()
        files['semantic-invariance.json']=encoded(dict(schema_version=1,before=read_bytes(files['migration-metrics.json'])['semantic_hashes_before'],after=read_bytes(files['migration-metrics.json'])['semantic_hashes_after'],counts=read_bytes(files['migration-metrics.json'])['semantic_counts'],active_history_before=bindings['active_history_identity'],active_history_after=bindings['active_history_identity'],knowledge_before=bindings['knowledge_fingerprint'],knowledge_after=bindings['knowledge_fingerprint']))
        files['transaction-plan.json']=encoded(TRANSACTION_PLAN)
        master=data['master']
        contract=dict(source=bindings,target=dict(geometry_fingerprint=master['geometry_fingerprint'],geometry_sha256=P.MASTER_HASH,geometry_schema_version=master['geometry_schema_version'],layout_algorithm_version=master['layout_algorithm_version'],catalog_fingerprint=master['source_catalog_fingerprint']),mapping=pm['target_mapping'],review_artifacts=digest_files(files),implementation=implementation(),policy=read_bytes(files['transaction-plan.json']))
        candidate_id=fp(contract);files.update(candidate(root,contract,candidate_id,files,data))
        metrics=read_bytes(files['migration-metrics.json']);files['review-summary.json']=encoded(dict(schema_version=1,status='AWAITING_EXPLICIT_HUMAN_REVIEW',source='Current accepted V6 Production',target='Canonical Global Pyramid',counts=metrics['semantic_counts'],displacement=metrics['displacement'],target_geometry_fingerprint=master['geometry_fingerprint'],review_candidate_fingerprint=candidate_id,fixture_only=fixture))
        files['view/labels.js']=(BASE.parent/'labels.js').read_bytes()
        files['view/app.js']=(BASE.parent/'migration-preview/view/app.js').read_bytes().replace(b'Generation 0 unchanged.',b'Current Generation 0; proposed Generation 1; activation history 0 unchanged.')
        files['view/style.css']=(BASE.parent/'migration-preview/view/style.css').read_bytes()+ (BASE/'runtime/review.css').read_bytes()
        html=(BASE.parent/'migration-preview/view/index.html').read_text().replace('Spatial migration — read-only preview','Exact spatial migration review').replace('Spatial migration preview','Exact spatial migration review').replace('MIGRATION_PREVIEW_READY','AWAITING HUMAN REVIEW').replace('<script src="../../labels.js">','<script src="labels.js">').replace('<script src="app.js"></script>','<script src="review.js"></script>')
        html=html.replace('<p id="summary"></p>','<p id="summary"></p><div id="review-bindings" aria-live="polite"></div>')
        files['view/index.html']=html.encode();files['view/review.js']=(BASE/'runtime/review.js').read_bytes()
        # Self-contained review: target.master_reference in original preview is unchanged.
        # Review runtime intercepts that one request and serves packaged exact master bytes.
        m=dict(schema_version=1,algorithm_version=VERSION,fixture_only=fixture,contract=contract,review_candidate_fingerprint=candidate_id,files=digest_files(files));files['manifest-core.json']=encoded(m);m['manifest_fingerprint']=fp(m);files['migration-manifest.json']=encoded(m)
        validate_material(m,files,data)
        if fault:fault('after_candidate_construction')
        need(bindings['input_files']==P.inventory(root),'Source changed during packaging')
        out.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.spatial-review-',dir=out.parent))
        try:
            for n,b in files.items():p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);transaction.durable_file(p,b)
            # mkdir is the non-overwrite claim; concurrent creator cannot be replaced.
            out.mkdir()
            for p in stage.iterdir():shutil.move(str(p),out/p.name)
            transaction.sync_dir(out);transaction.sync_dir(out.parent)
        finally:shutil.rmtree(stage,ignore_errors=True)
    return m

def inspect_package(path,token=None):
    path=Path(path);folder=path.parent;files=tree(folder);m=read_bytes(files.get('migration-manifest.json',b'{}'))
    need(token is not None,'Human-copied reviewed fingerprint required','REVIEWED_SPATIAL_FINGERPRINT_REQUIRED')
    need(token==m.get('manifest_fingerprint'),'Human review token no longer matches this candidate')
    need(set(m)==MANIFEST_FIELDS and m['schema_version']==1 and m['algorithm_version']==VERSION,'Unsupported review contract')
    need(fp({k:v for k,v in m.items() if k!='manifest_fingerprint'})==token,'Manifest fingerprint mismatch')
    need(files['migration-manifest.json']==encoded(m),'Noncanonical manifest bytes')
    need(files.get('manifest-core.json')==encoded({k:v for k,v in m.items() if k!='manifest_fingerprint'}),'Manifest preimage changed')
    need(set(files)==set(m['files'])|{'migration-manifest.json','manifest-core.json'} and digest_files({k:v for k,v in files.items() if k not in {'migration-manifest.json','manifest-core.json'}})==m['files'],'Package bytes differ from reviewed manifest')
    need(m['contract']['implementation']==implementation(),'Validation/runtime implementation changed')
    need(m['review_candidate_fingerprint']==fp(m['contract']),'Candidate contract changed')
    return m,files

def validate_material(m,files,data):
    """Independent checks only: no candidate adapter, preview constructor or layout."""
    need(set(m['contract'])=={'source','target','mapping','review_artifacts','implementation','policy'},'Unknown contract field')
    for n,h in m['contract']['review_artifacts'].items():need(n in files and sha(files[n])==h,'Changed review input '+n)
    master=read_bytes(files['global-geometry.json']);need(sha(files['global-geometry.json'])==P.MASTER_HASH,'Master changed')
    need(fp({k:v for k,v in master.items() if k!='geometry_fingerprint'})==master['geometry_fingerprint'],'Master embedded fingerprint changed')
    slots={n['key']:n for n in master['positions']};target=read_bytes(files['target-geometry.json']);current=read_bytes(files['current-geometry.json']);diff=read_bytes(files['migration-diff.json']);metrics=read_bytes(files['migration-metrics.json']);sem=read_bytes(files['semantic-snapshot.json']);h=data['history']
    need(set(target)=={'schema_version','master_fingerprint','master_sha256','master_reference','coordinate_convention','positions','context_positions','hierarchy_routes','root_sectors','world_bounds','scope_extent','leaf_groups','trays','semantic_fingerprint'} and type(target['schema_version']) is int and target['schema_version']==1,'Unknown target geometry schema')
    facts={f'{kind}:{r["id"]}':r for table,kind in [('categories','category'),('topics','topic')] for r in sem[table]}
    keys=sorted(h['active_categories']+h['active_topics']);mapping=m['contract']['mapping'];expected=[dict(key=k,slot=k if k.startswith('category:') else 'leaf:'+k.split(':')[1]) for k in keys]
    need(m['contract']['target']==dict(geometry_fingerprint=master['geometry_fingerprint'],geometry_sha256=P.MASTER_HASH,geometry_schema_version=master['geometry_schema_version'],layout_algorithm_version=master['layout_algorithm_version'],catalog_fingerprint=master['source_catalog_fingerprint']),'Target schema/version binding mismatch')
    need(m['contract']['policy']==read_bytes(files['transaction-plan.json'])==TRANSACTION_PLAN,'Transaction policy mismatch')
    need(mapping==expected and len(keys)==len(set(keys))==135 and len(h['active_categories'])==46 and len(h['active_topics'])==89,'Mapping/inventory mismatch')
    need([n['key'] for n in target['positions']]==keys and [n['key'] for n in current['positions']]==keys,'Geometry accepted inventory mismatch')
    need(current['native_geometry']==data['current'],'Accepted V6 geometry changed')
    need(all(sem[t]==data['model'][t] for t in snapshot.TABLES),'Semantic mismatch')
    need(metrics['semantic_hashes_before']==metrics['semantic_hashes_after']=={t:snapshot.digest(sem[t]) for t in snapshot.TABLES},'Semantic report mismatch')
    counts=dict(categories=len(sem['categories']),topics=len(sem['topics']),learned=len({p['topic_id'] for p in sem['progress']['topics'] if p['is_learned'] is True}),verified=len({p['topic_id'] for p in sem['progress']['topics'] if p['is_verified'] is True}),project_113=len({e['target'] for e in sem['edges'] if e['type']=='project_requires' and e['source']=='project:113'}),stage_617=len({e['target'] for e in sem['edges'] if e['type']=='project_requires' and e['source']=='project:113' and e.get('stage_id')==617}),generation=0,history_version=0)
    need(counts==metrics['semantic_counts']==dict(categories=46,topics=89,learned=31,verified=12,project_113=26,stage_617=12,generation=0,history_version=0),'Semantic counters changed')
    inv=read_bytes(files['semantic-invariance.json']);need(set(inv)=={'schema_version','before','after','counts','active_history_before','active_history_after','knowledge_before','knowledge_after'} and inv['schema_version']==1 and inv['before']==inv['after']==metrics['semantic_hashes_before'] and inv['counts']==counts and inv['active_history_before']==inv['active_history_after']==m['contract']['source']['active_history_identity'] and inv['knowledge_before']==inv['knowledge_after']==m['contract']['source']['knowledge_fingerprint'],'Semantic invariance artifact mismatch')
    aliases={r['slot']:r['semantic_aliases'] for r in master['leaf_identity_mapping']}
    for n,e in zip(target['positions'],expected):
        need(set(n)=={'key','slot','x','y','w','h','depth','parent','parents','root','path','title','type'},'Unknown target position field')
        need(n['title']==facts[n['key']]['title'] and n['type']==n['key'].split(':')[0],'Target semantic label/type mismatch')
        need(n['slot']==e['slot'] and e['slot'] in slots,'Unknown/duplicate leaf slot')
        p=slots[e['slot']];need([n[k] for k in ['x','y','w','h','depth','root']]==[p[k] for k in ['x','y','w','h','depth','root']] and n['parent']==p['primary_parent'] and n['parents']==p['parents'],'Target coordinates or ancestry changed')
        if e['key'].startswith('topic:'):need(aliases[e['slot']]==['reference:'+e['slot'][5:],'topic:'+e['slot'][5:]],'Reference/Topic alias mismatch')
    context=set()
    for n in target['positions']:
        k=n['slot'];seen=set()
        ancestry=[]
        while k:need(k not in seen and k in slots,'Invalid ancestry');seen.add(k);ancestry.append(k);context.add(k);k=slots[k]['primary_parent']
        need(n['path']==list(reversed(ancestry)),'Target ancestry path mismatch')
    need(target['hierarchy_routes']==[r for r in master['hierarchy_routes'] if r['child'] in context],'Persisted target routes changed')
    need(target['root_sectors']==master['root_sectors'] and target['world_bounds']==master['bounds'] and target['master_fingerprint']==master['geometry_fingerprint'],'Target geography changed')
    need([r['key'] for r in diff['entities']]==keys,'Diff inventory changed')
    source_nodes={n['key']:n for n in data['current']['nodes']}
    for r,c,t in zip(diff['entities'],current['positions'],target['positions']):
        native=source_nodes[r['key']];need(c['x']==native['x']-native['width']/2 and c['y']==native['y'] and c['w']==native['width'] and c['h']==native['height'],'Current rectangle mismatch')
        need([r['current_x'],r['current_y'],r['target_x'],r['target_y']]==[c['x'],c['y'],t['x'],t['y']],'Diff endpoint mismatch')
        need(r['delta_x']==t['x']-c['x'] and r['delta_y']==t['y']-c['y'] and r['displacement']==math.hypot(r['delta_x'],r['delta_y']),'Diff displacement mismatch')
        need(r['center_delta_x']==t['x']+t['w']/2-native['x'] and r['center_delta_y']==t['y']+t['h']/2-(native['y']+native['height']/2) and r['center_displacement']==math.hypot(r['center_delta_x'],r['center_delta_y']),'Center displacement mismatch')
        need([r[k] for k in ['current_width','current_height','target_width','target_height','delta_width','delta_height']]==[c['w'],c['h'],t['w'],t['h'],t['w']-c['w'],t['h']-c['h']],'Size diff mismatch')
        need(r['target_slot']==t['slot'] and r['target_global_root']==t['root'] and r['target_global_parent']==t['parent'] and r['target_depth']==t['depth'] and r['current_depth']==c['depth'] and r['current_native_x']==native['x'] and r['current_native_y']==native['y'] and r['current_path']==c['path'] and r['target_path']==t['path'],'Diff identity/context mismatch')
    for kind in ['category','topic','all']:need(metrics['displacement'][kind]==P.distribution([r['displacement'] for r in diff['entities'] if kind=='all' or r['entity_type']==kind]),'Metric mismatch')
    for kind in ['category','topic','all']:need(metrics['center_displacement'][kind]==P.distribution([r['center_displacement'] for r in diff['entities'] if kind=='all' or r['entity_type']==kind]),'Center metric mismatch')
    for section,nodes in [('current_scope_extent',current['positions']),('target_scope_extent',target['positions'])]:need(metrics[section]==P.extent(P.bounds(nodes)),'Scope bounds mismatch')
    need(metrics['target_world_bounds']==P.extent(master['bounds']) and target['scope_extent']==metrics['target_scope_extent'],'Global/scope bounds mismatch')
    groups=defaultdict(list)
    for n in target['positions']:
        if n['type']=='topic':groups[n['parent']].append(n['slot'])
    need(target['leaf_groups']==[dict(parent=k,slots=v) for k,v in sorted(groups.items())],'Leaf group mismatch')
    need(metrics['size_changes']==sum(r['delta_width']!=0 or r['delta_height']!=0 for r in diff['entities']) and metrics['primary_parent_changes']==[r['key'] for r,c,t in zip(diff['entities'],current['positions'],target['positions']) if c['parent']!=t['parent']],'Presentation change metric mismatch')
    summary=read_bytes(files['review-summary.json']);need(summary==dict(schema_version=1,status='AWAITING_EXPLICIT_HUMAN_REVIEW',source='Current accepted V6 Production',target='Canonical Global Pyramid',counts=counts,displacement=metrics['displacement'],target_geometry_fingerprint=master['geometry_fingerprint'],review_candidate_fingerprint=m['review_candidate_fingerprint'],fixture_only=m['fixture_only']),'Misleading review summary')
    candidate_state={k.removeprefix('candidate/state/'):v for k,v in files.items() if k.startswith('candidate/state/')};production={k.removeprefix('candidate/production/'):v for k,v in files.items() if k.startswith('candidate/production/')}
    validate_candidate(candidate_state,production,files,m)
    need(read_bytes(candidate_state['activation-state.json'])['active_categories']==h['active_categories'] and read_bytes(candidate_state['activation-state.json'])['active_topics']==h['active_topics'] and read_bytes(candidate_state['activation-state.json'])['events']==h['events'],'Activation history changed')
    need(production['model.json']==encoded(data['model']),'Production semantics/serialization changed')
    need(production['generated/catalog.json']==files['catalog.json'],'Catalog projection changed')
    need(read_bytes(candidate_state['update-snapshot.json'])['source_index']==read(Path(data['_root'])/'state/knowledge-atlas/update-snapshot.json'),'Source snapshot changed')
    need(files['catalog.json']==(Path(data['_root'])/'prototypes/global-pyramid/generated/catalog.json').read_bytes(),'Catalog bytes changed')

def validate_candidate(state_out,production,files,m):
    need(set(state_out)=={'spatial-authority.json','layout-checkpoint.json','activation-state.json','spatial-migrations.json','update-snapshot.json','README.md'},'Unknown candidate State files')
    authority=read_bytes(state_out['spatial-authority.json']);cp=read_bytes(state_out['layout-checkpoint.json']);h=read_bytes(state_out['activation-state.json']);events=read_bytes(state_out['spatial-migrations.json']);previous=read_bytes(state_out['update-snapshot.json']);target=read_bytes(files['target-geometry.json']);master=read_bytes(files['global-geometry.json']);source=m['contract']['source']
    for v,fields in [(authority,['schema_version','geometry_schema_version']),(cp,['state_schema_version','layout_schema_version','presentation_generation']),(h,['schema_version','history_version','layout_generation']),(events,['schema_version','spatial_history_version'])]:need(all(type(v[k]) is int for k in fields),'Non-integer schema/counter')
    need(set(authority)==AUTHORITY_FIELDS and authority['schema_version']==1 and authority['kind']=='global-canonical-pyramid','Unknown authority schema')
    need(authority['master_asset']=='generated/global-geometry.json','Unknown master asset reference')
    need(authority['review_candidate_fingerprint']==m['review_candidate_fingerprint'] and authority['geometry_fingerprint']==master['geometry_fingerprint'] and authority['geometry_sha256']==sha(files['global-geometry.json']) and authority['catalog_fingerprint']==master['source_catalog_fingerprint'] and authority['geometry_schema_version']==master['geometry_schema_version'] and authority['layout_algorithm_version']==master['layout_algorithm_version'] and authority['slot_contract']=='category:<id> -> category:<id>; reference:<id> and topic:<id> -> leaf:<id>','Authority binding mismatch')
    need(set(cp)==CP_FIELDS and cp['state_schema_version']==3 and cp['spatial_authority']==authority and cp['presentation_generation']==source['presentation_generation']+1 and cp['target_geometry_fingerprint']==fp(target) and cp['accepted_inventory']==source['accepted_inventory'] and cp['layout_algorithm_version']==master['layout_algorithm_version'] and cp['layout_schema_version']==master['geometry_schema_version'],'Unknown/conflicting checkpoint')
    need(set(h)==HISTORY_FIELDS and h['schema_version']==2 and h['history_version']==source['history_version'] and h['layout_generation']==cp['presentation_generation'] and h['accepted_geometry']==target and h['geometry_fingerprint']==fp(target) and h['spatial_authority']==authority,'Unknown/conflicting history')
    need(sorted(h['active_categories']+h['active_topics'])==source['accepted_inventory'] and fp({'categories':h['active_categories'],'topics':h['active_topics']})==source['active_history_identity'] and fp(h['events'])==source['activation_events_fingerprint'],'ACTIVE_HISTORY changed')
    expected_event=dict(type='SPATIAL_AUTHORITY_MIGRATION',version=1,review_candidate_fingerprint=m['review_candidate_fingerprint'],from_geometry=source['accepted_geometry_fingerprint'],to_geometry=master['geometry_fingerprint'],generation_before=source['presentation_generation'],generation_after=cp['presentation_generation'],active_history_identity=source['active_history_identity'])
    need(set(events)==EVENT_FIELDS and events['schema_version']==1 and events['spatial_history_version']==1 and events['events']==[expected_event],'Unknown/duplicate spatial event')
    need(set(previous)=={'state_schema_version','spatial_authority','checkpoint_fingerprint','geometry_fingerprint','source_index'} and previous['state_schema_version']==3 and previous['spatial_authority']==authority and previous['checkpoint_fingerprint']==fp(cp) and previous['geometry_fingerprint']==fp(target),'Unknown snapshot schema')
    need(production['target-geometry.json']==files['target-geometry.json'] and production['generated/global-geometry.json']==files['global-geometry.json'] and production['spatial-authority.json']==state_out['spatial-authority.json'] and production['layout-checkpoint.json']==state_out['layout-checkpoint.json'],'State/Production disagree')
    expected_assets={'atlas.js','ux.js','labels.js','style.css','app.js','index.html','authority-guard.js','generated/global-geometry.json','generated/catalog.json','model.json','target-geometry.json','layout-checkpoint.json','spatial-authority.json','release-manifest.json'}
    need(set(production)==expected_assets,'Unknown Production files')
    for n in ['atlas.js','ux.js','labels.js','style.css','app.js']:need(production[n]==(BASE.parent/n).read_bytes(),'Candidate runtime changed: '+n)
    need(production['authority-guard.js']==(BASE/'runtime/authority-guard.js').read_bytes(),'Candidate authority guard changed')
    release=read_bytes(production['release-manifest.json']);need(set(release)=={'pipeline_version','target','runtime_contract','generation','assets'} and release['target']=='production' and release['pipeline_version']==3 and release['runtime_contract']=='global-canonical-disposable-1' and release['generation']==cp['presentation_generation'] and release['assets']==digest_files({k:v for k,v in production.items() if k!='release-manifest.json'}),'Invalid Production release')

def validate_source(root,m):
    need(not (Path(root)/'state/.knowledge-atlas-transaction.json').exists(),'Pending transaction requires explicit test recovery','SPATIAL_RECOVERY_REQUIRED')
    need(not m['fixture_only'] or Path(root).resolve()!=ROOT,'Fixture package cannot authorize real repository','FIXTURE_SPATIAL_MIGRATION_FORBIDDEN')
    if m['fixture_only']:disposable(root)
    need(P.inventory(root)==m['contract']['source']['input_files'],'Source inventory changed since review')
    bindings,data=source(root);need(bindings==m['contract']['source'],'Source checkpoint/history/Knowledge changed');return data

def approve(root,path,token,seal_path=None,fault=None):
    root=Path(root).resolve()
    # Fixture domain rejection precedes locking or any real-source inspection.
    need(not (root==ROOT and read(path).get('fixture_only')), 'Fixture package cannot authorize real repository','FIXTURE_SPATIAL_MIGRATION_FORBIDDEN')
    need(root!=ROOT,'Real approval requires explicit confirmed apply mode','REAL_SPATIAL_MIGRATION_FORBIDDEN')
    with transaction.lock(root,write=False):
        m,files=inspect_package(path,token);data=validate_source(root,m);data['_root']=root;validate_material(m,files,data)
        if fault:fault('after_approval_validation')
        need(P.inventory(root)==m['contract']['source']['input_files'],'Concurrent source change')
        seal=dict(schema_version=1,status='APPROVED_FOR_APPLY',fixture_only=m['fixture_only'],reviewed_fingerprint=token,manifest_sha256=sha(files['migration-manifest.json']),package_inventory_fingerprint=fp(m['files']),implementation_fingerprint=fp(implementation()),publication_policy=authorization.SEAL_POLICY);seal['approval_fingerprint']=fp(seal)
        if seal_path:
            out=safe_new(seal_path);out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as f:f.write(encoded(seal));f.flush();os.fsync(f.fileno())
            transaction.sync_dir(out.parent)
        return seal

def check_seal(seal,m,files):
    need(set(seal)=={'schema_version','status','fixture_only','reviewed_fingerprint','manifest_sha256','package_inventory_fingerprint','implementation_fingerprint','publication_policy','approval_fingerprint'} and seal['schema_version']==1 and seal['status']=='APPROVED_FOR_APPLY' and seal['publication_policy']==authorization.SEAL_POLICY,'Unsupported seal')
    need(fp({k:v for k,v in seal.items() if k!='approval_fingerprint'})==seal['approval_fingerprint'] and seal['reviewed_fingerprint']==m['manifest_fingerprint'] and seal['fixture_only']==m['fixture_only'] and seal['manifest_sha256']==sha(files['migration-manifest.json']) and seal['package_inventory_fingerprint']==fp(m['files']) and seal['implementation_fingerprint']==fp(implementation()),'Approval seal no longer binds exact candidate')

def validate_installed(root,path,token,*,in_transaction=False):
    if not in_transaction:need(not (Path(root)/'state/.knowledge-atlas-transaction.json').exists(),'Pending transaction cannot be accepted','SPATIAL_RECOVERY_REQUIRED')
    m,files=inspect_package(path,token);state_out=tree(Path(root)/'state/knowledge-atlas');production=tree(Path(root)/'docs/knowledge-map')
    need(state_out.get('spatial-migration-review.json')==files['migration-manifest.json'],'Persisted human review receipt differs')
    validate_candidate({k:v for k,v in state_out.items() if k!='spatial-migration-review.json'},production,files,m)
    expected_state={k.removeprefix('candidate/state/'):v for k,v in files.items() if k.startswith('candidate/state/')};expected_production={k.removeprefix('candidate/production/'):v for k,v in files.items() if k.startswith('candidate/production/')}
    expected_state['spatial-migration-review.json']=files['migration-manifest.json']
    need(state_out==expected_state and production==expected_production,'Installed bytes differ from exact reviewed candidate')
    # All relevant non-published inputs must still match even on replay.
    current=P.inventory(root)
    nonspatial=lambda inv:{k:v for k,v in inv.items() if not k.startswith(('docs/knowledge-map/','state/knowledge-atlas/'))}
    need(nonspatial(current)==nonspatial(m['contract']['source']['input_files']),'Replay nonspatial source changed')
    build.verify_release(Path(root)/'docs/knowledge-map')
    return dict(status='PASS',generation=1,history_version=0,spatial_events=1,accepted_positions=135,exact_target=True)

def real_gate(root,path,token,confirmation):
    need(confirmation is True,'Explicit real migration confirmation required','REAL_SPATIAL_MIGRATION_FORBIDDEN')
    need(Path(path).is_absolute() and not Path(path).is_symlink(),'Absolute reviewed manifest path required','REAL_SPATIAL_MIGRATION_FORBIDDEN')
    need(bool(token),'Human-reviewed fingerprint required','REVIEWED_SPATIAL_FINGERPRINT_REQUIRED')
    authorization.real_repository(root,ROOT)
    need(not (Path(root)/'state/.knowledge-atlas-transaction.json').exists(),'Pending transaction requires recovery','SPATIAL_RECOVERY_REQUIRED')
    need(read(path).get('fixture_only') is False,'Fixture package cannot authorize real apply','FIXTURE_SPATIAL_MIGRATION_FORBIDDEN')
    for name in ('state/knowledge-atlas','docs/knowledge-map','data/knowledge'):tree(Path(root)/name)


def apply_real(root,path,token,confirmation=False,fault=None):
    """Only this explicit operator mode may authorize real publication."""
    real_gate(root,path,token,confirmation)
    return _apply_exact(Path(root),path,None,fault,real_token=token,confirmation=confirmation)


def apply_test(root,path,seal,fault=None):
    return _apply_exact(disposable(root),path,seal,fault)


def _apply_exact(root,path,seal,fault=None,*,real_token=None,confirmation=False):
    # Both authorization domains use this same established transaction writer.
    real = real_token is not None
    with transaction.lock(root,write=True):
        if real:real_gate(root,path,real_token,confirmation)
        need(not (root/'state/.knowledge-atlas-transaction.json').exists(),'Recovery required','SPATIAL_RECOVERY_REQUIRED')
        m,files=inspect_package(path,real_token if real else seal.get('reviewed_fingerprint'))
        if real:
            seal=dict(schema_version=1,status='APPROVED_FOR_APPLY',fixture_only=m['fixture_only'],reviewed_fingerprint=real_token,manifest_sha256=sha(files['migration-manifest.json']),package_inventory_fingerprint=fp(m['files']),implementation_fingerprint=fp(implementation()),publication_policy=authorization.SEAL_POLICY)
            seal['approval_fingerprint']=fp(seal)
        check_seal(seal,m,files)
        if (root/'state/knowledge-atlas/spatial-authority.json').exists():validate_installed(root,path,m['manifest_fingerprint']);return dict(status='ALREADY_APPLIED',applied=False,generation=1)
        data=validate_source(root,m);data['_root']=root;validate_material(m,files,data)
        if fault:fault('after_approval_validation')
        state_out={k.removeprefix('candidate/state/'):v for k,v in files.items() if k.startswith('candidate/state/')};production={k.removeprefix('candidate/production/'):v for k,v in files.items() if k.startswith('candidate/production/')}
        # Copy the reviewed manifest itself as the detached receipt; no self-hash
        # cycle and no regeneration/stamping of approved target or State bytes.
        state_out['spatial-migration-review.json']=files['migration-manifest.json']
        if fault:fault('before_state_staging')
        stages=0
        def hooks(name):
            nonlocal stages
            if name=='after_candidate_write':
                stages+=1
                if fault:fault('after_state_staging' if stages==1 else 'after_production_staging')
            elif name=='after_publish_0':
                if fault:fault('after_state_swap');fault('before_production_swap')
            elif name=='after_publish_1':
                if fault:fault('after_production_swap')
            elif name=='before_journal_completion':
                if fault:fault('before_durable_commit')
            elif fault:fault(name)
        def preflight():
            if real:real_gate(root,path,real_token,confirmation)
            mm,ff=inspect_package(path,seal['reviewed_fingerprint']);check_seal(seal,mm,ff);validate_source(root,mm)
        def verify():validate_installed(root,path,m['manifest_fingerprint'],in_transaction=True)
        transaction.publish(root,[(root/'state/knowledge-atlas',state_out),(root/'docs/knowledge-map',production)],fault=hooks,preflight=preflight,verify=verify)
        return dict(status='APPLIED_SPATIAL_MIGRATION' if real else 'APPLIED_DISPOSABLE_ONLY',applied=True,generation=1,manifest_fingerprint=m['manifest_fingerprint'])

def recover_test(root):
    root=disposable(root)
    with transaction.lock(root,write=True):
        transaction.recover(root/'state/.knowledge-atlas-transaction.json',root)
        # A crash before the journal can leave only unexchanged stages. No visible
        # state changed. These roots are exclusively marked test sandboxes.
        for parent in [root/'state',root/'docs']:
            for stage in parent.glob('.atlas-candidate-*'):
                need(not stage.is_symlink(),'Unsafe orphan stage','SPATIAL_RECOVERY_REQUIRED');shutil.rmtree(stage)
        for temp in (root/'state').glob('.knowledge-atlas-transaction.tmp'):temp.unlink()
    return dict(status='RECOVERED_DISPOSABLE_ONLY')

def reserved_projection(master,authority,identities):
    """Read-only future visibility adapter: lookups, no Knowledge or history write."""
    need(set(authority)==AUTHORITY_FIELDS and authority['schema_version']==1 and authority['kind']=='global-canonical-pyramid' and authority['geometry_fingerprint']==master['geometry_fingerprint'],'Invalid spatial authority')
    slots={p['key']:p for p in master['positions']};out={};used_slots=set()
    for key in identities:
        parts=key.split(':');need(len(parts)==2 and parts[0] in {'category','topic','reference'} and parts[1].isdigit(),'Unknown semantic identity')
        slot=key if parts[0]=='category' else 'leaf:'+parts[1];need(slot in slots,'No globally reserved slot')
        need(slot not in used_slots,'Duplicate semantic aliases for one physical slot');used_slots.add(slot)
        out[key]=dict(slot=slot,geometry=deepcopy(slots[slot]))
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('package');p.add_argument('--output',type=Path,required=True);p.add_argument('--preview',type=Path,default=BASE.parent/'migration-preview');p.add_argument('--root',type=Path,default=ROOT)
    p=sub.add_parser('approve');p.add_argument('--manifest',type=Path,required=True);p.add_argument('--reviewed-fingerprint');p.add_argument('--seal',type=Path,required=True);p.add_argument('--root',type=Path,default=ROOT)
    p=sub.add_parser('apply-test');p.add_argument('--manifest',type=Path,required=True);p.add_argument('--seal',type=Path,required=True);p.add_argument('--root',type=Path,required=True)
    p=sub.add_parser('recover-test');p.add_argument('--root',type=Path,required=True)
    p=sub.add_parser('validate-test');p.add_argument('--manifest',type=Path,required=True);p.add_argument('--reviewed-fingerprint',required=True);p.add_argument('--root',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.command=='package':r=make_package(args.root,args.preview,args.output);result=dict(status='SPATIAL_REVIEW_PACKAGE_READY',manifest_fingerprint=r['manifest_fingerprint'],applied=False)
        elif args.command=='approve':result=approve(args.root,args.manifest,args.reviewed_fingerprint,args.seal)
        elif args.command=='apply-test':disposable(args.root);result=apply_test(args.root,args.manifest,read(args.seal))
        elif args.command=='recover-test':result=recover_test(args.root)
        else:disposable(args.root);result=validate_installed(args.root,args.manifest,args.reviewed_fingerprint)
        print(json.dumps(result,sort_keys=True))
    except (ValueError,KeyError,TypeError,OSError,P.Gate) as e:
        print(json.dumps(dict(status=getattr(e,'status',STALE),reason=getattr(e,'reason',str(e)),applied=False),sort_keys=True));sys.exit(1)
