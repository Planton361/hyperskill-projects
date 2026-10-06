"""Canonical dispatch for the existing activation review/publication workflow."""
from copy import deepcopy
import json
from pathlib import Path
from . import canonical as C, snapshot, transaction, build, validate, layout_update
from .activation import ActivationPlanner
from .activation_persistence import projection, context_args

VERSION=2
FIELDS={'schema_version','bindings','context','outcome','selected_variant','new_categories','new_topics','blocked_references','expected_generation_change','expected_history_change','fixture_only','files','manifest_fingerprint'}

def runtime_fingerprint(root):
    # Bind all validators/dispatch/runtime bytes, excluding caches and test output.
    here=Path(root)/'scripts/knowledge_atlas'
    paths=[p for p in here.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'fixtures' not in p.parts and p.suffix in ('.py','.js','.cjs','.json','.css','.html')]
    paths.append(here.parent/'update-knowledge-atlas.py')
    return C.fp({p.relative_to(here.parent).as_posix():C.sha(p.read_bytes()) for p in sorted(paths)})

def plan(catalog,cp,h,geom,context=None):
    p=ActivationPlanner(catalog,cp,geom).plan(**(context or {}))
    for row in p['entities']:
        if row['id'] in cp['accepted_inventory']:continue
        fact=(catalog.categories if row['id'].startswith('category:') else catalog.topics).get(row['id'])
        metadata=(fact or {}).get('accepted_metadata')
        missing=['accepted_normalized_metadata'] if not metadata else []
        if metadata:
            if not metadata.get('evidence_ids') or any(not any(ev['id']==e and ev['confidence']=='explicit' for ev in catalog.active['evidence']) for e in metadata.get('evidence_ids',[])):missing.append('explicit_evidence')
            if row['entity_type']=='topic':
                if type(metadata.get('theory_step_id')) is not int or metadata['theory_step_id']<=0:missing.append('theory_step_id')
                if not isinstance(metadata.get('url'),str) or not metadata['url'].startswith(('https://','http://')):missing.append('url')
        if missing:
            row['missing_metadata']=sorted(set(row['missing_metadata']+missing))
            row['renderability']='BLOCKED_ON_METADATA';row['presentation_activation']='BLOCKED_ON_METADATA'
    p['blocked_references']=[row for row in p['entities'] if row['presentation_activation']=='BLOCKED_ON_METADATA']
    p['new_categories']=[row['id'] for row in p['entities'] if row['presentation_activation']=='ACTIVATION_CANDIDATE' and row['entity_type']=='category']
    p['new_topics']=[row['id'] for row in p['entities'] if row['presentation_activation']=='ACTIVATION_CANDIDATE' and row['entity_type']=='topic']
    outcome='METADATA_REQUIRED' if p['blocked_references'] else 'ACTIVATION_REVIEW_REQUIRED' if p['new_categories'] or p['new_topics'] else 'NO_CHANGE'
    p.update(recommended_outcome=outcome,pipeline_outcome={'METADATA_REQUIRED':None,'ACTIVATION_REVIEW_REQUIRED':'REVIEW_REQUIRED','NO_CHANGE':'SAFE_TO_APPLY'}[outcome],conditions=[outcome],geometry_required=False,future_displacement=0)
    return p

def binding(root,loaded,cp,h,p):
    return dict(knowledge=snapshot.digest(loaded),evidence=snapshot.digest({k:loaded[k] for k in ('courses','projects','stages','edges','evidence')}),personal=snapshot.digest(loaded['progress']),
        active_history=C.fp(h),checkpoint=C.fp(cp),authority=C.fp(cp['spatial_authority']),master=cp['spatial_authority']['geometry_sha256'],plan=C.fp(p),
        state=transaction.inventory(root/'state/knowledge-atlas'),production=transaction.inventory(root/'docs/knowledge-map'),implementation=runtime_fingerprint(root))

