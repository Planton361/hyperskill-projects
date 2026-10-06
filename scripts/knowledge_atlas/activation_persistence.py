"""Exact reviewed artifacts, append-only presentation history and joint publication.

No approval cache or ambient --approve flag. Production never runs the allocator.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from . import snapshot, state, transaction, layout_update, validate, build
from .activation import ActivationPlanner
from .catalog import Catalog, active_projection

NAME = 'activation-state.json'
VERSION = 1
ALGORITHM = 'append-only-reviewed-1'
VARIANTS = ('current', 'parent-distance', 'centering', 'connector', 'balanced')
FILES = ('activation-plan.json', 'candidate-geometry.json', 'metrics.json')


def fingerprint(value):
    """Semantic inventories are sets; presentation arrays deliberately are not."""
    return snapshot.ordered_digest(value)


def plan_fingerprint(plan):
    return snapshot.digest(plan)


def geometry_hashes(geometry):
    return {'geometry': fingerprint(geometry),
            'bounds': fingerprint([[n['key'], n['x'], n['y'], n['width'], n['height']]
                                   for n in geometry['nodes']]),
            'connectors': fingerprint(geometry['connectorSegments'])}


def algorithm_hash():
    here = Path(__file__).parent
    return fingerprint({n: hashlib.sha256((here/n).read_bytes()).hexdigest() for n in
                        ('activation_persistence.py', 'activation_geometry.js', 'activation_variants.js',
                         'layout_bridge.cjs', 'build.py', 'layout_update.js', 'persistent_layout.js', 'validate.py',
                         'activation.py', 'catalog.py', 'snapshot.py', 'activation-state.schema.json')})


def check_history(value):
    fields = {'schema_version', 'history_version', 'layout_generation', 'active_categories',
              'active_topics', 'geometry_hashes', 'accepted_geometry', 'events'}
    if not isinstance(value, dict) or value.get('schema_version') != VERSION or set(value) != fields:
        raise ValueError('ACTIVATION_STATE_MIGRATION_REQUIRED: incompatible presentation history')
    for k in ('history_version', 'layout_generation'):
        if type(value[k]) is not int or value[k] < 0: raise ValueError('Invalid activation counter')
    g = value['accepted_geometry']
    allowed={'nodes','trays','branches','connectorSegments','buses','bounds','activationRoutes'}
    if not isinstance(g,dict) or not set(g)<=allowed or not allowed-{'activationRoutes'}<=set(g):
        raise ValueError('ACTIVATION_STATE_MIGRATION_REQUIRED: unknown geometry fields')
    closed={'nodes':({'key','x','y','width','height','depth','font','line','lines'},{'parent'}),
            'trays':({'parent','x','y','width','height','topics'},set()),
            'branches':({'parent','child','points','d'},set()),
            'connectorSegments':({'parent','children','depth','points','d'},set()),
            'activationRoutes':({'parent','child','points','length','shared_frozen_segments'},set())}
    for section,(required,optional) in closed.items():
        if not isinstance(g.get(section,[]),list): raise ValueError('Invalid geometry inventory')
        for record in g.get(section,[]):
            if not isinstance(record,dict) or not required<=set(record) or not set(record)<=required|optional:
                raise ValueError('ACTIVATION_STATE_MIGRATION_REQUIRED: unknown '+section+' fields')
    if set(g['bounds'])!={'x0','x1','y0','y1'}: raise ValueError('ACTIVATION_STATE_MIGRATION_REQUIRED: bounds')
    keys=[n['key'] for n in g['nodes']]
    if len(keys)!=len(set(keys)): raise ValueError('Duplicate history geometry')
    for n in g['nodes']:
        if any(type(n.get(f)) not in (int,float) or not math.isfinite(n[f]) for f in ('x','y','width','height')) or n['width']<=0 or n['height']<=0:
            raise ValueError('Invalid history geometry number')
    if value['geometry_hashes'] != geometry_hashes(g): raise ValueError('ACTIVATION_STATE_INTEGRITY_MISMATCH')
    for field, kind in [('active_categories', 'category'), ('active_topics', 'topic')]:
        keys = value[field]
        if keys != sorted(set(keys)) or any(not k.startswith(kind+':') or not k.split(':')[1].isdigit() for k in keys):
            raise ValueError('Invalid activation identities')
        if set(keys) != {n['key'] for n in g['nodes'] if n['key'].startswith(kind+':')}:
            raise ValueError('Activation history/geometry inventory mismatch')
    if len(value['events']) != value['history_version']: raise ValueError('Invalid activation event count')
    for event in value['events']:
        if set(event) != {'manifest_fingerprint', 'plan_fingerprint', 'candidate_fingerprint', 'variant', 'generation'}:
            raise ValueError('Unknown activation event fields')
        if any(not isinstance(event[k],str) or len(event[k])!=64 or any(c not in '0123456789abcdef' for c in event[k]) for k in ('manifest_fingerprint','plan_fingerprint','candidate_fingerprint')) or type(event['generation']) is not int or event['generation']<1:
            raise ValueError('Invalid activation event fingerprints/generation')
        if event['variant'] not in VARIANTS: raise ValueError('Unknown accepted variant')
    return value


def baseline(cp, geometry):
    hashes = geometry_hashes(geometry)
    value = {'schema_version': VERSION, 'history_version': 0,
             'layout_generation': cp['presentation_generation'],
             'active_categories': sorted(cp['categories']),
             'active_topics': sorted(k for r in cp['categories'].values() for k in r['topic_order']),
             'geometry_hashes': hashes, 'accepted_geometry': deepcopy(geometry), 'events': []}
    return check_history(value)


def read_history(path, cp, geometry=None):
    from . import canonical
    if canonical.installed(path): return canonical.restore(path)[2]
    p = Path(path)/NAME
    value = check_history(json.loads(p.read_text())) if p.exists() else baseline(cp, geometry)
    if value['layout_generation'] != cp['presentation_generation'] or set(value['active_categories']) != set(cp['categories']):
        raise ValueError('ACTIVATION_STATE_INTEGRITY_MISMATCH: checkpoint/history disagree')
    return value


def accepted(root, loaded=None):
    root = Path(root)
    from . import canonical
    if canonical.installed(root/'state/knowledge-atlas'):
        cp, previous, history, geom, _ = canonical.restore(root/'state/knowledge-atlas')
        return cp, previous, history, geom, loaded or snapshot.load_source(root/'data/knowledge')
    cp, previous = state.read(root/'state/knowledge-atlas')
    loaded = loaded or snapshot.load_source(root/'data/knowledge')
    history_path = root/'state/knowledge-atlas'/NAME
    if history_path.exists():
        h = read_history(history_path.parent, cp)
        g = h['accepted_geometry']
    else:
        g = json.loads((root/'docs/knowledge-map/geometry.js').read_text().split('=',1)[1].rstrip(';\n'))
        h = baseline(cp, g)
    if fingerprint(g) != previous['geometry_fingerprint']:
        raise ValueError('STATE_GEOMETRY_MISMATCH: accepted geometry/snapshot disagree')
    return cp, previous, h, g, loaded


def bootstrap(root):
    root = Path(root)
    with transaction.lock(root, write=True):
        target = root/'state/knowledge-atlas'
        if (target/NAME).exists(): raise ValueError('ACTIVATION_STATE_ALREADY_EXISTS: bootstrap refuses overwrite')
        if (target.parent/'.knowledge-atlas-transaction.json').exists(): raise ValueError('RECOVERY_REQUIRED')
        cp, previous, history, geom, loaded = accepted(root)
        validate.geometry(projection(loaded,set(history['active_categories']+history['active_topics'])), cp, geom)
        if cp['presentation_generation']!=0 or len(history['active_categories'])!=46 or len(history['active_topics'])!=89:
            raise ValueError('ACTIVATION_STATE_MIGRATION_REQUIRED: bootstrap is the accepted Generation-0 baseline only')
        before = transaction.inventory(target)
        outputs = {p.name:p.read_bytes() for p in target.iterdir() if p.is_file()}
        outputs[NAME] = snapshot.encode(history)
        def preflight():
            if transaction.inventory(target) != before: raise ValueError('STATE_CHANGED_DURING_BOOTSTRAP')
        transaction.publish(root, [(target,outputs)], preflight=preflight,
                            journal=target.parent/'.knowledge-atlas-transaction.json')
    return {'status':'SAFE_TO_APPLY', 'outcome':'NO_CHANGE', 'generation':cp['presentation_generation'], 'bootstrap':True}


def binding(loaded, cp, history, frozen, plan, candidate, metrics, variant, root):
    return {'plan':plan_fingerprint(plan), 'knowledge':snapshot.digest(loaded),
            'catalog':snapshot.digest(loaded.get('catalog_observations',{})),
            'evidence':snapshot.digest({k:loaded[k] for k in ('courses','projects','stages','edges','evidence')}),
            'personal':snapshot.digest(loaded['progress']), 'activation_state':fingerprint(history),
            'checkpoint':fingerprint(cp), 'existing_geometry':geometry_hashes(frozen),
            'candidate':fingerprint(candidate), 'validation':fingerprint(metrics),
            'runtime':fingerprint({n:hashlib.sha256((Path(root)/'prototypes/knowledge-atlas-v6'/n).read_bytes()).hexdigest() for n in build.ASSETS}),
            'algorithm':algorithm_hash(), 'algorithm_version':ALGORITHM, 'variant':variant}


def display(plan):
    rows = {r['id']:r for r in plan['entities']}
    result=[]
    for key in plan['new_categories']+plan['new_topics']:
        r=rows[key]
        parent=r['canonical_parent'] or (r['structural_memberships'][0] if r['structural_memberships'] else None)
        result.append({'key':key,'title':r['title'],'type':r['entity_type'],'parent':parent})
    return sorted(result,key=lambda r:r['key'])


def complete_routes(geometry):
    """Record additive reviewed routes for LCA overlays, without rerouting old buses."""
    g=deepcopy(geometry)
    pairs={(b['parent'],b['child']) for b in g['branches']}
    for route in g.get('activationRoutes',[]):
        if route['child'].startswith('category:') and (route['parent'],route['child']) not in pairs:
            points=route['points']
            g['branches'].append({'parent':route['parent'],'child':route['child'],'points':points,
                                 'd':''.join(('M' if i==0 else 'L')+str(p['x'])+','+str(p['y']) for i,p in enumerate(points))})
    return g


def test_only_root(root):
    if Path(root).resolve()==Path(__file__).resolve().parents[2] or not (Path(root)/'.atlas-disposable-test').is_file():
        raise ValueError('FIXTURE_ACTIVATION_FORBIDDEN: disposable test root required')


def package_preview(root, destination, variant='current', context=None, *, fixture=None):
    """fixture override is an internal disposable-test adapter, never a CLI option."""
    root=Path(root); destination=Path(destination).resolve()
    from . import canonical, canonical_activation
    if canonical.installed(root/'state/knowledge-atlas'):
        if fixture: raise ValueError('Canonical reveal requires real disposable Knowledge inputs, not a fixture plan override')
        return canonical_activation.package_preview(root, destination, variant, context)
    if destination.is_relative_to(root.resolve()) and not destination.is_relative_to(root.resolve()/'prototypes/activation-previews'):
        raise ValueError('Preview destination must be external or below prototypes/activation-previews')
    if destination.exists(): raise ValueError('PREVIEW_ALREADY_EXISTS: never overwrite reviewed artifacts')
    if fixture: test_only_root(root)
    if variant not in VARIANTS: raise ValueError('Unknown placement variant')
    with transaction.lock(root):
        cp,previous,h,g,loaded=accepted(root)
        if (root/'state/.knowledge-atlas-transaction.json').exists(): raise ValueError('RECOVERY_REQUIRED')
        planner=ActivationPlanner(Catalog(loaded),cp,g)
        plan=fixture['plan'] if fixture else planner.plan(**(context or {}))
        f=fixture or {'plan':plan,'display':display(plan)}
        result=layout_update.bridge(root/'prototypes/knowledge-atlas-v6',action='activation-preview',
                                    geometry=g,fixture=f,variant=variant)
        candidate=complete_routes(result['geometry'])
        metrics={**result['report'],'fixture_only':bool(fixture),'generation':cp['presentation_generation']}
        checks=layout_update.bridge(root/'prototypes/knowledge-atlas-v6',action='activation-validate',frozen=g,geometry=candidate)
        if any(checks.values()): raise ValueError('INVALID_ACTIVATION_GEOMETRY')
        metrics={**metrics,'independent_geometry_validation':checks}
        b=binding(loaded,cp,h,g,plan,candidate,metrics,variant,root)
        manifest={'schema_version':VERSION,'bindings':b,'context':plan['context'],
                  'outcome':metrics['outcome'],'selected_variant':variant.upper(),
                  'new_categories':plan['new_categories'],'new_topics':plan['new_topics'],
                  'blocked_references':plan['blocked_references'], 'expected_generation_change':int(bool(plan['new_categories'] or plan['new_topics'])),
                  'fixture_only':bool(fixture)}
        # No arbitrary filesystem paths or timestamps in deterministic approval identity.
        manifest['manifest_fingerprint']=fingerprint(manifest)
        destination.mkdir(parents=True)
        for name,value in zip(FILES,(plan,candidate,metrics)):
            transaction.durable_file(destination/name,snapshot.encode(value))
        transaction.durable_file(destination/'activation-manifest.json',snapshot.encode(manifest))
        # Static local review uses the exact candidate; no algorithm rerun in the page.
        if not fixture and metrics['outcome'] in ('NO_CHANGE','ACTIVATION_REVIEW_REQUIRED'):
            data=projection(loaded,set(h['active_categories']+h['active_topics']+plan['new_categories']+plan['new_topics']))
            new_cp=checkpoint(cp,candidate,data)
            assets=build.preview_outputs(build.artifacts(root/'prototypes/knowledge-atlas-v6',data,new_cp,candidate,state.complete(data,new_cp,candidate)))
            for name,content in assets.items():
                p=destination/'view'/name;p.parent.mkdir(parents=True,exist_ok=True);transaction.durable_file(p,content)
        return manifest


def checkpoint(cp, geometry, data):
    """Allocation descriptors are derived from reviewed coordinates, never vice versa."""
    out=deepcopy(cp); nodes={n['key']:n for n in geometry['nodes']}; trays={t['parent']:t for t in geometry['trays']}
    cats={f"category:{r['id']}":r for r in data['categories']}
    topics={f"topic:{r['id']}":r for r in data['topics']}
    for key,row in cats.items():
        n=nodes[key];parent=nodes.get('category:'+str(row['canonical_parent_id']),{'x':0,'y':0})
        children=sorted(k for k,r in cats.items() if r['canonical_parent_id']==row['id'])
        leaves=sorted(k for k,r in topics.items() if r['canonical_parent_id']==row['id'])
        old=out['categories'].get(key)
        if not old:
            old={'slot_row':0,'visible_extent':{'left':-n['width']/2,'top':0,'width':n['width'],'height':n['height']},
                 'allocated_width':n['width'],'allocated_height':n['height'],'reserved_capacity':{'width':0,'height':0},
                 'sibling_order':[], 'topic_order':[], 'tray_allocation':None,
                 'card_allocation':{k:n[k] for k in ('width','height','font','line')}}
            out['categories'][key]=old
        old['slot_anchor']={'x':n['x']-parent['x'],'y':n['y']-parent['y']}
        for field,keys in [('sibling_order',children),('topic_order',leaves)]:
            old[field]=old[field]+[k for k in keys if k not in old[field]]
        t=trays.get(key)
        if t and old['tray_allocation'] is None:
            old['tray_allocation']={'left':t['x']-n['x'],'top':t['y']-n['y'],'width':t['width'],'height':t['height'],
                                    'padding':8,'row_gap':4,'rows':[{'key':k,'width':nodes[k]['width'],'height':nodes[k]['height']} for k in t['topics']]}
        # Only expand allocation metadata. Accepted coordinates/routes stay authoritative.
        boxes=[nodes[k] for k in children+leaves]+[n]
        left=min([old['visible_extent']['left']]+[b['x']-b['width']/2-n['x'] for b in boxes])
        right=max([old['visible_extent']['left']+old['visible_extent']['width']]+[b['x']+b['width']/2-n['x'] for b in boxes])
        bottom=max([old['visible_extent']['height']]+[b['y']+b['height']-n['y'] for b in boxes])
        old['visible_extent']={'left':left,'top':0,'width':right-left,'height':bottom}
        old['allocated_width']=max(old['allocated_width'],right-left);old['allocated_height']=max(old['allocated_height'],bottom)
        old['reserved_capacity']={'width':old['allocated_width']-(right-left),'height':old['allocated_height']-bottom}
    return out


def projection(loaded, keys):
    """History is an ID filter over Knowledge facts, never a copy of membership truth."""
    data=deepcopy(active_projection(loaded))
    for table,kind in [('categories','category'),('topics','topic')]:
        data[table]=[r for r in data[table] if f"{kind}:{r['id']}" in keys]
        if {f"{kind}:{r['id']}" for r in data[table]} != {k for k in keys if k.startswith(kind+':')}:
            raise ValueError('ACTIVE_HISTORY_METADATA_MISSING: restore accepted Knowledge evidence')
    data['edges']=[e for e in data['edges'] if all(not k.startswith(('category:','topic:')) or k in keys for k in (e['source'],e['target']))]
    return data


def approve(root, manifest_path, *, reviewed_fingerprint=None, fault=None, test_context=None):
    root=Path(root).resolve();path=Path(manifest_path);folder=path.parent
    from . import canonical, canonical_activation
    if canonical.installed(root/'state/knowledge-atlas'):
        if test_context: raise ValueError('Canonical reveal requires normal Knowledge inputs')
        return canonical_activation.approve(root, path, reviewed_fingerprint=reviewed_fingerprint, fault=fault)
    with transaction.lock(root,write=True):
        journal=root/'state/.knowledge-atlas-transaction.json'
        if journal.exists(): raise ValueError('RECOVERY_REQUIRED')
        m=json.loads(path.read_text())
        if reviewed_fingerprint is None: raise ValueError('REVIEW_FINGERPRINT_REQUIRED: provide the fingerprint copied during human review')
        if reviewed_fingerprint!=m.get('manifest_fingerprint'): raise ValueError('STALE_ACTIVATION_PREVIEW: reviewed manifest identity changed')
        core={k:v for k,v in m.items() if k!='manifest_fingerprint'}
        if set(m)!={'schema_version','bindings','context','outcome','selected_variant','new_categories','new_topics','blocked_references','expected_generation_change','fixture_only','manifest_fingerprint'} or m.get('schema_version')!=VERSION or fingerprint(core)!=m.get('manifest_fingerprint'):
            raise ValueError('STALE_ACTIVATION_PREVIEW: manifest changed')
        if m['selected_variant']!=m['bindings']['variant'].upper(): raise ValueError('STALE_ACTIVATION_PREVIEW: variant')
        if m.get('fixture_only') and test_context is None:
            raise ValueError('FIXTURE_ACTIVATION_FORBIDDEN: disposable tests only')
        plan,candidate,metrics=(json.loads((folder/n).read_text()) for n in FILES)
        if test_context is not None: test_only_root(root)
        try:
            cp,previous,h,frozen,loaded=accepted(root)
        except ValueError as error:
            if 'MIGRATION_REQUIRED' in str(error): raise
            raise ValueError('STALE_ACTIVATION_PREVIEW: '+str(error)) from error
        # Replay is an exact event identity, not permission to skip input validation.
        applied=any(e['manifest_fingerprint']==m['manifest_fingerprint'] for e in h['events'])
        if applied:
            expected=binding(loaded,cp,h,frozen,plan,candidate,metrics,m['bindings']['variant'],root)
            for key in ('plan','knowledge','catalog','evidence','personal','candidate','validation','algorithm','runtime','variant'):
                if expected[key]!=m['bindings'][key]: raise ValueError('STALE_ACTIVATION_PREVIEW: replay '+key)
            if fingerprint(frozen)!=m['bindings']['candidate']: raise ValueError('STALE_ACTIVATION_PREVIEW: replay geometry')
            return {'status':'SAFE_TO_APPLY','outcome':'NO_CHANGE','applied':False,'generation':cp['presentation_generation']}
        fresh=test_context['plan'] if test_context else ActivationPlanner(Catalog(loaded),cp,frozen).plan(**context_args(m['context']))
        if plan_fingerprint(fresh)!=plan_fingerprint(plan): raise ValueError('STALE_ACTIVATION_PREVIEW: semantic plan')
        expected=binding(loaded,cp,h,frozen,plan,candidate,metrics,m['bindings']['variant'],root)
        if expected!=m['bindings']: raise ValueError('STALE_ACTIVATION_PREVIEW: input/candidate/algorithm binding')
        if m['selected_variant']!=m['bindings']['variant'].upper(): raise ValueError('STALE_ACTIVATION_PREVIEW: variant')
        if any(m[k]!=plan[k] for k in ('new_categories','new_topics','blocked_references')) or m['outcome']!=metrics['outcome'] or m['expected_generation_change']!=int(bool(plan['new_categories'] or plan['new_topics'])):
            raise ValueError('STALE_ACTIVATION_PREVIEW: misleading manifest summary')
        if plan['blocked_references'] or metrics['outcome']=='METADATA_REQUIRED': raise ValueError('METADATA_REQUIRED: '+json.dumps(plan['blocked_references']))
        if plan['new_roots'] or metrics['outcome']=='ACTIVATION_REBALANCE_REQUIRED': raise ValueError('ACTIVATION_REBALANCE_REQUIRED')
        checks=layout_update.bridge(root/'prototypes/knowledge-atlas-v6',action='activation-validate',frozen=frozen,geometry=candidate)
        if any(checks.values()) or checks!=metrics['independent_geometry_validation']: raise ValueError('INVALID_ACTIVATION_GEOMETRY')
        if metrics['outcome']=='NO_CHANGE':
            return {'status':'SAFE_TO_APPLY','outcome':'NO_CHANGE','applied':False,'generation':cp['presentation_generation']}
        if metrics['outcome']!='ACTIVATION_REVIEW_REQUIRED': raise ValueError('Invalid activation outcome')
        # Preserve every accepted node, tray and connector exactly, not just its bounds.
        for field in ('nodes','trays','connectorSegments','branches'):
            if snapshot.encode(candidate[field][:len(frozen[field])])!=snapshot.encode(frozen[field]): raise ValueError('EXISTING_GEOMETRY_CHANGED')
        expected_keys=set(h['active_categories']+h['active_topics']+plan['new_categories']+plan['new_topics'])
        if {n['key'] for n in candidate['nodes']}!=expected_keys: raise ValueError('UNREVIEWED_ACTIVATION_ENTITY')
        data=projection(loaded,expected_keys);validate.validate(data)
        new_cp=checkpoint(cp,candidate,data);new_cp['presentation_generation']=cp['presentation_generation']+1
        validate.geometry(data,new_cp,candidate)
        new_history=baseline(new_cp,candidate);new_history['history_version']=h['history_version']+1
        new_history['events']=h['events']+[{'manifest_fingerprint':m['manifest_fingerprint'],'plan_fingerprint':m['bindings']['plan'],
            'candidate_fingerprint':m['bindings']['candidate'],'variant':m['bindings']['variant'],'generation':new_cp['presentation_generation']}]
        check_history(new_history)
        target=root/'state/knowledge-atlas'
        state_outputs={p.name:p.read_bytes() for p in target.iterdir() if p.is_file()}
        state_outputs[NAME]=snapshot.encode(new_history)
        if fault:fault('after_activation_state_candidate')
        new_previous=state.complete(data,new_cp,candidate)
        state_outputs.update({k:v for k,v in state.outputs(target,new_cp,new_previous).items() if k!=NAME})
        if fault:fault('after_geometry_candidate')
        assets=build.artifacts(root/'prototypes/knowledge-atlas-v6',data,new_cp,candidate,new_previous)
        layout_update.bridge(root/'prototypes/knowledge-atlas-v6',action='runtime-test',assets={n:b.decode() for n,b in assets.items()})
        production=build.production_outputs(assets,root/'docs/knowledge-atlas-preview')
        original_state=transaction.inventory(target);original_prod=transaction.inventory(root/'docs/knowledge-map')
        def preflight():
            if binding(loaded,cp,h,frozen,plan,candidate,metrics,m['bindings']['variant'],root)!=m['bindings']:
                raise ValueError('STALE_ACTIVATION_PREVIEW: algorithm/runtime changed during build')
            if transaction.inventory(target)!=original_state or transaction.inventory(root/'docs/knowledge-map')!=original_prod:
                raise ValueError('STALE_ACTIVATION_PREVIEW: concurrent presentation change')
            if snapshot.digest(snapshot.load_source(root/'data/knowledge'))!=m['bindings']['knowledge']:
                raise ValueError('STALE_ACTIVATION_PREVIEW: concurrent Knowledge change')
            if fingerprint(json.loads(path.read_text()))!=fingerprint(m) or any(fingerprint(json.loads((folder/n).read_text()))!=fingerprint(v) for n,v in zip(FILES,(plan,candidate,metrics))):
                raise ValueError('STALE_ACTIVATION_PREVIEW: concurrent artifact change')
        def verify():
            build.verify_release(root/'docs/knowledge-map',production)
            if (target/NAME).read_bytes()!=state_outputs[NAME]: raise ValueError('ACTIVATION_PUBLISH_MISMATCH')
        if fault:fault('before_state_staging')
        transaction.publish(root,[(target,state_outputs),(root/'docs/knowledge-map',production)],fault=fault,
                            preflight=preflight,journal=journal,verify=verify)
        return {'status':'SAFE_TO_APPLY','outcome':'APPROVED_ACTIVATION','applied':True,'generation':new_cp['presentation_generation']}


def context_args(context):
    return {'mode':context['mode'],'course_ids':context['course_ids'],'project_ids':context['project_ids'],
            'include_personal':context['include_personal']}
