"""Focused root composition checks; no Production writer or migration approval."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('root_composition',BASE/'build.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)

def read(p):return json.loads(p.read_bytes())
def protected():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ('docs/knowledge-map','state/knowledge-atlas','data/knowledge') for p in (ROOT/name).rglob('*') if p.is_file()}

class RootComposition(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=read(BASE/'root-layout/before.json');cls.old=read(BASE/'root-layout/previous-global-geometry.json');cls.new=read(BASE/'generated/global-geometry.json');cls.old_nodes={n['key']:n for n in cls.old['positions']};cls.nodes={n['key']:n for n in cls.new['positions']};cls.catalog=read(BASE/'generated/catalog.json');cls.pair_count=0
 def test_five_roots_order_depth_baseline(self):
  self.assertEqual([s['root'] for s in self.new['root_sectors']],list(B.ROOT_ORDER))
  self.assertEqual([next(n['title'] for n in self.catalog['entities'] if n['key']==r) for r in B.ROOT_ORDER],['Computer science','Math','Natural science','Product development','Generative AI'])
  self.assertEqual({self.nodes[r]['depth'] for r in B.ROOT_ORDER},{0});self.assertEqual({self.nodes[r]['y'] for r in B.ROOT_ORDER},{self.new['root_composition']['root_baseline']})
  self.assertEqual({n['key'] for n in self.nodes.values() if not n['parents']},set(B.ROOT_ORDER));self.assertNotIn('presentation:hyperskill',self.nodes)
 def test_sectors_contain_blocks_and_do_not_overlap(self):
  sectors=self.new['root_sectors']
  for a,b in zip(sectors,sectors[1:]):self.assertEqual(b['x']-a['x']-a['w'],B.SECTOR_GAP)
  for s in sectors:
   self.assertGreaterEqual(s['w'],B.MIN_SECTOR_WIDTH)
   for n in self.nodes.values():
    if n['root']==s['root']:
     self.assertTrue(s['x']<=n['x'] and n['x']+n['w']<=s['x']+s['w']);self.assertTrue(s['y']<=n['y'] and n['y']+n['h']<=s['y']+s['h'])
 def test_counts_semantics_and_catalog_unchanged(self):
  self.assertEqual(self.new['counts'],dict(categories=849,structural_leaves=3106,positions=3955,hierarchy_pairs=3952))
  self.assertEqual(self.catalog['counts'],dict(categories=849,topics=89,references=3017,positions=3955,hierarchy=3952))
  self.assertEqual(len(self.catalog['personal']),135);self.assertEqual(sum(p['is_learned'] is True for p in self.catalog['progress']),31);self.assertEqual(sum(p['is_verified'] is True for p in self.catalog['progress']),12)
  self.assertEqual(hashlib.sha256((BASE/'generated/catalog.json').read_bytes()).hexdigest(),self.before['catalog_sha256'])
  self.assertEqual(self.new['source_catalog_fingerprint'],self.old['source_catalog_fingerprint'])
 def test_every_internal_pair_exact(self):
  pairs=0
  for root in B.ROOT_ORDER:
   ns=[n for n in self.new['positions'] if n['root']==root]
   for i,a in enumerate(ns):
    oa=self.old_nodes[a['key']]
    for b in ns[i+1:]:
     ob=self.old_nodes[b['key']]
     if a['x']-b['x']!=oa['x']-ob['x'] or a['y']-b['y']!=oa['y']-ob['y']:self.fail('Internal geometry changed: '+a['key']+' / '+b['key'])
     pairs+=1
  type(self).pair_count=pairs
 def test_metadata_regions_routes_rigid(self):
  for key,n in self.nodes.items():
   old=self.old_nodes[key];dx=n['x']-old['x'];dy=n['y']-old['y'];expected=json.loads(json.dumps(old));expected['x']+=dx;expected['y']+=dy
   if 'region' in expected:expected['region']['x']+=dx;expected['region']['y']+=dy
   self.assertEqual(n,expected)
  old_routes={r['child']:r for r in self.old['hierarchy_routes']}
  for route in self.new['hierarchy_routes']:
   child=self.nodes[route['child']];old=self.old_nodes[child['key']];dx=child['x']-old['x'];dy=child['y']-old['y']
   if child['primary_parent']:
    self.assertEqual(route,dict(old_routes[child['key']],points=[[x+dx,y+dy] for x,y in old_routes[child['key']]['points']]))
   else:self.assertEqual(route['parent'],'presentation:hyperskill');self.assertEqual(route['points'][-1],[child['x']+child['w']//2,child['y']])
  self.assertEqual(self.new['leaf_identity_mapping'],self.old['leaf_identity_mapping'])
 def test_repeated_build_identical(self):
  a=B.encoded();self.assertEqual(a,B.encoded());self.assertEqual(a[1],(BASE/'generated/global-geometry.json').read_bytes())
 def test_scope_exact_coordinates(self):
  result=subprocess.check_output(['node',str(BASE/'tests/core.cjs')],text=True);v=json.loads(result);self.assertEqual(v['maximumDisplacementPx'],0)
  (BASE/'root-layout/scope-results.json').write_text(json.dumps(v,indent=2)+'\n')
 def test_old_review_token_stale(self):
  spec=importlib.util.spec_from_file_location('old_review_validator',BASE/'migration-review/review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
  path=BASE/'migration-review/real-authorized-v2/migration-manifest.json';token='7c79c8447b61bfeebca06bc17ab0792841c8c66eb22b568de8c93a3aba1247a2'
  self.assertEqual(read(path)['manifest_fingerprint'],token)
  for fn in [lambda:R.inspect_package(path,token),lambda:R.validate_source(ROOT,read(path))]:
   with self.assertRaises(R.Refusal) as failure:fn()
   self.assertEqual(failure.exception.status,'STALE_SPATIAL_MIGRATION_PREVIEW')
 def test_new_fingerprint_and_protected_bytes(self):
  self.assertNotEqual(self.new['geometry_fingerprint'],self.old['geometry_fingerprint'])
  self.assertEqual(self.new['geometry_fingerprint'],hashlib.sha256(B.snapshot.encode({k:v for k,v in self.new.items() if k!='geometry_fingerprint'})).hexdigest())
  self.assertEqual(protected(),self.before['protected'])
  history=read(ROOT/'state/knowledge-atlas/activation-state.json');self.assertEqual(history['layout_generation'],0);self.assertEqual(len(history['active_categories']),46);self.assertEqual(len(history['active_topics']),89)
  self.assertFalse((ROOT/'state/knowledge-atlas/spatial-authority.json').exists())
 @classmethod
 def tearDownClass(cls):
  assert protected()==cls.before['protected']
  (BASE/'root-layout/focused-results.json').write_text(json.dumps(dict(internal_pairs_checked=cls.pair_count,positions=3955,old_review_token='STALE_SPATIAL_MIGRATION_PREVIEW',protected_files_unchanged=True),indent=2)+'\n')

if __name__=='__main__':unittest.main()