def package_preview(root,destination,variant='current',context=None):
    root=Path(root).resolve();destination=Path(destination).resolve()
    if variant!='current':raise ValueError('SPATIAL_AUTHORITY_MIGRATION_REQUIRED: canonical authority has one target, no placement variants')
    if destination.is_relative_to(root) and not destination.is_relative_to(root/'prototypes/activation-previews'):raise ValueError('Preview destination must be external or below prototypes/activation-previews')
    if destination.exists():raise ValueError('PREVIEW_ALREADY_EXISTS: never overwrite reviewed artifacts')
    with transaction.lock(root):
        cp,previous,h,frozen,g=C.restore(root/'state/knowledge-atlas');loaded=snapshot.load_source(root/'data/knowledge');catalog=C.validate_structure(loaded,g,previous);p=plan(catalog,cp,h,frozen,context)
        keys=set(cp['accepted_inventory']+p['new_categories']+p['new_topics']);candidate=frozen if p['blocked_references'] else C.reveal_geometry(g,frozen,keys,catalog)
        slots=[dict(key=n['key'],slot=n['slot'],x=n['x'],y=n['y'],w=n['w'],h=n['h'],parent=n['parent'],root=n['root']) for n in candidate['positions'] if n['key'] not in cp['accepted_inventory']]
        metrics=dict(schema_version=1,outcome=p['recommended_outcome'],authority_fingerprint=cp['spatial_authority']['geometry_fingerprint'],existing_node_displacement=0,placement_search=False,search_evaluations=0,canonical_reveals=slots,generation=cp['presentation_generation'],expected_generation_change=0,expected_history_change=int(bool(slots)),metadata_state='METADATA_REQUIRED' if p['blocked_references'] else 'SUFFICIENT')
        new_cp=deepcopy(cp);new_cp.update(accepted_inventory=sorted(keys) if not p['blocked_references'] else cp['accepted_inventory'],target_geometry_fingerprint=C.fp(candidate))
        files={'activation-plan.json':snapshot.encode(p),'candidate-geometry.json':snapshot.encode(candidate),'candidate-checkpoint.json':snapshot.encode(new_cp),'metrics.json':snapshot.encode(metrics)}
        if not p['blocked_references']:
            data=projection(loaded,keys);validate.validate(data,canonical=True);previous=C.complete(data,new_cp,candidate)
            production=build.production_outputs(build.artifacts(root/'prototypes/knowledge-atlas-v6',data,new_cp,candidate,previous),root/'docs/knowledge-atlas-preview')
            layout_update.bridge(root/'prototypes/knowledge-atlas-v6',action='canonical-runtime-test',assets={n:b.decode() for n,b in production.items()})
            files.update({'view/'+n:b for n,b in production.items()})
        files['review.html']=b'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Exact canonical reveal review</title><style>body{font:16px system-ui;background:#0c1623;color:#e1ebf7;margin:20px}textarea{width:95%;color:inherit;background:#16283b}iframe{width:100%;height:75vh;border:1px solid #7295b8}button{padding:8px}</style><h1>Exact canonical reveal review</h1><p>Not applied. Review newly visible entities at reserved global slots.</p><pre id="summary"></pre><label>Manifest fingerprint<textarea id="token" readonly rows="2"></textarea></label><button id="copy">Copy fingerprint</button><p><a href="candidate-geometry.json">Exact coordinates/routes</a> &#183; <a href="activation-plan.json">Explicit relevance evidence</a> &#183; <a href="metrics.json">Canonical reveal metrics</a></p><iframe src="view/" title="Exact candidate Atlas"></iframe><script src="review.js"></script></html>'
        files['review.js']=b"(async()=>{const m=await(await fetch('activation-manifest.json')).json(),v=await(await fetch('metrics.json')).json();document.querySelector('#token').value=m.manifest_fingerprint;document.querySelector('#summary').textContent=JSON.stringify({outcome:m.outcome,new_categories:m.new_categories,new_topics:m.new_topics,authority:v.authority_fingerprint,existing_displacement:v.existing_node_displacement,generation_change:m.expected_generation_change,history_change:m.expected_history_change,metadata:v.metadata_state},null,2);document.querySelector('#copy').onclick=async()=>{const t=document.querySelector('#token');t.focus();t.select();try{await navigator.clipboard.writeText(t.value)}catch{}};})();"
        b=binding(root,loaded,cp,h,p)
        m=dict(schema_version=VERSION,bindings=b,context=p['context'],outcome=p['recommended_outcome'],selected_variant='CANONICAL_REVEAL',new_categories=p['new_categories'],new_topics=p['new_topics'],blocked_references=p['blocked_references'],expected_generation_change=0,expected_history_change=metrics['expected_history_change'],fixture_only=False,files={n:C.sha(v) for n,v in sorted(files.items())});m['manifest_fingerprint']=C.fp(m)
        if binding(root,snapshot.load_source(root/'data/knowledge'),cp,h,p)!=b:raise ValueError('STALE_ACTIVATION_PREVIEW: inputs changed during preview')
        files['activation-manifest.json']=snapshot.encode(m);destination.mkdir(parents=True)
        for n,v in files.items():path=destination/n;path.parent.mkdir(parents=True,exist_ok=True);transaction.durable_file(path,v)
        transaction.sync_dir(destination)
        return m

