#!/usr/bin/env python3
"""Offline ingestion of one reviewed, immutable dormant relation observation."""
import argparse
import hashlib
import json
from pathlib import Path
from knowledge_atlas.snapshot import load_source, encode
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.catalog_observation import require
from knowledge_atlas.scope_relations import observation_from_candidate, write_immutable, ScopeRelationCatalog

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', required=True, type=Path)
p.add_argument('--expected-digest', required=True)
p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
p.add_argument('--export', type=Path)
a = p.parse_args()
catalog = Catalog(load_source(a.root / 'data/knowledge'))
o = observation_from_candidate(a.candidate, a.expected_digest, catalog)
# Exact reviewed Global and semantic contracts are preconditions, including replay.
for key, relative in [('global_catalog_sha256', 'src/myatlas/knowledge-atlas-scope-pyramid/catalog.json'),
                      ('report_sha256', 'docs/evidence/SCOPE-RELATIONS-DISCOVERY.md')]:
    expected = o['candidate'][key] if key in o['candidate'] else o['semantic_contract'][key]
    require(hashlib.sha256((a.root / relative).read_bytes()).hexdigest() == expected, 'Reviewed source contract changed')
inventory = {}
for pth in sorted((a.root / 'data/knowledge').rglob('*')):
    if not pth.is_file(): continue
    require(not pth.is_symlink(), 'Knowledge symlink rejected')
    if pth.parent.name == 'observations' and pth.suffix == '.json':
        if json.loads(pth.read_bytes()).get('observation_type') == 'scope_relations_catalog': continue
    inventory[pth.relative_to(a.root).as_posix()] = hashlib.sha256(pth.read_bytes()).hexdigest()
require(hashlib.sha256((json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()).hexdigest() == o['candidate']['knowledge_inventory_sha256'], 'Reviewed Knowledge source changed')
path, created = write_immutable(a.root / 'data/knowledge/observations', o)
if a.export:
    a.export.write_bytes(encode(ScopeRelationCatalog(o, 'observations/' + path.name, catalog).index()))
print(('CREATED' if created else 'NO-OP') + ' ' + path.name)
print('SHA-256 ' + hashlib.sha256(path.read_bytes()).hexdigest())
