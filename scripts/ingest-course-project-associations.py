#!/usr/bin/env python3
"""Offline immutable association ingestion; no active-table or network operations."""
import argparse
import hashlib
from pathlib import Path
from knowledge_atlas import snapshot
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.catalog_observation import require
from knowledge_atlas.course_project_associations import observation_from_candidate, write_immutable

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', required=True, type=Path)
p.add_argument('--expected-digest', required=True)
p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
p.add_argument('--export', type=Path)
a = p.parse_args()
data = snapshot.load_source(a.root/'data/knowledge')
catalog = Catalog(data)
require(catalog.scope_relations is not None, 'Existing dormant scope catalog required')
o = observation_from_candidate(a.candidate, a.expected_digest, catalog.scope_relations, data['courses'])
require(hashlib.sha256((a.root/'prototypes/knowledge-atlas-scope-pyramid/catalog.json').read_bytes()).hexdigest() == o['candidate']['global_catalog_sha256'], 'Reviewed Global Catalog changed')
require(len(o['courses']) == 52 and sum(len(c['project_ids']) for c in o['courses']) == 867 and
        len({pid for c in o['courses'] for pid in c['project_ids']}) == 299, 'Reviewed association coverage mismatch')
require([c['course_id'] for c in o['courses'] if c['state'] == 'KNOWN_EMPTY'] == [31,41,57,60], 'Reviewed known-empty inventories changed')
path, created = write_immutable(a.root/'data/knowledge/observations', o)
# Re-load through the same typed composition boundary used by the Production guard.
composed = Catalog(snapshot.load_source(a.root/'data/knowledge'))
if a.export:
    body = snapshot.encode(composed.scope_relations.index())
    if not a.export.exists() or a.export.read_bytes() != body:
        a.export.write_bytes(body)
print(('CREATED' if created else 'NO-OP') + ' ' + path.name)
print('SHA-256 ' + hashlib.sha256(path.read_bytes()).hexdigest())
