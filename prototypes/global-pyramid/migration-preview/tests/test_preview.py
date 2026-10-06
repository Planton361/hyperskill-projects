import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import hashlib
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('migration_preview_build',BASE/'build.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class Preview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inputs=M.load();cls.output,cls.mapping=M.construct(**cls.inputs)
    def test_exact_inventory_and_mapping(self):
        mapping=self.mapping;self.assertEqual(len(mapping),135);self.assertEqual(len(set(x['slot'] for x in mapping)),135)
        self.assertEqual(sum(x['key'].startswith('category:') for x in mapping),46);self.assertEqual(sum(x['key'].startswith('topic:') for x in mapping),89)
        self.assertEqual({x['key'] for x in mapping},set(self.inputs['history']['active_categories']+self.inputs['history']['active_topics']))
        for x in mapping:self.assertEqual(x['slot'],x['key'] if x['key'].startswith('category:') else x['key'].replace('topic:','leaf:'))
    def test_exact_target_coordinates_and_native_source(self):
        master={n['key']:n for n in self.inputs['master']['positions']};native={n['key']:n for n in self.inputs['current']['nodes']}
        for n in self.output['target-geometry.json']['positions']:
            p=master[n['slot']];self.assertEqual([n[k] for k in ['x','y','w','h']],[p[k] for k in ['x','y','w','h']]);self.assertEqual(n['parent'],p['primary_parent'])
        for n in self.output['current-geometry.json']['positions']:
            p=native[n['key']];self.assertEqual(n['x'],p['x']-p['width']/2);self.assertEqual(n['native_x'],p['x'])
        self.assertEqual(self.output['current-geometry.json']['native_geometry'],self.inputs['current'])
    def test_semantics_and_metrics(self):
        x=self.output['migration-metrics.json'];self.assertEqual(x['semantic_hashes_before'],x['semantic_hashes_after']);self.assertEqual(x['semantic_counts'],dict(categories=46,topics=89,learned=31,verified=12,project_113=26,stage_617=12,generation=0,history_version=0))
        for t in M.snapshot.TABLES:self.assertEqual(self.output['semantic-snapshot.json'][t],self.inputs['model'][t])
        for n in self.output['migration-diff.json']['entities']:
            self.assertEqual(n['delta_x'],n['target_x']-n['current_x']);self.assertEqual(n['displacement'],M.math.hypot(n['delta_x'],n['delta_y']))
        self.assertEqual(x['displacement']['all']['moved'],135);self.assertEqual(x['displacement']['all']['unchanged'],0)
    def test_determinism_and_checked_contract(self):
        one,_=M.artifacts();two,_=M.artifacts();self.assertEqual(one,two);self.assertTrue(all((BASE/k).read_bytes()==v for k,v in one.items()));self.assertEqual(M.check()['status'],'MIGRATION_PREVIEW_READY')
    def test_missing_duplicate_unknown_and_ambiguous_fail_closed(self):
        for edit in ['missing','duplicate','unknown','ambiguous']:
            x=copy.deepcopy(self.inputs)
            if edit=='missing':x['master']['positions']=[n for n in x['master']['positions'] if n['key']!='leaf:1']
            elif edit=='duplicate':x['history']['active_topics'][0]=x['history']['active_topics'][1]
            elif edit=='unknown':x['history']['active_topics'][0]='topic:999999'
            else:next(r for r in x['master']['leaf_identity_mapping'] if r['slot']=='leaf:1')['semantic_aliases']=['reference:1']
            with self.subTest(edit=edit),self.assertRaises(M.Gate):M.construct(**x)
    def test_changed_parent_and_invalid_master_fail_closed(self):
        x=copy.deepcopy(self.inputs);x['master']['positions'][0]['primary_parent']='category:missing'
        with self.assertRaises(M.Gate) as c:M.construct(**x)
        self.assertEqual(c.exception.status,'MIGRATION_TARGET_INVALID')
        x=copy.deepcopy(self.inputs);x['model']['progress']['topics'][0]['is_learned']=True
        with self.assertRaises(M.Gate) as c:M.construct(**x)
        self.assertEqual(c.exception.status,'MIGRATION_SEMANTIC_MISMATCH')
    def test_stale_inputs_and_artifact_rejection_disposable_only(self):
        one,_=M.artifacts()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for k,v in one.items():(p/k).write_bytes(v)
            original=M.inventory
            try:
                M.inventory=lambda root:{**original(root),'synthetic-source-change':'changed'}
                with self.assertRaises(M.Gate) as c:M.check(directory=p)
                self.assertEqual(c.exception.status,'MIGRATION_SOURCE_CHANGED')
            finally:M.inventory=original
            (p/'target-geometry.json').write_bytes(one['target-geometry.json']+b' ')
            with self.assertRaises(M.Gate) as c:M.check(directory=p)
            self.assertEqual(c.exception.status,'MIGRATION_GEOMETRY_CONFLICT')
    def test_repeated_future_reveal_zero_displacement(self):
        master={n['key']:n for n in self.inputs['master']['positions']};accepted={n['slot']:copy.deepcopy(master[n['slot']]) for n in self.output['target-geometry.json']['positions']};original=copy.deepcopy(master)
        categories=[k for k in sorted(master) if k not in accepted and k.startswith('category:')];leaves=[k for k in sorted(master) if k not in accepted and k.startswith('leaf:')];dormant=[categories[0],leaves[0],categories[1],leaves[1]];comparisons=0
        for keys in [dormant[:2],dormant[2:4]]:
            before=copy.deepcopy(accepted)
            for k in keys:accepted[k]=copy.deepcopy(master[k])
            for k,n in before.items():self.assertEqual(n,accepted[k]);comparisons+=1
            for k in keys:self.assertEqual(accepted[k],original[k])
        self.assertEqual(comparisons,272);self.assertEqual(original,master)
        (BASE/'tests/future-reveal.json').write_bytes(M.snapshot.encode(dict(steps=2,initial_positions=135,newly_revealed=4,exact_existing_entity_comparisons=comparisons,maximum_displacement=0,placement_search=False,fixture_only=True)))
    def test_route_and_tray_comparison_preserves_saved_geometry(self):
        comparison=self.output['geometry-comparison.json'];master={r['child']:r for r in self.inputs['master']['hierarchy_routes']}
        self.assertEqual(len(comparison['category_routes']),45);self.assertEqual(comparison['changed_category_routes'],45)
        for route in comparison['category_routes']:
            self.assertEqual(route['target_points'],master[route['child']]['points'])
        self.assertEqual([t['current_surface'] for t in comparison['topic_trays']],self.inputs['current']['trays'])
        self.assertEqual(len(comparison['topic_trays']),26)
        self.assertEqual(sum(len(t['topic_mapping']) for t in comparison['topic_trays']),89)
    def test_stale_runtime_rejected_without_changing_real_files(self):
        one,_=M.artifacts()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for k,v in one.items():(p/k).write_bytes(v)
            manifest=json.loads(one['migration-manifest.json']);manifest['bindings']['runtime_files']['view/app.js']='synthetic-stale-runtime'
            manifest.pop('manifest_fingerprint');manifest['manifest_fingerprint']=M.fp(manifest)
            (p/'migration-manifest.json').write_bytes(M.snapshot.encode(manifest))
            with self.assertRaises(M.Gate) as c:M.check(directory=p)
            self.assertEqual(c.exception.status,'MIGRATION_SOURCE_CHANGED')
    def test_protected_locations_byte_identity(self):
        recorded=json.loads((BASE/'tests/baseline.json').read_text());current={str(p.relative_to(M.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['docs/knowledge-map','state/knowledge-atlas','data/knowledge'] for p in (M.ROOT/d).rglob('*') if p.is_file()}
        for name in ['prototypes/global-pyramid/generated/global-geometry.json','prototypes/global-pyramid/generated/catalog.json']:current[name]=hashlib.sha256((M.ROOT/name).read_bytes()).hexdigest()
        self.assertEqual(recorded,current)
if __name__=='__main__':unittest.main()