def inspect(path,token):
    path=Path(path);m=C.read(path)
    if not token:raise ValueError('REVIEW_FINGERPRINT_REQUIRED')
    if token!=m.get('manifest_fingerprint') or set(m)!=FIELDS or m['schema_version']!=VERSION or C.fp({k:v for k,v in m.items() if k!='manifest_fingerprint'})!=token:raise ValueError('STALE_ACTIVATION_PREVIEW: exact reviewed identity changed')
    names={p.relative_to(path.parent).as_posix() for p in path.parent.rglob('*') if p.is_file()}
    if names!=set(m['files'])|{'activation-manifest.json'}:raise ValueError('STALE_ACTIVATION_PREVIEW: package inventory changed')
    files={n:(path.parent/n).read_bytes() for n in m['files']}
    if any(C.sha(files[n])!=sha for n,sha in m['files'].items()):raise ValueError('STALE_ACTIVATION_PREVIEW: reviewed bytes changed')
    return m,files

def approve(root,path,*,reviewed_fingerprint=None,fault=None):
    root=Path(root).resolve();path=Path(path)
    C.writer_guard(root)
    with transaction.lock(root,write=True):
        m,files=inspect(path,reviewed_fingerprint)
        if fault:fault('before_authority_validation')
        cp,previous,h,frozen,g=C.restore(root/'state/knowledge-atlas');loaded=snapshot.load_source(root/'data/knowledge');catalog=C.validate_structure(loaded,g,previous)
        p=json.loads(files['activation-plan.json']);candidate=json.loads(files['candidate-geometry.json']);new_cp=json.loads(files['candidate-checkpoint.json']);metrics=json.loads(files['metrics.json'])
        fresh=plan(catalog,cp,h,frozen,context_args(m['context']))
        applied=any(e['manifest_fingerprint']==m['manifest_fingerprint'] for e in h['events'])
        if applied:
            for key in ('knowledge','evidence','personal','authority','master','implementation'):
                if binding(root,loaded,cp,h,p)[key]!=m['bindings'][key]:raise ValueError('STALE_ACTIVATION_PREVIEW: replay inputs changed')
            if frozen!=candidate:raise ValueError('STALE_ACTIVATION_PREVIEW: replay geometry differs')
            build.verify_release(root/'docs/knowledge-map',{n[5:]:b for n,b in files.items() if n.startswith('view/')})
            return dict(status='SAFE_TO_APPLY',outcome='NO_CHANGE',applied=False,generation=cp['presentation_generation'],history_version=h['history_version'])
        if fresh!=p or binding(root,loaded,cp,h,p)!=m['bindings']:raise ValueError('STALE_ACTIVATION_PREVIEW: source/authority/runtime changed')
        if p['blocked_references']:raise ValueError('METADATA_REQUIRED: valid normalized evidence is required before reveal')
        expected_keys=set(cp['accepted_inventory']+p['new_categories']+p['new_topics'])
        C.validate_geometry(g,candidate,expected_keys)
        existing={n['key']:n for n in candidate['positions']}
        if any(existing.get(n['key'])!=n for n in frozen['positions']):raise ValueError('STALE_ACTIVATION_PREVIEW: accepted geometry changed')
        expected_cp={**cp,'accepted_inventory':sorted(expected_keys),'target_geometry_fingerprint':C.fp(candidate)}
        if new_cp!=expected_cp or m['expected_generation_change']!=0 or m['expected_history_change']!=int(expected_keys!=set(cp['accepted_inventory'])) or metrics['existing_node_displacement']!=0 or metrics['placement_search'] is not False:raise ValueError('STALE_ACTIVATION_PREVIEW: counters/geometry contract changed')
        if any(m[k]!=p[k] for k in ('new_categories','new_topics','blocked_references')) or m['outcome']!=p['recommended_outcome'] or m['selected_variant']!='CANONICAL_REVEAL':raise ValueError('STALE_ACTIVATION_PREVIEW: misleading summary')
        if expected_keys==set(cp['accepted_inventory']):return dict(status='SAFE_TO_APPLY',outcome='NO_CHANGE',applied=False,generation=cp['presentation_generation'],history_version=h['history_version'])
        data=projection(loaded,expected_keys);validate.validate(data,canonical=True)
        production={n[5:]:b for n,b in files.items() if n.startswith('view/')}
        if not production or production['target-geometry.json']!=files['candidate-geometry.json'] or production['layout-checkpoint.json']!=files['candidate-checkpoint.json']:raise ValueError('STALE_ACTIVATION_PREVIEW: release disagrees with reviewed candidate')
        release=json.loads(production['release-manifest.json']);require_assets={n:C.sha(b) for n,b in production.items() if n!='release-manifest.json'}
        if release['assets']!=require_assets:raise ValueError('STALE_ACTIVATION_PREVIEW: release inventory')
        expected_metrics=dict(schema_version=1,outcome=p['recommended_outcome'],authority_fingerprint=cp['spatial_authority']['geometry_fingerprint'],existing_node_displacement=0,placement_search=False,search_evaluations=0,canonical_reveals=[{k:n[k] for k in ('key','slot','x','y','w','h','parent','root')} for n in candidate['positions'] if n['key'] not in cp['accepted_inventory']],generation=cp['presentation_generation'],expected_generation_change=0,expected_history_change=1,metadata_state='SUFFICIENT')
        if metrics!=expected_metrics:raise ValueError('STALE_ACTIVATION_PREVIEW: misleading reveal metrics')
        from . import catalog_projection
        runtime=root/'scripts/knowledge_atlas/canonical_runtime'
        for asset in runtime.rglob('*'):
            if asset.is_file() and production.get(asset.relative_to(runtime).as_posix())!=asset.read_bytes():raise ValueError('STALE_ACTIVATION_PREVIEW: unvalidated runtime bytes')
        new_history={'active_categories':sorted(k for k in expected_keys if k.startswith('category:')),'active_topics':sorted(k for k in expected_keys if k.startswith('topic:'))}
        if production['generated/global-geometry.json']!=(root/'docs/knowledge-map/generated/global-geometry.json').read_bytes() or json.loads(production['generated/catalog.json'])!=catalog_projection.project(loaded,new_history) or json.loads(production['spatial-authority.json'])!=cp['spatial_authority']:raise ValueError('STALE_ACTIVATION_PREVIEW: authority/semantic projection changed')
        if release.get('runtime_contract')!='global-canonical-1' or release.get('target')!='production' or release.get('generation')!=cp['presentation_generation']:raise ValueError('STALE_ACTIVATION_PREVIEW: release contract')
        if any(json.loads(production['model.json'])[t]!=data[t] for t in snapshot.TABLES):raise ValueError('STALE_ACTIVATION_PREVIEW: semantic publication changed')
        # State wrappers are derived from reviewed identities/counters. Coordinates,
        # checkpoint and Production bytes are consumed verbatim, never regenerated.
        new_h=deepcopy(h);new_h.update(history_version=h['history_version']+1,active_categories=sorted(k for k in expected_keys if k.startswith('category:')),active_topics=sorted(k for k in expected_keys if k.startswith('topic:')),accepted_geometry=candidate,geometry_fingerprint=C.fp(candidate))
        new_h['events'].append(dict(manifest_fingerprint=m['manifest_fingerprint'],plan_fingerprint=C.fp(p),candidate_fingerprint=C.fp(candidate),variant='canonical-reveal',generation=cp['presentation_generation']))
        new_previous=C.complete(data,new_cp,candidate);state_path=root/'state/knowledge-atlas';state_out=C.outputs(state_path,new_cp,new_previous,new_h)
        state_out['activation-reviews/'+m['manifest_fingerprint']+'.json']=path.read_bytes()
        if fault:fault('after_candidate_creation')
        def preflight():
            inspect(path,reviewed_fingerprint)
            if binding(root,snapshot.load_source(root/'data/knowledge'),cp,h,p)!=m['bindings']:raise ValueError('STALE_ACTIVATION_PREVIEW: concurrent inputs changed')
            C.master(root,cp['spatial_authority'])
        def verify():
            C.restore_after_swap(state_path);build.verify_release(root/'docs/knowledge-map',production)
            if transaction.inventory(state_path)!=files_inventory(state_out):raise ValueError('CANONICAL_PUBLISH_MISMATCH')
        stages=[0]
        def inject(boundary):
            names={'before_final_rename':'before_swaps','after_publish_0':'after_state_swap','after_publish_1':'after_production_swap','before_journal_completion':'before_commit_record'}
            if boundary=='after_candidate_write':name='after_state_staging' if stages[0]==0 else 'after_production_staging';stages[0]+=1
            else:name=names.get(boundary,boundary)
            if fault:fault(name)
        if fault:fault('before_state_staging')
        transaction.publish(root,[(state_path,state_out),(root/'docs/knowledge-map',production)],fault=inject,preflight=preflight,journal=root/'state/.knowledge-atlas-transaction.json',verify=verify)
        return dict(status='SAFE_TO_APPLY',outcome='APPROVED_ACTIVATION',applied=True,generation=cp['presentation_generation'],history_version=new_h['history_version'],existing_node_displacement=0,placement_search=False)

def files_inventory(files):
    import hashlib
    h=hashlib.sha256()
    for n,b in sorted(files.items()):h.update(n.encode());h.update(b'\0');h.update(b)
    return h.hexdigest()
