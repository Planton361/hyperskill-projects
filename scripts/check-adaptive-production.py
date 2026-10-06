#!/usr/bin/env python3
"""Read-only verification of the adopted adaptive release and protected inputs."""
import hashlib
import json
from pathlib import Path
from knowledge_atlas import adaptive_production as A, snapshot

root = Path(__file__).resolve().parents[1]
path = root / 'prototypes/adaptive-pyramid/production-review/final-v1/apply-manifest.json'
m = json.loads(path.read_bytes())
token = 'b1597b5ea86c481a855bcc6fe6c5a7f3380300b39262bb8faa0a9b729320a069'
A.require(A.digest({k:v for k,v in m.items() if k != 'manifest_fingerprint'}) == m['manifest_fingerprint'] == token,
          'Reviewed manifest changed')
A.pending(root)
for folder, key in ((A.PRODUCTION,'target_production'), (A.STATE,'source_state'), (A.KNOWLEDGE,'source_knowledge')):
    A.require(A.bound_tree(root,folder) == m[key], 'Changed inventory: ' + folder)
reference = (root / A.REFERENCE).read_bytes()
A.require(hashlib.sha256(reference).hexdigest() == m['global_reference_sha256'], 'Global reference changed')
A.require(reference == (root / A.PRODUCTION / 'global-reference.json').read_bytes(), 'Packaged reference changed')
data = snapshot.load_source(root / A.KNOWLEDGE)
raw = json.loads((root / A.PRODUCTION / 'model.json').read_bytes())
A.require(raw['source_hashes'] == {t:snapshot.digest(data[t]) for t in snapshot.TABLES} == m['semantic_invariance']['source_hashes'], 'Semantic inputs changed')
print(json.dumps({'status':'PASS','production_fingerprint':m['target_production']['fingerprint'],
                 'state_knowledge_active_history_generation_history_unchanged':True,
                 'global_reference_unchanged':True}, indent=2))
