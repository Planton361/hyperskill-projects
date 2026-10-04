"""Persistent history, semantic gates, rollback, process crash and readonly contracts."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_knowledge_atlas as fixtures
from knowledge_atlas import pipeline, snapshot, state, transaction, layout_update, regions
from knowledge_atlas import build

ROOT = fixtures.ROOT


class Hardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):fixtures.AtlasUpdates.setUpClass.__func__(cls)

    setUp=fixtures.AtlasUpdates.setUp
    save=fixtures.AtlasUpdates.save
    run_update=fixtures.AtlasUpdates.run_update
    baseline=fixtures.AtlasUpdates.baseline
    files=fixtures.AtlasUpdates.files
    zero=fixtures.AtlasUpdates.zero
    completion=fixtures.AtlasUpdates.completion
    progress=fixtures.AtlasUpdates.progress
    topics=fixtures.AtlasUpdates.topics
    category=fixtures.AtlasUpdates.category
    project=fixtures.AtlasUpdates.project
    relation=fixtures.AtlasUpdates.relation

    def state_bytes(self):
        return {n:(self.state/n).read_bytes() for n in state.NAMES}

    def test_checkpoint_boundary_and_fingerprint_snapshot(self):
        cp,previous=state.read(self.state)
        forbidden={'learned','verified','project_status','project_requires','course_membership','prerequisite','dependent','evidence','canonical_parent_id'}
        def walk(value):
            if isinstance(value,dict):
                self.assertFalse(forbidden&value.keys())
                for v in value.values():walk(v)
            elif isinstance(value,list):
                for v in value:walk(v)
        walk(cp)
        for r in cp['categories'].values():
            if r['tray_allocation']:
                for row in r['tray_allocation']['rows']:self.assertEqual(set(row),{'key','width','height'})
        self.assertEqual(previous['state_schema_version'],2)
        for row in previous['topic_states'].values():self.assertEqual(len(row['learned']),64)
        for row in previous['project_states'].values():self.assertEqual(len(row['status']),64)

    def test_completion_with_progress_and_evidence(self):
        self.baseline(); old_cp=(self.state/state.NAMES[0]).read_bytes()
        self.completion(); self.progress(); self.data['edges'].append({'id':'completion-evidence','type':'project_requires',
                  'source':'project:380','target':'topic:1','evidence_ids':['map-8']})
        r=self.run_update();self.zero(r,'PROJECT_STATE_ONLY')
        self.assertEqual(old_cp,(self.state/state.NAMES[0]).read_bytes())
        self.assertEqual(r['presentation']['generation'],r['presentation']['generation_before'])
        raw=json.loads((self.output/'model.json').read_text())
        self.assertEqual(next(p for p in raw['progress']['projects'] if p['project_id']==380)['status'],'completed')
        self.assertEqual(raw['indexes']['projects']['380']['required_topic_ids'],[1])

    def test_existing_tray_safe_and_generation_tracks_allocation(self):
        self.baseline(); old=self.state_bytes(); parent=next(c['id'] for c in self.data['categories'] if c['title']=='JVM basics')
        self.topics(3,parent); r=self.run_update(); self.assertEqual(r['status'],'SAFE_TO_APPLY')
        self.assertEqual(r['presentation']['category_displacement']['max'],0)
        self.assertEqual(r['presentation']['topic_displacement']['max'],0)
        self.assertEqual(r['presentation']['generation'],r['presentation']['generation_before']+1)
        now=self.state_bytes(); self.assertNotEqual(old,now)
        self.assertEqual(self.run_update()['diff']['change_types'],['NO_CHANGE']);self.assertEqual(now,self.state_bytes())
        expected=self.files();shutil.rmtree(self.output);self.run_update()
        rebuilt=self.files();expected.pop('update-report.json');rebuilt.pop('update-report.json')
        self.assertEqual(expected,rebuilt)

    def test_large_tray_review_stops_and_requires_override(self):
        self.baseline(); old=self.state_bytes(); build=self.files()
        parent=next(c['id'] for c in self.data['categories'] if c['title']=='JVM basics')
        self.topics(24,parent);r=self.run_update(); self.assertEqual(r['status'],'REVIEW_REQUIRED')
        self.assertFalse(r['applied']);self.assertEqual(old,self.state_bytes());self.assertEqual(build,self.files())
        r=self.run_update(approve_review=True);self.assertTrue(r['applied']);self.assertEqual(r['status'],'REVIEW_REQUIRED')

    def test_new_category_review_wrapped_with_no_major_movement(self):
        self.baseline(); old=self.state_bytes(); build=self.files();self.category()
        r=self.run_update(); self.assertEqual(r['status'],'REVIEW_REQUIRED');self.assertFalse(r['applied'])
        self.assertEqual(r['presentation']['category_displacement']['max'],0)
        self.assertEqual(old,self.state_bytes());self.assertEqual(build,self.files())
        self.assertTrue(self.run_update(approve_review=True)['applied'])

    def test_basics_growth_requires_rebalance_not_review_override(self):
        self.baseline(); old=self.state_bytes(); build=self.files();self.topics(3)
        r=self.run_update(approve_review=True);self.assertEqual(r['status'],'REBALANCE_REQUIRED');self.assertFalse(r['applied'])
        self.assertTrue(any(n['depth']==1 for n in r['region_impact']['moved_categories']))
        self.assertTrue(r['region_impact']['unrelated_moved_categories'])
        self.assertEqual(old,self.state_bytes());self.assertEqual(build,self.files())

    def test_unrelated_thirty_units_and_major_one_unit(self):
        cp,before=state.read(self.state); restored=layout_update.bridge(ROOT/'prototypes/knowledge-atlas-v6',action='restore',data=self.data,checkpoint=cp)
        geom=restored['geometry']; after=copy.deepcopy(geom)
        self.topics(); changes=__import__('knowledge_atlas.diff',fromlist=['compare']).compare(before,snapshot.index(self.data))
        unrelated=next(n for n in after['nodes'] if n['key']=='category:2944'); unrelated['x']+=30
        r=regions.impact(self.data,geom,after,changes,[],[],cp);self.assertEqual(r['outcome'],'REVIEW_REQUIRED')
        major=next(n for n in after['nodes'] if n['depth']==1); major['x']+=1
        r=regions.impact(self.data,geom,after,changes,[],[],cp);self.assertEqual(r['outcome'],'REBALANCE_REQUIRED')

    def test_failure_every_phase_preserves_state_and_build(self):
        self.baseline(); before=self.state_bytes(); build=self.files();self.completion()
        for phase in ['after_candidate_checkpoint','during_artifact_generation','during_browser_validation',
                      'before_final_rename','after_publish_0','after_publish_1']:
            def fault(current):
                if current==phase:raise RuntimeError('injected '+phase)
            with self.subTest(phase=phase),self.assertRaisesRegex(RuntimeError,'injected'):
                self.run_update(fault=fault)
            self.assertEqual(before,self.state_bytes());self.assertEqual(build,self.files())
            self.assertFalse((self.state.parent/'.knowledge-atlas-transaction.json').exists())

    def test_filesystem_exchange_error_rolls_back(self):
        self.baseline(); before=self.state_bytes(); build=self.files();self.completion()
        original=transaction.exchange; count=0
        def exchange(a,b):
            nonlocal count
            count+=1
            if count==2:raise OSError('injected rename failure')
            original(a,b)
        with patch.object(transaction,'exchange',exchange),self.assertRaises(OSError):self.run_update()
        self.assertEqual(before,self.state_bytes());self.assertEqual(build,self.files())

    def test_process_crash_readonly_block_and_explicit_recovery(self):
        self.baseline(); before=self.state_bytes(); build=self.files(); self.completion(); self.save()
        code="""import os,sys
