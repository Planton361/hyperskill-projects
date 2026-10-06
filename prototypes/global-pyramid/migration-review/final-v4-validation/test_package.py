"""Only fresh-package determinism, mapping, manifest and stale-input checks."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
spec=importlib.util.spec_from_file_location('five_root_review',BASE/'review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
PACKAGE=BASE/'real-five-root-final-v4';PATH=PACKAGE/'migration-manifest.json'
EXPECTED='0946f17af8229463757cda209a1307cd86449bfb5b54258d4aa5f14189310d29'

class Package(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.manifest=R.read(PATH)
 def test_deterministic_package_generation(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);preview=p/'preview';preview.mkdir();files,_=R.P.artifacts(ROOT)
   for n,b in files.items():(preview/n).write_bytes(b)
   regenerated=p/'determinism-test-only';m=R.make_package(ROOT,preview,regenerated)
   self.assertEqual(m,self.manifest);self.assertEqual(R.tree(regenerated),R.tree(PACKAGE))
 def test_exact_mapping_new_master(self):
  target=R.read(PACKAGE/'target-geometry.json');master=R.read(PACKAGE/'global-geometry.json');slots={n['key']:n for n in master['positions']};mapping=self.manifest['contract']['mapping']
  self.assertEqual(master['geometry_fingerprint'],EXPECTED);self.assertEqual(self.manifest['contract']['target']['geometry_fingerprint'],EXPECTED)
  self.assertEqual(len(mapping),135);self.assertEqual(len({n['key'] for n in mapping}),135);self.assertEqual(len({n['slot'] for n in mapping}),135)
  self.assertEqual(sum(n['key'].startswith('category:') for n in mapping),46);self.assertEqual(sum(n['key'].startswith('topic:') for n in mapping),89)
  for n in target['positions']:
   self.assertEqual(n['slot'],n['key'] if n['key'].startswith('category:') else 'leaf:'+n['key'].split(':')[1])
   for key in ('x','y','w','h'):self.assertEqual(n[key],slots[n['slot']][key])
  self.assertEqual(target['root_sectors'],master['root_sectors']);self.assertEqual({slots[s['root']]['y'] for s in master['root_sectors']},{43389})
 def test_manifest_fingerprint_and_source(self):
  m,files=R.inspect_package(PATH,self.manifest['manifest_fingerprint']);data=R.validate_source(ROOT,m);data['_root']=ROOT;R.validate_material(m,files,data)
  self.assertFalse(m['fixture_only']);self.assertEqual(m['contract']['source']['presentation_generation'],0)
  self.assertEqual(R.fp(m['contract']['source']['production_inventory']),'cc708761487a92b6f5851284af67854778784608c54509e3dc206fbcd8fa3056')
  self.assertEqual(m['contract']['source']['accepted_geometry_fingerprint'],'c8467c81b88d8e01351791cee448dc3509b95153bf3eb50bcf2d2f3412a07ec7')
 def test_old_review_token_stale(self):
  results=[]
  for p in sorted(BASE.rglob('migration-manifest.json')):
   if p==PATH:continue
   old=R.read(p)
   with self.assertRaises(R.Refusal) as e:R.inspect_package(p,old['manifest_fingerprint'])
   self.assertEqual(e.exception.status,'STALE_SPATIAL_MIGRATION_PREVIEW')
   results.append(dict(path=str(p.relative_to(ROOT)),status=e.exception.status,reason=e.exception.reason))
  self.assertGreaterEqual(len(results),5)
  (BASE/'final-v4-validation/old-package-results.json').write_bytes(R.encoded(results))

if __name__=='__main__':unittest.main()
