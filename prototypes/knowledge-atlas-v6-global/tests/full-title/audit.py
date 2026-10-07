#!/usr/bin/env python3
"""Offline candidate/immutable observation/Catalog audit. Never writes Knowledge."""
import argparse, copy, hashlib, importlib.util, json, re, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas.snapshot import encode,load_source
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.catalog_observation import validate_observation,FORBIDDEN,SECRET_VALUE
parser=argparse.ArgumentParser()
parser.add_argument('candidate',type=Path)
parser.add_argument('--baseline-manifests',type=Path)
args=parser.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=args.candidate.read_bytes();candidate=json.loads(raw)
assert sha(raw)=='e435b577a848cc542ef2a9a2e334708958680b961a93cc3fd8ebcef6564a2d2a','CANDIDATE_DIGEST_MISMATCH'
assert sha(encode({k:v for k,v in candidate.items() if k!='content_digest'}))==candidate['content_digest']==args.candidate.stem.removeprefix('candidate-'),'CANDIDATE_DIGEST_MISMATCH'
def guard(v):
 if isinstance(v,dict):
  for k,x in v.items():
   assert isinstance(k,str) and not FORBIDDEN.search(k) and not re.search(r'password|passwd|session|account|request_headers|set_cookie',k,re.I),'unsafe field'
   guard(x)
 elif isinstance(v,list):
  for x in v:guard(x)
 elif isinstance(v,str):
  assert not SECRET_VALUE.search(v) and not re.search(r'/(?:Users|var/folders|private|home|tmp)/|file://|(?:account|profile|session)[_-]?id\s*[=:]\s*\S+',v,re.I),'unsafe value'
 else:assert v is None or type(v) in (int,float,bool)
guard(candidate)
observation=candidate['sanitized_observation'];validate_observation(observation)
newdata=load_source(ROOT/'data/knowledge');baseline=copy.deepcopy(newdata)
name='observations/global-topic-metadata-2026-10-07-89d5c1a731e5.json'
assert baseline['catalog_observations'].pop(name)==observation
assert sha(encode(baseline))==candidate['source_catalog_fingerprint']
assert (ROOT/'data/knowledge'/name).read_bytes()==encode(observation)
old,new=Catalog(baseline),Catalog(newdata)
assert sorted(old.references)==candidate['target_ids'] and len(old.references)==3017
assert sha(encode(candidate['target_ids']))==candidate['target_set_fingerprint']
assert len(candidate['successful_acquisition_records'])==3017 and not candidate['unresolved_failure_records']
assert new.categories==old.categories and new.memberships==old.memberships and new.latest_hierarchy==old.latest_hierarchy and new.snapshot_positions==old.snapshot_positions
assert new.reference_history==old.reference_history and all(new.topics[k]==v for k,v in old.topics.items())
assert new.active==old.active and all(newdata[k]==baseline[k] for k in baseline if k!='catalog_observations')
counts={s:sum(t['resolution']==s for t in new.topics.values()) for s in ['RESOLVED_TOPIC','PARTIAL_TOPIC']}
assert counts=={'RESOLVED_TOPIC':3018,'PARTIAL_TOPIC':88} and not new.references
assert len(new.categories)==849 and len(new.topics)==3106 and all(k=='topic:'+str(t['id']) and t.get('is_group') is not True and t['title'].strip() for k,t in new.topics.items())
learned=sorted({p['topic_id'] for p in newdata['progress']['topics'] if p['is_learned']});verified=sorted({p['topic_id'] for p in newdata['progress']['topics'] if p['is_verified']})
assert len(learned)==31 and len(verified)==12
spec=importlib.util.spec_from_file_location('full_title_build',HERE.parents[1]/'build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
assert json.loads((HERE.parents[1]/'model.json').read_text())==json.loads(json.dumps(builder.project())),'stale projection'
result=dict(security='PASS',both_candidate_digests='PASS',strict_observation='PASS',immutable_observation='PASS',source_fingerprint='PASS',categories=849,leaves=3106,counts={**counts,'UNRESOLVED_REFERENCE':0},structural_memberships='unchanged',canonical_hierarchy='unchanged',canonical_positions='unchanged',reference_history='preserved',accepted_89_topics='preserved',active_knowledge_and_progress='unchanged',learned=learned,verified=verified,course8='unchanged',project113='unchanged',stage617='unchanged',normal_projection='current')
if args.baseline_manifests:
 for filename in ['protected-before.json','knowledge-before.json']:
  files=json.loads((args.baseline_manifests/filename).read_text())
  for name,digest in files.items():assert sha((ROOT/name).read_bytes())==digest,name
  result[filename]=dict(files=len(files),byte_identity='PASS')
 protected=json.loads((args.baseline_manifests/'protected-before.json').read_text())
 for directory in ['state/knowledge-atlas','docs/knowledge-map','prototypes/knowledge-atlas-v6','prototypes/knowledge-atlas-v6-skill-tree']:
  assert {str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file()}=={p for p in protected if p.startswith(directory+'/')},directory
 assert sha((HERE.parents[1]/'GLOBAL-V66-ACCEPTED.md').read_bytes())==(args.baseline_manifests/'accepted-md-sha.txt').read_text()
 result['historical_accepted_report']='byte-identical'
(HERE/'ingestion-audit.json').write_bytes(encode(result));print(json.dumps(result))