sys.path.insert(0,'scripts')
from knowledge_atlas.pipeline import run
def fault(phase):
    if phase=='after_publish_0':os._exit(77)
run(sys.argv[1],sys.argv[2],sys.argv[3],state=sys.argv[4],fault=fault)
"""
        result=subprocess.run([sys.executable,'-B','-c',code,str(ROOT),str(self.output),str(self.source),str(self.state)],cwd=ROOT)
        self.assertEqual(result.returncode,77)
        journal=self.state.parent/'.knowledge-atlas-transaction.json';self.assertTrue(journal.exists())
        changed=self.state_bytes()
        with self.assertRaisesRegex(ValueError,'RECOVERY_REQUIRED'):self.run_update('dry-run')
        self.assertEqual(changed,self.state_bytes())
        self.run_update(recover=True);self.assertEqual(before,self.state_bytes());self.assertEqual(build,self.files())
        self.assertFalse(journal.exists())

    def test_versions_partial_and_bootstrap_refusal(self):
        before=self.state_bytes()
        with self.assertRaisesRegex(ValueError,'STATE_ALREADY_EXISTS'):self.run_update(bootstrap=True)
        self.assertEqual(before,self.state_bytes())
        p=self.state/state.NAMES[1];value=json.loads(p.read_text());value['state_schema_version']=999;p.write_bytes(snapshot.encode(value))
        with self.assertRaisesRegex(ValueError,'STATE_MIGRATION_REQUIRED'):self.run_update('dry-run')
        p.write_bytes(before[state.NAMES[1]]);(self.state/state.NAMES[0]).unlink()
        with self.assertRaisesRegex(ValueError,'STATE_MIGRATION_REQUIRED'):self.run_update('check')
        with self.assertRaisesRegex(ValueError,'STATE_ALREADY_EXISTS'):self.run_update(bootstrap=True)

    def test_explicit_bootstrap_and_missing_build_check(self):
        shutil.rmtree(self.state)
        with self.assertRaisesRegex(ValueError,'STATE_MIGRATION_REQUIRED'):self.run_update('dry-run')
        r=self.run_update(bootstrap=True);self.assertEqual(r['status'],'SAFE_TO_APPLY');self.assertTrue(r['bootstrap'])
        before=self.state_bytes();r=self.run_update('check');self.assertEqual(r['status'],'SAFE_TO_APPLY')
        self.assertEqual(before,self.state_bytes());self.assertFalse(self.output.exists())

    def test_font_canary_stops_before_state_mutation(self):
        before=self.state_bytes();policy=json.loads((ROOT/'scripts/knowledge_atlas/font-canary.json').read_text());policy['samples'][0]['width']+=1
        with self.assertRaisesRegex(ValueError,'FONT_METRICS_MISMATCH'):
            layout_update.bridge(ROOT/'prototypes/knowledge-atlas-v6',action='canary',canary=policy)
        self.assertEqual(before,self.state_bytes());self.assertFalse(self.output.exists())

    def test_readonly_snapshot_and_build_hashes(self):
        self.baseline();before=self.state_bytes();build=self.files();self.progress()
        r=self.run_update('dry-run');self.assertEqual(r['status'],'SAFE_TO_APPLY')
        self.assertEqual(before,self.state_bytes());self.assertEqual(build,self.files())

    def test_state_pair_integrity_and_small_local_diff(self):
        self.baseline(); before=self.state_bytes();self.topics(3,next(c['id'] for c in self.data['categories'] if c['title']=='JVM basics'))
        self.run_update();new=self.state_bytes();a=json.loads(before[state.NAMES[0]]);b=json.loads(new[state.NAMES[0]])
        changed=[k for k in a['categories'] if a['categories'][k]!=b['categories'][k]]
        self.assertLessEqual(len(changed),7)
        self.assertEqual(set(a['categories']),set(b['categories']))
        (self.state/state.NAMES[0]).write_bytes(before[state.NAMES[0]])
        with self.assertRaisesRegex(ValueError,'STATE_INTEGRITY_MISMATCH'):self.run_update('dry-run')

    def test_removed_trailing_rows_do_not_enter_visible_bounds(self):
        self.baseline();parent=next(c['id'] for c in self.data['categories'] if c['title']=='JVM basics')
        self.topics(3,parent);self.run_update();before=json.loads((self.output/'geometry.json').read_text())
        self.data['topics']=[t for t in self.data['topics'] if t['id'] not in (90001,90002,90003)]
        self.data['edges']=[e for e in self.data['edges'] if e['target'] not in ('topic:90001','topic:90002','topic:90003')]
        r=self.run_update();self.assertEqual(r['status'],'SAFE_TO_APPLY')
        after=json.loads((self.output/'geometry.json').read_text())
        old_tray=next(t for t in before['trays'] if t['parent']==f'category:{parent}')
        new_tray=next(t for t in after['trays'] if t['parent']==f'category:{parent}')
        self.assertLess(new_tray['height'],old_tray['height'])
        cp,_=state.read(self.state);self.assertTrue(any(s['key']=='topic:90001' for s in cp['categories'][f'category:{parent}']['tray_allocation']['rows']))
        expected=self.files();shutil.rmtree(self.output);self.run_update();rebuilt=self.files()
        expected.pop('update-report.json');rebuilt.pop('update-report.json');self.assertEqual(expected,rebuilt)

    def test_validation_component_failures_preserve_final_outputs(self):
        self.baseline();old=self.state_bytes();final=self.files();self.completion()
        with patch.object(build,'artifacts',side_effect=OSError('artifact failure')),self.assertRaises(OSError):self.run_update()
        self.assertEqual(old,self.state_bytes());self.assertEqual(final,self.files())
        original=layout_update.bridge
        def browser_failure(runtime,**payload):
            if payload.get('action')=='runtime-test':raise ValueError('browser validation failure')
            return original(runtime,**payload)
        with patch.object(layout_update,'bridge',browser_failure),self.assertRaisesRegex(ValueError,'browser validation failure'):self.run_update()
        self.assertEqual(old,self.state_bytes());self.assertEqual(final,self.files())

    def test_known_layout_version_requires_explicit_rebalance(self):
        cp,previous=state.read(self.state)
        cp['layout_algorithm_version']='previous-algorithm';previous['layout_algorithm_version']='previous-algorithm'
        previous['checkpoint_fingerprint']=snapshot.ordered_digest(cp)
        (self.state/state.NAMES[0]).write_bytes(snapshot.encode(cp));(self.state/state.NAMES[1]).write_bytes(snapshot.encode(previous))
        old=self.state_bytes()
        with self.assertRaisesRegex(ValueError,'REBALANCE_REQUIRED'):self.run_update('dry-run')
        self.assertEqual(old,self.state_bytes());self.assertFalse(self.output.exists())
        r=self.run_update(rebalance=True);self.assertTrue(r['applied'])
        now,_=state.read(self.state);self.assertEqual(now['layout_algorithm_version'],snapshot.ALGORITHM)

    def test_ordered_state_fingerprint_detects_row_reordering(self):
        cp,_=state.read(self.state)
        region=next(r for r in cp['categories'].values() if r['tray_allocation'] and len(r['tray_allocation']['rows'])>1)
        region['tray_allocation']['rows'].reverse()
        (self.state/state.NAMES[0]).write_bytes(snapshot.encode(cp))
        with self.assertRaisesRegex(ValueError,'STATE_INTEGRITY_MISMATCH'):self.run_update('dry-run')

    def test_explicit_hash_migration_and_failure_rollback(self):
        self.baseline();cp,previous=state.read(self.state)
        geom=json.loads((self.output/'geometry.json').read_text());cp['state_schema_version']=1;previous['state_schema_version']=1
        previous['checkpoint_fingerprint']=snapshot.digest(cp);previous['geometry_fingerprint']=snapshot.digest(geom)
        (self.state/state.NAMES[0]).write_bytes(snapshot.encode(cp));(self.state/state.NAMES[1]).write_bytes(snapshot.encode(previous))
        before=self.state_bytes();final=self.files()
        with self.assertRaisesRegex(ValueError,'STATE_MIGRATION_REQUIRED'):self.run_update('dry-run')
        def fault(phase):
            if phase=='after_publish_0':raise RuntimeError('migration rollback')
        with self.assertRaises(RuntimeError):self.run_update(migrate=True,fault=fault)
        self.assertEqual(before,self.state_bytes());self.assertEqual(final,self.files())
        r=self.run_update(migrate=True);self.assertTrue(r['applied']);updated,_=state.read(self.state)
        self.assertEqual(updated['presentation_generation'],cp['presentation_generation'])
        self.assertEqual(updated['state_schema_version'],2)
        self.assertEqual(json.loads((self.output/'geometry.json').read_text()),geom)

    def test_bootstrap_rechecks_source_before_publication(self):
        shutil.rmtree(self.state)
        original=layout_update.bridge
        def concurrent_change(runtime,**payload):
            result=original(runtime,**payload)
            if payload.get('action')=='runtime-test':self.progress();self.save()
            return result
        with patch.object(layout_update,'bridge',concurrent_change),self.assertRaisesRegex(ValueError,'SOURCE_CHANGED_DURING_BOOTSTRAP'):
            self.run_update(bootstrap=True)
        self.assertFalse(self.state.exists());self.assertFalse(self.output.exists())
        self.assertFalse((self.state.parent/'.knowledge-atlas-transaction.json').exists())

    def test_normal_no_change_checks_saved_geometry_fingerprint(self):
        self.baseline();previous=json.loads((self.state/state.NAMES[1]).read_text())
        previous['geometry_fingerprint']='0'*64
        (self.state/state.NAMES[1]).write_bytes(snapshot.encode(previous))
        before=self.state_bytes();final=self.files()
        with self.assertRaisesRegex(ValueError,'STATE_GEOMETRY_MISMATCH'):self.run_update()
        self.assertEqual(before,self.state_bytes());self.assertEqual(final,self.files())

    def test_explicit_candidate_budget_returns_rebalance_without_publication(self):
        self.baseline();before=self.state_bytes();final=self.files();self.topics(3)
        r=self.run_update(budget={'max':0,'significant':0,'major':0})
        self.assertEqual(r['outcome'],'REBALANCE_REQUIRED');self.assertFalse(r['applied'])
        self.assertGreater(r['estimated_displacement'],0)
        self.assertEqual(before,self.state_bytes());self.assertEqual(final,self.files())


if __name__=='__main__':unittest.main()
