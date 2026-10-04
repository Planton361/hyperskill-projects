"""Persistent-state release gates and a joint state/build publication transaction."""
import json
import hashlib
from pathlib import Path
from . import build, diff, layout_update, snapshot, validate, state as state_store, regions, transaction
from .classify import MIGRATIONS


def run(root, output=None, source=None, mode='build', rebalance=False, preview=False, budget=None,
        state=None, approve_review=False, bootstrap=False, recover=False, fault=None, migrate=False):
    root = Path(root).resolve()
    if mode not in ('build','dry-run','check'):raise ValueError('unknown pipeline mode')
    if mode != 'build' and (bootstrap or recover or migrate or preview):raise ValueError('explicit writer operation requires build mode')
    with transaction.lock(root, write=mode == 'build' or bootstrap or recover):
        return _run(root, output, source, mode, rebalance, preview, budget, state, approve_review, bootstrap, recover, fault, migrate)


def _run(root, output, source, mode, rebalance, preview, budget, state_path, approve_review, bootstrap, recover, fault, migrate):
    runtime = root / 'prototypes/knowledge-atlas-v6'
    output = Path(output or runtime/'build').resolve()
    state_path = Path(state_path or root/'state/knowledge-atlas').resolve()
    source = Path(source or root/'data/knowledge').resolve()
    if not output.is_relative_to(root/'prototypes') or output == runtime or output.is_relative_to(runtime/'tests'):
        raise ValueError('build destination must be isolated below prototypes/')
    if state_path != root/'state/knowledge-atlas' and not state_path.is_relative_to(root/'prototypes'):
        raise ValueError('custom state must be isolated below prototypes/')
    if output == state_path or output.is_relative_to(state_path) or state_path.is_relative_to(output):
        raise ValueError('state and build directories must be disjoint')
    if source != root/'data/knowledge' and mode == 'build' and state_path == root/'state/knowledge-atlas':
        raise ValueError('custom source requires explicit isolated --state for writes')
    if output.exists():
        if not (output/'build-manifest.json').is_file(): raise ValueError('refusing to replace unmanaged output')
        build.verify_state(output)
    original_build = transaction.inventory(output)
    journal = state_path.parent/'.knowledge-atlas-transaction.json'
    if recover:
        transaction.recover(journal,root)
        return {'status':'SAFE_TO_APPLY','outcome':'SAFE_TO_APPLY','applied':True,'message':'Transaction recovery complete'}
    if journal.exists(): raise ValueError('RECOVERY_REQUIRED: pending transaction; run --recover-transaction')
    data = snapshot.load_source(source)
    validate.validate(data)
    environment = layout_update.bridge(runtime, action='canary')
    if migrate:
        original_state={n:(state_path/n).read_bytes() for n in state_store.NAMES}
        cp,previous,geom=state_store.migrate_ordered_hashes(state_path,data,runtime)
        outputs=build.artifacts(runtime,data,cp,geom,previous)
        runtime_result=layout_update.bridge(runtime,action='runtime-test',assets={n:b.decode() for n,b in outputs.items()})
        report={'report_schema_version':2,'status':'SAFE_TO_APPLY','outcome':'SAFE_TO_APPLY','applied':True,'migration':'state-schema-1-to-2-ordered-hashes',
                'message':'Explicit lossless state migration; geometry and generation unchanged',
                'generation':cp['presentation_generation'],'validation':{'status':'PASS','atlas_runtime':runtime_result}}
        outputs['update-report.json']=snapshot.encode(report)
        def preflight():
            if original_state!={n:(state_path/n).read_bytes() for n in state_store.NAMES} or transaction.inventory(output)!=original_build:
                raise ValueError('STATE_CHANGED_DURING_MIGRATION')
            if snapshot.index(snapshot.load_source(source))['fingerprint']!=previous['fingerprint']:
                raise ValueError('SOURCE_CHANGED_DURING_MIGRATION')
        transaction.publish(root,[(state_path,state_store.outputs(state_path,cp,previous)),(output,outputs)],
                            fault=fault,preflight=preflight,journal=journal)
        return report
    if bootstrap:
        if any((state_path/n).exists() for n in state_store.NAMES):
            raise ValueError('STATE_ALREADY_EXISTS: bootstrap never overwrites existing or partial state')
        bootstrap_state = transaction.inventory(state_path)
        accepted, cp, geom = state_store.baseline(runtime, data)
        if snapshot.index(accepted)['fingerprint'] != snapshot.index(data)['fingerprint']:
            raise ValueError('BOOTSTRAP_SOURCE_MISMATCH: current data must equal accepted V6 baseline')
        previous = state_store.complete(data, cp, geom)
        outputs = build.artifacts(runtime, data, cp, geom, previous)
        runtime_result = layout_update.bridge(runtime, action='runtime-test', assets={n:b.decode() for n,b in outputs.items()})
        def preflight():
            if transaction.inventory(state_path) != bootstrap_state:
                raise ValueError('STATE_CHANGED_DURING_BOOTSTRAP: refusing to overwrite concurrent state')
            if snapshot.index(snapshot.load_source(source))['fingerprint'] != previous['fingerprint']:
                raise ValueError('SOURCE_CHANGED_DURING_BOOTSTRAP: aborting publication')
        transaction.publish(root, [(state_path,state_store.outputs(state_path,cp,previous))], fault=fault,preflight=preflight,journal=journal)
        return {'status':'SAFE_TO_APPLY','outcome':'SAFE_TO_APPLY','applied':True,'bootstrap':True,
                'message':'Frozen V6 baseline reproduced: all 135 bounds exact; persistent state initialized',
                'generation':cp['presentation_generation'],'validation':{'status':'PASS','atlas_runtime':runtime_result}}
    cp, before = state_store.read(state_path, allow_layout_migration=rebalance)
    original_state = {n:(state_path/n).read_bytes() for n in state_store.NAMES}
    active_keys = [f'{kind}:{k}' for table,kind in [('categories','category'),('topics','topic')] for k in before[table]]
    restored = layout_update.bridge(runtime, action='restore', data=data, checkpoint=cp, activeKeys=active_keys)
    geom = restored['geometry']
    after = snapshot.index(data)
    changes = diff.compare(before,after)
    if changes['change_types'] == ['NO_CHANGE'] and not rebalance and snapshot.ordered_digest(geom) != before['geometry_fingerprint']:
        raise ValueError('STATE_GEOMETRY_MISMATCH: saved geometry cannot be reproduced; explicit migration required')
    migrations = set(changes['change_types']) & MIGRATIONS
    if migrations and not rebalance:
        return {'status':'REBALANCE_REQUIRED','outcome':'REBALANCE_REQUIRED','applied':False,'diff':changes,
                'message':'Explicit --rebalance required: '+', '.join(sorted(migrations)),
                'safe_to_build_preview':False,'validation':{'status':'SOURCE_VALID'},
                'affected_region':'taxonomy','required_width':None,'available_width':None,
                'affected_categories':[f"category:{r['id']}" for r in changes['categories']['reparented']],
                'estimated_displacement':None}
    result = layout_update.update(runtime,data,cp,geom,changes,rebalance,budget,active_keys)
    if result.get('status') == 'REBALANCE_REQUIRED':
        return {**result,'outcome':'REBALANCE_REQUIRED','applied':False,'diff':changes,
                'safe_to_build_preview':False,'validation':{'status':'SOURCE_VALID'},
                'message':'Candidate stopped at explicit displacement budget; no publication'}
    new_cp = snapshot.presentation(result['checkpoint'])
    # Generation tracks ALL presentation allocation/order mutations, including tray rows.
    new_cp['presentation_generation'] = cp['presentation_generation'] + (new_cp['categories'] != cp['categories'])
    new_geom = layout_update.bridge(runtime, action='restore',data=data,checkpoint=new_cp)['geometry']
    if fault: fault('after_candidate_checkpoint')
    region = regions.impact(data,geom,new_geom,changes,result['events'],result['repacked_trays'],cp)
    try: validate.geometry(data,new_cp,new_geom)
    except ValueError as e:
        if changes['topics']['added'] or changes['categories']['added'] or changes.get('label_changes'):
            displacement=layout_update.displacement(geom,new_geom,'category')
            return {'status':'REBALANCE_REQUIRED','outcome':'REBALANCE_REQUIRED','applied':False,'diff':changes,
                    'region_impact':{**region,'outcome':'REBALANCE_REQUIRED'},'message':'Candidate geometry requires migration: '+str(e),
                    'validation':{'status':'FAIL','message':str(e)},'safe_to_build_preview':False,
                    'affected_region':region['origins'][0] if region['origins'] else 'taxonomy',
                    'required_width':new_cp['categories'][region['origins'][0]]['allocated_width'] if region['origins'] else None,
                    'available_width':cp['categories'][region['origins'][0]]['allocated_width'] if region['origins'] else None,
                    'affected_categories':displacement['affected_nodes'],'estimated_displacement':displacement['max']}
        raise
    if not rebalance: layout_update.zero_guard(changes,cp,new_cp,geom,new_geom)
    if migrations: region['outcome']='REBALANCE_REQUIRED'; region['reasons'] += sorted(migrations)
    candidate = state_store.complete(data,new_cp,new_geom)
    if fault: fault('during_artifact_generation')
    outputs = build.artifacts(runtime,data,new_cp,new_geom,candidate)
    if fault: fault('during_browser_validation')
    runtime_validation = layout_update.bridge(runtime,action='runtime-test',assets={n:b.decode() for n,b in outputs.items()})
    if mode == 'check':
        state_store.baseline(runtime,data)
        if before['fingerprint'] != after['fingerprint']:
            raise ValueError('STATE_OUT_OF_DATE: knowledge differs from persistent update snapshot; use --dry-run')
        if snapshot.ordered_digest(new_geom) != before['geometry_fingerprint']:
            raise ValueError('STATE_GEOMETRY_MISMATCH: persistent geometry not reproducible')
        if output.exists():
            build.verify_state(output)
            for name,content in outputs.items():
                if not (output/name).exists() or (output/name).read_bytes() != content:
                    raise ValueError('stale build artifact: '+name+'; run --build')
    outcome = region['outcome']
    permitted = outcome == 'SAFE_TO_APPLY' or (outcome == 'REVIEW_REQUIRED' and approve_review) or rebalance
    report = {'report_schema_version':2,'status':outcome,'outcome':outcome,'mode':mode,'diff':changes,'region_impact':region,
              'applied':False,'authorization':'rebalance' if rebalance else 'approve-review' if approve_review else 'normal',
              'presentation':{'category_displacement':layout_update.displacement(geom,new_geom,'category'),
                'topic_displacement':layout_update.displacement(geom,new_geom,'topic'),
                'changed_region_anchors':layout_update.displacement(geom,new_geom,'category')['changed'],
                'repacked_topic_trays':result['repacked_trays'],
                'checkpoint_changed':snapshot.encode(cp)!=snapshot.encode(new_cp),
                'generation_before':cp['presentation_generation'],'generation':new_cp['presentation_generation'],
                'candidate_generation':new_cp['presentation_generation'],'persisted_generation':cp['presentation_generation'],
                'bounds_before':geom['bounds'],'bounds_after':new_geom['bounds'],'overflow_events':result['events'],
                'explicit_rebalance':rebalance},
              'evidence':{'requirements_updated':sum(len(changes['requirements'][k]) for k in ('added','removed','changed')),
                          'links_added':len(changes['requirements']['added'])},
              'validation':{'status':'PASS','atlas_runtime':runtime_validation,'font_canary':environment,
                'fingerprints':{'source':after['fingerprint'],'checkpoint':snapshot.ordered_digest(new_cp),
                    'geometry':snapshot.ordered_digest(new_geom),
                    'build_manifest':hashlib.sha256(outputs['build-manifest.json']).hexdigest(),
                    'build_assets':json.loads(outputs['build-manifest.json'])['assets']},
                **validate.geometry(data,new_cp,new_geom)},
              'safe_to_build_preview':permitted,'state_changed':state_store.outputs(state_path,new_cp,candidate)!=state_store.outputs(state_path,cp,before),
              'installed_build':'present' if output.exists() else 'absent; validated in memory',
              'message':'Validated candidate; '+('authorized for apply' if permitted else 'publication blocked pending explicit authorization')}
    origin=region['origins'][0] if region['origins'] else None
    report.update({'affected_region':origin,'affected_categories':report['presentation']['category_displacement']['affected_nodes'],
                   'estimated_displacement':report['presentation']['category_displacement']['max'],
                   'required_width':new_cp['categories'].get(origin,{}).get('allocated_width'),
                   'available_width':cp['categories'].get(origin,{}).get('allocated_width')})
    if mode == 'build' and permitted:
        report['applied']=True
        report['presentation']['persisted_generation']=new_cp['presentation_generation']
        saved = output/'update-report.json'
        saved_valid = saved.exists() and json.loads(saved.read_text()).get('report_schema_version') == 2
        artifact_changed = not output.exists() or any(not (output/n).is_file() or (output/n).read_bytes()!=b for n,b in outputs.items())
        outputs['update-report.json'] = saved.read_bytes() if saved_valid and not artifact_changed and changes['change_types']==['NO_CHANGE'] and not rebalance else snapshot.encode(report)
        destinations=[]
        candidate_state=state_store.outputs(state_path,new_cp,candidate)
        if any((state_path/n).read_bytes()!=candidate_state[n] for n in state_store.NAMES): destinations.append((state_path,candidate_state))
        if not output.exists() or any(not (output/n).is_file() or (output/n).read_bytes()!=b for n,b in outputs.items()): destinations.append((output,outputs))
        if preview:
            dest=root/'docs/knowledge-atlas-preview'; published=build.preview_outputs(outputs)
            if (dest/'PREVIEW-NOTES.md').exists(): published['PREVIEW-NOTES.md']=(dest/'PREVIEW-NOTES.md').read_bytes()
            destinations.append((dest,published))
        def preflight():
            if original_state!={n:(state_path/n).read_bytes() for n in state_store.NAMES}:
                raise ValueError('STATE_CHANGED_DURING_UPDATE: aborting publication')
            if snapshot.index(snapshot.load_source(source))['fingerprint'] != after['fingerprint']:
                raise ValueError('SOURCE_CHANGED_DURING_UPDATE: aborting publication')
            if transaction.inventory(output) != original_build:
                raise ValueError('BUILD_CHANGED_DURING_UPDATE: aborting publication')
        if destinations: transaction.publish(root,destinations,fault=fault,preflight=preflight,journal=journal)
    return report
