#!/usr/bin/env python3
"""Read-only accepted Knowledge projection. Writes only this prototype."""
import collections,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
from knowledge_atlas.catalog import Catalog
from knowledge_atlas.snapshot import load_source

def project():
    data=load_source(ROOT/'data/knowledge');catalog=Catalog(data)
    return dict(categories=list(catalog.categories.values()),topics=list(catalog.topics.values()),
        references=list(catalog.references.values()),memberships={str(k):sorted(v) for k,v in catalog.memberships.items()},
        progress=data['progress'],evidence=data['evidence'],provenance=catalog.provenance,
        courses=data['courses'],edges=data['edges'],observations=catalog.observation_ids)
if __name__=='__main__':
    start=time.perf_counter();raw=project()
    (HERE/'model.json').write_text(json.dumps(raw,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(build_ms=(time.perf_counter()-start)*1000,topics=len(raw['topics']))))
